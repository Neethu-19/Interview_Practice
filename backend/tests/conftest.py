"""
Pytest configuration and shared fixtures
"""
import pytest
import sys
from pathlib import Path

# Add backend to path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from models.data_models import Role, Message, MessageType, PersonaType
from services.ollama_client import OllamaClient
from services.prompt_generator import PromptGenerator
from services.persona_handler import PersonaHandler
from services.feedback_engine import FeedbackEngine
from services.interview_session_manager import InterviewSessionManager
from datetime import datetime


@pytest.fixture
def sample_role():
    """Create a sample role for testing"""
    return Role(
        name="backend_engineer",
        display_name="Backend Engineer",
        questions=[
            "Tell me about your experience with Python.",
            "How do you approach debugging?",
            "Describe a challenging project."
        ],
        evaluation_criteria={
            "communication": {"clarity": "Clear articulation"},
            "technical_knowledge": {"depth": "Deep understanding"},
            "structure": {"organization": "Well-organized"}
        }
    )


@pytest.fixture
def ollama_client():
    """Create OllamaClient instance"""
    return OllamaClient(
        base_url="http://localhost:11434",
        model="llama3.1:8b"
    )


@pytest.fixture
def prompt_generator():
    """Create PromptGenerator instance"""
    return PromptGenerator()


@pytest.fixture
def persona_handler():
    """Create PersonaHandler instance"""
    return PersonaHandler()


@pytest.fixture
def feedback_engine(ollama_client, prompt_generator):
    """Create FeedbackEngine instance"""
    return FeedbackEngine(
        ollama_client=ollama_client,
        prompt_generator=prompt_generator,
        timeout_seconds=10,
        temperature=0.3
    )


@pytest.fixture
def session_manager():
    """Create InterviewSessionManager instance"""
    return InterviewSessionManager()


@pytest.fixture
def sample_messages():
    """Create sample message history"""
    return [
        Message(
            type=MessageType.QUESTION,
            content="Tell me about your experience.",
            timestamp=datetime.now()
        ),
        Message(
            type=MessageType.ANSWER,
            content="I have 5 years of experience.",
            timestamp=datetime.now()
        )
    ]
