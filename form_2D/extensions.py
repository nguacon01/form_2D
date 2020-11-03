from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from logging import FileHandler, WARNING

db = SQLAlchemy()
bcrypt = Bcrypt()
login_manager = LoginManager()

filehandle = FileHandler("log.txt")
filehandle.setLevel(WARNING)

