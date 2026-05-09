"""
Application factory and initialization module.
Creates and configures the Flask application with all extensions.
"""

import os
import logging
from logging.handlers import RotatingFileHandler
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from config import config_by_name

# Initialize extensions
db = SQLAlchemy()
login_manager = LoginManager()
csrf = CSRFProtect()


def create_app(config_name="default"):
    """
    Create and configure the Flask application.
    
    Args:
        config_name (str): Configuration environment name
        
    Returns:
        Flask: Configured Flask application instance
    """
    # Get the parent directory (project root)
    import os as os_module
    project_root = os_module.path.dirname(os_module.path.dirname(os_module.path.abspath(__file__)))
    
    app = Flask(
        __name__,
        template_folder=os_module.path.join(project_root, 'templates'),
        static_folder=os_module.path.join(project_root, 'static')
    )
    
    # Load configuration
    app.config.from_object(config_by_name[config_name])
    
    # Create upload folder if it doesn't exist
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
    
    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)
    
    # Configure login manager
    login_manager.login_view = "login"
    login_manager.login_message = "Please log in to access this page."
    login_manager.login_message_category = "info"
    
    # Import models for table creation
    from app.models import User, Transaction
    
    # Create tables with error handling
    with app.app_context():
        try:
            db.create_all()
            app.logger.info("Database tables created successfully")
        except Exception as e:
            app.logger.warning(f"Could not create database tables: {str(e)}")
            app.logger.warning("The database will be created on first request if available")
    
    # User loader
    @login_manager.user_loader
    def load_user(user_id):
        """Load user by ID for session management."""
        try:
            return User.query.get(int(user_id))
        except Exception as e:
            app.logger.error(f"Error loading user: {str(e)}")
            return None
    
    # Register routes
    from app.routes import register_routes
    register_routes(app)
    
    # Configure logging
    setup_logging(app)
    
    return app


def setup_logging(app):
    """
    Configure application logging.
    
    Args:
        app (Flask): Flask application instance
    """
    if not app.debug and not app.testing:
        # Create logs directory if it doesn't exist
        os.makedirs("logs", exist_ok=True)
        
        # File handler with rotating backups
        file_handler = RotatingFileHandler(
            "logs/xpensetrack.log",
            maxBytes=10240000,  # 10MB
            backupCount=10
        )
        
        # Format
        file_handler.setFormatter(logging.Formatter(
            "%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]"
        ))
        
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
        app.logger.setLevel(logging.INFO)
        app.logger.info("XpenseTrack startup")
