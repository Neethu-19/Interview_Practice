"""
Test runner script for Interview Practice Partner
Runs all automated tests with pytest
"""
import sys
import subprocess


def run_tests(test_type="all", verbose=True):
    """
    Run tests using pytest
    
    Args:
        test_type: Type of tests to run ("all", "unit", "integration", "persona")
        verbose: Whether to show verbose output
    """
    cmd = ["pytest"]
    
    if verbose:
        cmd.append("-v")
    
    # Select test type
    if test_type == "unit":
        cmd.extend(["-m", "unit", "tests/test_unit_*.py"])
    elif test_type == "integration":
        cmd.extend(["tests/test_integration_*.py"])
    elif test_type == "persona":
        cmd.extend(["tests/test_persona_*.py"])
    elif test_type == "all":
        cmd.append("tests/")
    else:
        print(f"Unknown test type: {test_type}")
        print("Valid types: all, unit, integration, persona")
        return 1
    
    print(f"Running {test_type} tests...")
    print(f"Command: {' '.join(cmd)}")
    print("=" * 60)
    
    try:
        result = subprocess.run(cmd, cwd=".")
        return result.returncode
    except FileNotFoundError:
        print("\nError: pytest not found. Please install test dependencies:")
        print("  pip install -r requirements.txt")
        return 1


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Run Interview Practice Partner tests")
    parser.add_argument(
        "test_type",
        nargs="?",
        default="all",
        choices=["all", "unit", "integration", "persona"],
        help="Type of tests to run (default: all)"
    )
    parser.add_argument(
        "-q", "--quiet",
        action="store_true",
        help="Run tests in quiet mode"
    )
    
    args = parser.parse_args()
    
    return run_tests(args.test_type, verbose=not args.quiet)


if __name__ == "__main__":
    sys.exit(main())
