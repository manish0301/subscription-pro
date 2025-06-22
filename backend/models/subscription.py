from datetime import datetime, timedelta
from backend.core.database import db

class Subscription:
    def __init__(self, subscription_id=None, user_id=None, product_id=None, 
                 status='active', frequency='monthly', amount=0, next_billing_date=None):
        self.subscription_id = subscription_id
        self.user_id = user_id
        self.product_id = product_id
        self.status = status
        self.frequency = frequency
        self.amount = amount
        self.next_billing_date = next_billing_date or self._calculate_next_billing()
    
    def _calculate_next_billing(self):
        if self.frequency == 'weekly':
            return datetime.now() + timedelta(weeks=1)
        elif self.frequency == 'monthly':
            return datetime.now() + timedelta(days=30)
        elif self.frequency == 'quarterly':
            return datetime.now() + timedelta(days=90)
        return datetime.now() + timedelta(days=365)
    
    def save(self):
        with db.get_cursor() as (cursor, conn):
            if self.subscription_id:
                cursor.execute("""
                    UPDATE subscriptions SET status=%s, frequency=%s, amount=%s, 
                    next_billing_date=%s WHERE subscription_id=%s
                """, (self.status, self.frequency, self.amount, self.next_billing_date, self.subscription_id))
            else:
                cursor.execute("""
                    INSERT INTO subscriptions (user_id, product_id, status, frequency, amount, next_billing_date)
                    VALUES (%s, %s, %s, %s, %s, %s) RETURNING subscription_id
                """, (self.user_id, self.product_id, self.status, self.frequency, self.amount, self.next_billing_date))
                self.subscription_id = cursor.fetchone()['subscription_id']
            conn.commit()
    
    @classmethod
    def get_by_user(cls, user_id):
        with db.get_cursor() as (cursor, conn):
            cursor.execute("SELECT * FROM subscriptions WHERE user_id=%s", (user_id,))
            return [cls(**row) for row in cursor.fetchall()]
    
    @classmethod
    def get_active_subscriptions(cls):
        with db.get_cursor() as (cursor, conn):
            cursor.execute("SELECT * FROM subscriptions WHERE status='active'")
            return [cls(**row) for row in cursor.fetchall()]