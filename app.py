import sys
import os
print(f"--- Debug: Running with Python executable: {sys.executable}")
print(f"--- Debug: sys.path: {sys.path}")

from flask import Flask, render_template, redirect, url_for, flash, request, jsonify
from flask_login import LoginManager, login_required, current_user
from modules.auth.models import db, User

# Import configuration
from config import Config

# Initialize the Flask application
app = Flask(__name__)
app.config.from_object(Config)

# Initialize database
db.init_app(app)

# Setup Login Manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Import and register blueprints
from modules.auth.routes import auth_bp
from modules.ai.routes import ai_bp
from modules.woocommerce.products import products_bp
from modules.woocommerce.categories import categories_bp

app.register_blueprint(auth_bp, url_prefix='/auth')
app.register_blueprint(ai_bp, url_prefix='/ai')
app.register_blueprint(products_bp, url_prefix='/products')
app.register_blueprint(categories_bp, url_prefix='/categories')

# Main routes
@app.route('/')
def index():
    """Redirect to dashboard if logged in, otherwise to login page"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return redirect(url_for('auth.login'))

@app.route('/dashboard')
@login_required
def dashboard():
    """Display the main dashboard"""
    return render_template('dashboard/index.html')

@app.route('/settings')
@login_required
def settings():
    """Display the settings page"""
    return render_template('settings/index.html')

# Error handlers
@app.errorhandler(404)
def page_not_found(e):
    return render_template('error/404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('error/500.html'), 500

# License verification
@app.before_request
def verify_license():
    """Verify the license before processing any request"""
    from utils.license_manager import validate_license
    
    # Skip license check for static files and the license activation route
    if request.path.startswith('/static') or request.path == '/auth/activate_license':
        return
    
    # Check license validity
    if not validate_license():
        if request.path != '/auth/license':
            return redirect(url_for('auth.license'))

# Create database tables
def init_db():
    with app.app_context():
        db.create_all()
        # Create a default admin user if none exists
        if not User.query.filter_by(username='admin').first():
            admin = User(username='admin', email='admin@example.com')
            admin.set_password('admin')
            db.session.add(admin)
            db.session.commit()

if __name__ == '__main__':
    init_db()
    app.run(debug=True) 