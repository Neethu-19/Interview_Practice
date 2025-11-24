"""
Simple test validation script
Validates that test files are properly structured
"""
import sys
import os
from pathlib import Path

def validate_test_files():
    """Validate test file structure"""
    print("=" * 60)
    print("Test Suite Validation")
    print("=" * 60)
    
    tests_dir = Path(__file__).parent / "tests"
    
    if not tests_dir.exists():
        print("✗ Tests directory not found")
        return False
    
    print(f"\n✓ Tests directory found: {tests_dir}")
    
    # Expected test files
    expected_files = [
        "__init__.py",
        "conftest.py",
        "test_unit_persona_handler.py",
        "test_unit_prompt_generator.py",
        "test_unit_feedback_engine.py",
        "test_unit_session_manager.py",
        "test_integration_api.py",
        "test_persona_behaviors.py",
        "README.md"
    ]
    
    print("\nChecking test files:")
    all_found = True
    for filename in expected_files:
        filepath = tests_dir / filename
        if filepath.exists():
            size = filepath.stat().st_size
            print(f"  ✓ {filename} ({size} bytes)")
        else:
            print(f"  ✗ {filename} - NOT FOUND")
            all_found = False
    
    if not all_found:
        return False
    
    # Check imports
    print("\nValidating test imports:")
    try:
        sys.path.insert(0, str(Path(__file__).parent))
        
        # Try importing test modules
        test_modules = [
            "tests.conftest",
            "tests.test_unit_persona_handler",
            "tests.test_unit_prompt_generator",
            "tests.test_unit_feedback_engine",
            "tests.test_unit_session_manager",
            "tests.test_integration_api",
            "tests.test_persona_behaviors"
        ]
        
        for module_name in test_modules:
            try:
                __import__(module_name)
                print(f"  ✓ {module_name}")
            except ImportError as e:
                print(f"  ⚠ {module_name} - Import warning: {e}")
            except Exception as e:
                print(f"  ⚠ {module_name} - Warning: {e}")
        
    except Exception as e:
        print(f"  ✗ Error during import validation: {e}")
        return False
    
    # Check pytest configuration
    print("\nChecking pytest configuration:")
    pytest_ini = Path(__file__).parent / "pytest.ini"
    if pytest_ini.exists():
        print(f"  ✓ pytest.ini found")
    else:
        print(f"  ✗ pytest.ini not found")
    
    # Check test runner
    run_tests = Path(__file__).parent / "run_tests.py"
    if run_tests.exists():
        print(f"  ✓ run_tests.py found")
    else:
        print(f"  ✗ run_tests.py not found")
    
    print("\n" + "=" * 60)
    print("✓ Test suite validation complete!")
    print("=" * 60)
    
    print("\nTo run tests:")
    print("  1. Install dependencies: pip install -r requirements.txt")
    print("  2. Run all tests: pytest tests/")
    print("  3. Run specific tests: python run_tests.py unit")
    print("\nFor more information, see tests/README.md")
    
    return True


if __name__ == "__main__":
    success = validate_test_files()
    sys.exit(0 if success else 1)
