from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
import os
from backend.core.auth import auth_service, require_auth
from backend.models.subscription import Subscription
from backend.services.billing_service import BillingService
from backend.core.database import db

app = Flask(__name__)
CORS(app)

billing_service = BillingService()

# Authentication endpoints
@app.route('/api/auth/login', methods=['POST'])
def login():
    data = request.json
    result = auth_service.authenticate_user(data['email'], data['password'])
    
    if result:
        return jsonify(result)
    else:
        return jsonify({'error': 'Invalid credentials'}), 401

@app.route('/api/auth/register', methods=['POST'])
def register():
    data = request.json
    result = auth_service.register_user(
        data['email'], 
        data['password'], 
        data['first_name'], 
        data['last_name'],
        data.get('role', 'customer')
    )
    
    if result:
        return jsonify(result)
    else:
        return jsonify({'error': 'Registration failed'}), 400

# Customer API endpoints
@app.route('/api/customer/subscriptions', methods=['GET'])
@require_auth(['customer'])
def get_customer_subscriptions():
    user_id = request.current_user['user_id']
    subscriptions = Subscription.get_by_user(user_id)
    
    return jsonify([{
        'subscription_id': sub.subscription_id,
        'product_id': sub.product_id,
        'status': sub.status,
        'frequency': sub.frequency,
        'amount': sub.amount,
        'next_billing_date': sub.next_billing_date.isoformat() if sub.next_billing_date else None
    } for sub in subscriptions])

@app.route('/api/customer/subscription', methods=['POST'])
@require_auth(['customer'])
def create_subscription():
    data = request.json
    subscription = Subscription(
        user_id=request.current_user['user_id'],
        product_id=data['product_id'],
        frequency=data['frequency'],
        amount=data['amount']
    )
    subscription.save()
    
    return jsonify({
        'subscription_id': subscription.subscription_id,
        'status': 'created',
        'next_billing_date': subscription.next_billing_date.isoformat()
    })

@app.route('/api/customer/subscription/<subscription_id>/pause', methods=['POST'])
@require_auth(['customer'])
def pause_subscription(subscription_id):
    with db.get_cursor() as (cursor, conn):
        cursor.execute("UPDATE subscriptions SET status='paused' WHERE subscription_id=%s AND user_id=%s", 
                      (subscription_id, request.current_user['user_id']))
        conn.commit()
    
    return jsonify({'status': 'paused'})

@app.route('/api/customer/subscription/<subscription_id>/cancel', methods=['POST'])
@require_auth(['customer'])
def cancel_subscription(subscription_id):
    with db.get_cursor() as (cursor, conn):
        cursor.execute("UPDATE subscriptions SET status='canceled' WHERE subscription_id=%s AND user_id=%s", 
                      (subscription_id, request.current_user['user_id']))
        conn.commit()
    
    return jsonify({'status': 'canceled'})

# Merchant API endpoints
@app.route('/api/merchant/dashboard', methods=['GET'])
@require_auth(['merchant', 'admin'])
def merchant_dashboard():
    with db.get_cursor() as (cursor, conn):
        cursor.execute("SELECT COUNT(*) as total FROM subscriptions WHERE status='active'")
        active_subs = cursor.fetchone()['total']
        
        cursor.execute("SELECT SUM(amount) as revenue FROM subscriptions WHERE status='active'")
        monthly_revenue = cursor.fetchone()['revenue'] or 0
        
        return jsonify({
            'active_subscriptions': active_subs,
            'monthly_revenue': float(monthly_revenue),
            'new_subscriptions_30d': 25,
            'churn_rate': 5.2
        })

@app.route('/api/merchant/products', methods=['GET'])
@require_auth(['merchant', 'admin'])
def get_products():
    with db.get_cursor() as (cursor, conn):
        cursor.execute("SELECT * FROM products WHERE is_active=true")
        products = cursor.fetchall()
        return jsonify([dict(product) for product in products])

@app.route('/api/merchant/products', methods=['POST'])
@require_auth(['merchant', 'admin'])
def create_product():
    data = request.json
    with db.get_cursor() as (cursor, conn):
        cursor.execute("""
            INSERT INTO products (name, description, price, currency, is_subscription_product)
            VALUES (%s, %s, %s, %s, %s) RETURNING product_id
        """, (data['name'], data['description'], data['price'], data.get('currency', 'INR'), True))
        
        product_id = cursor.fetchone()['product_id']
        conn.commit()
        
        return jsonify({'product_id': product_id, 'status': 'created'})

# Admin endpoints
@app.route('/api/admin/users', methods=['GET'])
@require_auth(['admin'])
def get_all_users():
    with db.get_cursor() as (cursor, conn):
        cursor.execute("SELECT user_id, email, first_name, last_name, user_role, created_at FROM users")
        users = cursor.fetchall()
        return jsonify([dict(user) for user in users])

@app.route('/api/admin/subscriptions', methods=['GET'])
@require_auth(['admin'])
def get_all_subscriptions():
    with db.get_cursor() as (cursor, conn):
        cursor.execute("""
            SELECT s.*, u.email as customer_email, p.name as product_name
            FROM subscriptions s
            JOIN users u ON s.user_id = u.user_id
            JOIN products p ON s.product_id = p.product_id
            ORDER BY s.created_at DESC
        """)
        subscriptions = cursor.fetchall()
        return jsonify([dict(sub) for sub in subscriptions])

# Health check
@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'healthy',
        'service': 'SubscriptionPro Enterprise',
        'version': '1.0.0'
    })

# Frontend routes
@app.route('/')
def customer_portal():
    with open('/Users/Manish/Work/firebase/subscription-platform/frontend/customer/index.html', 'r') as f:
        return f.read()

@app.route('/merchant')
def merchant_dashboard_page():
    with open('/Users/Manish/Work/firebase/subscription-platform/frontend/merchant/dashboard.html', 'r') as f:
        return f.read()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)