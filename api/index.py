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

# Log Python version and other info
logger.info(f"Python version: {sys.version}")
logger.info(f"Current working directory: {os.getcwd()}")
logger.info(f"Files in current directory: {', '.join(os.listdir('.'))}")

try:
    # Explicitly add parent directory to path if needed
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    logger.info(f"Updated sys.path: {sys.path}")
    
    # Import the main application
    from vercel_app import app
    logger.info("Successfully imported vercel_app")
except Exception as e:
    logger.error(f"Error importing vercel_app: {str(e)}")
    raise

# This is needed for Vercel serverless function
def handler(request, context):
    """Handle Vercel serverless function request"""
    try:
        with app.request_context(request.environ):
            return app(request.environ, lambda status, headers: [status, headers, []])
    except Exception as e:
        logger.exception(f"Error in handler: {str(e)}")
        from flask import Flask, jsonify
        error_app = Flask(__name__)
        with error_app.request_context(request.environ):
            response = jsonify({
                'status': 'error',
                'message': f'Application error: {str(e)}'
            })
            return response(request.environ, lambda status, headers: [status, headers, []])

# For local testing
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', 8000))) 