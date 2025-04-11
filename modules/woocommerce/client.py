import requests
from woocommerce import API
from config import Config
import logging

class WooCommerceClient:
    """
    Client for interacting with the WooCommerce REST API
    """
    
    def __init__(self, store_url=None, consumer_key=None, consumer_secret=None, verify_ssl=None, timeout=None):
        """
        Initialize the WooCommerce client
        
        Args:
            store_url (str, optional): WooCommerce store URL
            consumer_key (str, optional): WooCommerce consumer key
            consumer_secret (str, optional): WooCommerce consumer secret
            verify_ssl (bool, optional): Whether to verify SSL certificates
            timeout (int, optional): Request timeout in seconds
        """
        # Use provided values or fall back to configuration
        self.store_url = store_url or Config.WOOCOMMERCE_STORE_URL
        self.consumer_key = consumer_key or Config.WOOCOMMERCE_CONSUMER_KEY
        self.consumer_secret = consumer_secret or Config.WOOCOMMERCE_CONSUMER_SECRET
        self.verify_ssl = verify_ssl if verify_ssl is not None else Config.WOOCOMMERCE_VERIFY_SSL
        self.timeout = timeout or Config.WOOCOMMERCE_TIMEOUT
        
        # Initialize WooCommerce API client
        self.api = API(
            url=self.store_url,
            consumer_key=self.consumer_key,
            consumer_secret=self.consumer_secret,
            version="wc/v3",
            timeout=self.timeout,
            verify_ssl=self.verify_ssl,
            query_string_auth=True  # Force authentication via query string for problematic hosting
        )
        
    def get(self, endpoint, params=None):
        """
        Make a GET request to the WooCommerce API
        
        Args:
            endpoint (str): API endpoint (e.g., 'products')
            params (dict, optional): Query parameters
            
        Returns:
            dict or list: Response data
        """
        try:
            response = self.api.get(endpoint, params=params)
            self._check_response(response)
            return response.json()
        except Exception as e:
            self._handle_error(e, endpoint, "GET", params)
            raise
    
    def post(self, endpoint, data):
        """
        Make a POST request to the WooCommerce API
        
        Args:
            endpoint (str): API endpoint (e.g., 'products')
            data (dict): Data to send
            
        Returns:
            dict: Response data
        """
        try:
            response = self.api.post(endpoint, data=data)
            self._check_response(response)
            return response.json()
        except Exception as e:
            self._handle_error(e, endpoint, "POST", data)
            raise
    
    def put(self, endpoint, data):
        """
        Make a PUT request to the WooCommerce API
        
        Args:
            endpoint (str): API endpoint (e.g., 'products/123')
            data (dict): Data to send
            
        Returns:
            dict: Response data
        """
        try:
            response = self.api.put(endpoint, data=data)
            self._check_response(response)
            return response.json()
        except Exception as e:
            self._handle_error(e, endpoint, "PUT", data)
            raise
    
    def delete(self, endpoint, params=None):
        """
        Make a DELETE request to the WooCommerce API
        
        Args:
            endpoint (str): API endpoint (e.g., 'products/123')
            params (dict, optional): Query parameters
            
        Returns:
            dict: Response data
        """
        try:
            response = self.api.delete(endpoint, params=params)
            self._check_response(response)
            return response.json()
        except Exception as e:
            self._handle_error(e, endpoint, "DELETE", params)
            raise
    
    def test_connection(self):
        """
        Test the connection to the WooCommerce API
        
        Returns:
            bool: True if connection is successful, False otherwise
        """
        try:
            # Try to fetch a single product to test connection
            self.get('products', {'per_page': 1})
            return True
        except Exception:
            return False
    
    def _check_response(self, response):
        """
        Check the response for errors
        
        Args:
            response (Response): Response object
            
        Raises:
            Exception: If the response contains an error
        """
        if not 200 <= response.status_code < 300:
            error_message = f"API Error (Status {response.status_code})"
            try:
                error_data = response.json()
                if 'message' in error_data:
                    error_message = f"API Error: {error_data['message']}"
            except:
                pass
            
            raise Exception(error_message)
    
    def _handle_error(self, exception, endpoint, method, data=None):
        """
        Handle API errors
        
        Args:
            exception (Exception): The exception that occurred
            endpoint (str): The API endpoint
            method (str): The HTTP method
            data (dict, optional): The request data
        """
        # Log the error
        logging.error(f"WooCommerce API Error: {method} {endpoint}")
        logging.error(f"Exception: {str(exception)}")
        
        # Log the request data if available
        if data:
            logging.error(f"Request data: {data}") 