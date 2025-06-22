-- Sample data for testing and demonstration
-- This script populates the database with realistic test data

-- Insert additional sample products
INSERT INTO products (name, description, price, currency, category, is_active) VALUES
('Artisan Tea Collection', 'Curated selection of premium teas from around the world, delivered monthly', 1899.00, 'INR', 'Food & Beverage', true),
('Gourmet Spice Box', 'Exotic spices and seasonings to elevate your cooking, delivered quarterly', 1299.00, 'INR', 'Food & Beverage', true),
('Fresh Flower Subscription', 'Beautiful seasonal flowers delivered to your doorstep weekly', 899.00, 'INR', 'Home & Garden', true),
('Craft Beer Discovery', 'Discover new craft beers from local breweries, monthly delivery', 3499.00, 'INR', 'Food & Beverage', true),
('Wellness Supplement Pack', 'Essential vitamins and supplements for optimal health, monthly delivery', 2799.00, 'INR', 'Health & Fitness', true),
('Artisan Chocolate Box', 'Handcrafted chocolates from premium chocolatiers, monthly delivery', 2199.00, 'INR', 'Food & Beverage', true),
('Pet Care Essentials', 'Monthly delivery of premium pet food and care products', 1799.00, 'INR', 'Pet Care', true),
('Home Cleaning Kit', 'Eco-friendly cleaning products for a spotless home, monthly delivery', 1399.00, 'INR', 'Home & Garden', true),
('Stationery & Office Supplies', 'Premium stationery and office essentials, quarterly delivery', 999.00, 'INR', 'Office & Business', true),
('Gourmet Snack Box', 'Healthy and delicious snacks from around the world, monthly delivery', 1699.00, 'INR', 'Food & Beverage', true),
('Yoga & Meditation Kit', 'Essential items for your yoga and meditation practice, quarterly delivery', 2499.00, 'INR', 'Health & Fitness', true),
('Artisan Soap Collection', 'Handmade soaps with natural ingredients, monthly delivery', 1199.00, 'INR', 'Beauty & Personal Care', true),
('Gourmet Cheese Selection', 'Premium cheeses from local and international producers, monthly delivery', 3299.00, 'INR', 'Food & Beverage', true),
('Plant Care Package', 'Everything you need to keep your plants healthy, monthly delivery', 899.00, 'INR', 'Home & Garden', true),
('Tech Accessories Box', 'Latest tech gadgets and accessories, quarterly delivery', 4999.00, 'INR', 'Technology', true)
ON CONFLICT DO NOTHING;

-- Insert sample users
INSERT INTO users (email, password_hash, first_name, last_name, phone_number, date_of_birth, address_line1, address_line2, city, state, postal_code, country, user_role) VALUES
('john.doe@example.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj/RK.s5uDjS', 'John', 'Doe', '+91-9876543210', '1985-03-15', '123 MG Road', 'Apartment 4B', 'Mumbai', 'Maharashtra', '400001', 'India', 'user'),
('jane.smith@example.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj/RK.s5uDjS', 'Jane', 'Smith', '+91-9876543211', '1990-07-22', '456 Brigade Road', 'Floor 2', 'Bangalore', 'Karnataka', '560001', 'India', 'user'),
('rajesh.kumar@example.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj/RK.s5uDjS', 'Rajesh', 'Kumar', '+91-9876543212', '1988-11-08', '789 Park Street', 'Near Metro Station', 'Kolkata', 'West Bengal', '700001', 'India', 'user'),
('priya.patel@example.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj/RK.s5uDjS', 'Priya', 'Patel', '+91-9876543213', '1992-05-18', '321 Connaught Place', 'Block A', 'New Delhi', 'Delhi', '110001', 'India', 'user'),
('amit.sharma@example.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj/RK.s5uDjS', 'Amit', 'Sharma', '+91-9876543214', '1987-09-12', '654 Anna Salai', 'T. Nagar', 'Chennai', 'Tamil Nadu', '600017', 'India', 'user'),
('sneha.reddy@example.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj/RK.s5uDjS', 'Sneha', 'Reddy', '+91-9876543215', '1991-12-03', '987 Banjara Hills', 'Road No. 12', 'Hyderabad', 'Telangana', '500034', 'India', 'user'),
('vikram.singh@example.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj/RK.s5uDjS', 'Vikram', 'Singh', '+91-9876543216', '1989-04-25', '147 Civil Lines', 'Near University', 'Jaipur', 'Rajasthan', '302006', 'India', 'user'),
('kavya.nair@example.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj/RK.s5uDjS', 'Kavya', 'Nair', '+91-9876543217', '1993-08-14', '258 Marine Drive', 'Sea View Apartments', 'Kochi', 'Kerala', '682001', 'India', 'user'),
('arjun.gupta@example.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj/RK.s5uDjS', 'Arjun', 'Gupta', '+91-9876543218', '1986-01-30', '369 Sector 17', 'Chandigarh', 'Chandigarh', 'Punjab', '160017', 'India', 'user'),
('meera.joshi@example.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj/RK.s5uDjS', 'Meera', 'Joshi', '+91-9876543219', '1994-06-07', '741 FC Road', 'Pune University Area', 'Pune', 'Maharashtra', '411005', 'India', 'user')
ON CONFLICT DO NOTHING;

-- Get user and product IDs for creating subscriptions
-- Note: In a real scenario, you would use the actual UUIDs from the database

-- Insert sample subscriptions (using placeholder UUIDs - these would need to be updated with actual IDs)
-- Active subscriptions
INSERT INTO subscriptions (user_id, product_id, status, frequency, quantity, amount, currency, start_date, next_delivery_date) 
SELECT 
    u.user_id,
    p.product_id,
    'active',
    'monthly',
    1,
    p.price,
    'INR',
    '2024-01-01',
    '2024-02-01'
FROM users u, products p 
WHERE u.email = 'john.doe@example.com' AND p.name = 'Premium Coffee Subscription'
LIMIT 1;

INSERT INTO subscriptions (user_id, product_id, status, frequency, quantity, amount, currency, start_date, next_delivery_date) 
SELECT 
    u.user_id,
    p.product_id,
    'active',
    'weekly',
    1,
    p.price,
    'INR',
    '2024-01-15',
    '2024-02-05'
FROM users u, products p 
WHERE u.email = 'jane.smith@example.com' AND p.name = 'Organic Vegetable Box'
LIMIT 1;

INSERT INTO subscriptions (user_id, product_id, status, frequency, quantity, amount, currency, start_date, next_delivery_date) 
SELECT 
    u.user_id,
    p.product_id,
    'active',
    'monthly',
    2,
    p.price * 2,
    'INR',
    '2024-01-10',
    '2024-02-10'
FROM users u, products p 
WHERE u.email = 'rajesh.kumar@example.com' AND p.name = 'Artisan Tea Collection'
LIMIT 1;

INSERT INTO subscriptions (user_id, product_id, status, frequency, quantity, amount, currency, start_date, next_delivery_date) 
SELECT 
    u.user_id,
    p.product_id,
    'active',
    'quarterly',
    1,
    p.price,
    'INR',
    '2024-01-01',
    '2024-04-01'
FROM users u, products p 
WHERE u.email = 'priya.patel@example.com' AND p.name = 'Gourmet Spice Box'
LIMIT 1;

INSERT INTO subscriptions (user_id, product_id, status, frequency, quantity, amount, currency, start_date, next_delivery_date) 
SELECT 
    u.user_id,
    p.product_id,
    'active',
    'monthly',
    1,
    p.price,
    'INR',
    '2024-01-20',
    '2024-02-20'
FROM users u, products p 
WHERE u.email = 'amit.sharma@example.com' AND p.name = 'Wellness Supplement Pack'
LIMIT 1;

-- Paused subscriptions
INSERT INTO subscriptions (user_id, product_id, status, frequency, quantity, amount, currency, start_date, next_delivery_date) 
SELECT 
    u.user_id,
    p.product_id,
    'paused',
    'weekly',
    1,
    p.price,
    'INR',
    '2024-01-05',
    '2024-03-01'
FROM users u, products p 
WHERE u.email = 'sneha.reddy@example.com' AND p.name = 'Fresh Flower Subscription'
LIMIT 1;

INSERT INTO subscriptions (user_id, product_id, status, frequency, quantity, amount, currency, start_date, next_delivery_date) 
SELECT 
    u.user_id,
    p.product_id,
    'paused',
    'monthly',
    1,
    p.price,
    'INR',
    '2024-01-12',
    '2024-03-12'
FROM users u, products p 
WHERE u.email = 'vikram.singh@example.com' AND p.name = 'Craft Beer Discovery'
LIMIT 1;

-- Canceled subscriptions
INSERT INTO subscriptions (user_id, product_id, status, frequency, quantity, amount, currency, start_date, end_date) 
SELECT 
    u.user_id,
    p.product_id,
    'canceled',
    'monthly',
    1,
    p.price,
    'INR',
    '2023-12-01',
    '2024-01-15'
FROM users u, products p 
WHERE u.email = 'kavya.nair@example.com' AND p.name = 'Book Club Subscription'
LIMIT 1;

-- More active subscriptions
INSERT INTO subscriptions (user_id, product_id, status, frequency, quantity, amount, currency, start_date, next_delivery_date) 
SELECT 
    u.user_id,
    p.product_id,
    'active',
    'monthly',
    1,
    p.price,
    'INR',
    '2024-01-08',
    '2024-02-08'
FROM users u, products p 
WHERE u.email = 'arjun.gupta@example.com' AND p.name = 'Artisan Chocolate Box'
LIMIT 1;

INSERT INTO subscriptions (user_id, product_id, status, frequency, quantity, amount, currency, start_date, next_delivery_date) 
SELECT 
    u.user_id,
    p.product_id,
    'active',
    'monthly',
    1,
    p.price,
    'INR',
    '2024-01-25',
    '2024-02-25'
FROM users u, products p 
WHERE u.email = 'meera.joshi@example.com' AND p.name = 'Skincare Essentials'
LIMIT 1;

-- Insert sample payments for active subscriptions
INSERT INTO payments (subscription_id, user_id, amount, currency, payment_method, payment_status, gateway_transaction_id, gateway_response)
SELECT 
    s.subscription_id,
    s.user_id,
    s.amount,
    s.currency,
    'razorpay',
    'completed',
    'pay_' || substr(md5(random()::text), 1, 10),
    '{"status": "captured", "method": "card"}'
FROM subscriptions s
WHERE s.status = 'active'
AND s.created_at >= '2024-01-01';

-- Insert some failed payments
INSERT INTO payments (subscription_id, user_id, amount, currency, payment_method, payment_status, gateway_transaction_id, gateway_response)
SELECT 
    s.subscription_id,
    s.user_id,
    s.amount,
    s.currency,
    'razorpay',
    'failed',
    'pay_' || substr(md5(random()::text), 1, 10),
    '{"status": "failed", "error": "insufficient_funds"}'
FROM subscriptions s
WHERE s.status = 'paused'
LIMIT 2;

-- Insert sample audit logs
INSERT INTO audit_logs (user_id, action_type, entity_type, entity_id, details, ip_address, user_agent)
SELECT 
    u.user_id,
    'CREATE',
    'user',
    u.user_id,
    'User account created',
    '192.168.1.' || (random() * 255)::int,
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
FROM users u
WHERE u.user_role = 'user';

INSERT INTO audit_logs (user_id, action_type, entity_type, entity_id, details, ip_address, user_agent)
SELECT 
    s.user_id,
    'CREATE',
    'subscription',
    s.subscription_id,
    'Subscription created for ' || p.name,
    '192.168.1.' || (random() * 255)::int,
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
FROM subscriptions s
JOIN products p ON s.product_id = p.product_id;

INSERT INTO audit_logs (user_id, action_type, entity_type, entity_id, details, ip_address, user_agent)
SELECT 
    s.user_id,
    'UPDATE',
    'subscription',
    s.subscription_id,
    'Subscription status changed to ' || s.status,
    '192.168.1.' || (random() * 255)::int,
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
FROM subscriptions s
WHERE s.status IN ('paused', 'canceled');

INSERT INTO audit_logs (user_id, action_type, entity_type, entity_id, details, ip_address, user_agent)
SELECT 
    p.user_id,
    'CREATE',
    'payment',
    p.payment_id,
    'Payment processed: ' || p.payment_status,
    '192.168.1.' || (random() * 255)::int,
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
FROM payments p;

-- Insert admin audit logs
INSERT INTO audit_logs (user_id, action_type, entity_type, entity_id, details, ip_address, user_agent)
SELECT 
    (SELECT user_id FROM users WHERE email = 'admin@subscriptionpro.com'),
    'VIEW',
    'dashboard',
    null,
    'Admin accessed dashboard',
    '10.0.0.1',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
FROM generate_series(1, 10);

INSERT INTO audit_logs (user_id, action_type, entity_type, entity_id, details, ip_address, user_agent)
SELECT 
    (SELECT user_id FROM users WHERE email = 'admin@subscriptionpro.com'),
    'VIEW',
    'users',
    null,
    'Admin viewed user list',
    '10.0.0.1',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
FROM generate_series(1, 5);

-- Update timestamps to create realistic data spread
UPDATE subscriptions SET 
    created_at = created_at - (random() * interval '30 days'),
    updated_at = created_at
WHERE created_at IS NOT NULL;

UPDATE payments SET 
    created_at = created_at - (random() * interval '30 days'),
    updated_at = created_at
WHERE created_at IS NOT NULL;

UPDATE audit_logs SET 
    timestamp = timestamp - (random() * interval '30 days')
WHERE timestamp IS NOT NULL;

-- Create some historical data for reporting
INSERT INTO audit_logs (user_id, action_type, entity_type, details, ip_address, timestamp)
SELECT 
    (SELECT user_id FROM users WHERE email = 'admin@subscriptionpro.com'),
    'REPORT',
    'revenue',
    'Monthly revenue: ₹' || (random() * 100000 + 50000)::int,
    '10.0.0.1',
    date_trunc('month', current_date) - interval '1 month' * generate_series(1, 12)
FROM generate_series(1, 12);

-- Add some subscription modifications by admin
INSERT INTO audit_logs (user_id, action_type, entity_type, entity_id, details, ip_address, user_agent)
SELECT 
    (SELECT user_id FROM users WHERE email = 'admin@subscriptionpro.com'),
    'UPDATE',
    'subscription',
    s.subscription_id,
    'Admin modified subscription: changed frequency to ' || s.frequency,
    '10.0.0.1',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
FROM subscriptions s
WHERE s.status = 'active'
LIMIT 3;

-- Add some user profile updates
INSERT INTO audit_logs (user_id, action_type, entity_type, entity_id, details, ip_address, user_agent)
SELECT 
    u.user_id,
    'UPDATE',
    'user',
    u.user_id,
    'Profile information updated',
    '192.168.1.' || (random() * 255)::int,
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
FROM users u
WHERE u.user_role = 'user'
AND random() < 0.3;

-- Add login audit logs
INSERT INTO audit_logs (user_id, action_type, entity_type, details, ip_address, user_agent, timestamp)
SELECT 
    u.user_id,
    'LOGIN',
    'auth',
    'User logged in',
    '192.168.1.' || (random() * 255)::int,
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    current_timestamp - (random() * interval '7 days')
FROM users u
WHERE u.user_role = 'user'
AND random() < 0.8;

-- Add admin login logs
INSERT INTO audit_logs (user_id, action_type, entity_type, details, ip_address, user_agent, timestamp)
SELECT 
    (SELECT user_id FROM users WHERE email = 'admin@subscriptionpro.com'),
    'LOGIN',
    'auth',
    'Admin logged in',
    '10.0.0.1',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
    current_timestamp - (random() * interval '7 days')
FROM generate_series(1, 20);

-- Summary of sample data created:
-- Products: 20 total (5 original + 15 new)
-- Users: 11 total (1 admin + 10 regular users)
-- Subscriptions: 10 total (7 active, 2 paused, 1 canceled)
-- Payments: Multiple payments for active subscriptions + some failed payments
-- Audit Logs: Comprehensive logs for all activities including user actions, admin actions, logins, and system events

-- Display summary
SELECT 
    'Products' as entity,
    count(*) as total,
    count(*) filter (where is_active = true) as active
FROM products
UNION ALL
SELECT 
    'Users' as entity,
    count(*) as total,
    count(*) filter (where user_role = 'user') as regular_users
FROM users
UNION ALL
SELECT 
    'Subscriptions' as entity,
    count(*) as total,
    count(*) filter (where status = 'active') as active
FROM subscriptions
UNION ALL
SELECT 
    'Payments' as entity,
    count(*) as total,
    count(*) filter (where payment_status = 'completed') as completed
FROM payments
UNION ALL
SELECT 
    'Audit Logs' as entity,
    count(*) as total,
    count(*) filter (where timestamp >= current_date - interval '7 days') as recent
FROM audit_logs;

