from flask import Flask, jsonify, request
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)

# Mock data for demo
users = [{"id": "1", "email": "admin@demo.com", "name": "Admin User"}]
products = [{"id": "1", "name": "Monthly Subscription", "price": 299}]
subscriptions = [{"id": "1", "user_id": "1", "product_id": "1", "status": "active"}]

@app.route('/api/health')
def health():
    return {"status": "ok", "message": "SubscriptionPro API"}

@app.route('/api/users')
def get_users():
    return jsonify(users)

@app.route('/api/products') 
def get_products():
    return jsonify(products)

@app.route('/api/subscriptions')
def get_subscriptions():
    return jsonify(subscriptions)

@app.route('/api/admin/dashboard')
def dashboard():
    return jsonify({
        "total_users": len(users),
        "total_products": len(products), 
        "active_subscriptions": 1,
        "total_revenue": 2990
    })

# Vercel serverless handler
def handler(request):
    return app(request.environ, lambda status, headers: None)