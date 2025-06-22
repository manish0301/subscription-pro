import os
from flask import Flask
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from google.cloud.sql.connector import Connector
import sqlalchemy

# Initialize Flask App
app = Flask(__name__)

# Configuration for Google Cloud
if os.getenv('GAE_ENV', '').startswith('standard'):
    # Production on Google Cloud
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
else:
    # Local development
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///local.db')

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY', 'dev-secret-key')

# Initialize Extensions
db = SQLAlchemy(app)
jwt = JWTManager(app)

# CORS configuration for Firebase Hosting
CORS(app, origins=[
    'https://*.web.app',
    'https://*.firebaseapp.com',
    'http://localhost:3000',
    'http://localhost:5173',
    'http://localhost:5174'
])

# Import models first
from src.models.user import User, Product, SubscriptionPlan, Subscription, Order, Payment, AuditLog

# Import and Register Blueprints
from src.routes.user import user_bp
from src.routes.product import product_bp
from src.routes.subscription import subscription_bp
from src.routes.payment import payment_bp
from src.routes.admin import admin_bp
from src.routes.razorpay_integration import razorpay_bp

app.register_blueprint(user_bp, url_prefix='/api')
app.register_blueprint(product_bp, url_prefix='/api')
app.register_blueprint(subscription_bp, url_prefix='/api')
app.register_blueprint(payment_bp, url_prefix='/api')
app.register_blueprint(admin_bp, url_prefix='/api')
app.register_blueprint(razorpay_bp, url_prefix='/api')

# Health check endpoint
@app.route('/health')
@app.route('/api/health')
def health_check():
    return {
        'status': 'healthy',
        'service': 'SubscriptionPro API',
        'version': '1.0.0'
    }

# Database initialization
@app.before_first_request
def create_tables():
    try:
        db.create_all()
    except Exception as e:
        print(f"Database initialization error: {e}")

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(debug=False, host='0.0.0.0', port=port)