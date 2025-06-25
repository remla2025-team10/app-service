import os
import json
import time
import requests
from flask import current_app
from app import review_counter, sentiment_analysis_duration, current_users_gauge


class ModelNotFoundError(Exception):
    """When a requested model is not found"""
    pass

def load_model(model_name):
    """
    Loads a model configuration by its name.

    Note: This is a placeholder and should be updated to dynamically
    load real model information.

    Args:
        model_name (str): The name of the model to load.

    Raises:
        ModelNotFoundError: If the model_name is not found.

    Returns:
        dict: The configuration of the requested model.
    """
    
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
    Makes a prediction by calling the external model service.

    This function takes input data, sends it to the configured model service
    for sentiment analysis, records performance metrics, and returns the
    prediction result.

    Args:
        data (dict): A dictionary containing the input data for the model.
                     It must have an "input" key with the text to be analyzed.

    Raises:
        ValueError: If the 'input' key is not in the data dictionary.
        requests.exceptions.RequestException: For issues connecting to the model service.

    Returns:
        dict: The JSON response from the model service, which includes the prediction.
    """
        
    start_time = time.time()
    
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
    
    if response and "prediction" in response:
        sentiment = str(response["prediction"]).lower()
        review_counter.labels(sentiment=sentiment).inc()
        
    processing_time = time.time() - start_time
    sentiment_analysis_duration.observe(processing_time)
    
    
    current_app.logger.info(f"Made prediction with model: {input_data}")
    return response
