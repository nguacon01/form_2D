import os
import datetime

class Config(object):
    basedir = os.path.abspath(os.path.dirname(__file__))
    TESTING = False
    SECRET_KEY = "X8slQiQWkvC0Zytlrntx9NQB009oOOg5r5kiah68NkckksDyuguwkz0KCV9lK3P5"
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = "sqlite:///" + os.path.join(basedir, "site.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_TOKEN_LOCATION = "cookies"
    JWT_ACCESS_TOKEN_EXPIRES = datetime.timedelta(minutes=30)
    

class ProductionConfig(Config):
    pass

class DevelopmentConfig(Config):
    TESTING = True
    DEBUG = True
    # SQLALCHEMY_DATABASE_URI = "sqlite:///" + os.path.join(Config.basedir, "site.db")
