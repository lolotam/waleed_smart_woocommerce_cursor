import os
import base64
import requests
import mimetypes
from modules.woocommerce.client import WooCommerceClient

class MediaManager:
    """
    Manager for WooCommerce media operations
    """
    
    def __init__(self, wc_client=None):
        """
        Initialize the media manager
        
        Args:
            wc_client (WooCommerceClient, optional): WooCommerce client instance
        """
        self.client = wc_client or WooCommerceClient()
    
    def upload_image(self, image_path, alt_text=None, title=None, caption=None, description=None):
        """
        Upload an image to the WooCommerce media library
        
        Args:
            image_path (str): Path to the image file
            alt_text (str, optional): Alt text for the image
            title (str, optional): Title for the image
            caption (str, optional): Caption for the image
            description (str, optional): Description for the image
            
        Returns:
            dict: Media item data
        """
        # Check if file exists
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Image file not found: {image_path}")
        
        # Get file name and mime type
        file_name = os.path.basename(image_path)
        mime_type, _ = mimetypes.guess_type(image_path)
        
        if not mime_type or not mime_type.startswith('image/'):
            raise ValueError(f"File is not a valid image: {image_path}")
        
        # Read file and encode as base64
        with open(image_path, 'rb') as img_file:
            base64_image = base64.b64encode(img_file.read()).decode('utf-8')
        
        # Prepare media data
        media_data = {
            'file': base64_image,
            'name': file_name,
        }
        
        # Add optional fields if provided
        if alt_text:
            media_data['alt_text'] = alt_text
        
        if title:
            media_data['title'] = title
        
        if caption:
            media_data['caption'] = caption
        
        if description:
            media_data['description'] = description
        
        # Upload the image
        return self.client.post('media', data=media_data)
    
    def get_media(self, media_id):
        """
        Get a media item by ID
        
        Args:
            media_id (int): Media ID
            
        Returns:
            dict: Media item data
        """
        return self.client.get(f'media/{media_id}')
    
    def delete_media(self, media_id, force=True):
        """
        Delete a media item
        
        Args:
            media_id (int): Media ID
            force (bool, optional): Whether to force deletion
            
        Returns:
            dict: Response data
        """
        return self.client.delete(f'media/{media_id}', params={'force': force})
    
    def download_image(self, image_url, save_path):
        """
        Download an image from a URL and save it to a file
        
        Args:
            image_url (str): URL of the image
            save_path (str): Path to save the image to
            
        Returns:
            str: Path to the saved image
        """
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        
        # Download the image
        response = requests.get(image_url, stream=True)
        response.raise_for_status()
        
        # Save the image
        with open(save_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        return save_path
    
    def update_media(self, media_id, alt_text=None, title=None, caption=None, description=None):
        """
        Update a media item's metadata
        
        Args:
            media_id (int): Media ID
            alt_text (str, optional): Alt text for the image
            title (str, optional): Title for the image
            caption (str, optional): Caption for the image
            description (str, optional): Description for the image
            
        Returns:
            dict: Updated media item data
        """
        # Prepare update data
        media_data = {}
        
        if alt_text is not None:
            media_data['alt_text'] = alt_text
        
        if title is not None:
            media_data['title'] = {'rendered': title}
        
        if caption is not None:
            media_data['caption'] = {'rendered': caption}
        
        if description is not None:
            media_data['description'] = {'rendered': description}
        
        # Only update if we have data to update
        if media_data:
            return self.client.put(f'media/{media_id}', data=media_data)
        
        # Otherwise, just get the current media data
        return self.get_media(media_id) 