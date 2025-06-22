# SubscriptionPro - Enterprise Subscription Management Platform

## 🚀 Overview

SubscriptionPro is a comprehensive, enterprise-grade subscription management platform designed specifically for e-commerce businesses. Built with modern technologies and best practices, it provides a complete solution for managing subscription-based products with deep integration capabilities for Salesforce Commerce Cloud B2C.

## ✨ Key Features

### 🔄 Complete Subscription Lifecycle Management
- Create, modify, pause, resume, cancel, skip, and extend subscriptions
- Flexible billing cycles and pricing models
- Automated recurring payment processing
- Real-time subscription status tracking

### 💳 Advanced Payment Processing
- Integrated with Razorpay for INR transactions
- Support for recurring payments and payment method management
- Comprehensive payment failure handling and retry logic
- PCI DSS compliance through Razorpay's secure infrastructure

### 👥 Multi-tenant Architecture
- Support for multiple businesses with isolated data
- Role-based access control (RBAC)
- Comprehensive audit logging for compliance
- Scalable infrastructure for growing businesses

### 🎨 Modern User Experience
- React-based user portal with responsive design
- Comprehensive admin dashboard with analytics
- Real-time updates and notifications
- Mobile-friendly interface

### 🔗 Salesforce Commerce Cloud Integration
- Deep integration with SFCC B2C using modern SCAPI
- SFRA cartridge for native storefront integration
- Real-time data synchronization
- Seamless customer experience within SFCC ecosystem

## 🏗️ Architecture

### Backend
- **Framework**: Flask (Python) with SQLAlchemy ORM
- **Database**: PostgreSQL with UUID primary keys
- **Authentication**: JWT tokens with role-based access control
- **API Design**: RESTful APIs with comprehensive error handling
- **Payment**: Razorpay SDK for INR transactions

### Frontend
- **Framework**: React 18 with Vite build tool
- **Styling**: Tailwind CSS with shadcn/ui components
- **State Management**: React Context API
- **Routing**: React Router with protected routes
- **Testing**: React Testing Library with Jest

### Infrastructure
- **Containerization**: Docker for all components
- **Orchestration**: Docker Compose for local development
- **CI/CD**: GitHub Actions with automated testing
- **Deployment**: Support for AWS, GCP, Azure, and Firebase

## 🚀 Quick Start

### Prerequisites
- Docker and Docker Compose
- Node.js 20+ (for local development)
- Python 3.11+ (for local development)

### Local Development Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd subscription-platform
   ```

2. **Environment Configuration**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

3. **Start all services**
   ```bash
   docker-compose up -d
   ```

4. **Access the applications**
   - User Portal: http://localhost:5174
   - Admin Portal: http://localhost:5176
   - Backend API: http://localhost:5000
   - API Documentation: http://localhost:5000/docs

### Sample Credentials
- **Admin User**: admin@subscriptionpro.com / admin123
- **Test User**: john.doe@example.com / password123

## 📁 Project Structure

```
subscription-platform/
├── backend/
│   └── subscription-api/          # Flask backend application
│       ├── src/                   # Source code
│       │   ├── models/           # Database models
│       │   ├── routes/           # API endpoints
│       │   └── services/         # Business logic
│       ├── tests/                # Test suites
│       └── Dockerfile           # Container configuration
├── frontend/
│   ├── user-portal/              # React user portal
│   └── admin-portal/             # React admin dashboard
├── database/
│   ├── init.sql                  # Database schema
│   └── sample_data.sql          # Sample data
├── docs/                         # Documentation
├── nginx/                        # Load balancer config
├── .github/workflows/           # CI/CD pipelines
└── docker-compose.yml          # Local development setup
```

## 🔧 Configuration

### Environment Variables

```bash
# Database Configuration
DATABASE_URL=postgresql://user:password@localhost:5432/subscriptionpro

# Razorpay Configuration
RAZORPAY_KEY_ID=your_razorpay_key_id
RAZORPAY_KEY_SECRET=your_razorpay_key_secret

# JWT Configuration
JWT_SECRET_KEY=your_jwt_secret_key

# Application Configuration
FLASK_ENV=development
CORS_ORIGINS=http://localhost:3000,http://localhost:3001
```

### Database Setup

The application automatically initializes the database with the required schema and sample data when started with Docker Compose.

For manual setup:
```bash
# Initialize database
psql -h localhost -U postgres -d subscriptionpro -f database/init.sql

# Load sample data
psql -h localhost -U postgres -d subscriptionpro -f database/sample_data.sql
```

## 🧪 Testing

### Backend Testing
```bash
cd backend/subscription-api
python -m pytest tests/ -v --cov=src
```

### Frontend Testing
```bash
# User Portal
cd frontend/user-portal
npm test

# Admin Portal
cd frontend/admin-portal
npm test
```

### Integration Testing
```bash
# Run all tests
docker-compose -f docker-compose.test.yml up --abort-on-container-exit
```

## 📚 API Documentation

The API documentation is automatically generated and available at:
- **Swagger UI**: http://localhost:5000/docs
- **OpenAPI Spec**: `/docs/api-documentation.yaml`

### Key API Endpoints

#### Authentication
- `POST /api/auth/login` - User login
- `POST /api/auth/register` - User registration
- `POST /api/auth/refresh` - Refresh JWT token

#### Subscriptions
- `GET /api/subscriptions` - List subscriptions
- `POST /api/subscriptions` - Create subscription
- `PUT /api/subscriptions/{id}` - Update subscription
- `POST /api/subscriptions/{id}/pause` - Pause subscription
- `POST /api/subscriptions/{id}/resume` - Resume subscription

#### Products
- `GET /api/products` - List products
- `POST /api/products` - Create product (admin)
- `PUT /api/products/{id}` - Update product (admin)

#### Payments
- `POST /api/payments/create-order` - Create Razorpay order
- `POST /api/payments/verify` - Verify payment
- `POST /api/payments/webhook` - Handle webhooks

## 🚀 Deployment

### Docker Deployment
```bash
# Build and deploy
docker-compose -f docker-compose.prod.yml up -d
```

### Cloud Deployment

#### AWS (ECS Fargate)
```bash
# Deploy to AWS
aws ecs create-cluster --cluster-name subscriptionpro
# Follow deployment guide in docs/deployment-guide.md
```

#### Google Cloud (Cloud Run)
```bash
# Deploy to GCP
gcloud run deploy subscriptionpro --source .
```

#### Azure (Container Instances)
```bash
# Deploy to Azure
az container create --resource-group subscriptionpro --name subscriptionpro
```

### CI/CD Pipeline

The project includes GitHub Actions workflows for:
- Automated testing on pull requests
- Container image building and scanning
- Multi-environment deployment
- Security vulnerability scanning

## 🔗 Salesforce Commerce Cloud Integration

### SFRA Cartridge Integration

1. **Install the cartridge**
   ```bash
   # Upload cartridge to SFCC instance
   npm run upload-cartridge
   ```

2. **Configure cartridge path**
   ```
   int_subscriptionpro_sfra:app_storefront_base
   ```

3. **Configure services in Business Manager**
   - SubscriptionPro API service
   - Razorpay payment service
   - SCAPI authentication

### SCAPI Integration

The platform provides modern SCAPI integration for:
- Customer data synchronization
- Product catalog integration
- Order management
- Real-time subscription updates

Detailed integration guide available in `/docs/salesforce-integration-implementation.md`

## 📊 Monitoring and Analytics

### Performance Metrics
- Subscription conversion rates
- Customer lifetime value
- Churn analysis
- Revenue analytics
- Payment success rates

### System Monitoring
- Application performance monitoring
- Database performance tracking
- API response time monitoring
- Error rate tracking
- Security event logging

## 🔒 Security

### Authentication & Authorization
- JWT-based authentication with refresh tokens
- Role-based access control (RBAC)
- Password hashing with bcrypt
- Session management and timeout

### Data Protection
- Data encryption at rest and in transit
- Input validation and sanitization
- SQL injection prevention
- XSS protection
- CSRF protection

### Payment Security
- PCI DSS compliance through Razorpay
- Secure payment tokenization
- Webhook signature verification
- Payment data encryption

## 🤝 Contributing

### Development Workflow
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Run the test suite
6. Submit a pull request

### Code Standards
- Follow PEP 8 for Python code
- Use ESLint and Prettier for JavaScript/React
- Write comprehensive tests
- Document new features
- Follow semantic versioning

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

### Documentation
- [Architecture Guide](/docs/architecture_design.md)
- [Database Schema](/docs/database_design.md)
- [API Documentation](/docs/api-documentation.yaml)
- [Deployment Guide](/docs/deployment-guide.md)
- [Salesforce Integration](/docs/salesforce-integration-implementation.md)

### Getting Help
- Create an issue for bug reports
- Use discussions for questions
- Check the documentation first
- Follow the issue templates

## 🎯 Roadmap

### Version 2.0 (Planned)
- Multi-currency support
- Advanced analytics with ML
- Mobile applications (iOS/Android)
- API marketplace for extensions
- Advanced personalization features

### Version 3.0 (Future)
- Microservices architecture
- Event-driven architecture
- Global CDN integration
- Advanced AI recommendations
- Blockchain integration for transparency

---

**Built with ❤️ for the e-commerce community**

For more information, visit our [documentation](/docs/) or contact our support team.

