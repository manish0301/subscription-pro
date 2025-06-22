from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import json
from datetime import datetime, timedelta

app = Flask(__name__)
CORS(app)

# Mock data for demo (replace with real database)
mock_subscriptions = [
    {
        'subscription_id': '1',
        'user_id': '1',
        'product_id': '1',
        'status': 'active',
        'frequency': 'monthly',
        'amount': 299,
        'next_billing_date': '2025-02-15',
        'product_name': 'Premium Coffee',
        'customer_email': 'john@example.com'
    }
]

mock_products = [
    {'product_id': '1', 'name': 'Premium Coffee', 'description': 'Monthly coffee delivery', 'price': 299, 'is_active': True},
    {'product_id': '2', 'name': 'Organic Snacks', 'description': 'Weekly snack box', 'price': 199, 'is_active': True},
    {'product_id': '3', 'name': 'Book Club', 'description': 'Monthly book selection', 'price': 999, 'is_active': True}
]

# Authentication endpoints
@app.route('/api/auth/login', methods=['POST'])
def login():
    data = request.json
    # Mock authentication
    if data.get('email') == 'admin@demo.com' and data.get('password') == 'admin123':
        return jsonify({
            'token': 'mock-jwt-token',
            'user_id': '1',
            'role': 'admin'
        })
    return jsonify({'error': 'Invalid credentials'}), 401

# Customer API
@app.route('/api/customer/subscriptions', methods=['GET'])
def get_customer_subscriptions():
    user_id = request.args.get('user_id', '1')
    user_subs = [sub for sub in mock_subscriptions if sub['user_id'] == user_id]
    return jsonify(user_subs)

@app.route('/api/customer/subscription', methods=['POST'])
def create_subscription():
    data = request.json
    new_sub = {
        'subscription_id': str(len(mock_subscriptions) + 1),
        'user_id': data['user_id'],
        'product_id': data['product_id'],
        'status': 'active',
        'frequency': data['frequency'],
        'amount': data['amount'],
        'next_billing_date': (datetime.now() + timedelta(days=30)).isoformat(),
        'product_name': 'New Product',
        'customer_email': 'customer@example.com'
    }
    mock_subscriptions.append(new_sub)
    return jsonify({'subscription_id': new_sub['subscription_id'], 'status': 'created'})

@app.route('/api/customer/subscription/<subscription_id>/pause', methods=['POST'])
def pause_subscription(subscription_id):
    for sub in mock_subscriptions:
        if sub['subscription_id'] == subscription_id:
            sub['status'] = 'paused'
            break
    return jsonify({'status': 'paused'})

@app.route('/api/customer/subscription/<subscription_id>/cancel', methods=['POST'])
def cancel_subscription(subscription_id):
    for sub in mock_subscriptions:
        if sub['subscription_id'] == subscription_id:
            sub['status'] = 'canceled'
            break
    return jsonify({'status': 'canceled'})

# Merchant API
@app.route('/api/merchant/dashboard', methods=['GET'])
def merchant_dashboard():
    active_subs = len([s for s in mock_subscriptions if s['status'] == 'active'])
    total_revenue = sum(s['amount'] for s in mock_subscriptions if s['status'] == 'active')
    
    return jsonify({
        'active_subscriptions': active_subs,
        'monthly_revenue': total_revenue,
        'new_subscriptions_30d': 15,
        'churn_rate': 8.5,
        'growth_rate': 12.3
    })

@app.route('/api/merchant/products', methods=['GET'])
def get_products():
    return jsonify(mock_products)

@app.route('/api/merchant/products', methods=['POST'])
def create_product():
    data = request.json
    new_product = {
        'product_id': str(len(mock_products) + 1),
        'name': data['name'],
        'description': data['description'],
        'price': data['price'],
        'is_active': True
    }
    mock_products.append(new_product)
    return jsonify({'product_id': new_product['product_id'], 'status': 'created'})

@app.route('/api/merchant/subscriptions', methods=['GET'])
def get_merchant_subscriptions():
    status_filter = request.args.get('status', 'all')
    if status_filter == 'all':
        return jsonify(mock_subscriptions)
    else:
        filtered = [s for s in mock_subscriptions if s['status'] == status_filter]
        return jsonify(filtered)

@app.route('/api/merchant/analytics/revenue', methods=['GET'])
def revenue_analytics():
    # Mock revenue data for last 30 days
    revenue_data = []
    for i in range(30):
        date = (datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d')
        revenue_data.append({
            'date': date,
            'revenue': 1000 + (i * 50)  # Mock increasing revenue
        })
    return jsonify(revenue_data)

@app.route('/api/merchant/analytics/churn', methods=['GET'])
def churn_analytics():
    # Mock churn data for last 12 months
    churn_data = []
    for i in range(12):
        month = (datetime.now() - timedelta(days=i*30)).strftime('%Y-%m-01')
        churn_data.append({
            'month': month,
            'churned_customers': 5 + (i % 3)  # Mock churn pattern
        })
    return jsonify(churn_data)

# Health check
@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'healthy',
        'service': 'SubscriptionPro Enterprise Demo',
        'version': '1.0.0',
        'database': 'mock_data'
    })

# Frontend routes
@app.route('/')
def customer_portal():
    return '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SubscriptionPro - Customer Portal</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-gray-50">
    <header class="bg-white shadow-sm">
        <div class="max-w-7xl mx-auto px-4 py-4">
            <h1 class="text-2xl font-bold text-blue-600">SubscriptionPro Enterprise Demo</h1>
        </div>
    </header>
    <main class="max-w-7xl mx-auto px-4 py-8">
        <div class="bg-yellow-100 border-l-4 border-yellow-500 p-4 mb-6">
            <div class="flex">
                <div class="ml-3">
                    <p class="text-sm text-yellow-700">
                        <strong>Demo Version:</strong> This is a functional demo with mock data. 
                        Production version requires database setup and full integration.
                    </p>
                </div>
            </div>
        </div>
        
        <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div class="bg-white p-6 rounded-lg shadow">
                <h3 class="text-lg font-semibold mb-4">Available Products</h3>
                <div class="space-y-4">
                    <div class="border-b pb-2">
                        <h4 class="font-medium">Premium Coffee</h4>
                        <p class="text-gray-600 text-sm">Monthly delivery</p>
                        <p class="text-green-600 font-bold">₹299/month</p>
                    </div>
                    <div class="border-b pb-2">
                        <h4 class="font-medium">Organic Snacks</h4>
                        <p class="text-gray-600 text-sm">Weekly delivery</p>
                        <p class="text-green-600 font-bold">₹199/week</p>
                    </div>
                    <div class="border-b pb-2">
                        <h4 class="font-medium">Book Club</h4>
                        <p class="text-gray-600 text-sm">Monthly books</p>
                        <p class="text-green-600 font-bold">₹999/month</p>
                    </div>
                </div>
            </div>
            
            <div class="bg-white p-6 rounded-lg shadow">
                <h3 class="text-lg font-semibold mb-4">API Endpoints</h3>
                <div class="space-y-2 text-sm">
                    <div><a href="/api/merchant/dashboard" class="text-blue-600 hover:underline">/api/merchant/dashboard</a></div>
                    <div><a href="/api/merchant/products" class="text-blue-600 hover:underline">/api/merchant/products</a></div>
                    <div><a href="/api/customer/subscriptions?user_id=1" class="text-blue-600 hover:underline">/api/customer/subscriptions</a></div>
                    <div><a href="/health" class="text-blue-600 hover:underline">/health</a></div>
                </div>
            </div>
            
            <div class="bg-white p-6 rounded-lg shadow">
                <h3 class="text-lg font-semibold mb-4">Quick Links</h3>
                <div class="space-y-2">
                    <div><a href="/merchant" class="text-blue-600 hover:underline">Merchant Dashboard</a></div>
                    <div><a href="/api/merchant/analytics/revenue" class="text-blue-600 hover:underline">Revenue Analytics</a></div>
                    <div><a href="/api/merchant/analytics/churn" class="text-blue-600 hover:underline">Churn Analytics</a></div>
                </div>
            </div>
        </div>
    </main>
</body>
</html>'''

@app.route('/merchant')
def merchant_dashboard_page():
    return '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Merchant Dashboard - SubscriptionPro</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
</head>
<body class="bg-gray-50">
    <header class="bg-white shadow-sm">
        <div class="max-w-7xl mx-auto px-4 py-4">
            <h1 class="text-2xl font-bold text-blue-600">SubscriptionPro Merchant Dashboard</h1>
        </div>
    </header>
    <main class="max-w-7xl mx-auto px-4 py-8">
        <div class="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
            <div class="bg-white p-6 rounded-lg shadow">
                <h3 class="text-sm text-gray-600">Active Subscriptions</h3>
                <p class="text-2xl font-semibold" id="active-subs">Loading...</p>
            </div>
            <div class="bg-white p-6 rounded-lg shadow">
                <h3 class="text-sm text-gray-600">Monthly Revenue</h3>
                <p class="text-2xl font-semibold" id="monthly-revenue">Loading...</p>
            </div>
            <div class="bg-white p-6 rounded-lg shadow">
                <h3 class="text-sm text-gray-600">New Subscribers</h3>
                <p class="text-2xl font-semibold" id="new-subs">Loading...</p>
            </div>
            <div class="bg-white p-6 rounded-lg shadow">
                <h3 class="text-sm text-gray-600">Churn Rate</h3>
                <p class="text-2xl font-semibold" id="churn-rate">Loading...</p>
            </div>
        </div>
        
        <div class="bg-white p-6 rounded-lg shadow">
            <h2 class="text-lg font-semibold mb-4">Revenue Trend (Last 30 Days)</h2>
            <canvas id="revenue-chart" width="400" height="200"></canvas>
        </div>
    </main>
    
    <script>
        // Load dashboard data
        fetch('/api/merchant/dashboard')
            .then(response => response.json())
            .then(data => {
                document.getElementById('active-subs').textContent = data.active_subscriptions;
                document.getElementById('monthly-revenue').textContent = '₹' + data.monthly_revenue.toLocaleString();
                document.getElementById('new-subs').textContent = data.new_subscriptions_30d;
                document.getElementById('churn-rate').textContent = data.churn_rate + '%';
            });
        
        // Load revenue chart
        fetch('/api/merchant/analytics/revenue')
            .then(response => response.json())
            .then(data => {
                const ctx = document.getElementById('revenue-chart').getContext('2d');
                new Chart(ctx, {
                    type: 'line',
                    data: {
                        labels: data.slice(0, 10).map(d => new Date(d.date).toLocaleDateString()),
                        datasets: [{
                            label: 'Revenue',
                            data: data.slice(0, 10).map(d => d.revenue),
                            borderColor: 'rgb(59, 130, 246)',
                            backgroundColor: 'rgba(59, 130, 246, 0.1)',
                            tension: 0.1
                        }]
                    },
                    options: {
                        responsive: true,
                        scales: {
                            y: {
                                beginAtZero: true
                            }
                        }
                    }
                });
            });
    </script>
</body>
</html>'''

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)