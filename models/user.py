# user.py
from database import db
from datetime import datetime, timezone
from sqlalchemy import Text

class User(db.Model):
    __tablename__='users'
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(50), unique = True, nullable = False, index=True)
    email = db.Column(db.String(255), unique = True, nullable = False, index=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    password = db.Column(Text, nullable = False)
    status = db.Column(db.String(20), nullable = False, default = "user")
    failed_login_attempts = db.Column(db.Integer, nullable=False, default=0)
    locked_until = db.Column(db.DateTime, nullable=True)
    email_verified = db.Column(db.Boolean, nullable=False, default=False)
    notes = db.relationship('Note', backref='user', lazy=True, cascade='all, delete-orphan')

    def __init__(self, username, email, password):
        self.username = username
        self.email = email
        self.password = password

    def __repr__(self):
        return f'<User {self.username}>'