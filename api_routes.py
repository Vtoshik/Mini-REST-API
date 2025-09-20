# api_routes.py
from database import db
from models.user import User
from models.note import Note
from flask import request, Blueprint, abort
from werkzeug.security import generate_password_hash, check_password_hash
from flask_restful import Api, Resource, reqparse
from flask_jwt_extended import jwt_required, create_access_token, get_jwt_identity
from sqlalchemy.exc import IntegrityError
from schemas import UserRegisterSchema, NoteSchema, UserSchema, UserUpdateSchema, LoginSchema, NoteCreateSchema, NoteUpdateSchema
from marshmallow import ValidationError
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

api_bp = Blueprint('api_bp', __name__)
api = Api(api_bp)

note_parser = reqparse.RequestParser()
note_parser.add_argument('title', type=str, required=True, help='Title required')
note_parser.add_argument('content', type=str, required=False)

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
        schema = LoginSchema()
        try:
            data = schema.load(request.get_json())
        except ValidationError as error:
            return {"error": "validation_error", "message": error.messages, "code": 400}, 400
        user = User.query.filter_by(username=data['username']).first()
        if user and check_password_hash(user.password, data['password']):
            access_token = create_access_token(identity=str(user.id))
            logger.debug(f"Login successful for user {data['username']}, token created")
            return {"message": "Login successful", 'access_token': access_token, 'user_id': user.id, 'user_status': user.status}, 200
        return {"message": "Invalid credentials"}, 401

           
class Register(Resource):
    def post(self):
        schema = UserRegisterSchema()
        try:
            data = schema.load(request.get_json())
        except ValidationError as error:
            return {"errors": error.messages}, 400
        existing_user = User.query.filter(
            (User.email == data['email']) | (User.username == data['username'])
        ).first()
        if existing_user:
            return {"message": "User with this email or username already exists."}, 400

        hashed_password = generate_password_hash(data['password'])
        user = User(username=data['username'], email=data['email'], password=hashed_password)
        try:
            db.session.add(user)
            db.session.commit()
            return {"message": "User created successfully", "user_id": user.id}, 201
        except IntegrityError:
            db.session.rollback()
            return {"message": "User with this email or username already exists."}, 400
        except Exception as e:
            db.session.rollback()
            return {"message": "Server error"}, 500


class Users(Resource):
    @jwt_required()
    def get(self):
        user = authenticate_request()
        if not user:
            return {"message": "Authentication required"}, 401
        if user.status != 'admin':
            return {"message": "Admin access required"}, 403
        users = User.query.all()
        users_schema = UserSchema(many=True)
        return users_schema.dump(users), 200

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
        schema = UserUpdateSchema(partial=True)
        try:
            data = schema.load(request.get_json())
        except ValidationError as error:
            return {"errors": error.messages}, 400
        target_user = User.query.get_or_404(user_id)
        # Update fields from validated data
        if 'username' in data:
            target_user.username = data['username']
        if 'email' in data:
            target_user.email = data['email']
        if 'status' in data:
            target_user.status = data['status']
        if 'password' in data and data['password']:  # Only update if provided
            target_user.password = generate_password_hash(data['password'])
        try:
            db.session.commit()
            return {"message": "User updated"}, 200
        except IntegrityError:
            db.session.rollback()
            return {"message": "User with this email or username already exists."}, 400
        except Exception as e:
            db.session.rollback()
            return {"message": "Server error", "error": str(e)}, 500

    @jwt_required()
    def delete(self, user_id):
        user = authenticate_request()
        if not user:
            return {"message": "Authentication required"}, 401
        if user.status != 'admin':
            return {"message": "Admin access required"}, 403
        target_user = User.query.get_or_404(user_id)
        try:
            db.session.delete(target_user)
            db.session.commit()
            return {"message": "User deleted"}, 200
        except IntegrityError:
            db.session.rollback()
            return {"message": "User with this with this id does not exist"}, 400
        except Exception as e:
            db.session.rollback()
            return {"message": "Server error"}, 500
    
class Notes(Resource):
    @jwt_required()
    def get(self):
        user = authenticate_request()
        if not user:
            return {"message": "Authentication required"}, 401
        notes = Note.query.filter_by(user_id=user.id).all()
        schema = NoteSchema(many=True)
        return schema.dump(notes), 200

    @jwt_required()
    def post(self):
        user = authenticate_request()
        if not user:
            return {"message": "Authentication required"}, 401
        schema = NoteCreateSchema()
        try:
            data = schema.load(request.get_json())
        except ValidationError as error:
            return {"errors": error.messages}, 400
        new_note = Note(**data, user_id=user.id)
        try: 
            db.session.add(new_note)
            db.session.commit()
            return {"message": "Note created", "note_id": new_note.id}, 201
        except IntegrityError:
            db.session.rollback()
            return {"message": "Note with title already exists"}, 400
        except Exception as e:
            db.session.rollback()
            return {"message": "Server error"}, 500

class NoteResource(Resource):
    @jwt_required()
    def get(self, note_id):
        user = authenticate_request()
        if not user:
            return {"message": "Authentication required"}, 401
        note = Note.query.get_or_404(note_id)
        if note.user_id != user.id:
            return {"message": "Forbidden"}, 403
        schema = NoteSchema(); 
        return schema.dump(note), 200

    @jwt_required()
    def patch(self, note_id):
        user = authenticate_request()
        if not user:
            return {"message": "Authentication required"}, 401
        
        note = Note.query.get_or_404(note_id)
        if note.user_id != user.id:
            return {"message": "Forbidden"}, 403

        schema = NoteUpdateSchema(partial=True)
        try:
            data = schema.load(request.get_json())
        except ValidationError as error:
            return {"errors": error.messages}, 400
            
        # Update fields from validated data
        if 'title' in data:
            note.title = data['title']
        if 'content' in data:
            note.content = data['content']

        try:
            db.session.commit()
            schema = NoteSchema()
            return {"message": "Note updated", "data": schema.dump(note)}, 200
        except IntegrityError:
            db.session.rollback()
            return {"message": "Note with this title already exist"}, 400
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error updating note {note_id}: {str(e)}", exc_info=True)
            return {"message": "Server error", "error": str(e)}, 500

    @jwt_required()
    def delete(self, note_id):
        user = authenticate_request()
        if not user:
            return {"message": "Authentication required"}, 401
        note = Note.query.get_or_404(note_id)
        if note.user_id != user.id:
            return {"message": "Forbidden"}, 403
        try:
            db.session.delete(note)
            db.session.commit()
            logger.info(f"Note {note_id} deleted by user {user.id}")
            return {"message": "Note deleted"}, 204
        except IntegrityError:
            db.session.rollback()
            return {"message": "Note with this id does not exist"}, 400
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error deleting note {note_id}: {str(e)}", exc_info=True)
            return {"message": "Failed to delete note", "error": str(e)}, 500

# Resources
api.add_resource(Login, '/api/v1/login')
api.add_resource(Register, '/api/v1/register')
api.add_resource(Users, '/api/v1/admin/users')
api.add_resource(UserResource, '/api/v1/admin/users/<int:user_id>')
api.add_resource(Notes, '/api/v1/notes')
api.add_resource(NoteResource, '/api/v1/notes/<int:note_id>')