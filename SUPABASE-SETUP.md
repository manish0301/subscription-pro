# 🗄️ Supabase Database Setup

## Step 1: Create Supabase Project
1. Go to [supabase.com](https://supabase.com)
2. Sign up/login
3. Create new project
4. Wait for database to initialize

## Step 2: Run SQL Setup
1. Go to SQL Editor in Supabase dashboard
2. Copy and paste content from `supabase-setup.sql`
3. Click "Run" to create tables and sample data

## Step 3: Get API Credentials
1. Go to Settings > API in Supabase
2. Copy:
   - Project URL
   - `anon` `public` key

## Step 4: Add to Vercel Environment
1. Go to Vercel dashboard > subscription-pro > Settings > Environment Variables
2. Add:
   - `SUPABASE_URL`: your-project-url
   - `SUPABASE_KEY`: your-anon-key

## Step 5: Update API Code
Replace `api/index.py` with `api/supabase.py`:
```bash
cp api/supabase.py api/index.py
```

## Step 6: Redeploy
```bash
vercel --prod
```

## ✅ Result:
- Real PostgreSQL database (500MB free)
- Live API with actual data
- Admin dashboard with real metrics

**Ready to set up Supabase?**