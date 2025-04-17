from http.server import BaseHTTPRequestHandler
from app import handler as app_handler
from health import handler as health_handler

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path.startswith('/api/health'):
            response = health_handler(self)
        else:
            response = app_handler(self)
            
        self.send_response(response.status_code)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(response.data) 