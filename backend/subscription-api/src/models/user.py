from flask_sqlalchemy import SQLAlchemy
import uuid
from datetime import datetime
from sqlalchemy.dialects.postgresql import UUID, ENUM

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    
    user_id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    first_name = db.Column(db.String(100))
    last_name = db.Column(db.String(100))
    phone_number = db.Column(db.String(20))
    address_line1 = db.Column(db.String(255))
    address_line2 = db.Column(db.String(255))
    city = db.Column(db.String(100))
    state = db.Column(db.String(100))
    postal_code = db.Column(db.String(20))
    country = db.Column(db.String(100), nullable=False)
    user_role = db.Column(ENUM('customer', 'admin', name='user_role_enum'), nullable=False, default='customer')
    created_at = db.Column(db.DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime(timezone=True), nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    subscriptions = db.relationship('Subscription', backref='user', lazy=True)
    payments = db.relationship('Payment', backref='user', lazy=True)
    audit_logs = db.relationship('AuditLog', backref='user', lazy=True)

    def __repr__(self):
        return f'<User {self.email}>'

    def to_dict(self):
        return {
            'user_id': str(self.user_id),
            'email': self.email,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'phone_number': self.phone_number,
            'address_line1': self.address_line1,
            'address_line2': self.address_line2,
            'city': self.city,
            'state': self.state,
            'postal_code': self.postal_code,
            'country': self.country,
            'user_role': self.user_role,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class Product(db.Model):
    __tablename__ = 'products'
    
    product_id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    price = db.Column(db.Numeric(10, 2), nullable=False)
    currency = db.Column(db.String(3), nullable=False, default='INR')
    is_subscription_product = db.Column(db.Boolean, nullable=False, default=False)
    salesforce_product_id = db.Column(db.String(255), unique=True)
    image_url = db.Column(db.String(255))
    created_at = db.Column(db.DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime(timezone=True), nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    subscription_plans = db.relationship('SubscriptionPlan', backref='product', lazy=True)
    subscriptions = db.relationship('Subscription', backref='product', lazy=True)

    def __repr__(self):
        return f'<Product {self.name}>'

    def to_dict(self):
        return {
            'product_id': str(self.product_id),
            'name': self.name,
            'description': self.description,
            'price': float(self.price),
            'currency': self.currency,
            'is_subscription_product': self.is_subscription_product,
            'salesforce_product_id': self.salesforce_product_id,
            'image_url': self.image_url,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class SubscriptionPlan(db.Model):
    __tablename__ = 'subscription_plans'
    
    plan_id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    product_id = db.Column(UUID(as_uuid=True), db.ForeignKey('products.product_id'), nullable=False)
    plan_name = db.Column(db.String(100), nullable=False)
    frequency_type = db.Column(ENUM('daily', 'weekly', 'monthly', 'custom', name='frequency_type_enum'), nullable=False)
    frequency_value = db.Column(db.Integer)
    duration_type = db.Column(ENUM('months', 'weeks', 'days', 'indefinite', name='duration_type_enum'))
    duration_value = db.Column(db.Integer)
    custom_schedule_days = db.Column(db.JSON)
    price_multiplier = db.Column(db.Numeric(5, 2), nullable=False, default=1.0)
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    created_at = db.Column(db.DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime(timezone=True), nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    subscriptions = db.relationship('Subscription', backref='plan', lazy=True)

    def __repr__(self):
        return f'<SubscriptionPlan {self.plan_name}>'

    def to_dict(self):
        return {
            'plan_id': str(self.plan_id),
            'product_id': str(self.product_id),
            'plan_name': self.plan_name,
            'frequency_type': self.frequency_type,
            'frequency_value': self.frequency_value,
            'duration_type': self.duration_type,
            'duration_value': self.duration_value,
            'custom_schedule_days': self.custom_schedule_days,
            'price_multiplier': float(self.price_multiplier),
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class Subscription(db.Model):
    __tablename__ = 'subscriptions'
    
    subscription_id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey('users.user_id'), nullable=False)
    product_id = db.Column(UUID(as_uuid=True), db.ForeignKey('products.product_id'), nullable=False)
    plan_id = db.Column(UUID(as_uuid=True), db.ForeignKey('subscription_plans.plan_id'), nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date)
    next_delivery_date = db.Column(db.Date, nullable=False)
    status = db.Column(ENUM('active', 'paused', 'canceled', 'completed', name='subscription_status_enum'), nullable=False, default='active')
    quantity = db.Column(db.Integer, nullable=False, default=1)
    payment_option = db.Column(ENUM('upfront', 'recurring', name='payment_option_enum'), nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime(timezone=True), nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    orders = db.relationship('Order', backref='subscription', lazy=True)
    payments = db.relationship('Payment', backref='subscription', lazy=True)

    def __repr__(self):
        return f'<Subscription {self.subscription_id}>'

    def to_dict(self):
        return {
            'subscription_id': str(self.subscription_id),
            'user_id': str(self.user_id),
            'product_id': str(self.product_id),
            'plan_id': str(self.plan_id),
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'next_delivery_date': self.next_delivery_date.isoformat() if self.next_delivery_date else None,
            'status': self.status,
            'quantity': self.quantity,
            'payment_option': self.payment_option,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class Order(db.Model):
    __tablename__ = 'orders'
    
    order_id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    subscription_id = db.Column(UUID(as_uuid=True), db.ForeignKey('subscriptions.subscription_id'), nullable=False)
    delivery_date = db.Column(db.Date, nullable=False)
    order_status = db.Column(ENUM('pending', 'shipped', 'delivered', 'canceled', name='order_status_enum'), nullable=False, default='pending')
    total_amount = db.Column(db.Numeric(10, 2), nullable=False)
    payment_status = db.Column(ENUM('pending', 'paid', 'failed', 'refunded', name='payment_status_enum'), nullable=False, default='pending')
    transaction_id = db.Column(db.String(255))
    created_at = db.Column(db.DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime(timezone=True), nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    payments = db.relationship('Payment', backref='order', lazy=True)

    def __repr__(self):
        return f'<Order {self.order_id}>'

    def to_dict(self):
        return {
            'order_id': str(self.order_id),
            'subscription_id': str(self.subscription_id),
            'delivery_date': self.delivery_date.isoformat() if self.delivery_date else None,
            'order_status': self.order_status,
            'total_amount': float(self.total_amount),
            'payment_status': self.payment_status,
            'transaction_id': self.transaction_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class Payment(db.Model):
    __tablename__ = 'payments'
    
    payment_id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey('users.user_id'), nullable=False)
    order_id = db.Column(UUID(as_uuid=True), db.ForeignKey('orders.order_id'))
    subscription_id = db.Column(UUID(as_uuid=True), db.ForeignKey('subscriptions.subscription_id'))
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    currency = db.Column(db.String(3), nullable=False)
    payment_gateway = db.Column(db.String(100))
    gateway_transaction_id = db.Column(db.String(255), nullable=False, unique=True)
    status = db.Column(ENUM('successful', 'failed', 'pending', name='payment_status_enum'), nullable=False)
    payment_date = db.Column(db.DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    created_at = db.Column(db.DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime(timezone=True), nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<Payment {self.payment_id}>'

    def to_dict(self):
        return {
            'payment_id': str(self.payment_id),
            'user_id': str(self.user_id),
            'order_id': str(self.order_id) if self.order_id else None,
            'subscription_id': str(self.subscription_id) if self.subscription_id else None,
            'amount': float(self.amount),
            'currency': self.currency,
            'payment_gateway': self.payment_gateway,
            'gateway_transaction_id': self.gateway_transaction_id,
            'status': self.status,
            'payment_date': self.payment_date.isoformat() if self.payment_date else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class AuditLog(db.Model):
    __tablename__ = 'audit_logs'
    
    log_id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey('users.user_id'))
    action_type = db.Column(db.String(100), nullable=False)
    entity_type = db.Column(db.String(100), nullable=False)
    entity_id = db.Column(UUID(as_uuid=True))
    old_value = db.Column(db.JSON)
    new_value = db.Column(db.JSON)
    ip_address = db.Column(db.String(45))
    timestamp = db.Column(db.DateTime(timezone=True), nullable=False, default=datetime.utcnow)

    def __repr__(self):
        return f'<AuditLog {self.log_id}>'

    def to_dict(self):
        return {
            'log_id': str(self.log_id),
            'user_id': str(self.user_id) if self.user_id else None,
            'action_type': self.action_type,
            'entity_type': self.entity_type,
            'entity_id': str(self.entity_id) if self.entity_id else None,
            'old_value': self.old_value,
            'new_value': self.new_value,
            'ip_address': self.ip_address,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None
        }
