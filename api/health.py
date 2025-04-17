from flask import Flask, jsonify, Response
import os
import sys
import json
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

def handler(request):
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
        
        response_data = {
            'status': 'healthy',
            'message': 'API is functioning correctly',
            'environment': env_vars,
            'python_version': sys.version
        }
        
        return Response(
            json.dumps(response_data),
            mimetype='application/json',
            status=200
        )
    except Exception as e:
        logger.exception(f"Error in health check: {str(e)}")
        return Response(
            json.dumps({
                'status': 'error',
                'message': str(e)
            }),
            mimetype='application/json',
            status=500
        )

# For Vercel serverless function
def lambda_handler(event, context):
    return handler(event)

# For Flask app
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def health_check(path):
    return handler(None)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', 8000))) 