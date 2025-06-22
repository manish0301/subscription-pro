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
                    <a href="#" onclick="showDashboard()" class="text-gray-700 hover:text-blue-600 cursor-pointer">Dashboard</a>
                    <a href="#" onclick="showProducts()" class="text-gray-700 hover:text-blue-600 cursor-pointer">Products</a>
                    <a href="#" onclick="showSubscriptions()" class="text-gray-700 hover:text-blue-600 cursor-pointer">Subscriptions</a>
                    <a href="#" onclick="showUsers()" class="text-gray-700 hover:text-blue-600 cursor-pointer">Users</a>
                </nav>
            </div>
        </div>
    </header>

    <main class="max-w-7xl mx-auto py-6 px-4">
        <!-- Dashboard View -->
        <div id="dashboard-view">
            <div class="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
                <div class="bg-white p-6 rounded-lg shadow cursor-pointer hover:shadow-lg" onclick="showUsers()">
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
                
                <div class="bg-white p-6 rounded-lg shadow cursor-pointer hover:shadow-lg" onclick="showProducts()">
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
                
                <div class="bg-white p-6 rounded-lg shadow cursor-pointer hover:shadow-lg" onclick="showSubscriptions()">
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

            <div class="bg-white p-6 rounded-lg shadow">
                <h2 class="text-lg font-semibold mb-4">Quick Actions</h2>
                <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <button onclick="addProduct()" class="bg-blue-600 text-white py-3 px-4 rounded hover:bg-blue-700">
                        <i class="fas fa-plus mr-2"></i>Add Product
                    </button>
                    <button onclick="showUsers()" class="bg-green-600 text-white py-3 px-4 rounded hover:bg-green-700">
                        <i class="fas fa-users mr-2"></i>Manage Users
                    </button>
                    <button onclick="showReports()" class="bg-purple-600 text-white py-3 px-4 rounded hover:bg-purple-700">
                        <i class="fas fa-chart-bar mr-2"></i>View Reports
                    </button>
                </div>
            </div>
        </div>

        <!-- Products View -->
        <div id="products-view" class="hidden">
            <div class="bg-white p-6 rounded-lg shadow">
                <div class="flex justify-between items-center mb-4">
                    <h2 class="text-lg font-semibold">Products</h2>
                    <button onclick="addProduct()" class="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700">
                        <i class="fas fa-plus mr-2"></i>Add Product
                    </button>
                </div>
                <div id="products-content">Loading products...</div>
            </div>
        </div>

        <!-- Users View -->
        <div id="users-view" class="hidden">
            <div class="bg-white p-6 rounded-lg shadow">
                <div class="flex justify-between items-center mb-4">
                    <h2 class="text-lg font-semibold">Users</h2>
                    <button onclick="addUser()" class="bg-green-600 text-white px-4 py-2 rounded hover:bg-green-700">
                        <i class="fas fa-user-plus mr-2"></i>Add User
                    </button>
                </div>
                <div id="users-content">Loading users...</div>
            </div>
        </div>

        <!-- Subscriptions View -->
        <div id="subscriptions-view" class="hidden">
            <div class="bg-white p-6 rounded-lg shadow">
                <h2 class="text-lg font-semibold mb-4">Subscriptions</h2>
                <div id="subscriptions-content">Loading subscriptions...</div>
            </div>
        </div>
    </main>

    <script>
        // Navigation functions
        function showDashboard() {
            hideAllViews();
            document.getElementById('dashboard-view').classList.remove('hidden');
            loadDashboard();
        }

        function showProducts() {
            hideAllViews();
            document.getElementById('products-view').classList.remove('hidden');
            loadProducts();
        }

        function showUsers() {
            hideAllViews();
            document.getElementById('users-view').classList.remove('hidden');
            loadUsers();
        }

        function showSubscriptions() {
            hideAllViews();
            document.getElementById('subscriptions-view').classList.remove('hidden');
            loadSubscriptions();
        }

        function hideAllViews() {
            document.getElementById('dashboard-view').classList.add('hidden');
            document.getElementById('products-view').classList.add('hidden');
            document.getElementById('users-view').classList.add('hidden');
            document.getElementById('subscriptions-view').classList.add('hidden');
        }

        // Data loading functions
        async function loadDashboard() {
            try {
                const response = await fetch('/admin/dashboard');
                const data = await response.json();
                
                document.getElementById('total-users').textContent = '25';
                document.getElementById('total-products').textContent = '12';
                document.getElementById('active-subscriptions').textContent = '48';
                document.getElementById('total-revenue').textContent = '₹1,25,000';
            } catch (error) {
                console.error('Error loading dashboard:', error);
            }
        }

        async function loadProducts() {
            try {
                const response = await fetch('/products');
                const data = await response.json();
                
                document.getElementById('products-content').innerHTML = `
                    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                        <div class="border rounded-lg p-4">
                            <h3 class="font-semibold">Monthly Coffee Subscription</h3>
                            <p class="text-gray-600">Premium coffee delivered monthly</p>
                            <p class="text-lg font-bold text-green-600">₹299/month</p>
                        </div>
                        <div class="border rounded-lg p-4">
                            <h3 class="font-semibold">Weekly Snack Box</h3>
                            <p class="text-gray-600">Healthy snacks delivered weekly</p>
                            <p class="text-lg font-bold text-green-600">₹199/week</p>
                        </div>
                        <div class="border rounded-lg p-4">
                            <h3 class="font-semibold">Book Club Subscription</h3>
                            <p class="text-gray-600">Curated books delivered monthly</p>
                            <p class="text-lg font-bold text-green-600">₹999/month</p>
                        </div>
                    </div>
                `;
            } catch (error) {
                document.getElementById('products-content').innerHTML = 'Error loading products';
            }
        }

        async function loadUsers() {
            try {
                const response = await fetch('/users');
                const data = await response.json();
                
                document.getElementById('users-content').innerHTML = `
                    <div class="overflow-x-auto">
                        <table class="min-w-full table-auto">
                            <thead class="bg-gray-50">
                                <tr>
                                    <th class="px-4 py-2 text-left">Name</th>
                                    <th class="px-4 py-2 text-left">Email</th>
                                    <th class="px-4 py-2 text-left">Role</th>
                                    <th class="px-4 py-2 text-left">Status</th>
                                </tr>
                            </thead>
                            <tbody>
                                <tr class="border-t">
                                    <td class="px-4 py-2">John Doe</td>
                                    <td class="px-4 py-2">john@example.com</td>
                                    <td class="px-4 py-2">Customer</td>
                                    <td class="px-4 py-2"><span class="bg-green-100 text-green-800 px-2 py-1 rounded text-sm">Active</span></td>
                                </tr>
                                <tr class="border-t">
                                    <td class="px-4 py-2">Jane Smith</td>
                                    <td class="px-4 py-2">jane@example.com</td>
                                    <td class="px-4 py-2">Customer</td>
                                    <td class="px-4 py-2"><span class="bg-green-100 text-green-800 px-2 py-1 rounded text-sm">Active</span></td>
                                </tr>
                            </tbody>
                        </table>
                    </div>
                `;
            } catch (error) {
                document.getElementById('users-content').innerHTML = 'Error loading users';
            }
        }

        async function loadSubscriptions() {
            try {
                const response = await fetch('/subscriptions');
                const data = await response.json();
                
                document.getElementById('subscriptions-content').innerHTML = `
                    <div class="space-y-4">
                        <div class="border rounded-lg p-4">
                            <div class="flex justify-between items-center">
                                <div>
                                    <h3 class="font-semibold">Monthly Coffee - John Doe</h3>
                                    <p class="text-gray-600">Next delivery: Jan 15, 2025</p>
                                </div>
                                <span class="bg-green-100 text-green-800 px-3 py-1 rounded">Active</span>
                            </div>
                        </div>
                        <div class="border rounded-lg p-4">
                            <div class="flex justify-between items-center">
                                <div>
                                    <h3 class="font-semibold">Weekly Snacks - Jane Smith</h3>
                                    <p class="text-gray-600">Next delivery: Jan 10, 2025</p>
                                </div>
                                <span class="bg-yellow-100 text-yellow-800 px-3 py-1 rounded">Paused</span>
                            </div>
                        </div>
                    </div>
                `;
            } catch (error) {
                document.getElementById('subscriptions-content').innerHTML = 'Error loading subscriptions';
            }
        }

        // Action functions
        function addProduct() {
            alert('Add Product functionality - Connect to your product management system');
        }

        function addUser() {
            alert('Add User functionality - Connect to your user management system');
        }

        function showReports() {
            alert('Reports functionality - Connect to your analytics system');
        }
        
        // Initialize dashboard on load
        document.addEventListener('DOMContentLoaded', function() {
            loadDashboard();
        });
    </script>
</body>
</html>'''
        
        self.wfile.write(html.encode())
    
    def get_users(self):
        return {
            "message": "Users endpoint ready for Supabase integration",
            "status": "configured",
            "sample_data": [
                {"user_id": "1", "email": "john@example.com", "name": "John Doe", "role": "customer"},
                {"user_id": "2", "email": "jane@example.com", "name": "Jane Smith", "role": "customer"}
            ]
        }
    
    def get_products(self):
        return {
            "message": "Products endpoint ready for Supabase integration", 
            "status": "configured",
            "sample_data": [
                {"product_id": "1", "name": "Monthly Coffee", "price": 299, "currency": "INR"},
                {"product_id": "2", "name": "Weekly Snacks", "price": 199, "currency": "INR"}
            ]
        }
    
    def get_subscriptions(self):
        return {
            "message": "Subscriptions endpoint ready for Supabase integration",
            "status": "configured",
            "sample_data": [
                {"subscription_id": "1", "user_id": "1", "product_id": "1", "status": "active"},
                {"subscription_id": "2", "user_id": "2", "product_id": "2", "status": "paused"}
            ]
        }
    
    def get_dashboard(self):
        return {
            "message": "Admin dashboard ready for Supabase integration",
            "status": "configured",
            "metrics": {
                "total_users": 25,
                "total_products": 12,
                "active_subscriptions": 48,
                "total_revenue": 125000
            }
        }