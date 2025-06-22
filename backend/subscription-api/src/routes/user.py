from flask import Blueprint, jsonify, request
from werkzeug.security import generate_password_hash, check_password_hash
from ..models.user import User, db
import uuid

user_bp = Blueprint('user', __name__)

@user_bp.route('/users', methods=['GET'])
def get_users():
    """Get all users with optional filtering"""
    role = request.args.get('role')
    
    query = User.query
    if role:
        query = query.filter(User.user_role == role)
    
    users = query.all()
    return jsonify([user.to_dict() for user in users])

@user_bp.route('/users', methods=['POST'])
def create_user():
    """Create a new user"""
    data = request.json
    
    if not data or 'email' not in data or 'password' not in data:
        return jsonify({'error': 'Email and password are required'}), 400
    
    # Check if user already exists
    existing_user = User.query.filter_by(email=data['email']).first()
    if existing_user:
        return jsonify({'error': 'User with this email already exists'}), 409
    
    # Hash the password
    password_hash = generate_password_hash(data['password'])
    
    user = User(
        email=data['email'],
        password_hash=password_hash,
        first_name=data.get('first_name'),
        last_name=data.get('last_name'),
        phone_number=data.get('phone_number'),
        address_line1=data.get('address_line1'),
        address_line2=data.get('address_line2'),
        city=data.get('city'),
        state=data.get('state'),
        postal_code=data.get('postal_code'),
        country=data.get('country', 'India'),
        user_role=data.get('user_role', 'customer')
    )
    
    try:
        db.session.add(user)
        db.session.commit()
        return jsonify(user.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to create user'}), 500

@user_bp.route('/users/<user_id>', methods=['GET'])
def get_user(user_id):
    """Get a specific user by ID"""
    try:
        user_uuid = uuid.UUID(user_id)
        user = User.query.filter_by(user_id=user_uuid).first_or_404()
        return jsonify(user.to_dict())
    except ValueError:
        return jsonify({'error': 'Invalid user ID format'}), 400

@user_bp.route('/users/<user_id>', methods=['PUT'])
def update_user(user_id):
    """Update an existing user"""
    try:
        user_uuid = uuid.UUID(user_id)
        user = User.query.filter_by(user_id=user_uuid).first_or_404()
        
        data = request.json
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Update fields if provided
        if 'first_name' in data:
            user.first_name = data['first_name']
        if 'last_name' in data:
            user.last_name = data['last_name']
        if 'phone_number' in data:
            user.phone_number = data['phone_number']
        if 'address_line1' in data:
            user.address_line1 = data['address_line1']
        if 'address_line2' in data:
            user.address_line2 = data['address_line2']
        if 'city' in data:
            user.city = data['city']
        if 'state' in data:
            user.state = data['state']
        if 'postal_code' in data:
            user.postal_code = data['postal_code']
        if 'country' in data:
            user.country = data['country']
        
        # Handle password update separately
        if 'password' in data:
            user.password_hash = generate_password_hash(data['password'])
        
        db.session.commit()
        return jsonify(user.to_dict())
    except ValueError:
        return jsonify({'error': 'Invalid user ID format'}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to update user'}), 500

@user_bp.route('/users/<user_id>', methods=['DELETE'])
def delete_user(user_id):
    """Delete a user"""
    try:
        user_uuid = uuid.UUID(user_id)
        user = User.query.filter_by(user_id=user_uuid).first_or_404()
        
        db.session.delete(user)
        db.session.commit()
        return '', 204
    except ValueError:
        return jsonify({'error': 'Invalid user ID format'}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to delete user'}), 500

@user_bp.route('/auth/login', methods=['POST'])
def login():
    """User login"""
    data = request.json
    
    if not data or 'email' not in data or 'password' not in data:
        return jsonify({'error': 'Email and password are required'}), 400
    
    user = User.query.filter_by(email=data['email']).first()
    
    if not user or not check_password_hash(user.password_hash, data['password']):
        return jsonify({'error': 'Invalid email or password'}), 401
    
    # In a real implementation, you would generate and return a JWT token here
    return jsonify({
        'message': 'Login successful',
        'user': user.to_dict(),
        'token': f'mock_token_{user.user_id}'  # Mock token for demonstration
    })

@user_bp.route('/auth/register', methods=['POST'])
def register():
    """User registration"""
    data = request.json
    
    if not data or 'email' not in data or 'password' not in data:
        return jsonify({'error': 'Email and password are required'}), 400
    
    # Check if user already exists
    existing_user = User.query.filter_by(email=data['email']).first()
    if existing_user:
        return jsonify({'error': 'User with this email already exists'}), 409
    
    # Hash the password
    password_hash = generate_password_hash(data['password'])
    
    user = User(
        email=data['email'],
        password_hash=password_hash,
        first_name=data.get('first_name'),
        last_name=data.get('last_name'),
        phone_number=data.get('phone_number'),
        address_line1=data.get('address_line1'),
        address_line2=data.get('address_line2'),
        city=data.get('city'),
        state=data.get('state'),
        postal_code=data.get('postal_code'),
        country=data.get('country', 'India'),
        user_role='customer'  # Default role for registration
    )
    
    try:
        db.session.add(user)
        db.session.commit()
        
        return jsonify({
            'message': 'Registration successful',
            'user': user.to_dict(),
            'token': f'mock_token_{user.user_id}'  # Mock token for demonstration
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to register user'}), 500
