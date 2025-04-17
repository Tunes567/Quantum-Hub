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

# This is the app instance Vercel will look for
app = Flask(__name__)

@app.route('/', defaults={'path': ''}, methods=['GET'])
@app.route('/<path:path>', methods=['GET'])
def handle_health_request(path):
    """Health check endpoint handler"""
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
            'status': 'healthy',
            'message': 'API is functioning correctly (health.py)',
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

# Remove the previous handler/lambda stuff
# def handler(request):
# ... (removed)
# def lambda_handler(event, context):
# ... (removed)

# Keep this for potential local testing, but Vercel won't use it directly
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', 8001))) # Use a different port for local testing if needed 