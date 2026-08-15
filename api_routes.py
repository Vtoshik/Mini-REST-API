# api_routes.py
from database import db
from models.user import User
from models.note import Note
from models.password_reset_token import PasswordResetToken
from models.email_verification_token import EmailVerificationToken
from flask import request, Blueprint, abort, jsonify, make_response
from werkzeug.security import generate_password_hash, check_password_hash
from flask_restful import Api, Resource
from flask_jwt_extended import jwt_required, create_access_token, get_jwt_identity, set_access_cookies, unset_jwt_cookies
from sqlalchemy.exc import IntegrityError
from schemas import (
    UserRegisterSchema, NoteSchema, UserSchema, UserUpdateSchema, LoginSchema,
    NoteCreateSchema, NoteUpdateSchema, SelfUpdateSchema, PasswordChangeSchema,
    PasswordResetSchema, EmailVerificationSchema,
)
from marshmallow import ValidationError
import logging
import secrets
from datetime import datetime, timedelta, timezone
from flask_wtf.csrf import validate_csrf, generate_csrf
from flask_jwt_extended.exceptions import JWTExtendedException
from jwt.exceptions import PyJWTError

PASSWORD_RESET_TOKEN_LIFETIME = timedelta(hours=1)
EMAIL_VERIFICATION_TOKEN_LIFETIME = timedelta(hours=24)
LOGIN_LOCKOUT_THRESHOLD = 5
LOGIN_LOCKOUT_DURATION = timedelta(minutes=15)

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

api_bp = Blueprint('api_bp', __name__)
api = Api(api_bp)

CSRF_EXEMPT_ENDPOINTS = {'api_bp.login', 'api_bp.register', 'api_bp.logout', 'api_bp.verifyemail'}

@api_bp.before_request
def check_csrf_token():
    if request.endpoint in CSRF_EXEMPT_ENDPOINTS:
        return
    if request.method in ['POST', 'PUT', 'PATCH', 'DELETE']:
        csrf_token = request.headers.get('X-CSRF-Token')
        try:
            validate_csrf(csrf_token)
        except Exception as e:
            logger.error(f"CSRF validation error: {str(e)}")
            return jsonify({"message": "The CSRF token is missing or invalid."}), 400

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

def _is_locked(user):
    locked_until = user.locked_until
    if not locked_until:
        return False
    if locked_until.tzinfo is None:
        locked_until = locked_until.replace(tzinfo=timezone.utc)
    return locked_until > datetime.now(timezone.utc)

def authenticate_and_check_admin():
    user = authenticate_request()
    if not user or user.status != 'admin':
        abort(403, "Admin access required")
    return user

@api_bp.errorhandler(JWTExtendedException)
@api_bp.errorhandler(PyJWTError)
def handle_jwt_error(e):
    logger.warning(f"JWT error: {str(e)}")
    return {"message": "Authentication required"}, 401

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

        if user and _is_locked(user):
            return {"message": "Account temporarily locked after too many failed attempts. Try again later."}, 423

        if user and check_password_hash(user.password, data['password']):
            if not user.email_verified:
                return {"message": "Please verify your email before logging in."}, 403
            user.failed_login_attempts = 0
            user.locked_until = None
            db.session.commit()
            access_token = create_access_token(identity=str(user.id))
            logger.debug(f"Login successful for user {data['username']}, token created")
            response = jsonify({"message": "Login successful", 'user_id': user.id, 'user_status': user.status})
            set_access_cookies(response, access_token)
            flask_response = make_response(response)
            return flask_response

        if user:
            user.failed_login_attempts += 1
            if user.failed_login_attempts >= LOGIN_LOCKOUT_THRESHOLD:
                user.locked_until = datetime.now(timezone.utc) + LOGIN_LOCKOUT_DURATION
            db.session.commit()
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
        except IntegrityError:
            db.session.rollback()
            return {"message": "User with this email or username already exists."}, 400
        except Exception as e:
            db.session.rollback()
            return {"message": "Server error"}, 500

        # No email service is configured, so — same as the admin password
        # reset flow — the verification link is returned directly rather
        # than emailed. A real deployment would email this instead.
        verify_token = EmailVerificationToken(
            token=secrets.token_urlsafe(32),
            user_id=user.id,
            expires_at=datetime.now(timezone.utc) + EMAIL_VERIFICATION_TOKEN_LIFETIME,
        )
        db.session.add(verify_token)
        db.session.commit()
        return {
            "message": "User created successfully",
            "user_id": user.id,
            "verify_token": verify_token.token,
            "verify_path": f"/verify-email/{verify_token.token}",
        }, 201


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

    @jwt_required()
    def post(self):
        user = authenticate_request()
        if not user:
            return {"message": "Authentication required"}, 401
        if user.status != 'admin':
            return {"message": "Admin access required"}, 403
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
        new_user = User(username=data['username'], email=data['email'], password=hashed_password)
        # Admin vouches for the email directly here, unlike self-registration
        # — there's no verification link issued on this path, so leaving
        # email_verified False would lock the account out permanently.
        new_user.email_verified = True
        try:
            db.session.add(new_user)
            db.session.commit()
            return {"message": "User created successfully", "user_id": new_user.id}, 201
        except IntegrityError:
            db.session.rollback()
            return {"message": "User with this email or username already exists."}, 400
        except Exception as e:
            db.session.rollback()
            return {"message": "Server error"}, 500

class UserResource(Resource):
    @jwt_required()
    def get(self, user_id):
        user = authenticate_request()
        if not user:
            return {"message": "Authentication required"}, 401
        if user.status != 'admin':
            return {"message": "Forbidden"}, 403
        target_user = User.query.get_or_404(user_id)
        return {
            "id": target_user.id,
            "username": target_user.username,
            "email": target_user.email,
            "status": target_user.status,
            "created_at": target_user.created_at.isoformat()
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
            if user.status != 'admin':
                return {"message": "Only admins can change account status"}, 403
            target_user.status = data['status']
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
        if target_user.id == user.id:
            return {"message": "You cannot delete your own account"}, 400
        if target_user.status == 'admin' and User.query.filter_by(status='admin').count() <= 1:
            return {"message": "Cannot delete the last remaining admin account"}, 400
        try:
            db.session.delete(target_user)
            db.session.commit()
            return {"message": "User deleted"}, 200
        except IntegrityError:
            db.session.rollback()
            return {"message": "Cannot delete user due to database constraints"}, 400
        except Exception as e:
            db.session.rollback()
            return {"message": "Server error"}, 500
    
class Notes(Resource):
    @jwt_required()
    def get(self):
        user = authenticate_request()
        if not user:
            return {"message": "Authentication required"}, 401
        notes = Note.query.filter_by(user_id=user.id).filter(Note.deleted_at.is_(None)).all()
        schema = NoteSchema(many=True)
        return schema.dump(notes), 200

    @jwt_required()
    def post(self):
        user = authenticate_request()
        if not user:
            return {"message": "Authentication required"}, 401
        logger.debug(f"Received payload: {request.get_json()}")
        schema = NoteCreateSchema()
        try:
            data = schema.load(request.get_json())
        except ValidationError as error:
            return {"message": "Validation error", "errors": error.messages}, 400
        new_note = Note(**data, user_id=user.id)
        try: 
            db.session.add(new_note)
            db.session.commit()
            return {"message": "Note created", "data": {"note_id": new_note.id}}, 201
        except IntegrityError:
            db.session.rollback()
            return {"message": "Note with this title already exists for this user"}, 400
        except Exception as e:
            db.session.rollback()
            return {"message": "Server error", "error": str(e)}, 500

class NoteResource(Resource):
    @jwt_required()
    def get(self, note_id):
        user = authenticate_request()
        if not user:
            return {"message": "Authentication required"}, 401
        note = Note.query.get_or_404(note_id)
        if note.user_id != user.id:
            return {"message": "Forbidden"}, 403
        if note.deleted_at is not None:
            abort(404)
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
        if note.deleted_at is not None:
            abort(404)

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
        if 'category' in data:
            note.category = data['category']
        if 'pinned' in data:
            note.pinned = data['pinned']

        try:
            db.session.commit()
            schema = NoteSchema()
            return {"message": "Note updated", "data": schema.dump(note)}, 200
        except IntegrityError:
            db.session.rollback()
            return {"message": "Note with this title already exists for this user"}, 400
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
        if note.deleted_at is not None:
            abort(404)
        try:
            note.deleted_at = datetime.now(timezone.utc)
            db.session.commit()
            logger.info(f"Note {note_id} moved to trash by user {user.id}")
            return {"message": "Note moved to trash"}, 200
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error trashing note {note_id}: {str(e)}", exc_info=True)
            return {"message": "Failed to delete note", "error": str(e)}, 500

class Trash(Resource):
    @jwt_required()
    def get(self):
        user = authenticate_request()
        if not user:
            return {"message": "Authentication required"}, 401
        notes = (
            Note.query.filter_by(user_id=user.id)
            .filter(Note.deleted_at.isnot(None))
            .order_by(Note.deleted_at.desc())
            .all()
        )
        schema = NoteSchema(many=True)
        return schema.dump(notes), 200

class NoteRestore(Resource):
    @jwt_required()
    def post(self, note_id):
        user = authenticate_request()
        if not user:
            return {"message": "Authentication required"}, 401
        note = Note.query.get_or_404(note_id)
        if note.user_id != user.id:
            return {"message": "Forbidden"}, 403
        if note.deleted_at is None:
            abort(404)
        try:
            note.deleted_at = None
            db.session.commit()
            return {"message": "Note restored"}, 200
        except IntegrityError:
            db.session.rollback()
            return {"message": "Note with this title already exists for this user"}, 400

class NotePermanentDelete(Resource):
    @jwt_required()
    def delete(self, note_id):
        user = authenticate_request()
        if not user:
            return {"message": "Authentication required"}, 401
        note = Note.query.get_or_404(note_id)
        if note.user_id != user.id:
            return {"message": "Forbidden"}, 403
        if note.deleted_at is None:
            abort(404)
        db.session.delete(note)
        db.session.commit()
        return {"message": "Note permanently deleted"}, 200

class Logout(Resource):
    def post(self):
        response = jsonify({"message": "Logout successful"})
        unset_jwt_cookies(response)
        return make_response(response)

class CsrfToken(Resource):
    def get(self):
        return {"csrf_token": generate_csrf()}, 200

class Me(Resource):
    @jwt_required()
    def get(self):
        user = authenticate_request()
        if not user:
            return {"message": "Authentication required"}, 401
        return {"id": user.id, "username": user.username, "email": user.email, "status": user.status}, 200

    @jwt_required()
    def put(self):
        user = authenticate_request()
        if not user:
            return {"message": "Authentication required"}, 401
        schema = SelfUpdateSchema(partial=True)
        try:
            data = schema.load(request.get_json())
        except ValidationError as error:
            return {"errors": error.messages}, 400
        if 'username' in data:
            user.username = data['username']
        if 'email' in data:
            user.email = data['email']
        try:
            db.session.commit()
            return {"message": "Profile updated"}, 200
        except IntegrityError:
            db.session.rollback()
            return {"message": "User with this email or username already exists."}, 400
        except Exception as e:
            db.session.rollback()
            return {"message": "Server error", "error": str(e)}, 500

class MePassword(Resource):
    @jwt_required()
    def post(self):
        user = authenticate_request()
        if not user:
            return {"message": "Authentication required"}, 401
        schema = PasswordChangeSchema()
        try:
            data = schema.load(request.get_json())
        except ValidationError as error:
            return {"errors": error.messages}, 400
        if not check_password_hash(user.password, data['current_password']):
            return {"message": "Current password is incorrect"}, 400
        user.password = generate_password_hash(data['new_password'])
        db.session.commit()
        return {"message": "Password updated"}, 200

class AdminPasswordReset(Resource):
    @jwt_required()
    def post(self, user_id):
        authenticate_and_check_admin()
        target_user = User.query.get_or_404(user_id)
        # Drop this user's previous unused tokens rather than letting one
        # pile up per reset request — old ones are useless once a fresh
        # token is issued anyway.
        PasswordResetToken.query.filter_by(user_id=target_user.id, used=False).delete()
        token = PasswordResetToken(
            token=secrets.token_urlsafe(32),
            user_id=target_user.id,
            expires_at=datetime.now(timezone.utc) + PASSWORD_RESET_TOKEN_LIFETIME,
        )
        db.session.add(token)
        db.session.commit()
        return {
            "message": "Password reset token created",
            "reset_token": token.token,
            "reset_path": f"/reset-password/{token.token}",
        }, 201

class PasswordReset(Resource):
    def post(self):
        schema = PasswordResetSchema()
        try:
            data = schema.load(request.get_json())
        except ValidationError as error:
            return {"errors": error.messages}, 400
        token = PasswordResetToken.query.filter_by(token=data['token']).first()
        if not token or not token.is_valid():
            return {"message": "This reset link is invalid or has expired"}, 400
        user = User.query.get_or_404(token.user_id)
        user.password = generate_password_hash(data['password'])
        token.used = True
        db.session.commit()
        return {"message": "Password reset successful"}, 200

class VerifyEmail(Resource):
    def post(self):
        schema = EmailVerificationSchema()
        try:
            data = schema.load(request.get_json())
        except ValidationError as error:
            return {"errors": error.messages}, 400
        token = EmailVerificationToken.query.filter_by(token=data['token']).first()
        if not token or not token.is_valid():
            return {"message": "This verification link is invalid or has expired"}, 400
        user = User.query.get_or_404(token.user_id)
        user.email_verified = True
        token.used = True
        db.session.commit()
        return {"message": "Email verified"}, 200

# Resources
api.add_resource(Logout, '/api/v1/logout')
api.add_resource(Login, '/api/v1/login')
api.add_resource(Register, '/api/v1/register')
api.add_resource(CsrfToken, '/api/v1/csrf-token')
api.add_resource(Me, '/api/v1/me')
api.add_resource(MePassword, '/api/v1/me/password')
api.add_resource(PasswordReset, '/api/v1/reset-password')
api.add_resource(VerifyEmail, '/api/v1/verify-email')
api.add_resource(Users, '/api/v1/admin/users')
api.add_resource(UserResource, '/api/v1/admin/users/<int:user_id>')
api.add_resource(AdminPasswordReset, '/api/v1/admin/users/<int:user_id>/reset-password')
api.add_resource(Notes, '/api/v1/notes')
api.add_resource(Trash, '/api/v1/notes/trash')
api.add_resource(NoteResource, '/api/v1/notes/<int:note_id>')
api.add_resource(NoteRestore, '/api/v1/notes/<int:note_id>/restore')
api.add_resource(NotePermanentDelete, '/api/v1/notes/<int:note_id>/permanent')