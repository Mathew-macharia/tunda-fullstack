#!/usr/bin/env python
"""
E2E Test Runner for Tunda Soko Backend

This script runs the complete E2E test suite with proper setup and teardown.
"""

import os
import sys
import subprocess
import time
from pathlib import Path

# Add backend to path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))


def check_server_running(url="http://127.0.0.1:8000/api/core/settings/", timeout=30):
    """Check if Django server is running"""
    import requests
    
    print(f"🔍 Checking if server is running at {url}...")
    
    for i in range(timeout):
        try:
            response = requests.get(url)
            # Accept any HTTP response (including 401, 403) as valid - means server is running
            if response.status_code in [200, 401, 403, 404, 405]:
                print("✅ Server is running")
                return True
        except requests.exceptions.RequestException:
            if i == 0:
                print("⏳ Waiting for server to start...")
            time.sleep(1)
    
    print("❌ Server is not responding")
    return False


def setup_test_environment():
    """Setup test environment"""
    print("🚀 Setting up E2E test environment...")
    
    # Setup test database
    db_setup_result = subprocess.run([
        sys.executable, "tests/db_setup.py", "setup"
    ], cwd=backend_dir)
    
    if db_setup_result.returncode != 0:
        print("❌ Failed to setup test database")
        return False
    
    return True


def cleanup_test_environment():
    """Cleanup test environment"""
    print("🧹 Cleaning up test environment...")
    
    cleanup_result = subprocess.run([
        sys.executable, "tests/db_setup.py", "cleanup"
    ], cwd=backend_dir)
    
    if cleanup_result.returncode != 0:
        print("⚠️  Warning: Failed to cleanup test database")


def run_tests(test_args=None):
    """Run E2E tests with pytest"""
    print("🧪 Running E2E tests...")
    
    # Base pytest command
    pytest_cmd = [
        sys.executable, "-m", "pytest",
        "tests/e2e/",
        "-v",
        "--tb=short",
        "--strict-markers",
        "-m", "e2e"
    ]
    
    # Add additional args if provided
    if test_args:
        pytest_cmd.extend(test_args)
    
    # Add coverage if not running specific tests
    if not test_args or not any('test_' in arg for arg in test_args):
        pytest_cmd.extend([
            "--cov=.",
            "--cov-report=term-missing",
            "--cov-report=html:tests/reports/coverage"
        ])
    
    # Run tests
    result = subprocess.run(pytest_cmd, cwd=backend_dir)
    
    return result.returncode == 0


def main():
    """Main execution function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Run E2E tests for Tunda Soko")
    parser.add_argument("--skip-setup", action="store_true", 
                       help="Skip test environment setup")
    parser.add_argument("--skip-cleanup", action="store_true",
                       help="Skip test environment cleanup")
    parser.add_argument("--skip-server-check", action="store_true",
                       help="Skip server running check")
    parser.add_argument("--test", type=str,
                       help="Run specific test (e.g., test_auth_workflow.py::TestUserRegistrationWorkflow)")
    parser.add_argument("--marker", type=str,
                       help="Run tests with specific marker (e.g., auth, workflow)")
    
    args = parser.parse_args()
    
    print("🌟 Tunda Soko E2E Test Runner")
    print("=" * 50)
    
    # Check if server is running
    if not args.skip_server_check:
        if not check_server_running():
            print("💡 Start your Django server with: python manage.py runserver")
            print("   Then run this script again with --skip-server-check")
            return 1
    
    # Setup test environment
    if not args.skip_setup:
        if not setup_test_environment():
            return 1
    
    # Prepare test arguments
    test_args = []
    
    if args.test:
        test_args.append(f"tests/e2e/{args.test}")
    
    if args.marker:
        test_args.extend(["-m", args.marker])
    
    try:
        # Run tests
        success = run_tests(test_args)
        
        if success:
            print("\n🎉 All E2E tests passed!")
            return_code = 0
        else:
            print("\n❌ Some E2E tests failed!")
            return_code = 1
            
    finally:
        # Cleanup
        if not args.skip_cleanup:
            cleanup_test_environment()
    
    print("\n📊 Test reports available at:")
    print("   - HTML Coverage: tests/reports/coverage/index.html")
    print("   - Test Report: tests/reports/report.html")
    
    return return_code


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code) 