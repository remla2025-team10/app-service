from flask import Blueprint, jsonify, request
from app import current_users_gauge, user_feedback_counter

metrics_bp = Blueprint('metrics', __name__, url_prefix="/api/metrics")

@metrics_bp.route('/user_visit', methods=['POST'])
def user_visit():
    current_users_gauge.inc()
    return jsonify({"status": "success"})

@metrics_bp.route('/user_leave', methods=['POST'])
def user_leave():
    current_users_gauge.dec()
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
    return jsonify({"status": "feedback recorded"})