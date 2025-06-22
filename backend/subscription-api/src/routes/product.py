from flask import Blueprint, jsonify, request
from ..models.user import Product, SubscriptionPlan, db
import uuid

product_bp = Blueprint('product', __name__)

@product_bp.route('/products', methods=['GET'])
def get_products():
    """Get all products with optional filtering"""
    is_subscription = request.args.get('subscription')
    
    query = Product.query
    if is_subscription:
        query = query.filter(Product.is_subscription_product == (is_subscription.lower() == 'true'))
    
    products = query.all()
    return jsonify([product.to_dict() for product in products])

@product_bp.route('/products', methods=['POST'])
def create_product():
    """Create a new product"""
    data = request.json
    
    if not data or 'name' not in data or 'price' not in data:
        return jsonify({'error': 'Name and price are required'}), 400
    
    product = Product(
        name=data['name'],
        description=data.get('description'),
        price=data['price'],
        currency=data.get('currency', 'INR'),
        is_subscription_product=data.get('is_subscription_product', False),
        salesforce_product_id=data.get('salesforce_product_id'),
        image_url=data.get('image_url')
    )
    
    try:
        db.session.add(product)
        db.session.commit()
        return jsonify(product.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to create product'}), 500

@product_bp.route('/products/<product_id>', methods=['GET'])
def get_product(product_id):
    """Get a specific product by ID"""
    try:
        product_uuid = uuid.UUID(product_id)
        product = Product.query.filter_by(product_id=product_uuid).first_or_404()
        return jsonify(product.to_dict())
    except ValueError:
        return jsonify({'error': 'Invalid product ID format'}), 400

@product_bp.route('/products/<product_id>/plans', methods=['GET'])
def get_product_plans(product_id):
    """Get subscription plans for a product"""
    try:
        product_uuid = uuid.UUID(product_id)
        plans = SubscriptionPlan.query.filter_by(product_id=product_uuid, is_active=True).all()
        return jsonify([plan.to_dict() for plan in plans])
    except ValueError:
        return jsonify({'error': 'Invalid product ID format'}), 400