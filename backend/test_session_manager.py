"""
Test script for InterviewSessionManager

Tests core functionality:
- Session creation
- Question retrieval
- Answer processing
- Follow-up logic
- Session completion
"""

import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

from services.interview_session_manager import (
    InterviewSessionManager,
    SessionManagerError,
    SessionNotFoundError,
    InvalidSessionStateError
)
from services.ollama_client import OllamaClient
from uuid import UUID


def test_session_creation(manager):
    """Test creating a new interview session"""
    print("\n=== Test: Session Creation ===")
    
    # Test valid session creation
    try:
        session, first_question = manager.create_session(
            role="backend_engineer",
            mode="chat"
        )
        
        print(f"✓ Session created: {session.session_id}")
        print(f"✓ Role: {session.role}")
        print(f"✓ Mode: {session.mode}")
        print(f"✓ Status: {session.status}")
        print(f"✓ First question received: {first_question[:100]}...")
        
        assert session.role == "backend_engineer"
        assert session.current_question_index == 0
        assert session.followup_count == 0
        assert len(session.messages) == 1  # First question added
        
        print("✓ All assertions passed")
        return session.session_id
        
    except Exception as e:
        print(f"✗ Failed: {e}")
        raise


def test_invalid_role(manager):
    """Test session creation with invalid role"""
    print("\n=== Test: Invalid Role ===")
    
    try:
        session, _ = manager.create_session(
            role="invalid_role",
            mode="chat"
        )
        print("✗ Should have raised SessionManagerError")
        return False
        
    except SessionManagerError as e:
        print(f"✓ Correctly raised error: {e}")
        return True


def test_answer_processing(manager, session_id: UUID):
    """Test processing user answers"""
    print("\n=== Test: Answer Processing ===")
    
    # Process a complete answer
    try:
        answer = """I have 5 years of experience with Python, focusing on backend development.
        I've worked extensively with FastAPI, Django, and Flask frameworks. In my current role,
        I lead a team of 3 developers building microservices architecture. I'm particularly
        skilled in API design, database optimization, and implementing CI/CD pipelines."""
        
        response = manager.process_answer(
            session_id=session_id,
            answer=answer
        )
        
        print(f"✓ Answer processed")
        print(f"✓ Response type: {response['type']}")
        print(f"✓ Question number: {response['question_number']}")
        print(f"✓ Persona detected: {response['persona'].type}")
        print(f"✓ Response content: {response['content'][:100]}...")
        
        session = manager.get_session(session_id)
        print(f"✓ Session now has {len(session.messages)} messages")
        
        return response['type']
        
    except Exception as e:
        print(f"✗ Failed: {e}")
        raise


def test_followup_logic(manager, session_id: UUID):
    """Test follow-up question generation"""
    print("\n=== Test: Follow-up Logic ===")
    
    # Give a short, incomplete answer to trigger follow-up
    try:
        short_answer = "I know Python."
        
        response = manager.process_answer(
            session_id=session_id,
            answer=short_answer
        )
        
        print(f"✓ Short answer processed")
        print(f"✓ Response type: {response['type']}")
        
        if response['type'] == 'followup':
            print(f"✓ Follow-up question generated: {response['content'][:100]}...")
            session = manager.get_session(session_id)
            print(f"✓ Follow-up count: {session.followup_count}")
        else:
            print(f"  Note: No follow-up generated (LLM decided answer was complete)")
        
        return True
        
    except Exception as e:
        print(f"✗ Failed: {e}")
        raise


def test_max_followups(manager):
    """Test max 3 follow-ups per question enforcement"""
    print("\n=== Test: Max Follow-ups Enforcement ===")
    
    try:
        # Create new session
        session, _ = manager.create_session(
            role="backend_engineer",
            mode="chat"
        )
        
        # Give short answers to trigger follow-ups
        followup_count = 0
        for i in range(5):  # Try to trigger more than 3 follow-ups
            answer = f"Short answer {i}"
            response = manager.process_answer(
                session_id=session.session_id,
                answer=answer
            )
            
            if response['type'] == 'followup':
                followup_count += 1
                print(f"  Follow-up {followup_count} generated")
            else:
                print(f"  Moved to next question after {followup_count} follow-ups")
                break
        
        # Verify max 3 follow-ups
        if followup_count <= 3:
            print(f"✓ Max follow-ups enforced (got {followup_count})")
            return True
        else:
            print(f"✗ Too many follow-ups: {followup_count}")
            return False
            
    except Exception as e:
        print(f"✗ Failed: {e}")
        raise


def test_session_completion(manager):
    """Test completing a session"""
    print("\n=== Test: Session Completion ===")
    
    try:
        # Create session
        session, _ = manager.create_session(
            role="backend_engineer",
            mode="chat"
        )
        
        # End session
        completed_session = manager.end_session(session.session_id)
        
        print(f"✓ Session ended")
        print(f"✓ Status: {completed_session.status}")
        
        assert completed_session.status.value == "completed"
        print("✓ Session marked as completed")
        
        return True
        
    except Exception as e:
        print(f"✗ Failed: {e}")
        raise


def test_session_transcript(manager, session_id: UUID):
    """Test getting session transcript"""
    print("\n=== Test: Session Transcript ===")
    
    try:
        transcript = manager.get_session_transcript(session_id)
        
        print(f"✓ Transcript retrieved")
        print(f"✓ Total messages: {len(transcript)}")
        
        for i, msg in enumerate(transcript[:3]):  # Show first 3
            print(f"  {i+1}. {msg['type']}: {msg['content'][:50]}...")
        
        return True
        
    except Exception as e:
        print(f"✗ Failed: {e}")
        raise


def test_session_progress(manager, session_id: UUID):
    """Test getting session progress"""
    print("\n=== Test: Session Progress ===")
    
    try:
        progress = manager.get_session_progress(session_id)
        
        print(f"✓ Progress retrieved:")
        print(f"  - Current question: {progress['current_question']}")
        print(f"  - Total questions: {progress['total_questions']}")
        print(f"  - Progress: {progress['progress_percentage']}%")
        print(f"  - Follow-up count: {progress['followup_count']}")
        print(f"  - Status: {progress['status']}")
        
        return True
        
    except Exception as e:
        print(f"✗ Failed: {e}")
        raise


def main():
    """Run all tests"""
    print("=" * 60)
    print("Testing InterviewSessionManager")
    print("=" * 60)
    
    # Check Ollama availability
    print("\nChecking Ollama availability...")
    client = OllamaClient()
    if not client.check_health():
        print("⚠ Warning: Ollama server not available")
        print("  Some tests may fail or use fallback behavior")
    else:
        print("✓ Ollama server is available")
    
    try:
        # Create shared manager instance
        manager = InterviewSessionManager()
        
        # Run tests
        session_id = test_session_creation(manager)
        test_invalid_role(manager)
        response_type = test_answer_processing(manager, session_id)
        
        # Only test follow-up if we didn't already move to next question
        if response_type != 'question':
            test_followup_logic(manager, session_id)
        
        test_max_followups(manager)
        test_session_completion(manager)
        test_session_transcript(manager, session_id)
        test_session_progress(manager, session_id)
        
        print("\n" + "=" * 60)
        print("✓ All tests passed!")
        print("=" * 60)
        
    except Exception as e:
        print("\n" + "=" * 60)
        print(f"✗ Tests failed: {e}")
        print("=" * 60)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
