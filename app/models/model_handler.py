import os
import json
import requests
from flask import current_app


class ModelNotFoundError(Exception):
    """When a requested model is not found"""
    pass

def load_model(model_name):
    
    # TODO Dynamically load real model list
    
    models = {
        "default": {"type": "example", "version": "1.0.0"}
    }
    
    if model_name not in models:
        raise ModelNotFoundError(f"Model '{model_name}' not found")
    
    current_app.logger.info(f"Loaded model: {model_name}")
    return models[model_name]

def predict_with_model(data):
    """
    Make prediction using the appropriate model
    Args:
        data: Dictionary containing input data and optionally model selection
    Returns:
        Dictionary with prediction results
    """
        
    input_data = data.get("input")
    if not input_data:
        raise ValueError("No input provided for prediction")
        
    MODEL_SERVICE_URL = current_app.config.get('MODEL_SERVICE_URL', 'http://model-service:3000')
    if MODEL_SERVICE_URL is not None:
        model_url = MODEL_SERVICE_URL + '/predict'
    
    response = None
    
    if MODEL_SERVICE_URL is None or MODEL_SERVICE_URL == 'test':
        # Return mock response for testing
        response = {
            "prediction": "Example prediction result",
        }
    else:
        model_request = {"Review": input_data}
        
        api_response = requests.post(model_url, json=model_request)
        api_response.raise_for_status()  # Raise exception for HTTP errors
        response = api_response.json()
    
    current_app.logger.info(f"Made prediction with model: {input_data}")
    return response
