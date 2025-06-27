#!/usr/bin/env python3
"""
Test runner script with various configurations and options.
Run with --help to see all options.
"""
import argparse
import subprocess
import sys
from typing import List
import os

def run_command(command: List[str]) -> int:
    """Run a command and return its exit code."""
    try:
        # Use python -m pytest to ensure we use the correct Python environment
        python_exe = sys.executable
        full_command = [python_exe, "-m"] + command
        print(f"Running command: {' '.join(full_command)}")
        result = subprocess.run(full_command, check=True)
        return result.returncode
    except subprocess.CalledProcessError as e:
        print(f"Error running command: {' '.join(full_command)}")
        print(f"Exit code: {e.returncode}")
        return e.returncode

def main() -> int:
    """Main entry point for the test runner."""
    parser = argparse.ArgumentParser(description="Run tests with various options")
    
    # Test selection options
    parser.add_argument("--unit", action="store_true", 
                       help="Run only unit tests")
    parser.add_argument("--integration", action="store_true",
                       help="Run only integration tests")
    parser.add_argument("--e2e", action="store_true",
                       help="Run only end-to-end tests")
    
    # Coverage options
    parser.add_argument("--coverage", action="store_true",
                       help="Generate coverage report")
    parser.add_argument("--coverage-html", action="store_true",
                       help="Generate HTML coverage report")
    
    # Type checking options
    parser.add_argument("--no-mypy", action="store_true",
                       help="Disable mypy type checking")
    
    # Test running options
    parser.add_argument("--verbose", "-v", action="store_true",
                       help="Verbose output")
    parser.add_argument("--failfast", action="store_true",
                       help="Stop on first failure")
    parser.add_argument("--pattern", "-p", type=str,
                       help="Only run tests matching this pattern")
    
    args = parser.parse_args()
    
    # Build pytest command
    command = ["pytest"]
    
    # Add test selection
    if args.unit:
        command.extend(["-m", "unit"])
    elif args.integration:
        command.extend(["-m", "integration"])
    elif args.e2e:
        command.extend(["-m", "e2e"])
    
    # Add coverage options
    if args.coverage or args.coverage_html:
        command.extend(["--cov=src", "--cov-report=term-missing"])
        if args.coverage_html:
            command.append("--cov-report=html")
    
    # Add type checking
    if not args.no_mypy:
        command.append("--mypy")
    
    # Add verbosity
    if args.verbose:
        command.append("-v")
    
    # Add failfast
    if args.failfast:
        command.append("--exitfirst")
    
    # Add pattern
    if args.pattern:
        command.extend(["-k", args.pattern])
    
    # Run the tests
    return run_command(command)

if __name__ == "__main__":
    sys.exit(main()) 