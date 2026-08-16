# note.py
from database import db
from datetime import datetime, timezone
from sqlalchemy import Text

class Note(db.Model):
    __tablename__='notes'
    __table_args__ = (
        # Partial index instead of a plain UniqueConstraint: a trashed note
        # (deleted_at set) shouldn't block creating a new active note with
        # the same title.
        db.Index(
            'ix_notes_user_title_active', 'user_id', 'title',
            unique=True,
            postgresql_where=db.text('deleted_at IS NULL'),
            sqlite_where=db.text('deleted_at IS NULL'),
        ),
    )
    id = db.Column(db.Integer, primary_key = True)
    title = db.Column(db.String(20), nullable = False)
    content = db.Column(Text, unique = False, nullable = True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable = False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    category = db.Column(db.String(30), nullable=True)
    pinned = db.Column(db.Boolean, nullable=False, default=False)
    deleted_at = db.Column(db.DateTime, nullable=True)

    def __init__(self, title, content, user_id, category=None):
        self.title = title
        self.content = content
        self.user_id = user_id
        self.category = category

    def __repr__(self):
        return f"Note(id={self.id}, title='{self.title}', content='{self.content}', created_at='{self.created_at}')"