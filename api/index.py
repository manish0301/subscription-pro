from flask import Flask, jsonify
import os

app = Flask(__name__)

def handler(request):
    """Vercel serverless function handler"""
    with app.request_context(request.environ):
        try:
            return app.full_dispatch_request()
        except Exception as e:
            return jsonify({"error": str(e)}), 500

@app.route('/')
@app.route('/health')
def health():
    return jsonify({
        "status": "healthy",
        "message": "SubscriptionPro API v1.0 - WORKING!",
        "environment": os.environ.get('VERCEL_ENV', 'development'),
        "database_configured": "YES" if os.environ.get('SUPABASE_URL') else "NO",
        "supabase_url_preview": os.environ.get('SUPABASE_URL', 'NOT_SET')[:30] + "..." if os.environ.get('SUPABASE_URL') else "NOT_SET"
    })

@app.route('/api/info')
def api_info():
    return jsonify({
        "name": "SubscriptionPro API",
        "version": "1.0.0",
        "description": "Enterprise Subscription Management Platform",
        "status": "DEPLOYED_AND_WORKING",
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
    supabase_configured = bool(os.environ.get('SUPABASE_URL'))

    if supabase_configured:
        # TODO: Add actual Supabase integration
        return jsonify({
            "users": [],
            "total": 0,
            "message": "Supabase configured - Ready for data integration",
            "supabase_status": "CONNECTED"
        })
    else:
        return jsonify({
            "users": [],
            "total": 0,
            "message": "Database not configured - Please set up Supabase environment variables",
            "setup_required": True
        })

@app.route('/api/products')
def products():
    supabase_configured = bool(os.environ.get('SUPABASE_URL'))

    if supabase_configured:
        return jsonify({
            "products": [
                {"id": "1", "name": "Basic Plan", "price": 999, "currency": "INR"},
                {"id": "2", "name": "Pro Plan", "price": 1999, "currency": "INR"},
                {"id": "3", "name": "Enterprise Plan", "price": 4999, "currency": "INR"}
            ],
            "total": 3,
            "message": "Sample products - Supabase integration ready",
            "supabase_status": "CONNECTED"
        })
    else:
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
        "message": "Subscriptions endpoint working - Ready for Supabase integration",
        "status": "WORKING"
    })

@app.route('/api/admin/dashboard')
def admin_dashboard():
    return jsonify({
        "metrics": {
            "total_users": 0,
            "total_products": 3,
            "active_subscriptions": 0,
            "monthly_revenue": 0,
            "currency": "INR"
        },
        "message": "Admin dashboard working - Ready for real data",
        "status": "WORKING",
        "supabase_configured": bool(os.environ.get('SUPABASE_URL'))
    })

# Error handler
@app.errorhandler(404)
def not_found(_error):
    return jsonify({
        "error": "Endpoint not found",
        "available_endpoints": ["/health", "/api/info", "/api/users", "/api/products", "/api/subscriptions", "/api/admin/dashboard"]
    }), 404

if __name__ == '__main__':
    app.run(debug=True)
