from flask import Blueprint, jsonify, request, current_app, Response
from prometheus_client import generate_latest, REGISTRY
import time
import re
from functools import wraps

from app import (
    version_interactions,
    feedback_metrics,
    conversion_metrics,
    performance_metrics,   
    current_users_gauge, 
    user_feedback_counter, 
    total_predict_times, 
    feedback_total,
    clicks_total, 
    conversion_rate,
    feedback_processing_time,
    get_version
)

metrics_bp = Blueprint('metrics', __name__, url_prefix="/api/metrics")

# Helper functions
def extract_major_version(version_str):
    """Extract the major version number from a version string."""
    if not version_str:
        return ""
    
    # Remove 'v' prefix if present
    if version_str.startswith('v'):
        version_str = version_str[1:]
    
    # Extract major version
    if version_str.isdigit():
        return version_str
    elif '.' in version_str:
        parts = version_str.split('.')
        if parts and parts[0].isdigit():
            return parts[0]
    
    # Try to extract any leading digits
    match = re.match(r'(\d+)', version_str)
    if match:
        return match.group(1)
        
    return version_str

def update_derived_metrics(version):
    """Update derived metrics after changes to base metrics"""
    try:
        # Get click counts
        clicks = 0
        for metric in total_predict_times.collect():
            for sample in metric.samples:
                if sample.name == 'total_predict_times_total' and extract_major_version(sample.labels.get('version')) == version:
                    clicks += sample.value
        
        # Set total clicks metric
        clicks_total.labels(version=version).set(clicks)
        
        # Get feedback counts
        feedback_count = 0
        for labels, counter in user_feedback_counter._metrics.items():
            label_dict = dict(zip(user_feedback_counter._labelnames, labels))
            if extract_major_version(label_dict.get('version', '')) == version:
                feedback_count += counter._value.get()
        
        # Set total feedback metric
        feedback_total.labels(version=version).set(feedback_count)
        
        # Calculate and set conversion rate
        if clicks > 0:
            conversion = (feedback_count / clicks) * 100
        else:
            conversion = 0
        conversion_rate.labels(version=version).set(conversion)
        
        current_app.logger.info(f"Updated derived metrics for version {version}: clicks={clicks}, feedback={feedback_count}, conversion={conversion:.2f}%")
    except Exception as e:
        current_app.logger.error(f"Error updating derived metrics: {e}", exc_info=True)

def update_conversion_metrics(version):
    ''' Upon receiving a click or feedback, update the conversion metrics ''' 
    try:
        # Get click sum
        total_clicks = 0
        for sample in version_interactions.collect():
            for s in sample.samples:
                if (s.name.endswith('_total') and 
                    s.labels.get('version') == version and 
                    s.labels.get('interaction_type') == 'click'):
                    total_clicks += s.value
        
        # Get feedback sum
        total_feedback = 0
        for sample in feedback_metrics.collect():
            for s in sample.samples:
                if s.name.endswith('_total') and s.labels.get('version') == version:
                    total_feedback += s.value
        
        # Set the derived metrics
        conversion_metrics.labels(version=version, metric_type='total_clicks').set(total_clicks)
        conversion_metrics.labels(version=version, metric_type='total_feedback').set(total_feedback)
        
        # Calculate conversion rate
        if total_clicks > 0:
            rate = (total_feedback / total_clicks) * 100
        else:
            rate = 0
        conversion_metrics.labels(version=version, metric_type='rate').set(rate)
        
        return total_clicks, total_feedback, rate
    except Exception as e:
        current_app.logger.error(f"Error updating conversion metrics: {e}", exc_info=True)
        return 0, 0, 0

# Decorator to track timing and update derived metrics
def track_metrics(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        version = extract_major_version(get_version())
        start_time = time.time()
        result = f(*args, **kwargs)
        duration = time.time() - start_time
        
        # Update the derived metrics after processing
        update_derived_metrics(version)
        
        return result
    return decorated_function

# Routes
@metrics_bp.route('/user_visit', methods=['POST'])
@track_metrics
def user_visit():
    version = extract_major_version(get_version())
    current_users_gauge.labels(version=version).inc()
    return jsonify({"status": "success"})

@metrics_bp.route('/user_leave', methods=['POST'])
@track_metrics
def user_leave():
    version = extract_major_version(get_version())
    current_users_gauge.labels(version=version).dec()
    current_app.logger.info("User left the application")
    return jsonify({"status": "success"})

@metrics_bp.route('/click', methods=['POST'])
@track_metrics
def record_click():
    version = extract_major_version(get_version())
    # Add a click interaction
    version_interactions.labels(version=version, interaction_type='click').inc()
    # Update conversion metrics
    update_conversion_metrics(version)
    current_app.logger.info(f"Click recorded for version {version}")
    return jsonify({"status": "success"})
    
@metrics_bp.route('/feedback', methods=['POST'])
@track_metrics
def record_feedback():
    version = extract_major_version(get_version())
    start_time = time.time()
    
    data = request.get_json()
    feedback = data.get('feedback')
    sentiment = data.get('sentiment')
    
    if feedback and sentiment is not None:
        try:
            # 标准化情绪值
            sentiment_str = str(sentiment).lower()
            
            # 记录反馈
            feedback_metrics.labels(
                version=version,
                feedback_type=feedback, 
                sentiment=sentiment_str
            ).inc()
            
            # 更新转化率
            update_conversion_metrics(version)
            
            current_app.logger.info(f"Feedback recorded for version {version}: {feedback}, Sentiment: {sentiment}")
        except Exception as e:
            current_app.logger.error(f"Error recording feedback: {e}", exc_info=True)
    else:
        current_app.logger.warning(f"Incomplete feedback data received: feedback={feedback}, sentiment={sentiment}")
    
    # 记录处理时间
    duration = time.time() - start_time
    performance_metrics.labels(version=version, operation='feedback_processing').observe(duration)
    
    return jsonify({"status": "feedback recorded"})

@metrics_bp.route('/feedback/count', methods=['GET'])
def get_feedback_count():
    # This endpoint can remain for API compatibility, but use derived metrics
    version = extract_major_version(get_version())
    
    # Get the values from our derived metrics
    feedback_count = 0
    clicks_count = 0
    conv_rate = 0
    
    try:
        for metric in feedback_total.collect():
            for sample in metric.samples:
                if sample.labels.get('version') == version:
                    feedback_count = sample.value
        
        for metric in clicks_total.collect():
            for sample in metric.samples:
                if sample.labels.get('version') == version:
                    clicks_count = sample.value
        
        for metric in conversion_rate.collect():
            for sample in metric.samples:
                if sample.labels.get('version') == version:
                    conv_rate = sample.value
    except Exception as e:
        current_app.logger.error(f"Error getting metrics: {e}", exc_info=True)
    
    traffic_distribution = 0.5
    if version == "1":  
        traffic_distribution = 0.1
    elif version == "2":
        traffic_distribution = 0.9
    
    normalized_metrics = {
        "raw_count": feedback_count,
        "prediction_clicks": clicks_count,
        "per_100_clicks": conv_rate,
        "conversion_rate": conv_rate,
        "configured_traffic_distribution": traffic_distribution
    }
    
    return jsonify({
        "status": "success",
        "total_feedback_count": feedback_count,
        "feedback_details": {},  # Simplified, could expand if needed
        "version": version,
        "normalized_metrics": normalized_metrics
    })

@metrics_bp.route('/prometheus', methods=['GET'])
def prometheus_metrics():
    """
    Standard Prometheus metrics endpoint that includes all metrics
    including our derived/aggregated metrics.
    """
    # Get the current state of all versions
    versions = ["1", "2"]
    for version in versions:
        update_derived_metrics(version)
    
    # Check if we have feedback data, if not, consider using fallbacks
    use_fallback = request.args.get('fallback', 'false').lower() == 'true'
    if use_fallback:
        # Check for HTTP metrics indicating feedback calls with no corresponding metrics
        feedback_calls = 0
        for metric in REGISTRY.collect():
            if "http_request" in metric.name:
                for sample in metric.samples:
                    if (sample.name.endswith('_count') and 
                        sample.labels.get('endpoint') == 'metrics.record_feedback' and
                        sample.labels.get('method') == 'POST'):
                        feedback_calls = int(sample.value)
                        break
                if feedback_calls > 0:
                    break
        
        if feedback_calls > 0:
            current_app.logger.warning(f"Found {feedback_calls} feedback calls but metrics may be inconsistent across pods. Using fallback.")
            # Apply fallback logic here if needed
    
    return Response(generate_latest(), mimetype='text/plain')