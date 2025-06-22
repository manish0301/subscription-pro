import unittest
import json
from unittest.mock import patch, MagicMock
from backend.api.customer_api import app

class TestSubscriptionAPI(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True
    
    @patch('backend.models.subscription.db')
    def test_get_customer_subscriptions(self, mock_db):
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = [
            {
                'subscription_id': '1',
                'user_id': '1',
                'product_id': '1',
                'status': 'active',
                'frequency': 'monthly',
                'amount': 299,
                'next_billing_date': '2025-02-01'
            }
        ]
        mock_db.get_cursor.return_value.__enter__.return_value = (mock_cursor, MagicMock())
        
        response = self.app.get('/api/customer/subscriptions?user_id=1')
        self.assertEqual(response.status_code, 200)
    
    def test_missing_user_id(self):
        response = self.app.get('/api/customer/subscriptions')
        self.assertEqual(response.status_code, 400)

if __name__ == '__main__':
    unittest.main()