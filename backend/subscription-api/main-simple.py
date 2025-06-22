import os
from flask import Flask, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Simple in-memory data for demo
users = [
    {"id": "1", "email": "admin@demo.com", "role": "admin"},
    {"id": "2", "email": "user@demo.com", "role": "customer"}
]

products = [
    {"id": "1", "name": "Monthly Coffee", "price": 299, "currency": "INR"},
    {"id": "2", "name": "Weekly Snacks", "price": 199, "currency": "INR"}
]

subscriptions = [
    {"id": "1", "user_id": "2", "product_id": "1", "status": "active"},
    {"id": "2", "user_id": "2", "product_id": "2", "status": "paused"}
]

@app.route('/health')
@app.route('/api/health')
def health():
    return {"status": "ok", "service": "SubscriptionPro Demo"}

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
        "active_subscriptions": len([s for s in subscriptions if s["status"] == "active"]),
        "total_revenue": 5000
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=True)