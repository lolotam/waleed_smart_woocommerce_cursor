from flask import Blueprint, request, jsonify, session, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from modules.woocommerce.client import WooCommerceClient
from modules.woocommerce.products import ProductManager
from modules.woocommerce.categories import CategoryManager
from modules.woocommerce.brands import BrandManager
from config import Config

# Create the blueprint
woocommerce_bp = Blueprint('woocommerce', __name__)

# Helper function to get WooCommerce client
def get_wc_client():
    """Get a WooCommerce client using the current credentials"""
    return WooCommerceClient(
        store_url=session.get('woocommerce_store_url', Config.WOOCOMMERCE_STORE_URL),
        consumer_key=session.get('woocommerce_consumer_key', Config.WOOCOMMERCE_CONSUMER_KEY),
        consumer_secret=session.get('woocommerce_consumer_secret', Config.WOOCOMMERCE_CONSUMER_SECRET)
    )

# ============= API Configuration Routes =============

@woocommerce_bp.route('/configure', methods=['GET', 'POST'])
@login_required
def configure():
    """Configure WooCommerce API credentials"""
    if request.method == 'POST':
        # Get values from form
        store_url = request.form.get('store_url', '').strip()
        consumer_key = request.form.get('consumer_key', '').strip()
        consumer_secret = request.form.get('consumer_secret', '').strip()
        
        # Validate input
        if not store_url or not consumer_key or not consumer_secret:
            flash('All fields are required', 'error')
            return render_template('woocommerce/configure.html')
        
        # Test connection
        client = WooCommerceClient(
            store_url=store_url,
            consumer_key=consumer_key,
            consumer_secret=consumer_secret
        )
        
        if client.test_connection():
            # Save to session
            session['woocommerce_store_url'] = store_url
            session['woocommerce_consumer_key'] = consumer_key
            session['woocommerce_consumer_secret'] = consumer_secret
            
            flash('WooCommerce connection successful', 'success')
            return redirect(url_for('woocommerce.status'))
        else:
            flash('Failed to connect to WooCommerce. Please check your credentials.', 'error')
    
    # Get current values
    store_url = session.get('woocommerce_store_url', Config.WOOCOMMERCE_STORE_URL)
    consumer_key = session.get('woocommerce_consumer_key', Config.WOOCOMMERCE_CONSUMER_KEY)
    consumer_secret = session.get('woocommerce_consumer_secret', Config.WOOCOMMERCE_CONSUMER_SECRET)
    
    return render_template(
        'woocommerce/configure.html',
        store_url=store_url,
        consumer_key=consumer_key,
        consumer_secret=consumer_secret
    )

@woocommerce_bp.route('/status')
@login_required
def status():
    """Display WooCommerce connection status and store information"""
    # Get WooCommerce client
    client = get_wc_client()
    
    # Check connection
    connection_status = client.test_connection()
    
    # Get store information
    store_info = None
    product_count = None
    category_count = None
    brand_count = None
    
    if connection_status:
        try:
            # Get simple product count for status display
            product_manager = ProductManager(client)
            products = product_manager.get_products(per_page=1)
            product_count = products.headers.get('X-WP-Total', 0) if hasattr(products, 'headers') else 0
            
            # Get category count
            category_manager = CategoryManager(client)
            categories = category_manager.get_categories(per_page=1)
            category_count = categories.headers.get('X-WP-Total', 0) if hasattr(categories, 'headers') else 0
            
            # Get brand count
            try:
                brand_manager = BrandManager(client)
                brands = brand_manager.get_brands(per_page=1)
                brand_count = brands.headers.get('X-WP-Total', 0) if hasattr(brands, 'headers') else 0
            except:
                # Brand taxonomy might not exist
                brand_count = 0
        except Exception as e:
            flash(f"Error retrieving store information: {str(e)}", 'error')
    
    return render_template(
        'woocommerce/status.html',
        connection_status=connection_status,
        store_url=client.store_url,
        product_count=product_count,
        category_count=category_count,
        brand_count=brand_count
    )

# ============= API Endpoints =============

@woocommerce_bp.route('/test-connection', methods=['POST'])
@login_required
def test_connection():
    """API endpoint to test WooCommerce connection"""
    # Get values from JSON request
    data = request.json
    store_url = data.get('store_url', '').strip()
    consumer_key = data.get('consumer_key', '').strip()
    consumer_secret = data.get('consumer_secret', '').strip()
    
    # Validate input
    if not store_url or not consumer_key or not consumer_secret:
        return jsonify({
            'success': False, 
            'message': 'All fields are required'
        }), 400
    
    # Test connection
    client = WooCommerceClient(
        store_url=store_url,
        consumer_key=consumer_key,
        consumer_secret=consumer_secret
    )
    
    success = client.test_connection()
    
    if success:
        return jsonify({
            'success': True, 
            'message': 'Connection successful'
        })
    else:
        return jsonify({
            'success': False, 
            'message': 'Failed to connect to WooCommerce. Please check your credentials.'
        }), 400 