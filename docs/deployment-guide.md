# Deployment Guide for SubscriptionPro Platform

This comprehensive guide provides step-by-step instructions for deploying the SubscriptionPro subscription platform across multiple cloud providers and environments.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Local Development Setup](#local-development-setup)
3. [Docker Deployment](#docker-deployment)
4. [AWS Deployment](#aws-deployment)
5. [Google Cloud Platform Deployment](#google-cloud-platform-deployment)
6. [Microsoft Azure Deployment](#microsoft-azure-deployment)
7. [Firebase Deployment](#firebase-deployment)
8. [CI/CD Pipeline Setup](#cicd-pipeline-setup)
9. [Monitoring and Logging](#monitoring-and-logging)
10. [Security Considerations](#security-considerations)
11. [Troubleshooting](#troubleshooting)

## Prerequisites

Before deploying the SubscriptionPro platform, ensure you have the following tools and accounts:

### Required Tools
- Docker and Docker Compose (v20.10+)
- Node.js (v18+) and pnpm
- Python (v3.11+) and pip
- Git
- kubectl (for Kubernetes deployments)
- Terraform (optional, for infrastructure as code)

### Required Accounts
- Cloud provider account (AWS, GCP, Azure, or Firebase)
- Razorpay account for payment processing
- Domain name and SSL certificate (for production)
- Email service provider (optional, for notifications)

### Environment Variables

Copy the `.env.example` file to `.env` and update the following variables:

```bash
# Database Configuration
DB_PASSWORD=your-secure-database-password
REDIS_PASSWORD=your-secure-redis-password

# Backend Configuration
SECRET_KEY=your-super-secret-key-minimum-32-characters
JWT_SECRET_KEY=your-jwt-secret-key-minimum-32-characters

# Payment Gateway Configuration
RAZORPAY_KEY_ID=your_razorpay_key_id
RAZORPAY_KEY_SECRET=your_razorpay_key_secret

# Frontend Configuration
REACT_APP_API_URL=https://your-api-domain.com
CORS_ORIGINS=https://your-user-portal.com,https://your-admin-portal.com
```

## Local Development Setup

### 1. Clone the Repository

```bash
git clone <repository-url>
cd subscription-platform
```

### 2. Install Dependencies

```bash
# Backend dependencies
cd backend/subscription-api
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Frontend dependencies
cd ../../frontend/user-portal
pnpm install

cd ../admin-portal
pnpm install
```

### 3. Database Setup

```bash
# Start PostgreSQL locally or use Docker
docker run --name postgres-dev -e POSTGRES_PASSWORD=postgres123 -e POSTGRES_DB=subscription_platform -p 5432:5432 -d postgres:15

# Run database migrations
cd backend/subscription-api
python src/database/migrate.py
```

### 4. Start Development Servers

```bash
# Terminal 1: Backend
cd backend/subscription-api
source venv/bin/activate
python src/main.py

# Terminal 2: User Portal
cd frontend/user-portal
pnpm run dev

# Terminal 3: Admin Portal
cd frontend/admin-portal
pnpm run dev
```

## Docker Deployment

### 1. Build and Start Services

```bash
# Copy environment variables
cp .env.example .env
# Edit .env with your configuration

# Build and start all services
docker-compose up -d --build

# Check service status
docker-compose ps

# View logs
docker-compose logs -f
```

### 2. Access the Applications

- User Portal: http://localhost:3000
- Admin Portal: http://localhost:3001
- Backend API: http://localhost:5000
- Database: localhost:5432

### 3. Production Docker Deployment

```bash
# Use production compose file
docker-compose -f docker-compose.prod.yml up -d --build

# Scale services if needed
docker-compose -f docker-compose.prod.yml up -d --scale backend=3
```

## AWS Deployment

### Option 1: AWS ECS with Fargate

#### 1. Create ECS Cluster

```bash
# Install AWS CLI and configure credentials
aws configure

# Create ECS cluster
aws ecs create-cluster --cluster-name subscription-platform

# Create task definitions
aws ecs register-task-definition --cli-input-json file://aws/task-definition-backend.json
aws ecs register-task-definition --cli-input-json file://aws/task-definition-frontend.json
```

#### 2. Deploy Services

```bash
# Create services
aws ecs create-service \
  --cluster subscription-platform \
  --service-name backend-service \
  --task-definition subscription-backend:1 \
  --desired-count 2 \
  --launch-type FARGATE \
  --network-configuration "awsvpcConfiguration={subnets=[subnet-12345],securityGroups=[sg-12345],assignPublicIp=ENABLED}"

aws ecs create-service \
  --cluster subscription-platform \
  --service-name frontend-service \
  --task-definition subscription-frontend:1 \
  --desired-count 2 \
  --launch-type FARGATE
```

#### 3. Setup Load Balancer

```bash
# Create Application Load Balancer
aws elbv2 create-load-balancer \
  --name subscription-alb \
  --subnets subnet-12345 subnet-67890 \
  --security-groups sg-12345

# Create target groups and listeners
aws elbv2 create-target-group \
  --name backend-targets \
  --protocol HTTP \
  --port 5000 \
  --vpc-id vpc-12345 \
  --target-type ip
```

### Option 2: AWS EKS (Kubernetes)

#### 1. Create EKS Cluster

```bash
# Install eksctl
curl --silent --location "https://github.com/weaveworks/eksctl/releases/latest/download/eksctl_$(uname -s)_amd64.tar.gz" | tar xz -C /tmp
sudo mv /tmp/eksctl /usr/local/bin

# Create cluster
eksctl create cluster \
  --name subscription-platform \
  --version 1.24 \
  --region us-west-2 \
  --nodegroup-name standard-workers \
  --node-type t3.medium \
  --nodes 3 \
  --nodes-min 1 \
  --nodes-max 4
```

#### 2. Deploy Applications

```bash
# Apply Kubernetes manifests
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/secrets.yaml
kubectl apply -f k8s/database.yaml
kubectl apply -f k8s/backend.yaml
kubectl apply -f k8s/frontend.yaml
kubectl apply -f k8s/ingress.yaml

# Check deployment status
kubectl get pods -n subscription-platform
kubectl get services -n subscription-platform
```

### Option 3: AWS Lambda (Serverless)

#### 1. Install Serverless Framework

```bash
npm install -g serverless
serverless plugin install -n serverless-python-requirements
serverless plugin install -n serverless-wsgi
```

#### 2. Deploy Backend

```bash
cd backend/subscription-api
serverless deploy --stage prod

# Deploy frontend to S3 + CloudFront
cd ../../frontend/user-portal
npm run build
aws s3 sync dist/ s3://your-bucket-name --delete
aws cloudfront create-invalidation --distribution-id YOUR_DISTRIBUTION_ID --paths "/*"
```

## Google Cloud Platform Deployment

### Option 1: Google Cloud Run

#### 1. Setup GCP Project

```bash
# Install gcloud CLI and authenticate
gcloud auth login
gcloud config set project your-project-id

# Enable required APIs
gcloud services enable run.googleapis.com
gcloud services enable sql-admin.googleapis.com
gcloud services enable container.googleapis.com
```

#### 2. Deploy Database

```bash
# Create Cloud SQL instance
gcloud sql instances create subscription-db \
  --database-version=POSTGRES_13 \
  --tier=db-f1-micro \
  --region=us-central1

# Create database and user
gcloud sql databases create subscription_platform --instance=subscription-db
gcloud sql users create appuser --instance=subscription-db --password=your-password
```

#### 3. Deploy Backend

```bash
cd backend/subscription-api

# Build and push container
gcloud builds submit --tag gcr.io/your-project-id/subscription-backend

# Deploy to Cloud Run
gcloud run deploy subscription-backend \
  --image gcr.io/your-project-id/subscription-backend \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars DATABASE_URL="postgresql://appuser:password@/subscription_platform?host=/cloudsql/your-project-id:us-central1:subscription-db" \
  --add-cloudsql-instances your-project-id:us-central1:subscription-db
```

#### 4. Deploy Frontend

```bash
cd frontend/user-portal

# Build and deploy to Firebase Hosting
npm install -g firebase-tools
firebase login
firebase init hosting
npm run build
firebase deploy --only hosting
```

### Option 2: Google Kubernetes Engine (GKE)

#### 1. Create GKE Cluster

```bash
# Create cluster
gcloud container clusters create subscription-platform \
  --zone us-central1-a \
  --num-nodes 3 \
  --enable-autoscaling \
  --min-nodes 1 \
  --max-nodes 10

# Get credentials
gcloud container clusters get-credentials subscription-platform --zone us-central1-a
```

#### 2. Deploy Applications

```bash
# Apply Kubernetes manifests
kubectl apply -f k8s/
kubectl get services
kubectl get ingress
```

## Microsoft Azure Deployment

### Option 1: Azure Container Instances

#### 1. Setup Azure CLI

```bash
# Install Azure CLI and login
az login
az account set --subscription "your-subscription-id"

# Create resource group
az group create --name subscription-platform-rg --location eastus
```

#### 2. Deploy Database

```bash
# Create Azure Database for PostgreSQL
az postgres server create \
  --resource-group subscription-platform-rg \
  --name subscription-db-server \
  --location eastus \
  --admin-user adminuser \
  --admin-password YourPassword123! \
  --sku-name GP_Gen5_2

# Create database
az postgres db create \
  --resource-group subscription-platform-rg \
  --server-name subscription-db-server \
  --name subscription_platform
```

#### 3. Deploy Containers

```bash
# Create container registry
az acr create --resource-group subscription-platform-rg --name subscriptionacr --sku Basic

# Build and push images
az acr build --registry subscriptionacr --image subscription-backend:latest backend/subscription-api/
az acr build --registry subscriptionacr --image subscription-frontend:latest frontend/user-portal/

# Deploy container group
az container create \
  --resource-group subscription-platform-rg \
  --name subscription-platform \
  --image subscriptionacr.azurecr.io/subscription-backend:latest \
  --dns-name-label subscription-platform \
  --ports 5000
```

### Option 2: Azure Kubernetes Service (AKS)

#### 1. Create AKS Cluster

```bash
# Create AKS cluster
az aks create \
  --resource-group subscription-platform-rg \
  --name subscription-aks \
  --node-count 3 \
  --enable-addons monitoring \
  --generate-ssh-keys

# Get credentials
az aks get-credentials --resource-group subscription-platform-rg --name subscription-aks
```

#### 2. Deploy Applications

```bash
# Apply Kubernetes manifests
kubectl apply -f k8s/
kubectl get services --watch
```

## Firebase Deployment

### Frontend Deployment

#### 1. Setup Firebase

```bash
# Install Firebase CLI
npm install -g firebase-tools
firebase login

# Initialize project
firebase init

# Select:
# - Hosting
# - Functions (optional, for serverless backend)
# - Firestore (optional, for NoSQL database)
```

#### 2. Deploy User Portal

```bash
cd frontend/user-portal

# Build application
npm run build

# Configure firebase.json
{
  "hosting": {
    "public": "dist",
    "ignore": ["firebase.json", "**/.*", "**/node_modules/**"],
    "rewrites": [
      {
        "source": "**",
        "destination": "/index.html"
      }
    ]
  }
}

# Deploy
firebase deploy --only hosting
```

#### 3. Deploy Admin Portal

```bash
cd frontend/admin-portal

# Build and deploy to different Firebase project or site
firebase use --add  # Add another project
npm run build
firebase deploy --only hosting
```

### Backend Deployment (Firebase Functions)

```bash
cd backend/subscription-api

# Convert Flask app to Firebase Functions
# Create functions/main.py with Firebase Functions wrapper

firebase deploy --only functions
```

## CI/CD Pipeline Setup

### GitHub Actions

Create `.github/workflows/deploy.yml`:

```yaml
name: Deploy SubscriptionPro

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: |
          cd backend/subscription-api
          pip install -r requirements.txt
      - name: Run tests
        run: |
          cd backend/subscription-api
          python -m pytest tests/

  build-and-deploy:
    needs: test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    steps:
      - uses: actions/checkout@v3
      
      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v2
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: us-west-2

      - name: Login to Amazon ECR
        id: login-ecr
        uses: aws-actions/amazon-ecr-login@v1

      - name: Build and push backend image
        env:
          ECR_REGISTRY: ${{ steps.login-ecr.outputs.registry }}
          ECR_REPOSITORY: subscription-backend
          IMAGE_TAG: ${{ github.sha }}
        run: |
          cd backend/subscription-api
          docker build -t $ECR_REGISTRY/$ECR_REPOSITORY:$IMAGE_TAG .
          docker push $ECR_REGISTRY/$ECR_REPOSITORY:$IMAGE_TAG

      - name: Deploy to ECS
        run: |
          aws ecs update-service --cluster subscription-platform --service backend-service --force-new-deployment
```

### GitLab CI/CD

Create `.gitlab-ci.yml`:

```yaml
stages:
  - test
  - build
  - deploy

variables:
  DOCKER_DRIVER: overlay2

test:
  stage: test
  image: python:3.11
  script:
    - cd backend/subscription-api
    - pip install -r requirements.txt
    - python -m pytest tests/

build:
  stage: build
  image: docker:latest
  services:
    - docker:dind
  script:
    - docker build -t $CI_REGISTRY_IMAGE/backend:$CI_COMMIT_SHA backend/subscription-api/
    - docker push $CI_REGISTRY_IMAGE/backend:$CI_COMMIT_SHA
  only:
    - main

deploy:
  stage: deploy
  image: google/cloud-sdk:alpine
  script:
    - echo $GCP_SERVICE_KEY | base64 -d > gcp-key.json
    - gcloud auth activate-service-account --key-file gcp-key.json
    - gcloud config set project $GCP_PROJECT_ID
    - gcloud run deploy subscription-backend --image $CI_REGISTRY_IMAGE/backend:$CI_COMMIT_SHA --region us-central1
  only:
    - main
```

## Monitoring and Logging

### Application Monitoring

#### 1. Setup Prometheus and Grafana

```yaml
# docker-compose.monitoring.yml
version: '3.8'
services:
  prometheus:
    image: prom/prometheus
    ports:
      - "9090:9090"
    volumes:
      - ./monitoring/prometheus.yml:/etc/prometheus/prometheus.yml

  grafana:
    image: grafana/grafana
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
    volumes:
      - grafana-storage:/var/lib/grafana

volumes:
  grafana-storage:
```

#### 2. Setup Application Metrics

Add to Flask backend:

```python
from prometheus_flask_exporter import PrometheusMetrics

app = Flask(__name__)
metrics = PrometheusMetrics(app)

# Custom metrics
subscription_counter = Counter('subscriptions_total', 'Total subscriptions created')
payment_histogram = Histogram('payment_duration_seconds', 'Payment processing time')
```

### Centralized Logging

#### 1. ELK Stack Setup

```yaml
# docker-compose.logging.yml
version: '3.8'
services:
  elasticsearch:
    image: docker.elastic.co/elasticsearch/elasticsearch:8.5.0
    environment:
      - discovery.type=single-node
      - xpack.security.enabled=false
    ports:
      - "9200:9200"

  logstash:
    image: docker.elastic.co/logstash/logstash:8.5.0
    volumes:
      - ./logging/logstash.conf:/usr/share/logstash/pipeline/logstash.conf
    ports:
      - "5044:5044"

  kibana:
    image: docker.elastic.co/kibana/kibana:8.5.0
    ports:
      - "5601:5601"
    environment:
      - ELASTICSEARCH_HOSTS=http://elasticsearch:9200
```

#### 2. Application Logging Configuration

```python
import logging
from pythonjsonlogger import jsonlogger

# Configure structured logging
logHandler = logging.StreamHandler()
formatter = jsonlogger.JsonFormatter()
logHandler.setFormatter(formatter)
logger = logging.getLogger()
logger.addHandler(logHandler)
logger.setLevel(logging.INFO)
```

### Health Checks and Alerts

#### 1. Health Check Endpoints

```python
@app.route('/health')
def health_check():
    try:
        # Check database connection
        db.session.execute('SELECT 1')
        
        # Check Redis connection
        redis_client.ping()
        
        return {'status': 'healthy', 'timestamp': datetime.utcnow().isoformat()}
    except Exception as e:
        return {'status': 'unhealthy', 'error': str(e)}, 500

@app.route('/ready')
def readiness_check():
    # Check if application is ready to serve traffic
    return {'status': 'ready'}
```

#### 2. Alerting with Alertmanager

```yaml
# alertmanager.yml
global:
  smtp_smarthost: 'localhost:587'
  smtp_from: 'alerts@subscriptionpro.com'

route:
  group_by: ['alertname']
  group_wait: 10s
  group_interval: 10s
  repeat_interval: 1h
  receiver: 'web.hook'

receivers:
- name: 'web.hook'
  email_configs:
  - to: 'admin@subscriptionpro.com'
    subject: 'SubscriptionPro Alert: {{ .GroupLabels.alertname }}'
    body: |
      {{ range .Alerts }}
      Alert: {{ .Annotations.summary }}
      Description: {{ .Annotations.description }}
      {{ end }}
```

## Security Considerations

### 1. Environment Security

```bash
# Use secrets management
# AWS Secrets Manager
aws secretsmanager create-secret --name subscription-platform/db-password --secret-string "your-secure-password"

# Google Secret Manager
gcloud secrets create db-password --data-file=password.txt

# Azure Key Vault
az keyvault secret set --vault-name subscription-vault --name db-password --value "your-secure-password"
```

### 2. Network Security

```yaml
# Security groups / firewall rules
# Allow only necessary ports
- Port 80/443: Public access for web traffic
- Port 5432: Database access from application only
- Port 6379: Redis access from application only
```

### 3. Application Security

```python
# Rate limiting
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(
    app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)

@app.route('/api/auth/login', methods=['POST'])
@limiter.limit("5 per minute")
def login():
    # Login logic
    pass
```

### 4. SSL/TLS Configuration

```bash
# Generate SSL certificates with Let's Encrypt
certbot certonly --webroot -w /var/www/html -d your-domain.com

# Or use cloud provider certificates
# AWS Certificate Manager
aws acm request-certificate --domain-name your-domain.com

# Google Cloud SSL
gcloud compute ssl-certificates create subscription-ssl --domains your-domain.com
```

## Troubleshooting

### Common Issues

#### 1. Database Connection Issues

```bash
# Check database connectivity
docker exec -it subscription-db psql -U postgres -d subscription_platform

# Check connection from application
docker exec -it subscription-backend python -c "
from src.database import db
try:
    db.session.execute('SELECT 1')
    print('Database connection successful')
except Exception as e:
    print(f'Database connection failed: {e}')
"
```

#### 2. Memory and Performance Issues

```bash
# Monitor container resources
docker stats

# Check application logs
docker logs subscription-backend --tail 100

# Monitor database performance
docker exec -it subscription-db psql -U postgres -c "
SELECT query, calls, total_time, mean_time 
FROM pg_stat_statements 
ORDER BY total_time DESC 
LIMIT 10;
"
```

#### 3. Frontend Build Issues

```bash
# Clear cache and rebuild
cd frontend/user-portal
rm -rf node_modules package-lock.json
npm install
npm run build

# Check for environment variable issues
echo $REACT_APP_API_URL
```

#### 4. Payment Gateway Issues

```bash
# Test Razorpay connectivity
curl -X POST https://api.razorpay.com/v1/orders \
  -H "Content-Type: application/json" \
  -u "your_key_id:your_key_secret" \
  -d '{
    "amount": 100,
    "currency": "INR",
    "receipt": "test_receipt"
  }'
```

### Debugging Commands

```bash
# View all container logs
docker-compose logs -f

# Execute commands in containers
docker exec -it subscription-backend bash
docker exec -it subscription-db psql -U postgres

# Check network connectivity
docker network ls
docker network inspect subscription-platform_subscription-network

# Monitor resource usage
docker system df
docker system prune -a  # Clean up unused resources
```

### Performance Optimization

#### 1. Database Optimization

```sql
-- Add indexes for frequently queried columns
CREATE INDEX CONCURRENTLY idx_subscriptions_user_status ON subscriptions(user_id, status);
CREATE INDEX CONCURRENTLY idx_payments_created_at ON payments(created_at);

-- Analyze query performance
EXPLAIN ANALYZE SELECT * FROM subscriptions WHERE user_id = 'uuid' AND status = 'active';
```

#### 2. Application Optimization

```python
# Use connection pooling
from sqlalchemy import create_engine
from sqlalchemy.pool import QueuePool

engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=20,
    max_overflow=30,
    pool_pre_ping=True
)

# Implement caching
from flask_caching import Cache

cache = Cache(app, config={'CACHE_TYPE': 'redis'})

@cache.memoize(timeout=300)
def get_user_subscriptions(user_id):
    return Subscription.query.filter_by(user_id=user_id).all()
```

#### 3. Frontend Optimization

```javascript
// Code splitting
const Dashboard = lazy(() => import('./pages/Dashboard'));
const Subscriptions = lazy(() => import('./pages/Subscriptions'));

// Optimize bundle size
// Use webpack-bundle-analyzer
npm install --save-dev webpack-bundle-analyzer
npm run build -- --analyze
```

This comprehensive deployment guide provides multiple options for deploying the SubscriptionPro platform across different environments and cloud providers. Choose the deployment method that best fits your requirements, budget, and technical expertise.

For production deployments, always ensure proper security measures, monitoring, and backup strategies are in place. Regular security updates and performance monitoring are essential for maintaining a robust subscription platform.




### Firebase Backend Deployment (Firebase Functions)

Deploying the Flask backend to Firebase Functions requires wrapping the Flask application within a Firebase Function. This allows you to leverage Firebase's serverless infrastructure for your backend API.

#### 1. Initialize Firebase Functions

Navigate to your `backend/subscription-api` directory and initialize Firebase Functions. If you haven't already, ensure you have the Firebase CLI installed (`npm install -g firebase-tools`).

```bash
cd backend/subscription-api
firebase init functions
```

During initialization, select Python as your language and choose to install dependencies with `pip`. This will create a `functions` directory with a `main.py` and `requirements.txt` file.

#### 2. Adapt Flask Application for Firebase Functions

Modify the `functions/main.py` file to serve your Flask application. You'll need to import your Flask app instance and use `firebase_functions.https.on_request` to handle HTTP requests.

First, ensure your Flask app is accessible from `main.py`. You might need to adjust your project structure or import paths. A common approach is to have a `create_app()` function in your Flask application's `src/main.py`.

**`backend/subscription-api/functions/main.py`**
```python
import os
import sys
from firebase_functions import https_fn
from firebase_admin import initialize_app

# Add the parent directory to the Python path to import your Flask app
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Initialize Firebase Admin SDK
initialize_app()

# Import your Flask app instance
# Assuming your Flask app is created by a function called create_app in src/main.py
from src.main import create_app

flask_app = create_app()

@https_fn.on_request()
def api(request):
    with flask_app.request_context(request):
        return flask_app.full_dispatch_request()

```

#### 3. Update `requirements.txt` for Firebase Functions

Copy the dependencies from your Flask application's `requirements.txt` to the `functions/requirements.txt` file. Also, add `firebase-functions` and `firebase-admin`.

**`backend/subscription-api/functions/requirements.txt`**
```
Flask
Flask-SQLAlchemy
psycopg2-binary
Flask-CORS
Flask-JWT-Extended
razorpay
firebase-functions
firebase-admin
```

#### 4. Configure `firebase.json`

Ensure your `firebase.json` in the root of your `subscription-platform` directory is configured to deploy the functions. It should look something like this:

**`firebase.json` (root directory)**
```json
{
  "hosting": {
    "public": "frontend/user-portal/dist",
    "ignore": [
      "firebase.json",
      "**/.*",
      "**/node_modules/**"
    ],
    "rewrites": [
      {
        "source": "/api/**",
        "function": "api"
      },
      {
        "source": "**",
        "destination": "/index.html"
      }
    ]
  },
  "functions": {
    "source": "backend/subscription-api/functions",
    "runtime": "python311"
  }
}
```

This configuration routes all requests starting with `/api/` to your `api` Firebase Function, and all other requests to your user portal frontend.

#### 5. Deploy to Firebase

From the root of your `subscription-platform` directory, deploy your functions and hosting:

```bash
firebase deploy --only functions,hosting
```

This command will build and deploy your Flask backend as a Firebase Function and your React frontend to Firebase Hosting. Your backend API will be accessible via a Firebase Functions URL (e.g., `https://your-project-id.cloudfunctions.net/api`) and your frontend will be served from Firebase Hosting (e.g., `https://your-project-id.web.app`).

**Important Considerations for Firebase Functions:**
- **Cold Starts**: Python functions can experience cold starts. For production, consider increasing memory or using a paid plan for better performance.
- **Environment Variables**: Manage sensitive information using Firebase Environment Configuration or Google Cloud Secret Manager.
- **Database Connectivity**: Ensure your Firebase Function has secure access to your PostgreSQL database. This might involve using Cloud SQL Proxy or configuring VPC access if your database is in a private network.
- **CORS**: Ensure your Flask application's CORS configuration (`CORS_ORIGINS`) includes your Firebase Hosting domain.



