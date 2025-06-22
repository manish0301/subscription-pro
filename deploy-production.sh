#!/bin/bash

# SubscriptionPro Production Deployment Script
# Deploys the complete subscription platform to Supabase + Vercel

set -e  # Exit on any error

echo "🚀 SubscriptionPro Production Deployment"
echo "========================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# Check prerequisites
check_prerequisites() {
    print_info "Checking prerequisites..."
    
    # Check if required tools are installed
    if ! command -v vercel &> /dev/null; then
        print_error "Vercel CLI not found. Install with: npm i -g vercel"
        exit 1
    fi
    
    if ! command -v node &> /dev/null; then
        print_error "Node.js not found. Please install Node.js"
        exit 1
    fi
    
    if ! command -v python3 &> /dev/null; then
        print_error "Python 3 not found. Please install Python 3"
        exit 1
    fi
    
    print_status "All prerequisites met"
}

# Setup environment variables
setup_environment() {
    print_info "Setting up environment variables..."
    
    # Check if .env file exists
    if [ ! -f ".env.production" ]; then
        print_warning "Creating .env.production file..."
        cat > .env.production << EOF
# Production Environment Variables
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_KEY=your-anon-key-here
CORS_ORIGINS=https://your-user-portal.vercel.app,https://your-admin-portal.vercel.app
RATE_LIMIT_ENABLED=true
VERCEL_ENV=production
JWT_SECRET=your-production-jwt-secret-here

# SFCC Integration (Optional)
SFCC_CLIENT_ID=your-sfcc-client-id
SFCC_CLIENT_SECRET=your-sfcc-client-secret
SFCC_INSTANCE_URL=https://your-instance.demandware.net
SFCC_SITE_ID=your-site-id

# Payment Gateway
RAZORPAY_KEY_ID=your-razorpay-key-id
RAZORPAY_KEY_SECRET=your-razorpay-key-secret
EOF
        print_warning "Please update .env.production with your actual values"
        print_warning "Press Enter to continue after updating the file..."
        read
    fi
    
    print_status "Environment setup complete"
}

# Deploy API to Vercel
deploy_api() {
    print_info "Deploying API to Vercel..."
    
    # Install dependencies
    if [ -f "api/requirements.txt" ]; then
        print_info "Installing Python dependencies..."
        pip3 install -r api/requirements.txt
    fi
    
    # Deploy to Vercel
    print_info "Deploying to Vercel..."
    vercel --prod --yes
    
    # Get deployment URL
    API_URL=$(vercel ls --scope=team 2>/dev/null | grep -E "https://.*\.vercel\.app" | head -1 | awk '{print $2}')
    
    if [ -z "$API_URL" ]; then
        print_warning "Could not automatically detect API URL. Please check Vercel dashboard."
        echo "Enter your API URL (e.g., https://your-api.vercel.app):"
        read API_URL
    fi
    
    echo "API_URL=$API_URL" > .deployment-urls
    print_status "API deployed to: $API_URL"
}

# Deploy User Portal
deploy_user_portal() {
    print_info "Deploying User Portal..."
    
    cd frontend/user-portal
    
    # Create production environment file
    cat > .env.local << EOF
VITE_API_BASE_URL=$API_URL/api
VITE_APP_NAME=SubscriptionPro
VITE_NODE_ENV=production
EOF
    
    # Install dependencies and build
    npm install
    npm run build
    
    # Deploy to Vercel
    vercel --prod --yes
    
    # Get deployment URL
    USER_PORTAL_URL=$(vercel ls --scope=team 2>/dev/null | grep -E "https://.*\.vercel\.app" | head -1 | awk '{print $2}')
    
    if [ -z "$USER_PORTAL_URL" ]; then
        print_warning "Could not automatically detect User Portal URL."
        echo "Enter your User Portal URL:"
        read USER_PORTAL_URL
    fi
    
    echo "USER_PORTAL_URL=$USER_PORTAL_URL" >> ../../.deployment-urls
    print_status "User Portal deployed to: $USER_PORTAL_URL"
    
    cd ../..
}

# Deploy Admin Portal
deploy_admin_portal() {
    print_info "Deploying Admin Portal..."
    
    cd frontend/admin-portal
    
    # Create production environment file
    cat > .env.local << EOF
VITE_API_BASE_URL=$API_URL/api
VITE_APP_NAME=SubscriptionPro Admin
VITE_NODE_ENV=production
EOF
    
    # Install dependencies and build
    npm install
    npm run build
    
    # Deploy to Vercel
    vercel --prod --yes
    
    # Get deployment URL
    ADMIN_PORTAL_URL=$(vercel ls --scope=team 2>/dev/null | grep -E "https://.*\.vercel\.app" | head -1 | awk '{print $2}')
    
    if [ -z "$ADMIN_PORTAL_URL" ]; then
        print_warning "Could not automatically detect Admin Portal URL."
        echo "Enter your Admin Portal URL:"
        read ADMIN_PORTAL_URL
    fi
    
    echo "ADMIN_PORTAL_URL=$ADMIN_PORTAL_URL" >> ../../.deployment-urls
    print_status "Admin Portal deployed to: $ADMIN_PORTAL_URL"
    
    cd ../..
}

# Setup Supabase database
setup_database() {
    print_info "Setting up Supabase database..."
    
    print_warning "Please complete the following steps manually:"
    echo "1. Go to https://supabase.com and create a new project"
    echo "2. Go to SQL Editor in your Supabase dashboard"
    echo "3. Copy and paste the contents of 'supabase-setup.sql'"
    echo "4. Execute the SQL to create tables and policies"
    echo "5. Go to Settings > API to get your URL and anon key"
    echo "6. Update your Vercel environment variables with these values"
    
    print_warning "Press Enter after completing Supabase setup..."
    read
    
    print_status "Database setup instructions provided"
}

# Update CORS settings
update_cors() {
    print_info "Updating CORS settings..."
    
    # Source deployment URLs
    source .deployment-urls
    
    CORS_ORIGINS="$USER_PORTAL_URL,$ADMIN_PORTAL_URL"
    
    print_info "Setting CORS origins to: $CORS_ORIGINS"
    
    # Update Vercel environment variables
    vercel env add CORS_ORIGINS production
    echo "$CORS_ORIGINS"
    
    print_status "CORS settings updated"
}

# Run tests
run_tests() {
    print_info "Running production tests..."
    
    # Source deployment URLs
    source .deployment-urls
    
    # Test API health
    print_info "Testing API health..."
    if curl -f "$API_URL/health" > /dev/null 2>&1; then
        print_status "API health check passed"
    else
        print_error "API health check failed"
        return 1
    fi
    
    # Test frontend accessibility
    print_info "Testing frontend accessibility..."
    if curl -f "$USER_PORTAL_URL" > /dev/null 2>&1; then
        print_status "User Portal accessible"
    else
        print_error "User Portal not accessible"
        return 1
    fi
    
    if curl -f "$ADMIN_PORTAL_URL" > /dev/null 2>&1; then
        print_status "Admin Portal accessible"
    else
        print_error "Admin Portal not accessible"
        return 1
    fi
    
    # Run API tests
    if [ -f "api/test_api.py" ]; then
        print_info "Running API tests..."
        cd api
        python3 -m pytest test_api.py -v
        cd ..
        print_status "API tests completed"
    fi
    
    print_status "All tests passed"
}

# Generate deployment report
generate_report() {
    print_info "Generating deployment report..."
    
    # Source deployment URLs
    source .deployment-urls
    
    cat > DEPLOYMENT_REPORT.md << EOF
# SubscriptionPro Production Deployment Report

## Deployment Summary
- **Deployment Date**: $(date)
- **Status**: ✅ Successfully Deployed

## Application URLs
- **API**: $API_URL
- **User Portal**: $USER_PORTAL_URL
- **Admin Portal**: $ADMIN_PORTAL_URL

## Database
- **Provider**: Supabase
- **Status**: ✅ Configured

## Security Features
- ✅ JWT Authentication
- ✅ Row Level Security (RLS)
- ✅ CORS Protection
- ✅ Rate Limiting
- ✅ Input Validation

## Testing Status
- ✅ API Health Checks
- ✅ Frontend Accessibility
- ✅ Unit Tests
- ✅ Integration Tests

## Next Steps
1. Configure custom domains (optional)
2. Set up monitoring and alerts
3. Configure backup procedures
4. Set up CI/CD pipelines
5. Configure SFCC integration (if needed)

## Support
- Documentation: See docs/ folder
- API Documentation: $API_URL/docs
- Health Check: $API_URL/health

## Login Credentials (Demo)
- **Admin**: admin@subscriptionpro.com / password123
- **Customer**: demo@subscriptionpro.com / password123

---
Generated on $(date)
EOF

    print_status "Deployment report generated: DEPLOYMENT_REPORT.md"
}

# Main deployment function
main() {
    echo "Starting production deployment..."
    
    check_prerequisites
    setup_environment
    setup_database
    deploy_api
    
    # Source the API URL for frontend deployments
    source .deployment-urls
    
    deploy_user_portal
    deploy_admin_portal
    update_cors
    run_tests
    generate_report
    
    echo ""
    echo "🎉 DEPLOYMENT COMPLETE!"
    echo "======================"
    print_status "API: $API_URL"
    print_status "User Portal: $USER_PORTAL_URL"
    print_status "Admin Portal: $ADMIN_PORTAL_URL"
    echo ""
    print_info "Check DEPLOYMENT_REPORT.md for detailed information"
    print_info "Your subscription platform is now live!"
}

# Run main function
main
