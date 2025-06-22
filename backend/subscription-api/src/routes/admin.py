from flask import Blueprint, jsonify, request
from ..models.user import User, Product, Subscription, Payment, AuditLog, db
from sqlalchemy import func

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/admin/dashboard', methods=['GET'])
def get_dashboard_stats():
    """Get admin dashboard statistics"""
    try:
        stats = {
            'total_users': User.query.count(),
            'total_products': Product.query.count(),
            'active_subscriptions': Subscription.query.filter_by(status='active').count(),
            'total_revenue': db.session.query(func.sum(Payment.amount)).filter_by(status='successful').scalar() or 0,
            'recent_payments': [p.to_dict() for p in Payment.query.order_by(Payment.created_at.desc()).limit(5).all()],
            'recent_subscriptions': [s.to_dict() for s in Subscription.query.order_by(Subscription.created_at.desc()).limit(5).all()]
        }
        return jsonify(stats)
    except Exception as e:
        return jsonify({'error': f'Failed to fetch dashboard stats: {str(e)}'}), 500

@admin_bp.route('/admin/users', methods=['GET'])
def get_all_users():
    """Get all users for admin"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        
        users = User.query.paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return jsonify({
            'users': [user.to_dict() for user in users.items],
            'total': users.total,
            'pages': users.pages,
            'current_page': page
        })
    except Exception as e:
        return jsonify({'error': f'Failed to fetch users: {str(e)}'}), 500

@admin_bp.route('/admin/subscriptions', methods=['GET'])
def get_all_subscriptions():
    """Get all subscriptions for admin"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        status = request.args.get('status')
        
        query = Subscription.query
        if status:
            query = query.filter_by(status=status)
        
        subscriptions = query.paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return jsonify({
            'subscriptions': [sub.to_dict() for sub in subscriptions.items],
            'total': subscriptions.total,
            'pages': subscriptions.pages,
            'current_page': page
        })
    except Exception as e:
        return jsonify({'error': f'Failed to fetch subscriptions: {str(e)}'}), 500

@admin_bp.route('/admin/payments', methods=['GET'])
def get_all_payments():
    """Get all payments for admin"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        status = request.args.get('status')
        
        query = Payment.query
        if status:
            query = query.filter_by(status=status)
        
        payments = query.paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return jsonify({
            'payments': [payment.to_dict() for payment in payments.items],
            'total': payments.total,
            'pages': payments.pages,
            'current_page': page
        })
    except Exception as e:
        return jsonify({'error': f'Failed to fetch payments: {str(e)}'}), 500

@admin_bp.route('/admin/audit-logs', methods=['GET'])
def get_audit_logs():
    """Get audit logs for admin"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 50, type=int)
        
        logs = AuditLog.query.order_by(AuditLog.timestamp.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return jsonify({
            'logs': [log.to_dict() for log in logs.items],
            'total': logs.total,
            'pages': logs.pages,
            'current_page': page
        })
    except Exception as e:
        return jsonify({'error': f'Failed to fetch audit logs: {str(e)}'}), 500