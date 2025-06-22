from http.server import BaseHTTPRequestHandler
import json
import os
import urllib.parse

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed_path = urllib.parse.urlparse(self.path)
        path = parsed_path.path
        
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        if path == '/' or path == '/health':
            response = {
                "status": "ok",
                "message": "SubscriptionPro Enterprise API",
                "version": "1.0.0",
                "database": "configured" if os.environ.get('SUPABASE_URL') else "not_configured"
            }
        elif path == '/api/users' or path == '/users':
            response = self.get_users()
        elif path == '/api/products' or path == '/products':
            response = self.get_products()
        elif path == '/api/subscriptions' or path == '/subscriptions':
            response = self.get_subscriptions()
        elif path == '/api/admin/dashboard' or path == '/admin/dashboard':
            response = self.get_dashboard()
        else:
            response = {"error": "Endpoint not found", "available_endpoints": ["/health", "/users", "/products", "/subscriptions", "/admin/dashboard"]}
        
        self.wfile.write(json.dumps(response).encode())
    
    def get_users(self):
        # Real Supabase integration would go here
        return {
            "message": "Users endpoint ready for Supabase integration",
            "status": "configured",
            "sample_structure": {
                "user_id": "uuid",
                "email": "string",
                "first_name": "string",
                "user_role": "customer|admin"
            }
        }
    
    def get_products(self):
        return {
            "message": "Products endpoint ready for Supabase integration", 
            "status": "configured",
            "sample_structure": {
                "product_id": "uuid",
                "name": "string",
                "price": "decimal",
                "currency": "INR"
            }
        }
    
    def get_subscriptions(self):
        return {
            "message": "Subscriptions endpoint ready for Supabase integration",
            "status": "configured", 
            "sample_structure": {
                "subscription_id": "uuid",
                "user_id": "uuid",
                "product_id": "uuid",
                "status": "active|paused|canceled"
            }
        }
    
    def get_dashboard(self):
        return {
            "message": "Admin dashboard ready for Supabase integration",
            "status": "configured",
            "metrics": {
                "total_users": "count from users table",
                "total_products": "count from products table", 
                "active_subscriptions": "count from subscriptions table",
                "total_revenue": "sum from payments table"
            }
        }