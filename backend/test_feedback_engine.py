"""
Test script for FeedbackEngine

Tests feedback generation with mock interview data.
"""

import sys
from uuid import uuid4
from datetime import datetime
from models.data_models import Role, Message, MessageType
from services.ollama_client import OllamaClient
from services.prompt_generator import PromptGenerator
from services.feedback_engine import FeedbackEngine


def create_test_role() -> Role:
    """Create a test role for feedback generation"""
    return Role(
        name="backend_engineer",
        display_name="Backend Engineer",
        questions=[
            "Tell me about your experience with Python and backend development.",
            "How do you approach debugging a production issue?",
            "Describe a challenging technical problem you solved."
        ],
        evaluation_criteria={
            "technical_depth": "Demonstrates understanding of backend concepts",
            "problem_solving": "Shows systematic approach to challenges",
            "communication": "Explains technical concepts clearly"
        }
    )


def create_test_transcript() -> list:
    """Create a mock interview transcript"""
    return [
        Message(
            type=MessageType.QUESTION,
            content="Tell me about your experience with Python and backend development.",
            timestamp=datetime.now()
        ),
        Message(
            type=MessageType.ANSWER,
            content="I have 3 years of experience with Python, primarily using FastAPI and Django for building REST APIs. I've worked on microservices architecture, implemented authentication systems, and optimized database queries for performance.",
            timestamp=datetime.now()
        ),
        Message(
            type=MessageType.FOLLOWUP,
            content="Can you give me a specific example of a performance optimization you implemented?",
            timestamp=datetime.now()
        ),
        Message(
            type=MessageType.ANSWER,
            content="Sure! In one project, we had slow API responses due to N+1 query problems. I identified the issue using Django Debug Toolbar, then refactored the code to use select_related and prefetch_related. This reduced response time from 2 seconds to 200ms.",
            timestamp=datetime.now()
        ),
        Message(
            type=MessageType.QUESTION,
            content="How do you approach debugging a production issue?",
            timestamp=datetime.now()
        ),
        Message(
            type=MessageType.ANSWER,
            content="I follow a systematic approach: First, I check logs and monitoring dashboards to understand the scope. Then I try to reproduce the issue in a staging environment. I use debugging tools and add additional logging if needed. Once identified, I implement a fix, test thoroughly, and deploy with proper rollback plans.",
            timestamp=datetime.now()
        )
    ]


def test_feedback_generation():
    """Test basic feedback generation"""
    print("=" * 60)
    print("Testing FeedbackEngine - Feedback Generation")
    print("=" * 60)
    
    # Initialize components
    ollama_client = OllamaClient(
        base_url="http://localhost:11434",
        model="llama3.1:8b"
    )
    
    # Check Ollama health
    print("\n1. Checking Ollama connection...")
    if not ollama_client.check_health():
        print("❌ Error: Ollama server is not available")
        print("   Please ensure Ollama is running: ollama serve")
        return False
    print("✓ Ollama server is healthy")
    
    # Initialize services
    prompt_generator = PromptGenerator()
    feedback_engine = FeedbackEngine(
        ollama_client=ollama_client,
        prompt_generator=prompt_generator,
        timeout_seconds=10,
        temperature=0.3
    )
    
    # Create test data
    session_id = uuid4()
    role = create_test_role()
    transcript = create_test_transcript()
    
    print(f"\n2. Generating feedback for session: {session_id}")
    print(f"   Role: {role.display_name}")
    print(f"   Transcript messages: {len(transcript)}")
    
    try:
        import time
        start_time = time.time()
        
        feedback = feedback_engine.generate_feedback(
            session_id=session_id,
            role=role,
            transcript=transcript
        )
        
        elapsed_time = time.time() - start_time
        
        print(f"\n✓ Feedback generated successfully in {elapsed_time:.2f}s")
        
        # Display feedback
        print("\n" + "=" * 60)
        print("FEEDBACK REPORT")
        print("=" * 60)
        
        print(f"\nSession ID: {feedback.session_id}")
        print(f"Generated at: {feedback.generated_at}")
        
        print("\n--- SCORES ---")
        print(f"Communication: {feedback.scores.communication}/5")
        print(f"Technical Knowledge: {feedback.scores.technical_knowledge}/5")
        print(f"Structure: {feedback.scores.structure}/5")
        print(f"Average: {feedback.scores.average}/5")
        
        print("\n--- STRENGTHS ---")
        for i, strength in enumerate(feedback.strengths, 1):
            print(f"{i}. {strength}")
        
        print("\n--- AREAS FOR IMPROVEMENT ---")
        for i, improvement in enumerate(feedback.improvements, 1):
            print(f"{i}. {improvement}")
        
        print("\n--- OVERALL FEEDBACK ---")
        print(feedback.overall_feedback)
        
        print("\n" + "=" * 60)
        
        # Validate feedback structure
        print("\n3. Validating feedback structure...")
        
        # Check scores are in range
        assert 1 <= feedback.scores.communication <= 5, "Communication score out of range"
        assert 1 <= feedback.scores.technical_knowledge <= 5, "Technical score out of range"
        assert 1 <= feedback.scores.structure <= 5, "Structure score out of range"
        print("✓ All scores are within valid range (1-5)")
        
        # Check exactly 3 strengths and improvements
        assert len(feedback.strengths) == 3, f"Expected 3 strengths, got {len(feedback.strengths)}"
        assert len(feedback.improvements) == 3, f"Expected 3 improvements, got {len(feedback.improvements)}"
        print("✓ Exactly 3 strengths and 3 improvements provided")
        
        # Check overall feedback length
        assert len(feedback.overall_feedback) >= 50, "Overall feedback too short"
        print("✓ Overall feedback meets minimum length requirement")
        
        # Check timeout compliance
        assert elapsed_time <= 10, f"Feedback generation took {elapsed_time:.2f}s, exceeding 10s limit"
        print(f"✓ Feedback generated within timeout ({elapsed_time:.2f}s < 10s)")
        
        print("\n" + "=" * 60)
        print("✓ All tests passed!")
        print("=" * 60)
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error generating feedback: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_score_validation():
    """Test score validation and clamping"""
    print("\n" + "=" * 60)
    print("Testing FeedbackEngine - Score Validation")
    print("=" * 60)
    
    ollama_client = OllamaClient()
    prompt_generator = PromptGenerator()
    feedback_engine = FeedbackEngine(
        ollama_client=ollama_client,
        prompt_generator=prompt_generator
    )
    
    # Test valid scores
    print("\n1. Testing valid scores...")
    for score in [1, 2, 3, 4, 5]:
        result = feedback_engine._validate_score(score, "test")
        assert result == score, f"Valid score {score} should remain unchanged"
    print("✓ Valid scores (1-5) pass validation")
    
    # Test clamping
    print("\n2. Testing score clamping...")
    assert feedback_engine._validate_score(0, "test") == 1, "Score 0 should clamp to 1"
    assert feedback_engine._validate_score(-5, "test") == 1, "Negative score should clamp to 1"
    assert feedback_engine._validate_score(6, "test") == 5, "Score 6 should clamp to 5"
    assert feedback_engine._validate_score(100, "test") == 5, "Score 100 should clamp to 5"
    print("✓ Out-of-range scores are clamped correctly")
    
    # Test invalid inputs
    print("\n3. Testing invalid score inputs...")
    try:
        feedback_engine._validate_score(None, "test")
        print("❌ Should have raised error for None")
        return False
    except Exception:
        print("✓ None score raises validation error")
    
    try:
        feedback_engine._validate_score("invalid", "test")
        print("❌ Should have raised error for string")
        return False
    except Exception:
        print("✓ String score raises validation error")
    
    print("\n✓ Score validation tests passed!")
    return True


def test_ensure_three_items():
    """Test ensuring exactly 3 items in lists"""
    print("\n" + "=" * 60)
    print("Testing FeedbackEngine - Three Items Validation")
    print("=" * 60)
    
    ollama_client = OllamaClient()
    prompt_generator = PromptGenerator()
    feedback_engine = FeedbackEngine(
        ollama_client=ollama_client,
        prompt_generator=prompt_generator
    )
    
    # Test with exactly 3 items
    print("\n1. Testing with exactly 3 items...")
    items = ["Item 1", "Item 2", "Item 3"]
    result = feedback_engine._ensure_three_items(items, "test", "Fallback")
    assert len(result) == 3, "Should have 3 items"
    assert result == items, "Items should be unchanged"
    print("✓ List with 3 items remains unchanged")
    
    # Test with fewer than 3 items
    print("\n2. Testing with fewer than 3 items...")
    items = ["Item 1"]
    result = feedback_engine._ensure_three_items(items, "test", "Fallback")
    assert len(result) == 3, "Should pad to 3 items"
    assert result[0] == "Item 1", "Original item should be preserved"
    print("✓ List padded to 3 items with fallback text")
    
    # Test with more than 3 items
    print("\n3. Testing with more than 3 items...")
    items = ["Item 1", "Item 2", "Item 3", "Item 4", "Item 5"]
    result = feedback_engine._ensure_three_items(items, "test", "Fallback")
    assert len(result) == 3, "Should truncate to 3 items"
    assert result == items[:3], "Should keep first 3 items"
    print("✓ List truncated to first 3 items")
    
    # Test with empty strings
    print("\n4. Testing with empty strings...")
    items = ["Item 1", "", "  ", "Item 2"]
    result = feedback_engine._ensure_three_items(items, "test", "Fallback")
    assert len(result) == 3, "Should have 3 items"
    assert result[0] == "Item 1", "First valid item preserved"
    assert result[1] == "Item 2", "Second valid item preserved"
    print("✓ Empty strings filtered out and replaced")
    
    print("\n✓ Three items validation tests passed!")
    return True


def main():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("FEEDBACK ENGINE TEST SUITE")
    print("=" * 60)
    
    tests = [
        ("Score Validation", test_score_validation),
        ("Three Items Validation", test_ensure_three_items),
        ("Feedback Generation", test_feedback_generation),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\n❌ Test '{test_name}' failed with exception: {e}")
            import traceback
            traceback.print_exc()
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    for test_name, result in results:
        status = "✓ PASSED" if result else "❌ FAILED"
        print(f"{status}: {test_name}")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed!")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
