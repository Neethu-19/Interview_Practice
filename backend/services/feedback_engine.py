"""
Feedback Engine Service

Generates comprehensive performance feedback for interview sessions.
Uses LLM to evaluate responses and provide structured feedback with scores,
strengths, and actionable improvements.
"""

import time
from typing import List, Dict, Optional
from uuid import UUID
from models.data_models import FeedbackReport, Scores, Role, Message
from services.ollama_client import OllamaClient, OllamaClientError
from services.prompt_generator import PromptGenerator


class FeedbackEngineError(Exception):
    """Base exception for feedback engine errors"""
    pass


class FeedbackTimeoutError(FeedbackEngineError):
    """Raised when feedback generation exceeds time limit"""
    pass


class FeedbackValidationError(FeedbackEngineError):
    """Raised when generated feedback fails validation"""
    pass


class FeedbackEngine:
    """
    Generates structured performance feedback for interview sessions.
    
    Uses LLM to analyze interview transcripts and produce:
    - Scores for communication, technical knowledge, and structure (1-5)
    - Three specific strengths
    - Three actionable improvements
    - Overall performance summary
    """
    
    def __init__(
        self,
        ollama_client: OllamaClient,
        prompt_generator: PromptGenerator,
        timeout_seconds: int = 10,
        temperature: float = 0.3
    ):
        """
        Initialize the FeedbackEngine.
        
        Args:
            ollama_client: Client for LLM communication
            prompt_generator: Generator for feedback prompts
            timeout_seconds: Maximum time allowed for feedback generation (default: 10)
            temperature: LLM temperature for generation (default: 0.3 for consistency)
        """
        self.ollama_client = ollama_client
        self.prompt_generator = prompt_generator
        self.timeout_seconds = timeout_seconds
        self.temperature = temperature
    
    def generate_feedback(
        self,
        session_id: UUID,
        role: Role,
        transcript: List[Message]
    ) -> FeedbackReport:
        """
        Generate comprehensive feedback for an interview session.
        
        Args:
            session_id: UUID of the interview session
            role: Role object with evaluation criteria
            transcript: List of Message objects from the interview
            
        Returns:
            FeedbackReport with scores, strengths, improvements, and summary
            
        Raises:
            FeedbackTimeoutError: If generation exceeds timeout
            FeedbackValidationError: If generated feedback is invalid
            FeedbackEngineError: For other generation errors
        """
        start_time = time.time()
        
        try:
            # Convert Message objects to dict format for prompt generation
            transcript_dicts = [
                {
                    "type": msg.type.value,
                    "content": msg.content,
                    "timestamp": msg.timestamp.isoformat()
                }
                for msg in transcript
            ]
            
            # Generate feedback prompt
            prompt = self.prompt_generator.generate_feedback_prompt(
                role=role,
                transcript=transcript_dicts
            )
            
            # Generate structured feedback using LLM
            feedback_data = self.ollama_client.generate_structured(
                prompt=prompt,
                system="You are an expert interview evaluator. Provide constructive, specific feedback in valid JSON format.",
                temperature=self.temperature,
                max_tokens=1000
            )
            
            # Check timeout
            elapsed_time = time.time() - start_time
            if elapsed_time > self.timeout_seconds:
                raise FeedbackTimeoutError(
                    f"Feedback generation took {elapsed_time:.2f}s, exceeding {self.timeout_seconds}s limit"
                )
            
            # Parse and validate feedback
            feedback_report = self._parse_and_validate_feedback(
                session_id=session_id,
                feedback_data=feedback_data
            )
            
            return feedback_report
            
        except OllamaClientError as e:
            raise FeedbackEngineError(f"LLM generation failed: {e}") from e
        except Exception as e:
            raise FeedbackEngineError(f"Unexpected error during feedback generation: {e}") from e
    
    def _parse_and_validate_feedback(
        self,
        session_id: UUID,
        feedback_data: Dict
    ) -> FeedbackReport:
        """
        Parse LLM output into structured FeedbackReport and validate.
        
        Args:
            session_id: UUID of the session
            feedback_data: Dictionary from LLM output
            
        Returns:
            Validated FeedbackReport
            
        Raises:
            FeedbackValidationError: If feedback data is invalid
        """
        try:
            # Extract scores
            scores_data = feedback_data.get("scores", {})
            
            # Validate and clamp scores to 1-5 range
            communication_score = self._validate_score(
                scores_data.get("communication"),
                "communication"
            )
            technical_score = self._validate_score(
                scores_data.get("technical_knowledge"),
                "technical_knowledge"
            )
            structure_score = self._validate_score(
                scores_data.get("structure"),
                "structure"
            )
            
            scores = Scores(
                communication=communication_score,
                technical_knowledge=technical_score,
                structure=structure_score
            )
            
            # Extract and validate strengths
            strengths = feedback_data.get("strengths", [])
            if not isinstance(strengths, list):
                raise FeedbackValidationError("Strengths must be a list")
            
            # Ensure exactly 3 strengths
            strengths = self._ensure_three_items(
                strengths,
                "strength",
                "Strong performance demonstrated"
            )
            
            # Extract and validate improvements
            improvements = feedback_data.get("improvements", [])
            if not isinstance(improvements, list):
                raise FeedbackValidationError("Improvements must be a list")
            
            # Ensure exactly 3 improvements
            improvements = self._ensure_three_items(
                improvements,
                "improvement",
                "Continue practicing to refine your skills"
            )
            
            # Extract overall feedback
            overall_feedback = feedback_data.get("overall_feedback", "")
            if not overall_feedback or len(overall_feedback.strip()) < 50:
                # Generate fallback overall feedback
                overall_feedback = self._generate_fallback_overall_feedback(scores)
            
            # Create and validate FeedbackReport
            feedback_report = FeedbackReport(
                session_id=session_id,
                scores=scores,
                strengths=strengths,
                improvements=improvements,
                overall_feedback=overall_feedback.strip()
            )
            
            return feedback_report
            
        except ValueError as e:
            raise FeedbackValidationError(f"Invalid feedback data: {e}") from e
        except Exception as e:
            raise FeedbackValidationError(f"Failed to parse feedback: {e}") from e
    
    def _validate_score(self, score: Optional[int], score_name: str) -> int:
        """
        Validate and clamp score to 1-5 range.
        
        Args:
            score: Score value to validate
            score_name: Name of the score for error messages
            
        Returns:
            Valid score between 1 and 5
            
        Raises:
            FeedbackValidationError: If score is not a valid integer
        """
        if score is None:
            raise FeedbackValidationError(f"Missing {score_name} score")
        
        try:
            score_int = int(score)
        except (TypeError, ValueError):
            raise FeedbackValidationError(
                f"{score_name} score must be an integer, got {type(score)}"
            )
        
        # Clamp to 1-5 range
        if score_int < 1:
            return 1
        elif score_int > 5:
            return 5
        else:
            return score_int
    
    def _ensure_three_items(
        self,
        items: List[str],
        item_type: str,
        fallback_text: str
    ) -> List[str]:
        """
        Ensure list has exactly 3 non-empty items.
        
        Args:
            items: List of items to validate
            item_type: Type of item for fallback generation
            fallback_text: Text to use for missing items
            
        Returns:
            List with exactly 3 items
        """
        # Filter out empty items
        valid_items = [item.strip() for item in items if item and item.strip()]
        
        # If we have more than 3, take the first 3
        if len(valid_items) > 3:
            return valid_items[:3]
        
        # If we have fewer than 3, pad with fallback
        while len(valid_items) < 3:
            valid_items.append(f"{fallback_text} ({item_type} {len(valid_items) + 1})")
        
        return valid_items
    
    def _generate_fallback_overall_feedback(self, scores: Scores) -> str:
        """
        Generate fallback overall feedback based on scores.
        
        Args:
            scores: Scores object with performance scores
            
        Returns:
            Overall feedback string
        """
        avg_score = scores.average
        
        if avg_score >= 4.0:
            return (
                f"Excellent performance overall with an average score of {avg_score:.1f}/5. "
                "You demonstrated strong communication skills, solid technical knowledge, "
                "and well-structured responses. Keep up the great work!"
            )
        elif avg_score >= 3.0:
            return (
                f"Good performance with an average score of {avg_score:.1f}/5. "
                "You showed adequate skills across all areas with room for improvement. "
                "Focus on the specific areas mentioned to enhance your interview performance."
            )
        else:
            return (
                f"Your performance shows potential with an average score of {avg_score:.1f}/5. "
                "There are several areas that need improvement. Review the feedback carefully "
                "and practice addressing the specific points mentioned to strengthen your skills."
            )
    
    def calculate_scores_from_transcript(
        self,
        transcript: List[Message]
    ) -> Dict[str, float]:
        """
        Calculate basic metrics from transcript for debugging/analysis.
        
        Args:
            transcript: List of Message objects
            
        Returns:
            Dictionary with calculated metrics
        """
        answer_messages = [msg for msg in transcript if msg.type.value == "answer"]
        
        if not answer_messages:
            return {
                "total_answers": 0,
                "avg_answer_length": 0,
                "total_words": 0
            }
        
        total_words = sum(len(msg.content.split()) for msg in answer_messages)
        avg_length = total_words / len(answer_messages)
        
        return {
            "total_answers": len(answer_messages),
            "avg_answer_length": round(avg_length, 2),
            "total_words": total_words
        }
