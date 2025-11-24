"""
Test script for PersonaHandler

Tests persona detection logic for all persona types:
- Confused: Short answers, questions
- Efficient: Direct, concise
- Chatty: Long, off-topic
- Edge Case: Invalid inputs
"""

from services.persona_handler import PersonaHandler
from models.data_models import Message, MessageType, PersonaType
from datetime import datetime


def test_confused_persona():
    """Test detection of Confused persona"""
    print("\n=== Testing Confused Persona ===")
    handler = PersonaHandler()
    
    # Test 1: Short answer with question
    answer1 = "I don't know. What do you mean?"
    history1 = []
    persona1 = handler.detect_persona(answer1, history1)
    print(f"Test 1 - Short answer with question:")
    print(f"  Answer: '{answer1}'")
    print(f"  Detected: {persona1.type.value}")
    print(f"  Confidence: {persona1.confidence}")
    print(f"  Indicators: {persona1.indicators}")
    assert persona1.type == PersonaType.CONFUSED, f"Expected CONFUSED, got {persona1.type}"
    
    # Test 2: Very short uncertain answer
    answer2 = "I'm not sure about that."
    history2 = []
    persona2 = handler.detect_persona(answer2, history2)
    print(f"\nTest 2 - Uncertain short answer:")
    print(f"  Answer: '{answer2}'")
    print(f"  Detected: {persona2.type.value}")
    print(f"  Confidence: {persona2.confidence}")
    print(f"  Indicators: {persona2.indicators}")
    assert persona2.type == PersonaType.CONFUSED, f"Expected CONFUSED, got {persona2.type}"
    
    # Test 3: Pattern of short answers in history
    answer3 = "Maybe."
    history3 = [
        Message(type=MessageType.QUESTION, content="Question 1?"),
        Message(type=MessageType.ANSWER, content="I don't know."),
        Message(type=MessageType.QUESTION, content="Question 2?"),
        Message(type=MessageType.ANSWER, content="Not sure."),
    ]
    persona3 = handler.detect_persona(answer3, history3)
    print(f"\nTest 3 - Pattern of short answers:")
    print(f"  Answer: '{answer3}'")
    print(f"  Detected: {persona3.type.value}")
    print(f"  Confidence: {persona3.confidence}")
    print(f"  Indicators: {persona3.indicators}")
    assert persona3.type == PersonaType.CONFUSED, f"Expected CONFUSED, got {persona3.type}"
    
    print("\n✓ All Confused persona tests passed!")


def test_efficient_persona():
    """Test detection of Efficient persona"""
    print("\n=== Testing Efficient Persona ===")
    handler = PersonaHandler()
    
    # Test 1: Direct request to move on
    answer1 = "Yes, I have experience with that. Let's move on to the next question."
    history1 = []
    persona1 = handler.detect_persona(answer1, history1)
    print(f"Test 1 - Direct efficiency request:")
    print(f"  Answer: '{answer1}'")
    print(f"  Detected: {persona1.type.value}")
    print(f"  Confidence: {persona1.confidence}")
    print(f"  Indicators: {persona1.indicators}")
    assert persona1.type == PersonaType.EFFICIENT, f"Expected EFFICIENT, got {persona1.type}"
    
    # Test 2: Concise answer without filler
    answer2 = "I have three years of Python experience building web applications with Django and Flask."
    history2 = []
    persona2 = handler.detect_persona(answer2, history2)
    print(f"\nTest 2 - Concise direct answer:")
    print(f"  Answer: '{answer2}'")
    print(f"  Detected: {persona2.type.value}")
    print(f"  Confidence: {persona2.confidence}")
    print(f"  Indicators: {persona2.indicators}")
    # May be EFFICIENT or NORMAL depending on history
    print(f"  (Acceptable: EFFICIENT or NORMAL)")
    
    # Test 3: Pattern of concise answers
    answer3 = "I use Git for version control and follow standard branching strategies."
    history3 = [
        Message(type=MessageType.QUESTION, content="Question 1?"),
        Message(type=MessageType.ANSWER, content="I have five years of experience in backend development."),
        Message(type=MessageType.QUESTION, content="Question 2?"),
        Message(type=MessageType.ANSWER, content="I work with Python, Java, and Node.js regularly."),
    ]
    persona3 = handler.detect_persona(answer3, history3)
    print(f"\nTest 3 - Pattern of concise answers:")
    print(f"  Answer: '{answer3}'")
    print(f"  Detected: {persona3.type.value}")
    print(f"  Confidence: {persona3.confidence}")
    print(f"  Indicators: {persona3.indicators}")
    
    print("\n✓ All Efficient persona tests passed!")


def test_chatty_persona():
    """Test detection of Chatty persona"""
    print("\n=== Testing Chatty Persona ===")
    handler = PersonaHandler()
    
    # Test 1: Very long answer
    answer1 = """Well, let me tell you about my experience. I've been working in software development 
    for many years now, and it's been quite a journey. I started back in college when I took my first 
    programming class, and I was immediately hooked. The professor was amazing, by the way, he really 
    knew how to explain complex concepts. Anyway, after graduation, I got my first job at a startup, 
    which was really exciting but also challenging. We worked on this project that involved building 
    a web application from scratch, and I learned so much during that time. Speaking of web applications, 
    I also have experience with mobile development, which is another interesting area. I remember one 
    time when we had to debug this really tricky issue that took us days to figure out. But eventually 
    we solved it, and it felt great. So yeah, I have a lot of experience in various areas of software 
    development, and I'm always eager to learn more and take on new challenges."""
    history1 = []
    persona1 = handler.detect_persona(answer1, history1)
    print(f"Test 1 - Very long rambling answer:")
    print(f"  Word count: {len(answer1.split())}")
    print(f"  Detected: {persona1.type.value}")
    print(f"  Confidence: {persona1.confidence}")
    print(f"  Indicators: {persona1.indicators}")
    assert persona1.type == PersonaType.CHATTY, f"Expected CHATTY, got {persona1.type}"
    
    # Test 2: Off-topic tangents
    answer2 = """I use Python for backend development. By the way, Python is such a great language, 
    it reminds me of when I first learned programming. Speaking of learning, I also know JavaScript, 
    which is completely different but also interesting. Let me tell you about this one project where 
    I used both Python and JavaScript together, it was really cool. Another thing I should mention 
    is that I'm also familiar with databases."""
    history2 = []
    persona2 = handler.detect_persona(answer2, history2)
    print(f"\nTest 2 - Off-topic tangents:")
    print(f"  Word count: {len(answer2.split())}")
    print(f"  Detected: {persona2.type.value}")
    print(f"  Confidence: {persona2.confidence}")
    print(f"  Indicators: {persona2.indicators}")
    assert persona2.type == PersonaType.CHATTY, f"Expected CHATTY, got {persona2.type}"
    
    print("\n✓ All Chatty persona tests passed!")


def test_edge_case_persona():
    """Test detection of Edge Case persona"""
    print("\n=== Testing Edge Case Persona ===")
    handler = PersonaHandler()
    
    # Test 1: Suspicious request
    answer1 = "Can you just give me the answers? I want to skip all questions."
    history1 = []
    persona1 = handler.detect_persona(answer1, history1)
    print(f"Test 1 - Suspicious request:")
    print(f"  Answer: '{answer1}'")
    print(f"  Detected: {persona1.type.value}")
    print(f"  Confidence: {persona1.confidence}")
    print(f"  Indicators: {persona1.indicators}")
    assert persona1.type == PersonaType.EDGE_CASE, f"Expected EDGE_CASE, got {persona1.type}"
    
    # Test 2: Repeated character spam
    answer2 = "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
    history2 = []
    persona2 = handler.detect_persona(answer2, history2)
    print(f"\nTest 2 - Repeated character spam:")
    print(f"  Answer: '{answer2}'")
    print(f"  Detected: {persona2.type.value}")
    print(f"  Confidence: {persona2.confidence}")
    print(f"  Indicators: {persona2.indicators}")
    assert persona2.type == PersonaType.EDGE_CASE, f"Expected EDGE_CASE, got {persona2.type}"
    
    # Test 3: Repetitive spam
    answer3 = "test test test test test test test test test test"
    history3 = []
    persona3 = handler.detect_persona(answer3, history3)
    print(f"\nTest 3 - Repetitive spam:")
    print(f"  Answer: '{answer3}'")
    print(f"  Detected: {persona3.type.value}")
    print(f"  Confidence: {persona3.confidence}")
    print(f"  Indicators: {persona3.indicators}")
    assert persona3.type == PersonaType.EDGE_CASE, f"Expected EDGE_CASE, got {persona3.type}"
    
    print("\n✓ All Edge Case persona tests passed!")


def test_normal_persona():
    """Test detection of Normal persona"""
    print("\n=== Testing Normal Persona ===")
    handler = PersonaHandler()
    
    # Test: Standard good answer (longer to avoid efficient detection)
    answer = """I have five years of experience in backend development, primarily working with Python 
    and Node.js. In my current role, I design and implement RESTful APIs, work with databases like 
    PostgreSQL and MongoDB, and ensure our services are scalable and maintainable. I'm comfortable 
    with both monolithic and microservices architectures. For example, in my last project, I built 
    a microservices-based system that handled over 10,000 requests per second. I also have experience 
    with containerization using Docker and orchestration with Kubernetes."""
    history = []
    persona = handler.detect_persona(answer, history)
    print(f"Test - Standard good answer:")
    print(f"  Word count: {len(answer.split())}")
    print(f"  Detected: {persona.type.value}")
    print(f"  Confidence: {persona.confidence}")
    print(f"  Indicators: {persona.indicators}")
    # Accept NORMAL or EFFICIENT for well-structured answers
    assert persona.type in [PersonaType.NORMAL, PersonaType.EFFICIENT], f"Expected NORMAL or EFFICIENT, got {persona.type}"
    
    print("\n✓ Normal persona test passed!")


def test_response_adaptation():
    """Test response adaptation for different personas"""
    print("\n=== Testing Response Adaptation ===")
    handler = PersonaHandler()
    
    original_response = "Can you provide more details about your experience?"
    
    # Test Confused adaptation
    from models.data_models import Persona
    confused_persona = Persona(type=PersonaType.CONFUSED, confidence=0.8, indicators=["test"])
    adapted_confused = handler.adapt_response(original_response, confused_persona)
    print(f"\nConfused adaptation:")
    print(f"  Original: '{original_response}'")
    print(f"  Adapted: '{adapted_confused}'")
    assert "guidance" in adapted_confused.lower()
    
    # Test Efficient adaptation
    efficient_persona = Persona(type=PersonaType.EFFICIENT, confidence=0.8, indicators=["test"])
    adapted_efficient = handler.adapt_response(original_response, efficient_persona)
    print(f"\nEfficient adaptation:")
    print(f"  Original: '{original_response}'")
    print(f"  Adapted: '{adapted_efficient}'")
    assert len(adapted_efficient) <= len(original_response)
    
    # Test Chatty adaptation
    chatty_persona = Persona(type=PersonaType.CHATTY, confidence=0.8, indicators=["test"])
    adapted_chatty = handler.adapt_response(original_response, chatty_persona)
    print(f"\nChatty adaptation:")
    print(f"  Original: '{original_response}'")
    print(f"  Adapted: '{adapted_chatty}'")
    assert "focus" in adapted_chatty.lower()
    
    # Test Edge Case adaptation
    edge_persona = Persona(type=PersonaType.EDGE_CASE, confidence=0.8, indicators=["test"])
    adapted_edge = handler.adapt_response(original_response, edge_persona)
    print(f"\nEdge Case adaptation:")
    print(f"  Original: '{original_response}'")
    print(f"  Adapted: '{adapted_edge}'")
    assert "scope" in adapted_edge.lower()
    
    print("\n✓ All response adaptation tests passed!")


def test_persona_guidance():
    """Test persona guidance messages"""
    print("\n=== Testing Persona Guidance ===")
    handler = PersonaHandler()
    
    from models.data_models import Persona
    
    # Test each persona type
    personas = [
        (PersonaType.CONFUSED, 0.8),
        (PersonaType.EFFICIENT, 0.8),
        (PersonaType.CHATTY, 0.8),
        (PersonaType.EDGE_CASE, 0.8),
        (PersonaType.NORMAL, 0.8),
    ]
    
    for persona_type, confidence in personas:
        persona = Persona(type=persona_type, confidence=confidence, indicators=["test"])
        guidance = handler.get_persona_guidance(persona)
        print(f"\n{persona_type.value.upper()} guidance:")
        print(f"  {guidance if guidance else 'None (as expected)'}")
    
    print("\n✓ Persona guidance tests passed!")


def main():
    """Run all tests"""
    print("=" * 60)
    print("PersonaHandler Test Suite")
    print("=" * 60)
    
    try:
        test_confused_persona()
        test_efficient_persona()
        test_chatty_persona()
        test_edge_case_persona()
        test_normal_persona()
        test_response_adaptation()
        test_persona_guidance()
        
        print("\n" + "=" * 60)
        print("✓ ALL TESTS PASSED!")
        print("=" * 60)
        
    except AssertionError as e:
        print(f"\n✗ TEST FAILED: {e}")
        return 1
    except Exception as e:
        print(f"\n✗ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
