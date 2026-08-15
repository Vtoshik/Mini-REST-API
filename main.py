# main.py
# Libraries
from flask import Flask, request, jsonify
from flask_migrate import Migrate
from flask_swagger_ui import get_swaggerui_blueprint
from urllib.parse import unquote
from dotenv import load_dotenv
import os
from flask_jwt_extended import JWTManager
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_cors import CORS
from flask_wtf.csrf import CSRFProtect

# Files
from database import db
from models.user import User
from models.note import Note
from models.password_reset_token import PasswordResetToken
from api_routes import api_bp
from api_routes import Login, Register

app = Flask(__name__)
load_dotenv()

database_url = os.environ.get("DATABASE_URL")
if database_url:
    database_url = unquote(database_url)
if not database_url:
    raise ValueError("DATABASE_URL environment variable is not set")

# Configure PostgreSQL database
app.config['SQLALCHEMY_DATABASE_URI'] = database_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False # Avoids warning
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY','dev_secret_key')
app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY', 'super-secret')
app.config['JWT_TOKEN_LOCATION'] = ['headers', 'cookies']
app.config['JWT_COOKIE_SECURE'] = False
app.config['JWT_ACCESS_COOKIE_PATH'] = '/'
app.config['JWT_COOKIE_SAMESITE'] = 'Lax'
app.config['JWT_COOKIE_CSRF_PROTECT'] = False
# Falls back to in-memory storage (single-process only, resets on restart)
# when REDIS_URL isn't set, so the app degrades gracefully instead of every
# request 500ing because Limiter can't reach a Redis it was never told to
# expect. Set REDIS_URL explicitly for multi-process/production deployments,
# where in-memory storage wouldn't share limits across workers.
app.config['RATELIMIT_STORAGE_URI'] = os.environ.get('REDIS_URL', 'memory://')
app.config['WTF_CSRF_ENABLED'] = True

db.init_app(app)
migrate = Migrate(app, db)
jwt = JWTManager(app)
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"],
    storage_uri=app.config['RATELIMIT_STORAGE_URI']  # Use Redis storage
)
limiter.init_app(app)

# The Next.js frontend calls these on every navigation (route gating +
# reading the current session), so they don't fit the same abuse-prevention
# budget as credential-guessing-prone routes like login/register.
NAVIGATION_EXEMPT_PATHS = {'/api/v1/me', '/api/v1/csrf-token'}

@limiter.request_filter
def exempt_navigation_endpoints():
    return request.path in NAVIGATION_EXEMPT_PATHS

csrf = CSRFProtect(app)
CORS(app, resources={r"/api/v1/*": {"origins": ["http://localhost:3000", "http://localhost:5000"], "supports_credentials": True}})

app.register_blueprint(api_bp)
csrf.exempt(api_bp)

# Apply rate limiting to login and register
@limiter.limit("10 per minute")
def limited_login():
    return Login().post()
@limiter.limit("5 per minute")
def limited_register():
    return Register().post()

app.add_url_rule('/api/v1/login', view_func=limited_login, methods=['POST'])
app.add_url_rule('/api/v1/register', view_func=limited_register, methods=['POST'])

# API documentation: a plain route rather than a Resource on api_bp, since
# this describes the API rather than being part of its REST surface, and
# doesn't need the blueprint's CSRF/auth machinery.
@app.route('/api/v1/openapi.json')
def openapi_spec():
    from openapi import spec
    return jsonify(spec.to_dict())

swagger_ui_bp = get_swaggerui_blueprint(
    '/api/v1/docs', '/api/v1/openapi.json', config={'app_name': 'Mini-REST-API'}
)
app.register_blueprint(swagger_ui_bp, url_prefix='/api/v1/docs')

@app.cli.command("seed-db")
def seed_db_command():
    """Create demo accounts and sample notes for local testing."""
    from seed import seed
    seed()

@app.cli.command("cleanup-tokens")
def cleanup_tokens_command():
    """Delete used or expired password reset / email verification tokens. Safe to run on a schedule."""
    from datetime import datetime, timezone
    from models.email_verification_token import EmailVerificationToken
    now = datetime.now(timezone.utc)
    deleted_reset = PasswordResetToken.query.filter(
        db.or_(PasswordResetToken.used.is_(True), PasswordResetToken.expires_at < now)
    ).delete(synchronize_session=False)
    deleted_verify = EmailVerificationToken.query.filter(
        db.or_(EmailVerificationToken.used.is_(True), EmailVerificationToken.expires_at < now)
    ).delete(synchronize_session=False)
    db.session.commit()
    print(f"Deleted {deleted_reset} stale password reset token(s).")
    print(f"Deleted {deleted_verify} stale email verification token(s).")

if __name__ == "__main__":
    app.run(debug=True)