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
logger.info("Environment variables loaded")

# Initialize Flask
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'fallback-secret-key')

def handler(request):
    """Main handler for API requests"""
    # Parse path
    path = request.path if hasattr(request, 'path') else '/'
    
    # Simple index route
    if path == '/' or path == '/api':
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
            
            response_data = {
                'status': 'ok',
                'message': 'Simplified Vercel Flask app is running',
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
                json.dumps({
                    'status': 'error',
                    'message': str(e)
                }),
                mimetype='application/json',
                status=500
            )
    
    # Health check endpoint
    elif path == '/api/health':
        return Response(
            json.dumps({
                'status': 'healthy',
                'message': 'API is operational'
            }),
            mimetype='application/json',
            status=200
        )
    
    # SMS sending endpoint
    elif path == '/api/send-sms' and request.method == 'POST':
        try:
            data = request.json
            
            if not data:
                return Response(
                    json.dumps({
                        'status': 'error',
                        'message': 'No data provided'
                    }),
                    mimetype='application/json',
                    status=400
                )
                
            # Extract required fields
            numbers = data.get('numbers', '')
            content = data.get('content', '')
            
            if not numbers or not content:
                return Response(
                    json.dumps({
                        'status': 'error',
                        'message': 'Missing required fields: numbers or content'
                    }),
                    mimetype='application/json',
                    status=400
                )
                
            # Just log the request for now
            logger.info(f"SMS request received for numbers: {numbers}")
            
            return Response(
                json.dumps({
                    'status': 'success',
                    'message': 'SMS request received and logged',
                    'numbers': numbers
                }),
                mimetype='application/json',
                status=200
            )
        except Exception as e:
            logger.exception(f"Error sending SMS: {str(e)}")
            return Response(
                json.dumps({
                    'status': 'error',
                    'message': str(e)
                }),
                mimetype='application/json',
                status=500
            )
    
    # Not found for everything else
    return Response(
        json.dumps({
            'status': 'error',
            'message': 'Endpoint not found'
        }),
        mimetype='application/json',
        status=404
    )

# For Flask app
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>', methods=['GET', 'POST'])
def catch_all(path):
    return handler(request)

# For local testing
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', 8000))) 