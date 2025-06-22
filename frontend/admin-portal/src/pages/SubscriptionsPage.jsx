import React, { useState, useEffect } from 'react';
import { useAdmin } from '../contexts/AdminContext';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Badge } from '@/components/ui/badge';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { 
  Table, 
  TableBody, 
  TableCell, 
  TableHead, 
  TableHeader, 
  TableRow 
} from '@/components/ui/table';
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
  Search, 
  Filter, 
  MoreHorizontal, 
  Edit, 
  Pause, 
  Play,
  X,
  Calendar,
  DollarSign,
  User,
  Package,
  Loader2,
  Clock
} from 'lucide-react';

const SubscriptionsPage = () => {
  const { subscriptions, loading, fetchSubscriptions, modifySubscription, extendSubscription } = useAdmin();
  const [statusFilter, setStatusFilter] = useState('');
  const [userEmailFilter, setUserEmailFilter] = useState('');
  const [selectedSubscription, setSelectedSubscription] = useState(null);
  const [showModifyDialog, setShowModifyDialog] = useState(false);
  const [modifyForm, setModifyForm] = useState({});
  const [extendDays, setExtendDays] = useState(30);
  const [error, setError] = useState('');
  const [currentPage, setCurrentPage] = useState(1);
  const [actionLoading, setActionLoading] = useState(null);

  useEffect(() => {
    loadSubscriptions();
  }, [currentPage, statusFilter, userEmailFilter]);

  const loadSubscriptions = async () => {
    const result = await fetchSubscriptions(currentPage, statusFilter, userEmailFilter);
    if (!result.success) {
      setError(result.error);
    }
  };

  const handleStatusFilter = (value) => {
    setStatusFilter(value === 'all' ? '' : value);
    setCurrentPage(1);
  };

  const handleUserEmailFilter = (e) => {
    setUserEmailFilter(e.target.value);
    setCurrentPage(1);
  };

  const handleModifySubscription = async () => {
    setActionLoading(selectedSubscription.subscription_id);
    setError('');

    const result = await modifySubscription(selectedSubscription.subscription_id, modifyForm);

    if (result.success) {
      setShowModifyDialog(false);
      setModifyForm({});
      loadSubscriptions();
    } else {
      setError(result.error);
    }

    setActionLoading(null);
  };

  const handleExtendSubscription = async () => {
    setActionLoading(selectedSubscription.subscription_id);
    setError('');

    const result = await extendSubscription(selectedSubscription.subscription_id, extendDays);

    if (result.success) {
      loadSubscriptions();
    } else {
      setError(result.error);
    }

    setActionLoading(null);
  };

  const openModifyDialog = (subscription) => {
    setSelectedSubscription(subscription);
    setModifyForm({
      status: subscription.status,
      quantity: subscription.quantity,
      frequency: subscription.frequency,
      next_delivery_date: subscription.next_delivery_date
    });
    setShowModifyDialog(true);
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

  if (loading && subscriptions.length === 0) {
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
        <h1 className="text-3xl font-bold">Subscriptions</h1>
        <p className="text-muted-foreground">
          Manage and monitor all subscription activities
        </p>
      </div>

      {error && (
        <Alert variant="destructive">
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      {/* Filters */}
      <Card>
        <CardHeader>
          <CardTitle>Filters</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex flex-col sm:flex-row gap-4">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
              <Input
                placeholder="Search by user email..."
                value={userEmailFilter}
                onChange={handleUserEmailFilter}
                className="pl-10"
              />
            </div>
            <Select value={statusFilter || 'all'} onValueChange={handleStatusFilter}>
              <SelectTrigger className="w-full sm:w-48">
                <Filter className="h-4 w-4 mr-2" />
                <SelectValue placeholder="Filter by status" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Status</SelectItem>
                <SelectItem value="active">Active</SelectItem>
                <SelectItem value="paused">Paused</SelectItem>
                <SelectItem value="canceled">Canceled</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </CardContent>
      </Card>

      {/* Subscriptions Table */}
      <Card>
        <CardHeader>
          <CardTitle>Subscription List</CardTitle>
          <CardDescription>
            {subscriptions.length} subscriptions found
          </CardDescription>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Subscription</TableHead>
                <TableHead>User</TableHead>
                <TableHead>Product</TableHead>
                <TableHead>Status</TableHead>
                <TableHead>Amount</TableHead>
                <TableHead>Next Delivery</TableHead>
                <TableHead>Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {subscriptions.map((subscription) => (
                <TableRow key={subscription.subscription_id}>
                  <TableCell>
                    <div>
                      <div className="font-medium">
                        {subscription.subscription_id}
                      </div>
                      <div className="text-sm text-muted-foreground">
                        {subscription.frequency} • Qty: {subscription.quantity}
                      </div>
                    </div>
                  </TableCell>
                  <TableCell>
                    <div className="flex items-center">
                      <User className="h-3 w-3 mr-1" />
                      <span className="text-sm">{subscription.user_email || 'N/A'}</span>
                    </div>
                  </TableCell>
                  <TableCell>
                    <div className="flex items-center">
                      <Package className="h-3 w-3 mr-1" />
                      <span className="text-sm">{subscription.product_name || 'Product'}</span>
                    </div>
                  </TableCell>
                  <TableCell>
                    <Badge className={getStatusColor(subscription.status)}>
                      {subscription.status}
                    </Badge>
                  </TableCell>
                  <TableCell>
                    <div className="flex items-center">
                      <DollarSign className="h-3 w-3 mr-1" />
                      <span className="text-sm">{formatCurrency(subscription.amount)}</span>
                    </div>
                  </TableCell>
                  <TableCell>
                    {subscription.next_delivery_date ? (
                      <div className="flex items-center">
                        <Calendar className="h-3 w-3 mr-1" />
                        <span className="text-sm">{formatDate(subscription.next_delivery_date)}</span>
                      </div>
                    ) : (
                      <span className="text-sm text-muted-foreground">N/A</span>
                    )}
                  </TableCell>
                  <TableCell>
                    <Dialog>
                      <DialogTrigger asChild>
                        <Button 
                          variant="ghost" 
                          size="sm"
                          onClick={() => setSelectedSubscription(subscription)}
                        >
                          <MoreHorizontal className="h-4 w-4" />
                        </Button>
                      </DialogTrigger>
                      <DialogContent className="max-w-2xl">
                        <DialogHeader>
                          <DialogTitle>Subscription Management</DialogTitle>
                          <DialogDescription>
                            Manage subscription details and perform admin actions
                          </DialogDescription>
                        </DialogHeader>
                        {selectedSubscription && (
                          <div className="space-y-6">
                            {/* Subscription Details */}
                            <div className="space-y-4">
                              <h3 className="text-lg font-medium">Subscription Details</h3>
                              <div className="grid grid-cols-2 gap-4">
                                <div>
                                  <Label>Subscription ID</Label>
                                  <div className="mt-1 text-sm">{selectedSubscription.subscription_id}</div>
                                </div>
                                <div>
                                  <Label>Status</Label>
                                  <div className="mt-1">
                                    <Badge className={getStatusColor(selectedSubscription.status)}>
                                      {selectedSubscription.status}
                                    </Badge>
                                  </div>
                                </div>
                                <div>
                                  <Label>Product</Label>
                                  <div className="mt-1 text-sm">{selectedSubscription.product_name || 'Product'}</div>
                                </div>
                                <div>
                                  <Label>Amount</Label>
                                  <div className="mt-1 text-sm">{formatCurrency(selectedSubscription.amount)}</div>
                                </div>
                                <div>
                                  <Label>Frequency</Label>
                                  <div className="mt-1 text-sm capitalize">{selectedSubscription.frequency}</div>
                                </div>
                                <div>
                                  <Label>Quantity</Label>
                                  <div className="mt-1 text-sm">{selectedSubscription.quantity}</div>
                                </div>
                                <div>
                                  <Label>Start Date</Label>
                                  <div className="mt-1 text-sm">{formatDate(selectedSubscription.start_date)}</div>
                                </div>
                                <div>
                                  <Label>Next Delivery</Label>
                                  <div className="mt-1 text-sm">
                                    {selectedSubscription.next_delivery_date 
                                      ? formatDate(selectedSubscription.next_delivery_date) 
                                      : 'N/A'
                                    }
                                  </div>
                                </div>
                              </div>
                            </div>

                            {/* Quick Actions */}
                            <div className="space-y-4">
                              <h3 className="text-lg font-medium">Quick Actions</h3>
                              <div className="flex flex-wrap gap-2">
                                <Button 
                                  variant="outline" 
                                  size="sm"
                                  onClick={() => openModifyDialog(selectedSubscription)}
                                >
                                  <Edit className="h-4 w-4 mr-2" />
                                  Modify
                                </Button>
                                <Button 
                                  variant="outline" 
                                  size="sm"
                                  onClick={handleExtendSubscription}
                                  disabled={actionLoading === selectedSubscription.subscription_id}
                                >
                                  {actionLoading === selectedSubscription.subscription_id ? (
                                    <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                                  ) : (
                                    <Clock className="h-4 w-4 mr-2" />
                                  )}
                                  Extend 30 Days
                                </Button>
                              </div>
                            </div>
                          </div>
                        )}
                      </DialogContent>
                    </Dialog>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>

          {subscriptions.length === 0 && !loading && (
            <div className="text-center py-8">
              <p className="text-muted-foreground">No subscriptions found</p>
            </div>
          )}

          {loading && (
            <div className="flex justify-center py-8">
              <Loader2 className="h-6 w-6 animate-spin" />
            </div>
          )}
        </CardContent>
      </Card>

      {/* Modify Subscription Dialog */}
      <Dialog open={showModifyDialog} onOpenChange={setShowModifyDialog}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Modify Subscription</DialogTitle>
            <DialogDescription>
              Update subscription details
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="status">Status</Label>
              <Select 
                value={modifyForm.status || ''} 
                onValueChange={(value) => setModifyForm({...modifyForm, status: value})}
              >
                <SelectTrigger>
                  <SelectValue placeholder="Select status" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="active">Active</SelectItem>
                  <SelectItem value="paused">Paused</SelectItem>
                  <SelectItem value="canceled">Canceled</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-2">
              <Label htmlFor="quantity">Quantity</Label>
              <Input
                id="quantity"
                type="number"
                min="1"
                value={modifyForm.quantity || ''}
                onChange={(e) => setModifyForm({
                  ...modifyForm, 
                  quantity: parseInt(e.target.value)
                })}
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="frequency">Frequency</Label>
              <Select 
                value={modifyForm.frequency || ''} 
                onValueChange={(value) => setModifyForm({...modifyForm, frequency: value})}
              >
                <SelectTrigger>
                  <SelectValue placeholder="Select frequency" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="weekly">Weekly</SelectItem>
                  <SelectItem value="monthly">Monthly</SelectItem>
                  <SelectItem value="quarterly">Quarterly</SelectItem>
                  <SelectItem value="yearly">Yearly</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-2">
              <Label htmlFor="next_delivery_date">Next Delivery Date</Label>
              <Input
                id="next_delivery_date"
                type="date"
                value={modifyForm.next_delivery_date || ''}
                onChange={(e) => setModifyForm({
                  ...modifyForm, 
                  next_delivery_date: e.target.value
                })}
              />
            </div>

            <Button onClick={handleModifySubscription} className="w-full">
              Save Changes
            </Button>
          </div>
        </DialogContent>
      </Dialog>

      {/* Pagination */}
      <div className="flex items-center justify-between">
        <div className="text-sm text-muted-foreground">
          Showing page {currentPage}
        </div>
        <div className="flex space-x-2">
          <Button 
            variant="outline" 
            size="sm"
            onClick={() => setCurrentPage(Math.max(1, currentPage - 1))}
            disabled={currentPage === 1}
          >
            Previous
          </Button>
          <Button 
            variant="outline" 
            size="sm"
            onClick={() => setCurrentPage(currentPage + 1)}
            disabled={subscriptions.length < 20}
          >
            Next
          </Button>
        </div>
      </div>
    </div>
  );
};

export default SubscriptionsPage;

