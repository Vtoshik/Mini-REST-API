from main.py import db

class User(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(20), unique = False, nullable = False)
    email = db.Column(db.String(1000), unique = True, nullable = False)
    created_at = db.Column() #TODO

    def __repr__(self):
        return f"Name : {self.id}, username : {self.username}, email : {self.email}, created_at: {self.created_at}"