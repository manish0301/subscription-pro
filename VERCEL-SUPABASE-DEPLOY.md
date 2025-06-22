# 🚀 Vercel + Supabase Deployment (FREE)

## Step 1: Deploy Backend to Vercel (2 minutes)
```bash
npm install -g vercel
vercel login
vercel --prod
```

## Step 2: Setup Supabase Database (3 minutes)
1. Go to [supabase.com](https://supabase.com)
2. Create account + new project
3. Go to SQL Editor
4. Run this SQL:
```sql
CREATE TABLE users (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  email VARCHAR(255) UNIQUE NOT NULL,
  name VARCHAR(255),
  created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE products (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  name VARCHAR(255) NOT NULL,
  price DECIMAL(10,2) NOT NULL,
  created_at TIMESTAMP DEFAULT NOW()
);

INSERT INTO users (email, name) VALUES 
('admin@demo.com', 'Admin User'),
('user@demo.com', 'Test User');

INSERT INTO products (name, price) VALUES 
('Monthly Coffee', 299.00),
('Weekly Snacks', 199.00);
```

## Step 3: Connect Database (1 minute)
1. Get Supabase URL + API Key from Settings > API
2. Add to Vercel environment variables:
   - `SUPABASE_URL`: your-project-url
   - `SUPABASE_KEY`: your-anon-key

## Step 4: Deploy Frontend
```bash
cd frontend/user-portal
npm run build
vercel --prod
```

## ✅ Result:
- **Backend API**: https://your-app.vercel.app/api
- **Frontend**: https://your-frontend.vercel.app
- **Database**: Supabase PostgreSQL (free 500MB)

**Total Cost: $0/month**
**Setup Time: 6 minutes**

## Want me to help you deploy this now?