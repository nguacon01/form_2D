from flask import Flask
from .config import DevelopmentConfig
from flask_assets import Environment
from .extensions import db, bcrypt, login_manager, filehandle
from .config import Config, DevelopmentConfig


def create_app():
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(DevelopmentConfig)
    # app.config.from_pyfile('config.py', silent=True)
    
    assets = Environment()
    with app.app_context():

        # add extensions
        assets.init_app(app)
        db.init_app(app)
        bcrypt.init_app(app)
        login_manager.init_app(app)

        #Blueprints imports
        from .main.views import main
        from .metadata.views import metadata
        from .auth.views import auth
        from .errors.handlers import errors
        from .assets import compile_static_assets

        app.register_blueprint(main)
        app.register_blueprint(metadata, url_prefix = "/metadata")
        app.register_blueprint(auth, url_prefix = "/auth")
        app.register_blueprint(errors, url_predix="/error")

        compile_static_assets(assets)
        db.create_all()

        # add log handler
        app.logger.addHandler(filehandle)
        
        return app

# app = create_app()
# from .utils import filters