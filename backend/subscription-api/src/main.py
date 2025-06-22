import os
from flask import Flask
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager

# Initialize Flask App
app = Flask(__name__)

# Configuration
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["JWT_SECRET_KEY"] = os.environ.get("JWT_SECRET_KEY")

# Initialize Extensions
db = SQLAlchemy(app)
jwt = JWTManager(app)
CORS(app) # Enable CORS for all origins during development, restrict in production

# Import and Register Blueprints
from .routes.user import user_bp
from .routes.product import product_bp
from .routes.subscription import subscription_bp
from .routes.payment import payment_bp
from .routes.admin import admin_bp
from .routes.razorpay_integration import razorpay_bp

app.register_blueprint(user_bp, url_prefix="/api/users")
app.register_blueprint(product_bp, url_prefix="/api/products")
app.register_blueprint(subscription_bp, url_prefix="/api/subscriptions")
app.register_blueprint(payment_bp, url_prefix="/api/payments")
app.register_blueprint(admin_bp, url_prefix="/api/admin")
app.register_blueprint(razorpay_bp, url_prefix="/api/razorpay")

# Database Initialization (for Cloud Functions, this might be handled by a separate migration script)
with app.app_context():
    db.create_all()

# For Firebase Cloud Functions, the entry point is typically a function that takes a request
# and returns a response. We'll wrap our Flask app.

# This is the entry point for Firebase Cloud Functions
def subscription_api(request):
    with app.app_context():
        # Dispatch the request to the Flask app
        return app.wsgi_app(request.environ, lambda status, headers: (status, headers))

if __name__ == "__main__":
    # This block is for local development only
    app.run(debug=True, host="0.0.0.0", port=5000)


