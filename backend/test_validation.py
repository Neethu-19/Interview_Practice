"""
Test script to verify input validation and error handling.
"""
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_start_with_invalid_role():
    """Test that invalid role returns 400 with helpful message."""
    response = client.post("/api/start", json={
        "role": "invalid_role",
        "mode": "chat"
    })
    assert response.status_code == 400
    assert "Invalid role" in response.json()["detail"]
    assert "Available roles" in response.json()["detail"]
    print("✓ Invalid role validation works")


def test_start_with_invalid_mode():
    """Test that invalid mode returns 400."""
    response = client.post("/api/start", json={
        "role": "backend_engineer",
        "mode": "invalid_mode"
    })
    assert response.status_code == 400
    assert "Invalid mode" in response.json()["detail"]
    print("✓ Invalid mode validation works")


def test_answer_with_invalid_session_id():
    """Test that invalid session_id format returns 400."""
    response = client.post("/api/answer", json={
        "session_id": "not-a-uuid",
        "answer": "Test answer"
    })
    assert response.status_code == 400
    assert "Invalid session_id format" in response.json()["detail"]
    print("✓ Invalid session_id format validation works")


def test_answer_with_empty_answer():
    """Test that empty answer returns 400."""
    # First create a valid session
    start_response = client.post("/api/start", json={
        "role": "backend_engineer",
        "mode": "chat"
    })
    session_id = start_response.json()["session_id"]
    
    # Try to submit empty answer
    response = client.post("/api/answer", json={
        "session_id": session_id,
        "answer": ""
    })
    assert response.status_code == 400
    assert "cannot be empty" in response.json()["detail"]
    print("✓ Empty answer validation works")


def test_answer_with_too_long_answer():
    """Test that answer over 2000 words returns 400."""
    # First create a valid session
    start_response = client.post("/api/start", json={
        "role": "backend_engineer",
        "mode": "chat"
    })
    session_id = start_response.json()["session_id"]
    
    # Create an answer with over 2000 words
    long_answer = " ".join(["word"] * 2001)
    
    response = client.post("/api/answer", json={
        "session_id": session_id,
        "answer": long_answer
    })
    assert response.status_code == 400
    assert "too long" in response.json()["detail"]
    assert "2000 words" in response.json()["detail"]
    print("✓ Answer length validation works")


def test_answer_with_nonexistent_session():
    """Test that nonexistent session returns 404."""
    response = client.post("/api/answer", json={
        "session_id": "00000000-0000-0000-0000-000000000000",
        "answer": "Test answer"
    })
    assert response.status_code == 404
    assert "not found" in response.json()["detail"]
    print("✓ Nonexistent session validation works")


def test_feedback_with_invalid_session_id():
    """Test that invalid session_id format returns 400."""
    response = client.post("/api/feedback", json={
        "session_id": "not-a-uuid"
    })
    assert response.status_code == 400
    assert "Invalid session_id format" in response.json()["detail"]
    print("✓ Feedback invalid session_id validation works")


def test_history_with_invalid_limit():
    """Test that invalid limit parameter returns 400."""
    response = client.get("/api/history?limit=-1")
    assert response.status_code == 400
    assert "positive integer" in response.json()["detail"]
    print("✓ History negative limit validation works")
    
    response = client.get("/api/history?limit=2000")
    assert response.status_code == 400
    assert "cannot exceed 1000" in response.json()["detail"]
    print("✓ History excessive limit validation works")


def test_transcript_with_invalid_session_id():
    """Test that invalid session_id format returns 400."""
    response = client.get("/api/session/not-a-uuid")
    assert response.status_code == 400
    assert "Invalid session_id format" in response.json()["detail"]
    print("✓ Transcript invalid session_id validation works")


if __name__ == "__main__":
    print("\nRunning validation tests...\n")
    
    try:
        test_start_with_invalid_role()
        test_start_with_invalid_mode()
        test_answer_with_invalid_session_id()
        test_answer_with_empty_answer()
        test_answer_with_too_long_answer()
        test_answer_with_nonexistent_session()
        test_feedback_with_invalid_session_id()
        test_history_with_invalid_limit()
        test_transcript_with_invalid_session_id()
        
        print("\n✅ All validation tests passed!")
    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
        raise
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        raise
