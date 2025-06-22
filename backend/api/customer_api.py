from flask import Flask, request, jsonify
from backend.models.subscription import Subscription
from backend.services.billing_service import BillingService
from backend.core.database import db

app = Flask(__name__)
billing_service = BillingService()

@app.route('/api/customer/subscriptions', methods=['GET'])
def get_customer_subscriptions():
    user_id = request.args.get('user_id')
    if not user_id:
        return jsonify({'error': 'user_id required'}), 400
    
    subscriptions = Subscription.get_by_user(user_id)
    return jsonify([{
        'subscription_id': sub.subscription_id,
        'product_id': sub.product_id,
        'status': sub.status,
        'frequency': sub.frequency,
        'amount': sub.amount,
        'next_billing_date': sub.next_billing_date.isoformat()
    } for sub in subscriptions])

@app.route('/api/customer/subscription', methods=['POST'])
def create_subscription():
    data = request.json
    subscription = Subscription(
        user_id=data['user_id'],
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

@app.route('/api/customer/subscription/<subscription_id>', methods=['PUT'])
def update_subscription(subscription_id):
    data = request.json
    
    with db.get_cursor() as (cursor, conn):
        cursor.execute("SELECT * FROM subscriptions WHERE subscription_id=%s", (subscription_id,))
        sub_data = cursor.fetchone()
        
        if not sub_data:
            return jsonify({'error': 'Subscription not found'}), 404
        
        subscription = Subscription(**sub_data)
        
        if 'status' in data:
            subscription.status = data['status']
        if 'frequency' in data:
            subscription.frequency = data['frequency']
            subscription.next_billing_date = subscription._calculate_next_billing()
        
        subscription.save()
        
        return jsonify({
            'subscription_id': subscription.subscription_id,
            'status': subscription.status,
            'frequency': subscription.frequency,
            'next_billing_date': subscription.next_billing_date.isoformat()
        })

@app.route('/api/customer/subscription/<subscription_id>/pause', methods=['POST'])
def pause_subscription(subscription_id):
    with db.get_cursor() as (cursor, conn):
        cursor.execute("UPDATE subscriptions SET status='paused' WHERE subscription_id=%s", (subscription_id,))
        conn.commit()
    
    return jsonify({'status': 'paused'})

@app.route('/api/customer/subscription/<subscription_id>/cancel', methods=['POST'])
def cancel_subscription(subscription_id):
    with db.get_cursor() as (cursor, conn):
        cursor.execute("UPDATE subscriptions SET status='canceled' WHERE subscription_id=%s", (subscription_id,))
        conn.commit()
    
    return jsonify({'status': 'canceled'})