from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from config import Config

db = SQLAlchemy()
login_manager = LoginManager()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'  # Assuming 'auth' blueprint for login route

    from . import models # Import models here to avoid circular imports

    # Import and register blueprints here
    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint, url_prefix='/auth')

    from .main_routes import main_bp # Register main_bp for HTML pages
    app.register_blueprint(main_bp) # No prefix, or use url_prefix='/'

    from .main_routes import api_bp # Register api_bp for API endpoints
    app.register_blueprint(api_bp, url_prefix='/api') # Prefix for all API routes

    return app

app = create_app() # Create the app instance

# The following lines are for creating DB tables.
# It's better to do this via a CLI command.
# For example, in run.py or a manage.py script:
#
# @app.cli.command("init-db")
# def init_db_command():
#     """Creates the database tables."""
#     with app.app_context():
#         db.create_all()
#     print("Initialized the database.")
#
# This keeps db creation separate from app run.
