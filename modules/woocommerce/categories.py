from modules.woocommerce.client import WooCommerceClient
from modules.woocommerce.media import MediaManager
from config import Config
# Added imports for Blueprint and route handling
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required

# Define the blueprint
categories_bp = Blueprint('categories', __name__)

class CategoryManager:
    """
    Manager for WooCommerce product category operations
    """
    
    def __init__(self, wc_client=None):
        """
        Initialize the category manager
        
        Args:
            wc_client (WooCommerceClient, optional): WooCommerce client instance
        """
        self.client = wc_client or WooCommerceClient()
        self.media_manager = MediaManager(self.client)
    
    def get_categories(self, page=1, per_page=None, **filters):
        """
        Get a list of product categories with optional filtering
        
        Args:
            page (int, optional): Page number
            per_page (int, optional): Items per page
            **filters: Additional filters (parent, order, etc.)
            
        Returns:
            list: List of categories
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
        return self.client.get('products/categories', params=params)
    
    def get_category(self, category_id):
        """
        Get a single product category by ID
        
        Args:
            category_id (int): Category ID
            
        Returns:
            dict: Category data
        """
        return self.client.get(f'products/categories/{category_id}')
    
    def create_category(self, category_data):
        """
        Create a new product category
        
        Args:
            category_data (dict): Category data
            
        Returns:
            dict: Created category data
        """
        return self.client.post('products/categories', data=category_data)
    
    def update_category(self, category_id, category_data):
        """
        Update an existing product category
        
        Args:
            category_id (int): Category ID
            category_data (dict): Category data to update
            
        Returns:
            dict: Updated category data
        """
        return self.client.put(f'products/categories/{category_id}', data=category_data)
    
    def delete_category(self, category_id, force=False):
        """
        Delete a product category
        
        Args:
            category_id (int): Category ID
            force (bool, optional): Whether to force deletion
            
        Returns:
            dict: Response data
        """
        return self.client.delete(f'products/categories/{category_id}', params={'force': force})
    
    def upload_category_image(self, category_id, image_path, alt_text=None):
        """
        Upload an image for a product category
        
        Args:
            category_id (int): Category ID
            image_path (str): Path to image file
            alt_text (str, optional): Alt text for the image
            
        Returns:
            dict: Updated category data
        """
        # Upload the image to the media library
        media = self.media_manager.upload_image(
            image_path,
            alt_text=alt_text
        )
        
        # Update the category with the new image
        return self.update_category(category_id, {
            'image': {'id': media['id']}
        })
    
    def update_category_seo(self, category_id, focus_keyword=None, meta_title=None, meta_description=None):
        """
        Update SEO fields for a category (using RankMath format)
        
        Args:
            category_id (int): Category ID
            focus_keyword (str, optional): Focus keyword
            meta_title (str, optional): Meta title
            meta_description (str, optional): Meta description
            
        Returns:
            dict: Updated category data
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
            return self.update_category(category_id, {'meta_data': meta_data})
        
        return self.get_category(category_id)
    
    def get_category_hierarchy(self):
        """
        Get the category hierarchy as a nested structure
        
        Returns:
            list: Hierarchical list of categories
        """
        # Get all categories
        categories = self.get_categories(per_page=100)
        
        # Create a dictionary with category ID as key
        cat_dict = {cat['id']: {**cat, 'children': []} for cat in categories}
        
        # Build the hierarchy
        root_categories = []
        for cat_id, cat in cat_dict.items():
            parent_id = cat.get('parent')
            if parent_id == 0:
                # Top-level category
                root_categories.append(cat)
            elif parent_id in cat_dict:
                # Add as child to parent
                cat_dict[parent_id]['children'].append(cat)
        
        # Sort by menu order
        for cat in cat_dict.values():
            cat['children'].sort(key=lambda x: x.get('menu_order', 0))
        
        root_categories.sort(key=lambda x: x.get('menu_order', 0))
        
        return root_categories
    
    def reorder_categories(self, category_orders):
        """
        Update the order of categories
        
        Args:
            category_orders (dict): Dictionary mapping category IDs to menu_order values
            
        Returns:
            list: List of updated categories
        """
        updated_categories = []
        
        # Update each category
        for category_id, menu_order in category_orders.items():
            updated_cat = self.update_category(category_id, {'menu_order': menu_order})
            updated_categories.append(updated_cat)
        
        return updated_categories 

# Initialize CategoryManager instance (can be shared)
category_manager = CategoryManager()

# === Category Routes ===

@categories_bp.route('/')
@login_required
def index():
    """Display the list of categories"""
    page = request.args.get('page', 1, type=int)
    per_page = Config.WOOCOMMERCE_ITEMS_PER_PAGE
    
    try:
        categories = category_manager.get_categories(page=page, per_page=per_page)
        # Note: WooCommerce API doesn't easily provide total category count via headers like products
        # We might need a separate call or handle pagination differently if needed.
        # For simplicity, we'll assume we get all or enough categories for display.
    except Exception as e:
        flash(f"Error fetching categories: {str(e)}", "error")
        categories = []
        
    return render_template('categories/list.html', 
                           categories=categories, 
                           current_page=page)

# Add other category-related routes here (e.g., create, edit, delete) if needed 