#!/usr/bin/env python3
"""
Comprehensive test script to verify all fixes:
1. OAUTHLIB environment variables not forced
2. API prefix normalization
3. Async httpx integration (basic import test)
4. GraphAPIError with status_code
5. Pagination support in models
"""

import os
import sys

# Constants
OAUTHLIB_VARS = ['OAUTHLIB_INSECURE_TRANSPORT', 'OAUTHLIB_RELAX_TOKEN_SCOPE', 'OAUTHLIB_IGNORE_SCOPE_CHANGE']


def test_oauthlib_not_forced():
    """Test that OAUTHLIB variables are not forced by config"""
    print("\n" + "="*80)
    print("TEST 1: OAUTHLIB Variables Not Forced")
    print("="*80)
    
    # Clear any existing OAUTHLIB variables
    for var in OAUTHLIB_VARS:
        os.environ.pop(var, None)
    
    # Import config
    from api.config import Settings
    
    # Check if variables are still not set
    passed = True
    for var in OAUTHLIB_VARS:
        value = os.environ.get(var)
        if value:
            print(f"✗ FAIL: {var} is set to '{value}' (should not be set by config.py)")
            passed = False
        else:
            print(f"✓ PASS: {var} is not set")
    
    return passed


def test_api_prefix_normalization():
    """Test API prefix normalization"""
    print("\n" + "="*80)
    print("TEST 2: API Prefix Normalization")
    print("="*80)
    
    from api.config import Settings
    
    tests = [
        ("", ""),
        ("api", "/api"),
        ("/api", "/api"),
        ("api/", "/api"),
        ("/api/", "/api"),
        ("  /api/v1/  ", "/api/v1"),
        ("///api///", "/api"),
    ]
    
    passed = True
    for input_val, expected in tests:
        os.environ['API_PREFIX'] = input_val
        s = Settings()
        if s.api_prefix == expected:
            print(f"✓ PASS: '{input_val}' -> '{s.api_prefix}' (expected: '{expected}')")
        else:
            print(f"✗ FAIL: '{input_val}' -> '{s.api_prefix}' (expected: '{expected}')")
            passed = False
    
    return passed


def test_httpx_integration():
    """Test that httpx is properly integrated"""
    print("\n" + "="*80)
    print("TEST 3: Async httpx Integration")
    print("="*80)
    
    try:
        import httpx
        print("✓ PASS: httpx module imported successfully")
        
        from api.graph_client import GraphAPIClient
        import inspect
        
        # Check that _make_request is async
        if inspect.iscoroutinefunction(GraphAPIClient._make_request):
            print("✓ PASS: GraphAPIClient._make_request is async")
        else:
            print("✗ FAIL: GraphAPIClient._make_request is not async")
            return False
        
        # Check that get_lists is async
        if inspect.iscoroutinefunction(GraphAPIClient.get_lists):
            print("✓ PASS: GraphAPIClient.get_lists is async")
        else:
            print("✗ FAIL: GraphAPIClient.get_lists is not async")
            return False
        
        # Check that get_tasks is async
        if inspect.iscoroutinefunction(GraphAPIClient.get_tasks):
            print("✓ PASS: GraphAPIClient.get_tasks is async")
        else:
            print("✗ FAIL: GraphAPIClient.get_tasks is not async")
            return False
        
        return True
    except Exception as e:
        print(f"✗ FAIL: {e}")
        return False


def test_graph_api_error_status_code():
    """Test GraphAPIError has status_code attribute"""
    print("\n" + "="*80)
    print("TEST 4: GraphAPIError with status_code")
    print("="*80)
    
    from api.graph_client import GraphAPIError
    
    tests = [
        ("Test error", 500, "Test error", "[500] Test error"),
        ("Not found", 404, "Not found", "[404] Not found"),
        ("Unauthorized", 401, "Unauthorized", "[401] Unauthorized"),
    ]
    
    passed = True
    for msg, code, expected_msg, expected_str in tests:
        if code == 500:
            e = GraphAPIError(msg)  # Test default
        else:
            e = GraphAPIError(msg, status_code=code)
        
        if e.status_code == code and e.message == expected_msg and str(e) == expected_str:
            print(f"✓ PASS: GraphAPIError('{msg}', status_code={code})")
        else:
            print(f"✗ FAIL: GraphAPIError('{msg}', status_code={code})")
            print(f"  Expected: status_code={code}, message='{expected_msg}', str='{expected_str}'")
            print(f"  Got: status_code={e.status_code}, message='{e.message}', str='{str(e)}'")
            passed = False
    
    return passed


def test_pagination_models():
    """Test pagination models exist and are properly defined"""
    print("\n" + "="*80)
    print("TEST 5: Pagination Models")
    print("="*80)
    
    try:
        from api.models import PaginatedTaskListResponse, PaginatedTaskResponse, TaskListResponse, TaskResponse
        
        # Test PaginatedTaskListResponse
        print("✓ PASS: PaginatedTaskListResponse imported successfully")
        
        # Test PaginatedTaskResponse
        print("✓ PASS: PaginatedTaskResponse imported successfully")
        
        # Create a sample paginated response to verify structure
        sample_list = PaginatedTaskListResponse(
            value=[],
            nextLink="https://example.com/next",
            count=0
        )
        
        if hasattr(sample_list, 'value') and hasattr(sample_list, 'nextLink') and hasattr(sample_list, 'count'):
            print("✓ PASS: PaginatedTaskListResponse has correct attributes")
        else:
            print("✗ FAIL: PaginatedTaskListResponse missing attributes")
            return False
        
        sample_tasks = PaginatedTaskResponse(
            value=[],
            nextLink="https://example.com/next",
            count=0
        )
        
        if hasattr(sample_tasks, 'value') and hasattr(sample_tasks, 'nextLink') and hasattr(sample_tasks, 'count'):
            print("✓ PASS: PaginatedTaskResponse has correct attributes")
        else:
            print("✗ FAIL: PaginatedTaskResponse missing attributes")
            return False
        
        return True
    except Exception as e:
        print(f"✗ FAIL: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_routes_use_status_code():
    """Test that routes use GraphAPIError.status_code instead of string matching"""
    print("\n" + "="*80)
    print("TEST 6: Routes Use status_code (Not String Matching)")
    print("="*80)
    
    import re
    
    files_to_check = [
        'api/routes/lists.py',
        'api/routes/tasks.py',
        'api/routes/html.py',
    ]
    
    passed = True
    for file_path in files_to_check:
        with open(file_path, 'r') as f:
            content = f.read()
        
        # Check for old pattern: "404" in str(e)
        if '"404" in str(e)' in content or "'404' in str(e)" in content:
            print(f"✗ FAIL: {file_path} still uses string matching for status codes")
            passed = False
        else:
            print(f"✓ PASS: {file_path} does not use string matching")
        
        # Check for new pattern: e.status_code
        if 'e.status_code' in content:
            print(f"✓ PASS: {file_path} uses e.status_code")
        else:
            print(f"✗ FAIL: {file_path} does not use e.status_code")
            passed = False
    
    return passed


def test_pagination_in_routes():
    """Test that routes support pagination parameters"""
    print("\n" + "="*80)
    print("TEST 7: Routes Support Pagination")
    print("="*80)
    
    files_to_check = [
        ('api/routes/lists.py', 'skip_token'),
        ('api/routes/tasks.py', 'skip_token'),
    ]
    
    passed = True
    for file_path, param_name in files_to_check:
        with open(file_path, 'r') as f:
            content = f.read()
        
        if param_name in content:
            print(f"✓ PASS: {file_path} supports {param_name} parameter")
        else:
            print(f"✗ FAIL: {file_path} does not support {param_name} parameter")
            passed = False
    
    return passed


def main():
    print("="*80)
    print("COMPREHENSIVE TEST SUITE FOR ALL FIXES")
    print("="*80)
    
    # Set minimal required environment variables
    os.environ.setdefault('CLIENT_ID', 'test_client_id')
    os.environ.setdefault('CLIENT_SECRET', 'test_client_secret')
    
    # Run tests
    test1_passed = test_oauthlib_not_forced()
    test2_passed = test_api_prefix_normalization()
    test3_passed = test_httpx_integration()
    test4_passed = test_graph_api_error_status_code()
    test5_passed = test_pagination_models()
    test6_passed = test_routes_use_status_code()
    test7_passed = test_pagination_in_routes()
    
    # Summary
    print("\n" + "="*80)
    print("FINAL RESULTS")
    print("="*80)
    print(f"Test 1 (OAUTHLIB not forced): {'✓ PASSED' if test1_passed else '✗ FAILED'}")
    print(f"Test 2 (API prefix normalization): {'✓ PASSED' if test2_passed else '✗ FAILED'}")
    print(f"Test 3 (Async httpx integration): {'✓ PASSED' if test3_passed else '✗ FAILED'}")
    print(f"Test 4 (GraphAPIError status_code): {'✓ PASSED' if test4_passed else '✗ FAILED'}")
    print(f"Test 5 (Pagination models): {'✓ PASSED' if test5_passed else '✗ FAILED'}")
    print(f"Test 6 (Routes use status_code): {'✓ PASSED' if test6_passed else '✗ FAILED'}")
    print(f"Test 7 (Routes support pagination): {'✓ PASSED' if test7_passed else '✗ FAILED'}")
    print("="*80)
    
    all_passed = all([test1_passed, test2_passed, test3_passed, test4_passed, test5_passed, test6_passed, test7_passed])
    
    if all_passed:
        print("\n✓ ALL TESTS PASSED!")
        sys.exit(0)
    else:
        print("\n✗ SOME TESTS FAILED")
        sys.exit(1)


if __name__ == "__main__":
    main()
