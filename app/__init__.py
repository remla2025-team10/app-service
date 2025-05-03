from flask import Flask
import os
from dotenv import load_dotenv

def create_app(config_name=None):
    """Application Factory"""
    
    # Load key-value env from `.env` file
    # Available using `os.getenv()``
    # https://12factor.net/config
    load_dotenv()
    
    app = Flask(__name__)
    
    app_settings = os.getenv("APP_SETTINGS", "config.DevelopmentConfig")
    app.config.from_object(app_settings)
    
    # Register two modules
    from app.routes import main_bp, model_bp
    app.register_blueprint(main_bp)
    app.register_blueprint(model_bp)
    
    return app