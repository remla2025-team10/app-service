from flask import Blueprint, jsonify, request, current_app

model_bp = Blueprint('model', __name__, url_prefix="/api/models")

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