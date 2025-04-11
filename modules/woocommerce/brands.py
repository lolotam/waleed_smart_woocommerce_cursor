from modules.woocommerce.client import WooCommerceClient
from modules.woocommerce.media import MediaManager
from config import Config

class BrandManager:
    """
    Manager for WooCommerce product brand operations
    (Works with Product Brands plugin or custom taxonomy)
    """
    
    def __init__(self, wc_client=None, taxonomy='product_brand'):
        """
        Initialize the brand manager
        
        Args:
            wc_client (WooCommerceClient, optional): WooCommerce client instance
            taxonomy (str, optional): Brand taxonomy name (default: 'product_brand')
        """
        self.client = wc_client or WooCommerceClient()
        self.media_manager = MediaManager(self.client)
        self.taxonomy = taxonomy
    
    def get_brands(self, page=1, per_page=None, **filters):
        """
        Get a list of product brands with optional filtering
        
        Args:
            page (int, optional): Page number
            per_page (int, optional): Items per page
            **filters: Additional filters (parent, order, etc.)
            
        Returns:
            list: List of brands
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
        endpoint = f'products/{self.taxonomy}'
        return self.client.get(endpoint, params=params)
    
    def get_brand(self, brand_id):
        """
        Get a single product brand by ID
        
        Args:
            brand_id (int): Brand ID
            
        Returns:
            dict: Brand data
        """
        endpoint = f'products/{self.taxonomy}/{brand_id}'
        return self.client.get(endpoint)
    
    def create_brand(self, brand_data):
        """
        Create a new product brand
        
        Args:
            brand_data (dict): Brand data
            
        Returns:
            dict: Created brand data
        """
        endpoint = f'products/{self.taxonomy}'
        return self.client.post(endpoint, data=brand_data)
    
    def update_brand(self, brand_id, brand_data):
        """
        Update an existing product brand
        
        Args:
            brand_id (int): Brand ID
            brand_data (dict): Brand data to update
            
        Returns:
            dict: Updated brand data
        """
        endpoint = f'products/{self.taxonomy}/{brand_id}'
        return self.client.put(endpoint, data=brand_data)
    
    def delete_brand(self, brand_id, force=False):
        """
        Delete a product brand
        
        Args:
            brand_id (int): Brand ID
            force (bool, optional): Whether to force deletion
            
        Returns:
            dict: Response data
        """
        endpoint = f'products/{self.taxonomy}/{brand_id}'
        return self.client.delete(endpoint, params={'force': force})
    
    def upload_brand_image(self, brand_id, image_path, alt_text=None):
        """
        Upload an image for a product brand
        
        Args:
            brand_id (int): Brand ID
            image_path (str): Path to image file
            alt_text (str, optional): Alt text for the image
            
        Returns:
            dict: Updated brand data
        """
        # Upload the image to the media library
        media = self.media_manager.upload_image(
            image_path,
            alt_text=alt_text
        )
        
        # Update the brand with the new image
        return self.update_brand(brand_id, {
            'image': {'id': media['id']}
        })
    
    def update_brand_seo(self, brand_id, focus_keyword=None, meta_title=None, meta_description=None):
        """
        Update SEO fields for a brand (using RankMath format)
        
        Args:
            brand_id (int): Brand ID
            focus_keyword (str, optional): Focus keyword
            meta_title (str, optional): Meta title
            meta_description (str, optional): Meta description
            
        Returns:
            dict: Updated brand data
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
            return self.update_brand(brand_id, {'meta_data': meta_data})
        
        return self.get_brand(brand_id)
    
    def reorder_brands(self, brand_orders):
        """
        Update the order of brands
        
        Args:
            brand_orders (dict): Dictionary mapping brand IDs to menu_order values
            
        Returns:
            list: List of updated brands
        """
        updated_brands = []
        
        # Update each brand
        for brand_id, menu_order in brand_orders.items():
            updated_brand = self.update_brand(brand_id, {'menu_order': menu_order})
            updated_brands.append(updated_brand)
        
        return updated_brands
    
    def get_brand_products(self, brand_id, page=1, per_page=None):
        """
        Get products associated with a specific brand
        
        Args:
            brand_id (int): Brand ID
            page (int, optional): Page number
            per_page (int, optional): Items per page
            
        Returns:
            list: List of products
        """
        # Set default per_page if not provided
        if per_page is None:
            per_page = Config.WOOCOMMERCE_ITEMS_PER_PAGE
        
        # Query parameters
        params = {
            'page': page,
            'per_page': per_page,
            self.taxonomy: brand_id
        }
        
        # Get products with this brand
        from modules.woocommerce.products import ProductManager
        product_manager = ProductManager(self.client)
        return product_manager.get_products(**params) 