from modules.woocommerce.client import WooCommerceClient
from modules.woocommerce.media import MediaManager
from config import Config
# Added imports for Blueprint and route handling
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required

# Define the blueprint
products_bp = Blueprint('products', __name__)

class ProductManager:
    """
    Manager for WooCommerce product operations
    """
    
    def __init__(self, wc_client=None):
        """
        Initialize the product manager
        
        Args:
            wc_client (WooCommerceClient, optional): WooCommerce client instance
        """
        self.client = wc_client or WooCommerceClient()
        self.media_manager = MediaManager(self.client)
        
    def get_products(self, page=1, per_page=None, **filters):
        """
        Get a list of products with optional filtering
        
        Args:
            page (int, optional): Page number
            per_page (int, optional): Items per page
            **filters: Additional filters (category, tag, search, etc.)
            
        Returns:
            list: List of products
        """
        # Set default per_page if not provided
        if per_page is None:
            per_page = Config.WOOCOMMERCE_ITEMS_PER_PAGE
        
        # Build query parameters
        params = {
            'page': page,
            'per_page': per_page,
            **filters
        }
        
        # Make the API request
        return self.client.get('products', params=params)
    
    def get_product(self, product_id):
        """
        Get a single product by ID
        
        Args:
            product_id (int): Product ID
            
        Returns:
            dict: Product data
        """
        return self.client.get(f'products/{product_id}')
    
    def create_product(self, product_data):
        """
        Create a new product
        
        Args:
            product_data (dict): Product data
            
        Returns:
            dict: Created product data
        """
        return self.client.post('products', data=product_data)
    
    def update_product(self, product_id, product_data):
        """
        Update an existing product
        
        Args:
            product_id (int): Product ID
            product_data (dict): Product data to update
            
        Returns:
            dict: Updated product data
        """
        return self.client.put(f'products/{product_id}', data=product_data)
    
    def delete_product(self, product_id, force=False):
        """
        Delete a product
        
        Args:
            product_id (int): Product ID
            force (bool, optional): Whether to force deletion
            
        Returns:
            dict: Response data
        """
        return self.client.delete(f'products/{product_id}', params={'force': force})
    
    def upload_product_image(self, product_id, image_path, alt_text=None, title=None, caption=None, description=None):
        """
        Upload a main image for a product
        
        Args:
            product_id (int): Product ID
            image_path (str): Path to image file
            alt_text (str, optional): Alt text for the image
            title (str, optional): Title for the image
            caption (str, optional): Caption for the image
            description (str, optional): Description for the image
            
        Returns:
            dict: Updated product data
        """
        # Upload the image to the media library
        media = self.media_manager.upload_image(
            image_path,
            alt_text=alt_text,
            title=title,
            caption=caption,
            description=description
        )
        
        # Update the product with the new image
        return self.update_product(product_id, {
            'images': [{'id': media['id']}]
        })
    
    def upload_gallery_images(self, product_id, image_paths, alt_texts=None, titles=None, captions=None, descriptions=None):
        """
        Upload multiple gallery images for a product
        
        Args:
            product_id (int): Product ID
            image_paths (list): List of paths to image files
            alt_texts (list, optional): List of alt texts for the images
            titles (list, optional): List of titles for the images
            captions (list, optional): List of captions for the images
            descriptions (list, optional): List of descriptions for the images
            
        Returns:
            dict: Updated product data
        """
        # Get the current product data
        product = self.get_product(product_id)
        
        # Keep the existing main image
        existing_images = []
        if product.get('images') and len(product['images']) > 0:
            existing_images = [{'id': product['images'][0]['id']}]
        
        # Upload each gallery image
        gallery_images = []
        for i, image_path in enumerate(image_paths):
            # Get the metadata for this image
            alt_text = alt_texts[i] if alt_texts and i < len(alt_texts) else None
            title = titles[i] if titles and i < len(titles) else None
            caption = captions[i] if captions and i < len(captions) else None
            description = descriptions[i] if descriptions and i < len(descriptions) else None
            
            # Upload the image
            media = self.media_manager.upload_image(
                image_path,
                alt_text=alt_text,
                title=title,
                caption=caption,
                description=description
            )
            
            # Add to gallery images
            gallery_images.append({'id': media['id']})
        
        # Update the product with the new gallery images
        return self.update_product(product_id, {
            'images': existing_images + gallery_images
        })
    
    def update_product_seo(self, product_id, focus_keyword=None, meta_title=None, meta_description=None):
        """
        Update SEO fields for a product (using RankMath format)
        
        Args:
            product_id (int): Product ID
            focus_keyword (str, optional): Focus keyword
            meta_title (str, optional): Meta title
            meta_description (str, optional): Meta description
            
        Returns:
            dict: Updated product data
        """
        # Build the meta data object
        meta_data = []
        
        if focus_keyword:
            meta_data.append({'key': 'rank_math_focus_keyword', 'value': focus_keyword})
        
        if meta_title:
            meta_data.append({'key': 'rank_math_title', 'value': meta_title})
        
        if meta_description:
            meta_data.append({'key': 'rank_math_description', 'value': meta_description})
        
        # Only update if we have meta data to update
        if meta_data:
            return self.update_product(product_id, {'meta_data': meta_data})
        
        return self.get_product(product_id)
    
    def get_product_count(self, **filters):
        """
        Get the total count of products
        
        Args:
            **filters: Filters to apply
            
        Returns:
            int: Total product count
        """
        # Request with limit=1 to minimize data transfer
        params = {
            'per_page': 1,
            **filters
        }
        
        response = self.client.get('products', params=params)
        
        # WooCommerce API returns X-WP-Total header with the total count
        total = response.headers.get('X-WP-Total')
        if total:
            return int(total)
        
        # Fallback: make another request to count
        return len(self.client.get('products', params={'per_page': 100, **filters})) 

# Initialize ProductManager instance (can be shared)
product_manager = ProductManager()

# === Product Routes ===

@products_bp.route('/')
@login_required
def index():
    """Display the list of products"""
    page = request.args.get('page', 1, type=int)
    per_page = Config.WOOCOMMERCE_ITEMS_PER_PAGE
    search_term = request.args.get('search', '')
    
    filters = {}
    if search_term:
        filters['search'] = search_term
        
    try:
        products = product_manager.get_products(page=page, per_page=per_page, **filters)
        total_products = product_manager.get_product_count(**filters)
        total_pages = (total_products + per_page - 1) // per_page
    except Exception as e:
        flash(f"Error fetching products: {str(e)}", "error")
        products = []
        total_pages = 0
        page = 1
        
    return render_template('products/list.html', 
                           products=products, 
                           current_page=page, 
                           total_pages=total_pages,
                           search_term=search_term)

# Add other product-related routes here (e.g., create, edit, delete) if needed 