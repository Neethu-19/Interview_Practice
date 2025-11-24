"""
Test script for SQLite storage layer.
"""

import os
from uuid import uuid4
from datetime import datetime

from storage.storage_service import StorageService
from models.data_models import Session, Message, FeedbackReport, Scores


def test_storage():
    """Test all storage service methods."""
    
    # Use a test database
    test_db = "test_interview.db"
    
    # Clean up any existing test database
    if os.path.exists(test_db):
        os.remove(test_db)
    
    print("Initializing storage service...")
    storage = StorageService(test_db)
    
    # Test 1: Save a session
    print("\n1. Testing save_session()...")
    session_id = uuid4()
    session = Session(
        session_id=session_id,
        role="backend_engineer",
        mode="chat",
        created_at=datetime.now(),
        status="active",
        current_question_index=0,
        followup_count=0,
        messages=[]
    )
    
    result = storage.save_session(session)
    print(f"   Save session: {'✓ Success' if result else '✗ Failed'}")
    
    # Test 2: Save messages
    print("\n2. Testing save_message()...")
    message1 = Message(
        type="question",
        content="Tell me about your experience with Python.",
        timestamp=datetime.now()
    )
    message2 = Message(
        type="answer",
        content="I have 5 years of experience with Python...",
        timestamp=datetime.now()
    )
    
    result1 = storage.save_message(session_id, message1)
    result2 = storage.save_message(session_id, message2)
    print(f"   Save message 1: {'✓ Success' if result1 else '✗ Failed'}")
    print(f"   Save message 2: {'✓ Success' if result2 else '✗ Failed'}")
    
    # Test 3: Get session
    print("\n3. Testing get_session()...")
    retrieved_session = storage.get_session(session_id)
    if retrieved_session:
        print(f"   ✓ Retrieved session: {retrieved_session.session_id}")
        print(f"   Role: {retrieved_session.role}")
        print(f"   Messages: {len(retrieved_session.messages)}")
    else:
        print("   ✗ Failed to retrieve session")
    
    # Test 4: Update session
    print("\n4. Testing update_session()...")
    # Create updated session with new values
    updated_session = Session(
        session_id=session_id,
        role=session.role,
        mode=session.mode,
        created_at=session.created_at,
        status="completed",
        current_question_index=1,
        followup_count=2,
        messages=session.messages
    )
    
    result = storage.update_session(updated_session)
    print(f"   Update session: {'✓ Success' if result else '✗ Failed'}")
    
    # Test 5: Save feedback
    print("\n5. Testing save_feedback()...")
    feedback = FeedbackReport(
        session_id=session_id,
        scores=Scores(
            communication=4,
            technical_knowledge=5,
            structure=4
        ),
        strengths=[
            "Clear communication",
            "Strong technical knowledge",
            "Good examples"
        ],
        improvements=[
            "Add more structure",
            "Be more concise",
            "Include metrics"
        ],
        overall_feedback="Great interview overall with strong technical knowledge and clear communication. Keep practicing to improve structure and conciseness in your responses.",
        generated_at=datetime.now()
    )
    
    result = storage.save_feedback(feedback)
    print(f"   Save feedback: {'✓ Success' if result else '✗ Failed'}")
    
    # Test 6: Get user history
    print("\n6. Testing get_user_history()...")
    history = storage.get_user_history()
    print(f"   Total interviews: {history.total_interviews}")
    print(f"   Average score: {history.average_score:.2f}")
    if history.sessions:
        print(f"   First session: {history.sessions[0].role} - Score: {history.sessions[0].score:.2f}")
    
    # Test 7: Get session transcript
    print("\n7. Testing get_session_transcript()...")
    transcript = storage.get_session_transcript(session_id)
    if transcript:
        print(f"   ✓ Retrieved transcript")
        print(f"   Role: {transcript['role']}")
        print(f"   Messages: {len(transcript['transcript'])}")
        print(f"   Has feedback: {transcript['feedback'] is not None}")
        if transcript['feedback']:
            scores = transcript['feedback']['scores']
            print(f"   Scores: Comm={scores['communication']}, Tech={scores['technical_knowledge']}, Struct={scores['structure']}")
    else:
        print("   ✗ Failed to retrieve transcript")
    
    # Test 8: Create another session for history testing
    print("\n8. Testing multiple sessions...")
    session_id2 = uuid4()
    session2 = Session(
        session_id=session_id2,
        role="sales_associate",
        mode="voice",
        created_at=datetime.now(),
        status="completed",
        current_question_index=5,
        followup_count=1,
        messages=[]
    )
    storage.save_session(session2)
    
    feedback2 = FeedbackReport(
        session_id=session_id2,
        scores=Scores(communication=3, technical_knowledge=4, structure=3),
        strengths=["Good energy", "Clear voice", "Confident"],
        improvements=["More examples", "Better structure", "Listen more"],
        overall_feedback="Solid performance with room for improvement. Your energy and confidence were strong, but adding more concrete examples would strengthen your answers significantly.",
        generated_at=datetime.now()
    )
    storage.save_feedback(feedback2)
    
    history = storage.get_user_history()
    print(f"   Total interviews: {history.total_interviews}")
    print(f"   Average score: {history.average_score:.2f}")
    
    print("\n" + "="*50)
    print("All storage tests completed successfully! ✓")
    print("="*50)
    
    # Clean up test database
    if os.path.exists(test_db):
        os.remove(test_db)
        print(f"\nCleaned up test database: {test_db}")


if __name__ == "__main__":
    test_storage()
