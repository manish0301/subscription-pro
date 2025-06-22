# SubscriptionPro - Optimized Firebase/Google Cloud Deployment

## 🚀 Quick Deploy

**Prerequisites:**
- Google Cloud SDK installed and authenticated
- Firebase CLI installed and authenticated  
- Node.js 18+ installed

**One-command deployment:**
```bash
./deploy.sh
```

## 🏗️ Architecture Overview

**Optimized for Google Cloud + Firebase:**
- **Frontend**: Firebase Hosting (React SPAs)
- **Backend**: Google Cloud Run (Containerized Flask API)
- **Database**: Google Cloud SQL (PostgreSQL)
- **Storage**: Google Cloud Storage
- **CDN**: Firebase Hosting CDN

## 📋 Manual Deployment Steps

### 1. Setup Google Cloud Project
```bash
gcloud config set project subscription-pro
gcloud services enable cloudbuild.googleapis.com run.googleapis.com sql-admin.googleapis.com
```

### 2. Deploy Database
```bash
gcloud sql instances create subscription-db \
  --database-version=POSTGRES_13 \
  --tier=db-f1-micro \
  --region=us-central1

gcloud sql databases create subscriptionpro --instance=subscription-db
gcloud sql users create appuser --instance=subscription-db --password=YOUR_PASSWORD
```

### 3. Deploy Backend API
```bash
cd backend/subscription-api
gcloud builds submit --tag gcr.io/subscription-pro/subscription-api
gcloud run deploy subscription-api \
  --image gcr.io/subscription-pro/subscription-api \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --add-cloudsql-instances subscription-pro:us-central1:subscription-db
```

### 4. Build & Deploy Frontend
```bash
# User Portal
cd frontend/user-portal
npm install && npm run build

# Admin Portal  
cd frontend/admin-portal
npm install && npm run build

# Deploy to Firebase
firebase deploy --only hosting
```

## 🔧 Environment Variables

**Cloud Run Environment Variables:**
```bash
DATABASE_URL=postgresql://user:pass@/dbname?host=/cloudsql/project:region:instance
JWT_SECRET_KEY=your-jwt-secret-32-chars-minimum
RAZORPAY_KEY_ID=your_razorpay_key_id
RAZORPAY_KEY_SECRET=your_razorpay_key_secret
```

**Frontend Environment Variables:**
```bash
VITE_API_URL=/api
VITE_APP_NAME=SubscriptionPro
```

## 🌐 URLs After Deployment

- **User Portal**: https://subscription-pro.web.app
- **Admin Portal**: https://subscription-pro-admin.web.app  
- **Backend API**: https://subscription-api-[hash]-uc.a.run.app

## 🔒 Security Configuration

1. **Database Security**: Private IP, authorized networks only
2. **API Security**: CORS configured for Firebase domains
3. **Authentication**: JWT tokens with secure secrets
4. **HTTPS**: Enforced on all endpoints

## 📊 Monitoring & Logging

- **Cloud Run**: Automatic logging and monitoring
- **Cloud SQL**: Performance insights enabled
- **Firebase**: Analytics and performance monitoring
- **Error Tracking**: Cloud Error Reporting

## 🚨 Production Checklist

- [ ] Set strong database passwords
- [ ] Configure Razorpay production keys
- [ ] Set up custom domains
- [ ] Enable Cloud SQL backups
- [ ] Configure monitoring alerts
- [ ] Set up CI/CD pipeline
- [ ] Enable security scanning

## 💰 Cost Optimization

- **Cloud Run**: Pay per request, auto-scaling to zero
- **Cloud SQL**: f1-micro tier for development
- **Firebase Hosting**: Free tier for most use cases
- **Estimated monthly cost**: $10-50 for low-medium traffic

## 🔄 Updates & Maintenance

**Backend Updates:**
```bash
cd backend/subscription-api
gcloud builds submit --tag gcr.io/subscription-pro/subscription-api
gcloud run deploy subscription-api --image gcr.io/subscription-pro/subscription-api
```

**Frontend Updates:**
```bash
npm run build && firebase deploy --only hosting
```

## 🆘 Troubleshooting

**Common Issues:**
1. **Database Connection**: Check Cloud SQL instance status and connection string
2. **CORS Errors**: Verify Firebase domains in CORS configuration
3. **Build Failures**: Check Node.js version and dependencies
4. **API Errors**: Check Cloud Run logs: `gcloud logs read --service=subscription-api`

**Support:**
- Cloud Run logs: Google Cloud Console > Cloud Run > subscription-api > Logs
- Firebase logs: Firebase Console > Hosting > Usage
- Database logs: Google Cloud Console > SQL > subscription-db > Logs