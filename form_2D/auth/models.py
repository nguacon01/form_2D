from form_2D import db
from flask_login import UserMixin
import bcrypt

class Users(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key = True, autoincrement = True)
    username = db.Column(db.String(20),nullable = True)
    password = db.Column(db.String(200), nullable = False)
    email = db.Column(db.String(100), nullable = False, unique = True)

    def __init__(self, username, password, email, first_name, last_name, address, phone_nb):
        self.username = username
        self.password = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
        self.email = email
        self.first_name = first_name
        self.last_name = last_name
        self.address = address
        self.phone_nb = phone_nb
    
    def __repr__(self):
        return self.id, self.username

    def check_password(self, password):
        if bcrypt.checkpw(password.encode("utf-8"), self.password):
            return True
        return False
    def set_password(self, password):
        self.password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
