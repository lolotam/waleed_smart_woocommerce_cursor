import os
import secrets
from datetime import timedelta

class Config:
    """Application configuration class"""
    
    # Base directory
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    
    # Secret key (generated if not set)
    SECRET_KEY = os.environ.get('SECRET_KEY') or secrets.token_hex(32)
    
    # Session configuration
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)
    
    # Database configuration
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        f"sqlite:///{os.path.join(BASE_DIR, 'instance', 'app.db')}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # File uploads
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'static', 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max upload
    
    # Temp folder for imports/exports
    TEMP_FOLDER = os.path.join(BASE_DIR, 'temp')
    
    # Logs directory
    LOG_DIR = os.path.join(BASE_DIR, 'logs')
    AI_LOG_FILE = os.path.join(LOG_DIR, 'ai_generations.json')
    
    # License file path
    LICENSE_FILE = os.path.join(BASE_DIR, 'license.key')
    
    # WooCommerce default settings
    WOOCOMMERCE_STORE_URL = os.environ.get('WOOCOMMERCE_STORE_URL', '')
    WOOCOMMERCE_CONSUMER_KEY = os.environ.get('WOOCOMMERCE_CONSUMER_KEY', '')
    WOOCOMMERCE_CONSUMER_SECRET = os.environ.get('WOOCOMMERCE_CONSUMER_SECRET', '')
    WOOCOMMERCE_VERIFY_SSL = False
    WOOCOMMERCE_TIMEOUT = 15
    WOOCOMMERCE_ITEMS_PER_PAGE = 20
    
    # AI API keys
    OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY', '')
    CLAUDE_API_KEY = os.environ.get('CLAUDE_API_KEY', '')
    GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY', '')
    
    # Default AI model
    DEFAULT_AI_MODEL = 'gpt-3.5-turbo'
    
    # UI configuration
    DEFAULT_THEME = 'light'  # 'light' or 'dark'
    
    # Create required directories if they don't exist
    @staticmethod
    def initialize():
        """Create necessary directories if they don't exist"""
        for directory in [
            os.path.join(Config.BASE_DIR, 'instance'),
            Config.UPLOAD_FOLDER, 
            Config.TEMP_FOLDER,
            Config.LOG_DIR
        ]:
            os.makedirs(directory, exist_ok=True)


class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    TESTING = False


class TestingConfig(Config):
    """Testing configuration"""
    DEBUG = False
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False


class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    TESTING = False


# Choose configuration based on environment
config_by_name = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}

# Default config
Config = config_by_name[os.environ.get('FLASK_ENV', 'default')]
Config.initialize() 