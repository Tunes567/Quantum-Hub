from flask import Flask, request, jsonify
import os
import sys
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

# Create a simple Flask app for debugging
app = Flask(__name__)

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def catch_all(path):
    """Simple debug route to verify Vercel setup"""
    try:
        # Show environment information
        env_vars = {
            key: '[SET]' if key in os.environ else '[NOT SET]'
            for key in [
                'FLASK_APP', 'SUPABASE_URL', 'SUPABASE_KEY', 
                'SMPP_HOST', 'SMPP_PORT', 'SMPP_USERNAME'
            ]
        }
        
        return jsonify({
            'status': 'ok',
            'message': 'Vercel serverless function is running',
            'path': path,
            'env_vars': env_vars,
            'python_version': sys.version,
            'request_method': request.method
        })
    except Exception as e:
        logger.exception(f"Error in catch_all route: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

# This is needed for Vercel serverless function
def handler(request, context):
    """Handle Vercel serverless function request"""
    with app.request_context(request.environ):
        return app(request.environ, lambda status, headers: [status, headers, []])

# For local testing
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', 8000))) 