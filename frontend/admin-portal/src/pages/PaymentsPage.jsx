import React from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { CreditCard } from 'lucide-react';

const PaymentsPage = () => {
  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="space-y-2">
        <h1 className="text-3xl font-bold">Payments</h1>
        <p className="text-muted-foreground">
          Monitor payment transactions and billing
        </p>
      </div>

      {/* Coming Soon */}
      <Card>
        <CardContent className="text-center py-12">
          <CreditCard className="h-16 w-16 text-muted-foreground mx-auto mb-4" />
          <h3 className="text-lg font-medium mb-2">Payment Management</h3>
          <p className="text-muted-foreground">
            Payment management features will be available soon
          </p>
        </CardContent>
      </Card>
    </div>
  );
};

export default PaymentsPage;

