from flask import Flask
import os
from dotenv import load_dotenv
from prometheus_flask_exporter import PrometheusMetrics
from prometheus_client import Counter, Gauge, Histogram


review_counter = Counter(
    'resturant_reviews_total',
    'Total number of restaurant reviews analyzed',
    ['sentiment']
)

user_feedback_counter = Counter(
    'user_feedback_total',
    'User feedback on sentiment analysis results',
    ['feedback', 'sentiment']
)

current_users_gauge = Gauge(
    'active_users_count', 
    'Number of users currently using the application'
)

sentiment_analysis_duration = Histogram(
    'sentiment_analysis_duration_seconds',
    'Time spent processing sentiment analysis',
    buckets=[0.1, 0.25, 0.5, 0.75, 1.0, 2.5, 5.0]
)



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
    
    app = Flask(__name__, static_folder="static")
    
    app_settings = os.getenv("APP_SETTINGS", "config.DevelopmentConfig")
    app.config.from_object(app_settings)
    app.config["VERSION"] = get_version()
    app.config['MODEL_SERVICE_URL'] = os.environ.get('MODEL_SERVICE_URL', 'http://model-service:3000')
    app.config['PORT'] = os.environ.get("PORT", 5000)
    
    metrics = PrometheusMetrics(
        app,
        path='/metrics',          
        export_defaults=True,     
        group_by_endpoint=True    
    )
    
    metrics.info('app_info', 'Application info', version=app.config["VERSION"])
    
    # Register two modules
    from app.routes import main_bp, model_bp, metrics_bp
    app.register_blueprint(main_bp)
    app.register_blueprint(model_bp)
    app.register_blueprint(metrics_bp)
    
    
    return app