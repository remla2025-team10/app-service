from flask import Flask
import os
from dotenv import load_dotenv
from prometheus_flask_exporter import PrometheusMetrics
from prometheus_client import Counter, Gauge, Histogram, Summary


# 在 app/__init__.py 中定义指标

# 主要交互指标
version_interactions = Counter(
    'version_interactions', 
    'User interactions by type and version', 
    ['version', 'interaction_type']
)

# 反馈指标
feedback_metrics = Counter(
    'feedback_metrics',
    'User feedback metrics',
    ['version', 'feedback_type', 'sentiment']
)

# 转化率（预计算）
conversion_metrics = Gauge(
    'conversion_metrics',
    'Conversion metrics for A/B testing',
    ['version', 'metric_type']  # metric_type: 'rate', 'total_clicks', 'total_feedback'
)

# 性能指标
performance_metrics = Histogram(
    'performance_metrics',
    'Performance metrics for different operations',
    ['version', 'operation'],
    buckets=[0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1, 2.5, 5, 10]
)


review_counter = Counter(
    'restaurant_reviews_total',
    'Total number of restaurant reviews analyzed',
    ['sentiment']
)

sentiment_analysis_duration = Histogram(
    'sentiment_analysis_duration_seconds',
    'Time spent processing sentiment analysis',
    buckets=[0.1, 0.25, 0.5, 0.75, 1.0, 2.5, 5.0]
)

# Base metrics (existing)
current_users_gauge = Gauge('current_users', 'Number of users currently using the application', ['version'])
total_predict_times = Counter('total_predict_times', 'Number of prediction button clicks', ['version'])
user_feedback_counter = Counter('user_feedback', 'User feedback counter', ['version', 'feedback', 'sentiment'])

# Add derived/aggregated metrics for easier querying
feedback_total = Gauge('feedback_total', 'Total feedback count by version', ['version'])
clicks_total = Gauge('clicks_total', 'Total prediction clicks by version', ['version'])
conversion_rate = Gauge('conversion_rate', 'Feedback conversion rate percentage', ['version'])

# Add feedback processing time summary
feedback_processing_time = Summary('feedback_processing_time', 'Time spent processing feedback', ['version'])


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

# Export all metrics through the default /metrics endpoint
from prometheus_client import start_http_server
def setup_metrics(app):
    # Configure Prometheus metrics endpoint
    app.config['PROMETHEUS_METRICS_PORT'] = 8000  # Adjust as needed
    start_http_server(app.config['PROMETHEUS_METRICS_PORT'])