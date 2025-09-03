from database import db
from datetime import datetime, timezone
from sqlalchemy import Text

class User(db.Model):
    __tablename__='users'
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(20), unique = False, nullable = False)
    email = db.Column(db.String(1000), unique = True, nullable = False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    password = db.Column(Text, nullable = False)
    status = db.Column(db.String(20), nullable = False, default = "user")
    notes = db.relationship('Note', backref='user', lazy=True)

    def __repr__(self):
        return f"Name : {self.id}, username : {self.username}, email : {self.email}, created_at: {self.created_at}"