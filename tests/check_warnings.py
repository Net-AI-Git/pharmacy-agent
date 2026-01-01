"""
Script to check what warnings are generated during test execution.

Purpose (Why):
Helps identify warnings that might need attention by running tests with warnings enabled.

Implementation (What):
Runs pytest with warnings enabled and filters to show only warnings.
"""

import subprocess
import sys
from pathlib import Path


def main():
    """Run tests with warnings enabled to see what warnings are generated."""
    tests_dir = Path(__file__).parent
    
    print("=" * 60)
    print("Checking Warnings in Tests")
    print("=" * 60)
    print()
    print("Running tests with warnings enabled...")
    print()
    
    # Run pytest with warnings enabled
    cmd = [
        sys.executable,
        "-m", "pytest",
        str(tests_dir),
        "-v",
        "-W", "default",  # Show all warnings
        "--tb=no",  # No traceback, just warnings
    ]
    
    result = subprocess.run(cmd, cwd=tests_dir.parent, capture_output=True, text=True)
    
    # Extract warnings from output
    output_lines = result.stdout.split("\n") + result.stderr.split("\n")
    warnings = [line for line in output_lines if "warning" in line.lower() or "Warning" in line]
    
    if warnings:
        print("Warnings found:")
        print("-" * 60)
        for warning in warnings:
            print(warning)
        print("-" * 60)
        print()
        print("Total warnings:", len(warnings))
    else:
        print("✅ No warnings found!")
    
    print()
    print("=" * 60)
    print("Full test output:")
    print("=" * 60)
    print(result.stdout)
    if result.stderr:
        print("STDERR:")
        print(result.stderr)


if __name__ == "__main__":
    main()

