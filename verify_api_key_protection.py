#!/usr/bin/env python3
"""
API Key Protection Verification Script

This script demonstrates and verifies that API key protection is working correctly.
It tests all endpoints to ensure proper protection when ENABLE_API_KEY=true.

Usage:
    1. Set environment variables:
       export ENABLE_API_KEY=true
       export X_API_KEY=your_secret_key
    
    2. Start the server:
       docker-compose up -d
    
    3. Run this script:
       python verify_api_key_protection.py
"""

import requests
import sys

# Configuration
BASE_URL = "http://localhost:8000"
API_KEY = "your_secret_key"  # Should match X_API_KEY in .env

def test_endpoint(name, method, path, headers=None, expected_status=None):
    """Test a single endpoint"""
    url = f"{BASE_URL}{path}"
    
    try:
        if method == "GET":
            response = requests.get(url, headers=headers, timeout=5)
        elif method == "POST":
            response = requests.post(url, headers=headers, timeout=5)
        else:
            raise ValueError(f"Unsupported method: {method}")
        
        status = response.status_code
        
        if expected_status:
            if status == expected_status:
                print(f"✓ PASS: {name:40s} (status: {status})")
                return True
            else:
                print(f"✗ FAIL: {name:40s} (expected: {expected_status}, got: {status})")
                return False
        else:
            print(f"  INFO: {name:40s} (status: {status})")
            return True
            
    except requests.exceptions.RequestException as e:
        print(f"✗ ERROR: {name:40s} - {e}")
        return False


def main():
    print("=" * 80)
    print("API KEY PROTECTION VERIFICATION")
    print("=" * 80)
    print()
    print(f"Testing API at: {BASE_URL}")
    print(f"Using API Key: {API_KEY}")
    print()
    
    tests_passed = 0
    tests_failed = 0
    
    print("Testing UNPROTECTED endpoints (should be accessible without API key):")
    print("-" * 80)
    
    # Unprotected endpoints
    unprotected_tests = [
        ("Health Check", "GET", "/health", None, 200),
        ("API Docs", "GET", "/docs", None, 200),
        ("API Docs (ReDoc)", "GET", "/redoc", None, 200),
        ("OpenAPI Schema", "GET", "/openapi.json", None, 200),
        ("Auth Login", "GET", "/auth/login", None, 200),
        ("Auth Callback Simple", "GET", "/auth/callback-simple?url=test", None, None),  # Will fail validation, not auth
    ]
    
    for test in unprotected_tests:
        if test_endpoint(*test):
            tests_passed += 1
        else:
            tests_failed += 1
    
    print()
    print("Testing PROTECTED endpoints WITHOUT API key (should be rejected):")
    print("-" * 80)
    
    # Protected endpoints without API key - should all return 401
    protected_no_key = [
        ("Auth Status (no key)", "GET", "/auth/status", None, 401),
        ("Auth Logout (no key)", "POST", "/auth/logout", None, 401),
        ("Lists (no key)", "GET", "/lists", None, 401),
    ]
    
    for test in protected_no_key:
        if test_endpoint(*test):
            tests_passed += 1
        else:
            tests_failed += 1
    
    print()
    print("Testing PROTECTED endpoints WITH INVALID API key (should be rejected):")
    print("-" * 80)
    
    # Protected endpoints with invalid API key - should all return 403
    protected_wrong_key = [
        ("Auth Status (wrong key)", "GET", "/auth/status", {"X-API-KEY": "wrong_key"}, 403),
        ("Auth Logout (wrong key)", "POST", "/auth/logout", {"X-API-KEY": "wrong_key"}, 403),
        ("Lists (wrong key)", "GET", "/lists", {"X-API-KEY": "wrong_key"}, 403),
    ]
    
    for test in protected_wrong_key:
        if test_endpoint(*test):
            tests_passed += 1
        else:
            tests_failed += 1
    
    print()
    print("Testing PROTECTED endpoints WITH VALID API key (should be accepted):")
    print("-" * 80)
    
    # Protected endpoints with valid API key - should pass API key check
    # Note: Some may still fail with 401 if Microsoft To Do authentication is not set up
    protected_valid_key = [
        ("Auth Status (valid key)", "GET", "/auth/status", {"X-API-KEY": API_KEY}, 200),
        ("Auth Logout (valid key)", "POST", "/auth/logout", {"X-API-KEY": API_KEY}, 200),
        # Lists will return 401 if not authenticated with Microsoft To Do, which is expected
    ]
    
    for test in protected_valid_key:
        if test_endpoint(*test):
            tests_passed += 1
        else:
            tests_failed += 1
    
    # Special case: Lists with valid API key (may fail MS To Do auth)
    print("  INFO: Testing Lists endpoint with valid API key...")
    response = requests.get(f"{BASE_URL}/lists", headers={"X-API-KEY": API_KEY}, timeout=5)
    if response.status_code in [200, 401]:
        # 200 = success, 401 = MS To Do not authenticated (but API key was accepted)
        if response.status_code == 401 and "Not authenticated" in response.text:
            print(f"✓ PASS: Lists (valid key, MS ToDo not auth) (status: 401)")
        elif response.status_code == 200:
            print(f"✓ PASS: Lists (valid key, fully authenticated) (status: 200)")
        else:
            print(f"  INFO: Lists (valid key)                     (status: {response.status_code})")
        tests_passed += 1
    elif response.status_code == 403:
        print(f"✗ FAIL: Lists (valid key)                     (status: 403 - API key rejected!)")
        tests_failed += 1
    else:
        print(f"  INFO: Lists (valid key)                     (status: {response.status_code})")
        tests_passed += 1
    
    print()
    print("=" * 80)
    print(f"RESULTS: {tests_passed} passed, {tests_failed} failed")
    print("=" * 80)
    
    if tests_failed > 0:
        print()
        print("⚠ Some tests failed. Please check the configuration:")
        print("  1. Ensure ENABLE_API_KEY=true in .env")
        print("  2. Ensure X_API_KEY is set correctly in .env")
        print("  3. Restart the server after changing .env")
        sys.exit(1)
    else:
        print()
        print("✓ ALL TESTS PASSED!")
        print("  API key protection is working correctly.")
        sys.exit(0)


if __name__ == "__main__":
    main()
