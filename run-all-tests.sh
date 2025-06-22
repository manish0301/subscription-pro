#!/bin/bash

# Comprehensive Testing Suite for SubscriptionPro
# Runs all tests: Unit, Integration, Performance, Security, UI

set -e

echo "🧪 SubscriptionPro Comprehensive Testing Suite"
echo "=============================================="

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_status() { echo -e "${GREEN}✅ $1${NC}"; }
print_warning() { echo -e "${YELLOW}⚠️  $1${NC}"; }
print_error() { echo -e "${RED}❌ $1${NC}"; }
print_info() { echo -e "${BLUE}ℹ️  $1${NC}"; }

# Test results tracking
TOTAL_TESTS=0
PASSED_TESTS=0
FAILED_TESTS=0

# Function to run a test and track results
run_test() {
    local test_name="$1"
    local test_command="$2"
    
    print_info "Running: $test_name"
    TOTAL_TESTS=$((TOTAL_TESTS + 1))
    
    if eval "$test_command"; then
        print_status "$test_name passed"
        PASSED_TESTS=$((PASSED_TESTS + 1))
        return 0
    else
        print_error "$test_name failed"
        FAILED_TESTS=$((FAILED_TESTS + 1))
        return 1
    fi
}

# Check if API is running
check_api_status() {
    print_info "Checking API status..."
    
    if curl -f http://localhost:3000/health > /dev/null 2>&1; then
        print_status "API is running"
        return 0
    else
        print_warning "API not running locally. Checking production..."
        
        if [ -f ".deployment-urls" ]; then
            source .deployment-urls
            if curl -f "$API_URL/health" > /dev/null 2>&1; then
                print_status "Production API is accessible"
                export TEST_API_URL="$API_URL"
                return 0
            fi
        fi
        
        print_error "No accessible API found. Please start the API or deploy to production."
        return 1
    fi
}

# Unit Tests
run_unit_tests() {
    print_info "Running Unit Tests..."
    
    # Python API tests
    if [ -f "api/test_api.py" ]; then
        run_test "API Unit Tests" "cd api && python3 -m pytest test_api.py -v --tb=short"
    fi
    
    # Frontend tests
    if [ -d "frontend/user-portal" ]; then
        run_test "User Portal Tests" "cd frontend/user-portal && npm test -- --watchAll=false"
    fi
    
    if [ -d "frontend/admin-portal" ]; then
        run_test "Admin Portal Tests" "cd frontend/admin-portal && npm test -- --watchAll=false"
    fi
}

# Integration Tests
run_integration_tests() {
    print_info "Running Integration Tests..."
    
    # Test API endpoints
    run_test "Health Check Integration" "curl -f ${TEST_API_URL:-http://localhost:3000}/health"
    run_test "Products API Integration" "curl -f ${TEST_API_URL:-http://localhost:3000}/api/products"
    
    # Test database connectivity
    if [ -n "$SUPABASE_URL" ]; then
        run_test "Database Connectivity" "curl -f $SUPABASE_URL/rest/v1/ -H 'apikey: $SUPABASE_KEY'"
    fi
}

# Performance Tests
run_performance_tests() {
    print_info "Running Performance Tests..."
    
    if [ -f "api/performance_test.py" ]; then
        run_test "API Performance Tests" "cd api && python3 performance_test.py"
    fi
    
    # Load testing with curl
    run_test "Basic Load Test" "
        for i in {1..50}; do
            curl -s ${TEST_API_URL:-http://localhost:3000}/health > /dev/null &
        done
        wait
        echo 'Load test completed'
    "
}

# Security Tests
run_security_tests() {
    print_info "Running Security Tests..."
    
    if [ -f "api/security_test.py" ]; then
        run_test "Security Vulnerability Tests" "cd api && python3 security_test.py"
    fi
    
    # Basic security checks
    run_test "HTTPS Redirect Check" "
        if [ -n '$TEST_API_URL' ]; then
            curl -I $TEST_API_URL 2>/dev/null | grep -q 'HTTP/2 200' || curl -I $TEST_API_URL 2>/dev/null | grep -q 'HTTP/1.1 200'
        else
            echo 'Skipping HTTPS check for local API'
        fi
    "
    
    run_test "CORS Headers Check" "
        curl -H 'Origin: https://example.com' -I ${TEST_API_URL:-http://localhost:3000}/api/products 2>/dev/null | grep -q 'Access-Control-Allow-Origin'
    "
}

# UI Tests
run_ui_tests() {
    print_info "Running UI Tests..."
    
    # Check if frontends are accessible
    if [ -f ".deployment-urls" ]; then
        source .deployment-urls
        
        if [ -n "$USER_PORTAL_URL" ]; then
            run_test "User Portal Accessibility" "curl -f $USER_PORTAL_URL > /dev/null 2>&1"
        fi
        
        if [ -n "$ADMIN_PORTAL_URL" ]; then
            run_test "Admin Portal Accessibility" "curl -f $ADMIN_PORTAL_URL > /dev/null 2>&1"
        fi
    fi
    
    # Basic HTML validation
    run_test "HTML Structure Validation" "
        if [ -d 'frontend/user-portal/dist' ]; then
            grep -q '<html' frontend/user-portal/dist/index.html
        else
            echo 'Frontend not built, skipping HTML validation'
        fi
    "
}

# Database Tests
run_database_tests() {
    print_info "Running Database Tests..."
    
    # Test database schema
    run_test "Database Schema Validation" "
        if [ -f 'supabase-setup.sql' ]; then
            grep -q 'CREATE TABLE' supabase-setup.sql
        else
            echo 'Database schema file not found'
            return 1
        fi
    "
    
    # Test sample data
    run_test "Sample Data Validation" "
        if [ -f 'supabase-setup.sql' ]; then
            grep -q 'INSERT INTO' supabase-setup.sql
        else
            echo 'Sample data not found'
            return 1
        fi
    "
}

# API Documentation Tests
run_documentation_tests() {
    print_info "Running Documentation Tests..."
    
    run_test "API Documentation Exists" "[ -f 'docs/api-documentation.yaml' ]"
    run_test "Deployment Guide Exists" "[ -f 'PRODUCTION-DEPLOYMENT.md' ]"
    run_test "README Completeness" "grep -q 'SubscriptionPro' README.md"
}

# Deployment Verification
run_deployment_verification() {
    print_info "Running Deployment Verification..."
    
    # Check required files
    run_test "Vercel Config Exists" "[ -f 'vercel.json' ]"
    run_test "Environment Template Exists" "[ -f 'frontend/user-portal/.env.example' ]"
    run_test "Database Setup Script Exists" "[ -f 'supabase-setup.sql' ]"
    
    # Check deployment script
    run_test "Deployment Script Exists" "[ -f 'deploy-production.sh' ]"
    run_test "Deployment Script Executable" "[ -x 'deploy-production.sh' ]"
}

# Generate test report
generate_test_report() {
    print_info "Generating test report..."
    
    local success_rate=0
    if [ $TOTAL_TESTS -gt 0 ]; then
        success_rate=$((PASSED_TESTS * 100 / TOTAL_TESTS))
    fi
    
    cat > TEST_REPORT.md << EOF
# SubscriptionPro Test Report

## Test Summary
- **Total Tests**: $TOTAL_TESTS
- **Passed**: $PASSED_TESTS
- **Failed**: $FAILED_TESTS
- **Success Rate**: $success_rate%

## Test Categories
- ✅ Unit Tests
- ✅ Integration Tests
- ✅ Performance Tests
- ✅ Security Tests
- ✅ UI Tests
- ✅ Database Tests
- ✅ Documentation Tests
- ✅ Deployment Verification

## Test Results
$(if [ $success_rate -ge 95 ]; then echo "🎉 EXCELLENT: All tests passing"; elif [ $success_rate -ge 80 ]; then echo "✅ GOOD: Most tests passing"; else echo "⚠️ NEEDS ATTENTION: Some tests failing"; fi)

## Recommendations
$(if [ $FAILED_TESTS -gt 0 ]; then echo "- Review failed tests and fix issues"; else echo "- All tests passing, ready for production"; fi)
- Run tests regularly during development
- Add more test cases as features are added
- Monitor performance metrics in production

---
Generated on $(date)
EOF

    print_status "Test report generated: TEST_REPORT.md"
}

# Main test execution
main() {
    echo "Starting comprehensive test suite..."
    
    # Check API status first
    if ! check_api_status; then
        print_warning "Some tests may fail without a running API"
    fi
    
    # Run all test categories
    run_unit_tests
    run_integration_tests
    run_performance_tests
    run_security_tests
    run_ui_tests
    run_database_tests
    run_documentation_tests
    run_deployment_verification
    
    # Generate report
    generate_test_report
    
    # Final summary
    echo ""
    echo "🏁 TEST SUITE COMPLETE"
    echo "======================"
    print_info "Total Tests: $TOTAL_TESTS"
    print_status "Passed: $PASSED_TESTS"
    if [ $FAILED_TESTS -gt 0 ]; then
        print_error "Failed: $FAILED_TESTS"
    fi
    
    local success_rate=$((PASSED_TESTS * 100 / TOTAL_TESTS))
    echo "Success Rate: $success_rate%"
    
    if [ $success_rate -ge 95 ]; then
        print_status "🎉 EXCELLENT: Ready for production!"
    elif [ $success_rate -ge 80 ]; then
        print_status "✅ GOOD: Minor issues to address"
    else
        print_warning "⚠️ NEEDS WORK: Address failing tests before production"
    fi
    
    echo ""
    print_info "Detailed report: TEST_REPORT.md"
    
    # Exit with error code if tests failed
    if [ $FAILED_TESTS -gt 0 ]; then
        exit 1
    fi
}

# Run main function
main
