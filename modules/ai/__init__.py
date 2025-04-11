"""
AI Module for Smart WooCommerce Plugin

This module provides AI-powered content generation for WooCommerce products
using advanced language models. It includes functionality for generating
product titles, descriptions, and SEO metadata.
"""

from flask import Blueprint

from .prompts import PromptManager
from .routes import register_routes
from .product_content_generator import ProductContentGenerator

# Initialize the blueprint
ai_bp = Blueprint('ai', __name__, url_prefix='/ai')

# Register all routes
register_routes(ai_bp)

# Initialize prompt manager
prompt_manager = PromptManager()
prompt_manager._ensure_prompts_file()
prompt_manager.initialize_default_prompts()

# Initialize content generator
product_content_generator = ProductContentGenerator(prompt_manager)

def init_app(app):
    """Initialize the AI module with the Flask app"""
    app.register_blueprint(ai_bp)
    return ai_bp 