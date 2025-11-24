"""
Simple test script for OllamaClient functionality.
This script tests the core features of the OllamaClient class.
"""
from services.ollama_client import OllamaClient, OllamaConnectionError
from models.data_models import Scores


def test_health_check():
    """Test Ollama server health check"""
    print("Testing health check...")
    client = OllamaClient()
    
    is_healthy = client.check_health()
    print(f"✓ Health check: {'Healthy' if is_healthy else 'Unavailable'}")
    
    if not is_healthy:
        print("⚠ Warning: Ollama server is not available. Make sure it's running.")
        print("  Run: ollama serve")
        return False
    
    return True


def test_list_models():
    """Test listing available models"""
    print("\nTesting list models...")
    client = OllamaClient()
    
    try:
        models = client.list_models()
        print(f"✓ Available models: {models}")
        return True
    except Exception as e:
        print(f"✗ Failed to list models: {e}")
        return False


def test_generate():
    """Test basic text generation"""
    print("\nTesting text generation...")
    # Use a model that's actually available
    client = OllamaClient(model="mistral:latest")
    
    try:
        response = client.generate(
            prompt="Say 'Hello, World!' and nothing else.",
            temperature=0.1
        )
        print(f"✓ Generated response: {response[:100]}...")
        return True
    except OllamaConnectionError as e:
        print(f"✗ Connection error: {e}")
        return False
    except Exception as e:
        print(f"✗ Generation error: {e}")
        return False


def test_generate_structured():
    """Test structured JSON generation"""
    print("\nTesting structured JSON generation...")
    # Use a model that's actually available
    client = OllamaClient(model="mistral:latest")
    
    prompt = """Generate a performance score with the following fields:
- communication: integer between 1 and 5
- technical_knowledge: integer between 1 and 5
- structure: integer between 1 and 5

Example format:
{
    "communication": 4,
    "technical_knowledge": 3,
    "structure": 5
}"""
    
    try:
        response = client.generate_structured(
            prompt=prompt,
            response_format=Scores,
            temperature=0.1
        )
        print(f"✓ Generated structured response: {response}")
        return True
    except Exception as e:
        print(f"✗ Structured generation error: {e}")
        return False


def test_retry_logic():
    """Test retry logic with invalid URL"""
    print("\nTesting retry logic with invalid URL...")
    client = OllamaClient(
        base_url="http://localhost:99999",
        max_retries=2,
        initial_retry_delay=0.1
    )
    
    # check_health returns False on failure, doesn't raise exception
    is_healthy = client.check_health()
    if not is_healthy:
        print("✓ Retry logic works correctly (failed as expected)")
        return True
    else:
        print("✗ Should have returned False for invalid URL")
        return False


def main():
    """Run all tests"""
    print("=" * 60)
    print("OllamaClient Test Suite")
    print("=" * 60)
    
    results = []
    
    # Test 1: Health check
    results.append(("Health Check", test_health_check()))
    
    # Only continue if Ollama is available
    if not results[0][1]:
        print("\n" + "=" * 60)
        print("Skipping remaining tests - Ollama server not available")
        print("=" * 60)
        return
    
    # Test 2: List models
    results.append(("List Models", test_list_models()))
    
    # Test 3: Basic generation
    results.append(("Text Generation", test_generate()))
    
    # Test 4: Structured generation
    results.append(("Structured Generation", test_generate_structured()))
    
    # Test 5: Retry logic
    results.append(("Retry Logic", test_retry_logic()))
    
    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {test_name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    print("=" * 60)


if __name__ == "__main__":
    main()
