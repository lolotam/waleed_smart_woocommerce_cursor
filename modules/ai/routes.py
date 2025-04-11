from flask import Blueprint, request, jsonify, render_template, redirect, url_for, flash, session
from flask_login import login_required, current_user
from modules.ai.models import get_ai_model
from modules.ai.prompts import PromptManager
from modules.ai.product_content_generator import ProductContentGenerator
from modules.woocommerce.products import ProductManager
from utils.logger import get_ai_logs, export_logs_to_json
from config import Config
import os
import json

# Create blueprint
ai_bp = Blueprint('ai', __name__)

# Initialize prompt manager
prompt_manager = PromptManager()
# Initialize the product content generator
product_content_generator = ProductContentGenerator(prompt_manager)

# ============= AI API Configuration Routes =============

@ai_bp.route('/configure', methods=['GET', 'POST'])
@login_required
def configure():
    """Configure AI API keys"""
    if request.method == 'POST':
        # Get values from form
        openai_api_key = request.form.get('openai_api_key', '').strip()
        claude_api_key = request.form.get('claude_api_key', '').strip()
        gemini_api_key = request.form.get('gemini_api_key', '').strip()
        default_model = request.form.get('default_model', '').strip()
        
        # Save to session
        if openai_api_key:
            session['openai_api_key'] = openai_api_key
        
        if claude_api_key:
            session['claude_api_key'] = claude_api_key
        
        if gemini_api_key:
            session['gemini_api_key'] = gemini_api_key
        
        if default_model:
            session['default_ai_model'] = default_model
        
        flash('AI configuration updated successfully', 'success')
        return redirect(url_for('ai.configure'))
    
    # Get current values
    openai_api_key = session.get('openai_api_key', Config.OPENAI_API_KEY)
    claude_api_key = session.get('claude_api_key', Config.CLAUDE_API_KEY)
    gemini_api_key = session.get('gemini_api_key', Config.GEMINI_API_KEY)
    default_model = session.get('default_ai_model', Config.DEFAULT_AI_MODEL)
    
    # Test connections
    openai_connected = test_openai_connection(openai_api_key)
    claude_connected = test_claude_connection(claude_api_key)
    gemini_connected = test_gemini_connection(gemini_api_key)
    
    return render_template(
        'ai/configure.html',
        openai_api_key=openai_api_key,
        claude_api_key=claude_api_key,
        gemini_api_key=gemini_api_key,
        default_model=default_model,
        openai_connected=openai_connected,
        claude_connected=claude_connected,
        gemini_connected=gemini_connected
    )

def test_openai_connection(api_key):
    """Test connection to OpenAI API"""
    if not api_key:
        return False
    
    model = get_ai_model("gpt-3.5-turbo", api_key)
    return model.test_connection()

def test_claude_connection(api_key):
    """Test connection to Claude API"""
    if not api_key:
        return False
    
    model = get_ai_model("claude-3-sonnet-20240229", api_key)
    return model.test_connection()

def test_gemini_connection(api_key):
    """Test connection to Gemini API"""
    if not api_key:
        return False
    
    model = get_ai_model("gemini-1.5-pro", api_key)
    return model.test_connection()

# ============= Prompt Management Routes =============

@ai_bp.route('/prompts')
@login_required
def list_prompts():
    """List all prompts"""
    # Get filter parameters
    target_section = request.args.get('section')
    target_field = request.args.get('field')
    
    # Get prompts
    prompts = prompt_manager.get_prompts(
        target_section=target_section,
        target_field=target_field
    )
    
    return render_template(
        'ai/prompts/list.html',
        prompts=prompts,
        target_section=target_section,
        target_field=target_field
    )

@ai_bp.route('/prompts/create', methods=['GET', 'POST'])
@login_required
def create_prompt():
    """Create a new prompt"""
    if request.method == 'POST':
        # Get values from form
        name = request.form.get('name', '').strip()
        description = request.form.get('description', '').strip()
        target_section = request.form.get('target_section', '').strip()
        target_field = request.form.get('target_field', '').strip()
        model = request.form.get('model', '').strip()
        prompt_template = request.form.get('prompt_template', '').strip()
        temperature = float(request.form.get('temperature', 0.7))
        max_tokens = int(request.form.get('max_tokens', 200))
        
        # Validate input
        if not name or not target_section or not target_field or not model or not prompt_template:
            flash('All fields are required', 'error')
            return render_template('ai/prompts/form.html')
        
        # Create the prompt
        prompt = prompt_manager.create_prompt(
            name=name,
            description=description,
            target_section=target_section,
            target_field=target_field,
            model=model,
            prompt_template=prompt_template,
            temperature=temperature,
            max_tokens=max_tokens
        )
        
        flash('Prompt created successfully', 'success')
        return redirect(url_for('ai.list_prompts'))
    
    return render_template('ai/prompts/form.html')

@ai_bp.route('/prompts/edit/<prompt_id>', methods=['GET', 'POST'])
@login_required
def edit_prompt(prompt_id):
    """Edit a prompt"""
    # Get the prompt
    prompt = prompt_manager.get_prompt(prompt_id)
    
    if not prompt:
        flash('Prompt not found', 'error')
        return redirect(url_for('ai.list_prompts'))
    
    if request.method == 'POST':
        # Get values from form
        name = request.form.get('name', '').strip()
        description = request.form.get('description', '').strip()
        target_section = request.form.get('target_section', '').strip()
        target_field = request.form.get('target_field', '').strip()
        model = request.form.get('model', '').strip()
        prompt_template = request.form.get('prompt_template', '').strip()
        temperature = float(request.form.get('temperature', 0.7))
        max_tokens = int(request.form.get('max_tokens', 200))
        
        # Validate input
        if not name or not target_section or not target_field or not model or not prompt_template:
            flash('All fields are required', 'error')
            return render_template('ai/prompts/form.html', prompt=prompt)
        
        # Update the prompt
        updated_prompt = prompt_manager.update_prompt(
            prompt_id,
            name=name,
            description=description,
            target_section=target_section,
            target_field=target_field,
            model=model,
            prompt_template=prompt_template,
            temperature=temperature,
            max_tokens=max_tokens
        )
        
        flash('Prompt updated successfully', 'success')
        return redirect(url_for('ai.list_prompts'))
    
    return render_template('ai/prompts/form.html', prompt=prompt)

@ai_bp.route('/prompts/delete/<prompt_id>', methods=['POST'])
@login_required
def delete_prompt(prompt_id):
    """Delete a prompt"""
    if prompt_manager.delete_prompt(prompt_id):
        flash('Prompt deleted successfully', 'success')
    else:
        flash('Prompt not found', 'error')
    
    return redirect(url_for('ai.list_prompts'))

@ai_bp.route('/prompts/set-default', methods=['POST'])
@login_required
def set_default_prompt():
    """Set a prompt as default for a section/field"""
    section = request.form.get('section')
    field = request.form.get('field')
    prompt_id = request.form.get('prompt_id')
    
    if not section or not field or not prompt_id:
        return jsonify({'success': False, 'message': 'Missing parameters'}), 400
    
    if prompt_manager.set_default_prompt(section, field, prompt_id):
        return jsonify({'success': True})
    else:
        return jsonify({'success': False, 'message': 'Failed to set default prompt'}), 400

@ai_bp.route('/prompts/initialize', methods=['POST'])
@login_required
def initialize_prompts():
    """Initialize default prompts"""
    created = prompt_manager.initialize_default_prompts()
    
    if created > 0:
        flash(f'Created {created} default prompts', 'success')
    else:
        flash('No prompts created (prompts already exist)', 'info')
    
    return redirect(url_for('ai.list_prompts'))

# ============= AI Generation API Endpoints =============

@ai_bp.route('/')
@login_required
def index():
    """Display the AI tools dashboard"""
    return render_template('ai/index.html')

@ai_bp.route('/generate', methods=['POST'])
@login_required
def generate():
    """Generate content using AI"""
    data = request.json
    
    # Required parameters
    product_data = data.get('product_data')
    prompt_id = data.get('prompt_id')
    section = data.get('section', 'product')  # product, category, brand
    field = data.get('field', 'title')  # title, description, meta_title, meta_description
    
    if not product_data:
        return jsonify({'success': False, 'message': 'Product data is required'}), 400
    
    # Generate content based on section and field
    if section == 'product':
        if field == 'title':
            result = product_content_generator.generate_title(product_data, prompt_id)
        elif field == 'description':
            result = product_content_generator.generate_description(product_data, prompt_id)
        elif field in ['meta_title', 'meta_description']:
            result = product_content_generator.generate_seo_content(product_data, prompt_id, field)
        else:
            return jsonify({'success': False, 'message': 'Invalid field'}), 400
    else:
        return jsonify({'success': False, 'message': 'Invalid section'}), 400
    
    if 'error' in result:
        return jsonify({'success': False, 'message': result['error']}), 400
    
    return jsonify({
        'success': True,
        'content': result.get('content'),
        'prompt_used': result.get('prompt_used')
    })

# ============= AI Log Routes =============

@ai_bp.route('/logs')
@login_required
def view_logs():
    """View AI generation logs"""
    # Get filter parameters
    section = request.args.get('section')
    field = request.args.get('field')
    model = request.args.get('model')
    
    # Build filters
    filters = {}
    if section:
        filters['section'] = section
    if field:
        filters['field'] = field
    if model:
        filters['model'] = model
    
    # Get page and limit
    page = int(request.args.get('page', 1))
    limit = int(request.args.get('limit', 50))
    offset = (page - 1) * limit
    
    # Get logs
    logs = get_ai_logs(limit=limit, offset=offset, filters=filters)
    
    return render_template(
        'ai/logs/list.html',
        logs=logs,
        page=page,
        limit=limit,
        section=section,
        field=field,
        model=model
    )

@ai_bp.route('/logs/export', methods=['POST'])
@login_required
def export_logs():
    """Export logs to JSON file"""
    # Create export directory if it doesn't exist
    export_dir = os.path.join(Config.TEMP_FOLDER, 'exports')
    os.makedirs(export_dir, exist_ok=True)
    
    # Create export file
    export_file = os.path.join(export_dir, 'ai_logs_export.json')
    
    if export_logs_to_json(export_file):
        return jsonify({
            'success': True,
            'file': export_file
        })
    else:
        return jsonify({
            'success': False,
            'message': 'Failed to export logs'
        }), 400

# ============= Product AI Generation Routes =============

@ai_bp.route('/products/generate-title', methods=['POST'])
@login_required
def generate_product_title():
    """Generate a title for a product"""
    data = request.json
    
    # Required parameters
    product_id = data.get('product_id')
    prompt_id = data.get('prompt_id')
    
    if not product_id:
        return jsonify({'success': False, 'message': 'Product ID is required'}), 400
    
    # Get product data
    product_manager = ProductManager()
    product = product_manager.get_product(product_id)
    
    if not product:
        return jsonify({'success': False, 'message': 'Product not found'}), 404
    
    # Generate title
    result = product_content_generator.generate_product_title(product, prompt_id=prompt_id)
    
    if not result.get('success', False):
        return jsonify(result), 400
    
    return jsonify(result)

@ai_bp.route('/products/generate-description', methods=['POST'])
@login_required
def generate_product_description():
    """Generate a description for a product"""
    data = request.json
    
    # Required parameters
    product_id = data.get('product_id')
    prompt_id = data.get('prompt_id')
    
    if not product_id:
        return jsonify({'success': False, 'message': 'Product ID is required'}), 400
    
    # Get product data
    product_manager = ProductManager()
    product = product_manager.get_product(product_id)
    
    if not product:
        return jsonify({'success': False, 'message': 'Product not found'}), 404
    
    # Generate description
    result = product_content_generator.generate_product_description(product, prompt_id=prompt_id)
    
    if not result.get('success', False):
        return jsonify(result), 400
    
    return jsonify(result)

@ai_bp.route('/products/generate-seo', methods=['POST'])
@login_required
def generate_product_seo():
    """Generate SEO content for a product"""
    data = request.json
    
    # Required parameters
    product_id = data.get('product_id')
    field = data.get('field', 'meta_title')
    prompt_id = data.get('prompt_id')
    
    if not product_id:
        return jsonify({'success': False, 'message': 'Product ID is required'}), 400
    
    if field not in ['meta_title', 'meta_description']:
        return jsonify({'success': False, 'message': 'Invalid field. Must be meta_title or meta_description.'}), 400
    
    # Get product data
    product_manager = ProductManager()
    product = product_manager.get_product(product_id)
    
    if not product:
        return jsonify({'success': False, 'message': 'Product not found'}), 404
    
    # Generate SEO content
    result = product_content_generator.generate_product_seo(product, prompt_id=prompt_id, field=field)
    
    if not result.get('success', False):
        return jsonify(result), 400
    
    return jsonify(result)

@ai_bp.route('/products/apply-content', methods=['POST'])
@login_required
def apply_product_content():
    """Apply generated content to a product"""
    data = request.json
    
    # Required parameters
    product_id = data.get('product_id')
    
    if not product_id:
        return jsonify({'success': False, 'message': 'Product ID is required'}), 400
    
    # Optional parameters
    title = data.get('title')
    description = data.get('description')
    meta_title = data.get('meta_title')
    meta_description = data.get('meta_description')
    focus_keyword = data.get('focus_keyword')
    
    # Make sure at least one field is provided
    if not any([title, description, meta_title, meta_description, focus_keyword]):
        return jsonify({'success': False, 'message': 'At least one content field must be provided'}), 400
    
    # Update product
    product_manager = ProductManager()
    
    try:
        updated_product = product_content_generator.update_product_with_ai_content(
            product_id,
            title=title,
            description=description,
            meta_title=meta_title,
            meta_description=meta_description,
            focus_keyword=focus_keyword
        )
        
        return jsonify({
            'success': True,
            'product': updated_product
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f"Failed to update product: {str(e)}"
        }), 400

@ai_bp.route('/products/generate-all', methods=['POST'])
@login_required
def generate_all_product_content():
    """Generate and apply all content for a product"""
    data = request.json
    
    # Required parameters
    product_id = data.get('product_id')
    
    if not product_id:
        return jsonify({'success': False, 'message': 'Product ID is required'}), 400
    
    # Optional parameters
    title_prompt_id = data.get('title_prompt_id')
    description_prompt_id = data.get('description_prompt_id')
    meta_title_prompt_id = data.get('meta_title_prompt_id')
    meta_description_prompt_id = data.get('meta_description_prompt_id')
    apply_immediately = data.get('apply_immediately', False)
    
    # Get product data
    product_manager = ProductManager()
    product = product_manager.get_product(product_id)
    
    if not product:
        return jsonify({'success': False, 'message': 'Product not found'}), 404
    
    # Generate content
    results = {}
    
    # Generate title
    title_result = product_content_generator.generate_product_title(product, prompt_id=title_prompt_id)
    if title_result.get('success', False):
        results['title'] = title_result.get('title')
        results['title_cost'] = title_result.get('cost')
        results['title_tokens'] = title_result.get('tokens')
    
    # Generate description
    desc_result = product_content_generator.generate_product_description(product, prompt_id=description_prompt_id)
    if desc_result.get('success', False):
        results['description'] = desc_result.get('description')
        results['description_cost'] = desc_result.get('cost')
        results['description_tokens'] = desc_result.get('tokens')
    
    # Generate meta title
    meta_title_result = product_content_generator.generate_product_seo(product, prompt_id=meta_title_prompt_id, field='meta_title')
    if meta_title_result.get('success', False):
        results['meta_title'] = meta_title_result.get('content')
        results['meta_title_cost'] = meta_title_result.get('cost')
        results['meta_title_tokens'] = meta_title_result.get('tokens')
    
    # Generate meta description
    meta_desc_result = product_content_generator.generate_product_seo(product, prompt_id=meta_description_prompt_id, field='meta_description')
    if meta_desc_result.get('success', False):
        results['meta_description'] = meta_desc_result.get('content')
        results['meta_description_cost'] = meta_desc_result.get('cost')
        results['meta_description_tokens'] = meta_desc_result.get('tokens')
    
    # Calculate total cost and tokens
    total_cost = sum([
        title_result.get('cost', 0) if title_result.get('success', False) else 0,
        desc_result.get('cost', 0) if desc_result.get('success', False) else 0,
        meta_title_result.get('cost', 0) if meta_title_result.get('success', False) else 0,
        meta_desc_result.get('cost', 0) if meta_desc_result.get('success', False) else 0
    ])
    
    total_tokens = sum([
        title_result.get('tokens', 0) if title_result.get('success', False) else 0,
        desc_result.get('tokens', 0) if desc_result.get('success', False) else 0,
        meta_title_result.get('tokens', 0) if meta_title_result.get('success', False) else 0,
        meta_desc_result.get('tokens', 0) if meta_desc_result.get('success', False) else 0
    ])
    
    results['total_cost'] = total_cost
    results['total_tokens'] = total_tokens
    
    # Apply the content if requested
    if apply_immediately and results:
        try:
            updated_product = product_content_generator.update_product_with_ai_content(
                product_id,
                title=results.get('title'),
                description=results.get('description'),
                meta_title=results.get('meta_title'),
                meta_description=results.get('meta_description')
            )
            
            results['applied'] = True
            results['product'] = updated_product
        except Exception as e:
            results['applied'] = False
            results['apply_error'] = str(e)
    
    return jsonify({
        'success': True,
        'results': results
    })

def register_routes(bp):
    """Register all routes for the AI module"""
    
    @bp.route('/prompts', methods=['GET'])
    def get_prompts():
        """Get all available prompts"""
        prompts = prompt_manager.get_all_prompts()
        
        return jsonify({
            'success': True,
            'data': {
                'prompts': prompts
            }
        })
    
    @bp.route('/generate/title', methods=['POST'])
    def generate_title():
        """Generate a product title"""
        data = request.json
        product_id = data.get('product_id')
        prompt_id = data.get('prompt_id')
        custom_input = data.get('custom_input', '')
        
        if not product_id or not prompt_id:
            return jsonify({
                'success': False,
                'error': 'Missing required parameters'
            }), 400
            
        result = product_content_generator.generate_title(
            product_id, prompt_id, custom_input)
            
        return jsonify({
            'success': True,
            'data': result
        })
    
    @bp.route('/generate/description', methods=['POST'])
    def generate_description():
        """Generate a product description"""
        data = request.json
        product_id = data.get('product_id')
        prompt_id = data.get('prompt_id')
        custom_input = data.get('custom_input', '')
        
        if not product_id or not prompt_id:
            return jsonify({
                'success': False,
                'error': 'Missing required parameters'
            }), 400
            
        result = product_content_generator.generate_description(
            product_id, prompt_id, custom_input)
            
        return jsonify({
            'success': True,
            'data': result
        })
    
    @bp.route('/generate/seo', methods=['POST'])
    def generate_seo():
        """Generate SEO metadata for a product"""
        data = request.json
        product_id = data.get('product_id')
        prompt_id = data.get('prompt_id')
        meta_type = data.get('meta_type', 'title')  # title, description, or keywords
        custom_input = data.get('custom_input', '')
        
        if not product_id or not prompt_id or not meta_type:
            return jsonify({
                'success': False,
                'error': 'Missing required parameters'
            }), 400
            
        result = product_content_generator.generate_seo_content(
            product_id, prompt_id, meta_type, custom_input)
            
        return jsonify({
            'success': True,
            'data': result
        })
    
    @bp.route('/apply', methods=['POST'])
    def apply_content():
        """Apply generated content to a product"""
        data = request.json
        product_id = data.get('product_id')
        content_type = data.get('content_type')  # title, description, seo_title, seo_description, seo_keywords
        content = data.get('content')
        
        if not product_id or not content_type or not content:
            return jsonify({
                'success': False,
                'error': 'Missing required parameters'
            }), 400
            
        result = product_content_generator.apply_content_to_product(
            product_id, content_type, content)
            
        return jsonify({
            'success': True,
            'data': {
                'product_id': product_id,
                'content_type': content_type,
                'success': result
            }
        }) 