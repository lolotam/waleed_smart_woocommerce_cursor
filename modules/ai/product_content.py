from modules.ai.models import get_ai_model
from modules.ai.prompts import PromptManager
from modules.woocommerce.products import ProductManager
from flask import session
from config import Config

class ProductContentGenerator:
    """
    Generator for AI-powered product content
    """
    
    def __init__(self, product_manager=None, prompt_manager=None):
        """
        Initialize the product content generator
        
        Args:
            product_manager (ProductManager, optional): Product manager instance
            prompt_manager (PromptManager, optional): Prompt manager instance
        """
        self.product_manager = product_manager or ProductManager()
        self.prompt_manager = prompt_manager or PromptManager()
    
    def _get_model_for_prompt(self, prompt):
        """
        Get the appropriate AI model for a prompt
        
        Args:
            prompt (dict): Prompt data
            
        Returns:
            AIModel: AI model instance
        """
        model_name = prompt.get('model')
        
        # Get API key from session or config
        api_key = None
        if 'gpt' in model_name.lower():
            api_key = session.get('openai_api_key', Config.OPENAI_API_KEY)
        elif 'claude' in model_name.lower():
            api_key = session.get('claude_api_key', Config.CLAUDE_API_KEY)
        elif 'gemini' in model_name.lower():
            api_key = session.get('gemini_api_key', Config.GEMINI_API_KEY)
        
        return get_ai_model(model_name, api_key)
    
    def generate_product_title(self, product, prompt_id=None):
        """
        Generate a title for a product
        
        Args:
            product (dict): Product data
            prompt_id (str, optional): ID of the prompt to use (uses default if None)
            
        Returns:
            dict: Generation result
        """
        # Get prompt to use
        if not prompt_id:
            prompts = self.prompt_manager.get_prompts(
                target_section='product', 
                target_field='title'
            )
            if not prompts:
                self.prompt_manager.initialize_default_prompts()
                prompts = self.prompt_manager.get_prompts(
                    target_section='product', 
                    target_field='title'
                )
            
            if prompts:
                prompt = prompts[0]
                prompt_id = prompt.get('id')
            else:
                return {
                    'success': False,
                    'message': 'No prompts available for product titles'
                }
        else:
            prompt = self.prompt_manager.get_prompt(prompt_id)
            if not prompt:
                return {
                    'success': False,
                    'message': 'Prompt not found'
                }
        
        # Prepare variables for prompt
        product_type = product.get('type', 'product')
        
        # Get product attributes
        attributes = []
        if 'attributes' in product:
            for attr in product.get('attributes', []):
                name = attr.get('name', '')
                options = attr.get('options', [])
                if options and isinstance(options, list):
                    attributes.append(f"{name}: {', '.join(options)}")
                elif 'option' in attr:
                    attributes.append(f"{name}: {attr.get('option')}")
        
        attributes_str = '; '.join(attributes)
        
        # Get product categories
        categories = []
        for category in product.get('categories', []):
            categories.append(category.get('name', ''))
        
        # Get product brand (if available)
        brand = "Unknown"
        for item in product.get('meta_data', []):
            if item.get('key') == '_product_brand':
                brand = item.get('value', 'Unknown')
                break
        
        # Get tags
        tags = []
        for tag in product.get('tags', []):
            tags.append(tag.get('name', ''))
        
        # Prepare variables
        variables = {
            'product_type': product_type,
            'attributes': attributes_str,
            'categories': ', '.join(categories),
            'tags': ', '.join(tags),
            'brand': brand,
            'name': product.get('name', ''),
            'product_id': product.get('id', ''),
            'sku': product.get('sku', '')
        }
        
        # Apply template
        prompt_text = self.prompt_manager.apply_prompt_template(prompt_id, variables)
        
        if not prompt_text:
            return {
                'success': False,
                'message': 'Failed to apply template'
            }
        
        # Get AI model
        model = self._get_model_for_prompt(prompt)
        
        # Generate content
        temperature = prompt.get('temperature', 0.7)
        max_tokens = prompt.get('max_tokens', 50)
        
        result = model.generate(prompt_text, max_tokens=max_tokens, temperature=temperature)
        
        # Check for error
        if 'error' in result:
            return {
                'success': False,
                'message': f"AI generation failed: {result.get('error')}"
            }
        
        # Log the generation
        model.log_generation(
            section='product',
            item_id=product.get('id', 0),
            item_name=product.get('name', 'Unnamed product'),
            field='title',
            prompt_id=prompt_id,
            prompt_text=prompt_text,
            input_data=variables,
            output=result.get('text'),
            tokens=result.get('tokens'),
            cost=result.get('cost')
        )
        
        return {
            'success': True,
            'title': result.get('text'),
            'tokens': result.get('tokens'),
            'cost': result.get('cost'),
            'prompt_id': prompt_id
        }
    
    def generate_product_description(self, product, prompt_id=None):
        """
        Generate a description for a product
        
        Args:
            product (dict): Product data
            prompt_id (str, optional): ID of the prompt to use (uses default if None)
            
        Returns:
            dict: Generation result
        """
        # Get prompt to use
        if not prompt_id:
            prompts = self.prompt_manager.get_prompts(
                target_section='product', 
                target_field='description'
            )
            if not prompts:
                self.prompt_manager.initialize_default_prompts()
                prompts = self.prompt_manager.get_prompts(
                    target_section='product', 
                    target_field='description'
                )
            
            if prompts:
                prompt = prompts[0]
                prompt_id = prompt.get('id')
            else:
                return {
                    'success': False,
                    'message': 'No prompts available for product descriptions'
                }
        else:
            prompt = self.prompt_manager.get_prompt(prompt_id)
            if not prompt:
                return {
                    'success': False,
                    'message': 'Prompt not found'
                }
        
        # Prepare variables for prompt
        product_type = product.get('type', 'product')
        
        # Get product attributes
        attributes = []
        if 'attributes' in product:
            for attr in product.get('attributes', []):
                name = attr.get('name', '')
                options = attr.get('options', [])
                if options and isinstance(options, list):
                    attributes.append(f"{name}: {', '.join(options)}")
                elif 'option' in attr:
                    attributes.append(f"{name}: {attr.get('option')}")
        
        attributes_str = '; '.join(attributes)
        
        # Get product categories
        categories = []
        for category in product.get('categories', []):
            categories.append(category.get('name', ''))
        
        # Get product brand (if available)
        brand = "Unknown"
        for item in product.get('meta_data', []):
            if item.get('key') == '_product_brand':
                brand = item.get('value', 'Unknown')
                break
        
        # Get tags
        tags = []
        for tag in product.get('tags', []):
            tags.append(tag.get('name', ''))
        
        # Get current description
        current_description = product.get('description', '').strip()
        
        # Prepare variables
        variables = {
            'product_type': product_type,
            'attributes': attributes_str,
            'categories': ', '.join(categories),
            'tags': ', '.join(tags),
            'brand': brand,
            'name': product.get('name', ''),
            'current_description': current_description,
            'product_id': product.get('id', ''),
            'sku': product.get('sku', '')
        }
        
        # Apply template
        prompt_text = self.prompt_manager.apply_prompt_template(prompt_id, variables)
        
        if not prompt_text:
            return {
                'success': False,
                'message': 'Failed to apply template'
            }
        
        # Get AI model
        model = self._get_model_for_prompt(prompt)
        
        # Generate content
        temperature = prompt.get('temperature', 0.7)
        max_tokens = prompt.get('max_tokens', 500)
        
        result = model.generate(prompt_text, max_tokens=max_tokens, temperature=temperature)
        
        # Check for error
        if 'error' in result:
            return {
                'success': False,
                'message': f"AI generation failed: {result.get('error')}"
            }
        
        # Log the generation
        model.log_generation(
            section='product',
            item_id=product.get('id', 0),
            item_name=product.get('name', 'Unnamed product'),
            field='description',
            prompt_id=prompt_id,
            prompt_text=prompt_text,
            input_data=variables,
            output=result.get('text'),
            tokens=result.get('tokens'),
            cost=result.get('cost')
        )
        
        return {
            'success': True,
            'description': result.get('text'),
            'tokens': result.get('tokens'),
            'cost': result.get('cost'),
            'prompt_id': prompt_id
        }
    
    def generate_product_seo(self, product, prompt_id=None, field='meta_title'):
        """
        Generate SEO content for a product
        
        Args:
            product (dict): Product data
            prompt_id (str, optional): ID of the prompt to use (uses default if None)
            field (str): SEO field to generate (meta_title or meta_description)
            
        Returns:
            dict: Generation result
        """
        # Validate field
        if field not in ['meta_title', 'meta_description']:
            return {
                'success': False,
                'message': 'Invalid field. Must be meta_title or meta_description.'
            }
        
        # Get prompt to use
        if not prompt_id:
            prompts = self.prompt_manager.get_prompts(
                target_section='product', 
                target_field=field
            )
            if not prompts:
                self.prompt_manager.initialize_default_prompts()
                prompts = self.prompt_manager.get_prompts(
                    target_section='product', 
                    target_field=field
                )
            
            if prompts:
                prompt = prompts[0]
                prompt_id = prompt.get('id')
            else:
                return {
                    'success': False,
                    'message': f'No prompts available for product {field}'
                }
        else:
            prompt = self.prompt_manager.get_prompt(prompt_id)
            if not prompt:
                return {
                    'success': False,
                    'message': 'Prompt not found'
                }
        
        # Prepare variables for prompt
        product_type = product.get('type', 'product')
        
        # Get product attributes
        attributes = []
        if 'attributes' in product:
            for attr in product.get('attributes', []):
                name = attr.get('name', '')
                options = attr.get('options', [])
                if options and isinstance(options, list):
                    attributes.append(f"{name}: {', '.join(options)}")
                elif 'option' in attr:
                    attributes.append(f"{name}: {attr.get('option')}")
        
        attributes_str = '; '.join(attributes)
        
        # Get product categories
        categories = []
        for category in product.get('categories', []):
            categories.append(category.get('name', ''))
        
        # Get product brand (if available)
        brand = "Unknown"
        for item in product.get('meta_data', []):
            if item.get('key') == '_product_brand':
                brand = item.get('value', 'Unknown')
                break
        
        # Get focus keyword (if available)
        focus_keyword = ""
        for item in product.get('meta_data', []):
            if item.get('key') == 'rank_math_focus_keyword':
                focus_keyword = item.get('value', '')
                break
        
        # Prepare variables
        variables = {
            'product_type': product_type,
            'attributes': attributes_str,
            'categories': ', '.join(categories),
            'brand': brand,
            'name': product.get('name', ''),
            'description': product.get('description', ''),
            'focus_keyword': focus_keyword,
            'product_id': product.get('id', ''),
            'sku': product.get('sku', '')
        }
        
        # Apply template
        prompt_text = self.prompt_manager.apply_prompt_template(prompt_id, variables)
        
        if not prompt_text:
            return {
                'success': False,
                'message': 'Failed to apply template'
            }
        
        # Get AI model
        model = self._get_model_for_prompt(prompt)
        
        # Generate content
        temperature = prompt.get('temperature', 0.7)
        max_tokens = prompt.get('max_tokens', 200)
        
        result = model.generate(prompt_text, max_tokens=max_tokens, temperature=temperature)
        
        # Check for error
        if 'error' in result:
            return {
                'success': False,
                'message': f"AI generation failed: {result.get('error')}"
            }
        
        # Log the generation
        model.log_generation(
            section='product',
            item_id=product.get('id', 0),
            item_name=product.get('name', 'Unnamed product'),
            field=field,
            prompt_id=prompt_id,
            prompt_text=prompt_text,
            input_data=variables,
            output=result.get('text'),
            tokens=result.get('tokens'),
            cost=result.get('cost')
        )
        
        return {
            'success': True,
            'content': result.get('text'),
            'tokens': result.get('tokens'),
            'cost': result.get('cost'),
            'prompt_id': prompt_id,
            'field': field
        }
    
    def update_product_with_ai_content(self, product_id, title=None, description=None, meta_title=None, meta_description=None, focus_keyword=None):
        """
        Update a product with AI-generated content
        
        Args:
            product_id (int): Product ID
            title (str, optional): New product title
            description (str, optional): New product description
            meta_title (str, optional): New meta title
            meta_description (str, optional): New meta description
            focus_keyword (str, optional): New focus keyword
            
        Returns:
            dict: Updated product data
        """
        update_data = {}
        
        # Update title if provided
        if title:
            update_data['name'] = title
        
        # Update description if provided
        if description:
            update_data['description'] = description
        
        # Update SEO fields
        seo_meta_data = []
        
        if focus_keyword:
            seo_meta_data.append({'key': 'rank_math_focus_keyword', 'value': focus_keyword})
        
        if meta_title:
            seo_meta_data.append({'key': 'rank_math_title', 'value': meta_title})
        
        if meta_description:
            seo_meta_data.append({'key': 'rank_math_description', 'value': meta_description})
        
        if seo_meta_data:
            update_data['meta_data'] = seo_meta_data
        
        # If we have updates to make
        if update_data:
            return self.product_manager.update_product(product_id, update_data)
        
        # Otherwise, just get the current product data
        return self.product_manager.get_product(product_id) 