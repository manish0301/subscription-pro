import razorpay
import os
from datetime import datetime
from backend.models.subscription import Subscription
from backend.core.database import db

class BillingService:
    def __init__(self):
        self.razorpay_client = razorpay.Client(
            auth=(os.environ.get('RAZORPAY_KEY_ID'), os.environ.get('RAZORPAY_KEY_SECRET'))
        )
    
    def create_subscription_order(self, subscription_id, amount):
        """Create Razorpay order for subscription billing"""
        order_data = {
            'amount': int(amount * 100),  # Convert to paise
            'currency': 'INR',
            'receipt': f'sub_{subscription_id}_{datetime.now().timestamp()}',
            'notes': {'subscription_id': subscription_id}
        }
        return self.razorpay_client.order.create(data=order_data)
    
    def process_recurring_billing(self):
        """Process all due subscriptions"""
        with db.get_cursor() as (cursor, conn):
            cursor.execute("""
                SELECT * FROM subscriptions 
                WHERE status='active' AND next_billing_date <= NOW()
            """)
            due_subscriptions = cursor.fetchall()
            
            for sub_data in due_subscriptions:
                subscription = Subscription(**sub_data)
                try:
                    # Create order for billing
                    order = self.create_subscription_order(subscription.subscription_id, subscription.amount)
                    
                    # Update next billing date
                    subscription.next_billing_date = subscription._calculate_next_billing()
                    subscription.save()
                    
                    # Log billing event
                    self._log_billing_event(subscription.subscription_id, 'success', order['id'])
                    
                except Exception as e:
                    self._log_billing_event(subscription.subscription_id, 'failed', str(e))
    
    def _log_billing_event(self, subscription_id, status, details):
        with db.get_cursor() as (cursor, conn):
            cursor.execute("""
                INSERT INTO billing_logs (subscription_id, status, details, created_at)
                VALUES (%s, %s, %s, NOW())
            """, (subscription_id, status, details))
            conn.commit()