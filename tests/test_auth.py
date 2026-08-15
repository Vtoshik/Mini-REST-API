from models.user import User


def register(client, csrf_token, **overrides):
    payload = {
        "username": "newuser",
        "email": "newuser@example.com",
        "password": "Str0ng@Pass",
    }
    payload.update(overrides)
    return client.post(
        '/api/v1/register', json=payload, headers={"X-CSRF-Token": csrf_token}
    )


def test_register_success(client, csrf_token):
    response = register(client, csrf_token)
    assert response.status_code == 201
    assert "user_id" in response.json


def test_register_duplicate_username(client, csrf_token, make_user):
    make_user(username="newuser", email="other@example.com")
    response = register(client, csrf_token)
    assert response.status_code == 400


def test_register_duplicate_email(client, csrf_token, make_user):
    make_user(username="someoneelse", email="newuser@example.com")
    response = register(client, csrf_token)
    assert response.status_code == 400


def test_register_weak_password(client, csrf_token):
    response = register(client, csrf_token, password="weak")
    assert response.status_code == 400


def test_register_invalid_email(client, csrf_token):
    response = register(client, csrf_token, email="not-an-email")
    assert response.status_code == 400


def test_register_username_too_short(client, csrf_token):
    response = register(client, csrf_token, username="ab")
    assert response.status_code == 400


def test_register_does_not_need_csrf_exemption_bypass(client):
    # register is CSRF-exempt, so it should succeed even with no token header.
    response = client.post(
        '/api/v1/register',
        json={"username": "nocsrf", "email": "nocsrf@example.com", "password": "Str0ng@Pass"},
    )
    assert response.status_code == 201


def test_login_success(client, make_user):
    make_user(username="loginuser", email="login@example.com", password="Test@1234")
    response = client.post(
        '/api/v1/login', json={"username": "loginuser", "password": "Test@1234"}
    )
    assert response.status_code == 200
    assert response.json['message'] == "Login successful"
    assert "access_token_cookie" in response.headers.get("Set-Cookie", "")


def test_login_wrong_password(client, make_user):
    make_user(username="loginuser", email="login@example.com", password="Test@1234")
    response = client.post(
        '/api/v1/login', json={"username": "loginuser", "password": "WrongPass@1"}
    )
    assert response.status_code == 401


def test_login_nonexistent_user(client):
    response = client.post(
        '/api/v1/login', json={"username": "ghost", "password": "Test@1234"}
    )
    assert response.status_code == 401


def test_login_missing_fields(client):
    response = client.post('/api/v1/login', json={"username": "loginuser"})
    assert response.status_code == 400


def test_logout_clears_cookie(client):
    response = client.post('/api/v1/logout')
    assert response.status_code == 200
    assert response.json['message'] == "Logout successful"


def test_csrf_token_endpoint(client):
    response = client.get('/api/v1/csrf-token')
    assert response.status_code == 200
    assert "csrf_token" in response.json


def test_me_requires_auth(client):
    response = client.get('/api/v1/me')
    assert response.status_code == 401


def test_me_returns_current_user(client, auth_headers):
    response = client.get('/api/v1/me', headers=auth_headers)
    assert response.status_code == 200
    assert response.json['username'] == "testuser"
    assert response.json['status'] == "user"


def test_me_put_updates_username(client, auth_headers):
    response = client.put(
        '/api/v1/me', json={"username": "renamed"}, headers=auth_headers
    )
    assert response.status_code == 200
    response = client.get('/api/v1/me', headers=auth_headers)
    assert response.json['username'] == "renamed"


def test_me_put_rejects_taken_email(client, auth_headers, make_user):
    make_user(username="other", email="taken@example.com")
    response = client.put(
        '/api/v1/me', json={"email": "taken@example.com"}, headers=auth_headers
    )
    assert response.status_code == 400


def test_me_put_without_csrf_fails(client, auth_headers):
    headers = {"Authorization": auth_headers["Authorization"]}
    response = client.put('/api/v1/me', json={"username": "renamed"}, headers=headers)
    assert response.status_code == 400


def test_me_password_change_success(client, auth_headers):
    response = client.post(
        '/api/v1/me/password',
        json={"current_password": "Test@1234", "new_password": "NewPass@123"},
        headers=auth_headers,
    )
    assert response.status_code == 200
    # old password no longer works
    login_response = client.post(
        '/api/v1/login', json={"username": "testuser", "password": "Test@1234"}
    )
    assert login_response.status_code == 401
    # new password does
    login_response = client.post(
        '/api/v1/login', json={"username": "testuser", "password": "NewPass@123"}
    )
    assert login_response.status_code == 200


def test_me_password_change_wrong_current(client, auth_headers):
    response = client.post(
        '/api/v1/me/password',
        json={"current_password": "WrongOne@1", "new_password": "NewPass@123"},
        headers=auth_headers,
    )
    assert response.status_code == 400


def test_me_password_change_weak_new_password(client, auth_headers):
    response = client.post(
        '/api/v1/me/password',
        json={"current_password": "Test@1234", "new_password": "weak"},
        headers=auth_headers,
    )
    assert response.status_code == 400
