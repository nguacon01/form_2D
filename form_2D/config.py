import os
import datetime
from datetime import timedelta

class Config(object):
    basedir = os.path.abspath(os.path.dirname(__file__))
    TESTING = False
    SECRET_KEY = "X8slQiQWkvC0Zytlrntx9NQB009oOOg5r5kiah68NkckksDyuguwkz0KCV9lK3P5"
    DEBUG = True

    # SQLAMCHEMY COFIGS
    SQLALCHEMY_DATABASE_URI = "sqlite:///" + os.path.join(basedir, "site.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # JWT CONFIGS
    JWT_TOKEN_LOCATION = "cookies"
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=30)

    # SESSION CONFIGS
    PERMANENT_SESSION_LIFETIME =  timedelta(minutes=30)

    def __str__(self) -> str:
        return 'this production config'
    

class ProductionConfig(Config):
    pass

class DevelopmentConfig(Config):
    TESTING = True
    DEBUG = True
