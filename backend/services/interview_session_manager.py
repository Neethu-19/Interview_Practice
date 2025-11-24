"""
Interview Session Manager

Manages interview sessions including:
- Session creation and initialization
- Question sequencing
- Answer processing
- Follow-up question logic
- Session state tracking
- Session completion
"""

from typing import Optional, Dict, List, Tuple
from uuid import UUID, uuid4
from datetime import datetime

from models.data_models import (
    Session, Message, MessageType, InteractionMode,
    SessionStatus, Question, QuestionType, Role,
    Persona, PersonaType
)
from services.role_loader import RoleLoader, get_role_loader
from services.ollama_client import OllamaClient, OllamaClientError
from services.prompt_generator import PromptGenerator
from services.persona_handler import PersonaHandler


class SessionManagerError(Exception):
    """Base exception for session manager errors"""
    pass


class SessionNotFoundError(SessionManagerError):
    """Raised when session is not found"""
    pass


class InvalidSessionStateError(SessionManagerError):
    """Raised when session is in invalid state for operation"""
    pass


class InterviewSessionManager:
    """
    Manages interview sessions and coordinates between components.
    
    Responsibilities:
    - Create and initialize new interview sessions
    - Track session state (current question, follow-up count)
    - Retrieve questions sequentially
    - Process user answers
    - Determine when to ask follow-up questions
    - Enforce max 3 follow-ups per question rule
    - Finalize completed sessions
    """
    
    MAX_FOLLOWUPS_PER_QUESTION = 3
    
    def __init__(
        self,
        role_loader: Optional[RoleLoader] = None,
        ollama_client: Optional[OllamaClient] = None,
        prompt_generator: Optional[PromptGenerator] = None,
        persona_handler: Optional[PersonaHandler] = None
    ):
        """
        Initialize the InterviewSessionManager.
        
        Args:
            role_loader: RoleLoader instance (uses default if None)
            ollama_client: OllamaClient instance (creates default if None)
            prompt_generator: PromptGenerator instance (creates default if None)
            persona_handler: PersonaHandler instance (creates default if None)
        """
        self.role_loader = role_loader or get_role_loader()
        self.ollama_client = ollama_client or OllamaClient()
        self.prompt_generator = prompt_generator or PromptGenerator()
        self.persona_handler = persona_handler or PersonaHandler()
        
        # In-memory session storage (will be replaced with database in task 9)
        self._sessions: Dict[UUID, Session] = {}
        
        # Track current question content for each session
        self._current_questions: Dict[UUID, str] = {}
        
        # Track detected personas for each session
        self._session_personas: Dict[UUID, Persona] = {}
    
    def create_session(
        self,
        role: str,
        mode: str = "chat"
    ) -> Tuple[Session, str]:
        """
        Create and initialize a new interview session.
        
        Args:
            role: Role name for the interview
            mode: Interaction mode ("chat" or "voice")
            
        Returns:
            Tuple of (Session object, first question text)
            
        Raises:
            SessionManagerError: If role is invalid or session creation fails
        """
        # Validate role
        if not self.role_loader.is_valid_role(role):
            available_roles = self.role_loader.get_role_names()
            raise SessionManagerError(
                f"Invalid role '{role}'. Available roles: {', '.join(available_roles)}"
            )
        
        # Validate mode
        try:
            interaction_mode = InteractionMode(mode)
        except ValueError:
            raise SessionManagerError(
                f"Invalid mode '{mode}'. Must be 'chat' or 'voice'"
            )
        
        # Create new session
        session = Session(
            session_id=uuid4(),
            role=role,
            mode=interaction_mode,
            created_at=datetime.now(),
            status=SessionStatus.ACTIVE,
            current_question_index=0,
            followup_count=0,
            messages=[]
        )
        
        # Store session
        self._sessions[session.session_id] = session
        
        # Initialize persona as normal
        self._session_personas[session.session_id] = Persona(
            type=PersonaType.NORMAL,
            confidence=0.8,
            indicators=["initial_state"]
        )
        
        # Get first question
        first_question = self.get_next_question(session.session_id)
        
        return session, first_question
    
    def get_next_question(self, session_id: UUID) -> str:
        """
        Retrieve the next question for the session.
        
        Args:
            session_id: Session identifier
            
        Returns:
            Next question text
            
        Raises:
            SessionNotFoundError: If session doesn't exist
            InvalidSessionStateError: If session is completed or no more questions
        """
        session = self._get_session(session_id)
        
        # Check session status
        if session.status == SessionStatus.COMPLETED:
            raise InvalidSessionStateError("Session is already completed")
        
        # Get role and questions
        role = self.role_loader.get_role(session.role)
        if not role:
            raise SessionManagerError(f"Role '{session.role}' not found")
        
        # Check if we have more questions
        if session.current_question_index >= len(role.questions):
            raise InvalidSessionStateError("No more questions available")
        
        # Get current question
        question_text = role.questions[session.current_question_index]
        
        # Store current question for this session
        self._current_questions[session.session_id] = question_text
        
        # Create question message
        question_msg = Message(
            type=MessageType.QUESTION,
            content=question_text,
            timestamp=datetime.now()
        )
        
        # Add to session messages
        session.messages.append(question_msg)
        
        # Format question with context
        persona = self._session_personas.get(session.session_id)
        formatted_question = self.prompt_generator.format_question_with_context(
            question=question_text,
            question_number=session.current_question_index + 1,
            total_questions=len(role.questions),
            persona=persona.type if persona else None
        )
        
        return formatted_question
    
    def process_answer(
        self,
        session_id: UUID,
        answer: str
    ) -> Dict[str, any]:
        """
        Process user's answer and determine next action.
        
        This method:
        1. Saves the answer to session history
        2. Detects user persona
        3. Determines if follow-up is needed
        4. Returns appropriate response (follow-up or next question)
        
        Args:
            session_id: Session identifier
            answer: User's answer text
            
        Returns:
            Dictionary with response information:
            {
                "type": "followup" | "question" | "complete",
                "content": str,
                "question_number": int,
                "persona": Persona (optional)
            }
            
        Raises:
            SessionNotFoundError: If session doesn't exist
            InvalidSessionStateError: If session is not active
        """
        session = self._get_session(session_id)
        
        # Validate session state
        if session.status != SessionStatus.ACTIVE:
            raise InvalidSessionStateError("Session is not active")
        
        # Validate answer
        if not answer or not answer.strip():
            raise ValueError("Answer cannot be empty")
        
        # Save answer to session
        answer_msg = Message(
            type=MessageType.ANSWER,
            content=answer.strip(),
            timestamp=datetime.now()
        )
        session.messages.append(answer_msg)
        
        # Detect persona
        previous_persona = self._session_personas.get(session_id)
        detected_persona = self.persona_handler.detect_persona(
            answer=answer,
            conversation_history=session.messages,
            previous_persona=previous_persona.type if previous_persona else None
        )
        self._session_personas[session_id] = detected_persona
        
        # Get current question
        current_question = self._current_questions.get(session_id, "")
        
        # Determine if follow-up is needed
        should_followup, followup_question = self.should_ask_followup(
            session_id=session_id,
            answer=answer,
            question=current_question
        )
        
        if should_followup and followup_question:
            # Increment follow-up count
            session.followup_count += 1
            
            # Create follow-up message
            followup_msg = Message(
                type=MessageType.FOLLOWUP,
                content=followup_question,
                timestamp=datetime.now()
            )
            session.messages.append(followup_msg)
            
            # Adapt response for persona
            adapted_followup = self.persona_handler.adapt_response(
                response=followup_question,
                persona=detected_persona
            )
            
            return {
                "type": "followup",
                "content": adapted_followup,
                "question_number": session.current_question_index + 1,
                "persona": detected_persona
            }
        
        # Move to next question
        session.current_question_index += 1
        session.followup_count = 0  # Reset follow-up count for new question
        
        # Check if interview is complete
        role = self.role_loader.get_role(session.role)
        if session.current_question_index >= len(role.questions):
            return {
                "type": "complete",
                "content": self.prompt_generator.generate_completion_message(),
                "question_number": session.current_question_index,
                "persona": detected_persona
            }
        
        # Get next question
        try:
            next_question = self.get_next_question(session_id)
            
            # Add transition message
            transition = self.prompt_generator.generate_transition_message(
                from_question_num=session.current_question_index,
                to_question_num=session.current_question_index + 1
            )
            
            full_response = f"{transition}\n\n{next_question}"
            
            return {
                "type": "question",
                "content": full_response,
                "question_number": session.current_question_index + 1,
                "persona": detected_persona
            }
        except InvalidSessionStateError:
            # No more questions
            return {
                "type": "complete",
                "content": self.prompt_generator.generate_completion_message(),
                "question_number": session.current_question_index,
                "persona": detected_persona
            }
    
    def should_ask_followup(
        self,
        session_id: UUID,
        answer: str,
        question: str
    ) -> Tuple[bool, Optional[str]]:
        """
        Determine if a follow-up question should be asked.
        
        Uses LLM to analyze answer completeness and generate follow-up if needed.
        Enforces max 3 follow-ups per question rule.
        
        Args:
            session_id: Session identifier
            answer: User's answer
            question: Original question that was asked
            
        Returns:
            Tuple of (should_ask_followup: bool, followup_question: Optional[str])
            
        Raises:
            SessionNotFoundError: If session doesn't exist
        """
        session = self._get_session(session_id)
        
        # Check if we've reached max follow-ups
        if session.followup_count >= self.MAX_FOLLOWUPS_PER_QUESTION:
            return False, None
        
        # Get role for context
        role = self.role_loader.get_role(session.role)
        if not role:
            return False, None
        
        # Generate follow-up analysis prompt
        followup_prompt = self.prompt_generator.generate_followup_prompt(
            role=role,
            question=question,
            answer=answer
        )
        
        try:
            # Use LLM to determine if follow-up is needed
            response = self.ollama_client.generate(
                prompt=followup_prompt,
                temperature=0.7
            )
            
            response_clean = response.strip()
            
            # Check if LLM says answer is complete
            if "COMPLETE" in response_clean.upper():
                return False, None
            
            # Otherwise, use the response as follow-up question
            # Remove any "COMPLETE" text if it appears with other content
            if "COMPLETE" in response_clean.upper():
                # Extract just the question part
                lines = response_clean.split('\n')
                followup_lines = [
                    line for line in lines
                    if "COMPLETE" not in line.upper() and line.strip()
                ]
                if followup_lines:
                    followup_question = '\n'.join(followup_lines).strip()
                else:
                    return False, None
            else:
                followup_question = response_clean
            
            # Validate we got a reasonable follow-up question
            if len(followup_question) < 10:
                return False, None
            
            return True, followup_question
            
        except OllamaClientError as e:
            # If LLM fails, default to no follow-up
            print(f"Warning: Failed to generate follow-up: {e}")
            return False, None
    
    def end_session(self, session_id: UUID) -> Session:
        """
        Finalize and complete an interview session.
        
        Args:
            session_id: Session identifier
            
        Returns:
            Completed Session object
            
        Raises:
            SessionNotFoundError: If session doesn't exist
        """
        session = self._get_session(session_id)
        
        # Mark session as completed
        session.status = SessionStatus.COMPLETED
        
        return session
    
    def get_session(self, session_id: UUID) -> Session:
        """
        Retrieve a session by ID.
        
        Args:
            session_id: Session identifier
            
        Returns:
            Session object
            
        Raises:
            SessionNotFoundError: If session doesn't exist
        """
        return self._get_session(session_id)
    
    def get_session_transcript(self, session_id: UUID) -> List[Dict[str, str]]:
        """
        Get formatted transcript of session messages.
        
        Args:
            session_id: Session identifier
            
        Returns:
            List of message dictionaries with 'type' and 'content'
            
        Raises:
            SessionNotFoundError: If session doesn't exist
        """
        session = self._get_session(session_id)
        
        transcript = []
        for message in session.messages:
            transcript.append({
                "type": message.type.value,
                "content": message.content,
                "timestamp": message.timestamp.isoformat()
            })
        
        return transcript
    
    def get_session_persona(self, session_id: UUID) -> Optional[Persona]:
        """
        Get detected persona for a session.
        
        Args:
            session_id: Session identifier
            
        Returns:
            Persona object or None if not detected
        """
        return self._session_personas.get(session_id)
    
    def _get_session(self, session_id: UUID) -> Session:
        """
        Internal method to retrieve session with error handling.
        
        Args:
            session_id: Session identifier
            
        Returns:
            Session object
            
        Raises:
            SessionNotFoundError: If session doesn't exist
        """
        if session_id not in self._sessions:
            raise SessionNotFoundError(f"Session {session_id} not found")
        
        return self._sessions[session_id]
    
    def list_active_sessions(self) -> List[Session]:
        """
        Get list of all active sessions.
        
        Returns:
            List of active Session objects
        """
        return [
            session for session in self._sessions.values()
            if session.status == SessionStatus.ACTIVE
        ]
    
    def list_completed_sessions(self) -> List[Session]:
        """
        Get list of all completed sessions.
        
        Returns:
            List of completed Session objects
        """
        return [
            session for session in self._sessions.values()
            if session.status == SessionStatus.COMPLETED
        ]
    
    def get_session_progress(self, session_id: UUID) -> Dict[str, any]:
        """
        Get progress information for a session.
        
        Args:
            session_id: Session identifier
            
        Returns:
            Dictionary with progress information
            
        Raises:
            SessionNotFoundError: If session doesn't exist
        """
        session = self._get_session(session_id)
        role = self.role_loader.get_role(session.role)
        
        total_questions = len(role.questions) if role else 0
        current_question = session.current_question_index + 1
        
        return {
            "session_id": str(session.session_id),
            "role": session.role,
            "current_question": current_question,
            "total_questions": total_questions,
            "progress_percentage": round((current_question / total_questions * 100), 1) if total_questions > 0 else 0,
            "followup_count": session.followup_count,
            "status": session.status.value
        }
