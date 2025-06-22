#!/bin/bash

# Simple deployment script that works with older Node.js versions
echo "🚀 SubscriptionPro Simple Deployment"
echo "===================================="

# Check Node.js version
NODE_VERSION=$(node --version | cut -d'v' -f2 | cut -d'.' -f1)
echo "📋 Node.js version: $(node --version)"

if [ "$NODE_VERSION" -lt 14 ]; then
    echo "⚠️  WARNING: Node.js version is too old for latest Vercel CLI"
    echo "📖 Please see QUICK_DEPLOYMENT_GUIDE.md for solutions"
    echo ""
    echo "🔧 Quick fix options:"
    echo "1. Update Node.js: brew install node@18"
    echo "2. Use manual deployment via vercel.com"
    echo "3. Use GitHub integration"
    echo ""
    read -p "Continue anyway? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Check if vercel is installed
if ! command -v vercel &> /dev/null; then
    echo "📦 Vercel CLI not found. Installing compatible version..."
    
    if [ "$NODE_VERSION" -lt 14 ]; then
        echo "🔧 Installing older Vercel CLI compatible with Node.js 12..."
        npm install -g vercel@25.2.3
    else
        echo "🔧 Installing latest Vercel CLI..."
        npm install -g vercel@latest
    fi
    
    if [ $? -ne 0 ]; then
        echo "❌ Failed to install Vercel CLI"
        echo "📖 Please see QUICK_DEPLOYMENT_GUIDE.md for manual deployment"
        exit 1
    fi
fi

echo "✅ Vercel CLI ready"

# Check if user is logged in to Vercel
if ! vercel whoami &> /dev/null; then
    echo "🔐 Please login to Vercel..."
    vercel login
fi

echo "🚀 Starting deployment..."

# Deploy API
echo "📡 Deploying API..."
cd api
if [ -f "vercel.json" ]; then
    vercel --prod
    if [ $? -eq 0 ]; then
        echo "✅ API deployed successfully"
        API_URL=$(vercel --prod 2>/dev/null | grep -o 'https://[^[:space:]]*')
        echo "🌐 API URL: $API_URL"
    else
        echo "❌ API deployment failed"
        exit 1
    fi
else
    echo "⚠️  No vercel.json found in api directory"
fi
cd ..

# Deploy User Portal
echo "👥 Deploying User Portal..."
cd frontend/user-portal
if [ -f "package.json" ]; then
    # Create environment file if API URL is available
    if [ ! -z "$API_URL" ]; then
        echo "VITE_API_BASE_URL=$API_URL/api" > .env.local
    fi
    
    npm install
    vercel --prod
    if [ $? -eq 0 ]; then
        echo "✅ User Portal deployed successfully"
        USER_PORTAL_URL=$(vercel --prod 2>/dev/null | grep -o 'https://[^[:space:]]*')
        echo "🌐 User Portal URL: $USER_PORTAL_URL"
    else
        echo "❌ User Portal deployment failed"
    fi
else
    echo "⚠️  No package.json found in user portal directory"
fi
cd ../..

# Deploy Admin Portal
echo "👨‍💼 Deploying Admin Portal..."
cd frontend/admin-portal
if [ -f "package.json" ]; then
    # Create environment file if API URL is available
    if [ ! -z "$API_URL" ]; then
        echo "VITE_API_BASE_URL=$API_URL/api" > .env.local
    fi
    
    npm install
    vercel --prod
    if [ $? -eq 0 ]; then
        echo "✅ Admin Portal deployed successfully"
        ADMIN_PORTAL_URL=$(vercel --prod 2>/dev/null | grep -o 'https://[^[:space:]]*')
        echo "🌐 Admin Portal URL: $ADMIN_PORTAL_URL"
    else
        echo "❌ Admin Portal deployment failed"
    fi
else
    echo "⚠️  No package.json found in admin portal directory"
fi
cd ../..

echo ""
echo "🎉 DEPLOYMENT SUMMARY"
echo "===================="
echo "📡 API: ${API_URL:-'❌ Failed'}"
echo "👥 User Portal: ${USER_PORTAL_URL:-'❌ Failed'}"
echo "👨‍💼 Admin Portal: ${ADMIN_PORTAL_URL:-'❌ Failed'}"
echo ""

if [ ! -z "$API_URL" ] && [ ! -z "$USER_PORTAL_URL" ] && [ ! -z "$ADMIN_PORTAL_URL" ]; then
    echo "✅ ALL SERVICES DEPLOYED SUCCESSFULLY!"
    echo ""
    echo "🔗 Production URLs:"
    echo "   API: $API_URL"
    echo "   User Portal: $USER_PORTAL_URL"
    echo "   Admin Portal: $ADMIN_PORTAL_URL"
    echo ""
    echo "📋 Next Steps:"
    echo "1. Set up Supabase database (see QUICK_DEPLOYMENT_GUIDE.md)"
    echo "2. Configure environment variables"
    echo "3. Test the deployment"
    echo "4. Run ./run-all-tests.sh"
    echo ""
    echo "🎯 Your enterprise subscription platform is LIVE!"
else
    echo "⚠️  Some deployments failed. Check the errors above."
    echo "📖 See QUICK_DEPLOYMENT_GUIDE.md for troubleshooting"
fi

echo ""
echo "📊 Run production readiness check:"
echo "   python3 production-readiness-check.py"
