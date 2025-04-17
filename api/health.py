from flask import Flask, jsonify
import os
import sys
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def health_check(path):
    """Health check endpoint to verify API functionality"""
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
            'status': 'healthy',
            'message': 'API is functioning correctly',
            'path': path,
            'environment': env_vars,
            'python_version': sys.version
        })
    except Exception as e:
        logger.exception(f"Error in health check: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', 8000))) 