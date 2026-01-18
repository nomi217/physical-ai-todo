#!/usr/bin/env python3
"""
Automated Authentication Testing Suite
Tests all Phase 2 authentication features before user delivery
"""

import requests
import json
import sys
from datetime import datetime

# Configuration
FRONTEND_URL = "http://localhost:3001"
BACKEND_URL = "http://127.0.0.1:8000"

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'
    BOLD = '\033[1m'

def print_test(name, status, details=""):
    """Print formatted test result"""
    icon = "[PASS]" if status else "[FAIL]"
    color = Colors.GREEN if status else Colors.RED
    print(f"{color}{icon}{Colors.END} {name}")
    if details:
        print(f"  {Colors.BLUE}-->{Colors.END} {details}")

def test_backend_health():
    """Test 1: Backend Health Check"""
    print(f"\n{Colors.BOLD}=== Backend API Tests ==={Colors.END}")
    try:
        response = requests.get(f"{BACKEND_URL}/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print_test("Backend Health", True, f"Status: {data.get('status')}, Version: {data.get('version')}")
            return True
        else:
            print_test("Backend Health", False, f"Status code: {response.status_code}")
            return False
    except Exception as e:
        print_test("Backend Health", False, f"Error: {str(e)}")
        return False

def test_backend_routes():
    """Test 2: Backend Auth Routes Exist"""
    routes = [
        ("/api/v1/auth/register", "POST", "Registration endpoint"),
        ("/api/v1/auth/login", "POST", "Login endpoint"),
        ("/api/v1/auth/verify-email", "POST", "Email verification endpoint"),
        ("/api/v1/auth/github/authorize", "GET", "GitHub OAuth authorize"),
        ("/api/v1/auth/github/callback", "POST", "GitHub OAuth callback"),
        ("/api/v1/auth/me", "GET", "Current user endpoint"),
        ("/api/v1/auth/logout", "POST", "Logout endpoint"),
    ]

    all_pass = True
    for path, method, desc in routes:
        try:
            # Just check if the endpoint exists (will return error but not 404)
            if method == "GET":
                response = requests.get(f"{BACKEND_URL}{path}", timeout=5, allow_redirects=False)
            else:
                response = requests.post(f"{BACKEND_URL}{path}", timeout=5, json={})

            # 422 (validation error) or 401 (auth required) means endpoint exists
            # 404 means endpoint doesn't exist
            exists = response.status_code != 404
            print_test(desc, exists, f"{method} {path} - Status: {response.status_code}")
            if not exists:
                all_pass = False
        except Exception as e:
            print_test(desc, False, f"Error: {str(e)}")
            all_pass = False

    return all_pass

def test_frontend_pages():
    """Test 3: Frontend Pages Load"""
    print(f"\n{Colors.BOLD}=== Frontend Pages Tests ==={Colors.END}")

    pages = [
        ("/landing", "Landing Page"),
        ("/auth/signin", "Sign In Page"),
        ("/auth/signup", "Sign Up Page"),
        ("/auth/verify-email", "Verify Email Page"),
    ]

    all_pass = True
    for path, name in pages:
        try:
            response = requests.get(f"{FRONTEND_URL}{path}", timeout=10)
            if response.status_code == 200:
                # Check for key content
                content = response.text.lower()

                if "flowtask" in content or "physical ai todo" in content:
                    print_test(name, True, f"GET {path} - Status: 200, Content verified")
                else:
                    print_test(name, False, f"Page loaded but missing expected content")
                    all_pass = False
            else:
                print_test(name, False, f"Status: {response.status_code}")
                all_pass = False
        except Exception as e:
            print_test(name, False, f"Error: {str(e)}")
            all_pass = False

    return all_pass

def test_registration_flow():
    """Test 4: Registration Flow (Without Email)"""
    print(f"\n{Colors.BOLD}=== Registration Flow Test ==={Colors.END}")

    try:
        # Generate unique email for testing
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        test_email = f"test_{timestamp}@example.com"
        test_data = {
            "email": test_email,
            "password": "TestPassword123!",
            "full_name": "Test User"
        }

        response = requests.post(
            f"{BACKEND_URL}/api/v1/auth/register",
            json=test_data,
            timeout=5
        )

        if response.status_code == 201:
            data = response.json()
            print_test("User Registration", True, f"Created user: {data.get('email')}")
            print_test("Email Field", data.get('email') == test_email, f"Email: {data.get('email')}")
            print_test("Verification Status", data.get('is_verified') == False, f"is_verified: {data.get('is_verified')}")
            return True
        else:
            error = response.json()
            print_test("User Registration", False, f"Status: {response.status_code}, Error: {error.get('detail')}")
            return False
    except Exception as e:
        print_test("User Registration", False, f"Error: {str(e)}")
        return False

def test_login_validation():
    """Test 5: Login Validation"""
    print(f"\n{Colors.BOLD}=== Login Validation Test ==={Colors.END}")

    try:
        # Test with invalid credentials
        response = requests.post(
            f"{BACKEND_URL}/api/v1/auth/login",
            json={"email": "nonexistent@example.com", "password": "wrongpassword"},
            timeout=5
        )

        if response.status_code == 401:
            print_test("Invalid Login Rejected", True, "Returns 401 for invalid credentials")
            return True
        else:
            print_test("Invalid Login Rejected", False, f"Expected 401, got {response.status_code}")
            return False
    except Exception as e:
        print_test("Invalid Login Rejected", False, f"Error: {str(e)}")
        return False

def test_github_oauth_config():
    """Test 6: GitHub OAuth Configuration"""
    print(f"\n{Colors.BOLD}=== GitHub OAuth Configuration ==={Colors.END}")

    try:
        # Check if GitHub OAuth is configured
        response = requests.get(
            f"{BACKEND_URL}/api/v1/auth/github/authorize",
            timeout=5,
            allow_redirects=False
        )

        if response.status_code in [302, 307]:  # Redirect to GitHub (307 is temporary redirect)
            redirect_url = response.headers.get('Location', '')
            if 'github.com' in redirect_url:
                print_test("GitHub OAuth Configured", True, "Redirects to GitHub")
                return True
            else:
                print_test("GitHub OAuth Configured", False, f"Unexpected redirect: {redirect_url}")
                return False
        elif response.status_code == 501:  # Not configured
            print_test("GitHub OAuth Configured", False, "OAuth credentials not set in .env (Expected - needs setup)")
            return False
        else:
            print_test("GitHub OAuth Configured", False, f"Unexpected status: {response.status_code}")
            return False
    except Exception as e:
        print_test("GitHub OAuth Configured", False, f"Error: {str(e)}")
        return False

def test_cors_headers():
    """Test 7: CORS Configuration"""
    print(f"\n{Colors.BOLD}=== CORS Configuration ==={Colors.END}")

    try:
        response = requests.options(
            f"{BACKEND_URL}/api/v1/auth/login",
            headers={
                'Origin': FRONTEND_URL,
                'Access-Control-Request-Method': 'POST',
                'Access-Control-Request-Headers': 'Content-Type'
            },
            timeout=5
        )

        has_cors = 'access-control-allow-origin' in response.headers
        print_test("CORS Headers Present", has_cors, f"Allows origin: {response.headers.get('access-control-allow-origin', 'None')}")
        return has_cors
    except Exception as e:
        print_test("CORS Headers Present", False, f"Error: {str(e)}")
        return False

def run_all_tests():
    """Run all tests and generate report"""
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}  Phase 2 Authentication Test Suite{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.END}")

    results = {
        "Backend Health": test_backend_health(),
        "Backend Routes": test_backend_routes(),
        "Frontend Pages": test_frontend_pages(),
        "Registration Flow": test_registration_flow(),
        "Login Validation": test_login_validation(),
        "GitHub OAuth": test_github_oauth_config(),
        "CORS Configuration": test_cors_headers(),
    }

    # Summary
    print(f"\n{Colors.BOLD}{'='*60}{Colors.END}")
    print(f"{Colors.BOLD}Test Summary{Colors.END}")
    print(f"{'='*60}")

    passed = sum(1 for v in results.values() if v)
    total = len(results)
    percentage = (passed / total) * 100

    for name, result in results.items():
        status_color = Colors.GREEN if result else Colors.RED
        status_text = "PASS" if result else "FAIL"
        print(f"{status_color}{status_text}{Colors.END} - {name}")

    print(f"\n{Colors.BOLD}Results: {passed}/{total} tests passed ({percentage:.1f}%){Colors.END}")

    if passed == total:
        print(f"\n{Colors.GREEN}{Colors.BOLD}[SUCCESS] ALL TESTS PASSED - Ready for user delivery!{Colors.END}")
        return 0
    else:
        print(f"\n{Colors.YELLOW}{Colors.BOLD}[WARNING] Some tests failed - Review before delivery{Colors.END}")
        return 1

if __name__ == "__main__":
    sys.exit(run_all_tests())
