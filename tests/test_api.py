import pytest
import sys
import os
# Add root folder to sys.path where main.py is located
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from main import app, db
from models.user import User
from werkzeug.security import generate_password_hash
from flask_jwt_extended import create_access_token

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

@pytest.fixture
def auth_headers(client):
    user=User(username="testuser", email="test@example.com", password=generate_password_hash("Test@1234"))
    with app.app_context():
        db.session.add(user)
        db.session.commit()
        token = create_access_token(identity=str(user.id))
    return {"Authorization": f"Bearer {token}"}

def test_create_note(client, auth_headers):
    response = client.post('/api/v1/notes', json={"title": "Test Note", "content": "Content"}, headers=auth_headers)
    assert response.status_code == 201
    assert response.json['message'] == "Note created"
    assert "note_id" in response.json['data']

def test_create_note_invalid_title(client, auth_headers):
    response = client.post('/api/v1/notes', json={"title": "   ", "content": "Content"}, headers=auth_headers)
    assert response.status_code == 400
    assert response.json['message'] == "Validation error"