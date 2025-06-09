from flask import Blueprint, jsonify, request, current_app
from app import current_users_gauge, user_feedback_counter, total_predict_times, get_version

metrics_bp = Blueprint('metrics', __name__, url_prefix="/api/metrics")

@metrics_bp.route('/user_visit', methods=['POST'])
def user_visit():
    current_users_gauge.inc()
    return jsonify({"status": "success"})

@metrics_bp.route('/user_leave', methods=['POST'])
def user_leave():
    current_users_gauge.dec()
    current_app.logger.info("User left the application")
    return jsonify({"status": "success"})

@metrics_bp.route('/click', methods=['POST'])
def record_click():
    total_predict_times.inc()
    return jsonify({"status": "success"})
    
@metrics_bp.route('/feedback', methods=['POST'])
def record_feedback():
    data = request.get_json()
    feedback = data.get('feedback')
    sentiment = data.get('sentiment')
    
    if feedback and sentiment:
        user_feedback_counter.labels(
            feedback=feedback, 
            sentiment=sentiment.lower() if sentiment else 'unknown'
        ).inc()
    current_app.logger.info(f"Feedback recorded: {feedback}, Sentiment: {sentiment}")
    return jsonify({"status": "feedback recorded"})

@metrics_bp.route('/feedback/count', methods=['GET'])
def get_feedback_count():
    total_count = 0
    version = get_version_number()
    feedback_metrics = {}
    
    visits = 0
    try:
        for metric in total_predict_times.collect():
            for sample in metric.samples:
                if sample.name == 'total_predict_times_total':
                    visits += sample.value
                    current_app.logger.info(f"Found visit count: {sample.value}")
        
    except Exception as e:
        current_app.logger.error(f"Error getting visit count: {e}")
        visits = 1
    
    traffic_distribution = 1.0
    if version == "1":  
        traffic_distribution = 0.9
    elif version == "2":
        traffic_distribution = 0.1
    else:
        traffic_distribution = 0.5
    
    for labels, counter in user_feedback_counter._metrics.items():
        value = counter._value.get()
        total_count += value
        label_dict = dict(zip(user_feedback_counter._labelnames, labels))
        feedback_metrics[str(label_dict)] = value
    
    normalized_metrics = {
        "raw_count": total_count,
        "actual_visits": visits,
        "per_100_users": round((total_count / max(visits, 1)) * 100, 2),
        "conversion_rate": round((total_count / max(visits, 1)) * 100, 2),
        "configured_traffic_distribution": traffic_distribution  # 名称更改以避免误解
    }
    
    return jsonify({
        "status": "success",
        "total_feedback_count": total_count,
        "feedback_details": feedback_metrics,
        "version": version,
        "normalized_metrics": normalized_metrics
    })
    
def get_version_number():
    version = get_version()
    if version is not None and version.startswith('v'):
        version = version.split('.')[0][1:]
    return version