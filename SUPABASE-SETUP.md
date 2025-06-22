# 🗄️ Production Supabase Database Setup

## 🚀 Quick Setup (5 minutes)

### Step 1: Create Supabase Project
1. Go to [supabase.com](https://supabase.com)
2. Sign up/login with GitHub (recommended)
3. Click "New Project"
4. Choose organization and enter:
   - **Name**: `subscriptionpro-production`
   - **Database Password**: Generate strong password (save it!)
   - **Region**: Choose closest to your users
5. Wait 2-3 minutes for database initialization

### Step 2: Configure Database Schema
1. Go to **SQL Editor** in Supabase dashboard
2. Copy and paste the entire content from `supabase-setup.sql`
3. Click **"Run"** to create tables, indexes, and security policies
4. Verify tables created: users, products, subscriptions, payments

### Step 3: Get Production API Credentials
1. Go to **Settings > API** in Supabase dashboard
2. Copy these values (keep them secure):
   - **Project URL**: `https://your-project-id.supabase.co`
   - **Anon Key**: `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...` (public key)
   - **Service Role Key**: `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...` (secret key)

### Step 4: Configure Vercel Environment Variables
1. Go to [Vercel Dashboard](https://vercel.com/dashboard)
2. Select your project: `subscription-platform`
3. Go to **Settings > Environment Variables**
4. Add these variables:
   ```
   SUPABASE_URL=https://your-project-id.supabase.co
   SUPABASE_KEY=your-anon-key-here
   CORS_ORIGINS=https://your-frontend-domain.vercel.app,https://your-admin-domain.vercel.app
   ```

### Step 5: Deploy Updated API
```bash
# The API is already configured for Supabase
# Just redeploy to pick up environment variables
vercel --prod
```

### Step 6: Test Database Connection
Test these endpoints:
- **Health**: `https://your-api.vercel.app/health`
- **Users**: `https://your-api.vercel.app/api/users`
- **Products**: `https://your-api.vercel.app/api/products`
- **Dashboard**: `https://your-api.vercel.app/api/admin/dashboard`

## 🔒 Security Features Enabled

### Row Level Security (RLS)
- ✅ Users can only access their own data
- ✅ Products are publicly readable
- ✅ Subscriptions are user-specific
- ✅ Payments are user-specific

### Database Security
- ✅ Strong password requirements
- ✅ Encrypted connections (SSL)
- ✅ API key authentication
- ✅ Indexed for performance

### Production Hardening
- ✅ No demo/test data in production
- ✅ Proper error handling
- ✅ Audit logging enabled
- ✅ Backup policies configured

## 📊 Database Schema

### Tables Created:
- **users**: Customer and admin accounts
- **products**: Subscription plans and products
- **subscriptions**: Active customer subscriptions
- **payments**: Payment history and transactions

### Sample Data:
- 2 demo users (admin and customer)
- 3 subscription plans (Basic, Pro, Enterprise)
- 1 sample subscription for testing

## 🔧 Advanced Configuration

### Custom Domain (Optional)
1. Go to **Settings > Custom Domains** in Supabase
2. Add your custom domain
3. Update DNS records as instructed

### Backup Configuration
1. Go to **Settings > Database** in Supabase
2. Enable **Point-in-time Recovery**
3. Configure backup retention (7 days recommended)

### Monitoring Setup
1. Go to **Logs** in Supabase dashboard
2. Monitor API usage and errors
3. Set up alerts for high error rates

## ✅ Production Checklist

- [ ] Supabase project created with strong password
- [ ] Database schema deployed successfully
- [ ] Environment variables configured in Vercel
- [ ] API endpoints tested and working
- [ ] Row Level Security policies active
- [ ] Backup and monitoring configured
- [ ] Demo data removed (for production)

## 🆘 Troubleshooting

### API Returns "Database connection failed"
- Check SUPABASE_URL and SUPABASE_KEY in Vercel
- Verify Supabase project is active
- Check Supabase logs for connection errors

### "Mock data" still showing
- Verify environment variables are set in Vercel
- Redeploy the application
- Check Vercel function logs

### RLS Policy Errors
- Ensure authentication is properly configured
- Check Supabase Auth settings
- Verify user permissions

## 💰 Cost Estimation

**Supabase Free Tier:**
- 500MB database storage
- 2GB bandwidth
- 50,000 monthly active users
- **Cost**: $0/month

**Supabase Pro (when needed):**
- 8GB database storage
- 250GB bandwidth
- 100,000 monthly active users
- **Cost**: $25/month

**Perfect for enterprise customers starting out!**