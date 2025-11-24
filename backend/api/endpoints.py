"""
FastAPI endpoints for Interview Practice Partner.

Provides REST API for:
- Starting interview sessions
- Submitting answers and receiving questions/follow-ups
- Generating feedback
- Retrieving interview history
- Accessing session transcripts
"""

from typing import Optional
from uuid import UUID
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

from services.interview_session_manager import (
    InterviewSessionManager,
    SessionNotFoundError,
    InvalidSessionStateError,
    SessionManagerError
)
from services.feedback_engine import (
    FeedbackEngine,
    FeedbackEngineError
)
from services.ollama_client import (
    OllamaClient,
    OllamaConnectionError,
    OllamaGenerationError
)
from services.prompt_generator import PromptGenerator
from services.role_loader import get_role_loader
from storage.storage_service import StorageService
from models.data_models import PersonaType


# Initialize services
ollama_client = OllamaClient()
prompt_generator = PromptGenerator()
session_manager = InterviewSessionManager(
    ollama_client=ollama_client,
    prompt_generator=prompt_generator
)
feedback_engine = FeedbackEngine(
    ollama_client=ollama_client,
    prompt_generator=prompt_generator
)
storage_service = StorageService()
role_loader = get_role_loader()

# Create router
router = APIRouter(prefix="/api", tags=["interview"])


# Request/Response Models
class StartRequest(BaseModel):
    """Request model for starting an interview session."""
    role: str = Field(..., description="Job role for the interview (e.g., 'backend_engineer')")
    mode: str = Field(default="chat", description="Interaction mode: 'chat' or 'voice'")


class StartResponse(BaseModel):
    """Response model for starting an interview session."""
    session_id: str = Field(..., description="Unique session identifier")
    question: str = Field(..., description="First interview question")
    question_number: int = Field(..., description="Current question number")
    total_questions: int = Field(..., description="Total number of questions")


class AnswerRequest(BaseModel):
    """Request model for submitting an answer."""
    session_id: str = Field(..., description="Session identifier")
    answer: str = Field(..., description="User's answer to the question")


class AnswerResponse(BaseModel):
    """Response model for answer submission."""
    type: str = Field(..., description="Response type: 'question', 'followup', or 'complete'")
    content: str = Field(..., description="Next question, follow-up, or completion message")
    question_number: int = Field(..., description="Current question number")
    persona: Optional[str] = Field(None, description="Detected user persona")


class FeedbackRequest(BaseModel):
    """Request model for generating feedback."""
    session_id: str = Field(..., description="Session identifier")


class FeedbackResponse(BaseModel):
    """Response model for feedback."""
    session_id: str
    scores: dict = Field(..., description="Scores for communication, technical_knowledge, structure")
    strengths: list[str] = Field(..., description="Three key strengths")
    improvements: list[str] = Field(..., description="Three areas for improvement")
    overall_feedback: str = Field(..., description="Overall performance summary")


class SessionSummaryResponse(BaseModel):
    """Response model for session summary in history."""
    session_id: str
    role: str
    date: str
    score: float
    status: str


class HistoryResponse(BaseModel):
    """Response model for interview history."""
    sessions: list[SessionSummaryResponse]
    total_interviews: int
    average_score: float


class TranscriptResponse(BaseModel):
    """Response model for session transcript."""
    session_id: str
    role: str
    mode: str
    created_at: str
    status: str
    transcript: list[dict]
    feedback: Optional[dict]


# Endpoints

@router.post("/start", response_model=StartResponse, status_code=status.HTTP_201_CREATED)
async def start_interview(request: StartRequest):
    """
    Start a new interview session.
    
    Creates a new interview session for the specified role and returns
    the first question.
    
    Args:
        request: StartRequest with role and mode
        
    Returns:
        StartResponse with session_id and first question
        
    Raises:
        HTTPException 400: Invalid role or mode
        HTTPException 503: Ollama service unavailable
        HTTPException 500: Server error during session creation
    """
    try:
        # Validate role against available roles
        if not role_loader.is_valid_role(request.role):
            available_roles = role_loader.get_role_names()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid role '{request.role}'. Available roles: {', '.join(available_roles)}"
            )
        
        # Validate mode
        valid_modes = ["chat", "voice"]
        if request.mode not in valid_modes:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid mode '{request.mode}'. Must be one of: {', '.join(valid_modes)}"
            )
        
        # Check Ollama health before starting session
        if not ollama_client.check_health():
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Interview service is temporarily unavailable. Please ensure Ollama is running and try again."
            )
        
        # Create session
        session, first_question = session_manager.create_session(
            role=request.role,
            mode=request.mode
        )
        
        # Save session to storage with error handling
        try:
            storage_service.save_session(session)
        except Exception as storage_error:
            # Log error but continue - session is in memory
            print(f"Warning: Failed to persist session to storage: {storage_error}")
        
        # Get total questions for this role
        role_obj = role_loader.get_role(request.role)
        total_questions = len(role_obj.questions) if role_obj else 0
        
        return StartResponse(
            session_id=str(session.session_id),
            question=first_question,
            question_number=1,
            total_questions=total_questions
        )
        
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except SessionManagerError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except OllamaConnectionError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Interview service is temporarily unavailable. Please ensure Ollama is running and try again."
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to start interview session: {str(e)}"
        )


@router.post("/answer", response_model=AnswerResponse)
async def submit_answer(request: AnswerRequest):
    """
    Submit an answer and get next question or follow-up.
    
    Processes the user's answer, detects persona, and determines whether
    to ask a follow-up question or move to the next main question.
    
    Args:
        request: AnswerRequest with session_id and answer
        
    Returns:
        AnswerResponse with next question, follow-up, or completion message
        
    Raises:
        HTTPException 400: Invalid input or session state
        HTTPException 404: Session not found
        HTTPException 503: Ollama service unavailable
        HTTPException 500: Server error during processing
    """
    try:
        # Validate session_id format
        try:
            session_uuid = UUID(request.session_id)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid session_id format. Must be a valid UUID."
            )
        
        # Validate session exists
        try:
            session = session_manager.get_session(session_uuid)
        except SessionNotFoundError:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Session '{request.session_id}' not found. It may have expired or been deleted."
            )
        
        # Validate answer is not empty
        if not request.answer or not request.answer.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Answer cannot be empty. Please provide a response to the question."
            )
        
        # Check answer length (max 2000 words)
        word_count = len(request.answer.split())
        if word_count > 2000:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Answer too long ({word_count} words). Please keep your response under 2000 words."
            )
        
        # Process answer with Ollama error handling
        try:
            response = session_manager.process_answer(
                session_id=session_uuid,
                answer=request.answer
            )
        except OllamaConnectionError as e:
            # Ollama service unavailable - provide helpful error
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Interview service is temporarily unavailable. Please ensure Ollama is running and try again in a moment."
            )
        except OllamaGenerationError as e:
            # LLM generation failed - provide fallback
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to generate response. Please try submitting your answer again."
            )
        
        # Update storage with graceful degradation
        try:
            session = session_manager.get_session(session_uuid)
            storage_service.update_session(session)
            
            # Save messages to storage
            # Get the last 1-2 messages (answer and possibly follow-up/question)
            recent_messages = session.messages[-2:] if len(session.messages) >= 2 else session.messages[-1:]
            for msg in recent_messages:
                storage_service.save_message(session_uuid, msg)
        except Exception as storage_error:
            # Log error but continue - session is in memory
            print(f"Warning: Failed to persist session updates to storage: {storage_error}")
        
        # Extract persona type if available
        persona_str = None
        if response.get("persona"):
            persona_str = response["persona"].type.value
        
        return AnswerResponse(
            type=response["type"],
            content=response["content"],
            question_number=response["question_number"],
            persona=persona_str
        )
        
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except SessionNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session '{request.session_id}' not found. It may have expired or been deleted."
        )
    except InvalidSessionStateError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except ValueError as e:
        error_msg = str(e) if str(e) else "Invalid input provided"
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_msg
        )
    except Exception as e:
        error_msg = str(e) if str(e) else "An unexpected error occurred"
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process answer: {error_msg}"
        )


@router.post("/feedback", response_model=FeedbackResponse)
async def generate_feedback(request: FeedbackRequest):
    """
    Generate comprehensive feedback for a completed interview session.
    
    Analyzes the interview transcript and generates structured feedback
    with scores, strengths, and improvement areas.
    
    Args:
        request: FeedbackRequest with session_id
        
    Returns:
        FeedbackResponse with detailed performance feedback
        
    Raises:
        HTTPException 400: Invalid session_id format or insufficient data
        HTTPException 404: Session not found
        HTTPException 503: Ollama service unavailable
        HTTPException 500: Server error during feedback generation
    """
    try:
        # Validate session_id format
        try:
            session_uuid = UUID(request.session_id)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid session_id format. Must be a valid UUID."
            )
        
        # Get session with validation
        try:
            session = session_manager.get_session(session_uuid)
        except SessionNotFoundError:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Session '{request.session_id}' not found. It may have expired or been deleted."
            )
        
        # Validate session has sufficient data for feedback
        if not session.messages or len(session.messages) < 2:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Insufficient interview data to generate feedback. Please answer at least one question."
            )
        
        # Get role
        role = role_loader.get_role(session.role)
        if not role:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Role configuration '{session.role}' not found. Please contact support."
            )
        
        # Generate feedback with Ollama error handling
        try:
            feedback_report = feedback_engine.generate_feedback(
                session_id=session_uuid,
                role=role,
                transcript=session.messages
            )
        except OllamaConnectionError as e:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Interview service is temporarily unavailable. Please ensure Ollama is running and try again in a moment."
            )
        except OllamaGenerationError as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to generate feedback. Please try again."
            )
        
        # Save feedback to storage with graceful degradation
        try:
            storage_service.save_feedback(feedback_report)
        except Exception as storage_error:
            # Log error but continue - feedback is still returned
            print(f"Warning: Failed to persist feedback to storage: {storage_error}")
        
        # Mark session as completed
        try:
            session_manager.end_session(session_uuid)
            session = session_manager.get_session(session_uuid)
            storage_service.update_session(session)
        except Exception as update_error:
            # Log error but continue - feedback is still returned
            print(f"Warning: Failed to update session status: {update_error}")
        
        return FeedbackResponse(
            session_id=str(feedback_report.session_id),
            scores={
                "communication": feedback_report.scores.communication,
                "technical_knowledge": feedback_report.scores.technical_knowledge,
                "structure": feedback_report.scores.structure
            },
            strengths=feedback_report.strengths,
            improvements=feedback_report.improvements,
            overall_feedback=feedback_report.overall_feedback
        )
        
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except SessionNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session '{request.session_id}' not found. It may have expired or been deleted."
        )
    except FeedbackEngineError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate feedback: {str(e)}"
        )
    except Exception as e:
        error_msg = str(e) if str(e) else "An unexpected error occurred"
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate feedback: {error_msg}"
        )


@router.get("/history", response_model=HistoryResponse)
async def get_interview_history(limit: Optional[int] = None):
    """
    Retrieve user's interview history.
    
    Returns a list of all completed interview sessions with summary
    information including scores and dates.
    
    Args:
        limit: Optional limit on number of sessions to return
        
    Returns:
        HistoryResponse with session summaries and statistics
        
    Raises:
        HTTPException 400: Invalid limit parameter
        HTTPException 500: Server error during retrieval
    """
    try:
        # Validate limit parameter
        if limit is not None:
            if limit < 1:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Limit must be a positive integer."
                )
            if limit > 1000:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Limit cannot exceed 1000 sessions."
                )
        
        # Get history from storage with error handling
        try:
            history = storage_service.get_user_history(limit=limit)
        except Exception as storage_error:
            # Log error and return empty history
            print(f"Warning: Failed to retrieve history from storage: {storage_error}")
            # Return empty history instead of failing
            return HistoryResponse(
                sessions=[],
                total_interviews=0,
                average_score=0.0
            )
        
        # Convert to response format
        sessions = [
            SessionSummaryResponse(
                session_id=str(s.session_id),
                role=s.role,
                date=s.date.isoformat(),
                score=round(s.score, 2),
                status=s.status
            )
            for s in history.sessions
        ]
        
        return HistoryResponse(
            sessions=sessions,
            total_interviews=history.total_interviews,
            average_score=round(history.average_score, 2)
        )
        
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        error_msg = str(e) if str(e) else "An unexpected error occurred"
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve interview history: {error_msg}"
        )


@router.get("/session/{session_id}", response_model=TranscriptResponse)
async def get_session_transcript(session_id: str):
    """
    Retrieve full session transcript with all messages and feedback.
    
    Returns the complete conversation history for a session including
    questions, answers, follow-ups, and feedback if available.
    
    Args:
        session_id: Session identifier
        
    Returns:
        TranscriptResponse with full transcript and feedback
        
    Raises:
        HTTPException 400: Invalid session_id format
        HTTPException 404: Session not found
        HTTPException 500: Server error during retrieval
    """
    try:
        # Validate session_id format
        try:
            session_uuid = UUID(session_id)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid session_id format. Must be a valid UUID."
            )
        
        # Get transcript from storage with error handling
        try:
            transcript_data = storage_service.get_session_transcript(session_uuid)
        except Exception as storage_error:
            print(f"Error retrieving transcript from storage: {storage_error}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to retrieve session transcript from storage."
            )
        
        if not transcript_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Session '{session_id}' not found. It may have expired or been deleted."
            )
        
        return TranscriptResponse(**transcript_data)
        
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        error_msg = str(e) if str(e) else "An unexpected error occurred"
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve session transcript: {error_msg}"
        )
