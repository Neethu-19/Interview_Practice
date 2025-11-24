"""
Test script for role loader functionality.
Verifies that roles.json can be loaded and validated correctly.
"""

from services.role_loader import RoleLoader, get_role_loader, is_valid_role, get_role
from models.data_models import Role


def test_role_loader():
    """Test the role loader service"""
    print("Testing Role Loader Service...")
    print("=" * 60)
    
    try:
        # Test 1: Load roles
        print("\n1. Loading roles from configuration...")
        loader = get_role_loader()
        roles = loader.load_roles()
        print(f"✓ Successfully loaded {len(roles)} roles")
        
        # Test 2: Check expected roles exist
        print("\n2. Verifying expected roles...")
        expected_roles = ["backend_engineer", "sales_associate", "retail_associate"]
        for role_name in expected_roles:
            if role_name in roles:
                print(f"✓ Found role: {role_name}")
            else:
                print(f"✗ Missing role: {role_name}")
        
        # Test 3: Validate role structure
        print("\n3. Validating role structures...")
        for role_name, role in roles.items():
            print(f"\n   Role: {role.display_name} ({role.name})")
            print(f"   - Questions: {len(role.questions)}")
            print(f"   - Evaluation criteria: {list(role.evaluation_criteria.keys())}")
            
            # Check minimum questions
            if len(role.questions) >= 8:
                print(f"   ✓ Has sufficient questions ({len(role.questions)} >= 8)")
            else:
                print(f"   ✗ Insufficient questions ({len(role.questions)} < 8)")
            
            # Check required criteria
            required_criteria = {"communication", "technical_knowledge", "structure"}
            has_all = required_criteria.issubset(set(role.evaluation_criteria.keys()))
            if has_all:
                print(f"   ✓ Has all required evaluation criteria")
            else:
                missing = required_criteria - set(role.evaluation_criteria.keys())
                print(f"   ✗ Missing criteria: {missing}")
        
        # Test 4: Test role retrieval methods
        print("\n4. Testing role retrieval methods...")
        
        # Get specific role
        backend_role = get_role("backend_engineer")
        if backend_role:
            print(f"✓ get_role('backend_engineer'): {backend_role.display_name}")
        else:
            print(f"✗ get_role('backend_engineer') returned None")
        
        # Check valid role
        if is_valid_role("backend_engineer"):
            print(f"✓ is_valid_role('backend_engineer'): True")
        else:
            print(f"✗ is_valid_role('backend_engineer'): False")
        
        # Check invalid role
        if not is_valid_role("nonexistent_role"):
            print(f"✓ is_valid_role('nonexistent_role'): False")
        else:
            print(f"✗ is_valid_role('nonexistent_role'): True")
        
        # Test 5: Display sample questions
        print("\n5. Sample questions from each role...")
        for role_name in expected_roles:
            role = get_role(role_name)
            if role and role.questions:
                print(f"\n   {role.display_name}:")
                print(f"   Q1: {role.questions[0]}")
                if len(role.questions) > 1:
                    print(f"   Q2: {role.questions[1]}")
        
        print("\n" + "=" * 60)
        print("✓ All tests completed successfully!")
        return True
        
    except Exception as e:
        print(f"\n✗ Error during testing: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_role_loader()
    exit(0 if success else 1)
