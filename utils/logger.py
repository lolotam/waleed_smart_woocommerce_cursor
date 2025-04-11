import os
import json
import datetime
import uuid
from config import Config

def ensure_log_file():
    """Ensure the log file exists and has a valid JSON structure"""
    # Create logs directory if it doesn't exist
    os.makedirs(os.path.dirname(Config.AI_LOG_FILE), exist_ok=True)
    
    # Check if log file exists
    if not os.path.exists(Config.AI_LOG_FILE):
        # Create new log file with empty array
        with open(Config.AI_LOG_FILE, 'w') as f:
            json.dump([], f)

def log_ai_generation(section, item_id, item_name, field, prompt_id, prompt_text, model, input_data, output, tokens_used=None, cost=None):
    """
    Log an AI generation event
    
    Args:
        section (str): The section (product, category, brand)
        item_id (int): The ID of the item
        item_name (str): The name of the item
        field (str): The field being generated (title, description, etc.)
        prompt_id (str): The ID of the prompt used
        prompt_text (str): The text of the prompt used
        model (str): The AI model used
        input_data (dict): The input data provided to the AI
        output (str): The generated content
        tokens_used (int, optional): The number of tokens used
        cost (float, optional): The estimated cost of the generation
    """
    ensure_log_file()
    
    # Read existing log
    with open(Config.AI_LOG_FILE, 'r') as f:
        try:
            log_data = json.load(f)
        except json.JSONDecodeError:
            # If the file is corrupt, start fresh
            log_data = []
    
    # Create new log entry
    log_entry = {
        'id': str(uuid.uuid4()),
        'timestamp': datetime.datetime.now().isoformat(),
        'section': section,
        'item_id': item_id,
        'item_name': item_name,
        'field': field,
        'prompt_id': prompt_id,
        'prompt_text': prompt_text,
        'model': model,
        'input_data': input_data,
        'output': output,
        'tokens_used': tokens_used,
        'cost': cost
    }
    
    # Add to log
    log_data.append(log_entry)
    
    # Write back to file
    with open(Config.AI_LOG_FILE, 'w') as f:
        json.dump(log_data, f, indent=2)
    
    return log_entry

def get_ai_logs(limit=100, offset=0, filters=None):
    """
    Get AI generation logs with optional filtering
    
    Args:
        limit (int): Maximum number of logs to return
        offset (int): Offset for pagination
        filters (dict, optional): Filters to apply
    
    Returns:
        list: List of log entries
    """
    ensure_log_file()
    
    # Read log file
    with open(Config.AI_LOG_FILE, 'r') as f:
        try:
            log_data = json.load(f)
        except json.JSONDecodeError:
            return []
    
    # Apply filters if provided
    if filters:
        filtered_data = []
        for entry in log_data:
            match = True
            for key, value in filters.items():
                if key in entry and entry[key] != value:
                    match = False
                    break
            if match:
                filtered_data.append(entry)
        log_data = filtered_data
    
    # Sort by timestamp (newest first)
    log_data.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
    
    # Apply pagination
    return log_data[offset:offset+limit]

def export_logs_to_json(output_file):
    """
    Export all logs to a JSON file
    
    Args:
        output_file (str): Path to output file
    
    Returns:
        bool: True if successful, False otherwise
    """
    ensure_log_file()
    
    try:
        # Read log file
        with open(Config.AI_LOG_FILE, 'r') as f:
            log_data = json.load(f)
        
        # Write to output file
        with open(output_file, 'w') as f:
            json.dump(log_data, f, indent=2)
        
        return True
    except Exception:
        return False

def clear_logs():
    """Clear all logs"""
    with open(Config.AI_LOG_FILE, 'w') as f:
        json.dump([], f) 