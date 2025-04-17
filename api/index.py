import os
import sys
import logging
import traceback

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

# Create a simple fallback Flask app for debugging
from flask import Flask, jsonify, request
fallback_app = Flask(__name__)

@fallback_app.route('/', defaults={'path': ''})
@fallback_app.route('/<path:path>')
def debug_route(path):
    """Debug route that shows environment information"""
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
        
        # List directories to debug
        directories = {
            'root': os.listdir('.') if os.path.exists('.') else [],
            'templates': os.listdir('./templates') if os.path.exists('./templates') else [],
            'api': os.listdir('./api') if os.path.exists('./api') else []
        }
        
        return jsonify({
            'status': 'debug',
            'message': 'Debug route is working',
            'path': path,
            'env_vars': env_vars,
            'python_version': sys.version,
            'directories': directories,
            'request_method': request.method
        })
    except Exception as e:
        logger.exception(f"Error in debug route: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': str(e),
            'traceback': traceback.format_exc()
        }), 500

# Try to import the main app
main_app = None
try:
    # First try to import the simplified app
    try:
        # Try to import from the same directory
        logger.info("Trying to import app from api/app.py")
        from app import app as main_app
        logger.info("Successfully imported app from api/app.py")
    except ImportError:
        # If that fails, try to import from project root
        logger.info("Trying to import app from vercel_app.py")
        sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        from vercel_app import app as main_app
        logger.info("Successfully imported vercel_app")
except Exception as e:
    logger.error(f"Error importing application: {str(e)}")
    logger.error(traceback.format_exc())
    # Continue with fallback app

# This is needed for Vercel serverless function
def handler(request, context):
    """Handle Vercel serverless function request"""
    try:
        if main_app:
            with main_app.request_context(request.environ):
                return main_app(request.environ, lambda status, headers: [status, headers, []])
        else:
            # If main app failed to load, use the fallback app
            with fallback_app.request_context(request.environ):
                return fallback_app(request.environ, lambda status, headers: [status, headers, []])
    except Exception as e:
        logger.exception(f"Error in handler: {str(e)}")
        with fallback_app.request_context(request.environ):
            response = jsonify({
                'status': 'error',
                'message': f'Application error: {str(e)}',
                'traceback': traceback.format_exc()
            })
            return response(request.environ, lambda status, headers: [status, headers, []])

# For local testing
if __name__ == '__main__':
    if main_app:
        main_app.run(host='0.0.0.0', port=int(os.getenv('PORT', 8000)))
    else:
        fallback_app.run(host='0.0.0.0', port=int(os.getenv('PORT', 8000))) 