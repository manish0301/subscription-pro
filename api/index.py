from flask import Flask, jsonify
import os

app = Flask(__name__)

@app.route('/')
@app.route('/health')
def health():
    return jsonify({
        "status": "healthy",
        "message": "SubscriptionPro API v1.0",
        "environment": os.environ.get('VERCEL_ENV', 'development'),
        "database_configured": "YES" if os.environ.get('SUPABASE_URL') else "NO"
    })

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

@app.route('/api/users')
def users():
    return jsonify({
        "users": [],
        "total": 0,
        "message": "Database not configured - Please set up Supabase",
        "setup_required": True
    })

@app.route('/api/products')
def products():
    return jsonify({
        "products": [],
        "total": 0,
        "message": "Database not configured - Please set up Supabase",
        "setup_required": True
    })

@app.route('/api/subscriptions')
def subscriptions():
    return jsonify({
        "subscriptions": [],
        "total": 0,
        "message": "Database not configured - Please set up Supabase",
        "setup_required": True
    })

@app.route('/api/admin/dashboard')
def admin_dashboard():
    return jsonify({
        "metrics": {
            "total_users": 0,
            "total_products": 0,
            "active_subscriptions": 0,
            "monthly_revenue": 0,
            "currency": "INR"
        },
        "message": "Database not configured - Please set up Supabase",
        "setup_required": True
    })

# Export the Flask app for Vercel
# This is the WSGI application that Vercel will use
application = app

if __name__ == '__main__':
    app.run(debug=False)
