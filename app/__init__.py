from flask import Flask
import os
from dotenv import load_dotenv


def get_version():
    try:
        with open("VERSION", "r") as f:
            return f.read().strip()
    except:
        return "unknown"

def create_app(config_name=None):
    """Application Factory"""
    
    # Load key-value env from `.env` file
    # Available using `os.getenv()``
    # https://12factor.net/config
    load_dotenv()
    
    app = Flask(__name__)
    
    app_settings = os.getenv("APP_SETTINGS", "config.DevelopmentConfig")
    app.config.from_object(app_settings)
    app.config["VERSION"] = get_version()
    app.config['MODEL_SERVICE_URL'] = os.environ.get('MODEL_SERVICE_URL', 'http://localhost:5000')
    
    # Register two modules
    from app.routes import main_bp, model_bp
    app.register_blueprint(main_bp)
    app.register_blueprint(model_bp)
    
    return app