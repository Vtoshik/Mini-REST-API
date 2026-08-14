# password_reset_token.py
from database import db
from datetime import datetime, timezone

class PasswordResetToken(db.Model):
    __tablename__ = 'password_reset_tokens'
    id = db.Column(db.Integer, primary_key=True)
    token = db.Column(db.String(64), unique=True, nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    expires_at = db.Column(db.DateTime, nullable=False)
    used = db.Column(db.Boolean, nullable=False, default=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    def __init__(self, token, user_id, expires_at):
        self.token = token
        self.user_id = user_id
        self.expires_at = expires_at

    def is_valid(self):
        expires_at = self.expires_at
        if expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=timezone.utc)
        return not self.used and expires_at > datetime.now(timezone.utc)

    def __repr__(self):
        return f'<PasswordResetToken user_id={self.user_id} used={self.used}>'
