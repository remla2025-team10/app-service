from flask import Blueprint, jsonify, request, current_app, Response
from app import current_users_gauge, user_feedback_counter, total_predict_times, get_version
from prometheus_client import generate_latest

metrics_bp = Blueprint('metrics', __name__, url_prefix="/api/metrics")

@metrics_bp.route('/user_visit', methods=['POST'])
def user_visit():
    version = extract_major_version(get_version())
    current_users_gauge.labels(version=version).inc()
    return jsonify({"status": "success"})

@metrics_bp.route('/user_leave', methods=['POST'])
def user_leave():
    version = extract_major_version(get_version())
    current_users_gauge.labels(version=version).dec()
    current_app.logger.info("User left the application")
    return jsonify({"status": "success"})

@metrics_bp.route('/click', methods=['POST'])
def record_click():
    version = extract_major_version(get_version())
    total_predict_times.labels(version=version).inc()
    return jsonify({"status": "success"})
    
@metrics_bp.route('/feedback', methods=['POST'])
def record_feedback():
    data = request.get_json()
    feedback = data.get('feedback')
    sentiment = data.get('sentiment')
    version = extract_major_version(get_version())
    
    if feedback and sentiment:
        user_feedback_counter.labels(
            version=version,
            feedback=feedback, 
            sentiment=sentiment.lower() if sentiment else 'unknown'
        ).inc()
    current_app.logger.info(f"Feedback recorded: {feedback}, Sentiment: {sentiment}, Version: {version}")
    return jsonify({"status": "feedback recorded"})

@metrics_bp.route('/feedback/count', methods=['GET'])
def get_feedback_count():
    total_count = 0
    version = extract_major_version(get_version())
    feedback_metrics = {}
    
    clicks = 0 
    try:
        for metric in total_predict_times.collect():
            for sample in metric.samples:
                if sample.name == 'total_predict_times_total' and sample.labels.get('version') == version:
                    clicks += sample.value
                    current_app.logger.info(f"Found prediction clicks for version {version}: {sample.value}")
        
    except Exception as e:
        current_app.logger.error(f"Error getting prediction clicks count: {e}")
        clicks = 1
    
    traffic_distribution = 1.0
    if version == "1":  
        traffic_distribution = 0.9
    elif version == "2":
        traffic_distribution = 0.1
    else:
        traffic_distribution = 0.5
    
    for labels, counter in user_feedback_counter._metrics.items():
        # check whether version aligns
        label_dict = dict(zip(user_feedback_counter._labelnames, labels))
        if label_dict.get('version') == version:
            value = counter._value.get()
            total_count += value
            feedback_metrics[str(label_dict)] = value
    
    normalized_metrics = {
        "raw_count": total_count,
        "prediction_clicks": clicks,
        "per_100_clicks": round((total_count / max(clicks, 1)) * 100, 2),
        "conversion_rate": round((total_count / max(clicks, 1)) * 100, 2),
        "configured_traffic_distribution": traffic_distribution
    }
    
    return jsonify({
        "status": "success",
        "total_feedback_count": total_count,
        "feedback_details": feedback_metrics,
        "version": version,
        "normalized_metrics": normalized_metrics
    })

@metrics_bp.route('/prometheus', methods=['GET'])
def prometheus_metrics():
    # Return Prometheus metrics in text format
    return Response(generate_latest(), mimetype='text/plain')

@metrics_bp.route('/prometheus/ab_metrics', methods=['GET'])
def ab_metrics():
    # Output A/B testing metrics in Prometheus format
    from prometheus_client import Gauge, CollectorRegistry, generate_latest
    
    current_app.logger.info("AB metrics endpoint called")
    registry = CollectorRegistry()
    
    # Create gauges for A/B testing metrics
    feedback_count = Gauge('feedback_count', 'Count of feedback responses', 
                          ['version', 'feedback', 'sentiment'], registry=registry)
    prediction_clicks = Gauge('prediction_clicks', 'Number of prediction button clicks by version', 
                         ['version'], registry=registry)
    conversion_rate = Gauge('feedback_conversion_rate', 'Conversion rate percentage (feedback/clicks)', 
                           ['version'], registry=registry)
    
    # Get different versions
    versions = ["1", "2"]
    current_app.logger.info(f"Processing metrics for versions: {versions}")
    
    for version in versions:
        current_app.logger.info(f"Processing metrics for version: {version}")
        clicks = 0 
        try:
            current_app.logger.debug(f"Collecting total_predict_times metrics")
            metrics_collection = list(total_predict_times.collect())
            current_app.logger.info(f"Found {len(metrics_collection)} total_predict_times metric collections")
            
            for metric in metrics_collection:
                current_app.logger.debug(f"Metric name: {metric.name}, samples: {len(metric.samples)}")
                for sample in metric.samples:
                    sample_version = extract_major_version(sample.labels.get('version', ''))
                    current_app.logger.debug(f"Sample: {sample.name}, labels: {sample.labels}, extracted version: {sample_version}, value: {sample.value}")
                    
                    if sample.name == 'total_predict_times_total' and sample_version == version:
                        clicks += sample.value
                        current_app.logger.info(f"Found click metric for version {version} (from {sample.labels.get('version')}): +{sample.value}, total now: {clicks}")
            
            current_app.logger.info(f"Total clicks for version {version}: {clicks}")
        except Exception as e:
            current_app.logger.error(f"Error getting prediction clicks count: {e}", exc_info=True)
            clicks = 0
            
        prediction_clicks.labels(version=version).set(clicks)
        current_app.logger.info(f"Set prediction_clicks metric for version {version} to {clicks}")
        
        # Calculate feedback counts for the specific version
        total_count = 0
        current_app.logger.debug(f"Getting feedback metrics for version {version}")
        current_app.logger.debug(f"Available metrics: {len(user_feedback_counter._metrics.items())}")
        
        for labels, counter in user_feedback_counter._metrics.items():
            label_dict = dict(zip(user_feedback_counter._labelnames, labels))
            original_version = label_dict.get('version', '')
            extracted_version = extract_major_version(original_version)
            current_app.logger.debug(f"Checking feedback metric with labels: {label_dict}, extracted version: {extracted_version}")
            
            if extracted_version == version:
                value = counter._value.get()
                total_count += value
                current_app.logger.info(f"Found feedback for version {version} (from {original_version}): {label_dict}, value: {value}")
                
                feedback_count.labels(
                    version=version,
                    feedback=label_dict.get('feedback', 'unknown'),
                    sentiment=label_dict.get('sentiment', 'unknown')
                ).set(value)
                
        current_app.logger.info(f"Total feedback count for version {version}: {total_count}")
                
        # Calculate conversion rate based on prediction clicks
        conversion = (total_count / max(clicks, 1)) * 100 if clicks > 0 else 0
        conversion_rate.labels(version=version).set(conversion)
        current_app.logger.info(f"Set conversion_rate for version {version} to {conversion}%")
    
    current_app.logger.info("AB metrics endpoint completed successfully")
    return Response(generate_latest(registry), mimetype='text/plain')
    
def extract_major_version(version_str):
    """
    Extract the major version number from a version string.
    Examples:
    - "v2.10.2" -> "2"
    - "2.10.2" -> "2"
    - "v2" -> "2"
    - "2" -> "2"
    """
    if not version_str:
        return ""
    
    # Remove 'v' prefix if present
    if version_str.startswith('v'):
        version_str = version_str[1:]
    
    # Extract major version (first part before any dot)
    parts = version_str.split('.')
    if parts and parts[0].isdigit():
        return parts[0]
    
    return version_str  # Return original if parsing fails