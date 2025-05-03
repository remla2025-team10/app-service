from flask import Blueprint, jsonify, request, current_app, render_template
import os

main_bp = Blueprint('main', __name__)
model_bp = Blueprint('model', __name__, url_prefix="/api/models")

@main_bp.route('/', methods=['GET'])
def index():
    # return jsonify({
    #     "status" : "online",
    #     "service": "app-service",
    #     # TODO: automatically fetch version
    #     "version": "NOT IMPLEMENTED"
    # })
    return render_template('index.html', version=current_app.config["VERSION"])
    
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