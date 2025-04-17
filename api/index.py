from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def home(path):
    return jsonify({
        "status": "success",
        "message": "API is working correctly",
        "path": path
    })

@app.route('/api/hello')
def hello():
    return jsonify({
        "message": "Hello from Vercel Serverless Functions!"
    })

# Specific error handler for common issues
@app.errorhandler(500)
def server_error(e):
    return jsonify({
        "status": "error",
        "message": "Internal server error",
        "error": str(e)
    }), 500

# For local testing only - not used in Vercel
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True) 