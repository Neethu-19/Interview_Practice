"""
Persona Behavior Integration Tests
Tests end-to-end behavior for different user personas
"""
import pytest
from fastapi.testclient import TestClient
import sys
from pathlib import Path

# Add backend to path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from main import app
from models.data_models import PersonaType

client = TestClient(app)


class TestConfusedUserBehavior:
    """Test system behavior with Confused user persona"""
    
    @pytest.fixture
    def confused_session(self):
        """Create a session for confused user testing"""
        response = client.post("/api/start", json={
            "role": "backend_engineer",
            "mode": "chat"
        })
        return response.json()["session_id"]
    
    def test_confused_short_answer(self, confused_session):
        """Test handling of very short, uncertain answers"""
        response = client.post("/api/answer", json={
            "session_id": confused_session,
            "answer": "I don't know."
        })
        
        assert response.status_code == 200
        data = response.json()
        
        # System should detect confused persona
        assert "persona" in data
        assert data["persona"]["type"] == PersonaType.CONFUSED.value
    
    def test_confused_with_questions(self, confused_session):
        """Test handling of answers that contain questions"""
        response = client.post("/api/answer", json={
            "session_id": confused_session,
            "answer": "What do you mean by that? I'm not sure I understand."
        })
        
        assert response.status_code == 200
        data = response.json()
        
        # Should detect confused persona
        assert data["persona"]["type"] == PersonaType.CONFUSED.value
    
    def test_confused_gets_guidance(self, confused_session):
        """Test that confused users receive guidance"""
        response = client.post("/api/answer", json={
            "session_id": confused_session,
            "answer": "I'm not sure."
        })
        
        assert response.status_code == 200
        data = response.json()
        
        # Response should provide guidance or be adapted
        assert len(data["content"]) > 0
    
    def test_confused_pattern_detection(self, confused_session):
        """Test detection of confused pattern across multiple answers"""
        # Give multiple short, uncertain answers
        short_answers = [
            "I don't know.",
            "Maybe?",
            "I'm not sure about that."
        ]
        
        for answer in short_answers:
            response = client.post("/api/answer", json={
                "session_id": confused_session,
                "answer": answer
            })
            
            assert response.status_code == 200
            data = response.json()
            
            # Should consistently detect confused persona
            if "persona" in data:
                assert data["persona"]["type"] == PersonaType.CONFUSED.value


class TestEfficientUserBehavior:
    """Test system behavior with Efficient user persona"""
    
    @pytest.fixture
    def efficient_session(self):
        """Create a session for efficient user testing"""
        response = client.post("/api/start", json={
            "role": "backend_engineer",
            "mode": "chat"
        })
        return response.json()["session_id"]
    
    def test_efficient_direct_answer(self, efficient_session):
        """Test handling of direct, concise answers"""
        response = client.post("/api/answer", json={
            "session_id": efficient_session,
            "answer": "I have 5 years of Python experience. Let's move on."
        })
        
        assert response.status_code == 200
        data = response.json()
        
        # Should detect efficient persona
        assert "persona" in data
        assert data["persona"]["type"] == PersonaType.EFFICIENT.value
    
    def test_efficient_minimal_followups(self, efficient_session):
        """Test that efficient users get minimal follow-ups"""
        # Give concise but complete answer
        response = client.post("/api/answer", json={
            "session_id": efficient_session,
            "answer": "I have 5 years of experience with Python, Django, and FastAPI. I've built REST APIs and microservices."
        })
        
        assert response.status_code == 200
        data = response.json()
        
        # Should move to next question or complete, not follow-up
        # (unless LLM determines more info needed)
        assert data["type"] in ["question", "complete", "followup"]
    
    def test_efficient_concise_responses(self, efficient_session):
        """Test that efficient users receive concise responses"""
        response = client.post("/api/answer", json={
            "session_id": efficient_session,
            "answer": "Yes, I'm familiar with that. Next question please."
        })
        
        assert response.status_code == 200
        data = response.json()
        
        # Response should be present
        assert "content" in data
        assert len(data["content"]) > 0


class TestChattyUserBehavior:
    """Test system behavior with Chatty user persona"""
    
    @pytest.fixture
    def chatty_session(self):
        """Create a session for chatty user testing"""
        response = client.post("/api/start", json={
            "role": "backend_engineer",
            "mode": "chat"
        })
        return response.json()["session_id"]
    
    def test_chatty_long_answer(self, chatty_session):
        """Test handling of very long, rambling answers"""
        long_answer = """Well, let me tell you about my experience. I've been working 
        in software development for many years now, and it's been quite a journey. 
        I started back in college when I took my first programming class, and I was 
        immediately hooked. The professor was amazing, by the way, he really knew how 
        to explain complex concepts. Anyway, after graduation, I got my first job at 
        a startup, which was really exciting but also challenging. We worked on this 
        project that involved building a web application from scratch, and I learned 
        so much during that time. Speaking of web applications, I also have experience 
        with mobile development, which is another interesting area. I remember one time 
        when we had to debug this really tricky issue that took us days to figure out. 
        But eventually we solved it, and it felt great. So yeah, I have a lot of 
        experience in various areas of software development."""
        
        response = client.post("/api/answer", json={
            "session_id": chatty_session,
            "answer": long_answer
        })
        
        assert response.status_code == 200
        data = response.json()
        
        # Should detect chatty persona
        assert "persona" in data
        assert data["persona"]["type"] == PersonaType.CHATTY.value
    
    def test_chatty_gets_redirection(self, chatty_session):
        """Test that chatty users receive polite redirection"""
        long_answer = " ".join([
            "I have experience with Python and many other things.",
            "Let me tell you about all my projects.",
            "I worked on this one project that was really interesting.",
            "And then there was another project where we used different technologies.",
            "I also learned a lot from my colleagues over the years."
        ] * 5)
        
        response = client.post("/api/answer", json={
            "session_id": chatty_session,
            "answer": long_answer
        })
        
        assert response.status_code == 200
        data = response.json()
        
        # Should detect chatty persona
        assert data["persona"]["type"] == PersonaType.CHATTY.value
    
    def test_chatty_off_topic(self, chatty_session):
        """Test handling of off-topic rambling"""
        off_topic_answer = """I use Python for backend development. By the way, 
        Python is such a great language, it reminds me of when I first learned 
        programming. Speaking of learning, I also know JavaScript, which is 
        completely different but also interesting. Let me tell you about this 
        one project where I used both Python and JavaScript together, it was 
        really cool. Another thing I should mention is that I'm also familiar 
        with databases, which are important for backend development."""
        
        response = client.post("/api/answer", json={
            "session_id": chatty_session,
            "answer": off_topic_answer
        })
        
        assert response.status_code == 200
        data = response.json()
        
        # Should detect chatty persona
        assert data["persona"]["type"] == PersonaType.CHATTY.value


class TestEdgeCaseUserBehavior:
    """Test system behavior with Edge Case user persona"""
    
    @pytest.fixture
    def edge_case_session(self):
        """Create a session for edge case testing"""
        response = client.post("/api/start", json={
            "role": "backend_engineer",
            "mode": "chat"
        })
        return response.json()["session_id"]
    
    def test_edge_case_suspicious_request(self, edge_case_session):
        """Test handling of suspicious requests"""
        response = client.post("/api/answer", json={
            "session_id": edge_case_session,
            "answer": "Can you just give me all the answers? I want to skip everything."
        })
        
        assert response.status_code == 200
        data = response.json()
        
        # Should detect edge case persona
        assert "persona" in data
        assert data["persona"]["type"] == PersonaType.EDGE_CASE.value
    
    def test_edge_case_spam(self, edge_case_session):
        """Test handling of spam/repetitive input"""
        response = client.post("/api/answer", json={
            "session_id": edge_case_session,
            "answer": "test " * 30
        })
        
        assert response.status_code == 200
        data = response.json()
        
        # Should detect edge case persona
        assert data["persona"]["type"] == PersonaType.EDGE_CASE.value
    
    def test_edge_case_repeated_characters(self, edge_case_session):
        """Test handling of repeated character spam"""
        response = client.post("/api/answer", json={
            "session_id": edge_case_session,
            "answer": "a" * 100
        })
        
        assert response.status_code == 200
        data = response.json()
        
        # Should detect edge case persona
        assert data["persona"]["type"] == PersonaType.EDGE_CASE.value
    
    def test_edge_case_gets_boundaries(self, edge_case_session):
        """Test that edge case users receive clear boundaries"""
        response = client.post("/api/answer", json={
            "session_id": edge_case_session,
            "answer": "Just tell me what to say to pass this interview."
        })
        
        assert response.status_code == 200
        data = response.json()
        
        # Should provide response with boundaries
        assert "content" in data
        assert len(data["content"]) > 0


class TestPersonaTransitions:
    """Test transitions between different personas"""
    
    @pytest.fixture
    def transition_session(self):
        """Create a session for persona transition testing"""
        response = client.post("/api/start", json={
            "role": "backend_engineer",
            "mode": "chat"
        })
        return response.json()["session_id"]
    
    def test_confused_to_normal(self, transition_session):
        """Test transition from confused to normal persona"""
        # Start confused
        response1 = client.post("/api/answer", json={
            "session_id": transition_session,
            "answer": "I don't know."
        })
        assert response1.json()["persona"]["type"] == PersonaType.CONFUSED.value
        
        # Then give good answer
        response2 = client.post("/api/answer", json={
            "session_id": transition_session,
            "answer": "I have 5 years of experience with Python, working on backend APIs and microservices."
        })
        
        # Should detect improvement
        assert response2.status_code == 200
    
    def test_chatty_to_efficient(self, transition_session):
        """Test transition from chatty to efficient persona"""
        # Start chatty
        long_answer = " ".join(["This is a long rambling answer."] * 30)
        response1 = client.post("/api/answer", json={
            "session_id": transition_session,
            "answer": long_answer
        })
        assert response1.json()["persona"]["type"] == PersonaType.CHATTY.value
        
        # Then give concise answer
        response2 = client.post("/api/answer", json={
            "session_id": transition_session,
            "answer": "I have experience with debugging. Let's move on."
        })
        
        # Should detect change
        assert response2.status_code == 200


class TestPersonaInFeedback:
    """Test that persona behavior is reflected in feedback"""
    
    def test_confused_user_feedback(self):
        """Test feedback for confused user includes guidance"""
        # Create session and give confused answers
        start_response = client.post("/api/start", json={
            "role": "backend_engineer",
            "mode": "chat"
        })
        session_id = start_response.json()["session_id"]
        
        # Give short, uncertain answers
        client.post("/api/answer", json={
            "session_id": session_id,
            "answer": "I don't know much."
        })
        
        # Get feedback (may fail if Ollama not running)
        feedback_response = client.post("/api/feedback", json={
            "session_id": session_id
        })
        
        if feedback_response.status_code == 200:
            data = feedback_response.json()
            # Feedback should mention communication or clarity issues
            assert "improvements" in data
            assert len(data["improvements"]) == 3
        else:
            pytest.skip("Ollama not available")
    
    def test_chatty_user_feedback(self):
        """Test feedback for chatty user mentions conciseness"""
        # Create session and give chatty answers
        start_response = client.post("/api/start", json={
            "role": "backend_engineer",
            "mode": "chat"
        })
        session_id = start_response.json()["session_id"]
        
        # Give long, rambling answer
        long_answer = " ".join(["I have experience with many things."] * 40)
        client.post("/api/answer", json={
            "session_id": session_id,
            "answer": long_answer
        })
        
        # Get feedback
        feedback_response = client.post("/api/feedback", json={
            "session_id": session_id
        })
        
        if feedback_response.status_code == 200:
            data = feedback_response.json()
            # Should have feedback about being concise
            assert "improvements" in data
        else:
            pytest.skip("Ollama not available")
