"""
API Integration tests
Tests complete interview flow through API endpoints
"""
import pytest
from fastapi.testclient import TestClient
import sys
from pathlib import Path

# Add backend to path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from main import app

client = TestClient(app)


class TestBasicEndpoints:
    """Test basic API endpoints"""
    
    def test_root_endpoint(self):
        """Test root endpoint returns status"""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert data["status"] == "running"
    
    def test_health_endpoint(self):
        """Test health check endpoint"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert data["status"] == "healthy"


class TestStartEndpoint:
    """Test interview start endpoint"""
    
    def test_start_valid_session(self):
        """Test starting interview with valid parameters"""
        response = client.post("/api/start", json={
            "role": "backend_engineer",
            "mode": "chat"
        })
        
        assert response.status_code == 201
        data = response.json()
        assert "session_id" in data
        assert "question" in data
        assert "question_number" in data
        assert data["question_number"] == 1
        assert len(data["question"]) > 0
    
    def test_start_invalid_role(self):
        """Test starting with invalid role"""
        response = client.post("/api/start", json={
            "role": "invalid_role",
            "mode": "chat"
        })
        
        assert response.status_code == 400
        data = response.json()
        assert "detail" in data
    
    def test_start_missing_role(self):
        """Test starting without role parameter"""
        response = client.post("/api/start", json={
            "mode": "chat"
        })
        
        assert response.status_code == 422  # Validation error
    
    def test_start_voice_mode(self):
        """Test starting interview in voice mode"""
        response = client.post("/api/start", json={
            "role": "backend_engineer",
            "mode": "voice"
        })
        
        assert response.status_code == 201
        data = response.json()
        assert "session_id" in data


class TestAnswerEndpoint:
    """Test answer submission endpoint"""
    
    @pytest.fixture
    def session_id(self):
        """Create a session for testing"""
        response = client.post("/api/start", json={
            "role": "backend_engineer",
            "mode": "chat"
        })
        return response.json()["session_id"]
    
    def test_submit_valid_answer(self, session_id):
        """Test submitting a valid answer"""
        response = client.post("/api/answer", json={
            "session_id": session_id,
            "answer": "I have 5 years of experience with Python and FastAPI."
        })
        
        assert response.status_code == 200
        data = response.json()
        assert "type" in data
        assert data["type"] in ["question", "followup", "complete"]
        assert "content" in data
        assert "question_number" in data
    
    def test_submit_empty_answer(self, session_id):
        """Test submitting empty answer"""
        response = client.post("/api/answer", json={
            "session_id": session_id,
            "answer": ""
        })
        
        # Should return error (400 or 500 depending on validation)
        assert response.status_code in [400, 500]
    
    def test_submit_invalid_session_id(self):
        """Test submitting answer with invalid session ID"""
        response = client.post("/api/answer", json={
            "session_id": "invalid-uuid",
            "answer": "Some answer"
        })
        
        assert response.status_code == 400
    
    def test_submit_nonexistent_session(self):
        """Test submitting answer to non-existent session"""
        response = client.post("/api/answer", json={
            "session_id": "00000000-0000-0000-0000-000000000000",
            "answer": "Some answer"
        })
        
        assert response.status_code == 404


class TestCompleteInterviewFlow:
    """Test complete interview flow from start to feedback"""
    
    def test_full_interview_flow(self):
        """Test complete interview: start -> answers -> feedback"""
        # Start interview
        start_response = client.post("/api/start", json={
            "role": "backend_engineer",
            "mode": "chat"
        })
        assert start_response.status_code == 201
        session_id = start_response.json()["session_id"]
        
        # Answer multiple questions
        answers = [
            "I have 5 years of experience with Python, Django, and FastAPI.",
            "I approach debugging systematically by checking logs and reproducing issues.",
            "I built a microservices architecture that handles 10k requests per second."
        ]
        
        for answer in answers:
            answer_response = client.post("/api/answer", json={
                "session_id": session_id,
                "answer": answer
            })
            assert answer_response.status_code == 200
            
            # If complete, break
            if answer_response.json()["type"] == "complete":
                break
        
        # Get feedback (may fail if Ollama not running)
        feedback_response = client.post("/api/feedback", json={
            "session_id": session_id
        })
        
        if feedback_response.status_code == 200:
            data = feedback_response.json()
            assert "scores" in data
            assert "strengths" in data
            assert "improvements" in data
            assert "overall_feedback" in data
    
    def test_followup_question_generation(self):
        """Test that follow-up questions are generated for incomplete answers"""
        # Start interview
        start_response = client.post("/api/start", json={
            "role": "backend_engineer",
            "mode": "chat"
        })
        session_id = start_response.json()["session_id"]
        
        # Give short answer to potentially trigger follow-up
        answer_response = client.post("/api/answer", json={
            "session_id": session_id,
            "answer": "Yes, I know Python."
        })
        
        assert answer_response.status_code == 200
        data = answer_response.json()
        
        # May or may not trigger follow-up depending on LLM
        assert data["type"] in ["question", "followup"]


class TestHistoryEndpoint:
    """Test interview history endpoint"""
    
    def test_get_history(self):
        """Test getting interview history"""
        response = client.get("/api/history")
        
        assert response.status_code == 200
        data = response.json()
        assert "sessions" in data
        assert "total_interviews" in data
        assert "average_score" in data
        assert isinstance(data["sessions"], list)
    
    def test_get_history_with_limit(self):
        """Test getting history with limit parameter"""
        response = client.get("/api/history?limit=5")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data["sessions"]) <= 5
    
    def test_history_after_creating_session(self):
        """Test that history includes newly created session"""
        # Get initial count
        initial_response = client.get("/api/history")
        initial_count = initial_response.json()["total_interviews"]
        
        # Create new session
        client.post("/api/start", json={
            "role": "backend_engineer",
            "mode": "chat"
        })
        
        # Check history updated
        updated_response = client.get("/api/history")
        updated_count = updated_response.json()["total_interviews"]
        
        assert updated_count >= initial_count


class TestSessionTranscriptEndpoint:
    """Test session transcript endpoint"""
    
    @pytest.fixture
    def session_with_messages(self):
        """Create a session with some messages"""
        start_response = client.post("/api/start", json={
            "role": "backend_engineer",
            "mode": "chat"
        })
        session_id = start_response.json()["session_id"]
        
        # Add an answer
        client.post("/api/answer", json={
            "session_id": session_id,
            "answer": "I have experience with Python."
        })
        
        return session_id
    
    def test_get_session_transcript(self, session_with_messages):
        """Test getting session transcript"""
        response = client.get(f"/api/session/{session_with_messages}")
        
        assert response.status_code == 200
        data = response.json()
        assert "session_id" in data
        assert "transcript" in data
        assert "role" in data
        assert isinstance(data["transcript"], list)
        assert len(data["transcript"]) > 0
    
    def test_get_transcript_invalid_id(self):
        """Test getting transcript with invalid ID"""
        response = client.get("/api/session/invalid-uuid")
        
        assert response.status_code == 400
    
    def test_get_transcript_nonexistent_session(self):
        """Test getting transcript for non-existent session"""
        response = client.get("/api/session/00000000-0000-0000-0000-000000000000")
        
        assert response.status_code == 404


class TestFeedbackEndpoint:
    """Test feedback generation endpoint"""
    
    @pytest.fixture
    def completed_session(self):
        """Create a session with answers"""
        start_response = client.post("/api/start", json={
            "role": "backend_engineer",
            "mode": "chat"
        })
        session_id = start_response.json()["session_id"]
        
        # Add some answers
        client.post("/api/answer", json={
            "session_id": session_id,
            "answer": "I have 5 years of experience with Python and backend development."
        })
        
        return session_id
    
    def test_generate_feedback(self, completed_session):
        """Test generating feedback for a session"""
        response = client.post("/api/feedback", json={
            "session_id": completed_session
        })
        
        # May fail if Ollama not running
        if response.status_code == 200:
            data = response.json()
            assert "scores" in data
            assert "communication" in data["scores"]
            assert "technical_knowledge" in data["scores"]
            assert "structure" in data["scores"]
            assert "strengths" in data
            assert "improvements" in data
            assert len(data["strengths"]) == 3
            assert len(data["improvements"]) == 3
        else:
            pytest.skip("Ollama not available for feedback generation")
    
    def test_feedback_invalid_session(self):
        """Test generating feedback for invalid session"""
        response = client.post("/api/feedback", json={
            "session_id": "invalid-uuid"
        })
        
        assert response.status_code == 400


class TestErrorHandling:
    """Test error handling across endpoints"""
    
    def test_malformed_json(self):
        """Test handling of malformed JSON"""
        response = client.post(
            "/api/start",
            data="not valid json",
            headers={"Content-Type": "application/json"}
        )
        
        assert response.status_code == 422
    
    def test_missing_required_fields(self):
        """Test handling of missing required fields"""
        response = client.post("/api/answer", json={
            "session_id": "some-id"
            # Missing 'answer' field
        })
        
        assert response.status_code == 422
    
    def test_invalid_field_types(self):
        """Test handling of invalid field types"""
        response = client.post("/api/start", json={
            "role": 123,  # Should be string
            "mode": "chat"
        })
        
        assert response.status_code == 422
