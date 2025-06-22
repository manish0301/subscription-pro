from flask import Flask, jsonify, request
from flask_cors import CORS
import os
from supabase import create_client, Client

app = Flask(__name__)
CORS(app)

# Supabase configuration
SUPABASE_URL = os.environ.get('SUPABASE_URL', '')
SUPABASE_KEY = os.environ.get('SUPABASE_KEY', '')

if SUPABASE_URL and SUPABASE_KEY:
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
else:
    supabase = None

@app.route('/')
def index():
    return {"status": "ok", "message": "SubscriptionPro API with Supabase"}

@app.route('/health')
def health():
    db_status = "connected" if supabase else "mock_data"
    return {"status": "ok", "message": "SubscriptionPro API", "database": db_status}

@app.route('/users')
def users():
    if supabase:
        try:
            response = supabase.table('users').select('*').execute()
            return jsonify(response.data)
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    else:
        return jsonify([{"id": "1", "email": "admin@demo.com", "name": "Admin"}])

@app.route('/products')
def products():
    if supabase:
        try:
            response = supabase.table('products').select('*').execute()
            return jsonify(response.data)
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    else:
        return jsonify([{"id": "1", "name": "Monthly Plan", "price": 299}])

@app.route('/subscriptions')
def subscriptions():
    if supabase:
        try:
            response = supabase.table('subscriptions').select('*').execute()
            return jsonify(response.data)
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    else:
        return jsonify([{"id": "1", "status": "active", "product": "Monthly Plan"}])

@app.route('/admin/dashboard')
def dashboard():
    if supabase:
        try:
            users_count = len(supabase.table('users').select('user_id').execute().data)
            products_count = len(supabase.table('products').select('product_id').execute().data)
            subscriptions_count = len(supabase.table('subscriptions').select('subscription_id').execute().data)
            
            return jsonify({
                "total_users": users_count,
                "total_products": products_count,
                "active_subscriptions": subscriptions_count,
                "total_revenue": 5000
            })
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    else:
        return jsonify({
            "total_users": 2,
            "total_products": 3,
            "active_subscriptions": 1,
            "total_revenue": 2990
        })

if __name__ == '__main__':
    app.run()