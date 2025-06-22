import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Badge } from './ui/badge';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select';
import { Input } from './ui/input';
import { Label } from './ui/label';
import { Calendar, Clock, CreditCard, Truck, Gift } from 'lucide-react';

const SubscriptionWidget = ({ product, onSubscriptionSelect, onAddToCart }) => {
  const [selectedPlan, setSelectedPlan] = useState('monthly');
  const [quantity, setQuantity] = useState(1);
  const [startDate, setStartDate] = useState('');
  const [paymentOption, setPaymentOption] = useState('recurring');
  const [customFrequency, setCustomFrequency] = useState({ value: 1, unit: 'weeks' });
  const [showCustom, setShowCustom] = useState(false);

  // Subscription plans with enterprise-grade options
  const subscriptionPlans = [
    {
      id: 'weekly',
      name: 'Weekly',
      frequency: 'Every week',
      discount: 5,
      savings: 'Save 5%',
      popular: false
    },
    {
      id: 'biweekly',
      name: 'Bi-Weekly',
      frequency: 'Every 2 weeks',
      discount: 8,
      savings: 'Save 8%',
      popular: false
    },
    {
      id: 'monthly',
      name: 'Monthly',
      frequency: 'Every month',
      discount: 15,
      savings: 'Save 15%',
      popular: true
    },
    {
      id: 'quarterly',
      name: 'Quarterly',
      frequency: 'Every 3 months',
      discount: 20,
      savings: 'Save 20%',
      popular: false
    },
    {
      id: 'custom',
      name: 'Custom',
      frequency: 'Choose your schedule',
      discount: 10,
      savings: 'Save 10%',
      popular: false
    }
  ];

  const calculatePrice = (plan) => {
    const basePrice = product.price * quantity;
    const discount = plan.discount / 100;
    return basePrice * (1 - discount);
  };

  const calculateSavings = (plan) => {
    const basePrice = product.price * quantity;
    const discountedPrice = calculatePrice(plan);
    return basePrice - discountedPrice;
  };

  const handleSubscriptionCreate = () => {
    const selectedPlanData = subscriptionPlans.find(p => p.id === selectedPlan);
    
    const subscriptionData = {
      productId: product.product_id,
      planId: selectedPlan,
      frequency: selectedPlan === 'custom' ? 
        `${customFrequency.value}_${customFrequency.unit}` : 
        selectedPlan,
      quantity: quantity,
      startDate: startDate || new Date().toISOString().split('T')[0],
      paymentOption: paymentOption,
      amount: calculatePrice(selectedPlanData),
      savings: calculateSavings(selectedPlanData),
      customSchedule: selectedPlan === 'custom' ? customFrequency : null
    };

    onSubscriptionSelect(subscriptionData);
  };

  const handleOneTimePurchase = () => {
    onAddToCart({
      productId: product.product_id,
      quantity: quantity,
      amount: product.price * quantity,
      type: 'one-time'
    });
  };

  useEffect(() => {
    // Set default start date to tomorrow
    const tomorrow = new Date();
    tomorrow.setDate(tomorrow.getDate() + 1);
    setStartDate(tomorrow.toISOString().split('T')[0]);
  }, []);

  return (
    <div className="subscription-widget space-y-6">
      {/* Purchase Options */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {/* One-time Purchase */}
        <Card className="border-2">
          <CardHeader className="pb-3">
            <CardTitle className="text-lg flex items-center gap-2">
              <CreditCard className="h-5 w-5" />
              One-time Purchase
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="text-2xl font-bold">
                ₹{(product.price * quantity).toLocaleString()}
              </div>
              <div className="space-y-2">
                <Label htmlFor="quantity-onetime">Quantity</Label>
                <Input
                  id="quantity-onetime"
                  type="number"
                  min="1"
                  value={quantity}
                  onChange={(e) => setQuantity(parseInt(e.target.value) || 1)}
                  className="w-20"
                />
              </div>
              <Button 
                onClick={handleOneTimePurchase}
                variant="outline" 
                className="w-full"
              >
                Add to Cart
              </Button>
            </div>
          </CardContent>
        </Card>

        {/* Subscription Purchase */}
        <Card className="border-2 border-primary bg-primary/5">
          <CardHeader className="pb-3">
            <CardTitle className="text-lg flex items-center gap-2">
              <Truck className="h-5 w-5" />
              Subscribe & Save
              <Badge variant="secondary" className="ml-auto">
                <Gift className="h-3 w-3 mr-1" />
                Recommended
              </Badge>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {/* Subscription Plans */}
              <div className="space-y-2">
                <Label>Delivery Frequency</Label>
                <div className="grid grid-cols-1 gap-2">
                  {subscriptionPlans.map((plan) => (
                    <div
                      key={plan.id}
                      className={`p-3 border rounded-lg cursor-pointer transition-all ${
                        selectedPlan === plan.id
                          ? 'border-primary bg-primary/10'
                          : 'border-gray-200 hover:border-gray-300'
                      }`}
                      onClick={() => {
                        setSelectedPlan(plan.id);
                        setShowCustom(plan.id === 'custom');
                      }}
                    >
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-2">
                          <input
                            type="radio"
                            checked={selectedPlan === plan.id}
                            onChange={() => {}}
                            className="text-primary"
                          />
                          <div>
                            <div className="font-medium flex items-center gap-2">
                              {plan.name}
                              {plan.popular && (
                                <Badge variant="default" className="text-xs">
                                  Most Popular
                                </Badge>
                              )}
                            </div>
                            <div className="text-sm text-gray-600">
                              {plan.frequency}
                            </div>
                          </div>
                        </div>
                        <div className="text-right">
                          <div className="font-bold text-green-600">
                            {plan.savings}
                          </div>
                          <div className="text-sm text-gray-600">
                            ₹{calculatePrice(plan).toLocaleString()}
                          </div>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Custom Frequency */}
              {showCustom && (
                <div className="space-y-2 p-3 bg-gray-50 rounded-lg">
                  <Label>Custom Delivery Schedule</Label>
                  <div className="flex gap-2">
                    <Input
                      type="number"
                      min="1"
                      max="52"
                      value={customFrequency.value}
                      onChange={(e) => setCustomFrequency({
                        ...customFrequency,
                        value: parseInt(e.target.value) || 1
                      })}
                      className="w-20"
                    />
                    <Select
                      value={customFrequency.unit}
                      onValueChange={(value) => setCustomFrequency({
                        ...customFrequency,
                        unit: value
                      })}
                    >
                      <SelectTrigger className="w-32">
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="days">Days</SelectItem>
                        <SelectItem value="weeks">Weeks</SelectItem>
                        <SelectItem value="months">Months</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  <div className="text-sm text-gray-600">
                    Delivery every {customFrequency.value} {customFrequency.unit}
                  </div>
                </div>
              )}

              {/* Quantity */}
              <div className="space-y-2">
                <Label htmlFor="quantity-subscription">Quantity per delivery</Label>
                <Input
                  id="quantity-subscription"
                  type="number"
                  min="1"
                  value={quantity}
                  onChange={(e) => setQuantity(parseInt(e.target.value) || 1)}
                  className="w-20"
                />
              </div>

              {/* Start Date */}
              <div className="space-y-2">
                <Label htmlFor="start-date">First delivery date</Label>
                <Input
                  id="start-date"
                  type="date"
                  value={startDate}
                  onChange={(e) => setStartDate(e.target.value)}
                  min={new Date().toISOString().split('T')[0]}
                />
              </div>

              {/* Payment Option */}
              <div className="space-y-2">
                <Label>Payment Option</Label>
                <Select value={paymentOption} onValueChange={setPaymentOption}>
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="recurring">
                      Pay before each delivery
                    </SelectItem>
                    <SelectItem value="upfront">
                      Pay upfront for entire subscription
                    </SelectItem>
                  </SelectContent>
                </Select>
              </div>

              {/* Price Summary */}
              <div className="space-y-2 p-3 bg-green-50 rounded-lg">
                <div className="flex justify-between items-center">
                  <span className="text-sm">Regular Price:</span>
                  <span className="text-sm line-through text-gray-500">
                    ₹{(product.price * quantity).toLocaleString()}
                  </span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-sm">Subscription Price:</span>
                  <span className="text-sm font-bold text-green-600">
                    ₹{calculatePrice(subscriptionPlans.find(p => p.id === selectedPlan)).toLocaleString()}
                  </span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-sm font-bold">You Save:</span>
                  <span className="text-sm font-bold text-green-600">
                    ₹{calculateSavings(subscriptionPlans.find(p => p.id === selectedPlan)).toLocaleString()}
                  </span>
                </div>
              </div>

              <Button 
                onClick={handleSubscriptionCreate}
                className="w-full"
                size="lg"
              >
                <Clock className="h-4 w-4 mr-2" />
                Subscribe Now
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Subscription Benefits */}
      <Card>
        <CardContent className="pt-6">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-center">
            <div className="space-y-2">
              <Truck className="h-8 w-8 mx-auto text-primary" />
              <div className="text-sm font-medium">Free Delivery</div>
              <div className="text-xs text-gray-600">On all subscription orders</div>
            </div>
            <div className="space-y-2">
              <Calendar className="h-8 w-8 mx-auto text-primary" />
              <div className="text-sm font-medium">Flexible Schedule</div>
              <div className="text-xs text-gray-600">Change anytime</div>
            </div>
            <div className="space-y-2">
              <CreditCard className="h-8 w-8 mx-auto text-primary" />
              <div className="text-sm font-medium">Secure Payments</div>
              <div className="text-xs text-gray-600">PCI DSS compliant</div>
            </div>
            <div className="space-y-2">
              <Gift className="h-8 w-8 mx-auto text-primary" />
              <div className="text-sm font-medium">Cancel Anytime</div>
              <div className="text-xs text-gray-600">No commitments</div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default SubscriptionWidget;
