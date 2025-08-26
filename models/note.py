from database import db
from datetime import datetime, timezone

class Note(db.Model):
    __tablename__='notes'
    id = db.Column(db.Integer, primary_key = True)
    title = db.Column(db.String(20), unique = False, nullable = False)
    content = db.Column(db.String(1000), unique = False, nullable = True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable = False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    def __repr__(self):
        return f"User(id={self.id}, username='{self.username}', email='{self.email}', created_at='{self.created_at}')"