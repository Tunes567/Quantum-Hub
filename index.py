import os
import sys
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

try:
    # Import the main application
    logger.info("Importing main application from vercel_app.py")
    from vercel_app import app
    logger.info("Successfully imported vercel_app")
except Exception as e:
    logger.error(f"Error importing application: {str(e)}")
    from flask import Flask, jsonify
    app = Flask(__name__)
    
    @app.route('/', defaults={'path': ''})
    @app.route('/<path:path>')
    def error_handler(path):
        return jsonify({
            'status': 'error',
            'message': 'Failed to load the application',
            'error': str(e),
            'path': path
        }), 500

# Vercel requires an "app" variable to be defined
# This is a WSGI application for Vercel to use 