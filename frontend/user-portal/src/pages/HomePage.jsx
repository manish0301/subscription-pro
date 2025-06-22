import React from 'react';
import { Link } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { ArrowRight, CheckCircle, Package, Repeat, Shield, Zap } from 'lucide-react';

const HomePage = () => {
  const features = [
    {
      icon: <Package className="h-6 w-6" />,
      title: "Smart Subscriptions",
      description: "Intelligent subscription management with flexible scheduling and automatic renewals."
    },
    {
      icon: <Repeat className="h-6 w-6" />,
      title: "Flexible Billing",
      description: "Multiple billing cycles, pause, skip, and modify subscriptions with ease."
    },
    {
      icon: <Shield className="h-6 w-6" />,
      title: "Secure Payments",
      description: "PCI DSS compliant payment processing with multiple payment methods."
    },
    {
      icon: <Zap className="h-6 w-6" />,
      title: "Real-time Analytics",
      description: "Comprehensive dashboard with insights into your subscription performance."
    }
  ];

  const benefits = [
    "Reduce customer churn with intelligent retention features",
    "Increase revenue with flexible subscription models",
    "Automate billing and reduce manual intervention",
    "Provide excellent customer experience with self-service portal",
    "Scale your subscription business with enterprise-grade infrastructure"
  ];

  return (
    <div className="space-y-16">
      {/* Hero Section */}
      <section className="text-center space-y-6 py-12">
        <Badge variant="secondary" className="mb-4">
          Subscription Management Platform
        </Badge>
        <h1 className="text-4xl md:text-6xl font-bold tracking-tight">
          Grow Your Business with
          <span className="text-primary block">Smart Subscriptions</span>
        </h1>
        <p className="text-xl text-muted-foreground max-w-3xl mx-auto">
          SubscriptionPro is a comprehensive platform that helps businesses manage recurring subscriptions, 
          automate billing, and provide exceptional customer experiences.
        </p>
        <div className="flex flex-col sm:flex-row gap-4 justify-center">
          <Button size="lg" asChild>
            <Link to="/register">
              Get Started Free
              <ArrowRight className="ml-2 h-4 w-4" />
            </Link>
          </Button>
          <Button size="lg" variant="outline" asChild>
            <Link to="/products">View Products</Link>
          </Button>
        </div>
      </section>

      {/* Features Section */}
      <section className="space-y-8">
        <div className="text-center space-y-4">
          <h2 className="text-3xl font-bold">Powerful Features</h2>
          <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
            Everything you need to build and scale your subscription business
          </p>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {features.map((feature, index) => (
            <Card key={index} className="text-center">
              <CardHeader>
                <div className="mx-auto w-12 h-12 bg-primary/10 rounded-lg flex items-center justify-center text-primary">
                  {feature.icon}
                </div>
                <CardTitle className="text-lg">{feature.title}</CardTitle>
              </CardHeader>
              <CardContent>
                <CardDescription>{feature.description}</CardDescription>
              </CardContent>
            </Card>
          ))}
        </div>
      </section>

      {/* Benefits Section */}
      <section className="bg-muted/50 rounded-lg p-8 space-y-8">
        <div className="text-center space-y-4">
          <h2 className="text-3xl font-bold">Why Choose SubscriptionPro?</h2>
          <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
            Join thousands of businesses that trust us with their subscription management
          </p>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="space-y-4">
            {benefits.map((benefit, index) => (
              <div key={index} className="flex items-start space-x-3">
                <CheckCircle className="h-5 w-5 text-green-500 mt-0.5 flex-shrink-0" />
                <span className="text-sm">{benefit}</span>
              </div>
            ))}
          </div>
          <div className="flex items-center justify-center">
            <div className="bg-gradient-to-br from-primary/20 to-primary/5 rounded-lg p-8 text-center space-y-4">
              <div className="text-4xl font-bold text-primary">99.9%</div>
              <div className="text-sm text-muted-foreground">Uptime Guarantee</div>
              <div className="text-2xl font-bold text-primary">24/7</div>
              <div className="text-sm text-muted-foreground">Customer Support</div>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="text-center space-y-6 py-12">
        <h2 className="text-3xl font-bold">Ready to Get Started?</h2>
        <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
          Join thousands of businesses already using SubscriptionPro to grow their recurring revenue.
        </p>
        <div className="flex flex-col sm:flex-row gap-4 justify-center">
          <Button size="lg" asChild>
            <Link to="/register">
              Start Your Free Trial
              <ArrowRight className="ml-2 h-4 w-4" />
            </Link>
          </Button>
          <Button size="lg" variant="outline" asChild>
            <Link to="/login">Sign In</Link>
          </Button>
        </div>
      </section>
    </div>
  );
};

export default HomePage;

