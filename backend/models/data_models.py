"""
Data models for the Interview Practice Partner system.
All models use Pydantic for validation and serialization.
"""
from pydantic import BaseModel, Field, field_validator
from typing import List, Optional, Literal
from datetime import datetime
from uuid import UUID, uuid4
from enum import Enum


class PersonaType(str, Enum):
    """User persona types based on interaction patterns"""
    CONFUSED = "confused"
    EFFICIENT = "efficient"
    CHATTY = "chatty"
    EDGE_CASE = "edge_case"
    NORMAL = "normal"


class MessageType(str, Enum):
    """Types of messages in interview conversation"""
    QUESTION = "question"
    ANSWER = "answer"
    FOLLOWUP = "followup"


class InteractionMode(str, Enum):
    """Communication modes for the interview"""
    CHAT = "chat"
    VOICE = "voice"


class SessionStatus(str, Enum):
    """Interview session status"""
    ACTIVE = "active"
    COMPLETED = "completed"


class QuestionType(str, Enum):
    """Types of interview questions"""
    MAIN = "main"
    FOLLOWUP = "followup"


# Core Data Models

class Role(BaseModel):
    """Role profile with interview questions and evaluation criteria"""
    name: str = Field(..., description="Internal role identifier (e.g., 'backend_engineer')")
    display_name: str = Field(..., description="Human-readable role name")
    questions: List[str] = Field(..., min_length=1, description="List of interview questions for this role")
    evaluation_criteria: dict = Field(..., description="Role-specific evaluation criteria")

    @field_validator('questions')
    @classmethod
    def validate_questions(cls, v):
        if not v or len(v) == 0:
            raise ValueError("Role must have at least one question")
        return v


class Question(BaseModel):
    """Individual interview question"""
    id: int = Field(..., ge=0, description="Question identifier")
    content: str = Field(..., min_length=1, description="Question text")
    role: str = Field(..., description="Associated role name")
    type: QuestionType = Field(default=QuestionType.MAIN, description="Question type")

    @field_validator('content')
    @classmethod
    def validate_content(cls, v):
        if not v or not v.strip():
            raise ValueError("Question content cannot be empty")
        return v.strip()


class Message(BaseModel):
    """Single message in interview conversation"""
    type: MessageType = Field(..., description="Message type")
    content: str = Field(..., min_length=1, description="Message content")
    timestamp: datetime = Field(default_factory=datetime.now, description="Message timestamp")

    @field_validator('content')
    @classmethod
    def validate_content(cls, v):
        if not v or not v.strip():
            raise ValueError("Message content cannot be empty")
        return v.strip()


class Session(BaseModel):
    """Interview session state"""
    session_id: UUID = Field(default_factory=uuid4, description="Unique session identifier")
    role: str = Field(..., description="Selected role for this interview")
    mode: InteractionMode = Field(..., description="Interaction mode (chat or voice)")
    created_at: datetime = Field(default_factory=datetime.now, description="Session creation timestamp")
    status: SessionStatus = Field(default=SessionStatus.ACTIVE, description="Current session status")
    current_question_index: int = Field(default=0, ge=0, description="Index of current question")
    followup_count: int = Field(default=0, ge=0, le=3, description="Number of follow-ups for current question")
    messages: List[Message] = Field(default_factory=list, description="Conversation history")

    @field_validator('followup_count')
    @classmethod
    def validate_followup_count(cls, v):
        if v > 3:
            raise ValueError("Maximum 3 follow-ups allowed per question")
        return v


class UserResponse(BaseModel):
    """User's answer to an interview question"""
    session_id: UUID = Field(..., description="Associated session ID")
    answer: str = Field(..., min_length=1, max_length=20000, description="User's answer text")
    word_count: int = Field(default=0, ge=0, description="Number of words in answer")
    response_time_seconds: Optional[float] = Field(default=None, ge=0, description="Time taken to respond")

    def model_post_init(self, __context):
        """Calculate word count after initialization if not set"""
        if self.word_count == 0 and self.answer:
            object.__setattr__(self, 'word_count', len(self.answer.strip().split()))

    @field_validator('answer')
    @classmethod
    def validate_answer(cls, v):
        if not v or not v.strip():
            raise ValueError("Answer cannot be empty")
        word_count = len(v.strip().split())
        if word_count > 2000:
            raise ValueError("Answer must be under 2000 words")
        return v.strip()


class Scores(BaseModel):
    """Performance scores across evaluation dimensions"""
    communication: int = Field(..., ge=1, le=5, description="Communication skills score (1-5)")
    technical_knowledge: int = Field(..., ge=1, le=5, description="Technical knowledge score (1-5)")
    structure: int = Field(..., ge=1, le=5, description="Answer structure score (1-5)")

    @property
    def average(self) -> float:
        """Calculate average score across all dimensions"""
        return round((self.communication + self.technical_knowledge + self.structure) / 3, 2)


class FeedbackReport(BaseModel):
    """Comprehensive performance feedback for an interview session"""
    session_id: UUID = Field(..., description="Associated session ID")
    scores: Scores = Field(..., description="Performance scores")
    strengths: List[str] = Field(..., min_length=3, max_length=3, description="Top 3 strengths")
    improvements: List[str] = Field(..., min_length=3, max_length=3, description="Top 3 areas for improvement")
    overall_feedback: str = Field(..., min_length=50, description="Overall assessment summary")
    generated_at: datetime = Field(default_factory=datetime.now, description="Feedback generation timestamp")

    @field_validator('strengths', 'improvements')
    @classmethod
    def validate_feedback_items(cls, v):
        if len(v) != 3:
            raise ValueError("Must provide exactly 3 items")
        for item in v:
            if not item or not item.strip():
                raise ValueError("Feedback items cannot be empty")
        return [item.strip() for item in v]

    @field_validator('overall_feedback')
    @classmethod
    def validate_overall_feedback(cls, v):
        if not v or len(v.strip()) < 50:
            raise ValueError("Overall feedback must be at least 50 characters")
        return v.strip()


class Persona(BaseModel):
    """Detected user persona based on interaction patterns"""
    type: PersonaType = Field(..., description="Detected persona type")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence level of detection (0-1)")
    indicators: List[str] = Field(default_factory=list, description="Behavioral indicators that led to detection")

    @field_validator('confidence')
    @classmethod
    def validate_confidence(cls, v):
        if not 0.0 <= v <= 1.0:
            raise ValueError("Confidence must be between 0.0 and 1.0")
        return round(v, 2)


class SessionSummary(BaseModel):
    """Summary of a completed interview session"""
    session_id: UUID = Field(..., description="Session identifier")
    role: str = Field(..., description="Interview role")
    date: datetime = Field(..., description="Session date")
    score: float = Field(..., ge=0.0, le=5.0, description="Average performance score (0.0 if no feedback yet)")
    status: str = Field(..., description="Session status")

    @field_validator('score')
    @classmethod
    def validate_score(cls, v):
        if not 0.0 <= v <= 5.0:
            raise ValueError("Score must be between 0.0 and 5.0")
        return round(v, 2)


class InterviewHistory(BaseModel):
    """User's complete interview history"""
    sessions: List[SessionSummary] = Field(default_factory=list, description="List of session summaries")
    total_interviews: int = Field(default=0, ge=0, description="Total number of interviews completed")
    average_score: float = Field(default=0.0, ge=0.0, le=5.0, description="Average score across all sessions")

    def model_post_init(self, __context):
        """Calculate totals and averages after initialization"""
        if self.total_interviews == 0 and self.sessions:
            object.__setattr__(self, 'total_interviews', len(self.sessions))
        
        if self.average_score == 0.0 and self.sessions:
            scores = [session.score for session in self.sessions]
            avg = round(sum(scores) / len(scores), 2) if scores else 0.0
            object.__setattr__(self, 'average_score', avg)
