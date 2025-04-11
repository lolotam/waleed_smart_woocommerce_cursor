"""
Authentication routes for the Smart WooCommerce Plugin
"""

from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from . import auth_bp
from .models import User
from utils.license_manager import save_license, validate_license

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Handle user login"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        remember = request.form.get('remember', False)
        
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user, remember=remember)
            return redirect(url_for('dashboard'))
        
        flash('Invalid username or password', 'error')
    
    return render_template('auth/login.html')

@auth_bp.route('/logout')
@login_required
def logout():
    """Handle user logout"""
    logout_user()
    return redirect(url_for('auth.login'))

@auth_bp.route('/license', methods=['GET', 'POST'])
def license():
    """Handle license activation"""
    if request.method == 'POST':
        license_key = request.form.get('license_key')
        if not license_key:
            flash('Please enter a license key.', 'error')
        else:
            # Attempt to save the license
            if save_license(license_key):
                flash('License activated successfully! Please log in.', 'success')
                return redirect(url_for('auth.login'))
            else:
                flash('Invalid or incorrect license key for this machine.', 'error')
                # Fall through to render the license page again

    return render_template('auth/license.html') 