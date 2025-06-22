#!/usr/bin/env python3
"""
Security Testing Suite for SubscriptionPro API
Tests for common security vulnerabilities
"""

import requests
import json
import time
import hashlib
import base64
from urllib.parse import quote

class SecurityTester:
    def __init__(self, base_url="http://localhost:3000"):
        self.base_url = base_url
        self.session = requests.Session()
        self.vulnerabilities = []
        
    def log_vulnerability(self, test_name, severity, description, details=None):
        """Log a security vulnerability"""
        vuln = {
            "test": test_name,
            "severity": severity,  # HIGH, MEDIUM, LOW
            "description": description,
            "details": details or {},
            "timestamp": time.time()
        }
        self.vulnerabilities.append(vuln)
        
        severity_emoji = {"HIGH": "🔴", "MEDIUM": "🟡", "LOW": "🟢"}
        print(f"{severity_emoji.get(severity, '⚪')} {severity}: {test_name}")
        print(f"   {description}")
        if details:
            print(f"   Details: {details}")
    
    def test_sql_injection(self):
        """Test for SQL injection vulnerabilities"""
        print("\n🔍 Testing SQL Injection...")
        
        sql_payloads = [
            "' OR '1'='1",
            "'; DROP TABLE users; --",
            "' UNION SELECT * FROM users --",
            "admin'/*",
            "' OR 1=1 --",
            "1' AND (SELECT COUNT(*) FROM users) > 0 --"
        ]
        
        endpoints = [
            "/api/auth/login",
            "/api/users",
            "/api/products"
        ]
        
        vulnerabilities_found = 0
        
        for endpoint in endpoints:
            for payload in sql_payloads:
                # Test in different parameters
                test_data = {
                    "email": payload,
                    "password": "test",
                    "search": payload,
                    "id": payload
                }
                
                try:
                    if endpoint == "/api/auth/login":
                        response = self.session.post(f"{self.base_url}{endpoint}", json=test_data)
                    else:
                        response = self.session.get(f"{self.base_url}{endpoint}", params={"search": payload})
                    
                    # Check for SQL error messages
                    response_text = response.text.lower()
                    sql_errors = [
                        "sql syntax",
                        "mysql_fetch",
                        "ora-",
                        "postgresql",
                        "sqlite_",
                        "sqlstate",
                        "database error"
                    ]
                    
                    for error in sql_errors:
                        if error in response_text:
                            self.log_vulnerability(
                                "SQL Injection",
                                "HIGH",
                                f"SQL error exposed in {endpoint}",
                                {"payload": payload, "error": error}
                            )
                            vulnerabilities_found += 1
                            break
                            
                except Exception as e:
                    pass  # Network errors are expected
        
        if vulnerabilities_found == 0:
            print("✅ No SQL injection vulnerabilities detected")
    
    def test_xss_vulnerabilities(self):
        """Test for Cross-Site Scripting (XSS) vulnerabilities"""
        print("\n🔍 Testing XSS Vulnerabilities...")
        
        xss_payloads = [
            "<script>alert('XSS')</script>",
            "javascript:alert('XSS')",
            "<img src=x onerror=alert('XSS')>",
            "';alert('XSS');//",
            "<svg onload=alert('XSS')>",
            "{{7*7}}"  # Template injection
        ]
        
        endpoints = [
            "/api/products",
            "/api/users"
        ]
        
        vulnerabilities_found = 0
        
        for endpoint in endpoints:
            for payload in xss_payloads:
                try:
                    response = self.session.get(f"{self.base_url}{endpoint}", params={"search": payload})
                    
                    # Check if payload is reflected without encoding
                    if payload in response.text and response.headers.get('content-type', '').startswith('text/html'):
                        self.log_vulnerability(
                            "XSS Vulnerability",
                            "MEDIUM",
                            f"Unescaped user input in {endpoint}",
                            {"payload": payload}
                        )
                        vulnerabilities_found += 1
                        
                except Exception as e:
                    pass
        
        if vulnerabilities_found == 0:
            print("✅ No XSS vulnerabilities detected")
    
    def test_authentication_bypass(self):
        """Test for authentication bypass vulnerabilities"""
        print("\n🔍 Testing Authentication Bypass...")
        
        protected_endpoints = [
            "/api/subscriptions",
            "/api/admin/dashboard",
            "/api/admin/users"
        ]
        
        bypass_attempts = [
            {},  # No headers
            {"Authorization": ""},  # Empty auth
            {"Authorization": "Bearer invalid"},  # Invalid token
            {"Authorization": "Bearer null"},  # Null token
            {"Authorization": "Bearer undefined"},  # Undefined token
            {"X-User-ID": "admin"},  # Header injection
        ]
        
        vulnerabilities_found = 0
        
        for endpoint in protected_endpoints:
            for headers in bypass_attempts:
                try:
                    response = self.session.get(f"{self.base_url}{endpoint}", headers=headers)
                    
                    # Should return 401 or 403, not 200
                    if response.status_code == 200:
                        self.log_vulnerability(
                            "Authentication Bypass",
                            "HIGH",
                            f"Protected endpoint accessible without auth: {endpoint}",
                            {"headers": headers, "status": response.status_code}
                        )
                        vulnerabilities_found += 1
                        
                except Exception as e:
                    pass
        
        if vulnerabilities_found == 0:
            print("✅ No authentication bypass vulnerabilities detected")
    
    def test_rate_limiting(self):
        """Test rate limiting implementation"""
        print("\n🔍 Testing Rate Limiting...")
        
        # Make rapid requests to test rate limiting
        endpoint = "/api/auth/login"
        rapid_requests = 70  # Should exceed typical rate limits
        
        responses = []
        for i in range(rapid_requests):
            try:
                response = self.session.post(
                    f"{self.base_url}{endpoint}",
                    json={"email": "test@example.com", "password": "wrong"}
                )
                responses.append(response.status_code)
                
                if i > 50 and response.status_code != 429:  # Should be rate limited by now
                    continue
                    
            except Exception as e:
                pass
        
        # Check if rate limiting is working
        rate_limited = any(status == 429 for status in responses[-20:])  # Check last 20 requests
        
        if not rate_limited:
            self.log_vulnerability(
                "Missing Rate Limiting",
                "MEDIUM",
                "No rate limiting detected on authentication endpoint",
                {"requests_made": rapid_requests}
            )
        else:
            print("✅ Rate limiting is working")
    
    def test_cors_configuration(self):
        """Test CORS configuration"""
        print("\n🔍 Testing CORS Configuration...")
        
        # Test with various origins
        test_origins = [
            "https://evil.com",
            "http://localhost:3000",
            "null",
            "*"
        ]
        
        for origin in test_origins:
            try:
                headers = {"Origin": origin}
                response = self.session.options(f"{self.base_url}/api/products", headers=headers)
                
                cors_origin = response.headers.get('Access-Control-Allow-Origin', '')
                
                if cors_origin == "*" and origin == "https://evil.com":
                    self.log_vulnerability(
                        "Overly Permissive CORS",
                        "MEDIUM",
                        "CORS allows all origins (*)",
                        {"origin": origin, "cors_header": cors_origin}
                    )
                    
            except Exception as e:
                pass
        
        print("✅ CORS configuration checked")
    
    def test_information_disclosure(self):
        """Test for information disclosure"""
        print("\n🔍 Testing Information Disclosure...")
        
        # Test error handling
        endpoints_to_test = [
            "/api/nonexistent",
            "/api/users/invalid-id",
            "/api/products/999999"
        ]
        
        for endpoint in endpoints_to_test:
            try:
                response = self.session.get(f"{self.base_url}{endpoint}")
                
                # Check for sensitive information in error responses
                sensitive_info = [
                    "stack trace",
                    "file path",
                    "database",
                    "internal server error",
                    "debug",
                    "exception"
                ]
                
                response_text = response.text.lower()
                for info in sensitive_info:
                    if info in response_text and len(response_text) > 100:  # Detailed error
                        self.log_vulnerability(
                            "Information Disclosure",
                            "LOW",
                            f"Detailed error information exposed in {endpoint}",
                            {"info_type": info}
                        )
                        break
                        
            except Exception as e:
                pass
        
        print("✅ Information disclosure test completed")
    
    def test_input_validation(self):
        """Test input validation"""
        print("\n🔍 Testing Input Validation...")
        
        # Test with various malformed inputs
        malformed_inputs = [
            {"email": "not-an-email", "password": "test"},
            {"email": "test@example.com", "password": ""},
            {"email": "", "password": "test"},
            {"email": "a" * 1000, "password": "test"},  # Very long input
            {"email": None, "password": None},
            {"quantity": -1},
            {"quantity": "not-a-number"},
            {"price": -100.50}
        ]
        
        for input_data in malformed_inputs:
            try:
                response = self.session.post(f"{self.base_url}/api/auth/login", json=input_data)
                
                # Should return 400 for bad input, not 500
                if response.status_code == 500:
                    self.log_vulnerability(
                        "Poor Input Validation",
                        "LOW",
                        "Server error on malformed input",
                        {"input": input_data, "status": response.status_code}
                    )
                    
            except Exception as e:
                pass
        
        print("✅ Input validation test completed")
    
    def generate_report(self):
        """Generate security test report"""
        print(f"\n{'='*60}")
        print("SECURITY TEST REPORT")
        print(f"{'='*60}")
        
        if not self.vulnerabilities:
            print("🎉 No security vulnerabilities detected!")
            return
        
        # Group by severity
        high_vulns = [v for v in self.vulnerabilities if v["severity"] == "HIGH"]
        medium_vulns = [v for v in self.vulnerabilities if v["severity"] == "MEDIUM"]
        low_vulns = [v for v in self.vulnerabilities if v["severity"] == "LOW"]
        
        print(f"🔴 HIGH SEVERITY: {len(high_vulns)}")
        print(f"🟡 MEDIUM SEVERITY: {len(medium_vulns)}")
        print(f"🟢 LOW SEVERITY: {len(low_vulns)}")
        print(f"📊 TOTAL VULNERABILITIES: {len(self.vulnerabilities)}")
        
        # Detailed report
        for vuln in self.vulnerabilities:
            print(f"\n{vuln['severity']}: {vuln['test']}")
            print(f"Description: {vuln['description']}")
            if vuln['details']:
                print(f"Details: {json.dumps(vuln['details'], indent=2)}")
        
        # Save to file
        with open("security_test_report.json", "w") as f:
            json.dump(self.vulnerabilities, f, indent=2)
        
        print(f"\n📁 Detailed report saved to: security_test_report.json")

def run_security_tests():
    """Run all security tests"""
    print("🔒 SubscriptionPro API Security Testing Suite")
    print("=" * 50)
    
    # Check if API is accessible
    try:
        response = requests.get("http://localhost:3000/health", timeout=5)
        print("✅ API is accessible")
    except:
        print("❌ API not accessible at http://localhost:3000")
        print("Please start the API server first")
        return
    
    tester = SecurityTester()
    
    # Run all security tests
    tester.test_sql_injection()
    tester.test_xss_vulnerabilities()
    tester.test_authentication_bypass()
    tester.test_rate_limiting()
    tester.test_cors_configuration()
    tester.test_information_disclosure()
    tester.test_input_validation()
    
    # Generate report
    tester.generate_report()

if __name__ == "__main__":
    run_security_tests()
