import os

class Config:
    """Base Configuration"""
    DEBUG = False
    TESTING = False
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    
class DevelopmentConfig(Config):
    """Development Configuration"""
    DEBUG = True
    LOG_LEVEL = os.getenv("LOG_LEVEL", "DEBUG")

class TestingConfig(Config):
    """Testing Configuration"""
    TESTING = True
    DEBUG = True

class ProductionConfig(Config):
    """Production Configuration"""
    # Production-specific settings
    LOG_LEVEL = os.getenv("LOG_LEVEL", "WARNING")

# Configuration dictionary
config = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
    "default": DevelopmentConfig,
}