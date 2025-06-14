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
    
    if feedback and sentiment is not None:
        try:
            # Get metric state before incrementing
            before_count = len(user_feedback_counter._metrics.items())
            
            # Convert sentiment to string for consistency in metrics
            sentiment_str = str(sentiment).lower() if sentiment is not None else 'unknown'
            
            user_feedback_counter.labels(
                version=version,
                feedback=feedback, 
                sentiment=sentiment_str
            ).inc()
            
            # Get metric state after incrementing
            after_count = len(user_feedback_counter._metrics.items())
            
            current_app.logger.info(f"Feedback counter incremented: before={before_count}, after={after_count}")
            current_app.logger.info(f"Feedback recorded for version {version}: {feedback}, Sentiment: {sentiment}")
        except Exception as e:
            current_app.logger.error(f"Error incrementing feedback counter: {e}", exc_info=True)
    else:
        current_app.logger.warning(f"Incomplete feedback data received: feedback={feedback}, sentiment={sentiment}")
        
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
    from prometheus_client import Gauge, CollectorRegistry, generate_latest, REGISTRY
    
    current_app.logger.info("AB metrics endpoint called")
    registry = CollectorRegistry()
    
    # Create gauges for A/B testing metrics
    feedback_count = Gauge('feedback_count', 'Count of feedback responses', 
                          ['version', 'feedback', 'sentiment'], registry=registry)
    prediction_clicks = Gauge('prediction_clicks', 'Number of prediction button clicks by version', 
                         ['version'], registry=registry)
    conversion_rate = Gauge('feedback_conversion_rate', 'Conversion rate percentage (feedback/clicks)', 
                           ['version'], registry=registry)
    
    # Print overall metrics information for debugging
    current_app.logger.info(f"Feedback counter structure type: {type(user_feedback_counter)}")
    current_app.logger.info(f"Feedback counter label names: {user_feedback_counter._labelnames}")
    
    # Print all metrics from registry
    current_app.logger.info("--- Examining all available metrics in registry ---")
    try:
        for metric in REGISTRY.collect():
            if "feedback" in metric.name or "predict" in metric.name:
                current_app.logger.info(f"Registry metric: {metric.name}, type: {metric.type}")
                for sample in metric.samples:
                    current_app.logger.info(f"  Sample: {sample.name}, labels: {sample.labels}, value: {sample.value}")
    except Exception as e:
        current_app.logger.error(f"Error examining registry metrics: {e}")
    current_app.logger.info("--- End of registry metrics ---")
    
    # Get different versions
    versions = ["1", "2"]
    current_app.logger.info(f"Processing metrics for versions: {versions}")
    
    # First, print ALL available feedback entries regardless of version
    current_app.logger.info("--- ALL FEEDBACK ENTRIES (regardless of version) ---")
    try:
        all_feedback_items = list(user_feedback_counter._metrics.items())
        current_app.logger.info(f"Total feedback metrics entries: {len(all_feedback_items)}")
        
        if len(all_feedback_items) == 0:
            current_app.logger.warning("No feedback metrics found in counter. Checking if feedback endpoint was called...")
            
            # Check if the feedback endpoint was called at all
            for metric in REGISTRY.collect():
                if "http_request" in metric.name:
                    for sample in metric.samples:
                        if sample.labels.get('endpoint') == 'metrics.record_feedback' and sample.labels.get('method') == 'POST':
                            current_app.logger.info(f"Found record_feedback endpoint calls: {sample.name}, value: {sample.value}")
        
        for idx, (labels, counter) in enumerate(all_feedback_items):
            label_dict = dict(zip(user_feedback_counter._labelnames, labels))
            value = counter._value.get()
            current_app.logger.info(f"  Feedback entry #{idx+1}: labels={label_dict}, value={value}")
    except Exception as e:
        current_app.logger.error(f"Error examining feedback entries: {e}", exc_info=True)
    current_app.logger.info("--- END OF ALL FEEDBACK ENTRIES ---")
    
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
        current_app.logger.debug(f"Available feedback metrics: {len(user_feedback_counter._metrics.items())}")
        
        current_app.logger.info(f"--- FEEDBACK MATCHING VERSION {version} ---")
        for labels, counter in user_feedback_counter._metrics.items():
            label_dict = dict(zip(user_feedback_counter._labelnames, labels))
            original_version = label_dict.get('version', '')
            extracted_version = extract_major_version(original_version)
            current_app.logger.info(f"  Checking: original_version={original_version}, extracted={extracted_version}, match={extracted_version == version}")
            
            if extracted_version == version:
                value = counter._value.get()
                total_count += value
                current_app.logger.info(f"  ✓ MATCH! Version {version}: {label_dict}, value: {value}")
                
                feedback_count.labels(
                    version=version,
                    feedback=label_dict.get('feedback', 'unknown'),
                    sentiment=label_dict.get('sentiment', 'unknown')
                ).set(value)
            else:
                current_app.logger.info(f"  ✗ NO MATCH: Version comparison failed: {extracted_version} != {version}")
        current_app.logger.info(f"--- END FEEDBACK MATCHING FOR VERSION {version} ---")
                
        current_app.logger.info(f"Total feedback count for version {version}: {total_count}")
                
        # Calculate conversion rate based on prediction clicks
        conversion = (total_count / max(clicks, 1)) * 100 if clicks > 0 else 0
        conversion_rate.labels(version=version).set(conversion)
        current_app.logger.info(f"Set conversion_rate for version {version} to {conversion}%")
    
    # Add additional debug option to inject test data if requested
    use_test_data = request.args.get('test_data', 'false').lower() == 'true'
    if use_test_data:
        current_app.logger.info("Test data requested - adding sample feedback data")
        for ver in versions:
            feedback_count.labels(version=ver, feedback="test_feedback", sentiment="positive").set(5)
            current_app.logger.info(f"Added test feedback data for version {ver}: 5 items")
            
            # Recalculate conversion
            ver_clicks = prediction_clicks._metrics.get((ver,), 0)
            if ver_clicks:
                ver_clicks = ver_clicks._value.get()
            else:
                ver_clicks = 10  # Default test value 
            
            test_conversion = (5 / max(ver_clicks, 1)) * 100
            conversion_rate.labels(version=ver).set(test_conversion)
            current_app.logger.info(f"Updated conversion rate for version {ver} to {test_conversion}%")
    
    current_app.logger.info("AB metrics endpoint completed successfully")
    return Response(generate_latest(registry), mimetype='text/plain')
    
def extract_major_version(version_str):
    """
    Extract the major version number from a version string.
    Handles both pure numbers and semantic versioning formats.
    
    Examples:
    - "v2.10.2" -> "2"
    - "2.10.2" -> "2"
    - "v2" -> "2"
    - "2" -> "2"
    - "" -> ""
    """
    if not version_str:
        return ""
    
    # Case: pure number - return as is if it's already a digit
    if version_str.isdigit():
        return version_str
    
    # Remove 'v' prefix if present
    if version_str.startswith('v'):
        version_str = version_str[1:]
    
    # Case: semantic version (with dots)
    if '.' in version_str:
        parts = version_str.split('.')
        if parts and parts[0].isdigit():
            return parts[0]
    # Case: just a number potentially with non-digit characters
    elif version_str.isdigit():
        return version_str
    
    # Try to extract any leading digits
    import re
    match = re.match(r'(\d+)', version_str)
    if match:
        return match.group(1)
        
    # Fallback: return original if no digits found
    return version_str