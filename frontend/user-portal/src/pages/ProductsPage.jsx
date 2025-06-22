import React, { useState } from 'react';
import { useSubscription } from '../contexts/SubscriptionContext';
import { useAuth } from '../contexts/AuthContext';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
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
  ShoppingCart, 
  Star, 
  Clock, 
  Loader2,
  Filter,
  Search
} from 'lucide-react';

const ProductsPage = () => {
  const { products, createSubscription } = useSubscription();
  const { isAuthenticated } = useAuth();
  const [selectedProduct, setSelectedProduct] = useState(null);
  const [subscriptionForm, setSubscriptionForm] = useState({
    frequency: 'monthly',
    quantity: 1,
    start_date: new Date().toISOString().split('T')[0]
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [searchTerm, setSearchTerm] = useState('');
  const [categoryFilter, setCategoryFilter] = useState('all');

  const handleSubscribe = async () => {
    if (!isAuthenticated) {
      setError('Please log in to create a subscription');
      return;
    }

    setLoading(true);
    setError('');

    const subscriptionData = {
      product_id: selectedProduct.product_id,
      plan_id: selectedProduct.plans?.[0]?.plan_id, // Use first plan if available
      frequency: subscriptionForm.frequency,
      quantity: subscriptionForm.quantity,
      start_date: subscriptionForm.start_date,
      amount: calculateAmount(selectedProduct, subscriptionForm.frequency)
    };

    const result = await createSubscription(subscriptionData);

    if (result.success) {
      setSelectedProduct(null);
      setSubscriptionForm({
        frequency: 'monthly',
        quantity: 1,
        start_date: new Date().toISOString().split('T')[0]
      });
    } else {
      setError(result.error);
    }

    setLoading(false);
  };

  const calculateAmount = (product, frequency) => {
    const basePrice = parseFloat(product.price || 0);
    
    // Apply frequency-based pricing if available
    switch (frequency) {
      case 'weekly':
        return basePrice * 0.95; // 5% discount for weekly
      case 'monthly':
        return basePrice;
      case 'quarterly':
        return basePrice * 3 * 0.9; // 10% discount for quarterly
      case 'yearly':
        return basePrice * 12 * 0.8; // 20% discount for yearly
      default:
        return basePrice;
    }
  };

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR'
    }).format(amount);
  };

  const filteredProducts = products.filter(product => {
    const matchesSearch = product.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         product.description?.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesCategory = categoryFilter === 'all' || product.category === categoryFilter;
    
    return matchesSearch && matchesCategory;
  });

  const categories = [...new Set(products.map(product => product.category).filter(Boolean))];

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="space-y-2">
        <h1 className="text-3xl font-bold">Products</h1>
        <p className="text-muted-foreground">
          Discover and subscribe to our premium products
        </p>
      </div>

      {/* Filters */}
      <div className="flex flex-col sm:flex-row gap-4">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
          <Input
            placeholder="Search products..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="pl-10"
          />
        </div>
        <Select value={categoryFilter} onValueChange={setCategoryFilter}>
          <SelectTrigger className="w-full sm:w-48">
            <Filter className="h-4 w-4 mr-2" />
            <SelectValue placeholder="Category" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All Categories</SelectItem>
            {categories.map(category => (
              <SelectItem key={category} value={category}>
                {category}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>

      {error && (
        <Alert variant="destructive">
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      {/* Products Grid */}
      {filteredProducts.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredProducts.map((product) => (
            <Card key={product.product_id} className="relative overflow-hidden">
              {product.image_url && (
                <div className="aspect-video bg-muted">
                  <img
                    src={product.image_url}
                    alt={product.name}
                    className="w-full h-full object-cover"
                  />
                </div>
              )}
              
              <CardHeader>
                <div className="flex items-start justify-between">
                  <div>
                    <CardTitle className="text-lg">{product.name}</CardTitle>
                    {product.category && (
                      <Badge variant="secondary" className="mt-1">
                        {product.category}
                      </Badge>
                    )}
                  </div>
                  <div className="text-right">
                    <div className="text-2xl font-bold text-primary">
                      {formatCurrency(product.price)}
                    </div>
                    {product.subscription_only && (
                      <Badge variant="outline" className="mt-1">
                        Subscription Only
                      </Badge>
                    )}
                  </div>
                </div>
              </CardHeader>

              <CardContent className="space-y-4">
                <CardDescription className="line-clamp-3">
                  {product.description}
                </CardDescription>

                {/* Product Features */}
                {product.features && (
                  <div className="space-y-2">
                    <h4 className="font-medium text-sm">Features:</h4>
                    <ul className="text-sm text-muted-foreground space-y-1">
                      {product.features.slice(0, 3).map((feature, index) => (
                        <li key={index} className="flex items-center">
                          <Star className="h-3 w-3 mr-2 text-yellow-500" />
                          {feature}
                        </li>
                      ))}
                    </ul>
                  </div>
                )}

                {/* Subscription Options */}
                <div className="pt-4 border-t">
                  <Dialog>
                    <DialogTrigger asChild>
                      <Button 
                        className="w-full" 
                        onClick={() => setSelectedProduct(product)}
                        disabled={!isAuthenticated}
                      >
                        <ShoppingCart className="h-4 w-4 mr-2" />
                        {isAuthenticated ? 'Subscribe Now' : 'Login to Subscribe'}
                      </Button>
                    </DialogTrigger>
                    <DialogContent>
                      <DialogHeader>
                        <DialogTitle>Subscribe to {product.name}</DialogTitle>
                        <DialogDescription>
                          Choose your subscription preferences
                        </DialogDescription>
                      </DialogHeader>
                      
                      <div className="space-y-4">
                        <div className="space-y-2">
                          <Label htmlFor="frequency">Delivery Frequency</Label>
                          <Select 
                            value={subscriptionForm.frequency} 
                            onValueChange={(value) => setSubscriptionForm({
                              ...subscriptionForm,
                              frequency: value
                            })}
                          >
                            <SelectTrigger>
                              <SelectValue />
                            </SelectTrigger>
                            <SelectContent>
                              <SelectItem value="weekly">
                                Weekly - {formatCurrency(calculateAmount(product, 'weekly'))}
                              </SelectItem>
                              <SelectItem value="monthly">
                                Monthly - {formatCurrency(calculateAmount(product, 'monthly'))}
                              </SelectItem>
                              <SelectItem value="quarterly">
                                Quarterly - {formatCurrency(calculateAmount(product, 'quarterly'))}
                              </SelectItem>
                              <SelectItem value="yearly">
                                Yearly - {formatCurrency(calculateAmount(product, 'yearly'))}
                              </SelectItem>
                            </SelectContent>
                          </Select>
                        </div>

                        <div className="space-y-2">
                          <Label htmlFor="quantity">Quantity</Label>
                          <Input
                            id="quantity"
                            type="number"
                            min="1"
                            max="10"
                            value={subscriptionForm.quantity}
                            onChange={(e) => setSubscriptionForm({
                              ...subscriptionForm,
                              quantity: parseInt(e.target.value) || 1
                            })}
                          />
                        </div>

                        <div className="space-y-2">
                          <Label htmlFor="start_date">Start Date</Label>
                          <Input
                            id="start_date"
                            type="date"
                            min={new Date().toISOString().split('T')[0]}
                            value={subscriptionForm.start_date}
                            onChange={(e) => setSubscriptionForm({
                              ...subscriptionForm,
                              start_date: e.target.value
                            })}
                          />
                        </div>

                        {/* Pricing Summary */}
                        <div className="p-4 bg-muted/50 rounded-lg space-y-2">
                          <div className="flex justify-between">
                            <span>Unit Price:</span>
                            <span>{formatCurrency(calculateAmount(product, subscriptionForm.frequency))}</span>
                          </div>
                          <div className="flex justify-between">
                            <span>Quantity:</span>
                            <span>{subscriptionForm.quantity}</span>
                          </div>
                          <div className="flex justify-between font-bold text-lg border-t pt-2">
                            <span>Total per {subscriptionForm.frequency.slice(0, -2)}:</span>
                            <span>{formatCurrency(calculateAmount(product, subscriptionForm.frequency) * subscriptionForm.quantity)}</span>
                          </div>
                        </div>

                        <Button onClick={handleSubscribe} className="w-full" disabled={loading}>
                          {loading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                          Confirm Subscription
                        </Button>
                      </div>
                    </DialogContent>
                  </Dialog>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      ) : (
        <Card>
          <CardContent className="text-center py-12">
            <Package className="h-16 w-16 text-muted-foreground mx-auto mb-4" />
            <h3 className="text-lg font-medium mb-2">No products found</h3>
            <p className="text-muted-foreground">
              {searchTerm || categoryFilter !== 'all' 
                ? 'Try adjusting your search or filters' 
                : 'Products will appear here when available'
              }
            </p>
          </CardContent>
        </Card>
      )}
    </div>
  );
};

export default ProductsPage;

