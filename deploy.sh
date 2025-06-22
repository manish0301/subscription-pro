#!/bin/bash

# SubscriptionPro Deployment Script for Google Cloud + Firebase
set -e

echo "🚀 Starting SubscriptionPro deployment..."

# Set your project variables
PROJECT_ID="subscription-pro"
REGION="us-central1"
DB_INSTANCE_NAME="subscription-db"
DB_NAME="subscriptionpro"
DB_USER="subscriptionpro"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}Step 1: Setting up Google Cloud Project${NC}"
gcloud config set project $PROJECT_ID

echo -e "${YELLOW}Step 2: Enabling required APIs${NC}"
gcloud services enable cloudbuild.googleapis.com
gcloud services enable run.googleapis.com
gcloud services enable sql-admin.googleapis.com
gcloud services enable sqladmin.googleapis.com

echo -e "${YELLOW}Step 3: Creating Cloud SQL instance${NC}"
if ! gcloud sql instances describe $DB_INSTANCE_NAME --quiet 2>/dev/null; then
    echo "Creating Cloud SQL instance..."
    gcloud sql instances create $DB_INSTANCE_NAME \
        --database-version=POSTGRES_13 \
        --tier=db-f1-micro \
        --region=$REGION \
        --storage-auto-increase \
        --backup-start-time=03:00
    
    echo "Creating database and user..."
    gcloud sql databases create $DB_NAME --instance=$DB_INSTANCE_NAME
    gcloud sql users create $DB_USER --instance=$DB_INSTANCE_NAME --password=$(openssl rand -base64 32)
else
    echo "Cloud SQL instance already exists"
fi

echo -e "${YELLOW}Step 4: Building and deploying backend to Cloud Run${NC}"
cd backend/subscription-api

# Build and deploy
gcloud builds submit --tag gcr.io/$PROJECT_ID/subscription-api

# Deploy to Cloud Run
gcloud run deploy subscription-api \
    --image gcr.io/$PROJECT_ID/subscription-api \
    --platform managed \
    --region $REGION \
    --allow-unauthenticated \
    --set-env-vars "DATABASE_URL=postgresql://$DB_USER:PASSWORD@/$DB_NAME?host=/cloudsql/$PROJECT_ID:$REGION:$DB_INSTANCE_NAME" \
    --add-cloudsql-instances $PROJECT_ID:$REGION:$DB_INSTANCE_NAME \
    --memory 1Gi \
    --cpu 1 \
    --max-instances 10

# Get Cloud Run URL
BACKEND_URL=$(gcloud run services describe subscription-api --platform managed --region $REGION --format 'value(status.url)')

cd ../..

echo -e "${YELLOW}Step 5: Building frontend applications${NC}"

# Build user portal
echo "Building user portal..."
cd frontend/user-portal
npm install --legacy-peer-deps || yarn install
VITE_API_URL="/api" npm run build || yarn build
cd ../..

# Build admin portal  
echo "Building admin portal..."
cd frontend/admin-portal
npm install --legacy-peer-deps || yarn install
VITE_API_URL="/api" npm run build || yarn build
cd ../..

echo -e "${YELLOW}Step 6: Updating Firebase configuration${NC}"
# Update firebase.json with actual Cloud Run URL
sed -i.bak "s|https://subscription-api-REPLACE_WITH_CLOUD_RUN_URL.run.app|$BACKEND_URL|g" firebase.json

echo -e "${YELLOW}Step 7: Deploying to Firebase Hosting${NC}"
firebase deploy --only hosting

echo -e "${GREEN}✅ Deployment completed successfully!${NC}"
echo -e "${GREEN}Backend API: $BACKEND_URL${NC}"
echo -e "${GREEN}User Portal: https://$PROJECT_ID.web.app${NC}"
echo -e "${GREEN}Admin Portal: https://$PROJECT_ID-admin.web.app${NC}"

echo -e "${YELLOW}⚠️  Next steps:${NC}"
echo "1. Set up your Razorpay credentials in Cloud Run environment variables"
echo "2. Configure your database password in Cloud SQL"
echo "3. Set up custom domains in Firebase Hosting (optional)"
echo "4. Configure monitoring and logging"