import os
import sys
from firebase_functions import https_fn
from firebase_admin import initialize_app
from flask import Flask
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager

# Initialize Firebase Admin SDK
initialize_app()

# Create Flask app for Firebase Functions
app = Flask(__name__)

# Configuration
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///temp.db")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["JWT_SECRET_KEY"] = os.environ.get("JWT_SECRET_KEY", "dev-secret-key")

# Initialize Extensions
db = SQLAlchemy(app)
jwt = JWTManager(app)
CORS(app, origins=os.environ.get("CORS_ORIGINS", "*").split(","))

# Add the parent directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import and Register Blueprints
try:
    from src.routes.user import user_bp
    from src.routes.product import product_bp
    from src.routes.subscription import subscription_bp
    from src.routes.payment import payment_bp
    from src.routes.admin import admin_bp
    from src.routes.razorpay_integration import razorpay_bp

    app.register_blueprint(user_bp, url_prefix="/api/users")
    app.register_blueprint(product_bp, url_prefix="/api/products")
    app.register_blueprint(subscription_bp, url_prefix="/api/subscriptions")
    app.register_blueprint(payment_bp, url_prefix="/api/payments")
    app.register_blueprint(admin_bp, url_prefix="/api/admin")
    app.register_blueprint(razorpay_bp, url_prefix="/api/razorpay")
except ImportError as e:
    print(f"Warning: Could not import routes: {e}")
    # Create a simple health check endpoint
    @app.route('/api/health')
    def health():
        return {'status': 'ok', 'message': 'SubscriptionPro API is running'}

# Database initialization for Firebase Functions
with app.app_context():
    try:
        db.create_all()
    except Exception as e:
        print(f"Database initialization error: {e}")

@https_fn.on_request(cors=True)
def api(req):
    """Firebase Function entry point for the Flask app"""
    with app.request_context(req.environ):
        return app.full_dispatch_request() 