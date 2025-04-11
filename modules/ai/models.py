import os
import json
import uuid
import datetime
import openai
import anthropic
import google.generativeai as genai
from config import Config
from utils.logger import log_ai_generation

class AIModel:
    """Base class for AI models"""
    
    def __init__(self, api_key=None):
        """
        Initialize the AI model
        
        Args:
            api_key (str, optional): API key for the AI service
        """
        self.api_key = api_key
    
    def generate(self, prompt, max_tokens=None, temperature=None):
        """
        Generate text based on the prompt
        
        Args:
            prompt (str): The prompt to send to the AI model
            max_tokens (int, optional): Maximum number of tokens to generate
            temperature (float, optional): Sampling temperature
            
        Returns:
            dict: Generation result
        """
        raise NotImplementedError("Subclasses must implement this method")
    
    def log_generation(self, section, item_id, item_name, field, prompt_id, prompt_text, input_data, output, tokens=None, cost=None):
        """
        Log an AI generation event
        
        Args:
            section (str): Section (product, category, brand)
            item_id (int): Item ID
            item_name (str): Item name
            field (str): Field being generated
            prompt_id (str): Prompt ID
            prompt_text (str): Prompt text
            input_data (dict): Input data
            output (str): Generated output
            tokens (int, optional): Tokens used
            cost (float, optional): Cost of generation
            
        Returns:
            dict: Log entry
        """
        return log_ai_generation(
            section=section,
            item_id=item_id,
            item_name=item_name,
            field=field,
            prompt_id=prompt_id,
            prompt_text=prompt_text,
            model=self.get_model_name(),
            input_data=input_data,
            output=output,
            tokens_used=tokens,
            cost=cost
        )
    
    def get_model_name(self):
        """Get the model name"""
        return "base_model"
    
    def test_connection(self):
        """Test the connection to the AI service"""
        try:
            self.generate("Hello, world!", max_tokens=5, temperature=0)
            return True
        except Exception:
            return False


class OpenAIModel(AIModel):
    """OpenAI GPT model implementation"""
    
    def __init__(self, api_key=None, model="gpt-3.5-turbo"):
        """
        Initialize the OpenAI model
        
        Args:
            api_key (str, optional): OpenAI API key
            model (str, optional): Model name (e.g., gpt-3.5-turbo, gpt-4)
        """
        super().__init__(api_key)
        self.api_key = api_key or Config.OPENAI_API_KEY
        self.model = model
        openai.api_key = self.api_key
    
    def generate(self, prompt, max_tokens=None, temperature=None):
        """
        Generate text using OpenAI's GPT models
        
        Args:
            prompt (str): The prompt to send to the model
            max_tokens (int, optional): Maximum number of tokens to generate
            temperature (float, optional): Sampling temperature
            
        Returns:
            dict: Generation result
        """
        # Set default values
        max_tokens = max_tokens or 1000
        temperature = temperature if temperature is not None else 0.7
        
        try:
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=max_tokens,
                temperature=temperature
            )
            
            # Extract the generated text
            generated_text = response.choices[0].message.content
            
            # Calculate tokens and cost
            prompt_tokens = response.usage.prompt_tokens
            completion_tokens = response.usage.completion_tokens
            total_tokens = prompt_tokens + completion_tokens
            
            # Approximate cost calculation
            # This is a rough estimate and should be updated based on OpenAI's pricing
            cost = 0
            if self.model == "gpt-3.5-turbo":
                cost = (prompt_tokens * 0.0000015) + (completion_tokens * 0.000002)
            elif self.model == "gpt-4":
                cost = (prompt_tokens * 0.00003) + (completion_tokens * 0.00006)
            elif self.model == "gpt-4-32k":
                cost = (prompt_tokens * 0.00006) + (completion_tokens * 0.00012)
            
            return {
                "text": generated_text,
                "tokens": total_tokens,
                "cost": cost
            }
        except Exception as e:
            return {
                "text": f"Error generating text: {str(e)}",
                "error": str(e)
            }
    
    def get_model_name(self):
        """Get the model name"""
        return self.model


class ClaudeModel(AIModel):
    """Anthropic Claude model implementation"""
    
    def __init__(self, api_key=None, model="claude-3-sonnet-20240229"):
        """
        Initialize the Claude model
        
        Args:
            api_key (str, optional): Anthropic API key
            model (str, optional): Model name (e.g., claude-3-sonnet-20240229)
        """
        super().__init__(api_key)
        self.api_key = api_key or Config.CLAUDE_API_KEY
        self.model = model
        self.client = anthropic.Anthropic(api_key=self.api_key)
    
    def generate(self, prompt, max_tokens=None, temperature=None):
        """
        Generate text using Anthropic's Claude models
        
        Args:
            prompt (str): The prompt to send to the model
            max_tokens (int, optional): Maximum number of tokens to generate
            temperature (float, optional): Sampling temperature
            
        Returns:
            dict: Generation result
        """
        # Set default values
        max_tokens = max_tokens or 1000
        temperature = temperature if temperature is not None else 0.7
        
        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=max_tokens,
                temperature=temperature,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            # Extract the generated text
            generated_text = response.content[0].text
            
            # Get usage information
            input_tokens = response.usage.input_tokens
            output_tokens = response.usage.output_tokens
            total_tokens = input_tokens + output_tokens
            
            # Approximate cost calculation
            # This is a rough estimate and should be updated based on Anthropic's pricing
            cost = 0
            if "claude-3-opus" in self.model:
                cost = (input_tokens * 0.00015) + (output_tokens * 0.00075)
            elif "claude-3-sonnet" in self.model:
                cost = (input_tokens * 0.000003) + (output_tokens * 0.000015)
            elif "claude-3-haiku" in self.model:
                cost = (input_tokens * 0.00000025) + (output_tokens * 0.00000125)
            
            return {
                "text": generated_text,
                "tokens": total_tokens,
                "cost": cost
            }
        except Exception as e:
            return {
                "text": f"Error generating text: {str(e)}",
                "error": str(e)
            }
    
    def get_model_name(self):
        """Get the model name"""
        return self.model


class GeminiModel(AIModel):
    """Google Gemini model implementation"""
    
    def __init__(self, api_key=None, model="gemini-1.5-pro"):
        """
        Initialize the Gemini model
        
        Args:
            api_key (str, optional): Google AI API key
            model (str, optional): Model name (e.g., gemini-1.5-pro)
        """
        super().__init__(api_key)
        self.api_key = api_key or Config.GEMINI_API_KEY
        self.model = model
        
        # Configure the API
        genai.configure(api_key=self.api_key)
    
    def generate(self, prompt, max_tokens=None, temperature=None):
        """
        Generate text using Google's Gemini models
        
        Args:
            prompt (str): The prompt to send to the model
            max_tokens (int, optional): Maximum number of tokens to generate
            temperature (float, optional): Sampling temperature
            
        Returns:
            dict: Generation result
        """
        # Set default values
        max_tokens = max_tokens or 1000
        temperature = temperature if temperature is not None else 0.7
        
        try:
            # Initialize the model
            model = genai.GenerativeModel(self.model)
            
            # Generate content
            response = model.generate_content(
                prompt,
                generation_config=genai.GenerationConfig(
                    max_output_tokens=max_tokens,
                    temperature=temperature
                )
            )
            
            # Extract the generated text
            generated_text = response.text
            
            # Gemini doesn't provide token counts directly, so this is estimated
            # Roughly 4 characters per token
            estimated_tokens = (len(prompt) + len(generated_text)) // 4
            
            # Approximate cost calculation
            # This is a rough estimate and should be updated based on Google's pricing
            cost = 0
            if "gemini-1.5-pro" in self.model:
                cost = estimated_tokens * 0.00000375  # $0.00375 per 1K tokens
            elif "gemini-1.5-flash" in self.model:
                cost = estimated_tokens * 0.00000075  # $0.00075 per 1K tokens
            
            return {
                "text": generated_text,
                "tokens": estimated_tokens,
                "cost": cost
            }
        except Exception as e:
            return {
                "text": f"Error generating text: {str(e)}",
                "error": str(e)
            }
    
    def get_model_name(self):
        """Get the model name"""
        return self.model


def get_ai_model(model_name=None, api_key=None):
    """
    Factory function to get an AI model instance
    
    Args:
        model_name (str, optional): Name of the model to use
        api_key (str, optional): API key for the model
        
    Returns:
        AIModel: An instance of the appropriate AI model
    """
    # Use default model if none specified
    if not model_name:
        model_name = Config.DEFAULT_AI_MODEL
    
    # Create the appropriate model
    if "gpt" in model_name.lower():
        return OpenAIModel(api_key=api_key, model=model_name)
    elif "claude" in model_name.lower():
        return ClaudeModel(api_key=api_key, model=model_name)
    elif "gemini" in model_name.lower():
        return GeminiModel(api_key=api_key, model=model_name)
    else:
        # Default to OpenAI
        return OpenAIModel(api_key=api_key, model=model_name) 