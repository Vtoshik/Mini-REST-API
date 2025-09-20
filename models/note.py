# note.py
from database import db
from datetime import datetime, timezone
from sqlalchemy import Text

class Note(db.Model):
    __tablename__='notes'
    __table_args__ = (db.UniqueConstraint('user_id', 'title', name='unique_user_title'),)
    id = db.Column(db.Integer, primary_key = True)
    title = db.Column(db.String(20), nullable = False)
    content = db.Column(Text, unique = False, nullable = True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable = False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    def __init__(self, title, content, user_id):
        self.title = title
        self.content = content
        self.user_id = user_id

    def __repr__(self):
        return f"Note(id={self.id}, title='{self.title}', content='{self.content}', created_at='{self.created_at}')"
    
    def json(self):
        return {
            "id": self.id,
            "title": self.title,
            "content": self.content,
            "user_id": self.user_id,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }