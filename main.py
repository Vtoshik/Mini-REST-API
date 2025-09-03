# main.py
# Libraries
from flask import Flask, render_template, request, redirect
from flask_migrate import Migrate
from urllib.parse import unquote
from dotenv import load_dotenv
import psycopg2
import os

# Files
from database import db
from models.user import User
from models.note import Note
from routes import user_bp

app = Flask(__name__)

load_dotenv()

database_url = os.environ.get("DATABASE_URL")

if database_url:
    database_url = unquote(database_url)

# Test connection with psycopg2
try:
    conn = psycopg2.connect(database_url)
    cursor = conn.cursor()
    cursor.execute("SELECT current_database();")
    db_name = cursor.fetchone()[0]
    print(f"Connected to database: {db_name}")
    conn.close()
except Exception as e:
    print("Error connection:", e)

if not database_url:
    raise ValueError("DATABASE_URL environment variable is not set")

# Configure PostgreSQL database
app.config['SQLALCHEMY_DATABASE_URI'] = database_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False # Avoids warning
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY','dev_secret_key')

db.init_app(app)
migrate = Migrate(app, db)
app.register_blueprint(user_bp)

if __name__ == "__main__":
    app.run(debug=True)