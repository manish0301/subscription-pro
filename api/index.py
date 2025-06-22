from http.server import BaseHTTPRequestHandler
import json
import os
import urllib.parse

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        # Parse the URL path
        parsed_path = urllib.parse.urlparse(self.path)
        path = parsed_path.path
        
        # Remove /api prefix if present
        if path.startswith('/api'):
            path = path[4:]
        
        # Route handling
        if path == '/' or path == '/health':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            response = {
                "status": "ok",
                "message": "SubscriptionPro Enterprise API",
                "version": "1.0.0",
                "database": "supabase" if os.environ.get('SUPABASE_URL') else "not_configured"
            }
            self.wfile.write(json.dumps(response).encode())
            
        elif path == '/users':
            self.handle_users()
        elif path == '/products':
            self.handle_products()
        elif path == '/subscriptions':
            self.handle_subscriptions()
        elif path == '/admin/dashboard':
            self.handle_dashboard()
        else:
            self.send_error(404, "Endpoint not found")
    
    def handle_users(self):
        supabase_url = os.environ.get('SUPABASE_URL')
        if supabase_url:
            # Real Supabase integration will be added here
            users = self.get_supabase_data('users')
        else:
            users = {"error": "Database not configured. Please set SUPABASE_URL environment variable."}
        
        self.send_json_response(users)
    
    def handle_products(self):
        supabase_url = os.environ.get('SUPABASE_URL')
        if supabase_url:
            products = self.get_supabase_data('products')
        else:
            products = {"error": "Database not configured. Please set SUPABASE_URL environment variable."}
        
        self.send_json_response(products)
    
    def handle_subscriptions(self):
        supabase_url = os.environ.get('SUPABASE_URL')
        if supabase_url:
            subscriptions = self.get_supabase_data('subscriptions')
        else:
            subscriptions = {"error": "Database not configured. Please set SUPABASE_URL environment variable."}
        
        self.send_json_response(subscriptions)
    
    def handle_dashboard(self):
        supabase_url = os.environ.get('SUPABASE_URL')
        if supabase_url:
            dashboard_data = {
                "total_users": 0,
                "total_products": 0,
                "active_subscriptions": 0,
                "total_revenue": 0,
                "message": "Connect to Supabase to see real metrics"
            }
        else:
            dashboard_data = {"error": "Database not configured. Please set SUPABASE_URL environment variable."}
        
        self.send_json_response(dashboard_data)
    
    def get_supabase_data(self, table):
        # This will integrate with actual Supabase once credentials are configured
        return {
            "message": f"Supabase {table} endpoint ready",
            "status": "awaiting_credentials",
            "required_env": ["SUPABASE_URL", "SUPABASE_KEY"]
        }
    
    def send_json_response(self, data):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        self.end_headers()