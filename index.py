from http.server import BaseHTTPRequestHandler
import json
import os

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        response = {
            "status": "ok",
            "message": "SubscriptionPro Enterprise API",
            "version": "1.0.0",
            "path": self.path,
            "database": "configured" if os.environ.get('SUPABASE_URL') else "not_configured"
        }
        self.wfile.write(json.dumps(response).encode())