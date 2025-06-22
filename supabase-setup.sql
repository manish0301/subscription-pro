-- Supabase Database Setup for SubscriptionPro
-- Run this in Supabase SQL Editor

-- Enable necessary extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create users table
CREATE TABLE IF NOT EXISTS users (
    user_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    phone_number VARCHAR(20),
    user_role VARCHAR(20) DEFAULT 'customer' CHECK (user_role IN ('customer', 'admin')),
    address_line1 VARCHAR(255),
    address_line2 VARCHAR(255),
    city VARCHAR(100),
    state VARCHAR(100),
    postal_code VARCHAR(20),
    country VARCHAR(100) DEFAULT 'India',
    is_active BOOLEAN DEFAULT true,
    email_verified BOOLEAN DEFAULT false,
    last_login TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Create products table
CREATE TABLE IF NOT EXISTS products (
    product_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    price DECIMAL(10, 2) NOT NULL,
    currency VARCHAR(3) DEFAULT 'INR',
    is_subscription_product BOOLEAN DEFAULT true,
    category VARCHAR(100),
    sku VARCHAR(100) UNIQUE,
    image_url VARCHAR(255),
    is_active BOOLEAN DEFAULT true,
    salesforce_product_id VARCHAR(255),
    inventory_count INTEGER DEFAULT 0,
    min_subscription_period INTEGER DEFAULT 1, -- minimum months
    max_subscription_period INTEGER, -- maximum months, null for unlimited
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Create subscriptions table
CREATE TABLE IF NOT EXISTS subscriptions (
    subscription_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    product_id UUID NOT NULL REFERENCES products(product_id) ON DELETE CASCADE,
    status VARCHAR(20) DEFAULT 'active' CHECK (status IN ('active', 'paused', 'canceled', 'completed')),
    frequency VARCHAR(20) NOT NULL CHECK (frequency IN ('daily', 'weekly', 'monthly', 'quarterly', 'yearly', 'custom')),
    quantity INTEGER DEFAULT 1,
    amount DECIMAL(10, 2) NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE,
    next_delivery_date DATE,
    last_delivery_date DATE,
    delivery_count INTEGER DEFAULT 0,
    max_deliveries INTEGER, -- null for unlimited
    payment_method VARCHAR(50) DEFAULT 'recurring' CHECK (payment_method IN ('upfront', 'recurring')),
    custom_schedule JSONB, -- for custom delivery schedules
    delivery_address JSONB, -- delivery address details
    notes TEXT,
    salesforce_subscription_id VARCHAR(255),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Create payments table
CREATE TABLE IF NOT EXISTS payments (
    payment_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    subscription_id UUID REFERENCES subscriptions(subscription_id) ON DELETE CASCADE,
    amount DECIMAL(10, 2) NOT NULL,
    currency VARCHAR(3) DEFAULT 'INR',
    payment_gateway VARCHAR(100) DEFAULT 'razorpay',
    gateway_transaction_id VARCHAR(255) UNIQUE NOT NULL,
    gateway_order_id VARCHAR(255),
    status VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('successful', 'failed', 'pending', 'refunded')),
    payment_method VARCHAR(50), -- card, upi, netbanking, etc.
    failure_reason TEXT,
    refund_amount DECIMAL(10, 2),
    refund_date TIMESTAMP,
    payment_date TIMESTAMP DEFAULT NOW(),
    created_at TIMESTAMP DEFAULT NOW()
);

-- Create audit logs table for tracking all activities
CREATE TABLE IF NOT EXISTS audit_logs (
    log_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(user_id) ON DELETE SET NULL,
    action VARCHAR(100) NOT NULL,
    resource_type VARCHAR(50) NOT NULL, -- users, products, subscriptions, payments
    resource_id UUID,
    old_values JSONB,
    new_values JSONB,
    ip_address INET,
    user_agent TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Create notifications table
CREATE TABLE IF NOT EXISTS notifications (
    notification_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    type VARCHAR(50) NOT NULL, -- email, sms, push
    subject VARCHAR(255),
    message TEXT NOT NULL,
    status VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('pending', 'sent', 'failed')),
    sent_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_role ON users(user_role);
CREATE INDEX IF NOT EXISTS idx_products_active ON products(is_active);
CREATE INDEX IF NOT EXISTS idx_products_category ON products(category);
CREATE INDEX IF NOT EXISTS idx_subscriptions_user_id ON subscriptions(user_id);
CREATE INDEX IF NOT EXISTS idx_subscriptions_status ON subscriptions(status);
CREATE INDEX IF NOT EXISTS idx_subscriptions_next_delivery ON subscriptions(next_delivery_date);
CREATE INDEX IF NOT EXISTS idx_payments_user_id ON payments(user_id);
CREATE INDEX IF NOT EXISTS idx_payments_subscription_id ON payments(subscription_id);
CREATE INDEX IF NOT EXISTS idx_payments_status ON payments(status);
CREATE INDEX IF NOT EXISTS idx_payments_date ON payments(payment_date);
CREATE INDEX IF NOT EXISTS idx_audit_logs_user_id ON audit_logs(user_id);
CREATE INDEX IF NOT EXISTS idx_audit_logs_resource ON audit_logs(resource_type, resource_id);
CREATE INDEX IF NOT EXISTS idx_notifications_user_id ON notifications(user_id);
CREATE INDEX IF NOT EXISTS idx_notifications_status ON notifications(status);

-- Enable Row Level Security (RLS)
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE products ENABLE ROW LEVEL SECURITY;
ALTER TABLE subscriptions ENABLE ROW LEVEL SECURITY;
ALTER TABLE payments ENABLE ROW LEVEL SECURITY;
ALTER TABLE audit_logs ENABLE ROW LEVEL SECURITY;
ALTER TABLE notifications ENABLE ROW LEVEL SECURITY;

-- Create RLS policies
-- Users can only see their own data
CREATE POLICY "Users can view own profile" ON users
    FOR SELECT USING (auth.uid()::text = user_id::text);

CREATE POLICY "Users can update own profile" ON users
    FOR UPDATE USING (auth.uid()::text = user_id::text);

-- Products are publicly readable
CREATE POLICY "Products are publicly readable" ON products
    FOR SELECT USING (true);

-- Subscriptions are user-specific
CREATE POLICY "Users can view own subscriptions" ON subscriptions
    FOR SELECT USING (auth.uid()::text = user_id::text);

CREATE POLICY "Users can update own subscriptions" ON subscriptions
    FOR UPDATE USING (auth.uid()::text = user_id::text);

-- Payments are user-specific
CREATE POLICY "Users can view own payments" ON payments
    FOR SELECT USING (auth.uid()::text = user_id::text);

-- Admin policies for full access
CREATE POLICY "Admins can view all users" ON users
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM users u
            WHERE u.user_id::text = auth.uid()::text
            AND u.user_role = 'admin'
        )
    );

CREATE POLICY "Admins can update all users" ON users
    FOR UPDATE USING (
        EXISTS (
            SELECT 1 FROM users u
            WHERE u.user_id::text = auth.uid()::text
            AND u.user_role = 'admin'
        )
    );

CREATE POLICY "Admins can view all subscriptions" ON subscriptions
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM users u
            WHERE u.user_id::text = auth.uid()::text
            AND u.user_role = 'admin'
        )
    );

CREATE POLICY "Admins can update all subscriptions" ON subscriptions
    FOR UPDATE USING (
        EXISTS (
            SELECT 1 FROM users u
            WHERE u.user_id::text = auth.uid()::text
            AND u.user_role = 'admin'
        )
    );

CREATE POLICY "Admins can view all payments" ON payments
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM users u
            WHERE u.user_id::text = auth.uid()::text
            AND u.user_role = 'admin'
        )
    );

-- Audit logs - admins only
CREATE POLICY "Admins can view audit logs" ON audit_logs
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM users u
            WHERE u.user_id::text = auth.uid()::text
            AND u.user_role = 'admin'
        )
    );

-- Notifications - users can view their own
CREATE POLICY "Users can view own notifications" ON notifications
    FOR SELECT USING (auth.uid()::text = user_id::text);

-- Insert sample data (for development only)
-- Note: Password is 'password123' hashed with SHA256
INSERT INTO users (email, password_hash, first_name, last_name, user_role, phone_number, city, country) VALUES
('admin@subscriptionpro.com', 'ef92b778bafe771e89245b89ecbc08a44a4e166c06659911881f383d4473e94f', 'Admin', 'User', 'admin', '+91-9876543210', 'Mumbai', 'India'),
('demo@subscriptionpro.com', 'ef92b778bafe771e89245b89ecbc08a44a4e166c06659911881f383d4473e94f', 'Demo', 'Customer', 'customer', '+91-9876543211', 'Delhi', 'India'),
('merchant@subscriptionpro.com', 'ef92b778bafe771e89245b89ecbc08a44a4e166c06659911881f383d4473e94f', 'Merchant', 'Owner', 'admin', '+91-9876543212', 'Bangalore', 'India')
ON CONFLICT (email) DO NOTHING;

INSERT INTO products (name, description, price, category, sku, is_active) VALUES
('Premium Coffee Subscription', 'Freshly roasted coffee beans delivered monthly', 1299.00, 'Food & Beverages', 'COFFEE-001', true),
('Organic Tea Collection', 'Curated selection of organic teas', 899.00, 'Food & Beverages', 'TEA-001', true),
('Skincare Essentials Kit', 'Monthly skincare products for healthy skin', 1599.00, 'Beauty & Personal Care', 'SKIN-001', true),
('Fitness Supplement Pack', 'Protein and vitamin supplements', 2499.00, 'Health & Fitness', 'FIT-001', true),
('Book Club Subscription', 'Handpicked books delivered monthly', 799.00, 'Books & Media', 'BOOK-001', true),
('Gourmet Snack Box', 'International snacks and treats', 1199.00, 'Food & Beverages', 'SNACK-001', true),
('Plant Care Kit', 'Everything needed for indoor plants', 699.00, 'Home & Garden', 'PLANT-001', true),
('Tech Gadget Box', 'Latest tech accessories and gadgets', 2999.00, 'Electronics', 'TECH-001', true)
ON CONFLICT (sku) DO NOTHING;

-- Create a sample subscription only if demo user exists
INSERT INTO subscriptions (user_id, product_id, frequency, amount, start_date, next_delivery_date)
SELECT
    u.user_id,
    p.product_id,
    'monthly',
    p.price,
    CURRENT_DATE,
    CURRENT_DATE + INTERVAL '1 month'
FROM users u, products p
WHERE u.email = 'demo@subscriptionpro.com'
AND p.name = 'Pro Plan'
AND NOT EXISTS (
    SELECT 1 FROM subscriptions s
    WHERE s.user_id = u.user_id AND s.product_id = p.product_id
);