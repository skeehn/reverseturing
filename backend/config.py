"""Configuration management for Reverse Turing Game"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Base configuration"""
    # Flask
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    DEBUG = os.environ.get('DEBUG', 'False').lower() == 'true'
    
    # Database
    POSTGRES_USER = os.environ.get('POSTGRES_USER', 'user')
    POSTGRES_PASSWORD = os.environ.get('POSTGRES_PASSWORD', 'password')
    POSTGRES_DB = os.environ.get('POSTGRES_DB', 'reverse_turing')
    POSTGRES_HOST = os.environ.get('POSTGRES_HOST', 'localhost')
    POSTGRES_PORT = os.environ.get('POSTGRES_PORT', '5432')
    
    SQLALCHEMY_DATABASE_URI = (
        f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@"
        f"{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Redis
    REDIS_HOST = os.environ.get('REDIS_HOST', 'localhost')
    REDIS_PORT = int(os.environ.get('REDIS_PORT', 6379))
    REDIS_DB = int(os.environ.get('REDIS_DB', 0))
    REDIS_PASSWORD = os.environ.get('REDIS_PASSWORD', None)
    
    # Celery
    CELERY_BROKER_URL = os.environ.get('CELERY_BROKER_URL', f'redis://{REDIS_HOST}:{REDIS_PORT}/0')
    CELERY_RESULT_BACKEND = os.environ.get('CELERY_RESULT_BACKEND', f'redis://{REDIS_HOST}:{REDIS_PORT}/0')
    
    # WebSocket
    CORS_ALLOWED_ORIGINS = os.environ.get('CORS_ALLOWED_ORIGINS', '*')
    
    # AI Models
    JUDGE_MODEL_NAME = os.environ.get('JUDGE_MODEL_NAME', 'microsoft/Phi-3.5-mini-instruct')
    RESPONDER_MODEL_NAME = os.environ.get('RESPONDER_MODEL_NAME', 'Qwen/Qwen2.5-1.5B-Instruct')
    MODEL_CACHE_DIR = os.environ.get('MODEL_CACHE_DIR', './models')
    USE_GPU = os.environ.get('USE_GPU', 'auto')  # 'auto', 'cuda', 'cpu'
    
    # Game Settings
    MAX_RESPONSE_LENGTH = int(os.environ.get('MAX_RESPONSE_LENGTH', 500))
    RESPONSE_TIMEOUT = int(os.environ.get('RESPONSE_TIMEOUT', 90))  # seconds
    VOTING_TIMEOUT = int(os.environ.get('VOTING_TIMEOUT', 30))  # seconds
    MIN_PLAYERS_PER_ROOM = int(os.environ.get('MIN_PLAYERS_PER_ROOM', 1))
    MAX_PLAYERS_PER_ROOM = int(os.environ.get('MAX_PLAYERS_PER_ROOM', 10))
    
    # Training
    BATCH_SIZE_FOR_TRAINING = int(os.environ.get('BATCH_SIZE_FOR_TRAINING', 50))
    MIN_ACCURACY_THRESHOLD = float(os.environ.get('MIN_ACCURACY_THRESHOLD', 0.6))
    LORA_R = int(os.environ.get('LORA_R', 16))
    LORA_ALPHA = int(os.environ.get('LORA_ALPHA', 32))
    LORA_DROPOUT = float(os.environ.get('LORA_DROPOUT', 0.1))
    
    # Security
    BCRYPT_LOG_ROUNDS = int(os.environ.get('BCRYPT_LOG_ROUNDS', 12))
    SESSION_COOKIE_SECURE = os.environ.get('SESSION_COOKIE_SECURE', 'False').lower() == 'true'
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    TESTING = False

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    TESTING = False
    SESSION_COOKIE_SECURE = True

class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'

# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}

def get_config():
    """Get configuration based on environment"""
    env = os.environ.get('FLASK_ENV', 'development')
    return config.get(env, config['default'])