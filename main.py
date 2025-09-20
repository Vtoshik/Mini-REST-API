# main.py
# Libraries
from flask import Flask
from flask_migrate import Migrate
from urllib.parse import unquote
from dotenv import load_dotenv
import os
from flask_jwt_extended import JWTManager
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_cors import CORS

# Files
from database import db
from models.user import User
from models.note import Note
from api_routes import api_bp
from user_routes import user_bp
from admin_routes import admin_bp
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
app.config['JWT_TOKEN_LOCATION'] = ['headers']
app.config['RATELIMIT_STORAGE_URI'] = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')

db.init_app(app)
migrate = Migrate(app, db)
jwt = JWTManager(app)
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"],
    storage_uri=app.config['RATELIMIT_STORAGE_URI']  # Use Redis storage
)
limiter.init_app(app)
CORS(app, resources={r"/api/v1/*": {"origins": ["http://localhost:3000"]}})

app.register_blueprint(user_bp)
app.register_blueprint(api_bp)
app.register_blueprint(admin_bp, url_prefix='/admin')

# Apply rate limiting to login and register
@limiter.limit("10 per minute")
def limited_login():
    return Login().post()
@limiter.limit("5 per minute")
def limited_register():
    return Register().post()

app.add_url_rule('/api/v1/login', view_func=limited_login, methods=['POST'])
app.add_url_rule('/api/v1/register', view_func=limited_register, methods=['POST'])

if __name__ == "__main__":
    app.run(debug=True)