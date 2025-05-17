from flask import Blueprint, jsonify, request, current_app, render_template
import os
from lib_version.version_awareness import VersionUtil
from app import current_users_gauge, user_feedback_counter

main_bp = Blueprint('main', __name__)
model_bp = Blueprint('model', __name__, url_prefix="/api/models")
metrics_bp = Blueprint('metrics', __name__, url_prefix="/api/metrics")

@main_bp.route('/', methods=['GET'])
def index():
    # return jsonify({
    #     "status" : "online",
    #     "service": "app-service",
    #     # TODO: automatically fetch version
    #     "version": "NOT IMPLEMENTED"
    # })
    
    # Inc active user number
    current_users_gauge.inc()
    
    version_util = VersionUtil()
    lib_version = version_util.get_version()
    return render_template('index.html', version=current_app.config["VERSION"], lib_version=lib_version)
    
@main_bp.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "alive!"})

@model_bp.route('/predict', methods=['POST'])
def predict():
    data = request.get_json()
    
    # Validation
    if not data:
        return jsonify({"error": "No input data procided"}), 400
    
    # Invoke model service
    from app.models.model_handler import predict_with_model
    
    try:
        result = predict_with_model(data)
        if not result:
            raise ValueError(f"No results returned")
        return jsonify({"result": result})
    except Exception as e:
        current_app.logger.error(f"Prediction error: {str(e)}")
        return jsonify({"error": str(e)}), 500
    
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
    
    # TODO: Add user feedback metrics
    if feedback and sentiment:
        user_feedback_counter.labels(
            feedback=feedback, 
            sentiment=sentiment.lower() if sentiment else 'unknown'
        ).inc()
    return jsonify({"status": "feedback recorded"})
