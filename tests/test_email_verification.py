from datetime import datetime, timedelta, timezone

from main import app, db
from models.user import User
from models.email_verification_token import EmailVerificationToken


def test_register_creates_unverified_user(client, csrf_token):
    response = client.post(
        '/api/v1/register',
        json={"username": "newuser", "email": "newuser@example.com", "password": "Str0ng@Pass"},
        headers={"X-CSRF-Token": csrf_token},
    )
    user_id = response.json['user_id']
    with app.app_context():
        assert User.query.get(user_id).email_verified is False


def test_unverified_user_cannot_log_in(client, make_user):
    make_user(username="unverified", email="u@example.com", password="Test@1234", email_verified=False)
    response = client.post(
        '/api/v1/login', json={"username": "unverified", "password": "Test@1234"}
    )
    assert response.status_code == 403


def test_verify_email_success(client, csrf_token):
    register_response = client.post(
        '/api/v1/register',
        json={"username": "newuser", "email": "newuser@example.com", "password": "Str0ng@Pass"},
        headers={"X-CSRF-Token": csrf_token},
    )
    token = register_response.json['verify_token']

    response = client.post(
        '/api/v1/verify-email', json={"token": token}, headers={"X-CSRF-Token": csrf_token}
    )
    assert response.status_code == 200

    login_response = client.post(
        '/api/v1/login', json={"username": "newuser", "password": "Str0ng@Pass"}
    )
    assert login_response.status_code == 200


def test_verify_email_does_not_need_csrf_exemption_bypass(client, csrf_token):
    register_response = client.post(
        '/api/v1/register',
        json={"username": "newuser", "email": "newuser@example.com", "password": "Str0ng@Pass"},
        headers={"X-CSRF-Token": csrf_token},
    )
    token = register_response.json['verify_token']

    # verify-email is CSRF-exempt (public, unauthenticated action reached
    # from an emailed link, same as register).
    response = client.post('/api/v1/verify-email', json={"token": token})
    assert response.status_code == 200


def test_verify_email_invalid_token(client):
    response = client.post('/api/v1/verify-email', json={"token": "does-not-exist"})
    assert response.status_code == 400


def test_verify_email_token_cannot_be_reused(client, csrf_token):
    register_response = client.post(
        '/api/v1/register',
        json={"username": "newuser", "email": "newuser@example.com", "password": "Str0ng@Pass"},
        headers={"X-CSRF-Token": csrf_token},
    )
    token = register_response.json['verify_token']
    client.post('/api/v1/verify-email', json={"token": token})
    response = client.post('/api/v1/verify-email', json={"token": token})
    assert response.status_code == 400


def test_verify_email_expired_token(client, make_user):
    user_id = make_user(username="unverified", email="u@example.com", email_verified=False)
    with app.app_context():
        expired = EmailVerificationToken(
            token="expired-token",
            user_id=user_id,
            expires_at=datetime.now(timezone.utc) - timedelta(hours=1),
        )
        db.session.add(expired)
        db.session.commit()

    response = client.post('/api/v1/verify-email', json={"token": "expired-token"})
    assert response.status_code == 400


def test_cleanup_tokens_also_purges_stale_verification_tokens(client, make_user):
    user_id = make_user(username="unverified", email="u@example.com", email_verified=False)
    with app.app_context():
        expired = EmailVerificationToken(
            token="expired-token",
            user_id=user_id,
            expires_at=datetime.now(timezone.utc) - timedelta(hours=1),
        )
        fresh = EmailVerificationToken(
            token="fresh-token",
            user_id=user_id,
            expires_at=datetime.now(timezone.utc) + timedelta(hours=1),
        )
        db.session.add_all([expired, fresh])
        db.session.commit()

    runner = app.test_cli_runner()
    result = runner.invoke(args=["cleanup-tokens"])
    assert "Deleted 1 stale email verification token(s)." in result.output

    with app.app_context():
        remaining = {t.token for t in EmailVerificationToken.query.all()}
    assert remaining == {"fresh-token"}
