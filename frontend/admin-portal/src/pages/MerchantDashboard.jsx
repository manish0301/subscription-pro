import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../components/ui/tabs';
import { Button } from '../components/ui/button';
import { Badge } from '../components/ui/badge';
import { 
  TrendingUp, 
  Users, 
  Package, 
  CreditCard, 
  Calendar,
  AlertTriangle,
  CheckCircle,
  Clock,
  DollarSign,
  BarChart3,
  Settings,
  Download
} from 'lucide-react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, BarChart, Bar, PieChart, Pie, Cell } from 'recharts';
import { apiRequest, API_ENDPOINTS } from '../config/api';

const MerchantDashboard = () => {
  const [dashboardData, setDashboardData] = useState(null);
  const [subscriptions, setSubscriptions] = useState([]);
  const [analytics, setAnalytics] = useState(null);
  const [loading, setLoading] = useState(true);
  const [timeRange, setTimeRange] = useState('30d');

  useEffect(() => {
    fetchDashboardData();
    fetchSubscriptions();
    fetchAnalytics();
  }, [timeRange]);

  const fetchDashboardData = async () => {
    try {
      const response = await apiRequest(API_ENDPOINTS.ADMIN_DASHBOARD);
      if (response.success) {
        setDashboardData(response.metrics);
      }
    } catch (error) {
      console.error('Failed to fetch dashboard data:', error);
    }
  };

  const fetchSubscriptions = async () => {
    try {
      const response = await apiRequest(API_ENDPOINTS.SUBSCRIPTIONS);
      if (response.success) {
        setSubscriptions(response.subscriptions || []);
      }
    } catch (error) {
      console.error('Failed to fetch subscriptions:', error);
    }
  };

  const fetchAnalytics = async () => {
    try {
      const response = await apiRequest(API_ENDPOINTS.ADMIN_ANALYTICS);
      if (response.success) {
        setAnalytics(response.analytics);
      }
    } catch (error) {
      console.error('Failed to fetch analytics:', error);
    } finally {
      setLoading(false);
    }
  };

  // Mock data for charts (replace with real data)
  const revenueData = [
    { month: 'Jan', revenue: 45000, subscriptions: 120 },
    { month: 'Feb', revenue: 52000, subscriptions: 145 },
    { month: 'Mar', revenue: 48000, subscriptions: 135 },
    { month: 'Apr', revenue: 61000, subscriptions: 165 },
    { month: 'May', revenue: 55000, subscriptions: 155 },
    { month: 'Jun', revenue: 67000, subscriptions: 180 }
  ];

  const subscriptionStatusData = [
    { name: 'Active', value: 75, color: '#10B981' },
    { name: 'Paused', value: 15, color: '#F59E0B' },
    { name: 'Canceled', value: 10, color: '#EF4444' }
  ];

  const topProducts = [
    { name: 'Premium Coffee', subscriptions: 45, revenue: 67500 },
    { name: 'Organic Tea', subscriptions: 32, revenue: 28800 },
    { name: 'Skincare Kit', subscriptions: 28, revenue: 44800 },
    { name: 'Fitness Supplements', subscriptions: 22, revenue: 54978 }
  ];

  const recentSubscriptions = subscriptions.slice(0, 10);

  const getStatusBadge = (status) => {
    const statusConfig = {
      active: { variant: 'default', color: 'bg-green-100 text-green-800' },
      paused: { variant: 'secondary', color: 'bg-yellow-100 text-yellow-800' },
      canceled: { variant: 'destructive', color: 'bg-red-100 text-red-800' }
    };
    const config = statusConfig[status] || statusConfig.active;
    return (
      <Badge variant={config.variant} className={config.color}>
        {status.charAt(0).toUpperCase() + status.slice(1)}
      </Badge>
    );
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading dashboard...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Merchant Dashboard</h1>
          <p className="text-gray-600 mt-1">
            Monitor your subscription business performance
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Button variant="outline" size="sm">
            <Download className="h-4 w-4 mr-2" />
            Export Report
          </Button>
          <Button variant="outline" size="sm">
            <Settings className="h-4 w-4 mr-2" />
            Settings
          </Button>
        </div>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Total Revenue</p>
                <p className="text-2xl font-bold">₹{dashboardData?.total_revenue?.toLocaleString() || '0'}</p>
                <p className="text-xs text-green-600 flex items-center mt-1">
                  <TrendingUp className="h-3 w-3 mr-1" />
                  +12.5% from last month
                </p>
              </div>
              <DollarSign className="h-8 w-8 text-green-600" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Active Subscriptions</p>
                <p className="text-2xl font-bold">{dashboardData?.active_subscriptions || 0}</p>
                <p className="text-xs text-green-600 flex items-center mt-1">
                  <TrendingUp className="h-3 w-3 mr-1" />
                  +8.2% from last month
                </p>
              </div>
              <Users className="h-8 w-8 text-blue-600" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Total Customers</p>
                <p className="text-2xl font-bold">{dashboardData?.total_users || 0}</p>
                <p className="text-xs text-green-600 flex items-center mt-1">
                  <TrendingUp className="h-3 w-3 mr-1" />
                  +15.3% from last month
                </p>
              </div>
              <Package className="h-8 w-8 text-purple-600" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Churn Rate</p>
                <p className="text-2xl font-bold">2.4%</p>
                <p className="text-xs text-red-600 flex items-center mt-1">
                  <TrendingUp className="h-3 w-3 mr-1" />
                  +0.3% from last month
                </p>
              </div>
              <AlertTriangle className="h-8 w-8 text-red-600" />
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Main Content Tabs */}
      <Tabs defaultValue="overview" className="space-y-6">
        <TabsList className="grid w-full grid-cols-5">
          <TabsTrigger value="overview">Overview</TabsTrigger>
          <TabsTrigger value="subscriptions">Subscriptions</TabsTrigger>
          <TabsTrigger value="products">Products</TabsTrigger>
          <TabsTrigger value="customers">Customers</TabsTrigger>
          <TabsTrigger value="analytics">Analytics</TabsTrigger>
        </TabsList>

        <TabsContent value="overview" className="space-y-6">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Revenue Chart */}
            <Card>
              <CardHeader>
                <CardTitle>Revenue Trend</CardTitle>
              </CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={300}>
                  <LineChart data={revenueData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="month" />
                    <YAxis />
                    <Tooltip formatter={(value) => [`₹${value.toLocaleString()}`, 'Revenue']} />
                    <Line type="monotone" dataKey="revenue" stroke="#3B82F6" strokeWidth={2} />
                  </LineChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>

            {/* Subscription Status Distribution */}
            <Card>
              <CardHeader>
                <CardTitle>Subscription Status</CardTitle>
              </CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={300}>
                  <PieChart>
                    <Pie
                      data={subscriptionStatusData}
                      cx="50%"
                      cy="50%"
                      outerRadius={80}
                      dataKey="value"
                      label={({ name, value }) => `${name}: ${value}%`}
                    >
                      {subscriptionStatusData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={entry.color} />
                      ))}
                    </Pie>
                    <Tooltip />
                  </PieChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>
          </div>

          {/* Top Products */}
          <Card>
            <CardHeader>
              <CardTitle>Top Performing Products</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {topProducts.map((product, index) => (
                  <div key={index} className="flex items-center justify-between p-4 border rounded-lg">
                    <div className="flex items-center gap-4">
                      <div className="w-10 h-10 bg-primary/10 rounded-lg flex items-center justify-center">
                        <Package className="h-5 w-5 text-primary" />
                      </div>
                      <div>
                        <h4 className="font-medium">{product.name}</h4>
                        <p className="text-sm text-gray-600">{product.subscriptions} active subscriptions</p>
                      </div>
                    </div>
                    <div className="text-right">
                      <p className="font-bold">₹{product.revenue.toLocaleString()}</p>
                      <p className="text-sm text-gray-600">Monthly Revenue</p>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="subscriptions" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Recent Subscriptions</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {recentSubscriptions.map((subscription) => (
                  <div key={subscription.subscription_id} className="flex items-center justify-between p-4 border rounded-lg">
                    <div className="flex items-center gap-4">
                      <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center">
                        <Calendar className="h-5 w-5 text-blue-600" />
                      </div>
                      <div>
                        <h4 className="font-medium">{subscription.product?.name || 'Product'}</h4>
                        <p className="text-sm text-gray-600">
                          {subscription.frequency} • Qty: {subscription.quantity}
                        </p>
                      </div>
                    </div>
                    <div className="flex items-center gap-4">
                      <div className="text-right">
                        <p className="font-bold">₹{subscription.amount?.toLocaleString()}</p>
                        <p className="text-sm text-gray-600">per delivery</p>
                      </div>
                      {getStatusBadge(subscription.status)}
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="products" className="space-y-6">
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <CardTitle>Product Performance</CardTitle>
                <Button>Add Product</Button>
              </div>
            </CardHeader>
            <CardContent>
              <div className="text-center py-8">
                <Package className="h-12 w-12 mx-auto text-gray-400 mb-4" />
                <h3 className="text-lg font-medium mb-2">Product Management</h3>
                <p className="text-gray-600">Configure subscription products and pricing</p>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="customers" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Customer Management</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-center py-8">
                <Users className="h-12 w-12 mx-auto text-gray-400 mb-4" />
                <h3 className="text-lg font-medium mb-2">Customer Insights</h3>
                <p className="text-gray-600">View and manage customer subscriptions</p>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="analytics" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Advanced Analytics</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-center py-8">
                <BarChart3 className="h-12 w-12 mx-auto text-gray-400 mb-4" />
                <h3 className="text-lg font-medium mb-2">Business Intelligence</h3>
                <p className="text-gray-600">Deep insights into subscription performance</p>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default MerchantDashboard;
