from flask import Flask, jsonify, request
from flask_cors import CORS
import os
import logging
from datetime import datetime, timedelta
import uuid
from functools import wraps
import time

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Simple rate limiting storage (in production, use Redis)
rate_limit_storage = {}

def rate_limit(max_requests=60, window=60):
    """Simple rate limiting decorator"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not os.environ.get('RATE_LIMIT_ENABLED', 'false').lower() == 'true':
                return f(*args, **kwargs)

            # Get client IP (consider proxy headers in production)
            client_ip = request.environ.get('HTTP_X_FORWARDED_FOR', request.environ.get('REMOTE_ADDR', 'unknown'))
            current_time = time.time()

            # Clean old entries
            rate_limit_storage[client_ip] = [
                timestamp for timestamp in rate_limit_storage.get(client_ip, [])
                if current_time - timestamp < window
            ]

            # Check rate limit
            if len(rate_limit_storage.get(client_ip, [])) >= max_requests:
                logger.warning(f"Rate limit exceeded for IP: {client_ip}")
                return jsonify({"error": "Rate limit exceeded", "retry_after": window}), 429

            # Add current request
            rate_limit_storage.setdefault(client_ip, []).append(current_time)

            return f(*args, **kwargs)
        return decorated_function
    return decorator

# Production-ready CORS configuration
cors_origins = os.environ.get('CORS_ORIGINS', 'https://localhost:3000').split(',')
# Never allow wildcard (*) in production
if '*' in cors_origins and os.environ.get('VERCEL_ENV') == 'production':
    cors_origins = ['https://subscriptionpro.vercel.app']  # Default production domain
    logger.warning("Wildcard CORS detected in production, using default domain")

CORS(app,
     origins=cors_origins,
     methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
     allow_headers=['Content-Type', 'Authorization'],
     supports_credentials=True)

# Enhanced security headers
@app.after_request
def after_request(response):
    # Prevent MIME type sniffing
    response.headers['X-Content-Type-Options'] = 'nosniff'

    # Prevent clickjacking
    response.headers['X-Frame-Options'] = 'DENY'

    # XSS protection
    response.headers['X-XSS-Protection'] = '1; mode=block'

    # HTTPS enforcement (only in production)
    if os.environ.get('VERCEL_ENV') == 'production':
        response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains; preload'

    # Content Security Policy
    response.headers['Content-Security-Policy'] = "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'"

    # Referrer policy
    response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'

    # Permissions policy
    response.headers['Permissions-Policy'] = 'geolocation=(), microphone=(), camera=()'

    return response

# Supabase integration
try:
    from supabase import create_client, Client
    SUPABASE_URL = os.environ.get('SUPABASE_URL')
    SUPABASE_KEY = os.environ.get('SUPABASE_KEY')

    if SUPABASE_URL and SUPABASE_KEY:
        supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
        logger.info("Supabase client initialized successfully")
    else:
        supabase = None
        logger.warning("Supabase credentials not found, using mock data")
except ImportError:
    supabase = None
    logger.warning("Supabase library not installed, using mock data")

# Health check endpoint
@app.route('/')
@app.route('/health')
def health():
    supabase_url = os.environ.get('SUPABASE_URL', 'NOT_SET')
    return jsonify({
        "status": "healthy",
        "message": "SubscriptionPro API v1.0",
        "environment": os.environ.get('VERCEL_ENV', 'development'),
        "database_configured": "YES" if supabase_url != 'NOT_SET' else "NO"
    })

# API Info endpoint
@app.route('/api/info')
def api_info():
    return jsonify({
        "name": "SubscriptionPro API",
        "version": "1.0.0",
        "description": "Enterprise Subscription Management Platform",
        "endpoints": [
            "/health - Health check",
            "/api/users - User management",
            "/api/products - Product catalog",
            "/api/subscriptions - Subscription management",
            "/api/admin/dashboard - Admin dashboard"
        ]
    })

# API endpoints with Supabase integration
@app.route('/api/users')
@rate_limit(max_requests=30, window=60)  # 30 requests per minute
def users():
    if supabase:
        try:
            response = supabase.table('users').select('*').execute()
            return jsonify({
                "users": response.data,
                "total": len(response.data),
                "message": "Data from Supabase"
            })
        except Exception as e:
            logger.error(f"Supabase error: {e}")
            return jsonify({"error": "Database connection failed"}), 500
    else:
        return jsonify({
            "users": [],
            "total": 0,
            "message": "Database not configured - Please set up Supabase",
            "setup_required": True
        })

@app.route('/api/products')
@rate_limit(max_requests=60, window=60)  # 60 requests per minute for products
def products():
    if supabase:
        try:
            response = supabase.table('products').select('*').execute()
            return jsonify({
                "products": response.data,
                "total": len(response.data),
                "message": "Data from Supabase"
            })
        except Exception as e:
            logger.error(f"Supabase error: {e}")
            return jsonify({"error": "Database connection failed"}), 500
    else:
        return jsonify({
            "products": [],
            "total": 0,
            "message": "Database not configured - Please set up Supabase",
            "setup_required": True
        })

@app.route('/api/subscriptions')
@rate_limit(max_requests=30, window=60)  # 30 requests per minute for subscriptions
def subscriptions():
    if supabase:
        try:
            response = supabase.table('subscriptions').select('*').execute()
            return jsonify({
                "subscriptions": response.data,
                "total": len(response.data),
                "message": "Data from Supabase"
            })
        except Exception as e:
            logger.error(f"Supabase error: {e}")
            return jsonify({"error": "Database connection failed"}), 500
    else:
        return jsonify({
            "subscriptions": [],
            "total": 0,
            "message": "Database not configured - Please set up Supabase",
            "setup_required": True
        })

@app.route('/api/admin/dashboard')
@rate_limit(max_requests=20, window=60)  # 20 requests per minute for admin dashboard
def admin_dashboard():
    if supabase:
        try:
            users_response = supabase.table('users').select('user_id').execute()
            products_response = supabase.table('products').select('product_id').execute()
            subscriptions_response = supabase.table('subscriptions').select('subscription_id, status').execute()

            active_subscriptions = len([s for s in subscriptions_response.data if s.get('status') == 'active'])

            return jsonify({
                "metrics": {
                    "total_users": len(users_response.data),
                    "total_products": len(products_response.data),
                    "active_subscriptions": active_subscriptions,
                    "monthly_revenue": active_subscriptions * 1500,  # Estimated
                    "currency": "INR"
                },
                "message": "Data from Supabase"
            })
        except Exception as e:
            logger.error(f"Supabase error: {e}")
            return jsonify({"error": "Database connection failed"}), 500
    else:
        return jsonify({
            "metrics": {
                "total_users": 2,
                "total_products": 3,
                "active_subscriptions": 2,
                "monthly_revenue": 2998,
                "currency": "INR"
            },
            "recent_activity": [
                {"type": "subscription_created", "user": "user@subscriptionpro.com", "timestamp": "2025-06-22T10:00:00Z"},
                {"type": "payment_successful", "amount": 1999, "timestamp": "2025-06-22T09:30:00Z"}
            ],
            "message": "Mock data - Supabase not configured"
        })

# Error handlers
@app.errorhandler(404)
def not_found(_error):
    return jsonify({"error": "Endpoint not found", "status": 404}), 404

@app.errorhandler(429)
def rate_limit_exceeded(_error):
    return jsonify({
        "error": "Rate limit exceeded",
        "message": "Too many requests. Please try again later.",
        "status": 429
    }), 429

@app.errorhandler(500)
def internal_error(error):
    logger.error(f"Internal error: {error}")
    return jsonify({"error": "Internal server error", "status": 500}), 500

# Vercel serverless function handler
def handler(request):
    return app(request.environ, lambda _status, _headers: None)

if __name__ == '__main__':
    app.run(debug=False, host="0.0.0.0", port=5000)