from flask import Blueprint, jsonify, request
from ..models.user import Subscription, db
import uuid

subscription_bp = Blueprint('subscription', __name__)

@subscription_bp.route('/subscriptions', methods=['GET'])
def get_subscriptions():
    """Get all subscriptions with optional filtering"""
    user_id = request.args.get('user_id')
    status = request.args.get('status')
    
    query = Subscription.query
    if user_id:
        try:
            user_uuid = uuid.UUID(user_id)
            query = query.filter(Subscription.user_id == user_uuid)
        except ValueError:
            return jsonify({'error': 'Invalid user ID format'}), 400
    
    if status:
        query = query.filter(Subscription.status == status)
    
    subscriptions = query.all()
    return jsonify([sub.to_dict() for sub in subscriptions])

@subscription_bp.route('/subscriptions', methods=['POST'])
def create_subscription():
    """Create a new subscription"""
    data = request.json
    
    required_fields = ['user_id', 'product_id', 'plan_id', 'start_date', 'next_delivery_date']
    if not data or not all(field in data for field in required_fields):
        return jsonify({'error': 'Missing required fields'}), 400
    
    try:
        subscription = Subscription(
            user_id=uuid.UUID(data['user_id']),
            product_id=uuid.UUID(data['product_id']),
            plan_id=uuid.UUID(data['plan_id']),
            start_date=data['start_date'],
            end_date=data.get('end_date'),
            next_delivery_date=data['next_delivery_date'],
            quantity=data.get('quantity', 1),
            payment_option=data.get('payment_option', 'recurring')
        )
        
        db.session.add(subscription)
        db.session.commit()
        return jsonify(subscription.to_dict()), 201
    except ValueError:
        return jsonify({'error': 'Invalid UUID format'}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to create subscription'}), 500

@subscription_bp.route('/subscriptions/<subscription_id>/pause', methods=['POST'])
def pause_subscription(subscription_id):
    """Pause a subscription"""
    try:
        sub_uuid = uuid.UUID(subscription_id)
        subscription = Subscription.query.filter_by(subscription_id=sub_uuid).first_or_404()
        
        if subscription.status != 'active':
            return jsonify({'error': 'Can only pause active subscriptions'}), 400
        
        subscription.status = 'paused'
        db.session.commit()
        return jsonify(subscription.to_dict())
    except ValueError:
        return jsonify({'error': 'Invalid subscription ID format'}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to pause subscription'}), 500

@subscription_bp.route('/subscriptions/<subscription_id>/resume', methods=['POST'])
def resume_subscription(subscription_id):
    """Resume a paused subscription"""
    try:
        sub_uuid = uuid.UUID(subscription_id)
        subscription = Subscription.query.filter_by(subscription_id=sub_uuid).first_or_404()
        
        if subscription.status != 'paused':
            return jsonify({'error': 'Can only resume paused subscriptions'}), 400
        
        subscription.status = 'active'
        db.session.commit()
        return jsonify(subscription.to_dict())
    except ValueError:
        return jsonify({'error': 'Invalid subscription ID format'}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to resume subscription'}), 500

@subscription_bp.route('/subscriptions/<subscription_id>/cancel', methods=['POST'])
def cancel_subscription(subscription_id):
    """Cancel a subscription"""
    try:
        sub_uuid = uuid.UUID(subscription_id)
        subscription = Subscription.query.filter_by(subscription_id=sub_uuid).first_or_404()
        
        subscription.status = 'canceled'
        db.session.commit()
        return jsonify(subscription.to_dict())
    except ValueError:
        return jsonify({'error': 'Invalid subscription ID format'}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to cancel subscription'}), 500