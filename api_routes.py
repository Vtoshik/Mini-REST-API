from database import db
from models.user import User
from models.note import Note
from flask import render_template, request, redirect, Blueprint, url_for, session, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from flask_restful import Api, Resource, reqparse

api_bp = Blueprint('api_bp', __name__)
api = Api(api_bp)

user_parser = reqparse.RequestParser()
user_parser.add_argument('username', type=str, required=True, help='Username required')
user_parser.add_argument('email', type=str, required=True, help='Email required')
user_parser.add_argument('password', type=str, required=True, help='Password required')

note_parser = reqparse.RequestParser()
note_parser.add_argument('title', type=str, required=True, help='Title required')
note_parser.add_argument('content', type=str, required=False)
note_parser.add_argument('user_id', type=int, required=True, help='User ID required')

def authenticate_request():
    user_id = session.get('user_id')
    if not user_id:
        return None
    return User.query.get(user_id)

@api_bp.errorhandler(Exception)
def handle_exception(e):
    return {"message": "An unexpected error occurred", "error": str(e)}, 500

class Login(Resource):
    def post(self):
        try:
            data = request.get_json()
            if not data:
                return {"message": "No data provided"}, 400
            username = data.get('username')
            password = data.get('password')
            if not username or not password:
                return {"message": "Username and password are required"}, 400
            user = User.query.filter_by(username=username).first()
            if user and check_password_hash(user.password, password):
                session['user_id'] = user.id
                return {"message": "Login successful", "user_id": user.id}, 200
            return {"message": "Invalid credentials"}, 401
        except Exception as e:
            return {"message": f"Server error: {str(e)}", "error": str(type(e))}, 500

class Register(Resource):
    def post(self):
        data = request.get_json()
        existing_user = User.query.filter(
            (User.email == data['email']) | (User.username == data['username'])
        ).first()
        if existing_user:
            return {"message": "User with this email or username already exists."},400

        hashed_password = generate_password_hash(data['password'])
        user = User(username=data['username'], email=data['email'], password=hashed_password)
        db.session.add(user)
        db.session.commit()
        return {"message": "User created successfully", "user_id": user.id}, 201

class Users(Resource):
    def get(self):
        user = authenticate_request()
        if not user:
            return {"message": "Authentication required"}, 401
        users = User.query.all()
        return [{"id": u.id, "username": u.username, "email": u.email, "created_at": u.created_at.isoformat()} for u in users], 200

class UserResource(Resource):
    def get(self, user_id):
        user = authenticate_request()
        if not user:
            return {"message": "Authentication required"}, 401
        user = User.query.get_or_404(user_id)
        return {"id": user.id, "username": user.username, "email": user.email, "status": user.status, "created_at": user.created_at.isoformat()}, 200
    
    def put(self, user_id):
        user = authenticate_request()
        if not user:
            return {"message": "Authentication required"}, 401
        data = user_parser.parse_args()
        user = User.query.get_or_404(user_id)
        user.username = data['username']
        user.email = data['email']
        if 'password' in data:
            user.password = generate_password_hash(data['password'])
        db.session.commit()
        return {"message": "User updated"}, 200

    def delete(self, user_id):
        user = authenticate_request()
        if not user:
            return {"message": "Authentication required"}, 401
        user = User.query.get_or_404(user_id)
        db.session.delete(user)
        db.session.commit()
        return {"message": "User deleted"}, 200
    
class Notes(Resource):
    def get(self):
        user = authenticate_request()
        if not user:
            return {"message": "Authentication required"}, 401
        notes = Note.query.filter_by(user_id=user.id).all()
        return [{"id": n.id, "title": n.title, "content": n.content, "created_at": n.created_at.isoformat()} for n in notes], 200

    def post(self):
        user = authenticate_request()
        if not user:
            return {"message": "Authentication required"}, 401
        data = note_parser.parse_args()
        new_note = Note(title=data['title'], content=data['content'], user_id=user.id)
        db.session.add(new_note)
        db.session.commit()
        return {"message": "Note created", "note_id": new_note.id}, 201

# Resources
api.add_resource(Login, '/api/v1/login')
api.add_resource(Register, '/api/v1/register')
api.add_resource(Users, '/api/v1/users')
api.add_resource(UserResource, '/api/v1/users/<int:user_id>')
api.add_resource(Notes, '/api/v1/notes')