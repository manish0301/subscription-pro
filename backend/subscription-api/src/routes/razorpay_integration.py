from flask import Blueprint, jsonify, request
import razorpay
import os

razorpay_bp = Blueprint('razorpay', __name__)

# Initialize Razorpay client
razorpay_client = razorpay.Client(auth=(
    os.environ.get('RAZORPAY_KEY_ID', ''),
    os.environ.get('RAZORPAY_KEY_SECRET', '')
))

@razorpay_bp.route('/razorpay/plans', methods=['POST'])
def create_subscription_plan():
    """Create a Razorpay subscription plan"""
    data = request.json
    
    if not data or 'period' not in data or 'interval' not in data:
        return jsonify({'error': 'Period and interval are required'}), 400
    
    try:
        plan_data = {
            'period': data['period'],  # daily, weekly, monthly, yearly
            'interval': data['interval'],  # number
            'item': {
                'name': data.get('name', 'Subscription Plan'),
                'amount': int(data.get('amount', 0) * 100),  # Convert to paise
                'currency': data.get('currency', 'INR'),
                'description': data.get('description', '')
            },
            'notes': data.get('notes', {})
        }
        
        plan = razorpay_client.plan.create(data=plan_data)
        return jsonify(plan)
    except Exception as e:
        return jsonify({'error': f'Failed to create plan: {str(e)}'}), 500

@razorpay_bp.route('/razorpay/subscriptions', methods=['POST'])
def create_razorpay_subscription():
    """Create a Razorpay subscription"""
    data = request.json
    
    if not data or 'plan_id' not in data:
        return jsonify({'error': 'Plan ID is required'}), 400
    
    try:
        subscription_data = {
            'plan_id': data['plan_id'],
            'customer_notify': data.get('customer_notify', 1),
            'quantity': data.get('quantity', 1),
            'total_count': data.get('total_count', 0),  # 0 for infinite
            'start_at': data.get('start_at'),  # Unix timestamp
            'expire_by': data.get('expire_by'),  # Unix timestamp
            'addons': data.get('addons', []),
            'notes': data.get('notes', {})
        }
        
        subscription = razorpay_client.subscription.create(data=subscription_data)
        return jsonify(subscription)
    except Exception as e:
        return jsonify({'error': f'Failed to create subscription: {str(e)}'}), 500

@razorpay_bp.route('/razorpay/subscriptions/<subscription_id>/cancel', methods=['POST'])
def cancel_razorpay_subscription(subscription_id):
    """Cancel a Razorpay subscription"""
    data = request.json or {}
    
    try:
        cancel_data = {
            'cancel_at_cycle_end': data.get('cancel_at_cycle_end', 0)
        }
        
        subscription = razorpay_client.subscription.cancel(subscription_id, cancel_data)
        return jsonify(subscription)
    except Exception as e:
        return jsonify({'error': f'Failed to cancel subscription: {str(e)}'}), 500

@razorpay_bp.route('/razorpay/customers', methods=['POST'])
def create_razorpay_customer():
    """Create a Razorpay customer"""
    data = request.json
    
    if not data or 'name' not in data or 'email' not in data:
        return jsonify({'error': 'Name and email are required'}), 400
    
    try:
        customer_data = {
            'name': data['name'],
            'email': data['email'],
            'contact': data.get('contact', ''),
            'fail_existing': data.get('fail_existing', '0'),
            'notes': data.get('notes', {})
        }
        
        customer = razorpay_client.customer.create(data=customer_data)
        return jsonify(customer)
    except Exception as e:
        return jsonify({'error': f'Failed to create customer: {str(e)}'}), 500

@razorpay_bp.route('/razorpay/payment-links', methods=['POST'])
def create_payment_link():
    """Create a Razorpay payment link"""
    data = request.json
    
    if not data or 'amount' not in data:
        return jsonify({'error': 'Amount is required'}), 400
    
    try:
        link_data = {
            'amount': int(data['amount'] * 100),  # Convert to paise
            'currency': data.get('currency', 'INR'),
            'accept_partial': data.get('accept_partial', False),
            'first_min_partial_amount': data.get('first_min_partial_amount', 0),
            'description': data.get('description', 'Payment for subscription'),
            'customer': data.get('customer', {}),
            'notify': data.get('notify', {'sms': True, 'email': True}),
            'reminder_enable': data.get('reminder_enable', True),
            'notes': data.get('notes', {}),
            'callback_url': data.get('callback_url', ''),
            'callback_method': data.get('callback_method', 'get')
        }
        
        payment_link = razorpay_client.payment_link.create(data=link_data)
        return jsonify(payment_link)
    except Exception as e:
        return jsonify({'error': f'Failed to create payment link: {str(e)}'}), 500