from flask import Flask, request, jsonify
from backend.core.database import db

app = Flask(__name__)

@app.route('/api/merchant/dashboard', methods=['GET'])
def merchant_dashboard():
    with db.get_cursor() as (cursor, conn):
        # Get subscription metrics
        cursor.execute("SELECT COUNT(*) as total FROM subscriptions WHERE status='active'")
        active_subs = cursor.fetchone()['total']
        
        cursor.execute("SELECT SUM(amount) as revenue FROM subscriptions WHERE status='active'")
        monthly_revenue = cursor.fetchone()['revenue'] or 0
        
        cursor.execute("SELECT COUNT(*) as total FROM subscriptions WHERE created_at >= NOW() - INTERVAL '30 days'")
        new_subs = cursor.fetchone()['total']
        
        cursor.execute("SELECT COUNT(*) as total FROM subscriptions WHERE status='canceled' AND updated_at >= NOW() - INTERVAL '30 days'")
        churned_subs = cursor.fetchone()['total']
        
        return jsonify({
            'active_subscriptions': active_subs,
            'monthly_revenue': float(monthly_revenue),
            'new_subscriptions_30d': new_subs,
            'churn_rate': (churned_subs / max(active_subs, 1)) * 100,
            'growth_rate': ((new_subs - churned_subs) / max(active_subs, 1)) * 100
        })

@app.route('/api/merchant/products', methods=['GET'])
def get_products():
    with db.get_cursor() as (cursor, conn):
        cursor.execute("SELECT * FROM products WHERE is_active=true")
        products = cursor.fetchall()
        return jsonify([dict(product) for product in products])

@app.route('/api/merchant/products', methods=['POST'])
def create_product():
    data = request.json
    with db.get_cursor() as (cursor, conn):
        cursor.execute("""
            INSERT INTO products (name, description, price, currency, is_subscription_product)
            VALUES (%s, %s, %s, %s, %s) RETURNING product_id
        """, (data['name'], data['description'], data['price'], data.get('currency', 'INR'), True))
        
        product_id = cursor.fetchone()['product_id']
        conn.commit()
        
        return jsonify({'product_id': product_id, 'status': 'created'})

@app.route('/api/merchant/subscriptions', methods=['GET'])
def get_merchant_subscriptions():
    status_filter = request.args.get('status', 'all')
    
    with db.get_cursor() as (cursor, conn):
        if status_filter == 'all':
            cursor.execute("""
                SELECT s.*, p.name as product_name, u.email as customer_email
                FROM subscriptions s
                JOIN products p ON s.product_id = p.product_id
                JOIN users u ON s.user_id = u.user_id
                ORDER BY s.created_at DESC
            """)
        else:
            cursor.execute("""
                SELECT s.*, p.name as product_name, u.email as customer_email
                FROM subscriptions s
                JOIN products p ON s.product_id = p.product_id
                JOIN users u ON s.user_id = u.user_id
                WHERE s.status = %s
                ORDER BY s.created_at DESC
            """, (status_filter,))
        
        subscriptions = cursor.fetchall()
        return jsonify([dict(sub) for sub in subscriptions])

@app.route('/api/merchant/analytics/revenue', methods=['GET'])
def revenue_analytics():
    period = request.args.get('period', '30')  # days
    
    with db.get_cursor() as (cursor, conn):
        cursor.execute(f"""
            SELECT DATE(created_at) as date, SUM(amount) as revenue
            FROM subscriptions
            WHERE created_at >= NOW() - INTERVAL '{period} days'
            AND status = 'active'
            GROUP BY DATE(created_at)
            ORDER BY date
        """)
        
        revenue_data = cursor.fetchall()
        return jsonify([dict(row) for row in revenue_data])

@app.route('/api/merchant/analytics/churn', methods=['GET'])
def churn_analytics():
    with db.get_cursor() as (cursor, conn):
        cursor.execute("""
            SELECT 
                DATE_TRUNC('month', updated_at) as month,
                COUNT(*) as churned_customers
            FROM subscriptions
            WHERE status = 'canceled'
            AND updated_at >= NOW() - INTERVAL '12 months'
            GROUP BY DATE_TRUNC('month', updated_at)
            ORDER BY month
        """)
        
        churn_data = cursor.fetchall()
        return jsonify([dict(row) for row in churn_data])