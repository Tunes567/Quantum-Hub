from flask import Flask, jsonify, request, Response
import os
import sys
import json
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
logger.info("Environment variables loaded for app.py")

# Initialize Flask - This is the app instance Vercel will use
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'fallback-secret-key')

# Main index route (handles /api/ and potentially other paths based on vercel.json)
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>', methods=['GET'])
def index_route(path):
    """Handles root and other GET requests routed to this file"""
    logger.info(f"Handling GET request for path: {path}")
    try:
        env_vars = {
            key: '[SET]' if key in os.environ else '[NOT SET]'
            for key in [
                'FLASK_APP', 'SUPABASE_URL', 'SUPABASE_KEY', 
                'SMPP_HOST', 'SMPP_PORT', 'SMPP_USERNAME',
                'SECRET_KEY', 'PYTHONPATH'
            ]
        }
        response_data = {
            'status': 'ok',
            'message': f'Simplified Vercel Flask app (app.py) is running at path: {path}',
            'env_vars': env_vars,
            'python_version': sys.version
        }
        return Response(
            json.dumps(response_data),
            mimetype='application/json',
            status=200
        )
    except Exception as e:
        logger.exception(f"Error in index route: {str(e)}")
        return Response(
            json.dumps({'status': 'error', 'message': str(e)}),
            mimetype='application/json',
            status=500
        )

# SMS sending endpoint
@app.route('/send-sms', methods=['POST'])
@app.route('/api/send-sms', methods=['POST']) # Explicitly handle /api/send-sms
def send_sms_route():
    """Simplified SMS sending endpoint"""
    logger.info(f"Handling POST request for path: {request.path}")
    try:
        # Use request.get_json() for Flask
        data = request.get_json()
        
        if not data:
            logger.warning("No data provided in POST request")
            return Response(
                json.dumps({'status': 'error', 'message': 'No JSON data provided'}),
                mimetype='application/json',
                status=400
            )
            
        numbers = data.get('numbers', '')
        content = data.get('content', '')
        
        if not numbers or not content:
            logger.warning("Missing fields: numbers or content")
            return Response(
                json.dumps({'status': 'error', 'message': 'Missing required fields: numbers or content'}),
                mimetype='application/json',
                status=400
            )
            
        logger.info(f"SMS request received for numbers: {numbers}")
        return Response(
            json.dumps({
                'status': 'success',
                'message': 'SMS request received and logged (app.py)',
                'numbers': numbers
            }),
            mimetype='application/json',
            status=200
        )
    except Exception as e:
        logger.exception(f"Error sending SMS: {str(e)}")
        return Response(
            json.dumps({'status': 'error', 'message': str(e)}),
            mimetype='application/json',
            status=500
        )

# Keep this for local testing
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', 8000))) 