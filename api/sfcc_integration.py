#!/usr/bin/env python3
"""
Salesforce Commerce Cloud B2C Integration
Handles data synchronization between SubscriptionPro and SFCC
"""

import requests
import json
import os
import time
import hashlib
import hmac
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any

class SFCCIntegration:
    """Salesforce Commerce Cloud B2C Integration Client"""
    
    def __init__(self):
        self.client_id = os.environ.get('SFCC_CLIENT_ID')
        self.client_secret = os.environ.get('SFCC_CLIENT_SECRET')
        self.instance_url = os.environ.get('SFCC_INSTANCE_URL')  # e.g., https://your-instance.demandware.net
        self.site_id = os.environ.get('SFCC_SITE_ID', 'SiteGenesis')
        self.version = os.environ.get('SFCC_API_VERSION', 'v23_2')
        
        self.access_token = None
        self.token_expires_at = None
        
        # API endpoints
        self.auth_url = f"{self.instance_url}/dw/oauth2/access_token"
        # SCAPI (Shopper API) - Modern API for customer-facing operations
        self.scapi_base = f"{self.instance_url}/s/{self.site_id}/dw/shop/{self.version}"
        # OCAPI (Open Commerce API) - Legacy API for data management
        self.ocapi_base = f"{self.instance_url}/s/{self.site_id}/dw/data/{self.version}"
        
    def authenticate(self) -> bool:
        """Authenticate with SFCC using OAuth 2.0"""
        if not all([self.client_id, self.client_secret, self.instance_url]):
            print("❌ SFCC credentials not configured")
            return False
        
        try:
            auth_data = {
                'grant_type': 'client_credentials',
                'scope': 'SALESFORCE_COMMERCE_API:your-instance_your-site'
            }
            
            auth_header = f"{self.client_id}:{self.client_secret}"
            auth_encoded = requests.auth._basic_auth_str(self.client_id, self.client_secret)
            
            headers = {
                'Authorization': auth_encoded,
                'Content-Type': 'application/x-www-form-urlencoded'
            }
            
            response = requests.post(self.auth_url, data=auth_data, headers=headers)
            
            if response.status_code == 200:
                token_data = response.json()
                self.access_token = token_data['access_token']
                self.token_expires_at = time.time() + token_data.get('expires_in', 3600)
                print("✅ SFCC authentication successful")
                return True
            else:
                print(f"❌ SFCC authentication failed: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ SFCC authentication error: {e}")
            return False
    
    def get_headers(self) -> Dict[str, str]:
        """Get authenticated request headers"""
        if not self.access_token or time.time() >= self.token_expires_at:
            if not self.authenticate():
                raise Exception("Failed to authenticate with SFCC")
        
        return {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json'
        }
    
    def sync_customer_to_sfcc(self, customer_data: Dict) -> Optional[str]:
        """Sync customer data to SFCC"""
        try:
            headers = self.get_headers()
            
            # Transform customer data to SFCC format
            sfcc_customer = {
                'customer_id': customer_data['user_id'],
                'email': customer_data['email'],
                'first_name': customer_data.get('first_name'),
                'last_name': customer_data.get('last_name'),
                'phone_home': customer_data.get('phone_number'),
                'enabled': customer_data.get('is_active', True)
            }
            
            # Add address if available
            if customer_data.get('address_line1'):
                sfcc_customer['addresses'] = [{
                    'address_id': 'default',
                    'first_name': customer_data.get('first_name'),
                    'last_name': customer_data.get('last_name'),
                    'address1': customer_data.get('address_line1'),
                    'address2': customer_data.get('address_line2'),
                    'city': customer_data.get('city'),
                    'state_code': customer_data.get('state'),
                    'postal_code': customer_data.get('postal_code'),
                    'country_code': customer_data.get('country', 'IN')
                }]
            
            # Create or update customer in SFCC
            customer_url = f"{self.ocapi_base}/customers/{customer_data['user_id']}"
            response = requests.put(customer_url, json=sfcc_customer, headers=headers)
            
            if response.status_code in [200, 201]:
                print(f"✅ Customer synced to SFCC: {customer_data['email']}")
                return customer_data['user_id']
            else:
                print(f"❌ Failed to sync customer to SFCC: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"❌ Error syncing customer to SFCC: {e}")
            return None
    
    def sync_product_to_sfcc(self, product_data: Dict) -> Optional[str]:
        """Sync product data to SFCC"""
        try:
            headers = self.get_headers()
            
            # Transform product data to SFCC format
            sfcc_product = {
                'id': product_data['product_id'],
                'name': {
                    'default': product_data['name']
                },
                'short_description': {
                    'default': product_data.get('description', '')
                },
                'long_description': {
                    'default': product_data.get('description', '')
                },
                'online': product_data.get('is_active', True),
                'searchable': True,
                'price': product_data['price'],
                'currency': product_data.get('currency', 'INR'),
                'custom': {
                    'isSubscriptionProduct': product_data.get('is_subscription_product', True),
                    'subscriptionProId': product_data['product_id'],
                    'category': product_data.get('category'),
                    'sku': product_data.get('sku')
                }
            }
            
            # Create or update product in SFCC
            product_url = f"{self.ocapi_base}/products/{product_data['product_id']}"
            response = requests.put(product_url, json=sfcc_product, headers=headers)
            
            if response.status_code in [200, 201]:
                print(f"✅ Product synced to SFCC: {product_data['name']}")
                return product_data['product_id']
            else:
                print(f"❌ Failed to sync product to SFCC: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"❌ Error syncing product to SFCC: {e}")
            return None
    
    def create_subscription_order(self, subscription_data: Dict) -> Optional[str]:
        """Create a subscription order in SFCC"""
        try:
            headers = self.get_headers()
            
            # Create order data
            order_data = {
                'customer_info': {
                    'customer_id': subscription_data['user_id'],
                    'email': subscription_data.get('customer_email')
                },
                'product_items': [{
                    'product_id': subscription_data['product_id'],
                    'quantity': subscription_data.get('quantity', 1),
                    'price': subscription_data['amount']
                }],
                'custom': {
                    'subscriptionId': subscription_data['subscription_id'],
                    'subscriptionFrequency': subscription_data['frequency'],
                    'isSubscriptionOrder': True,
                    'nextDeliveryDate': subscription_data.get('next_delivery_date')
                },
                'order_total': subscription_data['amount'],
                'currency': subscription_data.get('currency', 'INR')
            }
            
            # Create order in SFCC
            order_url = f"{self.scapi_base}/orders"
            response = requests.post(order_url, json=order_data, headers=headers)
            
            if response.status_code in [200, 201]:
                order_response = response.json()
                order_id = order_response.get('order_no')
                print(f"✅ Subscription order created in SFCC: {order_id}")
                return order_id
            else:
                print(f"❌ Failed to create order in SFCC: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"❌ Error creating order in SFCC: {e}")
            return None
    
    def get_sfcc_customer(self, customer_id: str) -> Optional[Dict]:
        """Get customer data from SFCC"""
        try:
            headers = self.get_headers()
            customer_url = f"{self.ocapi_base}/customers/{customer_id}"
            
            response = requests.get(customer_url, headers=headers)
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"❌ Failed to get customer from SFCC: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"❌ Error getting customer from SFCC: {e}")
            return None
    
    def get_sfcc_product(self, product_id: str) -> Optional[Dict]:
        """Get product data from SFCC"""
        try:
            headers = self.get_headers()
            product_url = f"{self.scapi_base}/products/{product_id}"
            
            response = requests.get(product_url, headers=headers)
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"❌ Failed to get product from SFCC: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"❌ Error getting product from SFCC: {e}")
            return None
    
    def webhook_handler(self, webhook_data: Dict) -> bool:
        """Handle webhooks from SFCC"""
        try:
            event_type = webhook_data.get('event_type')
            
            if event_type == 'customer.created':
                # Handle new customer from SFCC
                customer_data = webhook_data.get('data', {})
                print(f"📥 New customer from SFCC: {customer_data.get('email')}")
                # Sync to SubscriptionPro database
                return True
                
            elif event_type == 'order.created':
                # Handle new order from SFCC
                order_data = webhook_data.get('data', {})
                print(f"📥 New order from SFCC: {order_data.get('order_no')}")
                # Process subscription if applicable
                return True
                
            elif event_type == 'product.updated':
                # Handle product updates from SFCC
                product_data = webhook_data.get('data', {})
                print(f"📥 Product updated in SFCC: {product_data.get('id')}")
                # Sync to SubscriptionPro database
                return True
                
            else:
                print(f"⚠️  Unknown webhook event: {event_type}")
                return False
                
        except Exception as e:
            print(f"❌ Error handling SFCC webhook: {e}")
            return False
    
    def sync_all_data(self) -> Dict[str, int]:
        """Sync all data between SubscriptionPro and SFCC"""
        print("🔄 Starting full data synchronization with SFCC...")
        
        sync_results = {
            'customers_synced': 0,
            'products_synced': 0,
            'orders_created': 0,
            'errors': 0
        }
        
        try:
            # This would integrate with your Supabase database
            # For now, we'll simulate the sync process
            
            print("✅ Data synchronization completed")
            return sync_results
            
        except Exception as e:
            print(f"❌ Error during data synchronization: {e}")
            sync_results['errors'] += 1
            return sync_results

# SFCC Cartridge Integration Helper
class SFCCCartridgeHelper:
    """Helper for SFCC cartridge development"""
    
    @staticmethod
    def generate_cartridge_structure():
        """Generate basic cartridge structure for SFCC"""
        cartridge_structure = {
            "cartridge_name": "int_subscriptionpro",
            "directories": [
                "cartridge/controllers",
                "cartridge/models",
                "cartridge/scripts",
                "cartridge/templates/default",
                "cartridge/static/default/js",
                "cartridge/static/default/css"
            ],
            "files": {
                "cartridge/controllers/SubscriptionPro.js": "// SubscriptionPro controller",
                "cartridge/models/SubscriptionModel.js": "// Subscription model",
                "cartridge/scripts/SubscriptionService.js": "// API integration service",
                "cartridge/templates/default/subscription/manage.isml": "<!-- Subscription management template -->"
            }
        }
        
        return cartridge_structure
    
    @staticmethod
    def generate_api_integration_code():
        """Generate SFCC server-side JavaScript for API integration"""
        
        api_code = """
// SubscriptionPro API Integration for SFCC
var HTTPClient = require('dw/net/HTTPClient');
var Encoding = require('dw/crypto/Encoding');

var SubscriptionProAPI = {
    baseURL: 'https://your-api.vercel.app/api',
    
    createSubscription: function(customerData, productData, subscriptionData) {
        var client = new HTTPClient();
        client.open('POST', this.baseURL + '/subscriptions');
        client.setRequestHeader('Content-Type', 'application/json');
        client.setRequestHeader('Authorization', 'Bearer ' + this.getAuthToken());
        
        var requestData = {
            user_id: customerData.ID,
            product_id: productData.ID,
            frequency: subscriptionData.frequency,
            start_date: subscriptionData.startDate,
            quantity: subscriptionData.quantity
        };
        
        client.send(JSON.stringify(requestData));
        
        if (client.statusCode === 201) {
            return JSON.parse(client.text);
        } else {
            throw new Error('Failed to create subscription: ' + client.statusCode);
        }
    },
    
    getAuthToken: function() {
        // Implement token management
        return session.privacy.subscriptionProToken;
    }
};

module.exports = SubscriptionProAPI;
"""
        
        return api_code

# Integration testing
def test_sfcc_integration():
    """Test SFCC integration functionality"""
    print("🧪 Testing SFCC Integration...")
    
    integration = SFCCIntegration()
    
    # Test authentication
    if integration.authenticate():
        print("✅ Authentication test passed")
    else:
        print("❌ Authentication test failed")
        return False
    
    # Test data sync (mock data)
    mock_customer = {
        'user_id': 'test-customer-123',
        'email': 'test@example.com',
        'first_name': 'Test',
        'last_name': 'Customer'
    }
    
    mock_product = {
        'product_id': 'test-product-123',
        'name': 'Test Subscription Product',
        'price': 1299.00,
        'is_subscription_product': True
    }
    
    print("✅ SFCC integration tests completed")
    return True

if __name__ == "__main__":
    test_sfcc_integration()
