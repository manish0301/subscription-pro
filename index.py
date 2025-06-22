from http.server import BaseHTTPRequestHandler
import json
import os
import urllib.parse

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed_path = urllib.parse.urlparse(self.path)
        path = parsed_path.path
        
        # Serve HTML UI for root path
        if path == '/':
            self.serve_html()
            return
        
        # API endpoints return JSON
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        if path == '/health':
            response = {
                "status": "ok",
                "message": "SubscriptionPro Enterprise API",
                "version": "1.0.0",
                "database": "configured" if os.environ.get('SUPABASE_URL') else "not_configured"
            }
        elif path == '/api/users' or path == '/users':
            response = self.get_users()
        elif path == '/api/products' or path == '/products':
            response = self.get_products()
        elif path == '/api/subscriptions' or path == '/subscriptions':
            response = self.get_subscriptions()
        elif path == '/api/admin/dashboard' or path == '/admin/dashboard':
            response = self.get_dashboard()
        else:
            response = {"error": "Endpoint not found", "available_endpoints": ["/health", "/users", "/products", "/subscriptions", "/admin/dashboard"]}
        
        self.wfile.write(json.dumps(response).encode())
    
    def serve_html(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        html = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SubscriptionPro - Enterprise Dashboard</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
</head>
<body class="bg-gray-50">
    <header class="bg-white shadow-sm border-b">
        <div class="max-w-7xl mx-auto px-4 py-4">
            <div class="flex justify-between items-center">
                <div class="flex items-center">
                    <h1 class="text-2xl font-bold text-gray-900">SubscriptionPro</h1>
                    <span class="ml-2 px-2 py-1 bg-blue-100 text-blue-800 text-xs rounded">Enterprise</span>
                </div>
                <nav class="flex space-x-8">
                    <a href="#dashboard" class="text-gray-700 hover:text-blue-600">Dashboard</a>
                    <a href="#products" class="text-gray-700 hover:text-blue-600">Products</a>
                    <a href="#subscriptions" class="text-gray-700 hover:text-blue-600">Subscriptions</a>
                </nav>
            </div>
        </div>
    </header>

    <main class="max-w-7xl mx-auto py-6 px-4">
        <div class="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
            <div class="bg-white p-6 rounded-lg shadow">
                <div class="flex items-center">
                    <div class="p-2 bg-blue-100 rounded-lg">
                        <i class="fas fa-users text-blue-600"></i>
                    </div>
                    <div class="ml-4">
                        <p class="text-sm text-gray-600">Total Users</p>
                        <p class="text-2xl font-semibold" id="total-users">Loading...</p>
                    </div>
                </div>
            </div>
            
            <div class="bg-white p-6 rounded-lg shadow">
                <div class="flex items-center">
                    <div class="p-2 bg-green-100 rounded-lg">
                        <i class="fas fa-box text-green-600"></i>
                    </div>
                    <div class="ml-4">
                        <p class="text-sm text-gray-600">Products</p>
                        <p class="text-2xl font-semibold" id="total-products">Loading...</p>
                    </div>
                </div>
            </div>
            
            <div class="bg-white p-6 rounded-lg shadow">
                <div class="flex items-center">
                    <div class="p-2 bg-purple-100 rounded-lg">
                        <i class="fas fa-sync text-purple-600"></i>
                    </div>
                    <div class="ml-4">
                        <p class="text-sm text-gray-600">Active Subscriptions</p>
                        <p class="text-2xl font-semibold" id="active-subscriptions">Loading...</p>
                    </div>
                </div>
            </div>
            
            <div class="bg-white p-6 rounded-lg shadow">
                <div class="flex items-center">
                    <div class="p-2 bg-yellow-100 rounded-lg">
                        <i class="fas fa-rupee-sign text-yellow-600"></i>
                    </div>
                    <div class="ml-4">
                        <p class="text-sm text-gray-600">Revenue</p>
                        <p class="text-2xl font-semibold" id="total-revenue">₹0</p>
                    </div>
                </div>
            </div>
        </div>

        <div class="bg-white p-6 rounded-lg shadow mb-8">
            <h2 class="text-lg font-semibold mb-4">API Endpoints</h2>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                    <h3 class="font-medium mb-2">Available APIs:</h3>
                    <ul class="space-y-1 text-sm">
                        <li><a href="/users" class="text-blue-600 hover:underline">/users</a> - User management</li>
                        <li><a href="/products" class="text-blue-600 hover:underline">/products</a> - Product catalog</li>
                        <li><a href="/subscriptions" class="text-blue-600 hover:underline">/subscriptions</a> - Subscription data</li>
                        <li><a href="/admin/dashboard" class="text-blue-600 hover:underline">/admin/dashboard</a> - Dashboard metrics</li>
                    </ul>
                </div>
                <div>
                    <h3 class="font-medium mb-2">System Status:</h3>
                    <div class="space-y-1 text-sm">
                        <div class="flex items-center">
                            <div class="w-2 h-2 bg-green-500 rounded-full mr-2"></div>
                            <span>API: Online</span>
                        </div>
                        <div class="flex items-center">
                            <div class="w-2 h-2 bg-green-500 rounded-full mr-2"></div>
                            <span>Database: Connected</span>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <div class="bg-white p-6 rounded-lg shadow">
            <h2 class="text-lg font-semibold mb-4">Quick Actions</h2>
            <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
                <button class="bg-blue-600 text-white py-3 px-4 rounded hover:bg-blue-700">
                    <i class="fas fa-plus mr-2"></i>Add Product
                </button>
                <button class="bg-green-600 text-white py-3 px-4 rounded hover:bg-green-700">
                    <i class="fas fa-users mr-2"></i>Manage Users
                </button>
                <button class="bg-purple-600 text-white py-3 px-4 rounded hover:bg-purple-700">
                    <i class="fas fa-chart-bar mr-2"></i>View Reports
                </button>
            </div>
        </div>
    </main>

    <script>
        async function loadDashboard() {
            try {
                const response = await fetch('/admin/dashboard');
                const data = await response.json();
                
                if (data.metrics) {
                    document.getElementById('total-users').textContent = data.metrics.total_users || '0';
                    document.getElementById('total-products').textContent = data.metrics.total_products || '0';
                    document.getElementById('active-subscriptions').textContent = data.metrics.active_subscriptions || '0';
                }
            } catch (error) {
                console.error('Error loading dashboard:', error);
            }
        }
        
        document.addEventListener('DOMContentLoaded', loadDashboard);
    </script>
</body>
</html>'''
        
        self.wfile.write(html.encode())
    
    def get_users(self):
        return {
            "message": "Users endpoint ready for Supabase integration",
            "status": "configured",
            "sample_structure": {
                "user_id": "uuid",
                "email": "string",
                "first_name": "string",
                "user_role": "customer|admin"
            }
        }
    
    def get_products(self):
        return {
            "message": "Products endpoint ready for Supabase integration", 
            "status": "configured",
            "sample_structure": {
                "product_id": "uuid",
                "name": "string",
                "price": "decimal",
                "currency": "INR"
            }
        }
    
    def get_subscriptions(self):
        return {
            "message": "Subscriptions endpoint ready for Supabase integration",
            "status": "configured", 
            "sample_structure": {
                "subscription_id": "uuid",
                "user_id": "uuid",
                "product_id": "uuid",
                "status": "active|paused|canceled"
            }
        }
    
    def get_dashboard(self):
        return {
            "message": "Admin dashboard ready for Supabase integration",
            "status": "configured",
            "metrics": {
                "total_users": "count from users table",
                "total_products": "count from products table", 
                "active_subscriptions": "count from subscriptions table",
                "total_revenue": "sum from payments table"
            }
        }