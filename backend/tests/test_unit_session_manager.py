"""
Unit tests for InterviewSessionManager
Tests session state transitions and management
"""
import pytest
from uuid import UUID
from services.interview_session_manager import (
    SessionManagerError,
    SessionNotFoundError,
    InvalidSessionStateError
)
from models.data_models import SessionStatus


class TestSessionCreation:
    """Test session creation logic"""
    
    def test_create_valid_session(self, session_manager):
        """Test creating a session with valid role"""
        session, first_question = session_manager.create_session(
            role="backend_engineer",
            mode="chat"
        )
        
        assert session.role == "backend_engineer"
        assert session.mode == "chat"
        assert session.status == SessionStatus.ACTIVE
        assert session.current_question_index == 0
        assert session.followup_count == 0
        assert len(first_question) > 0
    
    def test_create_session_invalid_role(self, session_manager):
        """Test creating session with invalid role raises error"""
        with pytest.raises(SessionManagerError):
            session_manager.create_session(
                role="invalid_role",
                mode="chat"
            )
    
    def test_session_id_is_uuid(self, session_manager):
        """Test that session ID is a valid UUID"""
        session, _ = session_manager.create_session(
            role="backend_engineer",
            mode="chat"
        )
        
        assert isinstance(session.session_id, UUID)
    
    def test_first_message_added(self, session_manager):
        """Test that first question is added to messages"""
        session, _ = session_manager.create_session(
            role="backend_engineer",
            mode="chat"
        )
        
        assert len(session.messages) == 1
        assert session.messages[0].type.value == "question"


class TestSessionRetrieval:
    """Test session retrieval"""
    
    def test_get_existing_session(self, session_manager):
        """Test retrieving an existing session"""
        session, _ = session_manager.create_session(
            role="backend_engineer",
            mode="chat"
        )
        
        retrieved = session_manager.get_session(session.session_id)
        assert retrieved.session_id == session.session_id
    
    def test_get_nonexistent_session(self, session_manager):
        """Test retrieving non-existent session raises error"""
        from uuid import uuid4
        fake_id = uuid4()
        
        with pytest.raises(SessionNotFoundError):
            session_manager.get_session(fake_id)


class TestAnswerProcessing:
    """Test answer processing logic"""
    
    def test_process_valid_answer(self, session_manager):
        """Test processing a valid answer"""
        session, _ = session_manager.create_session(
            role="backend_engineer",
            mode="chat"
        )
        
        answer = "I have 5 years of experience with Python and FastAPI."
        response = session_manager.process_answer(session.session_id, answer)
        
        assert "type" in response
        assert response["type"] in ["question", "followup", "complete"]
        assert "content" in response
        assert "persona" in response
    
    def test_answer_added_to_messages(self, session_manager):
        """Test that answer is added to session messages"""
        session, _ = session_manager.create_session(
            role="backend_engineer",
            mode="chat"
        )
        
        initial_count = len(session.messages)
        answer = "I have experience with Python."
        session_manager.process_answer(session.session_id, answer)
        
        updated_session = session_manager.get_session(session.session_id)
        assert len(updated_session.messages) > initial_count


class TestFollowupLogic:
    """Test follow-up question logic"""
    
    def test_followup_count_increments(self, session_manager):
        """Test that follow-up count increments"""
        session, _ = session_manager.create_session(
            role="backend_engineer",
            mode="chat"
        )
        
        # Give short answer to potentially trigger follow-up
        short_answer = "Yes."
        response = session_manager.process_answer(session.session_id, short_answer)
        
        if response["type"] == "followup":
            updated_session = session_manager.get_session(session.session_id)
            assert updated_session.followup_count > 0
    
    def test_max_followups_enforced(self, session_manager):
        """Test that max 3 follow-ups are enforced"""
        session, _ = session_manager.create_session(
            role="backend_engineer",
            mode="chat"
        )
        
        # Try to trigger multiple follow-ups
        followup_count = 0
        for i in range(10):  # Try many times
            answer = f"Short {i}"
            response = session_manager.process_answer(session.session_id, answer)
            
            if response["type"] == "followup":
                followup_count += 1
            else:
                break
        
        # Should not exceed 3 follow-ups
        assert followup_count <= 3
    
    def test_followup_resets_on_new_question(self, session_manager):
        """Test that follow-up count resets when moving to new question"""
        session, _ = session_manager.create_session(
            role="backend_engineer",
            mode="chat"
        )
        
        # Process answers until we move to next question
        for i in range(5):
            answer = f"Answer {i}"
            response = session_manager.process_answer(session.session_id, answer)
            
            if response["type"] == "question":
                # Moved to new question, check followup count reset
                updated_session = session_manager.get_session(session.session_id)
                assert updated_session.followup_count == 0
                break


class TestSessionCompletion:
    """Test session completion"""
    
    def test_end_session(self, session_manager):
        """Test ending a session"""
        session, _ = session_manager.create_session(
            role="backend_engineer",
            mode="chat"
        )
        
        completed = session_manager.end_session(session.session_id)
        
        assert completed.status == SessionStatus.COMPLETED
    
    def test_cannot_process_answer_after_completion(self, session_manager):
        """Test that answers cannot be processed after session ends"""
        session, _ = session_manager.create_session(
            role="backend_engineer",
            mode="chat"
        )
        
        session_manager.end_session(session.session_id)
        
        with pytest.raises(InvalidSessionStateError):
            session_manager.process_answer(session.session_id, "Answer")


class TestSessionProgress:
    """Test session progress tracking"""
    
    def test_get_progress(self, session_manager):
        """Test getting session progress"""
        session, _ = session_manager.create_session(
            role="backend_engineer",
            mode="chat"
        )
        
        progress = session_manager.get_session_progress(session.session_id)
        
        assert "current_question" in progress
        assert "total_questions" in progress
        assert "progress_percentage" in progress
        assert "followup_count" in progress
        assert "status" in progress
    
    def test_progress_percentage_calculation(self, session_manager):
        """Test that progress percentage is calculated correctly"""
        session, _ = session_manager.create_session(
            role="backend_engineer",
            mode="chat"
        )
        
        progress = session_manager.get_session_progress(session.session_id)
        
        expected_percentage = (session.current_question_index / progress["total_questions"]) * 100
        assert abs(progress["progress_percentage"] - expected_percentage) < 0.01


class TestSessionTranscript:
    """Test session transcript retrieval"""
    
    def test_get_transcript(self, session_manager):
        """Test getting session transcript"""
        session, _ = session_manager.create_session(
            role="backend_engineer",
            mode="chat"
        )
        
        # Add some messages
        session_manager.process_answer(session.session_id, "Test answer")
        
        transcript = session_manager.get_session_transcript(session.session_id)
        
        assert isinstance(transcript, list)
        assert len(transcript) > 0
        assert all("type" in msg and "content" in msg for msg in transcript)
    
    def test_transcript_order(self, session_manager):
        """Test that transcript maintains chronological order"""
        session, _ = session_manager.create_session(
            role="backend_engineer",
            mode="chat"
        )
        
        session_manager.process_answer(session.session_id, "Answer 1")
        
        transcript = session_manager.get_session_transcript(session.session_id)
        
        # First message should be question, second should be answer
        assert transcript[0]["type"] == "question"
        assert transcript[1]["type"] == "answer"
