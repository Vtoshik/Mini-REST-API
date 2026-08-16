# audit_log.py
from database import db
from datetime import datetime, timezone

class AuditLog(db.Model):
    __tablename__ = 'audit_logs'
    id = db.Column(db.Integer, primary_key=True)
    actor_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
    actor_username = db.Column(db.String(20), nullable=False)
    action = db.Column(db.String(50), nullable=False)
    target_type = db.Column(db.String(20), nullable=False)
    target_id = db.Column(db.Integer, nullable=True)
    details = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), index=True)

    def __init__(self, actor, action, target_type, target_id=None, details=None):
        self.actor_id = actor.id
        self.actor_username = actor.username
        self.action = action
        self.target_type = target_type
        self.target_id = target_id
        self.details = details

    def __repr__(self):
        return f'<AuditLog actor={self.actor_username} action={self.action} target={self.target_type}:{self.target_id}>'
