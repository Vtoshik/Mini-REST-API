import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Flask-SQLAlchemy binds its engine once, when db.init_app(app) runs at
# import time in main.py — setting app.config['SQLALCHEMY_DATABASE_URI']
# later (e.g. inside a fixture) has no effect on which database gets used.
# These need to be in the environment before `main` is ever imported, which
# is why they're set here in conftest.py rather than in the fixtures.
os.environ.setdefault('DATABASE_URL', 'sqlite:///:memory:')
os.environ.setdefault('SECRET_KEY', 'test-secret')
os.environ.setdefault('JWT_SECRET_KEY', 'test-jwt-secret')
# Same reasoning as DATABASE_URL above: Limiter binds its storage backend at
# import time too. Defaulting to in-memory storage keeps the test suite from
# depending on a real Redis instance being up, and from tripping the real
# "50 per hour" rate limit across many requests in one test run (every test
# client shares 127.0.0.1 as its remote address).
os.environ.setdefault('REDIS_URL', 'memory://')

import pytest
from werkzeug.security import generate_password_hash

from main import app, db, limiter
from models.user import User
from models.note import Note
from models.password_reset_token import PasswordResetToken


@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            limiter.reset()
            yield client
            db.session.remove()
            db.drop_all()


def _make_user(username, email, password, status="user"):
    user = User(username=username, email=email, password=generate_password_hash(password))
    user.status = status
    db.session.add(user)
    db.session.commit()
    return user


@pytest.fixture
def make_user(client):
    """Factory fixture: create a user directly in the DB (bypasses the API)."""
    def _factory(username="testuser", email="test@example.com", password="Test@1234", status="user"):
        with app.app_context():
            return _make_user(username, email, password, status).id
    return _factory


def _csrf(client):
    return client.get('/api/v1/csrf-token').json['csrf_token']


@pytest.fixture
def csrf_token(client):
    return _csrf(client)


def _auth_headers_for(client, user_id):
    from flask_jwt_extended import create_access_token
    with app.app_context():
        token = create_access_token(identity=str(user_id))
    return {"Authorization": f"Bearer {token}", "X-CSRF-Token": _csrf(client)}


@pytest.fixture
def auth_headers(client, make_user):
    user_id = make_user(username="testuser", email="test@example.com", password="Test@1234", status="user")
    return _auth_headers_for(client, user_id)


@pytest.fixture
def admin_headers(client, make_user):
    user_id = make_user(username="adminuser", email="admin@example.com", password="Test@1234", status="admin")
    return _auth_headers_for(client, user_id)


@pytest.fixture
def auth_as():
    """Returns a function that builds auth headers for an arbitrary user_id."""
    def _factory(client, user_id):
        return _auth_headers_for(client, user_id)
    return _factory
