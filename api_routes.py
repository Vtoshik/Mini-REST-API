from database import db
from models.user import User
from models.note import Note
from flask import request, Blueprint, abort
from werkzeug.security import generate_password_hash, check_password_hash
from flask_restful import Api, Resource, reqparse
from flask_jwt_extended import jwt_required, create_access_token, get_jwt_identity
import logging


logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

api_bp = Blueprint('api_bp', __name__)
api = Api(api_bp)

user_parser = reqparse.RequestParser()
user_parser.add_argument('username', type=str, required=True, help='Username required')
user_parser.add_argument('email', type=str, required=True, help='Email required')
user_parser.add_argument('password', type=str, required=True, help='Password required')
user_parser.add_argument('status', type=str, choices=['user', 'admin'], default='user')

note_parser = reqparse.RequestParser()
note_parser.add_argument('title', type=str, required=True, help='Title required')
note_parser.add_argument('content', type=str, required=False)
note_parser.add_argument('user_id', type=int, required=True, help='User ID required')

def authenticate_request():
    user_id = get_jwt_identity()
    logger.debug(f"JWT Identity: {user_id}")
    if not user_id:
        logger.warning("No JWT identity found")
        return None
    user = User.query.get(user_id)
    if not user:
        logger.warning(f"User not found for ID: {user_id}")
        return None
    return user

def authenticate_and_check_admin():
    user = authenticate_request()
    if not user or user.status != 'admin':
        abort(403, "Admin access required")
    return user

@api_bp.errorhandler(Exception)
def handle_exception(e):
    logger.error(f"Exception occurred: {str(e)}", exc_info=True)
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
                access_token = create_access_token(identity=str(user.id))
                logger.debug(f"Login successful for user {username}, token created")
                print(f"Returning for login user_id: {user.id}, status: {user.status}")
                return {"message": "Login successful", 'access_token': access_token, 'user_id': user.id, 'user_status': user.status}, 200
            return {"message": "Invalid credentials"}, 401
        except Exception as e:
            logger.error(f"Login error: {str(e)}", exc_info=True)
            return {"message": f"Server error: {str(e)}", "error": str(type(e))}, 500
           
class Register(Resource):
    def post(self):
        data = request.get_json()
        existing_user = User.query.filter(
            (User.email == data['email']) | (User.username == data['username'])
        ).first()
        if existing_user:
            return {"message": "User with this email or username already exists."}, 400

        hashed_password = generate_password_hash(data['password'])
        user = User(username=data['username'], email=data['email'], password=hashed_password)
        db.session.add(user)
        db.session.commit()
        return {"message": "User created successfully", "user_id": user.id}, 201

class Users(Resource):
    @jwt_required()
    def get(self):
        user = authenticate_request()
        if not user:
            return {"message": "Authentication required"}, 401
        if user.status != 'admin':
            return {"message": "Admin access required"}, 403
        users = User.query.all()
        return [{"id": u.id, "username": u.username, "email": u.email, "created_at": u.created_at.isoformat()} for u in users], 200

class UserResource(Resource):
    @jwt_required()
    def get(self, user_id):
        user = authenticate_request()
        if not user:
            return {"message": "Authentication required"}, 401
        if user.status != 'admin':
            return {"message": "Forbidden"}, 403
        user = User.query.get_or_404(user_id)
        return {
            "id": user.id, 
            "username": user.username, 
            "email": user.email, 
            "status": user.status, 
            "created_at": user.created_at.isoformat()
            }, 200
    
    @jwt_required()
    def put(self, user_id):
        user = authenticate_request()
        if not user:
            return {"message": "Authentication required"}, 401
        if user.status != 'admin' and user.id != user_id:
            return {"message": "Forbidden"}, 403
        data = user_parser.parse_args()
        target_user = User.query.get_or_404(user_id)
        target_user.username = data['username']
        target_user.email = data['email']
        if 'password' in data:
            target_user.password = generate_password_hash(data['password'])
        db.session.commit()
        return {"message": "User updated"}, 200

    @jwt_required()
    def delete(self, user_id):
        user = authenticate_request()
        if not user:
            return {"message": "Authentication required"}, 401
        if user.status != 'admin':
            return {"message": "Admin access required"}, 403
        target_user = User.query.get_or_404(user_id)
        db.session.delete(target_user)
        db.session.commit()
        return {"message": "User deleted"}, 200
    
class Notes(Resource):
    @jwt_required()
    def get(self):
        user = authenticate_request()
        if not user:
            return {"message": "Authentication required"}, 401
        notes = Note.query.filter_by(user_id=user.id).all()
        return [{"id": n.id, "title": n.title, "content": n.content, "created_at": n.created_at.isoformat()} for n in notes], 200

    @jwt_required()
    def post(self):
        user = authenticate_request()
        if not user:
            return {"message": "Authentication required"}, 401
        data = note_parser.parse_args()
        new_note = Note(title=data['title'], content=data['content'], user_id=user.id)
        db.session.add(new_note)
        db.session.commit()
        return {"message": "Note created", "note_id": new_note.id}, 201

    @jwt_required()
    def delete(self, note_id):
        user = authenticate_request()
        if not user:
            return {"message": "Authentication required"}, 401
        note = Note.query.get_or_404(note_id)
        if note.user_id != user.id:
            abort(403, description="Forbidden: You do not own this note")
        try:
            db.session.delete(note)
            db.session.commit()
            logger.info(f"Note {note_id} deleted by user {user.id}")
            return {"message": "Note deleted"}, 204
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error deleting note {note_id}: {str(e)}", exc_info=True)
            return {"message": "Failed to delete note", "error": str(e)}, 500

class NoteResource(Resource):
    @jwt_required()
    def get(self, note_id):
        user = authenticate_request()
        if not user:
            return {"message": "Authentication required"}, 401
        note = Note.query.get_or_404(note_id)
        if note.user_id != user.id:
            return {"message": "Forbidden"}, 403
        return {"id": note.id, "title": note.title, "content": note.content, "created_at": note.created_at.isoformat()}, 200

    @jwt_required()
    def patch(self, note_id):
        user = authenticate_request()
        if not user:
            return {"message": "Authentication required"}, 401
        note = Note.query.get_or_404(note_id)
        if note.user_id != user.id:
            return {"message": "Forbidden"}, 403
        data = note_parser.parse_args()
        if data['title'] is not None:
            note.title = data['title']
        if data['content'] is not None:
            note.content = data['content']
        db.session.commit()
        return {"message": "Note updated"}, 200

    @jwt_required()
    def put(self, note_id):
        user = authenticate_request()
        if not user:
            return {"message": "Authentication required"}, 401
        note = Note.query.get_or_404(note_id)
        if note.user_id != user.id:
            return {"message": "Forbidden"}, 403
        data = note_parser.parse_args()
        note.title = data['title']
        note.content = data['content']
        db.session.commit()
        return {"message": "Note updated"}, 200

# Resources
api.add_resource(Login, '/api/v1/login')
api.add_resource(Register, '/api/v1/register')
api.add_resource(Users, '/api/v1/users')
api.add_resource(UserResource, '/api/v1/users/<int:user_id>')
api.add_resource(Notes, '/api/v1/notes')
api.add_resource(NoteResource, '/api/v1/notes/<int:note_id>')