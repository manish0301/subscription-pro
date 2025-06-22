from flask import Blueprint, jsonify, request
from ..models.user import Payment, db
import uuid
import razorpay
import os

payment_bp = Blueprint('payment', __name__)

# Initialize Razorpay client
razorpay_client = razorpay.Client(auth=(
    os.environ.get('RAZORPAY_KEY_ID', ''),
    os.environ.get('RAZORPAY_KEY_SECRET', '')
))

@payment_bp.route('/payments', methods=['GET'])
def get_payments():
    """Get all payments with optional filtering"""
    user_id = request.args.get('user_id')
    status = request.args.get('status')
    
    query = Payment.query
    if user_id:
        try:
            user_uuid = uuid.UUID(user_id)
            query = query.filter(Payment.user_id == user_uuid)
        except ValueError:
            return jsonify({'error': 'Invalid user ID format'}), 400
    
    if status:
        query = query.filter(Payment.status == status)
    
    payments = query.all()
    return jsonify([payment.to_dict() for payment in payments])

@payment_bp.route('/payments/create-order', methods=['POST'])
def create_razorpay_order():
    """Create a Razorpay order"""
    data = request.json
    
    if not data or 'amount' not in data:
        return jsonify({'error': 'Amount is required'}), 400
    
    try:
        order_data = {
            'amount': int(data['amount'] * 100),  # Convert to paise
            'currency': data.get('currency', 'INR'),
            'receipt': data.get('receipt', f'order_{uuid.uuid4().hex[:8]}'),
            'notes': data.get('notes', {})
        }
        
        order = razorpay_client.order.create(data=order_data)
        return jsonify(order)
    except Exception as e:
        return jsonify({'error': f'Failed to create order: {str(e)}'}), 500

@payment_bp.route('/payments/verify', methods=['POST'])
def verify_payment():
    """Verify Razorpay payment"""
    data = request.json
    
    required_fields = ['razorpay_order_id', 'razorpay_payment_id', 'razorpay_signature']
    if not data or not all(field in data for field in required_fields):
        return jsonify({'error': 'Missing required payment verification fields'}), 400
    
    try:
        # Verify payment signature
        razorpay_client.utility.verify_payment_signature({
            'razorpay_order_id': data['razorpay_order_id'],
            'razorpay_payment_id': data['razorpay_payment_id'],
            'razorpay_signature': data['razorpay_signature']
        })
        
        # Create payment record
        payment = Payment(
            user_id=uuid.UUID(data['user_id']),
            amount=data['amount'],
            currency=data.get('currency', 'INR'),
            payment_gateway='razorpay',
            gateway_transaction_id=data['razorpay_payment_id'],
            status='successful'
        )
        
        if 'subscription_id' in data:
            payment.subscription_id = uuid.UUID(data['subscription_id'])
        
        db.session.add(payment)
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'payment': payment.to_dict()
        })
    except razorpay.errors.SignatureVerificationError:
        return jsonify({'error': 'Invalid payment signature'}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Payment verification failed: {str(e)}'}), 500

@payment_bp.route('/payments/webhook', methods=['POST'])
def razorpay_webhook():
    """Handle Razorpay webhooks"""
    data = request.json
    
    # In production, verify webhook signature
    # webhook_signature = request.headers.get('X-Razorpay-Signature')
    
    try:
        event = data.get('event')
        payload = data.get('payload', {}).get('payment', {}).get('entity', {})
        
        if event == 'payment.captured':
            # Handle successful payment
            payment_id = payload.get('id')
            # Update payment status in database
            # Add your business logic here
            
        elif event == 'payment.failed':
            # Handle failed payment
            payment_id = payload.get('id')
            # Update payment status and handle failure
            # Add your business logic here
            
        return jsonify({'status': 'ok'})
    except Exception as e:
        return jsonify({'error': f'Webhook processing failed: {str(e)}'}), 500