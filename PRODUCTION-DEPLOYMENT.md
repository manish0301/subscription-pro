# 🚀 Production Deployment Guide

## 📋 Pre-Deployment Checklist

### ✅ Security Requirements
- [ ] All hardcoded credentials removed
- [ ] Environment variables configured
- [ ] CORS policies set to production domains
- [ ] Rate limiting enabled
- [ ] Security headers implemented
- [ ] HTTPS enforced

### ✅ Database Setup
- [ ] Supabase project created
- [ ] Database schema deployed
- [ ] Row Level Security enabled
- [ ] Backup policies configured

### ✅ API Configuration
- [ ] Production API keys configured
- [ ] Error handling implemented
- [ ] Logging configured
- [ ] Health checks working

## 🗄️ Step 1: Setup Supabase Database

### 1.1 Create Supabase Project
1. Go to [supabase.com](https://supabase.com)
2. Create new project: `subscriptionpro-production`
3. Choose strong database password
4. Select region closest to users

### 1.2 Deploy Database Schema
1. Go to SQL Editor in Supabase
2. Copy content from `supabase-setup.sql`
3. Execute to create tables and security policies

### 1.3 Get Credentials
```bash
# From Supabase Settings > API
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_KEY=your-anon-key-here
```

## 🔧 Step 2: Deploy Backend API

### 2.1 Configure Vercel Environment Variables
1. Go to [Vercel Dashboard](https://vercel.com/dashboard)
2. Select your project
3. Go to Settings > Environment Variables
4. Add these variables:

```bash
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_KEY=your-anon-key-here
CORS_ORIGINS=https://your-user-portal.vercel.app,https://your-admin-portal.vercel.app
RATE_LIMIT_ENABLED=true
VERCEL_ENV=production
```

### 2.2 Deploy API
```bash
# The API is already configured in /api/index.py
# Just push to GitHub or deploy via Vercel CLI
vercel --prod
```

### 2.3 Test API Endpoints
```bash
# Health check
curl https://your-api.vercel.app/health

# API info
curl https://your-api.vercel.app/api/info

# Test with Supabase
curl https://your-api.vercel.app/api/products
```

## 🎨 Step 3: Deploy Frontend Applications

### 3.1 User Portal
```bash
cd frontend/user-portal

# Create environment file
cp .env.example .env.local

# Update with your API URL
echo "VITE_API_BASE_URL=https://your-api.vercel.app/api" > .env.local

# Deploy to Vercel
vercel --prod
```

### 3.2 Admin Portal
```bash
cd frontend/admin-portal

# Create environment file
cp .env.example .env.local

# Update with your API URL
echo "VITE_API_BASE_URL=https://your-api.vercel.app/api" > .env.local

# Deploy to Vercel
vercel --prod
```

## 🔒 Step 4: Security Configuration

### 4.1 Update CORS Origins
Update your API environment variables with actual frontend URLs:
```bash
CORS_ORIGINS=https://user-portal-xyz.vercel.app,https://admin-portal-abc.vercel.app
```

### 4.2 Configure Custom Domains (Optional)
1. Add custom domains in Vercel
2. Update DNS records
3. Update CORS_ORIGINS with custom domains

## 📊 Step 5: Monitoring & Testing

### 5.1 Test Complete Flow
1. **User Portal**: Registration, login, subscription creation
2. **Admin Portal**: Dashboard, user management, analytics
3. **API**: All endpoints with real data
4. **Database**: Data persistence and security

### 5.2 Performance Testing
```bash
# Test API performance
curl -w "@curl-format.txt" -o /dev/null -s https://your-api.vercel.app/api/products

# Test rate limiting
for i in {1..70}; do curl https://your-api.vercel.app/api/users; done
```

## 🎯 Production URLs

After deployment, you'll have:
- **Backend API**: `https://your-api.vercel.app`
- **User Portal**: `https://user-portal-xyz.vercel.app`
- **Admin Portal**: `https://admin-portal-abc.vercel.app`
- **Database**: `https://your-project.supabase.co`

## 🆘 Troubleshooting

### API Returns 404
- Check vercel.json configuration
- Verify API routes are correct
- Check Vercel function logs

### Database Connection Failed
- Verify SUPABASE_URL and SUPABASE_KEY
- Check Supabase project status
- Review RLS policies

### CORS Errors
- Update CORS_ORIGINS environment variable
- Ensure frontend URLs are correct
- Check browser developer tools

### Rate Limiting Issues
- Adjust rate limits in API code
- Check client IP detection
- Monitor rate limit logs

## 📈 Scaling Considerations

### Database
- Monitor Supabase usage
- Upgrade to Pro plan when needed
- Implement database indexing

### API
- Monitor Vercel function usage
- Implement caching if needed
- Consider CDN for static assets

### Frontend
- Optimize bundle sizes
- Implement lazy loading
- Use Vercel Edge Network

## 💰 Cost Estimation

**Free Tier (Development/Small Scale):**
- Supabase: Free (500MB, 50K users)
- Vercel: Free (100GB bandwidth)
- **Total**: $0/month

**Production Scale:**
- Supabase Pro: $25/month
- Vercel Pro: $20/month
- **Total**: $45/month

## ✅ Go-Live Checklist

- [ ] All services deployed and tested
- [ ] Custom domains configured (if applicable)
- [ ] SSL certificates active
- [ ] Monitoring and alerts set up
- [ ] Backup procedures tested
- [ ] Security scan completed
- [ ] Performance benchmarks met
- [ ] Documentation updated

**🎉 Your enterprise-grade subscription platform is now live!**
