from flask import Blueprint, jsonify, request, current_app

model_bp = Blueprint('model', __name__, url_prefix="/api/models")

@model_bp.route('/predict', methods=['POST'])
def predict():
    """
    Perform sentiment analysis on a given text.
    ---
    tags:
      - Model
    summary: Predicts the sentiment of a review text.
    requestBody:
      required: true
      content:
        application/json:
          schema:
            type: object
            properties:
              input:
                type: string
                description: The review text to analyze.
                example: "The food was amazing!"
    responses:
      200:
        description: Prediction successful.
        content:
          application/json:
            schema:
              type: object
              properties:
                result:
                  type: object
                  properties:
                    prediction:
                      type: string
                      example: "positive"
      400:
        description: Bad Request - No input data provided.
      500:
        description: Internal Server Error - Prediction failed.
    """
    data = request.get_json()
    
    # Validation
    if not data:
        return jsonify({"error": "No input data provided"}), 400
    
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