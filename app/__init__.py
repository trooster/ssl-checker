"""
SSL Certificate Monitor Application
A web application to monitor SSL certificate expiration dates for multiple domains.
"""

from flask import Flask
from .config import Config
from .database import init_db, close_db

def create_app(config_class=None):
    app = Flask(__name__)
    
    if config_class:
        app.config.from_object(config_class)
    else:
        app.config.from_object(Config)
    
    # Initialize database
    init_db(app)
    
    # Register blueprints
    from .routes import main_bp
    app.register_blueprint(main_bp)
    
    # Register teardown handler for database cleanup
    app.teardown_appcontext(close_db)
    
    return app
