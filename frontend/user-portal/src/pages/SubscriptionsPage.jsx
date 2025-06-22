import React, { useState } from 'react';
import { useSubscription } from '../contexts/SubscriptionContext';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { 
  Dialog, 
  DialogContent, 
  DialogDescription, 
  DialogHeader, 
  DialogTitle, 
  DialogTrigger 
} from '@/components/ui/dialog';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { 
  Package, 
  Calendar, 
  Play, 
  Pause, 
  X, 
  SkipForward,
  Edit,
  Loader2
} from 'lucide-react';

const SubscriptionsPage = () => {
  const { 
    subscriptions, 
    loading, 
    pauseSubscription, 
    resumeSubscription, 
    cancelSubscription, 
    skipNextDelivery,
    updateSubscription 
  } = useSubscription();
  
  const [actionLoading, setActionLoading] = useState(null);
  const [editingSubscription, setEditingSubscription] = useState(null);
  const [editForm, setEditForm] = useState({});
  const [error, setError] = useState('');

  const handleAction = async (action, subscriptionId) => {
    setActionLoading(subscriptionId);
    setError('');

    let result;
    switch (action) {
      case 'pause':
        result = await pauseSubscription(subscriptionId);
        break;
      case 'resume':
        result = await resumeSubscription(subscriptionId);
        break;
      case 'cancel':
        result = await cancelSubscription(subscriptionId);
        break;
      case 'skip':
        result = await skipNextDelivery(subscriptionId);
        break;
      default:
        result = { success: false, error: 'Unknown action' };
    }

    if (!result.success) {
      setError(result.error);
    }

    setActionLoading(null);
  };

  const handleEdit = (subscription) => {
    setEditingSubscription(subscription);
    setEditForm({
      quantity: subscription.quantity,
      next_delivery_date: subscription.next_delivery_date
    });
  };

  const handleSaveEdit = async () => {
    setActionLoading(editingSubscription.subscription_id);
    setError('');

    const result = await updateSubscription(editingSubscription.subscription_id, editForm);

    if (result.success) {
      setEditingSubscription(null);
      setEditForm({});
    } else {
      setError(result.error);
    }

    setActionLoading(null);
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'active':
        return 'bg-green-100 text-green-800';
      case 'paused':
        return 'bg-yellow-100 text-yellow-800';
      case 'canceled':
        return 'bg-red-100 text-red-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR'
    }).format(amount);
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-IN', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    });
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-primary"></div>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="space-y-2">
        <h1 className="text-3xl font-bold">My Subscriptions</h1>
        <p className="text-muted-foreground">
          Manage your active subscriptions and delivery schedules
        </p>
      </div>

      {error && (
        <Alert variant="destructive">
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      {/* Subscriptions List */}
      {subscriptions.length > 0 ? (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {subscriptions.map((subscription) => (
            <Card key={subscription.subscription_id} className="relative">
              <CardHeader>
                <div className="flex items-start justify-between">
                  <div>
                    <CardTitle className="text-lg">
                      {subscription.product_name || 'Product'}
                    </CardTitle>
                    <CardDescription>
                      {subscription.plan_name || 'Subscription Plan'}
                    </CardDescription>
                  </div>
                  <Badge className={getStatusColor(subscription.status)}>
                    {subscription.status}
                  </Badge>
                </div>
              </CardHeader>
              <CardContent className="space-y-4">
                {/* Subscription Details */}
                <div className="grid grid-cols-2 gap-4 text-sm">
                  <div>
                    <span className="text-muted-foreground">Amount:</span>
                    <div className="font-medium">{formatCurrency(subscription.amount)}</div>
                  </div>
                  <div>
                    <span className="text-muted-foreground">Frequency:</span>
                    <div className="font-medium capitalize">{subscription.frequency}</div>
                  </div>
                  <div>
                    <span className="text-muted-foreground">Quantity:</span>
                    <div className="font-medium">{subscription.quantity}</div>
                  </div>
                  <div>
                    <span className="text-muted-foreground">Start Date:</span>
                    <div className="font-medium">{formatDate(subscription.start_date)}</div>
                  </div>
                </div>

                {subscription.next_delivery_date && (
                  <div className="flex items-center space-x-2 p-3 bg-muted/50 rounded-lg">
                    <Calendar className="h-4 w-4 text-muted-foreground" />
                    <span className="text-sm">
                      Next delivery: <strong>{formatDate(subscription.next_delivery_date)}</strong>
                    </span>
                  </div>
                )}

                {/* Action Buttons */}
                <div className="flex flex-wrap gap-2">
                  {subscription.status === 'active' && (
                    <>
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => handleAction('pause', subscription.subscription_id)}
                        disabled={actionLoading === subscription.subscription_id}
                      >
                        {actionLoading === subscription.subscription_id ? (
                          <Loader2 className="h-4 w-4 animate-spin" />
                        ) : (
                          <Pause className="h-4 w-4" />
                        )}
                        Pause
                      </Button>
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => handleAction('skip', subscription.subscription_id)}
                        disabled={actionLoading === subscription.subscription_id}
                      >
                        <SkipForward className="h-4 w-4" />
                        Skip Next
                      </Button>
                    </>
                  )}

                  {subscription.status === 'paused' && (
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={() => handleAction('resume', subscription.subscription_id)}
                      disabled={actionLoading === subscription.subscription_id}
                    >
                      {actionLoading === subscription.subscription_id ? (
                        <Loader2 className="h-4 w-4 animate-spin" />
                      ) : (
                        <Play className="h-4 w-4" />
                      )}
                      Resume
                    </Button>
                  )}

                  {subscription.status !== 'canceled' && (
                    <>
                      <Dialog>
                        <DialogTrigger asChild>
                          <Button
                            size="sm"
                            variant="outline"
                            onClick={() => handleEdit(subscription)}
                          >
                            <Edit className="h-4 w-4" />
                            Edit
                          </Button>
                        </DialogTrigger>
                        <DialogContent>
                          <DialogHeader>
                            <DialogTitle>Edit Subscription</DialogTitle>
                            <DialogDescription>
                              Modify your subscription details
                            </DialogDescription>
                          </DialogHeader>
                          <div className="space-y-4">
                            <div className="space-y-2">
                              <Label htmlFor="quantity">Quantity</Label>
                              <Input
                                id="quantity"
                                type="number"
                                min="1"
                                value={editForm.quantity || ''}
                                onChange={(e) => setEditForm({
                                  ...editForm,
                                  quantity: parseInt(e.target.value)
                                })}
                              />
                            </div>
                            <div className="space-y-2">
                              <Label htmlFor="next_delivery_date">Next Delivery Date</Label>
                              <Input
                                id="next_delivery_date"
                                type="date"
                                value={editForm.next_delivery_date || ''}
                                onChange={(e) => setEditForm({
                                  ...editForm,
                                  next_delivery_date: e.target.value
                                })}
                              />
                            </div>
                            <Button onClick={handleSaveEdit} className="w-full">
                              Save Changes
                            </Button>
                          </div>
                        </DialogContent>
                      </Dialog>

                      <Button
                        size="sm"
                        variant="destructive"
                        onClick={() => handleAction('cancel', subscription.subscription_id)}
                        disabled={actionLoading === subscription.subscription_id}
                      >
                        {actionLoading === subscription.subscription_id ? (
                          <Loader2 className="h-4 w-4 animate-spin" />
                        ) : (
                          <X className="h-4 w-4" />
                        )}
                        Cancel
                      </Button>
                    </>
                  )}
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      ) : (
        <Card>
          <CardContent className="text-center py-12">
            <Package className="h-16 w-16 text-muted-foreground mx-auto mb-4" />
            <h3 className="text-lg font-medium mb-2">No subscriptions yet</h3>
            <p className="text-muted-foreground mb-6">
              Start your first subscription to see it here
            </p>
            <Button>Browse Products</Button>
          </CardContent>
        </Card>
      )}
    </div>
  );
};

export default SubscriptionsPage;

