from flask import Flask
from flask_cors import CORS
from config import Config
import os

def create_app(config_class=Config):
    # Initialize Flask app
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Setup CORS
    CORS(app)

    # Ensure required directories exist
    os.makedirs(app.config['UPLOADS_FOLDER'], exist_ok=True)
    os.makedirs(app.config['LOGS_FOLDER'], exist_ok=True)
    os.makedirs(app.config['TEMP_FOLDER'], exist_ok=True)

    # Register blueprints
    from modules.api import api_bp
    from modules.web import web_bp
    from modules.woo.routes import woo_bp
    from modules.ai.routes import ai_bp
    
    app.register_blueprint(api_bp, url_prefix='/api')
    app.register_blueprint(web_bp, url_prefix='/')
    app.register_blueprint(woo_bp, url_prefix='/woo')
    app.register_blueprint(ai_bp, url_prefix='/ai')

    # Register error handlers
    @app.errorhandler(404)
    def page_not_found(e):
        return {"error": "The resource could not be found"}, 404

    @app.errorhandler(500)
    def server_error(e):
        return {"error": "Internal server error"}, 500

    return app 