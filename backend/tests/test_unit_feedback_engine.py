"""
Unit tests for FeedbackEngine
Tests score calculation and validation logic
"""
import pytest
from uuid import uuid4
from datetime import datetime
from models.data_models import Message, MessageType


class TestScoreValidation:
    """Test score validation and clamping"""
    
    def test_valid_scores(self, feedback_engine):
        """Test that valid scores pass validation"""
        for score in [1, 2, 3, 4, 5]:
            result = feedback_engine._validate_score(score, "test")
            assert result == score
    
    def test_score_clamping_low(self, feedback_engine):
        """Test that scores below 1 are clamped to 1"""
        assert feedback_engine._validate_score(0, "test") == 1
        assert feedback_engine._validate_score(-5, "test") == 1
    
    def test_score_clamping_high(self, feedback_engine):
        """Test that scores above 5 are clamped to 5"""
        assert feedback_engine._validate_score(6, "test") == 5
        assert feedback_engine._validate_score(100, "test") == 5
    
    def test_invalid_score_none(self, feedback_engine):
        """Test that None score raises error"""
        with pytest.raises(Exception):
            feedback_engine._validate_score(None, "test")
    
    def test_invalid_score_string(self, feedback_engine):
        """Test that string score raises error"""
        with pytest.raises(Exception):
            feedback_engine._validate_score("invalid", "test")


class TestThreeItemsValidation:
    """Test ensuring exactly 3 items in lists"""
    
    def test_exactly_three_items(self, feedback_engine):
        """Test list with exactly 3 items remains unchanged"""
        items = ["Item 1", "Item 2", "Item 3"]
        result = feedback_engine._ensure_three_items(items, "test", "Fallback")
        
        assert len(result) == 3
        assert result == items
    
    def test_fewer_than_three_items(self, feedback_engine):
        """Test list with fewer items is padded"""
        items = ["Item 1"]
        result = feedback_engine._ensure_three_items(items, "test", "Fallback")
        
        assert len(result) == 3
        assert result[0] == "Item 1"
        assert "Fallback" in result[1]
    
    def test_more_than_three_items(self, feedback_engine):
        """Test list with more items is truncated"""
        items = ["Item 1", "Item 2", "Item 3", "Item 4", "Item 5"]
        result = feedback_engine._ensure_three_items(items, "test", "Fallback")
        
        assert len(result) == 3
        assert result == items[:3]
    
    def test_empty_strings_filtered(self, feedback_engine):
        """Test that empty strings are filtered out"""
        items = ["Item 1", "", "  ", "Item 2"]
        result = feedback_engine._ensure_three_items(items, "test", "Fallback")
        
        assert len(result) == 3
        assert result[0] == "Item 1"
        assert result[1] == "Item 2"
        assert "Fallback" in result[2]
    
    def test_empty_list(self, feedback_engine):
        """Test empty list is filled with fallback"""
        items = []
        result = feedback_engine._ensure_three_items(items, "test", "Fallback")
        
        assert len(result) == 3
        for item in result:
            assert "Fallback" in item


class TestFeedbackStructure:
    """Test feedback report structure validation"""
    
    def test_feedback_has_required_fields(self, feedback_engine, sample_role):
        """Test that generated feedback has all required fields"""
        # Skip if Ollama not available
        if not feedback_engine.ollama_client.check_health():
            pytest.skip("Ollama not available")
        
        session_id = uuid4()
        transcript = [
            Message(
                type=MessageType.QUESTION,
                content="Tell me about your experience.",
                timestamp=datetime.now()
            ),
            Message(
                type=MessageType.ANSWER,
                content="I have 5 years of experience with Python and FastAPI.",
                timestamp=datetime.now()
            )
        ]
        
        feedback = feedback_engine.generate_feedback(session_id, sample_role, transcript)
        
        assert feedback.session_id == session_id
        assert hasattr(feedback, 'scores')
        assert hasattr(feedback, 'strengths')
        assert hasattr(feedback, 'improvements')
        assert hasattr(feedback, 'overall_feedback')
    
    def test_feedback_scores_in_range(self, feedback_engine, sample_role):
        """Test that feedback scores are within valid range"""
        # Skip if Ollama not available
        if not feedback_engine.ollama_client.check_health():
            pytest.skip("Ollama not available")
        
        session_id = uuid4()
        transcript = [
            Message(
                type=MessageType.QUESTION,
                content="Tell me about your experience.",
                timestamp=datetime.now()
            ),
            Message(
                type=MessageType.ANSWER,
                content="I have experience with backend development.",
                timestamp=datetime.now()
            )
        ]
        
        feedback = feedback_engine.generate_feedback(session_id, sample_role, transcript)
        
        assert 1 <= feedback.scores.communication <= 5
        assert 1 <= feedback.scores.technical_knowledge <= 5
        assert 1 <= feedback.scores.structure <= 5
    
    def test_feedback_has_three_strengths(self, feedback_engine, sample_role):
        """Test that feedback has exactly 3 strengths"""
        # Skip if Ollama not available
        if not feedback_engine.ollama_client.check_health():
            pytest.skip("Ollama not available")
        
        session_id = uuid4()
        transcript = [
            Message(
                type=MessageType.QUESTION,
                content="Tell me about your experience.",
                timestamp=datetime.now()
            ),
            Message(
                type=MessageType.ANSWER,
                content="I have experience.",
                timestamp=datetime.now()
            )
        ]
        
        feedback = feedback_engine.generate_feedback(session_id, sample_role, transcript)
        
        assert len(feedback.strengths) == 3
    
    def test_feedback_has_three_improvements(self, feedback_engine, sample_role):
        """Test that feedback has exactly 3 improvements"""
        # Skip if Ollama not available
        if not feedback_engine.ollama_client.check_health():
            pytest.skip("Ollama not available")
        
        session_id = uuid4()
        transcript = [
            Message(
                type=MessageType.QUESTION,
                content="Tell me about your experience.",
                timestamp=datetime.now()
            ),
            Message(
                type=MessageType.ANSWER,
                content="I have experience.",
                timestamp=datetime.now()
            )
        ]
        
        feedback = feedback_engine.generate_feedback(session_id, sample_role, transcript)
        
        assert len(feedback.improvements) == 3


class TestAverageScore:
    """Test average score calculation"""
    
    def test_average_score_calculation(self, feedback_engine, sample_role):
        """Test that average score is calculated correctly"""
        # Skip if Ollama not available
        if not feedback_engine.ollama_client.check_health():
            pytest.skip("Ollama not available")
        
        session_id = uuid4()
        transcript = [
            Message(
                type=MessageType.QUESTION,
                content="Question",
                timestamp=datetime.now()
            ),
            Message(
                type=MessageType.ANSWER,
                content="Answer",
                timestamp=datetime.now()
            )
        ]
        
        feedback = feedback_engine.generate_feedback(session_id, sample_role, transcript)
        
        expected_avg = (
            feedback.scores.communication +
            feedback.scores.technical_knowledge +
            feedback.scores.structure
        ) / 3
        
        assert abs(feedback.scores.average - expected_avg) < 0.01
