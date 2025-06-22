#!/usr/bin/env python3
"""
Performance and Load Testing for SubscriptionPro API
Tests API performance under various load conditions
"""

import asyncio
import aiohttp
import time
import statistics
import json
import os
from concurrent.futures import ThreadPoolExecutor
import threading

class PerformanceTest:
    def __init__(self, base_url="http://localhost:3000"):
        self.base_url = base_url
        self.results = []
        
    async def make_request(self, session, endpoint, method="GET", data=None, headers=None):
        """Make an async HTTP request and measure response time"""
        start_time = time.time()
        
        try:
            if method == "GET":
                async with session.get(f"{self.base_url}{endpoint}", headers=headers) as response:
                    await response.text()
                    status = response.status
            elif method == "POST":
                async with session.post(f"{self.base_url}{endpoint}", json=data, headers=headers) as response:
                    await response.text()
                    status = response.status
            
            end_time = time.time()
            response_time = (end_time - start_time) * 1000  # Convert to milliseconds
            
            return {
                "endpoint": endpoint,
                "method": method,
                "status": status,
                "response_time": response_time,
                "success": status < 400
            }
            
        except Exception as e:
            end_time = time.time()
            response_time = (end_time - start_time) * 1000
            
            return {
                "endpoint": endpoint,
                "method": method,
                "status": 0,
                "response_time": response_time,
                "success": False,
                "error": str(e)
            }
    
    async def load_test(self, endpoint, concurrent_users=10, requests_per_user=10, method="GET", data=None):
        """Perform load testing on a specific endpoint"""
        print(f"Starting load test: {concurrent_users} users, {requests_per_user} requests each")
        print(f"Target: {method} {endpoint}")
        
        async with aiohttp.ClientSession() as session:
            tasks = []
            
            for user in range(concurrent_users):
                for request in range(requests_per_user):
                    task = self.make_request(session, endpoint, method, data)
                    tasks.append(task)
            
            results = await asyncio.gather(*tasks)
            
        return results
    
    def analyze_results(self, results):
        """Analyze performance test results"""
        successful_requests = [r for r in results if r["success"]]
        failed_requests = [r for r in results if not r["success"]]
        
        if not successful_requests:
            return {
                "total_requests": len(results),
                "successful_requests": 0,
                "failed_requests": len(failed_requests),
                "success_rate": 0,
                "error": "All requests failed"
            }
        
        response_times = [r["response_time"] for r in successful_requests]
        
        analysis = {
            "total_requests": len(results),
            "successful_requests": len(successful_requests),
            "failed_requests": len(failed_requests),
            "success_rate": (len(successful_requests) / len(results)) * 100,
            "avg_response_time": statistics.mean(response_times),
            "min_response_time": min(response_times),
            "max_response_time": max(response_times),
            "median_response_time": statistics.median(response_times),
            "p95_response_time": self.percentile(response_times, 95),
            "p99_response_time": self.percentile(response_times, 99),
            "requests_per_second": len(successful_requests) / (max(response_times) / 1000) if response_times else 0
        }
        
        return analysis
    
    def percentile(self, data, percentile):
        """Calculate percentile of a dataset"""
        if not data:
            return 0
        sorted_data = sorted(data)
        index = int((percentile / 100) * len(sorted_data))
        return sorted_data[min(index, len(sorted_data) - 1)]
    
    def print_results(self, analysis, test_name):
        """Print formatted test results"""
        print(f"\n{'='*50}")
        print(f"PERFORMANCE TEST RESULTS: {test_name}")
        print(f"{'='*50}")
        print(f"Total Requests: {analysis['total_requests']}")
        print(f"Successful: {analysis['successful_requests']}")
        print(f"Failed: {analysis['failed_requests']}")
        print(f"Success Rate: {analysis['success_rate']:.2f}%")
        print(f"Average Response Time: {analysis['avg_response_time']:.2f}ms")
        print(f"Min Response Time: {analysis['min_response_time']:.2f}ms")
        print(f"Max Response Time: {analysis['max_response_time']:.2f}ms")
        print(f"Median Response Time: {analysis['median_response_time']:.2f}ms")
        print(f"95th Percentile: {analysis['p95_response_time']:.2f}ms")
        print(f"99th Percentile: {analysis['p99_response_time']:.2f}ms")
        print(f"Requests/Second: {analysis['requests_per_second']:.2f}")
        
        # Performance benchmarks
        avg_time = analysis['avg_response_time']
        if avg_time < 200:
            print("✅ EXCELLENT: Response time < 200ms")
        elif avg_time < 500:
            print("✅ GOOD: Response time < 500ms")
        elif avg_time < 1000:
            print("⚠️  ACCEPTABLE: Response time < 1000ms")
        else:
            print("❌ POOR: Response time > 1000ms")
        
        success_rate = analysis['success_rate']
        if success_rate >= 99:
            print("✅ EXCELLENT: Success rate >= 99%")
        elif success_rate >= 95:
            print("✅ GOOD: Success rate >= 95%")
        elif success_rate >= 90:
            print("⚠️  ACCEPTABLE: Success rate >= 90%")
        else:
            print("❌ POOR: Success rate < 90%")

async def run_performance_tests():
    """Run comprehensive performance tests"""
    tester = PerformanceTest()
    
    # Test scenarios
    test_scenarios = [
        {
            "name": "Health Check - Light Load",
            "endpoint": "/health",
            "method": "GET",
            "concurrent_users": 5,
            "requests_per_user": 10
        },
        {
            "name": "Health Check - Medium Load",
            "endpoint": "/health",
            "method": "GET",
            "concurrent_users": 20,
            "requests_per_user": 25
        },
        {
            "name": "Health Check - Heavy Load",
            "endpoint": "/health",
            "method": "GET",
            "concurrent_users": 50,
            "requests_per_user": 20
        },
        {
            "name": "Products API - Light Load",
            "endpoint": "/api/products",
            "method": "GET",
            "concurrent_users": 10,
            "requests_per_user": 10
        },
        {
            "name": "Products API - Medium Load",
            "endpoint": "/api/products",
            "method": "GET",
            "concurrent_users": 25,
            "requests_per_user": 20
        },
        {
            "name": "Authentication - Load Test",
            "endpoint": "/api/auth/login",
            "method": "POST",
            "data": {"email": "demo@subscriptionpro.com", "password": "password123"},
            "concurrent_users": 15,
            "requests_per_user": 5
        }
    ]
    
    print("🚀 Starting Performance Test Suite")
    print(f"Target URL: {tester.base_url}")
    
    all_results = {}
    
    for scenario in test_scenarios:
        print(f"\n📊 Running: {scenario['name']}")
        
        results = await tester.load_test(
            endpoint=scenario["endpoint"],
            method=scenario["method"],
            concurrent_users=scenario["concurrent_users"],
            requests_per_user=scenario["requests_per_user"],
            data=scenario.get("data")
        )
        
        analysis = tester.analyze_results(results)
        tester.print_results(analysis, scenario["name"])
        
        all_results[scenario["name"]] = analysis
        
        # Brief pause between tests
        await asyncio.sleep(1)
    
    # Overall summary
    print(f"\n{'='*60}")
    print("OVERALL PERFORMANCE SUMMARY")
    print(f"{'='*60}")
    
    total_requests = sum(r["total_requests"] for r in all_results.values())
    total_successful = sum(r["successful_requests"] for r in all_results.values())
    overall_success_rate = (total_successful / total_requests) * 100 if total_requests > 0 else 0
    
    print(f"Total Requests Across All Tests: {total_requests}")
    print(f"Total Successful Requests: {total_successful}")
    print(f"Overall Success Rate: {overall_success_rate:.2f}%")
    
    avg_response_times = [r["avg_response_time"] for r in all_results.values()]
    overall_avg_response = statistics.mean(avg_response_times)
    print(f"Average Response Time Across Tests: {overall_avg_response:.2f}ms")
    
    # Save results to file
    with open("performance_test_results.json", "w") as f:
        json.dump(all_results, f, indent=2)
    
    print(f"\n📁 Results saved to: performance_test_results.json")
    
    return all_results

def stress_test_concurrent_users():
    """Test with increasing concurrent users to find breaking point"""
    print("\n🔥 STRESS TEST: Finding Breaking Point")
    
    async def stress_test():
        tester = PerformanceTest()
        user_counts = [10, 25, 50, 100, 200, 500]
        
        for user_count in user_counts:
            print(f"\n🧪 Testing with {user_count} concurrent users...")
            
            results = await tester.load_test(
                endpoint="/health",
                concurrent_users=user_count,
                requests_per_user=5
            )
            
            analysis = tester.analyze_results(results)
            
            print(f"Users: {user_count}, Success Rate: {analysis['success_rate']:.1f}%, "
                  f"Avg Response: {analysis['avg_response_time']:.1f}ms")
            
            # Stop if success rate drops below 90%
            if analysis['success_rate'] < 90:
                print(f"⚠️  Breaking point reached at {user_count} concurrent users")
                break
            
            await asyncio.sleep(2)  # Cool down between tests
    
    asyncio.run(stress_test())

if __name__ == "__main__":
    print("SubscriptionPro API Performance Testing Suite")
    print("=" * 50)
    
    # Check if API is running
    import requests
    try:
        response = requests.get("http://localhost:3000/health", timeout=5)
        print("✅ API is accessible")
    except:
        print("❌ API not accessible at http://localhost:3000")
        print("Please start the API server first")
        exit(1)
    
    # Run performance tests
    asyncio.run(run_performance_tests())
    
    # Run stress test
    stress_test_concurrent_users()
    
    print("\n🎉 Performance testing completed!")
