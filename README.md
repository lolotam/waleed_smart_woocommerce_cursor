# Waleed Smart WooCommerce

An AI-integrated WooCommerce admin system with enterprise-level features for managing products, categories, and brands with advanced SEO capabilities.

## Features

- 🛍️ **Complete WooCommerce Management**
  - Products, Categories, and Brands
  - SEO optimization for all content
  - Image upload and management
  
- 🧠 **AI Integration**
  - Multiple AI models supported (GPT-4.5, Claude 3.7, Gemini)
  - Custom prompts for each content type
  - Preview and edit generated content
  
- 📊 **Import/Export**
  - Bulk edit via Excel
  - Apply AI to multiple items
  - Export data for backup
  
- 🔐 **License System**
  - Machine-locked licenses
  - Trial and full license options
  - Secure activation process

## Installation

### Prerequisites
- Python 3.9 or higher
- Windows operating system
- WooCommerce store with REST API access

### Steps
1. **Download and extract** the ZIP file
2. **Run the installer**:
   ```
   start.bat
   ```
3. **Activate your license**:
   - Enter your license key when prompted, or
   - Generate a trial license using:
     ```
     python generate_local_license.py --save
     ```

## Configuration

### WooCommerce API Setup
1. In your WordPress admin, go to **WooCommerce → Settings → Advanced → REST API**
2. **Create a key** with **Read/Write** permissions
3. Note your **Consumer Key** and **Consumer Secret**
4. Enter these credentials in the app's **Settings** panel

### AI API Keys
1. Obtain API keys for your preferred AI providers:
   - [OpenAI API Key](https://platform.openai.com/account/api-keys)
   - [Claude API Key](https://console.anthropic.com/)
   - [Google Generative AI API Key](https://ai.google.dev/)
2. Enter these keys in the app's **Settings** panel

## Usage

### Products Management
- **View all products** with advanced filtering
- **Edit products** with AI-assisted content generation
- **Bulk edit** via Excel import/export

### Categories & Brands
- Organize products with hierarchical categories
- Manage brand information and imagery
- Apply SEO optimization to all taxonomies

### AI Prompt Management
- **Create custom prompts** for different content types
- **Select AI models** for different tasks
- **Preview and edit** AI-generated content before saving

## Troubleshooting

- **License Issues**: Run `python generate_local_license.py --type full --save` to create a new license
- **Connection Problems**: Check your WooCommerce API credentials and store URL
- **AI Generation Errors**: Verify your API keys and check logs in the `logs` directory

## Support & Contact

- **Developer**: Waleed Mohamed
- **Email**: dr.vet.waleedtam@gmail.com
- **Phone**: +96555683677

## License

This software is licensed to you personally and cannot be redistributed. See the license agreement for details. #   w a l e e d _ s m a r t _ w o o c o m m e r c e 3  
 