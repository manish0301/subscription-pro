import pytest
import json
from datetime import datetime, date
from unittest.mock import patch, MagicMock
from src.main import app, db
from src.models.user import User, Product, Subscription, Payment, AuditLog


@pytest.fixture
def client():
    """Create a test client for the Flask application."""
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['JWT_SECRET_KEY'] = 'test-secret-key'
    
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            yield client
            db.drop_all()


@pytest.fixture
def sample_user():
    """Create a sample user for testing."""
    return {
        'email': 'test@example.com',
        'password': 'password123',
        'first_name': 'Test',
        'last_name': 'User',
        'phone_number': '+91-9876543210',
        'date_of_birth': '1990-01-01',
        'address_line1': '123 Test Street',
        'city': 'Mumbai',
        'state': 'Maharashtra',
        'postal_code': '400001',
        'country': 'India'
    }


@pytest.fixture
def sample_product():
    """Create a sample product for testing."""
    return {
        'name': 'Test Product',
        'description': 'A test product for subscription',
        'price': 999.00,
        'currency': 'INR',
        'category': 'Test Category'
    }


@pytest.fixture
def sample_subscription():
    """Create a sample subscription for testing."""
    return {
        'frequency': 'monthly',
        'quantity': 1,
        'start_date': '2024-01-01'
    }


class TestAuthentication:
    """Test cases for authentication endpoints."""

    def test_user_registration_success(self, client, sample_user):
        """Test successful user registration."""
        response = client.post('/auth/register', 
                             data=json.dumps(sample_user),
                             content_type='application/json')
        
        assert response.status_code == 201
        data = json.loads(response.data)
        assert 'access_token' in data
        assert 'user' in data
        assert data['user']['email'] == sample_user['email']

    def test_user_registration_duplicate_email(self, client, sample_user):
        """Test registration with duplicate email."""
        # Register user first time
        client.post('/auth/register', 
                   data=json.dumps(sample_user),
                   content_type='application/json')
        
        # Try to register again with same email
        response = client.post('/auth/register', 
                             data=json.dumps(sample_user),
                             content_type='application/json')
        
        assert response.status_code == 409
        data = json.loads(response.data)
        assert 'error' in data

    def test_user_registration_invalid_data(self, client):
        """Test registration with invalid data."""
        invalid_user = {
            'email': 'invalid-email',
            'password': '123',  # Too short
            'first_name': '',   # Empty
        }
        
        response = client.post('/auth/register', 
                             data=json.dumps(invalid_user),
                             content_type='application/json')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data

    def test_user_login_success(self, client, sample_user):
        """Test successful user login."""
        # Register user first
        client.post('/auth/register', 
                   data=json.dumps(sample_user),
                   content_type='application/json')
        
        # Login
        login_data = {
            'email': sample_user['email'],
            'password': sample_user['password']
        }
        response = client.post('/auth/login', 
                             data=json.dumps(login_data),
                             content_type='application/json')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'access_token' in data
        assert 'user' in data

    def test_user_login_invalid_credentials(self, client, sample_user):
        """Test login with invalid credentials."""
        # Register user first
        client.post('/auth/register', 
                   data=json.dumps(sample_user),
                   content_type='application/json')
        
        # Login with wrong password
        login_data = {
            'email': sample_user['email'],
            'password': 'wrongpassword'
        }
        response = client.post('/auth/login', 
                             data=json.dumps(login_data),
                             content_type='application/json')
        
        assert response.status_code == 401
        data = json.loads(response.data)
        assert 'error' in data

    def test_user_login_nonexistent_user(self, client):
        """Test login with non-existent user."""
        login_data = {
            'email': 'nonexistent@example.com',
            'password': 'password123'
        }
        response = client.post('/auth/login', 
                             data=json.dumps(login_data),
                             content_type='application/json')
        
        assert response.status_code == 401
        data = json.loads(response.data)
        assert 'error' in data

    def test_protected_route_without_token(self, client):
        """Test accessing protected route without token."""
        response = client.get('/users/profile')
        assert response.status_code == 401

    def test_protected_route_with_invalid_token(self, client):
        """Test accessing protected route with invalid token."""
        headers = {'Authorization': 'Bearer invalid-token'}
        response = client.get('/users/profile', headers=headers)
        assert response.status_code == 401


class TestUserManagement:
    """Test cases for user management endpoints."""

    def get_auth_headers(self, client, sample_user):
        """Helper method to get authentication headers."""
        # Register and login user
        client.post('/auth/register', 
                   data=json.dumps(sample_user),
                   content_type='application/json')
        
        login_data = {
            'email': sample_user['email'],
            'password': sample_user['password']
        }
        response = client.post('/auth/login', 
                             data=json.dumps(login_data),
                             content_type='application/json')
        
        data = json.loads(response.data)
        return {'Authorization': f"Bearer {data['access_token']}"}

    def test_get_user_profile(self, client, sample_user):
        """Test getting user profile."""
        headers = self.get_auth_headers(client, sample_user)
        
        response = client.get('/users/profile', headers=headers)
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['email'] == sample_user['email']
        assert data['first_name'] == sample_user['first_name']

    def test_update_user_profile(self, client, sample_user):
        """Test updating user profile."""
        headers = self.get_auth_headers(client, sample_user)
        
        update_data = {
            'first_name': 'Updated',
            'last_name': 'Name',
            'phone_number': '+91-9876543211'
        }
        
        response = client.put('/users/profile', 
                            data=json.dumps(update_data),
                            content_type='application/json',
                            headers=headers)
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['first_name'] == 'Updated'
        assert data['last_name'] == 'Name'

    def test_change_password_success(self, client, sample_user):
        """Test successful password change."""
        headers = self.get_auth_headers(client, sample_user)
        
        password_data = {
            'current_password': sample_user['password'],
            'new_password': 'newpassword123'
        }
        
        response = client.post('/users/change-password', 
                             data=json.dumps(password_data),
                             content_type='application/json',
                             headers=headers)
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'message' in data

    def test_change_password_wrong_current(self, client, sample_user):
        """Test password change with wrong current password."""
        headers = self.get_auth_headers(client, sample_user)
        
        password_data = {
            'current_password': 'wrongpassword',
            'new_password': 'newpassword123'
        }
        
        response = client.post('/users/change-password', 
                             data=json.dumps(password_data),
                             content_type='application/json',
                             headers=headers)
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data


class TestProductManagement:
    """Test cases for product management endpoints."""

    def test_list_products(self, client):
        """Test listing products."""
        response = client.get('/products')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert 'products' in data
        assert 'total' in data
        assert 'page' in data
        assert 'limit' in data

    def test_list_products_with_filters(self, client):
        """Test listing products with filters."""
        response = client.get('/products?category=Food&search=coffee')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert 'products' in data

    def test_get_product_details(self, client):
        """Test getting product details."""
        # First, get a product ID from the list
        response = client.get('/products')
        data = json.loads(response.data)
        
        if data['products']:
            product_id = data['products'][0]['product_id']
            response = client.get(f'/products/{product_id}')
            assert response.status_code == 200
            
            product_data = json.loads(response.data)
            assert product_data['product_id'] == product_id

    def test_get_nonexistent_product(self, client):
        """Test getting non-existent product."""
        fake_id = '00000000-0000-0000-0000-000000000000'
        response = client.get(f'/products/{fake_id}')
        assert response.status_code == 404


class TestSubscriptionManagement:
    """Test cases for subscription management endpoints."""

    def get_auth_headers(self, client, sample_user):
        """Helper method to get authentication headers."""
        client.post('/auth/register', 
                   data=json.dumps(sample_user),
                   content_type='application/json')
        
        login_data = {
            'email': sample_user['email'],
            'password': sample_user['password']
        }
        response = client.post('/auth/login', 
                             data=json.dumps(login_data),
                             content_type='application/json')
        
        data = json.loads(response.data)
        return {'Authorization': f"Bearer {data['access_token']}"}

    def get_product_id(self, client):
        """Helper method to get a product ID."""
        response = client.get('/products')
        data = json.loads(response.data)
        if data['products']:
            return data['products'][0]['product_id']
        return None

    def test_list_user_subscriptions(self, client, sample_user):
        """Test listing user subscriptions."""
        headers = self.get_auth_headers(client, sample_user)
        
        response = client.get('/subscriptions', headers=headers)
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert 'subscriptions' in data
        assert 'total' in data

    def test_create_subscription_success(self, client, sample_user, sample_subscription):
        """Test successful subscription creation."""
        headers = self.get_auth_headers(client, sample_user)
        product_id = self.get_product_id(client)
        
        if product_id:
            sample_subscription['product_id'] = product_id
            
            response = client.post('/subscriptions', 
                                 data=json.dumps(sample_subscription),
                                 content_type='application/json',
                                 headers=headers)
            
            assert response.status_code == 201
            data = json.loads(response.data)
            assert data['product_id'] == product_id
            assert data['frequency'] == sample_subscription['frequency']

    def test_create_subscription_invalid_product(self, client, sample_user, sample_subscription):
        """Test subscription creation with invalid product."""
        headers = self.get_auth_headers(client, sample_user)
        
        sample_subscription['product_id'] = '00000000-0000-0000-0000-000000000000'
        
        response = client.post('/subscriptions', 
                             data=json.dumps(sample_subscription),
                             content_type='application/json',
                             headers=headers)
        
        assert response.status_code == 400

    def test_get_subscription_details(self, client, sample_user, sample_subscription):
        """Test getting subscription details."""
        headers = self.get_auth_headers(client, sample_user)
        product_id = self.get_product_id(client)
        
        if product_id:
            sample_subscription['product_id'] = product_id
            
            # Create subscription
            response = client.post('/subscriptions', 
                                 data=json.dumps(sample_subscription),
                                 content_type='application/json',
                                 headers=headers)
            
            subscription_data = json.loads(response.data)
            subscription_id = subscription_data['subscription_id']
            
            # Get subscription details
            response = client.get(f'/subscriptions/{subscription_id}', headers=headers)
            assert response.status_code == 200
            
            data = json.loads(response.data)
            assert data['subscription_id'] == subscription_id

    def test_update_subscription(self, client, sample_user, sample_subscription):
        """Test updating subscription."""
        headers = self.get_auth_headers(client, sample_user)
        product_id = self.get_product_id(client)
        
        if product_id:
            sample_subscription['product_id'] = product_id
            
            # Create subscription
            response = client.post('/subscriptions', 
                                 data=json.dumps(sample_subscription),
                                 content_type='application/json',
                                 headers=headers)
            
            subscription_data = json.loads(response.data)
            subscription_id = subscription_data['subscription_id']
            
            # Update subscription
            update_data = {
                'frequency': 'weekly',
                'quantity': 2
            }
            
            response = client.put(f'/subscriptions/{subscription_id}', 
                                data=json.dumps(update_data),
                                content_type='application/json',
                                headers=headers)
            
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['frequency'] == 'weekly'
            assert data['quantity'] == 2

    def test_pause_subscription(self, client, sample_user, sample_subscription):
        """Test pausing subscription."""
        headers = self.get_auth_headers(client, sample_user)
        product_id = self.get_product_id(client)
        
        if product_id:
            sample_subscription['product_id'] = product_id
            
            # Create subscription
            response = client.post('/subscriptions', 
                                 data=json.dumps(sample_subscription),
                                 content_type='application/json',
                                 headers=headers)
            
            subscription_data = json.loads(response.data)
            subscription_id = subscription_data['subscription_id']
            
            # Pause subscription
            pause_data = {
                'reason': 'Going on vacation'
            }
            
            response = client.post(f'/subscriptions/{subscription_id}/pause', 
                                 data=json.dumps(pause_data),
                                 content_type='application/json',
                                 headers=headers)
            
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['status'] == 'paused'

    def test_resume_subscription(self, client, sample_user, sample_subscription):
        """Test resuming subscription."""
        headers = self.get_auth_headers(client, sample_user)
        product_id = self.get_product_id(client)
        
        if product_id:
            sample_subscription['product_id'] = product_id
            
            # Create and pause subscription
            response = client.post('/subscriptions', 
                                 data=json.dumps(sample_subscription),
                                 content_type='application/json',
                                 headers=headers)
            
            subscription_data = json.loads(response.data)
            subscription_id = subscription_data['subscription_id']
            
            # Pause first
            client.post(f'/subscriptions/{subscription_id}/pause', 
                       data=json.dumps({'reason': 'Test'}),
                       content_type='application/json',
                       headers=headers)
            
            # Resume subscription
            response = client.post(f'/subscriptions/{subscription_id}/resume', 
                                 headers=headers)
            
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['status'] == 'active'

    def test_cancel_subscription(self, client, sample_user, sample_subscription):
        """Test canceling subscription."""
        headers = self.get_auth_headers(client, sample_user)
        product_id = self.get_product_id(client)
        
        if product_id:
            sample_subscription['product_id'] = product_id
            
            # Create subscription
            response = client.post('/subscriptions', 
                                 data=json.dumps(sample_subscription),
                                 content_type='application/json',
                                 headers=headers)
            
            subscription_data = json.loads(response.data)
            subscription_id = subscription_data['subscription_id']
            
            # Cancel subscription
            cancel_data = {
                'reason': 'No longer needed',
                'immediate': True
            }
            
            response = client.post(f'/subscriptions/{subscription_id}/cancel', 
                                 data=json.dumps(cancel_data),
                                 content_type='application/json',
                                 headers=headers)
            
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['status'] == 'canceled'

    def test_skip_delivery(self, client, sample_user, sample_subscription):
        """Test skipping next delivery."""
        headers = self.get_auth_headers(client, sample_user)
        product_id = self.get_product_id(client)
        
        if product_id:
            sample_subscription['product_id'] = product_id
            
            # Create subscription
            response = client.post('/subscriptions', 
                                 data=json.dumps(sample_subscription),
                                 content_type='application/json',
                                 headers=headers)
            
            subscription_data = json.loads(response.data)
            subscription_id = subscription_data['subscription_id']
            
            # Skip delivery
            skip_data = {
                'reason': 'Already have enough'
            }
            
            response = client.post(f'/subscriptions/{subscription_id}/skip', 
                                 data=json.dumps(skip_data),
                                 content_type='application/json',
                                 headers=headers)
            
            assert response.status_code == 200


class TestPaymentIntegration:
    """Test cases for payment integration."""

    def get_auth_headers(self, client, sample_user):
        """Helper method to get authentication headers."""
        client.post('/auth/register', 
                   data=json.dumps(sample_user),
                   content_type='application/json')
        
        login_data = {
            'email': sample_user['email'],
            'password': sample_user['password']
        }
        response = client.post('/auth/login', 
                             data=json.dumps(login_data),
                             content_type='application/json')
        
        data = json.loads(response.data)
        return {'Authorization': f"Bearer {data['access_token']}"}

    def test_list_user_payments(self, client, sample_user):
        """Test listing user payments."""
        headers = self.get_auth_headers(client, sample_user)
        
        response = client.get('/payments', headers=headers)
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert 'payments' in data
        assert 'total' in data

    @patch('razorpay.Client')
    def test_create_razorpay_order(self, mock_razorpay, client, sample_user):
        """Test creating Razorpay order."""
        headers = self.get_auth_headers(client, sample_user)
        
        # Mock Razorpay client
        mock_client = MagicMock()
        mock_client.order.create.return_value = {
            'id': 'order_test123',
            'amount': 100000,
            'currency': 'INR'
        }
        mock_razorpay.return_value = mock_client
        
        order_data = {
            'subscription_id': '00000000-0000-0000-0000-000000000000',
            'amount': 1000.00,
            'currency': 'INR'
        }
        
        response = client.post('/razorpay/create-order', 
                             data=json.dumps(order_data),
                             content_type='application/json',
                             headers=headers)
        
        assert response.status_code == 201
        data = json.loads(response.data)
        assert 'order_id' in data
        assert 'key' in data

    @patch('razorpay.Client')
    def test_verify_razorpay_payment(self, mock_razorpay, client, sample_user):
        """Test verifying Razorpay payment."""
        headers = self.get_auth_headers(client, sample_user)
        
        # Mock Razorpay client
        mock_client = MagicMock()
        mock_client.utility.verify_payment_signature.return_value = True
        mock_razorpay.return_value = mock_client
        
        payment_data = {
            'razorpay_order_id': 'order_test123',
            'razorpay_payment_id': 'pay_test123',
            'razorpay_signature': 'signature_test123'
        }
        
        response = client.post('/razorpay/verify-payment', 
                             data=json.dumps(payment_data),
                             content_type='application/json',
                             headers=headers)
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'verified'


class TestAdminEndpoints:
    """Test cases for admin endpoints."""

    def get_admin_headers(self, client):
        """Helper method to get admin authentication headers."""
        admin_user = {
            'email': 'admin@subscriptionpro.com',
            'password': 'admin123',
            'first_name': 'Admin',
            'last_name': 'User',
            'user_role': 'admin'
        }
        
        client.post('/auth/register', 
                   data=json.dumps(admin_user),
                   content_type='application/json')
        
        login_data = {
            'email': admin_user['email'],
            'password': admin_user['password']
        }
        response = client.post('/auth/login', 
                             data=json.dumps(login_data),
                             content_type='application/json')
        
        data = json.loads(response.data)
        return {'Authorization': f"Bearer {data['access_token']}"}

    def test_admin_list_users(self, client):
        """Test admin listing all users."""
        headers = self.get_admin_headers(client)
        
        response = client.get('/admin/users', headers=headers)
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert 'users' in data
        assert 'total' in data

    def test_admin_list_subscriptions(self, client):
        """Test admin listing all subscriptions."""
        headers = self.get_admin_headers(client)
        
        response = client.get('/admin/subscriptions', headers=headers)
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert 'subscriptions' in data
        assert 'total' in data

    def test_admin_dashboard_stats(self, client):
        """Test admin dashboard statistics."""
        headers = self.get_admin_headers(client)
        
        response = client.get('/admin/dashboard/stats', headers=headers)
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert 'total_users' in data
        assert 'active_subscriptions' in data
        assert 'monthly_revenue' in data

    def test_admin_audit_logs(self, client):
        """Test admin audit logs."""
        headers = self.get_admin_headers(client)
        
        response = client.get('/admin/audit-logs', headers=headers)
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert 'logs' in data
        assert 'total' in data

    def test_non_admin_access_denied(self, client, sample_user):
        """Test non-admin user accessing admin endpoints."""
        # Create regular user
        client.post('/auth/register', 
                   data=json.dumps(sample_user),
                   content_type='application/json')
        
        login_data = {
            'email': sample_user['email'],
            'password': sample_user['password']
        }
        response = client.post('/auth/login', 
                             data=json.dumps(login_data),
                             content_type='application/json')
        
        data = json.loads(response.data)
        headers = {'Authorization': f"Bearer {data['access_token']}"}
        
        # Try to access admin endpoint
        response = client.get('/admin/users', headers=headers)
        assert response.status_code == 403


class TestSystemEndpoints:
    """Test cases for system endpoints."""

    def test_health_check(self, client):
        """Test health check endpoint."""
        response = client.get('/health')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['status'] == 'healthy'
        assert 'timestamp' in data


class TestErrorHandling:
    """Test cases for error handling."""

    def test_404_error(self, client):
        """Test 404 error handling."""
        response = client.get('/nonexistent-endpoint')
        assert response.status_code == 404

    def test_405_method_not_allowed(self, client):
        """Test 405 method not allowed error."""
        response = client.delete('/health')
        assert response.status_code == 405

    def test_invalid_json(self, client):
        """Test invalid JSON handling."""
        response = client.post('/auth/login', 
                             data='invalid json',
                             content_type='application/json')
        assert response.status_code == 400


class TestRateLimiting:
    """Test cases for rate limiting."""

    def test_login_rate_limiting(self, client):
        """Test login rate limiting."""
        login_data = {
            'email': 'test@example.com',
            'password': 'wrongpassword'
        }
        
        # Make multiple failed login attempts
        for _ in range(6):  # Exceed the 5 per minute limit
            response = client.post('/auth/login', 
                                 data=json.dumps(login_data),
                                 content_type='application/json')
        
        # The last request should be rate limited
        assert response.status_code == 429


if __name__ == '__main__':
    pytest.main(['-v', '--cov=src', '--cov-report=html'])

