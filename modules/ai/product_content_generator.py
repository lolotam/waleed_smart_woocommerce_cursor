"""
Product Content Generator

This file contains the ProductContentGenerator class which handles the generation
of product content using AI, including titles, descriptions, and SEO metadata.
"""

import json
import requests
from flask import current_app

class ProductContentGenerator:
    def __init__(self, prompt_manager):
        """Initialize the content generator with the prompt manager"""
        self.prompt_manager = prompt_manager
        self.openai_api_key = None
    
    def _get_openai_api_key(self):
        """Get the OpenAI API key from plugin settings"""
        # Lazy loading of the API key to ensure we're getting the latest value
        if not self.openai_api_key:
            from ..settings import get_setting
            self.openai_api_key = get_setting('openai_api_key')
        return self.openai_api_key
    
    def _call_openai_api(self, prompt, temperature=0.7, max_tokens=256):
        """Call the OpenAI API to generate content"""
        api_key = self._get_openai_api_key()
        if not api_key:
            raise ValueError("OpenAI API key not configured")
            
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }
        
        data = {
            "model": "gpt-3.5-turbo",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": temperature,
            "max_tokens": max_tokens
        }
        
        try:
            response = requests.post(
                "https://api.openai.com/v1/chat/completions",
                headers=headers,
                json=data
            )
            response.raise_for_status()
            result = response.json()
            return result["choices"][0]["message"]["content"].strip()
        except Exception as e:
            current_app.logger.error(f"Error calling OpenAI API: {str(e)}")
            return None
    
    def generate_title(self, product_data, prompt_id=None, custom_input=""):
        """Generate a product title using AI"""
        prompt_data = self.prompt_manager.get_prompt(prompt_id)
        if not prompt_data:
            return {"error": "Prompt not found"}
            
        prompt_template = prompt_data.get("template")
        temperature = prompt_data.get("temperature", 0.7)
        max_tokens = prompt_data.get("max_tokens", 100)
        
        # Replace placeholders in the prompt template
        filled_prompt = prompt_template.format(
            product_name=product_data.get("name", ""),
            product_description=product_data.get("description", ""),
            custom_input=custom_input
        )
        
        generated_content = self._call_openai_api(filled_prompt, temperature, max_tokens)
        if not generated_content:
            return {"error": "Failed to generate content"}
            
        return {
            "content": generated_content,
            "prompt_used": filled_prompt
        }
    
    def generate_description(self, product_data, prompt_id=None, custom_input=""):
        """Generate a product description using AI"""
        prompt_data = self.prompt_manager.get_prompt(prompt_id)
        if not prompt_data:
            return {"error": "Prompt not found"}
            
        prompt_template = prompt_data.get("template")
        temperature = prompt_data.get("temperature", 0.7)
        max_tokens = prompt_data.get("max_tokens", 500)
        
        # Replace placeholders in the prompt template
        filled_prompt = prompt_template.format(
            product_name=product_data.get("name", ""),
            product_description=product_data.get("description", ""),
            custom_input=custom_input
        )
        
        generated_content = self._call_openai_api(filled_prompt, temperature, max_tokens)
        if not generated_content:
            return {"error": "Failed to generate content"}
            
        return {
            "content": generated_content,
            "prompt_used": filled_prompt
        }
    
    def generate_seo_content(self, product_data, prompt_id=None, meta_type="meta_title", custom_input=""):
        """Generate SEO metadata (title, description, keywords) using AI"""
        prompt_data = self.prompt_manager.get_prompt(prompt_id)
        if not prompt_data:
            return {"error": "Prompt not found"}
            
        prompt_template = prompt_data.get("template")
        temperature = prompt_data.get("temperature", 0.7)
        max_tokens = prompt_data.get("max_tokens", 200)
        
        # Replace placeholders in the prompt template
        filled_prompt = prompt_template.format(
            product_name=product_data.get("name", ""),
            product_description=product_data.get("description", ""),
            meta_type=meta_type,
            custom_input=custom_input
        )
        
        generated_content = self._call_openai_api(filled_prompt, temperature, max_tokens)
        if not generated_content:
            return {"error": "Failed to generate content"}
            
        return {
            "content": generated_content,
            "meta_type": meta_type,
            "prompt_used": filled_prompt
        } 