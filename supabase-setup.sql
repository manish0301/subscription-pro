-- Supabase Database Setup for SubscriptionPro
-- Run this in Supabase SQL Editor

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
    image_url VARCHAR(255),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Create subscriptions table
CREATE TABLE IF NOT EXISTS subscriptions (
    subscription_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    product_id UUID NOT NULL REFERENCES products(product_id) ON DELETE CASCADE,
    status VARCHAR(20) DEFAULT 'active' CHECK (status IN ('active', 'paused', 'canceled')),
    frequency VARCHAR(20) NOT NULL CHECK (frequency IN ('weekly', 'monthly', 'quarterly', 'yearly')),
    quantity INTEGER DEFAULT 1,
    amount DECIMAL(10, 2) NOT NULL,
    start_date DATE NOT NULL,
    next_delivery_date DATE,
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
    status VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('successful', 'failed', 'pending')),
    payment_date TIMESTAMP DEFAULT NOW(),
    created_at TIMESTAMP DEFAULT NOW()
);

-- Insert sample data
INSERT INTO users (email, password_hash, first_name, last_name, user_role) VALUES
('admin@demo.com', 'hashed_password', 'Admin', 'User', 'admin'),
('user@demo.com', 'hashed_password', 'Test', 'User', 'customer')
ON CONFLICT (email) DO NOTHING;

INSERT INTO products (name, description, price) VALUES
('Monthly Coffee', 'Premium coffee delivered monthly', 299.00),
('Weekly Snacks', 'Healthy snacks delivered weekly', 199.00),
('Quarterly Books', 'Curated books delivered quarterly', 999.00)
ON CONFLICT DO NOTHING;

INSERT INTO subscriptions (user_id, product_id, frequency, amount, start_date, next_delivery_date) VALUES
((SELECT user_id FROM users WHERE email = 'user@demo.com'), 
 (SELECT product_id FROM products WHERE name = 'Monthly Coffee'), 
 'monthly', 299.00, CURRENT_DATE, CURRENT_DATE + INTERVAL '1 month')
ON CONFLICT DO NOTHING;