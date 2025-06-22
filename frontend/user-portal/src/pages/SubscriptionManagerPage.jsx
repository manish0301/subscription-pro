import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Badge } from '../components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../components/ui/tabs';
import { 
  Calendar, 
  CreditCard, 
  Package, 
  Pause, 
  Play, 
  X, 
  Edit3, 
  Truck,
  Clock,
  AlertCircle,
  CheckCircle
} from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';
import { apiRequest, API_ENDPOINTS } from '../config/api';

const SubscriptionManagerPage = () => {
  const { user } = useAuth();
  const [subscriptions, setSubscriptions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedSubscription, setSelectedSubscription] = useState(null);
  const [actionLoading, setActionLoading] = useState(false);

  useEffect(() => {
    fetchSubscriptions();
  }, []);

  const fetchSubscriptions = async () => {
    try {
      setLoading(true);
      const response = await apiRequest(API_ENDPOINTS.SUBSCRIPTIONS);
      if (response.success) {
        setSubscriptions(response.subscriptions || []);
      }
    } catch (error) {
      console.error('Failed to fetch subscriptions:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSubscriptionAction = async (subscriptionId, action, data = {}) => {
    try {
      setActionLoading(true);
      
      let endpoint = `${API_ENDPOINTS.SUBSCRIPTIONS}/${subscriptionId}`;
      let method = 'PUT';
      let payload = { ...data };

      switch (action) {
        case 'pause':
          payload.status = 'paused';
          break;
        case 'resume':
          payload.status = 'active';
          break;
        case 'cancel':
          payload.status = 'canceled';
          break;
        case 'skip':
          // Calculate next delivery date
          const subscription = subscriptions.find(s => s.subscription_id === subscriptionId);
          const nextDate = new Date(subscription.next_delivery_date);
          
          if (subscription.frequency === 'weekly') {
            nextDate.setDate(nextDate.getDate() + 7);
          } else if (subscription.frequency === 'monthly') {
            nextDate.setMonth(nextDate.getMonth() + 1);
          } else if (subscription.frequency === 'quarterly') {
            nextDate.setMonth(nextDate.getMonth() + 3);
          }
          
          payload.next_delivery_date = nextDate.toISOString().split('T')[0];
          break;
        case 'update':
          // payload already contains the update data
          break;
      }

      const response = await apiRequest(endpoint, {
        method: method,
        body: JSON.stringify(payload)
      });

      if (response.success) {
        await fetchSubscriptions(); // Refresh the list
        setSelectedSubscription(null);
      }
    } catch (error) {
      console.error(`Failed to ${action} subscription:`, error);
    } finally {
      setActionLoading(false);
    }
  };

  const getStatusBadge = (status) => {
    const statusConfig = {
      active: { variant: 'default', color: 'bg-green-100 text-green-800', icon: CheckCircle },
      paused: { variant: 'secondary', color: 'bg-yellow-100 text-yellow-800', icon: Pause },
      canceled: { variant: 'destructive', color: 'bg-red-100 text-red-800', icon: X },
      completed: { variant: 'outline', color: 'bg-gray-100 text-gray-800', icon: CheckCircle }
    };

    const config = statusConfig[status] || statusConfig.active;
    const Icon = config.icon;

    return (
      <Badge variant={config.variant} className={config.color}>
        <Icon className="h-3 w-3 mr-1" />
        {status.charAt(0).toUpperCase() + status.slice(1)}
      </Badge>
    );
  };

  const getNextDeliveryStatus = (nextDeliveryDate, status) => {
    if (status !== 'active') return null;
    
    const today = new Date();
    const deliveryDate = new Date(nextDeliveryDate);
    const diffTime = deliveryDate - today;
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));

    if (diffDays < 0) {
      return { text: 'Overdue', color: 'text-red-600', icon: AlertCircle };
    } else if (diffDays === 0) {
      return { text: 'Today', color: 'text-blue-600', icon: Truck };
    } else if (diffDays === 1) {
      return { text: 'Tomorrow', color: 'text-blue-600', icon: Truck };
    } else if (diffDays <= 7) {
      return { text: `In ${diffDays} days`, color: 'text-green-600', icon: Calendar };
    } else {
      return { text: `In ${diffDays} days`, color: 'text-gray-600', icon: Calendar };
    }
  };

  const SubscriptionCard = ({ subscription }) => {
    const nextDelivery = getNextDeliveryStatus(subscription.next_delivery_date, subscription.status);
    
    return (
      <Card className="hover:shadow-md transition-shadow">
        <CardHeader className="pb-3">
          <div className="flex items-start justify-between">
            <div className="space-y-1">
              <CardTitle className="text-lg">{subscription.product?.name || 'Product'}</CardTitle>
              <div className="flex items-center gap-2">
                {getStatusBadge(subscription.status)}
                <Badge variant="outline">
                  {subscription.frequency}
                </Badge>
              </div>
            </div>
            <div className="text-right">
              <div className="text-2xl font-bold">₹{subscription.amount?.toLocaleString()}</div>
              <div className="text-sm text-gray-600">per delivery</div>
            </div>
          </div>
        </CardHeader>
        
        <CardContent className="space-y-4">
          {/* Next Delivery */}
          {nextDelivery && (
            <div className="flex items-center gap-2 p-3 bg-blue-50 rounded-lg">
              <nextDelivery.icon className={`h-4 w-4 ${nextDelivery.color}`} />
              <span className="text-sm font-medium">Next delivery: </span>
              <span className={`text-sm font-bold ${nextDelivery.color}`}>
                {nextDelivery.text} ({new Date(subscription.next_delivery_date).toLocaleDateString()})
              </span>
            </div>
          )}

          {/* Subscription Details */}
          <div className="grid grid-cols-2 gap-4 text-sm">
            <div>
              <span className="text-gray-600">Quantity:</span>
              <span className="ml-2 font-medium">{subscription.quantity}</span>
            </div>
            <div>
              <span className="text-gray-600">Started:</span>
              <span className="ml-2 font-medium">
                {new Date(subscription.start_date).toLocaleDateString()}
              </span>
            </div>
          </div>

          {/* Action Buttons */}
          <div className="flex flex-wrap gap-2 pt-2">
            {subscription.status === 'active' && (
              <>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => handleSubscriptionAction(subscription.subscription_id, 'pause')}
                  disabled={actionLoading}
                >
                  <Pause className="h-4 w-4 mr-1" />
                  Pause
                </Button>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => handleSubscriptionAction(subscription.subscription_id, 'skip')}
                  disabled={actionLoading}
                >
                  <Clock className="h-4 w-4 mr-1" />
                  Skip Next
                </Button>
              </>
            )}
            
            {subscription.status === 'paused' && (
              <Button
                variant="outline"
                size="sm"
                onClick={() => handleSubscriptionAction(subscription.subscription_id, 'resume')}
                disabled={actionLoading}
              >
                <Play className="h-4 w-4 mr-1" />
                Resume
              </Button>
            )}
            
            <Button
              variant="outline"
              size="sm"
              onClick={() => setSelectedSubscription(subscription)}
            >
              <Edit3 className="h-4 w-4 mr-1" />
              Modify
            </Button>
            
            {subscription.status !== 'canceled' && (
              <Button
                variant="destructive"
                size="sm"
                onClick={() => handleSubscriptionAction(subscription.subscription_id, 'cancel')}
                disabled={actionLoading}
              >
                <X className="h-4 w-4 mr-1" />
                Cancel
              </Button>
            )}
          </div>
        </CardContent>
      </Card>
    );
  };

  const activeSubscriptions = subscriptions.filter(s => s.status === 'active');
  const pausedSubscriptions = subscriptions.filter(s => s.status === 'paused');
  const canceledSubscriptions = subscriptions.filter(s => s.status === 'canceled');

  if (loading) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="flex items-center justify-center h-64">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto"></div>
            <p className="mt-4 text-gray-600">Loading your subscriptions...</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold">My Subscriptions</h1>
            <p className="text-gray-600 mt-1">
              Manage your recurring deliveries and save money
            </p>
          </div>
          <div className="text-right">
            <div className="text-2xl font-bold">{subscriptions.length}</div>
            <div className="text-sm text-gray-600">Total Subscriptions</div>
          </div>
        </div>

        {/* Summary Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <Card>
            <CardContent className="p-4 text-center">
              <div className="text-2xl font-bold text-green-600">{activeSubscriptions.length}</div>
              <div className="text-sm text-gray-600">Active</div>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="p-4 text-center">
              <div className="text-2xl font-bold text-yellow-600">{pausedSubscriptions.length}</div>
              <div className="text-sm text-gray-600">Paused</div>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="p-4 text-center">
              <div className="text-2xl font-bold text-red-600">{canceledSubscriptions.length}</div>
              <div className="text-sm text-gray-600">Canceled</div>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="p-4 text-center">
              <div className="text-2xl font-bold text-blue-600">
                ₹{subscriptions.reduce((total, sub) => total + (sub.amount || 0), 0).toLocaleString()}
              </div>
              <div className="text-sm text-gray-600">Monthly Value</div>
            </CardContent>
          </Card>
        </div>

        {/* Subscriptions Tabs */}
        <Tabs defaultValue="active" className="space-y-6">
          <TabsList className="grid w-full grid-cols-3">
            <TabsTrigger value="active">
              Active ({activeSubscriptions.length})
            </TabsTrigger>
            <TabsTrigger value="paused">
              Paused ({pausedSubscriptions.length})
            </TabsTrigger>
            <TabsTrigger value="canceled">
              Canceled ({canceledSubscriptions.length})
            </TabsTrigger>
          </TabsList>

          <TabsContent value="active" className="space-y-4">
            {activeSubscriptions.length > 0 ? (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {activeSubscriptions.map((subscription) => (
                  <SubscriptionCard key={subscription.subscription_id} subscription={subscription} />
                ))}
              </div>
            ) : (
              <Card>
                <CardContent className="p-8 text-center">
                  <Package className="h-12 w-12 mx-auto text-gray-400 mb-4" />
                  <h3 className="text-lg font-medium mb-2">No active subscriptions</h3>
                  <p className="text-gray-600 mb-4">Start saving with a subscription today!</p>
                  <Button>Browse Products</Button>
                </CardContent>
              </Card>
            )}
          </TabsContent>

          <TabsContent value="paused" className="space-y-4">
            {pausedSubscriptions.length > 0 ? (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {pausedSubscriptions.map((subscription) => (
                  <SubscriptionCard key={subscription.subscription_id} subscription={subscription} />
                ))}
              </div>
            ) : (
              <Card>
                <CardContent className="p-8 text-center">
                  <Pause className="h-12 w-12 mx-auto text-gray-400 mb-4" />
                  <h3 className="text-lg font-medium mb-2">No paused subscriptions</h3>
                  <p className="text-gray-600">All your subscriptions are active or canceled.</p>
                </CardContent>
              </Card>
            )}
          </TabsContent>

          <TabsContent value="canceled" className="space-y-4">
            {canceledSubscriptions.length > 0 ? (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {canceledSubscriptions.map((subscription) => (
                  <SubscriptionCard key={subscription.subscription_id} subscription={subscription} />
                ))}
              </div>
            ) : (
              <Card>
                <CardContent className="p-8 text-center">
                  <CheckCircle className="h-12 w-12 mx-auto text-gray-400 mb-4" />
                  <h3 className="text-lg font-medium mb-2">No canceled subscriptions</h3>
                  <p className="text-gray-600">You haven't canceled any subscriptions yet.</p>
                </CardContent>
              </Card>
            )}
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
};

export default SubscriptionManagerPage;
