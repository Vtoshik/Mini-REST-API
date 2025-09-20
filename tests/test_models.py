import pytest
from main import app, db
from models.user import User
from models.note import Note

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'

    with app.test_client() as client:
        with app.app_context():
            db.create_all()
        yield client
        with app.app_context():
            db.drop_all()

def test_create_user_and_note(client):
    with app.app_context():
        user = User(username="testuser", email="test@example.com")
        db.session.add(user)
        db.session.commit()

        note = Note(title="Test Note", content="Test Content", user_id=user.id)
        db.session.add(note)
        db.session.commit()

        assert user.id is not None
        assert note.id is not None
        assert note.user_id == user.id

def test_user_email_uniqueness(client):
    with app.app_context():
        user1 = User(username="u1", email="duplicate@example.com")
        db.session.add(user1)
        db.session.commit()

        user2 = User(username="u2", email="duplicate@example.com")
        db.session.add(user2)
        with pytest.raises(Exception):
            db.session.commit()