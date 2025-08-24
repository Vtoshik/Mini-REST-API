from main.py import db

class Note(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    title = db.Column(db.String(20), unique = False, nullable = False)
    content = db.Column(db.String(1000), unique = False, nullable = True)
    user_id = db.Column(db.Integer, unique = False, nullable = False)
    created_at = db.Column() #TODO

    def __repr__(self):
        return f"Name : {self.id}, title : {self.title}, content : {self.content}, created_at: {self.created_at}"