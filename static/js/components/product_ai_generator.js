/**
 * Product AI Content Generator Component
 * 
 * This component provides an interface to generate AI content for WooCommerce products
 * including titles, descriptions, and SEO meta content.
 */

class ProductAIGenerator {
    constructor(config = {}) {
        this.config = {
            apiBasePath: '/ai',
            productId: null,
            containerSelector: '#ai-content-generator',
            onContentGenerated: null,
            onContentApplied: null,
            ...config
        };

        this.promptsData = null;
        this.selectedPrompts = {
            title: null,
            description: null,
            meta_title: null,
            meta_description: null
        };

        this.generatedContent = {
            title: null,
            description: null,
            meta_title: null,
            meta_description: null
        };

        this.init();
    }

    /**
     * Initialize the component
     */
    init() {
        this.container = document.querySelector(this.config.containerSelector);
        if (!this.container) {
            console.error(`Container ${this.config.containerSelector} not found`);
            return;
        }

        this.render();
        this.loadPrompts();
        this.attachEventListeners();
    }

    /**
     * Render the initial component
     */
    render() {
        this.container.innerHTML = `
            <div class="card">
                <div class="card-header">
                    <h4>AI Content Generator</h4>
                </div>
                <div class="card-body">
                    <div class="mb-4">
                        <h5>Select Prompts</h5>
                        <div class="row">
                            <div class="col-md-6 mb-3">
                                <label for="title-prompt">Title Prompt</label>
                                <select id="title-prompt" class="form-control">
                                    <option value="">Loading prompts...</option>
                                </select>
                            </div>
                            <div class="col-md-6 mb-3">
                                <label for="description-prompt">Description Prompt</label>
                                <select id="description-prompt" class="form-control">
                                    <option value="">Loading prompts...</option>
                                </select>
                            </div>
                            <div class="col-md-6 mb-3">
                                <label for="meta-title-prompt">Meta Title Prompt</label>
                                <select id="meta-title-prompt" class="form-control">
                                    <option value="">Loading prompts...</option>
                                </select>
                            </div>
                            <div class="col-md-6 mb-3">
                                <label for="meta-description-prompt">Meta Description Prompt</label>
                                <select id="meta-description-prompt" class="form-control">
                                    <option value="">Loading prompts...</option>
                                </select>
                            </div>
                        </div>
                    </div>

                    <div class="mb-4">
                        <h5>Generate Content</h5>
                        <div class="mb-3">
                            <div class="btn-group w-100">
                                <button id="generate-title-btn" class="btn btn-outline-primary">
                                    Generate Title
                                </button>
                                <button id="generate-description-btn" class="btn btn-outline-primary">
                                    Generate Description
                                </button>
                                <button id="generate-meta-title-btn" class="btn btn-outline-primary">
                                    Generate Meta Title
                                </button>
                                <button id="generate-meta-description-btn" class="btn btn-outline-primary">
                                    Generate Meta Description
                                </button>
                            </div>
                        </div>
                        <div class="mb-3">
                            <button id="generate-all-btn" class="btn btn-primary btn-lg w-100">
                                Generate All Content
                            </button>
                        </div>
                    </div>

                    <div id="content-preview" class="mb-4 d-none">
                        <h5>Generated Content Preview</h5>
                        <div class="alert alert-info">
                            <p>Review the generated content below before applying it to your product.</p>
                        </div>
                        
                        <div id="title-preview-section" class="mb-3 d-none">
                            <label>Title</label>
                            <div class="input-group mb-2">
                                <textarea id="title-preview" class="form-control" rows="1" readonly></textarea>
                                <div class="input-group-append">
                                    <button id="copy-title-btn" class="btn btn-outline-secondary" type="button">
                                        <i class="fas fa-copy"></i>
                                    </button>
                                </div>
                            </div>
                            <small class="text-muted">Cost: <span id="title-cost">$0.00</span> | Tokens: <span id="title-tokens">0</span></small>
                        </div>
                        
                        <div id="description-preview-section" class="mb-3 d-none">
                            <label>Description</label>
                            <div class="input-group mb-2">
                                <textarea id="description-preview" class="form-control" rows="4" readonly></textarea>
                                <div class="input-group-append">
                                    <button id="copy-description-btn" class="btn btn-outline-secondary" type="button">
                                        <i class="fas fa-copy"></i>
                                    </button>
                                </div>
                            </div>
                            <small class="text-muted">Cost: <span id="description-cost">$0.00</span> | Tokens: <span id="description-tokens">0</span></small>
                        </div>
                        
                        <div id="meta-title-preview-section" class="mb-3 d-none">
                            <label>Meta Title</label>
                            <div class="input-group mb-2">
                                <textarea id="meta-title-preview" class="form-control" rows="1" readonly></textarea>
                                <div class="input-group-append">
                                    <button id="copy-meta-title-btn" class="btn btn-outline-secondary" type="button">
                                        <i class="fas fa-copy"></i>
                                    </button>
                                </div>
                            </div>
                            <small class="text-muted">Cost: <span id="meta-title-cost">$0.00</span> | Tokens: <span id="meta-title-tokens">0</span></small>
                        </div>
                        
                        <div id="meta-description-preview-section" class="mb-3 d-none">
                            <label>Meta Description</label>
                            <div class="input-group mb-2">
                                <textarea id="meta-description-preview" class="form-control" rows="2" readonly></textarea>
                                <div class="input-group-append">
                                    <button id="copy-meta-description-btn" class="btn btn-outline-secondary" type="button">
                                        <i class="fas fa-copy"></i>
                                    </button>
                                </div>
                            </div>
                            <small class="text-muted">Cost: <span id="meta-description-cost">$0.00</span> | Tokens: <span id="meta-description-tokens">0</span></small>
                        </div>
                        
                        <div class="mt-3">
                            <div class="d-flex justify-content-between align-items-center">
                                <div>
                                    <strong>Total Cost: <span id="total-cost">$0.00</span></strong> |
                                    <strong>Total Tokens: <span id="total-tokens">0</span></strong>
                                </div>
                                <div>
                                    <button id="apply-content-btn" class="btn btn-success">
                                        Apply All Content to Product
                                    </button>
                                </div>
                            </div>
                        </div>
                    </div>

                    <div id="result-message" class="alert d-none"></div>
                    <div id="loading-indicator" class="text-center d-none">
                        <div class="spinner-border text-primary" role="status">
                            <span class="sr-only">Loading...</span>
                        </div>
                        <p class="mt-2">Generating content...</p>
                    </div>
                </div>
            </div>
        `;
    }

    /**
     * Load available prompts from the server
     */
    loadPrompts() {
        this.showLoading();
        
        fetch(`${this.config.apiBasePath}/prompts`)
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    this.promptsData = data.prompts;
                    this.populatePromptSelects();
                } else {
                    this.showError('Failed to load prompts: ' + data.message);
                }
            })
            .catch(error => {
                this.showError('Error loading prompts: ' + error.message);
            })
            .finally(() => {
                this.hideLoading();
            });
    }

    /**
     * Populate prompt select dropdowns
     */
    populatePromptSelects() {
        if (!this.promptsData) return;

        const titlePromptSelect = this.container.querySelector('#title-prompt');
        const descriptionPromptSelect = this.container.querySelector('#description-prompt');
        const metaTitlePromptSelect = this.container.querySelector('#meta-title-prompt');
        const metaDescriptionPromptSelect = this.container.querySelector('#meta-description-prompt');

        // Clear existing options
        titlePromptSelect.innerHTML = '';
        descriptionPromptSelect.innerHTML = '';
        metaTitlePromptSelect.innerHTML = '';
        metaDescriptionPromptSelect.innerHTML = '';

        // Add default options
        titlePromptSelect.innerHTML = '<option value="">Default Title Prompt</option>';
        descriptionPromptSelect.innerHTML = '<option value="">Default Description Prompt</option>';
        metaTitlePromptSelect.innerHTML = '<option value="">Default Meta Title Prompt</option>';
        metaDescriptionPromptSelect.innerHTML = '<option value="">Default Meta Description Prompt</option>';

        // Filter prompts by type
        const titlePrompts = this.promptsData.filter(p => p.name.toLowerCase().includes('title') && !p.name.toLowerCase().includes('meta'));
        const descriptionPrompts = this.promptsData.filter(p => p.name.toLowerCase().includes('description') && !p.name.toLowerCase().includes('meta'));
        const metaTitlePrompts = this.promptsData.filter(p => p.name.toLowerCase().includes('meta title'));
        const metaDescriptionPrompts = this.promptsData.filter(p => p.name.toLowerCase().includes('meta description'));

        // Add options to selects
        titlePrompts.forEach(prompt => {
            titlePromptSelect.appendChild(new Option(prompt.name, prompt.id));
        });

        descriptionPrompts.forEach(prompt => {
            descriptionPromptSelect.appendChild(new Option(prompt.name, prompt.id));
        });

        metaTitlePrompts.forEach(prompt => {
            metaTitlePromptSelect.appendChild(new Option(prompt.name, prompt.id));
        });

        metaDescriptionPrompts.forEach(prompt => {
            metaDescriptionPromptSelect.appendChild(new Option(prompt.name, prompt.id));
        });
    }

    /**
     * Attach event listeners to the UI elements
     */
    attachEventListeners() {
        // Prompt selection listeners
        this.container.querySelector('#title-prompt').addEventListener('change', (e) => {
            this.selectedPrompts.title = e.target.value || null;
        });

        this.container.querySelector('#description-prompt').addEventListener('change', (e) => {
            this.selectedPrompts.description = e.target.value || null;
        });

        this.container.querySelector('#meta-title-prompt').addEventListener('change', (e) => {
            this.selectedPrompts.meta_title = e.target.value || null;
        });

        this.container.querySelector('#meta-description-prompt').addEventListener('change', (e) => {
            this.selectedPrompts.meta_description = e.target.value || null;
        });

        // Generate content buttons
        this.container.querySelector('#generate-title-btn').addEventListener('click', () => {
            this.generateProductTitle();
        });

        this.container.querySelector('#generate-description-btn').addEventListener('click', () => {
            this.generateProductDescription();
        });

        this.container.querySelector('#generate-meta-title-btn').addEventListener('click', () => {
            this.generateProductSeo('meta_title');
        });

        this.container.querySelector('#generate-meta-description-btn').addEventListener('click', () => {
            this.generateProductSeo('meta_description');
        });

        this.container.querySelector('#generate-all-btn').addEventListener('click', () => {
            this.generateAllContent();
        });

        // Apply content button
        this.container.querySelector('#apply-content-btn').addEventListener('click', () => {
            this.applyContentToProduct();
        });

        // Copy buttons
        this.container.querySelector('#copy-title-btn').addEventListener('click', () => {
            this.copyToClipboard('title-preview');
        });

        this.container.querySelector('#copy-description-btn').addEventListener('click', () => {
            this.copyToClipboard('description-preview');
        });

        this.container.querySelector('#copy-meta-title-btn').addEventListener('click', () => {
            this.copyToClipboard('meta-title-preview');
        });

        this.container.querySelector('#copy-meta-description-btn').addEventListener('click', () => {
            this.copyToClipboard('meta-description-preview');
        });
    }

    /**
     * Generate product title
     */
    generateProductTitle() {
        if (!this.config.productId) {
            this.showError('Product ID is required');
            return;
        }

        this.showLoading();
        
        fetch(`${this.config.apiBasePath}/products/generate-title`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                product_id: this.config.productId,
                prompt_id: this.selectedPrompts.title
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                this.generatedContent.title = data.title;
                
                // Update preview
                const previewElement = this.container.querySelector('#title-preview');
                previewElement.value = data.title;
                
                // Update stats
                this.container.querySelector('#title-cost').textContent = `$${data.cost.toFixed(6)}`;
                this.container.querySelector('#title-tokens').textContent = data.tokens;
                
                // Show preview section
                this.container.querySelector('#title-preview-section').classList.remove('d-none');
                this.container.querySelector('#content-preview').classList.remove('d-none');
                
                // Update totals
                this.updateTotals();
                
                if (typeof this.config.onContentGenerated === 'function') {
                    this.config.onContentGenerated('title', data);
                }
            } else {
                this.showError('Failed to generate title: ' + data.message);
            }
        })
        .catch(error => {
            this.showError('Error generating title: ' + error.message);
        })
        .finally(() => {
            this.hideLoading();
        });
    }

    /**
     * Generate product description
     */
    generateProductDescription() {
        if (!this.config.productId) {
            this.showError('Product ID is required');
            return;
        }

        this.showLoading();
        
        fetch(`${this.config.apiBasePath}/products/generate-description`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                product_id: this.config.productId,
                prompt_id: this.selectedPrompts.description
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                this.generatedContent.description = data.description;
                
                // Update preview
                const previewElement = this.container.querySelector('#description-preview');
                previewElement.value = data.description;
                
                // Update stats
                this.container.querySelector('#description-cost').textContent = `$${data.cost.toFixed(6)}`;
                this.container.querySelector('#description-tokens').textContent = data.tokens;
                
                // Show preview section
                this.container.querySelector('#description-preview-section').classList.remove('d-none');
                this.container.querySelector('#content-preview').classList.remove('d-none');
                
                // Update totals
                this.updateTotals();
                
                if (typeof this.config.onContentGenerated === 'function') {
                    this.config.onContentGenerated('description', data);
                }
            } else {
                this.showError('Failed to generate description: ' + data.message);
            }
        })
        .catch(error => {
            this.showError('Error generating description: ' + error.message);
        })
        .finally(() => {
            this.hideLoading();
        });
    }

    /**
     * Generate product SEO content (meta title or meta description)
     */
    generateProductSeo(field) {
        if (!this.config.productId) {
            this.showError('Product ID is required');
            return;
        }

        const promptId = field === 'meta_title' 
            ? this.selectedPrompts.meta_title 
            : this.selectedPrompts.meta_description;

        this.showLoading();
        
        fetch(`${this.config.apiBasePath}/products/generate-seo`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                product_id: this.config.productId,
                field: field,
                prompt_id: promptId
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                this.generatedContent[field] = data.content;
                
                // Update preview
                const fieldId = field.replace('_', '-');
                const previewElement = this.container.querySelector(`#${fieldId}-preview`);
                previewElement.value = data.content;
                
                // Update stats
                this.container.querySelector(`#${fieldId}-cost`).textContent = `$${data.cost.toFixed(6)}`;
                this.container.querySelector(`#${fieldId}-tokens`).textContent = data.tokens;
                
                // Show preview section
                this.container.querySelector(`#${fieldId}-preview-section`).classList.remove('d-none');
                this.container.querySelector('#content-preview').classList.remove('d-none');
                
                // Update totals
                this.updateTotals();
                
                if (typeof this.config.onContentGenerated === 'function') {
                    this.config.onContentGenerated(field, data);
                }
            } else {
                this.showError(`Failed to generate ${field.replace('_', ' ')}: ${data.message}`);
            }
        })
        .catch(error => {
            this.showError(`Error generating ${field.replace('_', ' ')}: ${error.message}`);
        })
        .finally(() => {
            this.hideLoading();
        });
    }

    /**
     * Generate all content at once
     */
    generateAllContent() {
        if (!this.config.productId) {
            this.showError('Product ID is required');
            return;
        }

        this.showLoading();
        
        fetch(`${this.config.apiBasePath}/products/generate-all`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                product_id: this.config.productId,
                title_prompt_id: this.selectedPrompts.title,
                description_prompt_id: this.selectedPrompts.description,
                meta_title_prompt_id: this.selectedPrompts.meta_title,
                meta_description_prompt_id: this.selectedPrompts.meta_description,
                apply_immediately: false
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                const results = data.results;
                
                // Update previews
                if (results.title) {
                    this.generatedContent.title = results.title;
                    this.container.querySelector('#title-preview').value = results.title;
                    this.container.querySelector('#title-cost').textContent = `$${results.title_cost.toFixed(6)}`;
                    this.container.querySelector('#title-tokens').textContent = results.title_tokens;
                    this.container.querySelector('#title-preview-section').classList.remove('d-none');
                }
                
                if (results.description) {
                    this.generatedContent.description = results.description;
                    this.container.querySelector('#description-preview').value = results.description;
                    this.container.querySelector('#description-cost').textContent = `$${results.description_cost.toFixed(6)}`;
                    this.container.querySelector('#description-tokens').textContent = results.description_tokens;
                    this.container.querySelector('#description-preview-section').classList.remove('d-none');
                }
                
                if (results.meta_title) {
                    this.generatedContent.meta_title = results.meta_title;
                    this.container.querySelector('#meta-title-preview').value = results.meta_title;
                    this.container.querySelector('#meta-title-cost').textContent = `$${results.meta_title_cost.toFixed(6)}`;
                    this.container.querySelector('#meta-title-tokens').textContent = results.meta_title_tokens;
                    this.container.querySelector('#meta-title-preview-section').classList.remove('d-none');
                }
                
                if (results.meta_description) {
                    this.generatedContent.meta_description = results.meta_description;
                    this.container.querySelector('#meta-description-preview').value = results.meta_description;
                    this.container.querySelector('#meta-description-cost').textContent = `$${results.meta_description_cost.toFixed(6)}`;
                    this.container.querySelector('#meta-description-tokens').textContent = results.meta_description_tokens;
                    this.container.querySelector('#meta-description-preview-section').classList.remove('d-none');
                }
                
                // Show the preview container
                this.container.querySelector('#content-preview').classList.remove('d-none');
                
                // Update totals
                this.container.querySelector('#total-cost').textContent = `$${results.total_cost.toFixed(6)}`;
                this.container.querySelector('#total-tokens').textContent = results.total_tokens;
                
                if (typeof this.config.onContentGenerated === 'function') {
                    this.config.onContentGenerated('all', results);
                }
                
                this.showSuccess('Content generated successfully');
            } else {
                this.showError('Failed to generate content: ' + data.message);
            }
        })
        .catch(error => {
            this.showError('Error generating content: ' + error.message);
        })
        .finally(() => {
            this.hideLoading();
        });
    }

    /**
     * Apply generated content to the product
     */
    applyContentToProduct() {
        if (!this.config.productId) {
            this.showError('Product ID is required');
            return;
        }

        if (!this.generatedContent.title && !this.generatedContent.description && 
            !this.generatedContent.meta_title && !this.generatedContent.meta_description) {
            this.showError('No content has been generated to apply');
            return;
        }

        this.showLoading();
        
        fetch(`${this.config.apiBasePath}/products/apply-content`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                product_id: this.config.productId,
                title: this.generatedContent.title,
                description: this.generatedContent.description,
                meta_title: this.generatedContent.meta_title,
                meta_description: this.generatedContent.meta_description
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                this.showSuccess('Content applied to product successfully');
                
                if (typeof this.config.onContentApplied === 'function') {
                    this.config.onContentApplied(data.product);
                }
            } else {
                this.showError('Failed to apply content: ' + data.message);
            }
        })
        .catch(error => {
            this.showError('Error applying content: ' + error.message);
        })
        .finally(() => {
            this.hideLoading();
        });
    }

    /**
     * Update total cost and tokens
     */
    updateTotals() {
        let totalCost = 0;
        let totalTokens = 0;
        
        // Parse costs and tokens from the UI
        const titleCost = parseFloat(this.container.querySelector('#title-cost').textContent.replace('$', '')) || 0;
        const descCost = parseFloat(this.container.querySelector('#description-cost').textContent.replace('$', '')) || 0;
        const metaTitleCost = parseFloat(this.container.querySelector('#meta-title-cost').textContent.replace('$', '')) || 0;
        const metaDescCost = parseFloat(this.container.querySelector('#meta-description-cost').textContent.replace('$', '')) || 0;
        
        const titleTokens = parseInt(this.container.querySelector('#title-tokens').textContent) || 0;
        const descTokens = parseInt(this.container.querySelector('#description-tokens').textContent) || 0;
        const metaTitleTokens = parseInt(this.container.querySelector('#meta-title-tokens').textContent) || 0;
        const metaDescTokens = parseInt(this.container.querySelector('#meta-description-tokens').textContent) || 0;
        
        // Calculate totals
        totalCost = titleCost + descCost + metaTitleCost + metaDescCost;
        totalTokens = titleTokens + descTokens + metaTitleTokens + metaDescTokens;
        
        // Update UI
        this.container.querySelector('#total-cost').textContent = `$${totalCost.toFixed(6)}`;
        this.container.querySelector('#total-tokens').textContent = totalTokens;
    }

    /**
     * Copy content to clipboard
     */
    copyToClipboard(elementId) {
        const textArea = this.container.querySelector(`#${elementId}`);
        textArea.select();
        document.execCommand('copy');
        
        // Flash effect to indicate copied
        const originalBg = textArea.style.backgroundColor;
        textArea.style.backgroundColor = '#d1e7dd';
        setTimeout(() => {
            textArea.style.backgroundColor = originalBg;
        }, 300);
    }

    /**
     * Show loading indicator
     */
    showLoading() {
        this.container.querySelector('#loading-indicator').classList.remove('d-none');
        this.container.querySelector('#result-message').classList.add('d-none');
    }

    /**
     * Hide loading indicator
     */
    hideLoading() {
        this.container.querySelector('#loading-indicator').classList.add('d-none');
    }

    /**
     * Show success message
     */
    showSuccess(message) {
        const msgElement = this.container.querySelector('#result-message');
        msgElement.textContent = message;
        msgElement.classList.remove('d-none', 'alert-danger');
        msgElement.classList.add('alert-success');
    }

    /**
     * Show error message
     */
    showError(message) {
        const msgElement = this.container.querySelector('#result-message');
        msgElement.textContent = message;
        msgElement.classList.remove('d-none', 'alert-success');
        msgElement.classList.add('alert-danger');
    }

    /**
     * Set the product ID
     */
    setProductId(productId) {
        this.config.productId = productId;
    }

    /**
     * Reset the component
     */
    reset() {
        this.generatedContent = {
            title: null,
            description: null,
            meta_title: null,
            meta_description: null
        };
        
        // Reset preview sections
        this.container.querySelector('#title-preview-section').classList.add('d-none');
        this.container.querySelector('#description-preview-section').classList.add('d-none');
        this.container.querySelector('#meta-title-preview-section').classList.add('d-none');
        this.container.querySelector('#meta-description-preview-section').classList.add('d-none');
        this.container.querySelector('#content-preview').classList.add('d-none');
        
        // Reset preview content
        this.container.querySelector('#title-preview').value = '';
        this.container.querySelector('#description-preview').value = '';
        this.container.querySelector('#meta-title-preview').value = '';
        this.container.querySelector('#meta-description-preview').value = '';
        
        // Reset costs and tokens
        this.container.querySelector('#title-cost').textContent = '$0.00';
        this.container.querySelector('#title-tokens').textContent = '0';
        this.container.querySelector('#description-cost').textContent = '$0.00';
        this.container.querySelector('#description-tokens').textContent = '0';
        this.container.querySelector('#meta-title-cost').textContent = '$0.00';
        this.container.querySelector('#meta-title-tokens').textContent = '0';
        this.container.querySelector('#meta-description-cost').textContent = '$0.00';
        this.container.querySelector('#meta-description-tokens').textContent = '0';
        this.container.querySelector('#total-cost').textContent = '$0.00';
        this.container.querySelector('#total-tokens').textContent = '0';
        
        // Hide result message
        this.container.querySelector('#result-message').classList.add('d-none');
    }
} 