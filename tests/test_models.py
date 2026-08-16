from datetime import datetime, timedelta, timezone

import pytest
from sqlalchemy.exc import IntegrityError

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


def test_create_user_and_note(client):
    user = User(username="testuser", email="test@example.com", password="hashed-password")
    db.session.add(user)
    db.session.commit()

    note = Note(title="Test Note", content="Test Content", user_id=user.id)
    db.session.add(note)
    db.session.commit()

    assert user.id is not None
    assert note.id is not None
    assert note.user_id == user.id


def test_note_defaults(client):
    user = User(username="testuser", email="test@example.com", password="hashed-password")
    db.session.add(user)
    db.session.commit()

    note = Note(title="Defaults", content=None, user_id=user.id)
    db.session.add(note)
    db.session.commit()

    assert note.pinned is False
    assert note.deleted_at is None
    assert note.category is None


def test_user_defaults_to_user_status(client):
    user = User(username="testuser", email="test@example.com", password="hashed-password")
    db.session.add(user)
    db.session.commit()
    assert user.status == "user"


def test_user_email_uniqueness(client):
    user1 = User(username="u1", email="duplicate@example.com", password="hashed-password")
    db.session.add(user1)
    db.session.commit()

    user2 = User(username="u2", email="duplicate@example.com", password="hashed-password")
    db.session.add(user2)
    with pytest.raises(IntegrityError):
        db.session.commit()


def test_user_username_uniqueness(client):
    user1 = User(username="dup", email="a@example.com", password="hashed-password")
    db.session.add(user1)
    db.session.commit()

    user2 = User(username="dup", email="b@example.com", password="hashed-password")
    db.session.add(user2)
    with pytest.raises(IntegrityError):
        db.session.commit()


def test_note_deleting_user_cascades_to_notes(client):
    user = User(username="testuser", email="test@example.com", password="hashed-password")
    db.session.add(user)
    db.session.commit()

    note = Note(title="Will be deleted", content=None, user_id=user.id)
    db.session.add(note)
    db.session.commit()
    note_id = note.id

    db.session.delete(user)
    db.session.commit()

    assert Note.query.get(note_id) is None


def test_active_note_titles_unique_per_user(client):
    user = User(username="testuser", email="test@example.com", password="hashed-password")
    db.session.add(user)
    db.session.commit()

    db.session.add(Note(title="Same", content=None, user_id=user.id))
    db.session.commit()

    db.session.add(Note(title="Same", content=None, user_id=user.id))
    with pytest.raises(IntegrityError):
        db.session.commit()


def test_trashed_note_title_does_not_block_new_active_note(client):
    user = User(username="testuser", email="test@example.com", password="hashed-password")
    db.session.add(user)
    db.session.commit()

    trashed = Note(title="Same", content=None, user_id=user.id)
    trashed.deleted_at = datetime.now(timezone.utc)
    db.session.add(trashed)
    db.session.commit()

    active = Note(title="Same", content=None, user_id=user.id)
    db.session.add(active)
    db.session.commit()  # should not raise

    assert active.id is not None


def test_password_reset_token_valid_when_fresh_and_unused(client):
    user = User(username="testuser", email="test@example.com", password="hashed-password")
    db.session.add(user)
    db.session.commit()

    token = PasswordResetToken(
        token="abc123",
        user_id=user.id,
        expires_at=datetime.now(timezone.utc) + timedelta(hours=1),
    )
    assert token.is_valid() is True


def test_password_reset_token_invalid_when_used(client):
    user = User(username="testuser", email="test@example.com", password="hashed-password")
    db.session.add(user)
    db.session.commit()

    token = PasswordResetToken(
        token="abc123",
        user_id=user.id,
        expires_at=datetime.now(timezone.utc) + timedelta(hours=1),
    )
    token.used = True
    assert token.is_valid() is False


def test_password_reset_token_invalid_when_expired(client):
    user = User(username="testuser", email="test@example.com", password="hashed-password")
    db.session.add(user)
    db.session.commit()

    token = PasswordResetToken(
        token="abc123",
        user_id=user.id,
        expires_at=datetime.now(timezone.utc) - timedelta(hours=1),
    )
    assert token.is_valid() is False


def test_password_reset_token_handles_naive_expires_at(client):
    user = User(username="testuser", email="test@example.com", password="hashed-password")
    db.session.add(user)
    db.session.commit()

    # SQLite round-trips DateTime columns without tzinfo; is_valid() should
    # still compare correctly against an aware "now".
    token = PasswordResetToken(
        token="abc123",
        user_id=user.id,
        expires_at=datetime.now(timezone.utc).replace(tzinfo=None) + timedelta(hours=1),
    )
    assert token.is_valid() is True
