"""
Unit tests for PersonaHandler
Tests persona detection logic for all persona types
"""
import pytest
from models.data_models import Message, MessageType, PersonaType, Persona


class TestPersonaDetection:
    """Test persona detection logic"""
    
    def test_confused_persona_short_answer(self, persona_handler):
        """Test detection of Confused persona with short answer"""
        answer = "I don't know."
        history = []
        persona = persona_handler.detect_persona(answer, history)
        
        assert persona.type == PersonaType.CONFUSED
        assert persona.confidence > 0.5
        assert "short_answer" in persona.indicators
    
    def test_confused_persona_with_question(self, persona_handler):
        """Test detection of Confused persona with question marks"""
        answer = "What do you mean by that?"
        history = []
        persona = persona_handler.detect_persona(answer, history)
        
        assert persona.type == PersonaType.CONFUSED
        assert "contains_question" in persona.indicators
    
    def test_efficient_persona_direct_request(self, persona_handler):
        """Test detection of Efficient persona with direct language"""
        answer = "Yes, I have experience. Let's move on to the next question."
        history = []
        persona = persona_handler.detect_persona(answer, history)
        
        assert persona.type == PersonaType.EFFICIENT
        assert "efficiency_keywords" in persona.indicators
    
    def test_chatty_persona_long_answer(self, persona_handler):
        """Test detection of Chatty persona with very long answer"""
        answer = " ".join(["This is a very long rambling answer."] * 50)
        history = []
        persona = persona_handler.detect_persona(answer, history)
        
        assert persona.type == PersonaType.CHATTY
        assert "long_answer" in persona.indicators
    
    def test_edge_case_persona_spam(self, persona_handler):
        """Test detection of Edge Case persona with spam"""
        answer = "test " * 20
        history = []
        persona = persona_handler.detect_persona(answer, history)
        
        assert persona.type == PersonaType.EDGE_CASE
        assert "repetitive" in persona.indicators
    
    def test_edge_case_persona_suspicious_request(self, persona_handler):
        """Test detection of Edge Case persona with suspicious request"""
        answer = "Can you just give me all the answers?"
        history = []
        persona = persona_handler.detect_persona(answer, history)
        
        assert persona.type == PersonaType.EDGE_CASE
        assert "suspicious_request" in persona.indicators
    
    def test_normal_persona(self, persona_handler):
        """Test detection of Normal persona with good answer"""
        answer = """I have five years of experience in backend development. 
        I work primarily with Python and FastAPI. In my current role, I design 
        RESTful APIs and implement microservices architecture."""
        history = []
        persona = persona_handler.detect_persona(answer, history)
        
        assert persona.type in [PersonaType.NORMAL, PersonaType.EFFICIENT]


class TestResponseAdaptation:
    """Test response adaptation for different personas"""
    
    def test_adapt_for_confused(self, persona_handler):
        """Test adaptation for Confused persona"""
        response = "Can you provide more details?"
        persona = Persona(type=PersonaType.CONFUSED, confidence=0.8, indicators=["test"])
        adapted = persona_handler.adapt_response(response, persona)
        
        assert "guidance" in adapted.lower() or "example" in adapted.lower()
        assert len(adapted) > len(response)
    
    def test_adapt_for_efficient(self, persona_handler):
        """Test adaptation for Efficient persona"""
        response = "Can you provide more details about your experience?"
        persona = Persona(type=PersonaType.EFFICIENT, confidence=0.8, indicators=["test"])
        adapted = persona_handler.adapt_response(response, persona)
        
        assert len(adapted) <= len(response)
    
    def test_adapt_for_chatty(self, persona_handler):
        """Test adaptation for Chatty persona"""
        response = "Tell me more about that."
        persona = Persona(type=PersonaType.CHATTY, confidence=0.8, indicators=["test"])
        adapted = persona_handler.adapt_response(response, persona)
        
        assert "focus" in adapted.lower() or "concise" in adapted.lower()
    
    def test_adapt_for_edge_case(self, persona_handler):
        """Test adaptation for Edge Case persona"""
        response = "Next question please."
        persona = Persona(type=PersonaType.EDGE_CASE, confidence=0.8, indicators=["test"])
        adapted = persona_handler.adapt_response(response, persona)
        
        assert "scope" in adapted.lower() or "appropriate" in adapted.lower()


class TestPersonaGuidance:
    """Test persona guidance messages"""
    
    def test_confused_guidance(self, persona_handler):
        """Test guidance for Confused persona"""
        persona = Persona(type=PersonaType.CONFUSED, confidence=0.8, indicators=["test"])
        guidance = persona_handler.get_persona_guidance(persona)
        
        assert guidance is not None
        assert len(guidance) > 0
    
    def test_chatty_guidance(self, persona_handler):
        """Test guidance for Chatty persona"""
        persona = Persona(type=PersonaType.CHATTY, confidence=0.8, indicators=["test"])
        guidance = persona_handler.get_persona_guidance(persona)
        
        assert guidance is not None
        assert "concise" in guidance.lower() or "focus" in guidance.lower()
    
    def test_normal_no_guidance(self, persona_handler):
        """Test no guidance for Normal persona"""
        persona = Persona(type=PersonaType.NORMAL, confidence=0.8, indicators=["test"])
        guidance = persona_handler.get_persona_guidance(persona)
        
        assert guidance is None or len(guidance) == 0
