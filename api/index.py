from http.server import BaseHTTPRequestHandler
import json
import os
import urllib.parse
from datetime import datetime, timedelta
import jwt
import hashlib
import hmac
import uuid

# Supabase client setup
try:
    from supabase import create_client, Client
    SUPABASE_AVAILABLE = True
except ImportError:
    SUPABASE_AVAILABLE = False

class handler(BaseHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        self.supabase = None
        if SUPABASE_AVAILABLE and os.environ.get('SUPABASE_URL') and os.environ.get('SUPABASE_KEY'):
            try:
                self.supabase = create_client(
                    os.environ.get('SUPABASE_URL'),
                    os.environ.get('SUPABASE_KEY')
                )
            except Exception as e:
                print(f"Supabase initialization error: {e}")
        super().__init__(*args, **kwargs)

    def do_GET(self):
        try:
            parsed_path = urllib.parse.urlparse(self.path)
            path = parsed_path.path
            query_params = urllib.parse.parse_qs(parsed_path.query)

            # Remove /api prefix if present
            if path.startswith('/api'):
                path = path[4:]

            # Add CORS headers
            self.add_cors_headers()

            # Route handling
            if path == '/' or path == '/health':
                self.handle_health()
            elif path == '/users':
                self.handle_users_get(query_params)
            elif path == '/products':
                self.handle_products_get(query_params)
            elif path == '/subscriptions':
                self.handle_subscriptions_get(query_params)
            elif path == '/admin/dashboard':
                self.handle_dashboard()
            elif path == '/admin/users':
                self.handle_admin_users(query_params)
            elif path == '/admin/analytics':
                self.handle_admin_analytics()
            else:
                self.send_error_response(404, "Endpoint not found")

        except Exception as e:
            self.send_error_response(500, f"Internal server error: {str(e)}")

    def do_POST(self):
        try:
            parsed_path = urllib.parse.urlparse(self.path)
            path = parsed_path.path

            # Remove /api prefix if present
            if path.startswith('/api'):
                path = path[4:]

            # Add CORS headers
            self.add_cors_headers()

            # Get request body
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length).decode('utf-8') if content_length > 0 else '{}'

            try:
                data = json.loads(post_data)
            except json.JSONDecodeError:
                self.send_error_response(400, "Invalid JSON in request body")
                return

            # Route handling
            if path == '/auth/login':
                self.handle_login(data)
            elif path == '/auth/register':
                self.handle_register(data)
            elif path == '/users':
                self.handle_users_post(data)
            elif path == '/products':
                self.handle_products_post(data)
            elif path == '/subscriptions':
                self.handle_subscriptions_post(data)
            elif path == '/payments':
                self.handle_payments_post(data)
            else:
                self.send_error_response(404, "Endpoint not found")

        except Exception as e:
            self.send_error_response(500, f"Internal server error: {str(e)}")

    def do_PUT(self):
        try:
            parsed_path = urllib.parse.urlparse(self.path)
            path = parsed_path.path

            # Remove /api prefix if present
            if path.startswith('/api'):
                path = path[4:]

            # Add CORS headers
            self.add_cors_headers()

            # Get request body
            content_length = int(self.headers.get('Content-Length', 0))
            put_data = self.rfile.read(content_length).decode('utf-8') if content_length > 0 else '{}'

            try:
                data = json.loads(put_data)
            except json.JSONDecodeError:
                self.send_error_response(400, "Invalid JSON in request body")
                return

            # Extract ID from path
            path_parts = path.strip('/').split('/')
            if len(path_parts) >= 2:
                resource_id = path_parts[1]
                resource_type = path_parts[0]

                if resource_type == 'subscriptions':
                    self.handle_subscriptions_put(resource_id, data)
                elif resource_type == 'users':
                    self.handle_users_put(resource_id, data)
                else:
                    self.send_error_response(404, "Resource not found")
            else:
                self.send_error_response(400, "Invalid resource path")

        except Exception as e:
            self.send_error_response(500, f"Internal server error: {str(e)}")

    def do_DELETE(self):
        try:
            parsed_path = urllib.parse.urlparse(self.path)
            path = parsed_path.path

            # Remove /api prefix if present
            if path.startswith('/api'):
                path = path[4:]

            # Add CORS headers
            self.add_cors_headers()

            # Extract ID from path
            path_parts = path.strip('/').split('/')
            if len(path_parts) >= 2:
                resource_id = path_parts[1]
                resource_type = path_parts[0]

                if resource_type == 'subscriptions':
                    self.handle_subscriptions_delete(resource_id)
                else:
                    self.send_error_response(404, "Resource not found")
            else:
                self.send_error_response(400, "Invalid resource path")

        except Exception as e:
            self.send_error_response(500, f"Internal server error: {str(e)}")

    def do_OPTIONS(self):
        self.add_cors_headers()
        self.send_response(200)
        self.end_headers()

    def add_cors_headers(self):
        """Add CORS headers for cross-origin requests"""
        allowed_origins = os.environ.get('CORS_ORIGINS', '*').split(',')
        origin = self.headers.get('Origin', '')

        if '*' in allowed_origins or origin in allowed_origins:
            self.send_header('Access-Control-Allow-Origin', origin or '*')

        self.send_header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization, X-Requested-With')
        self.send_header('Access-Control-Allow-Credentials', 'true')
        self.send_header('Access-Control-Max-Age', '86400')

    def send_json_response(self, data, status_code=200):
        """Send JSON response with proper headers"""
        self.send_response(status_code)
        self.send_header('Content-Type', 'application/json')
        self.add_cors_headers()
        self.end_headers()
        self.wfile.write(json.dumps(data, default=str).encode('utf-8'))

    def send_error_response(self, status_code, message):
        """Send error response"""
        error_data = {
            "error": message,
            "status_code": status_code,
            "timestamp": datetime.utcnow().isoformat()
        }
        self.send_json_response(error_data, status_code)