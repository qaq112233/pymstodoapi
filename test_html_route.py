#!/usr/bin/env python3
"""
Test script for HTML rendering route
Tests the e-ink display HTML generation functionality
"""
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

def test_config_validation():
    """Test configuration validation for query auth"""
    print("\n" + "="*80)
    print("TEST 1: Configuration Validation")
    print("="*80)
    
    from api.config import Settings
    
    # Test 1: ENABLE_QUERY_AUTH=true but no QUERY_PASSWD should fail
    print("Testing: ENABLE_QUERY_AUTH=true but no QUERY_PASSWD")
    os.environ['CLIENT_ID'] = 'test'
    os.environ['CLIENT_SECRET'] = 'test'
    os.environ['ENABLE_QUERY_AUTH'] = 'true'
    os.environ['QUERY_PASSWD'] = ''
    
    test_settings = Settings()
    try:
        test_settings.validate()
        print("✗ FAIL: Should have raised ValueError")
        return False
    except ValueError as e:
        if 'QUERY_PASSWD' in str(e):
            print("✓ PASS: Validation correctly rejects missing QUERY_PASSWD")
        else:
            print(f"✗ FAIL: Wrong error: {e}")
            return False
    
    # Test 2: ENABLE_QUERY_AUTH=false should not require QUERY_PASSWD
    print("Testing: ENABLE_QUERY_AUTH=false should not require QUERY_PASSWD")
    os.environ['ENABLE_QUERY_AUTH'] = 'false'
    test_settings = Settings()
    try:
        test_settings.validate()
        print("✓ PASS: Validation passes when ENABLE_QUERY_AUTH is false")
    except ValueError as e:
        print(f"✗ FAIL: Should not fail when ENABLE_QUERY_AUTH is false: {e}")
        return False
    
    # Test 3: ENABLE_QUERY_AUTH=true with QUERY_PASSWD should pass
    print("Testing: ENABLE_QUERY_AUTH=true with QUERY_PASSWD")
    os.environ['ENABLE_QUERY_AUTH'] = 'true'
    os.environ['QUERY_PASSWD'] = 'test_password'
    test_settings = Settings()
    try:
        test_settings.validate()
        print("✓ PASS: Validation passes with QUERY_PASSWD set")
    except ValueError as e:
        print(f"✗ FAIL: Should pass when QUERY_PASSWD is set: {e}")
        return False
    
    return True


def test_html_template():
    """Test that HTML template exists and is valid"""
    print("\n" + "="*80)
    print("TEST 2: HTML Template Validation")
    print("="*80)
    
    template_path = Path(__file__).parent / "api" / "templates" / "tasks.html"
    
    if not template_path.exists():
        print(f"✗ FAIL: Template not found at {template_path}")
        return False
    
    print(f"✓ PASS: Template exists at {template_path}")
    
    # Check template content
    content = template_path.read_text()
    required_elements = [
        'Generated at:',
        '{{ generated_at }}',
        'task-item',
        'starred',
        'due-today',
        '1600px',
        '960px',
        '{% for task in tasks %}'
    ]
    
    missing = []
    for element in required_elements:
        if element not in content:
            missing.append(element)
    
    if missing:
        print(f"✗ FAIL: Template missing required elements: {missing}")
        return False
    
    print("✓ PASS: Template contains all required elements")
    return True


def test_timezone_handling():
    """Test timezone handling for Asia/Shanghai"""
    print("\n" + "="*80)
    print("TEST 3: Timezone Handling")
    print("="*80)
    
    import pytz
    
    try:
        shanghai_tz = pytz.timezone('Asia/Shanghai')
        now = datetime.now(shanghai_tz)
        print(f"✓ PASS: Can create Shanghai timezone")
        print(f"        Current time in Shanghai: {now.strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Test UTC conversion
        utc_time = datetime.now(pytz.UTC)
        shanghai_time = utc_time.astimezone(shanghai_tz)
        
        # Shanghai should be UTC+8
        time_diff = (shanghai_time.utcoffset().total_seconds()) / 3600
        if time_diff == 8:
            print(f"✓ PASS: Shanghai timezone is correctly UTC+8")
        else:
            print(f"✗ FAIL: Shanghai timezone offset is {time_diff}, expected 8")
            return False
        
        return True
    except Exception as e:
        print(f"✗ FAIL: Error handling timezones: {e}")
        return False


def test_route_registration():
    """Test that HTML route is properly registered"""
    print("\n" + "="*80)
    print("TEST 4: Route Registration")
    print("="*80)
    
    try:
        # Set up environment
        os.environ['CLIENT_ID'] = 'test'
        os.environ['CLIENT_SECRET'] = 'test'
        os.environ['ENABLE_QUERY_AUTH'] = 'false'
        os.environ['QUERY_PASSWD'] = ''
        os.environ['ENABLE_API_KEY'] = 'false'
        
        from api.main import app
        
        # Check if html routes are registered
        html_routes = [route for route in app.routes if '/html/' in str(route.path)]
        
        if not html_routes:
            print("✗ FAIL: No HTML routes found in app")
            return False
        
        print(f"✓ PASS: Found {len(html_routes)} HTML route(s)")
        
        # Check for tasks.html route
        tasks_html_route = None
        for route in html_routes:
            if 'tasks.html' in str(route.path):
                tasks_html_route = route
                break
        
        if not tasks_html_route:
            print("✗ FAIL: tasks.html route not found")
            return False
        
        print(f"✓ PASS: tasks.html route registered at {tasks_html_route.path}")
        
        # Verify HTML route doesn't require API key
        from api.dependencies import verify_api_key
        
        # Check if verify_api_key is NOT in the dependencies
        has_api_key_dep = False
        if hasattr(tasks_html_route, 'dependant'):
            for dep in tasks_html_route.dependant.dependencies:
                if 'verify_api_key' in str(dep.call):
                    has_api_key_dep = True
                    break
        
        if has_api_key_dep:
            print("✗ FAIL: HTML route incorrectly has API key protection")
            return False
        
        print("✓ PASS: HTML route does not have API key protection")
        return True
        
    except Exception as e:
        print(f"✗ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_query_auth_dependency():
    """Test the query auth dependency function"""
    print("\n" + "="*80)
    print("TEST 5: Query Auth Dependency")
    print("="*80)
    
    try:
        import importlib
        os.environ['CLIENT_ID'] = 'test'
        os.environ['CLIENT_SECRET'] = 'test'
        os.environ['ENABLE_QUERY_AUTH'] = 'true'
        os.environ['QUERY_PASSWD'] = 'test_password'
        
        # Reload settings and module
        from api import config
        from api.routes import html
        importlib.reload(config)
        config.settings = config.Settings()
        importlib.reload(html)
        
        from api.routes.html import verify_query_auth
        from fastapi import HTTPException
        import asyncio
        
        # Test 1: No password when required
        print("Testing: No password when ENABLE_QUERY_AUTH=true")
        raised_403 = False
        try:
            asyncio.run(verify_query_auth(passwd=None))
        except HTTPException as e:
            if e.status_code == 403:
                raised_403 = True
        
        if raised_403:
            print("✓ PASS: Correctly raises 403 for missing password")
        else:
            print("✗ FAIL: Should have raised 403 for missing password")
            return False
        
        # Test 2: Wrong password
        print("Testing: Wrong password")
        raised_403 = False
        try:
            asyncio.run(verify_query_auth(passwd="wrong_password"))
        except HTTPException as e:
            if e.status_code == 403:
                raised_403 = True
        
        if raised_403:
            print("✓ PASS: Correctly raises 403 for wrong password")
        else:
            print("✗ FAIL: Should have raised 403 for wrong password")
            return False
        
        # Test 3: Correct password
        print("Testing: Correct password")
        raised_exception = False
        try:
            asyncio.run(verify_query_auth(passwd="test_password"))
        except HTTPException as e:
            raised_exception = True
        
        if not raised_exception:
            print("✓ PASS: Accepts correct password")
        else:
            print("✗ FAIL: Should not raise exception for correct password")
            return False
        
        # Test 4: Auth disabled
        print("Testing: Auth disabled (ENABLE_QUERY_AUTH=false)")
        os.environ['ENABLE_QUERY_AUTH'] = 'false'
        importlib.reload(config)
        config.settings = config.Settings()
        importlib.reload(html)
        
        raised_exception = False
        try:
            asyncio.run(verify_query_auth(passwd=None))
        except HTTPException as e:
            raised_exception = True
        
        if not raised_exception:
            print("✓ PASS: No auth required when ENABLE_QUERY_AUTH=false")
        else:
            print("✗ FAIL: Should not raise exception when auth disabled")
            return False
        
        return True
        
    except Exception as e:
        print(f"✗ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    print("="*80)
    print("TESTING HTML RENDERING ROUTE FOR E-INK DISPLAY")
    print("="*80)
    
    # Run tests
    test1_passed = test_config_validation()
    test2_passed = test_html_template()
    test3_passed = test_timezone_handling()
    test4_passed = test_route_registration()
    test5_passed = test_query_auth_dependency()
    
    # Summary
    print("\n" + "="*80)
    print("FINAL RESULTS")
    print("="*80)
    print(f"Test 1 (Config Validation): {'✓ PASSED' if test1_passed else '✗ FAILED'}")
    print(f"Test 2 (HTML Template): {'✓ PASSED' if test2_passed else '✗ FAILED'}")
    print(f"Test 3 (Timezone Handling): {'✓ PASSED' if test3_passed else '✗ FAILED'}")
    print(f"Test 4 (Route Registration): {'✓ PASSED' if test4_passed else '✗ FAILED'}")
    print(f"Test 5 (Query Auth Dependency): {'✓ PASSED' if test5_passed else '✗ FAILED'}")
    print("="*80)
    
    if all([test1_passed, test2_passed, test3_passed, test4_passed, test5_passed]):
        print("\n✓ ALL TESTS PASSED!")
        return 0
    else:
        print("\n✗ SOME TESTS FAILED")
        return 1


if __name__ == "__main__":
    sys.exit(main())
