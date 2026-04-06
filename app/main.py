"""
Application configuration and factory
"""
import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from .database import init_db, close_db

# Initialize Flask and SQLAlchemy
app = Flask(__name__)

# Load configuration from environment or use defaults
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
app.config['DATABASE_URI'] = os.environ.get('DATABASE_URI') or 'sqlite:///ssl_monitor.db'
app.config['CACHE_EXPIRATION_HOURS'] = 24

# Configure database
app.config['SQLALCHEMY_DATABASE_URI'] = app.config['DATABASE_URI']
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize database
db = SQLAlchemy(app)

# Initialize custom database tables
init_db(app)

# Register blueprints
from .routes import main_bp
app.register_blueprint(main_bp)

# Register teardown handler
app.teardown_appcontext(close_db)

# Import and test
with app.app_context():
    pass
