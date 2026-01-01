"""
Test runner script to execute all tests in the tests/ directory.

Purpose (Why):
Provides a single entry point to run all tests with proper configuration
and visual feedback.

Implementation (What):
Uses pytest to discover and run all test files, with verbose output
and clear status indicators (✅ PASS, ❌ FAIL, ⚠️ WARNING).
"""

import sys
import subprocess
from pathlib import Path


def main():
    """
    Main test runner function.
    
    Purpose (Why):
    Executes all tests using pytest with verbose output and proper exit codes.
    
    Implementation (What):
    Runs pytest with verbose mode, shows test names, and exits with appropriate code.
    """
    # Get the tests directory
    tests_dir = Path(__file__).parent
    
    # Build pytest command
    cmd = [
        sys.executable,
        "-m", "pytest",
        str(tests_dir),
        "-v",  # Verbose output
        "--tb=short",  # Short traceback format
        "--color=yes",  # Colored output
        "-ra",  # Show all test outcomes (pass, fail, skip, etc.)
    ]
    
    print("=" * 60)
    print("Running All Tests")
    print("=" * 60)
    print(f"Tests directory: {tests_dir}")
    print()
    
    # Run pytest
    result = subprocess.run(cmd, cwd=tests_dir.parent)
    
    print()
    print("=" * 60)
    if result.returncode == 0:
        print("✅ All tests passed!")
    else:
        print("❌ Some tests failed!")
    print("=" * 60)
    
    sys.exit(result.returncode)


if __name__ == "__main__":
    main()

