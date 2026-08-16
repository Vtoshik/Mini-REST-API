from datetime import datetime, timedelta, timezone

from main import app, db
from models.password_reset_token import PasswordResetToken


def test_admin_can_create_reset_token(client, admin_headers, make_user):
    target_id = make_user(username="target", email="target@example.com")
    response = client.post(
        f'/api/v1/admin/users/{target_id}/reset-password', headers=admin_headers
    )
    assert response.status_code == 201
    assert "reset_token" in response.json
    assert response.json['reset_path'] == f"/reset-password/{response.json['reset_token']}"


def test_create_reset_token_requires_admin(client, auth_headers, make_user):
    target_id = make_user(username="target", email="target@example.com")
    response = client.post(
        f'/api/v1/admin/users/{target_id}/reset-password', headers=auth_headers
    )
    assert response.status_code == 403


def test_create_reset_token_for_missing_user(client, admin_headers):
    response = client.post(
        '/api/v1/admin/users/9999/reset-password', headers=admin_headers
    )
    assert response.status_code == 404


def test_complete_password_reset(client, admin_headers, make_user, csrf_token):
    target_id = make_user(username="target", email="target@example.com", password="Old@1234")
    token = client.post(
        f'/api/v1/admin/users/{target_id}/reset-password', headers=admin_headers
    ).json['reset_token']

    response = client.post(
        '/api/v1/reset-password',
        json={"token": token, "password": "NewPass@123"},
        headers={"X-CSRF-Token": csrf_token},
    )
    assert response.status_code == 200

    login = client.post('/api/v1/login', json={"username": "target", "password": "NewPass@123"})
    assert login.status_code == 200


def test_reset_password_invalid_token(client, csrf_token):
    response = client.post(
        '/api/v1/reset-password',
        json={"token": "does-not-exist", "password": "NewPass@123"},
        headers={"X-CSRF-Token": csrf_token},
    )
    assert response.status_code == 400


def test_reset_password_weak_password(client, admin_headers, make_user, csrf_token):
    target_id = make_user(username="target", email="target@example.com")
    token = client.post(
        f'/api/v1/admin/users/{target_id}/reset-password', headers=admin_headers
    ).json['reset_token']
    response = client.post(
        '/api/v1/reset-password',
        json={"token": token, "password": "weak"},
        headers={"X-CSRF-Token": csrf_token},
    )
    assert response.status_code == 400


def test_reset_password_token_cannot_be_reused(client, admin_headers, make_user, csrf_token):
    target_id = make_user(username="target", email="target@example.com")
    token = client.post(
        f'/api/v1/admin/users/{target_id}/reset-password', headers=admin_headers
    ).json['reset_token']
    client.post(
        '/api/v1/reset-password',
        json={"token": token, "password": "NewPass@123"},
        headers={"X-CSRF-Token": csrf_token},
    )
    response = client.post(
        '/api/v1/reset-password',
        json={"token": token, "password": "AnotherPass@1"},
        headers={"X-CSRF-Token": csrf_token},
    )
    assert response.status_code == 400


def test_requesting_a_new_reset_token_invalidates_the_previous_one(client, admin_headers, make_user, csrf_token):
    target_id = make_user(username="target", email="target@example.com")
    old_token = client.post(
        f'/api/v1/admin/users/{target_id}/reset-password', headers=admin_headers
    ).json['reset_token']
    client.post(
        f'/api/v1/admin/users/{target_id}/reset-password', headers=admin_headers
    ).json['reset_token']

    response = client.post(
        '/api/v1/reset-password',
        json={"token": old_token, "password": "NewPass@123"},
        headers={"X-CSRF-Token": csrf_token},
    )
    assert response.status_code == 400


def test_cleanup_tokens_cli_command_removes_stale_tokens(client, admin_headers, make_user):
    from main import app, db
    from models.password_reset_token import PasswordResetToken

    target_id = make_user(username="target", email="target@example.com")
    fresh_token = client.post(
        f'/api/v1/admin/users/{target_id}/reset-password', headers=admin_headers
    ).json['reset_token']
    with app.app_context():
        expired = PasswordResetToken(
            token="stale-token",
            user_id=target_id,
            expires_at=datetime.now(timezone.utc) - timedelta(hours=1),
        )
        db.session.add(expired)
        db.session.commit()

    runner = app.test_cli_runner()
    result = runner.invoke(args=["cleanup-tokens"])
    assert "Deleted 1 stale password reset token(s)." in result.output

    with app.app_context():
        remaining = {t.token for t in PasswordResetToken.query.all()}
    assert remaining == {fresh_token}


def test_reset_password_expired_token(client, admin_headers, make_user, csrf_token):
    target_id = make_user(username="target", email="target@example.com")
    with app.app_context():
        expired = PasswordResetToken(
            token="expired-token",
            user_id=target_id,
            expires_at=datetime.now(timezone.utc) - timedelta(hours=1),
        )
        db.session.add(expired)
        db.session.commit()

    response = client.post(
        '/api/v1/reset-password',
        json={"token": "expired-token", "password": "NewPass@123"},
        headers={"X-CSRF-Token": csrf_token},
    )
    assert response.status_code == 400
