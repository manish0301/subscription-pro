from http.server import BaseHTTPRequestHandler
import json
import os
import urllib.parse
from datetime import datetime, timedelta, timezone
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
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        self.send_json_response(error_data, status_code)

    def verify_token(self, token):
        """Verify JWT token"""
        try:
            if not token:
                return None

            # Remove 'Bearer ' prefix if present
            if token.startswith('Bearer '):
                token = token[7:]

            # For Supabase, we would verify the JWT token here
            # For now, we'll do basic validation
            secret = os.environ.get('JWT_SECRET', 'your-secret-key')
            payload = jwt.decode(token, secret, algorithms=['HS256'])
            return payload
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None

    def hash_password(self, password):
        """Hash password using SHA256"""
        return hashlib.sha256(password.encode()).hexdigest()

    def generate_token(self, user_data):
        """Generate JWT token"""
        secret = os.environ.get('JWT_SECRET', 'your-secret-key')
        payload = {
            'user_id': str(user_data['user_id']),
            'email': user_data['email'],
            'role': user_data.get('user_role', 'customer'),
            'exp': datetime.now(timezone.utc) + timedelta(hours=24)
        }
        return jwt.encode(payload, secret, algorithm='HS256')

    def handle_health(self):
        """Health check endpoint"""
        health_data = {
            "status": "healthy",
            "service": "SubscriptionPro Enterprise API",
            "version": "1.0.0",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "database": "connected" if self.supabase else "not_configured",
            "environment": os.environ.get('VERCEL_ENV', 'development')
        }
        self.send_json_response(health_data)

    def handle_login(self, data):
        """Handle user login"""
        email = data.get('email')
        password = data.get('password')

        if not email or not password:
            self.send_error_response(400, "Email and password are required")
            return

        if not self.supabase:
            self.send_error_response(503, "Database not available")
            return

        try:
            # Query user from database
            result = self.supabase.table('users').select('*').eq('email', email).execute()

            if not result.data:
                self.send_error_response(401, "Invalid credentials")
                return

            user = result.data[0]
            hashed_password = self.hash_password(password)

            if user['password_hash'] != hashed_password:
                self.send_error_response(401, "Invalid credentials")
                return

            # Generate token
            token = self.generate_token(user)

            # Remove password hash from response
            user_data = {k: v for k, v in user.items() if k != 'password_hash'}

            response_data = {
                "success": True,
                "user": user_data,
                "token": token,
                "message": "Login successful"
            }

            self.send_json_response(response_data)

        except Exception as e:
            self.send_error_response(500, f"Login failed: {str(e)}")

    def handle_register(self, data):
        """Handle user registration"""
        required_fields = ['email', 'password', 'first_name', 'last_name']

        for field in required_fields:
            if not data.get(field):
                self.send_error_response(400, f"{field} is required")
                return

        if not self.supabase:
            self.send_error_response(503, "Database not available")
            return

        try:
            # Check if user already exists
            existing_user = self.supabase.table('users').select('email').eq('email', data['email']).execute()

            if existing_user.data:
                self.send_error_response(409, "User already exists")
                return

            # Create new user
            user_data = {
                'user_id': str(uuid.uuid4()),
                'email': data['email'],
                'password_hash': self.hash_password(data['password']),
                'first_name': data['first_name'],
                'last_name': data['last_name'],
                'phone_number': data.get('phone_number'),
                'user_role': data.get('user_role', 'customer'),
                'address_line1': data.get('address_line1'),
                'city': data.get('city'),
                'state': data.get('state'),
                'country': data.get('country', 'India'),
                'created_at': datetime.now(timezone.utc).isoformat(),
                'updated_at': datetime.now(timezone.utc).isoformat()
            }

            result = self.supabase.table('users').insert(user_data).execute()

            if result.data:
                # Generate token
                token = self.generate_token(result.data[0])

                # Remove password hash from response
                user_response = {k: v for k, v in result.data[0].items() if k != 'password_hash'}

                response_data = {
                    "success": True,
                    "user": user_response,
                    "token": token,
                    "message": "Registration successful"
                }

                self.send_json_response(response_data, 201)
            else:
                self.send_error_response(500, "Failed to create user")

        except Exception as e:
            self.send_error_response(500, f"Registration failed: {str(e)}")

    def handle_users_get(self, query_params):
        """Handle GET /users"""
        # Verify authentication
        auth_header = self.headers.get('Authorization', '')
        user_payload = self.verify_token(auth_header)

        if not user_payload:
            self.send_error_response(401, "Authentication required")
            return

        if not self.supabase:
            self.send_error_response(503, "Database not available")
            return

        try:
            # If admin, can see all users; if customer, only own profile
            if user_payload.get('role') == 'admin':
                result = self.supabase.table('users').select('user_id, email, first_name, last_name, user_role, created_at').execute()
                users_data = result.data
            else:
                result = self.supabase.table('users').select('*').eq('user_id', user_payload['user_id']).execute()
                users_data = result.data

            response_data = {
                "success": True,
                "users": users_data,
                "total": len(users_data)
            }

            self.send_json_response(response_data)

        except Exception as e:
            self.send_error_response(500, f"Failed to fetch users: {str(e)}")

    def handle_products_get(self, query_params):
        """Handle GET /products"""
        if not self.supabase:
            self.send_error_response(503, "Database not available")
            return

        try:
            # Products are publicly accessible
            query = self.supabase.table('products').select('*')

            # Add filters if provided
            if 'category' in query_params:
                # This would be implemented when category field is added
                pass

            if 'search' in query_params:
                search_term = query_params['search'][0]
                query = query.ilike('name', f'%{search_term}%')

            result = query.execute()

            response_data = {
                "success": True,
                "products": result.data,
                "total": len(result.data)
            }

            self.send_json_response(response_data)

        except Exception as e:
            self.send_error_response(500, f"Failed to fetch products: {str(e)}")

    def handle_subscriptions_get(self, query_params):
        """Handle GET /subscriptions"""
        # Verify authentication
        auth_header = self.headers.get('Authorization', '')
        user_payload = self.verify_token(auth_header)

        if not user_payload:
            self.send_error_response(401, "Authentication required")
            return

        if not self.supabase:
            self.send_error_response(503, "Database not available")
            return

        try:
            # Users can only see their own subscriptions unless admin
            if user_payload.get('role') == 'admin':
                query = self.supabase.table('subscriptions').select('*, users(first_name, last_name, email), products(name, price)')
            else:
                query = self.supabase.table('subscriptions').select('*, products(name, price)').eq('user_id', user_payload['user_id'])

            result = query.execute()

            response_data = {
                "success": True,
                "subscriptions": result.data,
                "total": len(result.data)
            }

            self.send_json_response(response_data)

        except Exception as e:
            self.send_error_response(500, f"Failed to fetch subscriptions: {str(e)}")

    def handle_subscriptions_post(self, data):
        """Handle POST /subscriptions - Create new subscription"""
        # Verify authentication
        auth_header = self.headers.get('Authorization', '')
        user_payload = self.verify_token(auth_header)

        if not user_payload:
            self.send_error_response(401, "Authentication required")
            return

        if not self.supabase:
            self.send_error_response(503, "Database not available")
            return

        required_fields = ['product_id', 'frequency', 'start_date']
        for field in required_fields:
            if not data.get(field):
                self.send_error_response(400, f"{field} is required")
                return

        try:
            # Get product details
            product_result = self.supabase.table('products').select('*').eq('product_id', data['product_id']).execute()

            if not product_result.data:
                self.send_error_response(404, "Product not found")
                return

            product = product_result.data[0]

            # Calculate next delivery date based on frequency
            start_date = datetime.fromisoformat(data['start_date'].replace('Z', '+00:00'))

            if data['frequency'] == 'weekly':
                next_delivery = start_date + timedelta(weeks=1)
            elif data['frequency'] == 'monthly':
                next_delivery = start_date + timedelta(days=30)
            elif data['frequency'] == 'quarterly':
                next_delivery = start_date + timedelta(days=90)
            else:  # yearly
                next_delivery = start_date + timedelta(days=365)

            # Create subscription
            subscription_data = {
                'subscription_id': str(uuid.uuid4()),
                'user_id': user_payload['user_id'],
                'product_id': data['product_id'],
                'status': 'active',
                'frequency': data['frequency'],
                'quantity': data.get('quantity', 1),
                'amount': float(product['price']) * data.get('quantity', 1),
                'start_date': data['start_date'],
                'next_delivery_date': next_delivery.isoformat(),
                'created_at': datetime.now(timezone.utc).isoformat(),
                'updated_at': datetime.now(timezone.utc).isoformat()
            }

            result = self.supabase.table('subscriptions').insert(subscription_data).execute()

            if result.data:
                response_data = {
                    "success": True,
                    "subscription": result.data[0],
                    "message": "Subscription created successfully"
                }
                self.send_json_response(response_data, 201)
            else:
                self.send_error_response(500, "Failed to create subscription")

        except Exception as e:
            self.send_error_response(500, f"Failed to create subscription: {str(e)}")

    def handle_subscriptions_put(self, subscription_id, data):
        """Handle PUT /subscriptions/{id} - Update subscription"""
        # Verify authentication
        auth_header = self.headers.get('Authorization', '')
        user_payload = self.verify_token(auth_header)

        if not user_payload:
            self.send_error_response(401, "Authentication required")
            return

        if not self.supabase:
            self.send_error_response(503, "Database not available")
            return

        try:
            # Check if subscription exists and user has permission
            query = self.supabase.table('subscriptions').select('*').eq('subscription_id', subscription_id)

            if user_payload.get('role') != 'admin':
                query = query.eq('user_id', user_payload['user_id'])

            result = query.execute()

            if not result.data:
                self.send_error_response(404, "Subscription not found")
                return

            # Update subscription
            update_data = {
                'updated_at': datetime.now(timezone.utc).isoformat()
            }

            # Only allow certain fields to be updated
            allowed_fields = ['status', 'quantity', 'next_delivery_date']
            for field in allowed_fields:
                if field in data:
                    update_data[field] = data[field]

            update_result = self.supabase.table('subscriptions').update(update_data).eq('subscription_id', subscription_id).execute()

            if update_result.data:
                response_data = {
                    "success": True,
                    "subscription": update_result.data[0],
                    "message": "Subscription updated successfully"
                }
                self.send_json_response(response_data)
            else:
                self.send_error_response(500, "Failed to update subscription")

        except Exception as e:
            self.send_error_response(500, f"Failed to update subscription: {str(e)}")

    def handle_subscriptions_delete(self, subscription_id):
        """Handle DELETE /subscriptions/{id} - Cancel subscription"""
        # Verify authentication
        auth_header = self.headers.get('Authorization', '')
        user_payload = self.verify_token(auth_header)

        if not user_payload:
            self.send_error_response(401, "Authentication required")
            return

        if not self.supabase:
            self.send_error_response(503, "Database not available")
            return

        try:
            # Check if subscription exists and user has permission
            query = self.supabase.table('subscriptions').select('*').eq('subscription_id', subscription_id)

            if user_payload.get('role') != 'admin':
                query = query.eq('user_id', user_payload['user_id'])

            result = query.execute()

            if not result.data:
                self.send_error_response(404, "Subscription not found")
                return

            # Update status to canceled instead of deleting
            update_data = {
                'status': 'canceled',
                'updated_at': datetime.now(timezone.utc).isoformat()
            }

            update_result = self.supabase.table('subscriptions').update(update_data).eq('subscription_id', subscription_id).execute()

            if update_result.data:
                response_data = {
                    "success": True,
                    "message": "Subscription canceled successfully"
                }
                self.send_json_response(response_data)
            else:
                self.send_error_response(500, "Failed to cancel subscription")

        except Exception as e:
            self.send_error_response(500, f"Failed to cancel subscription: {str(e)}")

    def handle_dashboard(self):
        """Handle GET /admin/dashboard"""
        # Verify admin authentication
        auth_header = self.headers.get('Authorization', '')
        user_payload = self.verify_token(auth_header)

        if not user_payload or user_payload.get('role') != 'admin':
            self.send_error_response(403, "Admin access required")
            return

        if not self.supabase:
            self.send_error_response(503, "Database not available")
            return

        try:
            # Get dashboard metrics
            users_result = self.supabase.table('users').select('user_id', count='exact').execute()
            products_result = self.supabase.table('products').select('product_id', count='exact').execute()
            subscriptions_result = self.supabase.table('subscriptions').select('subscription_id', count='exact').eq('status', 'active').execute()
            payments_result = self.supabase.table('payments').select('amount').eq('status', 'successful').execute()

            total_revenue = sum(float(payment['amount']) for payment in payments_result.data) if payments_result.data else 0

            dashboard_data = {
                "success": True,
                "metrics": {
                    "total_users": users_result.count or 0,
                    "total_products": products_result.count or 0,
                    "active_subscriptions": subscriptions_result.count or 0,
                    "total_revenue": total_revenue,
                    "currency": "INR"
                },
                "timestamp": datetime.now(timezone.utc).isoformat()
            }

            self.send_json_response(dashboard_data)

        except Exception as e:
            self.send_error_response(500, f"Failed to fetch dashboard data: {str(e)}")

    def handle_admin_users(self, query_params):
        """Handle GET /admin/users"""
        # Verify admin authentication
        auth_header = self.headers.get('Authorization', '')
        user_payload = self.verify_token(auth_header)

        if not user_payload or user_payload.get('role') != 'admin':
            self.send_error_response(403, "Admin access required")
            return

        if not self.supabase:
            self.send_error_response(503, "Database not available")
            return

        try:
            # Get all users with their subscription counts
            users_result = self.supabase.table('users').select('user_id, email, first_name, last_name, user_role, created_at').execute()

            # Get subscription counts for each user
            for user in users_result.data:
                subs_result = self.supabase.table('subscriptions').select('subscription_id', count='exact').eq('user_id', user['user_id']).execute()
                user['subscription_count'] = subs_result.count or 0

            response_data = {
                "success": True,
                "users": users_result.data,
                "total": len(users_result.data)
            }

            self.send_json_response(response_data)

        except Exception as e:
            self.send_error_response(500, f"Failed to fetch admin users: {str(e)}")

    def handle_admin_analytics(self):
        """Handle GET /admin/analytics"""
        # Verify admin authentication
        auth_header = self.headers.get('Authorization', '')
        user_payload = self.verify_token(auth_header)

        if not user_payload or user_payload.get('role') != 'admin':
            self.send_error_response(403, "Admin access required")
            return

        if not self.supabase:
            self.send_error_response(503, "Database not available")
            return

        try:
            # Get analytics data
            # This is a simplified version - in production you'd want more sophisticated analytics
            subscriptions_by_status = {}
            status_result = self.supabase.table('subscriptions').select('status').execute()

            for sub in status_result.data:
                status = sub['status']
                subscriptions_by_status[status] = subscriptions_by_status.get(status, 0) + 1

            # Revenue by month (simplified)
            payments_result = self.supabase.table('payments').select('amount, payment_date').eq('status', 'successful').execute()

            monthly_revenue = {}
            for payment in payments_result.data:
                if payment['payment_date']:
                    month = payment['payment_date'][:7]  # YYYY-MM
                    monthly_revenue[month] = monthly_revenue.get(month, 0) + float(payment['amount'])

            analytics_data = {
                "success": True,
                "analytics": {
                    "subscriptions_by_status": subscriptions_by_status,
                    "monthly_revenue": monthly_revenue,
                    "total_revenue": sum(monthly_revenue.values())
                },
                "timestamp": datetime.now(timezone.utc).isoformat()
            }

            self.send_json_response(analytics_data)

        except Exception as e:
            self.send_error_response(500, f"Failed to fetch analytics: {str(e)}")

    def handle_payments_post(self, data):
        """Handle POST /payments - Process payment"""
        # Verify authentication
        auth_header = self.headers.get('Authorization', '')
        user_payload = self.verify_token(auth_header)

        if not user_payload:
            self.send_error_response(401, "Authentication required")
            return

        if not self.supabase:
            self.send_error_response(503, "Database not available")
            return

        required_fields = ['amount', 'gateway_transaction_id']
        for field in required_fields:
            if not data.get(field):
                self.send_error_response(400, f"{field} is required")
                return

        try:
            # Create payment record
            payment_data = {
                'payment_id': str(uuid.uuid4()),
                'user_id': user_payload['user_id'],
                'subscription_id': data.get('subscription_id'),
                'amount': data['amount'],
                'currency': data.get('currency', 'INR'),
                'payment_gateway': data.get('payment_gateway', 'razorpay'),
                'gateway_transaction_id': data['gateway_transaction_id'],
                'status': data.get('status', 'successful'),
                'payment_date': datetime.now(timezone.utc).isoformat(),
                'created_at': datetime.now(timezone.utc).isoformat()
            }

            result = self.supabase.table('payments').insert(payment_data).execute()

            if result.data:
                response_data = {
                    "success": True,
                    "payment": result.data[0],
                    "message": "Payment recorded successfully"
                }
                self.send_json_response(response_data, 201)
            else:
                self.send_error_response(500, "Failed to record payment")

        except Exception as e:
            self.send_error_response(500, f"Failed to process payment: {str(e)}")

    def handle_products_post(self, data):
        """Handle POST /products - Create new product (Admin only)"""
        # Verify admin authentication
        auth_header = self.headers.get('Authorization', '')
        user_payload = self.verify_token(auth_header)

        if not user_payload or user_payload.get('role') != 'admin':
            self.send_error_response(403, "Admin access required")
            return

        if not self.supabase:
            self.send_error_response(503, "Database not available")
            return

        required_fields = ['name', 'price']
        for field in required_fields:
            if not data.get(field):
                self.send_error_response(400, f"{field} is required")
                return

        try:
            # Create product
            product_data = {
                'product_id': str(uuid.uuid4()),
                'name': data['name'],
                'description': data.get('description'),
                'price': data['price'],
                'currency': data.get('currency', 'INR'),
                'is_subscription_product': data.get('is_subscription_product', True),
                'image_url': data.get('image_url'),
                'created_at': datetime.now(timezone.utc).isoformat(),
                'updated_at': datetime.now(timezone.utc).isoformat()
            }

            result = self.supabase.table('products').insert(product_data).execute()

            if result.data:
                response_data = {
                    "success": True,
                    "product": result.data[0],
                    "message": "Product created successfully"
                }
                self.send_json_response(response_data, 201)
            else:
                self.send_error_response(500, "Failed to create product")

        except Exception as e:
            self.send_error_response(500, f"Failed to create product: {str(e)}")

    def handle_users_post(self, data):
        """Handle POST /users - This is handled by register endpoint"""
        self.send_error_response(400, "Use /auth/register endpoint for user creation")

    def handle_users_put(self, user_id, data):
        """Handle PUT /users/{id} - Update user profile"""
        # Verify authentication
        auth_header = self.headers.get('Authorization', '')
        user_payload = self.verify_token(auth_header)

        if not user_payload:
            self.send_error_response(401, "Authentication required")
            return

        # Users can only update their own profile unless admin
        if user_payload.get('role') != 'admin' and user_payload['user_id'] != user_id:
            self.send_error_response(403, "Access denied")
            return

        if not self.supabase:
            self.send_error_response(503, "Database not available")
            return

        try:
            # Update user profile
            update_data = {
                'updated_at': datetime.now(timezone.utc).isoformat()
            }

            # Only allow certain fields to be updated
            allowed_fields = ['first_name', 'last_name', 'phone_number', 'address_line1', 'address_line2', 'city', 'state', 'postal_code', 'country']
            for field in allowed_fields:
                if field in data:
                    update_data[field] = data[field]

            result = self.supabase.table('users').update(update_data).eq('user_id', user_id).execute()

            if result.data:
                # Remove password hash from response
                user_data = {k: v for k, v in result.data[0].items() if k != 'password_hash'}

                response_data = {
                    "success": True,
                    "user": user_data,
                    "message": "Profile updated successfully"
                }
                self.send_json_response(response_data)
            else:
                self.send_error_response(404, "User not found")

        except Exception as e:
            self.send_error_response(500, f"Failed to update user: {str(e)}")