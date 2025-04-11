import os
import json
import uuid
import datetime
from config import Config

class PromptManager:
    """Manager for AI prompts"""
    
    def __init__(self, prompts_file=None):
        """
        Initialize the prompt manager
        
        Args:
            prompts_file (str, optional): Path to the prompts JSON file
        """
        self.prompts_file = prompts_file or os.path.join(Config.BASE_DIR, 'data', 'prompts.json')
        self._ensure_prompts_file()
    
    def _ensure_prompts_file(self):
        """Ensure the prompts file exists with valid structure"""
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(self.prompts_file), exist_ok=True)
        
        # Create file if it doesn't exist
        if not os.path.exists(self.prompts_file):
            with open(self.prompts_file, 'w') as f:
                json.dump([], f)
    
    def get_prompts(self, target_section=None, target_field=None):
        """
        Get prompts, optionally filtered by section and field
        
        Args:
            target_section (str, optional): Filter by target section
            target_field (str, optional): Filter by target field
            
        Returns:
            list: List of prompts
        """
        with open(self.prompts_file, 'r') as f:
            try:
                prompts = json.load(f)
            except json.JSONDecodeError:
                # If file is corrupted, start fresh
                prompts = []
        
        # Apply filters if provided
        if target_section:
            prompts = [p for p in prompts if p.get('target_section') == target_section]
        
        if target_field:
            prompts = [p for p in prompts if p.get('target_field') == target_field]
        
        return prompts
    
    def get_prompt(self, prompt_id):
        """
        Get a prompt by ID
        
        Args:
            prompt_id (str): Prompt ID
            
        Returns:
            dict: Prompt data or None if not found
        """
        prompts = self.get_prompts()
        
        for prompt in prompts:
            if prompt.get('id') == prompt_id:
                return prompt
        
        return None
    
    def create_prompt(self, name, description, target_section, target_field, model, prompt_template, temperature=0.7, max_tokens=200):
        """
        Create a new prompt
        
        Args:
            name (str): User-friendly name
            description (str): Brief description
            target_section (str): Target section (product/category/brand)
            target_field (str): Target field (title/description/etc.)
            model (str): Default AI model
            prompt_template (str): Prompt template with variables
            temperature (float, optional): Default temperature
            max_tokens (int, optional): Default max tokens
            
        Returns:
            dict: Created prompt
        """
        # Generate a unique ID
        prompt_id = str(uuid.uuid4())
        
        # Create the prompt
        prompt = {
            'id': prompt_id,
            'name': name,
            'description': description,
            'target_section': target_section,
            'target_field': target_field,
            'model': model,
            'prompt_template': prompt_template,
            'temperature': temperature,
            'max_tokens': max_tokens,
            'created_at': datetime.datetime.now().isoformat(),
            'updated_at': datetime.datetime.now().isoformat()
        }
        
        # Add to prompts
        prompts = self.get_prompts()
        prompts.append(prompt)
        
        # Save prompts
        with open(self.prompts_file, 'w') as f:
            json.dump(prompts, f, indent=2)
        
        return prompt
    
    def update_prompt(self, prompt_id, **kwargs):
        """
        Update a prompt
        
        Args:
            prompt_id (str): Prompt ID
            **kwargs: Fields to update
            
        Returns:
            dict: Updated prompt or None if not found
        """
        prompts = self.get_prompts()
        
        for i, prompt in enumerate(prompts):
            if prompt.get('id') == prompt_id:
                # Update fields
                for key, value in kwargs.items():
                    if key != 'id' and key != 'created_at':
                        prompt[key] = value
                
                # Update timestamp
                prompt['updated_at'] = datetime.datetime.now().isoformat()
                
                # Save prompts
                with open(self.prompts_file, 'w') as f:
                    json.dump(prompts, f, indent=2)
                
                return prompt
        
        return None
    
    def delete_prompt(self, prompt_id):
        """
        Delete a prompt
        
        Args:
            prompt_id (str): Prompt ID
            
        Returns:
            bool: True if deleted, False if not found
        """
        prompts = self.get_prompts()
        
        for i, prompt in enumerate(prompts):
            if prompt.get('id') == prompt_id:
                # Remove the prompt
                prompts.pop(i)
                
                # Save prompts
                with open(self.prompts_file, 'w') as f:
                    json.dump(prompts, f, indent=2)
                
                return True
        
        return False
    
    def get_default_prompts(self):
        """
        Get the default prompts for each section/field combination
        
        Returns:
            dict: Default prompts mapped by section/field
        """
        # Create a dictionary to store default prompts
        defaults = {}
        
        # Get all prompts
        prompts = self.get_prompts()
        
        # Group by section/field
        for prompt in prompts:
            section = prompt.get('target_section')
            field = prompt.get('target_field')
            
            if section and field:
                key = f"{section}_{field}"
                
                # If this is the first prompt for this section/field, make it the default
                if key not in defaults:
                    defaults[key] = prompt
        
        return defaults
    
    def set_default_prompt(self, section, field, prompt_id):
        """
        Set the default prompt for a section/field
        
        Args:
            section (str): Target section
            field (str): Target field
            prompt_id (str): Prompt ID
            
        Returns:
            bool: True if successful, False otherwise
        """
        # Get the prompt
        prompt = self.get_prompt(prompt_id)
        
        if not prompt:
            return False
        
        # Make sure the prompt matches the section/field
        if prompt.get('target_section') != section or prompt.get('target_field') != field:
            return False
        
        # Get all prompts for this section/field
        prompts = self.get_prompts(target_section=section, target_field=field)
        
        # Update prompts
        all_prompts = self.get_prompts()
        
        # Move the selected prompt to the top of the list
        all_prompts = [p for p in all_prompts if p.get('id') != prompt_id]
        all_prompts.insert(0, prompt)
        
        # Save prompts
        with open(self.prompts_file, 'w') as f:
            json.dump(all_prompts, f, indent=2)
        
        return True
    
    def apply_prompt_template(self, prompt_id, variables):
        """
        Apply variables to a prompt template
        
        Args:
            prompt_id (str): Prompt ID
            variables (dict): Variables to replace in the template
            
        Returns:
            str: Processed prompt
        """
        # Get the prompt
        prompt = self.get_prompt(prompt_id)
        
        if not prompt:
            return None
        
        # Get the template
        template = prompt.get('prompt_template', '')
        
        # Replace variables
        for key, value in variables.items():
            template = template.replace(f"{{{key}}}", str(value))
        
        return template
    
    def initialize_default_prompts(self):
        """
        Initialize with default prompts if none exist
        
        Returns:
            int: Number of prompts created
        """
        # Check if we have any prompts
        existing_prompts = self.get_prompts()
        
        if existing_prompts:
            return 0
        
        # Create default prompts
        created = 0
        
        # Product Title
        self.create_prompt(
            name="Product Title Generator",
            description="Generates a concise, SEO-friendly product title",
            target_section="product",
            target_field="title",
            model="gpt-3.5-turbo",
            prompt_template="Create a concise, SEO-friendly product title for a {product_type} with these features: {attributes}. The brand is {brand}. Make it under 70 characters.",
            temperature=0.7,
            max_tokens=50
        )
        created += 1
        
        # Product Description
        self.create_prompt(
            name="Product Description Generator",
            description="Generates a detailed product description with features and benefits",
            target_section="product",
            target_field="description",
            model="gpt-3.5-turbo",
            prompt_template="Write a detailed product description for a {product_type} with these features: {attributes}. The brand is {brand}. Include key features, benefits, and use cases. Format with bullet points for features.",
            temperature=0.7,
            max_tokens=500
        )
        created += 1
        
        # Product Meta Title
        self.create_prompt(
            name="SEO Meta Title Generator",
            description="Generates an SEO-optimized meta title for a product",
            target_section="product",
            target_field="meta_title",
            model="gpt-3.5-turbo",
            prompt_template="Create an SEO-optimized meta title for a {product_type} by {brand} with these features: {attributes}. Include the main keyword if possible: {focus_keyword}. Keep it under 60 characters.",
            temperature=0.7,
            max_tokens=70
        )
        created += 1
        
        # Product Meta Description
        self.create_prompt(
            name="SEO Meta Description Generator",
            description="Generates an SEO-optimized meta description for a product",
            target_section="product",
            target_field="meta_description",
            model="gpt-3.5-turbo",
            prompt_template="Write an SEO-optimized meta description for a {product_type} by {brand} with these features: {attributes}. Include the main keyword if natural: {focus_keyword}. Make it compelling and under 160 characters.",
            temperature=0.7,
            max_tokens=200
        )
        created += 1
        
        # Category Description
        self.create_prompt(
            name="Category Description Generator",
            description="Generates a comprehensive category description",
            target_section="category",
            target_field="description",
            model="gpt-3.5-turbo",
            prompt_template="Write a detailed description for a product category of {category} products. Cover what these products are, their common uses, benefits, and what customers should look for when buying. Use HTML formatting for headings and lists.",
            temperature=0.7,
            max_tokens=500
        )
        created += 1
        
        # Brand Description
        self.create_prompt(
            name="Brand Description Generator",
            description="Generates a comprehensive brand description",
            target_section="brand",
            target_field="description",
            model="gpt-3.5-turbo",
            prompt_template="Write a detailed description for the brand {brand}. Include information about the brand's history, values, product range, unique selling points, and what makes them stand out in the market. Use HTML formatting for headings and paragraphs.",
            temperature=0.7,
            max_tokens=500
        )
        created += 1
        
        return created 