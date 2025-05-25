import os

# Get the absolute path of the directory where this config.py file is located
basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    # Secret key should be loaded from an environment variable in production
    # A default is provided for development convenience if the env var is not set
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'a-very-secure-default-secret-key-for-dev'

    # Database configuration
    # Prefer DATABASE_URL from environment (e.g., for Heroku Postgres)
    # Fallback to local SQLite database if DATABASE_URL is not set
    # The local SQLite database will be located in the project's root directory as 'app.db'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'app.db')
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
