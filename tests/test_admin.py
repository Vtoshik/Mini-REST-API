from models.user import User
from main import app, db


def test_list_users_requires_admin(client, auth_headers):
    response = client.get('/api/v1/admin/users', headers=auth_headers)
    assert response.status_code == 403


def test_list_users_requires_auth(client):
    response = client.get('/api/v1/admin/users')
    assert response.status_code == 401


def test_list_users_as_admin(client, admin_headers):
    response = client.get('/api/v1/admin/users', headers=admin_headers)
    assert response.status_code == 200
    assert isinstance(response.json['data'], list)
    assert any(u['username'] == "adminuser" for u in response.json['data'])
    assert response.json['pagination']['page'] == 1


def test_list_users_is_paginated(client, admin_headers, make_user):
    for i in range(3):
        make_user(username=f"paged{i}", email=f"paged{i}@example.com")

    response = client.get('/api/v1/admin/users?page=1&per_page=2', headers=admin_headers)
    assert response.status_code == 200
    assert len(response.json['data']) == 2
    assert response.json['pagination']['per_page'] == 2
    assert response.json['pagination']['total'] >= 4


def test_create_user_as_admin(client, admin_headers):
    response = client.post(
        '/api/v1/admin/users',
        json={"username": "created", "email": "created@example.com", "password": "Str0ng@Pass"},
        headers=admin_headers,
    )
    assert response.status_code == 201


def test_create_user_requires_admin(client, auth_headers):
    response = client.post(
        '/api/v1/admin/users',
        json={"username": "created", "email": "created@example.com", "password": "Str0ng@Pass"},
        headers=auth_headers,
    )
    assert response.status_code == 403


def test_admin_created_user_can_log_in_immediately(client, admin_headers):
    # Admin-created accounts have no verification link issued for them, so
    # they must be auto-verified — otherwise they'd be locked out forever.
    client.post(
        '/api/v1/admin/users',
        json={"username": "created", "email": "created@example.com", "password": "Str0ng@Pass"},
        headers=admin_headers,
    )
    response = client.post(
        '/api/v1/login', json={"username": "created", "password": "Str0ng@Pass"}
    )
    assert response.status_code == 200


def test_create_user_duplicate(client, admin_headers):
    client.post(
        '/api/v1/admin/users',
        json={"username": "dup", "email": "dup@example.com", "password": "Str0ng@Pass"},
        headers=admin_headers,
    )
    response = client.post(
        '/api/v1/admin/users',
        json={"username": "dup", "email": "dup@example.com", "password": "Str0ng@Pass"},
        headers=admin_headers,
    )
    assert response.status_code == 400


def test_get_user_as_admin(client, admin_headers, make_user):
    target_id = make_user(username="target", email="target@example.com")
    response = client.get(f'/api/v1/admin/users/{target_id}', headers=admin_headers)
    assert response.status_code == 200
    assert response.json['username'] == "target"


def test_get_user_requires_admin(client, auth_headers, make_user):
    target_id = make_user(username="target", email="target@example.com")
    response = client.get(f'/api/v1/admin/users/{target_id}', headers=auth_headers)
    assert response.status_code == 403


def test_get_user_not_found(client, admin_headers):
    response = client.get('/api/v1/admin/users/9999', headers=admin_headers)
    assert response.status_code == 404


def test_admin_can_update_other_users_username(client, admin_headers, make_user):
    target_id = make_user(username="target", email="target@example.com")
    response = client.put(
        f'/api/v1/admin/users/{target_id}', json={"username": "renamed"}, headers=admin_headers
    )
    assert response.status_code == 200


def test_admin_can_promote_user_to_admin(client, admin_headers, make_user):
    target_id = make_user(username="target", email="target@example.com")
    response = client.put(
        f'/api/v1/admin/users/{target_id}', json={"status": "admin"}, headers=admin_headers
    )
    assert response.status_code == 200
    with app.app_context():
        assert User.query.get(target_id).status == "admin"


def test_self_can_update_own_username(client, auth_headers, make_user):
    # auth_headers user is 'testuser'; find its id via /me
    me = client.get('/api/v1/me', headers=auth_headers).json
    response = client.put(
        f"/api/v1/admin/users/{me['id']}", json={"username": "selfrenamed"}, headers=auth_headers
    )
    assert response.status_code == 200


def test_self_cannot_escalate_to_admin(client, auth_headers):
    me = client.get('/api/v1/me', headers=auth_headers).json
    response = client.put(
        f"/api/v1/admin/users/{me['id']}", json={"status": "admin"}, headers=auth_headers
    )
    assert response.status_code == 403
    with app.app_context():
        assert User.query.get(me['id']).status == "user"


def test_user_cannot_edit_other_users_record(client, auth_headers, make_user):
    target_id = make_user(username="other", email="other@example.com")
    response = client.put(
        f'/api/v1/admin/users/{target_id}', json={"username": "hijacked"}, headers=auth_headers
    )
    assert response.status_code == 403


def test_delete_user_as_admin(client, admin_headers, make_user):
    target_id = make_user(username="target", email="target@example.com")
    response = client.delete(f'/api/v1/admin/users/{target_id}', headers=admin_headers)
    assert response.status_code == 200
    with app.app_context():
        assert User.query.get(target_id) is None


def test_delete_user_requires_admin(client, auth_headers, make_user):
    target_id = make_user(username="target", email="target@example.com")
    response = client.delete(f'/api/v1/admin/users/{target_id}', headers=auth_headers)
    assert response.status_code == 403


def test_delete_user_not_found(client, admin_headers):
    response = client.delete('/api/v1/admin/users/9999', headers=admin_headers)
    assert response.status_code == 404


def test_admin_cannot_delete_own_account(client, admin_headers):
    me = client.get('/api/v1/me', headers=admin_headers).json
    response = client.delete(f"/api/v1/admin/users/{me['id']}", headers=admin_headers)
    assert response.status_code == 400
    with app.app_context():
        assert User.query.get(me['id']) is not None


def test_cannot_delete_the_last_remaining_admin(client, admin_headers, make_user):
    # A second admin deletes the first: allowed, since another admin remains.
    second_admin_id = make_user(username="secondadmin", email="second@example.com", status="admin")
    from flask_jwt_extended import create_access_token
    with app.app_context():
        token = create_access_token(identity=str(second_admin_id))
    csrf = client.get('/api/v1/csrf-token').json['csrf_token']
    second_admin_headers = {"Authorization": f"Bearer {token}", "X-CSRF-Token": csrf}

    me = client.get('/api/v1/me', headers=admin_headers).json
    response = client.delete(f"/api/v1/admin/users/{me['id']}", headers=second_admin_headers)
    assert response.status_code == 200

    # Now only one admin (second_admin) is left — deleting them should be blocked.
    me2 = client.get('/api/v1/me', headers=second_admin_headers).json
    response = client.delete(f"/api/v1/admin/users/{me2['id']}", headers=second_admin_headers)
    assert response.status_code == 400
    with app.app_context():
        assert User.query.get(second_admin_id) is not None


def test_admin_can_delete_a_non_admin_user(client, admin_headers, make_user):
    target_id = make_user(username="target", email="target@example.com")
    response = client.delete(f'/api/v1/admin/users/{target_id}', headers=admin_headers)
    assert response.status_code == 200
