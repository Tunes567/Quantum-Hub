from flask import Flask, jsonify, request
import os
import sys
import logging
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

# Log startup information
logger.info(f"Python version: {sys.version}")
logger.info(f"Starting simplified app for Vercel deployment")

# Load environment variables
load_dotenv()
logger.info("Environment variables loaded")

# Initialize Flask
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'fallback-secret-key')

# Simple routes for testing
@app.route('/')
def index():
    """Basic index route"""
    try:
        # Show environment information
        env_vars = {
            key: '[SET]' if key in os.environ else '[NOT SET]'
            for key in [
                'FLASK_APP', 'SUPABASE_URL', 'SUPABASE_KEY', 
                'SMPP_HOST', 'SMPP_PORT', 'SMPP_USERNAME',
                'SECRET_KEY', 'PYTHONPATH'
            ]
        }
        
        return jsonify({
            'status': 'ok',
            'message': 'Simplified Vercel Flask app is running',
            'env_vars': env_vars,
            'python_version': sys.version
        })
    except Exception as e:
        logger.exception(f"Error in index route: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/api/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'message': 'API is operational'
    })

@app.route('/api/send-sms', methods=['POST'])
def send_sms():
    """Simplified SMS sending endpoint"""
    try:
        data = request.json
        
        if not data:
            return jsonify({
                'status': 'error',
                'message': 'No data provided'
            }), 400
            
        # Extract required fields
        numbers = data.get('numbers', '')
        content = data.get('content', '')
        
        if not numbers or not content:
            return jsonify({
                'status': 'error',
                'message': 'Missing required fields: numbers or content'
            }), 400
            
        # Just log the request for now
        logger.info(f"SMS request received for numbers: {numbers}")
        
        return jsonify({
            'status': 'success',
            'message': 'SMS request received and logged',
            'numbers': numbers
        })
    except Exception as e:
        logger.exception(f"Error sending SMS: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

# For local testing
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', 8000))) 