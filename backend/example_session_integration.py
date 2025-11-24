"""
Example Integration: InterviewSessionManager

Demonstrates complete interview session workflow:
1. Create session
2. Answer questions
3. Handle follow-ups
4. Complete session
"""

import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

from services.interview_session_manager import InterviewSessionManager
from services.ollama_client import OllamaClient


def print_separator():
    print("\n" + "=" * 70 + "\n")


def simulate_interview():
    """Simulate a complete interview session"""
    
    print_separator()
    print("INTERVIEW PRACTICE PARTNER - Session Demo")
    print_separator()
    
    # Check Ollama availability
    print("Checking Ollama server...")
    client = OllamaClient()
    if client.check_health():
        print("✓ Ollama server is available")
    else:
        print("⚠ Ollama server not available - using fallback behavior")
    
    # Initialize manager
    manager = InterviewSessionManager()
    
    # Step 1: Create session
    print_separator()
    print("STEP 1: Creating Interview Session")
    print_separator()
    
    session, first_question = manager.create_session(
        role="backend_engineer",
        mode="chat"
    )
    
    print(f"Session ID: {session.session_id}")
    print(f"Role: {session.role}")
    print(f"Mode: {session.mode.value}")
    print(f"\nFirst Question:\n{first_question}")
    
    # Step 2: Answer first question (complete answer)
    print_separator()
    print("STEP 2: Answering First Question (Complete Answer)")
    print_separator()
    
    answer1 = """I have 5 years of experience in backend development, primarily working with Python.
    I've built RESTful APIs using FastAPI and Django, implemented microservices architectures,
    and worked extensively with PostgreSQL and MongoDB databases. In my current role at TechCorp,
    I lead a team of 3 developers building scalable backend systems that handle over 1 million
    requests per day. I'm particularly passionate about API design, performance optimization,
    and implementing robust testing strategies."""
    
    print(f"Your Answer:\n{answer1}\n")
    
    response1 = manager.process_answer(
        session_id=session.session_id,
        answer=answer1
    )
    
    print(f"Response Type: {response1['type']}")
    print(f"Persona Detected: {response1['persona'].type.value}")
    print(f"Confidence: {response1['persona'].confidence}")
    print(f"\nNext Question:\n{response1['content']}")
    
    # Step 3: Answer second question (short answer to trigger follow-up)
    print_separator()
    print("STEP 3: Answering Second Question (Short Answer)")
    print_separator()
    
    answer2 = "SQL is relational, NoSQL is not."
    
    print(f"Your Answer:\n{answer2}\n")
    
    response2 = manager.process_answer(
        session_id=session.session_id,
        answer=answer2
    )
    
    print(f"Response Type: {response2['type']}")
    print(f"Persona Detected: {response2['persona'].type.value}")
    
    if response2['type'] == 'followup':
        print(f"\nFollow-up Question:\n{response2['content']}")
        
        # Step 4: Answer follow-up
        print_separator()
        print("STEP 4: Answering Follow-up Question")
        print_separator()
        
        answer3 = """SQL databases use structured schemas with tables and relationships,
        ensuring ACID compliance. They're great for complex queries and transactions.
        NoSQL databases are more flexible, schema-less, and horizontally scalable.
        They're better for handling large volumes of unstructured data and high-velocity writes."""
        
        print(f"Your Answer:\n{answer3}\n")
        
        response3 = manager.process_answer(
            session_id=session.session_id,
            answer=answer3
        )
        
        print(f"Response Type: {response3['type']}")
        print(f"\nNext Question:\n{response3['content']}")
    else:
        print(f"\nNo follow-up needed. Moving to next question:\n{response2['content']}")
    
    # Step 5: Check session progress
    print_separator()
    print("STEP 5: Checking Session Progress")
    print_separator()
    
    progress = manager.get_session_progress(session.session_id)
    
    print(f"Current Question: {progress['current_question']} of {progress['total_questions']}")
    print(f"Progress: {progress['progress_percentage']}%")
    print(f"Follow-up Count: {progress['followup_count']}")
    print(f"Status: {progress['status']}")
    
    # Step 6: View transcript
    print_separator()
    print("STEP 6: Session Transcript")
    print_separator()
    
    transcript = manager.get_session_transcript(session.session_id)
    
    print(f"Total Messages: {len(transcript)}\n")
    
    for i, msg in enumerate(transcript, 1):
        msg_type = msg['type'].upper()
        content = msg['content'][:100] + "..." if len(msg['content']) > 100 else msg['content']
        print(f"{i}. [{msg_type}]")
        print(f"   {content}\n")
    
    # Step 7: End session
    print_separator()
    print("STEP 7: Ending Session")
    print_separator()
    
    completed_session = manager.end_session(session.session_id)
    
    print(f"Session Status: {completed_session.status.value}")
    print(f"Total Messages: {len(completed_session.messages)}")
    print(f"Questions Answered: {completed_session.current_question_index}")
    
    print_separator()
    print("✓ Interview Session Demo Complete!")
    print_separator()
    
    return session.session_id


def demonstrate_persona_detection():
    """Demonstrate different persona detections"""
    
    print_separator()
    print("PERSONA DETECTION DEMO")
    print_separator()
    
    manager = InterviewSessionManager()
    
    # Test different personas
    personas_to_test = [
        {
            "name": "Confused User",
            "answer": "I don't know. What do you mean?",
            "expected": "confused"
        },
        {
            "name": "Efficient User",
            "answer": "Python, Java, JavaScript. 5 years experience. Next question.",
            "expected": "efficient"
        },
        {
            "name": "Chatty User",
            "answer": """Well, let me tell you about my entire career journey. It all started
            when I was in college, and by the way, I had this amazing professor who taught me
            programming. Speaking of which, I remember this one time when I was working on a project
            and something really interesting happened. On another note, I also learned about databases
            which reminds me of this other experience I had...""" * 3,
            "expected": "chatty"
        }
    ]
    
    for test in personas_to_test:
        session, _ = manager.create_session(role="backend_engineer", mode="chat")
        
        print(f"\nTesting: {test['name']}")
        print(f"Answer: {test['answer'][:80]}...")
        
        response = manager.process_answer(
            session_id=session.session_id,
            answer=test['answer']
        )
        
        persona = response['persona']
        print(f"Detected: {persona.type.value} (confidence: {persona.confidence})")
        print(f"Indicators: {', '.join(persona.indicators[:3])}")
        
        if persona.type.value == test['expected']:
            print("✓ Correct detection")
        else:
            print(f"  Note: Expected {test['expected']}, got {persona.type.value}")
    
    print_separator()


def main():
    """Run demonstrations"""
    
    try:
        # Run main interview simulation
        simulate_interview()
        
        # Demonstrate persona detection
        demonstrate_persona_detection()
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
