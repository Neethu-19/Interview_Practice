"""
Persona Handler Service

Detects user personas based on interaction patterns and adapts responses accordingly.

Persona Types:
- Confused: Short answers, many questions, uncertainty
- Efficient: Direct, concise, requests to skip
- Chatty: Long answers, off-topic content
- Edge Case: Invalid inputs, out-of-scope requests
- Normal: Standard interview behavior
"""

from typing import List, Dict, Optional
import re
from models.data_models import Persona, PersonaType, Message, MessageType


class PersonaHandler:
    """
    Detects and handles different user personas during interviews.
    
    Analyzes user responses and conversation history to identify behavioral
    patterns and adapt the interview experience accordingly.
    """
    
    # Detection thresholds
    CONFUSED_SHORT_ANSWER_THRESHOLD = 30  # words
    CONFUSED_QUESTION_INDICATORS = [
        "what do you mean", "i don't understand", "can you explain",
        "i'm not sure", "i don't know", "could you clarify",
        "what does that mean", "i'm confused", "?"
    ]
    
    EFFICIENT_INDICATORS = [
        "let's move on", "next question", "skip", "keep it brief",
        "quickly", "short answer", "be direct", "get to the point"
    ]
    EFFICIENT_CONCISE_THRESHOLD = 50  # words
    
    CHATTY_LONG_ANSWER_THRESHOLD = 200  # words
    CHATTY_OFF_TOPIC_INDICATORS = [
        "by the way", "speaking of", "that reminds me",
        "on a different note", "another thing",
        "let me tell you about", "i remember when",
        "on another note", "this reminds me"
    ]
    
    EDGE_CASE_INDICATORS = [
        "hack", "cheat", "skip all", "give me answers",
        "what's the password", "admin", "bypass",
        "tell me the questions", "show me feedback now",
        "give me the answer", "just give me"
    ]
    EDGE_CASE_INVALID_PATTERNS = [
        r"^[^a-zA-Z0-9\s]{10,}$",  # Only special characters
        r"^(.)\1{20,}$",  # Repeated character spam
        r"^[0-9]{50,}$",  # Only numbers (excessive)
    ]
    
    def __init__(self):
        """Initialize the PersonaHandler."""
        pass
    
    def detect_persona(
        self,
        answer: str,
        conversation_history: List[Message],
        previous_persona: Optional[PersonaType] = None
    ) -> Persona:
        """
        Detect user persona based on current answer and conversation history.
        
        Args:
            answer: Current user answer
            conversation_history: List of previous messages in the session
            previous_persona: Previously detected persona (for consistency)
            
        Returns:
            Persona object with type, confidence, and indicators
        """
        answer_lower = answer.lower().strip()
        word_count = len(answer.split())
        
        # Track all detection scores
        # Note: Edge case is checked first as it should take priority
        detection_scores = {
            PersonaType.EDGE_CASE: self._detect_edge_case(answer, answer_lower),
            PersonaType.CONFUSED: self._detect_confused(answer, answer_lower, word_count, conversation_history),
            PersonaType.CHATTY: self._detect_chatty(answer, answer_lower, word_count),
            PersonaType.EFFICIENT: self._detect_efficient(answer, answer_lower, word_count, conversation_history),
        }
        
        # Edge case takes priority if detected with reasonable confidence
        if detection_scores[PersonaType.EDGE_CASE]["confidence"] >= 0.4:
            edge_data = detection_scores[PersonaType.EDGE_CASE]
            return Persona(
                type=PersonaType.EDGE_CASE,
                confidence=edge_data["confidence"],
                indicators=edge_data["indicators"]
            )
        
        # Find highest scoring persona among remaining types
        max_score = max(detection_scores.values(), key=lambda x: x["confidence"])
        
        # If confidence is low, default to NORMAL
        if max_score["confidence"] < 0.3:
            return Persona(
                type=PersonaType.NORMAL,
                confidence=0.8,
                indicators=["standard_interaction_pattern"]
            )
        
        # Apply persona consistency bonus if previous persona matches
        if previous_persona and previous_persona in detection_scores:
            detection_scores[previous_persona]["confidence"] *= 1.2
            detection_scores[previous_persona]["confidence"] = min(
                detection_scores[previous_persona]["confidence"], 1.0
            )
        
        # Select persona with highest confidence
        detected_type = max(detection_scores.keys(), key=lambda k: detection_scores[k]["confidence"])
        detected_data = detection_scores[detected_type]
        
        return Persona(
            type=detected_type,
            confidence=detected_data["confidence"],
            indicators=detected_data["indicators"]
        )
    
    def _detect_confused(
        self,
        answer: str,
        answer_lower: str,
        word_count: int,
        history: List[Message]
    ) -> Dict:
        """
        Detect Confused persona indicators.
        
        Indicators:
        - Very short answers (< 30 words)
        - Questions in response
        - Uncertainty phrases
        - Pattern of short answers in history
        """
        indicators = []
        confidence = 0.0
        
        # Check for short answer
        if word_count < self.CONFUSED_SHORT_ANSWER_THRESHOLD:
            indicators.append("short_answer")
            confidence += 0.3
        
        # Check for question marks (asking questions back)
        question_count = answer.count("?")
        if question_count > 0:
            indicators.append(f"asking_questions ({question_count})")
            confidence += 0.2 * min(question_count, 3)
        
        # Check for confusion indicators
        confusion_phrases = [
            phrase for phrase in self.CONFUSED_QUESTION_INDICATORS
            if phrase in answer_lower
        ]
        if confusion_phrases:
            indicators.append(f"uncertainty_phrases: {', '.join(confusion_phrases[:2])}")
            confidence += 0.3 * min(len(confusion_phrases), 2)
        
        # Check history for pattern of short answers
        recent_answers = [
            msg for msg in history[-6:]
            if msg.type == MessageType.ANSWER
        ]
        if len(recent_answers) >= 2:
            short_answer_count = sum(
                1 for msg in recent_answers
                if len(msg.content.split()) < self.CONFUSED_SHORT_ANSWER_THRESHOLD
            )
            if short_answer_count >= 2:
                indicators.append("pattern_of_short_answers")
                confidence += 0.2
        
        return {
            "confidence": min(confidence, 1.0),
            "indicators": indicators if indicators else ["none"]
        }
    
    def _detect_efficient(
        self,
        answer: str,
        answer_lower: str,
        word_count: int,
        history: List[Message]
    ) -> Dict:
        """
        Detect Efficient persona indicators.
        
        Indicators:
        - Direct, concise answers (30-50 words)
        - Requests to move quickly
        - Consistent brevity
        - No unnecessary elaboration
        """
        indicators = []
        confidence = 0.0
        
        # Check for efficient language
        efficient_phrases = [
            phrase for phrase in self.EFFICIENT_INDICATORS
            if phrase in answer_lower
        ]
        if efficient_phrases:
            indicators.append(f"efficiency_requests: {', '.join(efficient_phrases[:2])}")
            confidence += 0.4
        
        # Check for concise but complete answers
        if self.CONFUSED_SHORT_ANSWER_THRESHOLD <= word_count <= self.EFFICIENT_CONCISE_THRESHOLD:
            indicators.append("concise_answer")
            confidence += 0.3
        
        # Check history for consistent brevity
        recent_answers = [
            msg for msg in history[-6:]
            if msg.type == MessageType.ANSWER
        ]
        if len(recent_answers) >= 2:
            concise_count = sum(
                1 for msg in recent_answers
                if self.CONFUSED_SHORT_ANSWER_THRESHOLD <= len(msg.content.split()) <= self.EFFICIENT_CONCISE_THRESHOLD
            )
            if concise_count >= 2:
                indicators.append("consistent_brevity")
                confidence += 0.3
        
        # Check for direct structure (no fluff)
        filler_words = ["um", "uh", "like", "you know", "basically", "actually"]
        filler_count = sum(1 for word in filler_words if word in answer_lower)
        if filler_count == 0 and word_count >= 20:
            indicators.append("direct_communication")
            confidence += 0.2
        
        return {
            "confidence": min(confidence, 1.0),
            "indicators": indicators if indicators else ["none"]
        }
    
    def _detect_chatty(
        self,
        answer: str,
        answer_lower: str,
        word_count: int
    ) -> Dict:
        """
        Detect Chatty persona indicators.
        
        Indicators:
        - Very long answers (> 200 words)
        - Off-topic content
        - Multiple tangents
        - Excessive detail
        """
        indicators = []
        confidence = 0.0
        
        # Check for long answer
        if word_count > self.CHATTY_LONG_ANSWER_THRESHOLD:
            indicators.append(f"long_answer ({word_count} words)")
            # Scale confidence with length
            excess_words = word_count - self.CHATTY_LONG_ANSWER_THRESHOLD
            confidence += 0.3 + min(excess_words / 200, 0.3)
        
        # Check for off-topic indicators
        off_topic_phrases = [
            phrase for phrase in self.CHATTY_OFF_TOPIC_INDICATORS
            if phrase in answer_lower
        ]
        if off_topic_phrases:
            indicators.append(f"tangential_content: {', '.join(off_topic_phrases[:2])}")
            confidence += 0.3 * min(len(off_topic_phrases), 2)
        
        # Check for multiple sentences (excessive elaboration)
        sentence_count = len([s for s in re.split(r'[.!?]+', answer) if s.strip()])
        if sentence_count > 10:
            indicators.append(f"excessive_elaboration ({sentence_count} sentences)")
            confidence += 0.2
        
        # Check for storytelling patterns
        story_indicators = ["i remember", "one time", "there was", "let me tell you"]
        story_count = sum(1 for phrase in story_indicators if phrase in answer_lower)
        if story_count > 0:
            indicators.append("storytelling_pattern")
            confidence += 0.2
        
        return {
            "confidence": min(confidence, 1.0),
            "indicators": indicators if indicators else ["none"]
        }
    
    def _detect_edge_case(
        self,
        answer: str,
        answer_lower: str
    ) -> Dict:
        """
        Detect Edge Case persona indicators.
        
        Indicators:
        - Invalid or malicious inputs
        - Out-of-scope requests
        - System manipulation attempts
        - Nonsensical content
        """
        indicators = []
        confidence = 0.0
        
        # Check for edge case keywords
        edge_phrases = [
            phrase for phrase in self.EDGE_CASE_INDICATORS
            if phrase in answer_lower
        ]
        if edge_phrases:
            indicators.append(f"suspicious_requests: {', '.join(edge_phrases[:2])}")
            confidence += 0.5
        
        # Check for invalid patterns
        for pattern in self.EDGE_CASE_INVALID_PATTERNS:
            if re.match(pattern, answer):
                indicators.append("invalid_input_pattern")
                confidence += 0.6
                break
        
        # Check for empty or whitespace-only (shouldn't reach here due to validation)
        if not answer.strip():
            indicators.append("empty_input")
            confidence += 0.8
        
        # Check for extremely short nonsensical input
        if len(answer.strip()) < 3:
            indicators.append("too_short")
            confidence += 0.5
        
        # Check for repeated words (spam)
        words = answer_lower.split()
        if len(words) > 5:
            unique_words = set(words)
            if len(unique_words) / len(words) < 0.3:
                indicators.append("repetitive_spam")
                confidence += 0.4
        
        return {
            "confidence": min(confidence, 1.0),
            "indicators": indicators if indicators else ["none"]
        }
    
    def adapt_response(
        self,
        response: str,
        persona: Persona
    ) -> str:
        """
        Adapt a response based on detected persona.
        
        Args:
            response: Original response text
            persona: Detected persona with type and confidence
            
        Returns:
            Adapted response text
        """
        # Only adapt if confidence is reasonably high
        if persona.confidence < 0.4 or persona.type == PersonaType.NORMAL:
            return response
        
        if persona.type == PersonaType.CONFUSED:
            return self._adapt_for_confused(response)
        elif persona.type == PersonaType.EFFICIENT:
            return self._adapt_for_efficient(response)
        elif persona.type == PersonaType.CHATTY:
            return self._adapt_for_chatty(response)
        elif persona.type == PersonaType.EDGE_CASE:
            return self._adapt_for_edge_case(response)
        
        return response
    
    def _adapt_for_confused(self, response: str) -> str:
        """
        Adapt response for Confused persona.
        
        Adds guidance, examples, and encouragement.
        """
        prefix = "I notice you might need some guidance. "
        suffix = " Take your time and feel free to ask if anything is unclear."
        
        # Add helpful framing
        adapted = f"{prefix}{response}{suffix}"
        
        return adapted
    
    def _adapt_for_efficient(self, response: str) -> str:
        """
        Adapt response for Efficient persona.
        
        Keeps it concise and direct, removes unnecessary pleasantries.
        """
        # Remove common pleasantries
        response = response.replace("Thank you for that response. ", "")
        response = response.replace("I appreciate your answer. ", "")
        response = response.replace("That's great. ", "")
        response = response.replace("Excellent. ", "")
        
        # Keep it direct
        return response.strip()
    
    def _adapt_for_chatty(self, response: str) -> str:
        """
        Adapt response for Chatty persona.
        
        Politely redirects to stay focused.
        """
        prefix = "Thank you for sharing. "
        redirect = "Let's focus on the key point: "
        suffix = " Please keep your response focused on this specific aspect."
        
        adapted = f"{prefix}{redirect}{response}{suffix}"
        
        return adapted
    
    def _adapt_for_edge_case(self, response: str) -> str:
        """
        Adapt response for Edge Case persona.
        
        Sets clear boundaries and provides guidance.
        """
        prefix = "I understand your concern. However, "
        suffix = " Let's stay within the scope of the interview. Please provide a relevant answer to the question."
        
        adapted = f"{prefix}{response}{suffix}"
        
        return adapted
    
    def get_persona_guidance(self, persona: Persona) -> Optional[str]:
        """
        Get guidance message for a detected persona.
        
        Args:
            persona: Detected persona
            
        Returns:
            Guidance message or None if not needed
        """
        if persona.confidence < 0.5 or persona.type == PersonaType.NORMAL:
            return None
        
        guidance = {
            PersonaType.CONFUSED: (
                "I'm here to help! If any question is unclear, feel free to ask for "
                "clarification or examples. Take your time with your answers."
            ),
            PersonaType.EFFICIENT: (
                "I appreciate your direct communication style. I'll keep my questions "
                "focused and move efficiently through the interview."
            ),
            PersonaType.CHATTY: (
                "I appreciate your enthusiasm! To make the best use of our time, "
                "please try to keep your answers focused on the specific question asked."
            ),
            PersonaType.EDGE_CASE: (
                "Please provide relevant answers to the interview questions. "
                "If you have concerns about the interview format, let me know, "
                "but let's stay focused on the interview content."
            )
        }
        
        return guidance.get(persona.type)
    
    def should_provide_extra_guidance(self, persona: Persona) -> bool:
        """
        Determine if extra guidance should be provided based on persona.
        
        Args:
            persona: Detected persona
            
        Returns:
            True if extra guidance is recommended
        """
        return (
            persona.type == PersonaType.CONFUSED and
            persona.confidence >= 0.5
        )
    
    def should_skip_pleasantries(self, persona: Persona) -> bool:
        """
        Determine if pleasantries should be skipped based on persona.
        
        Args:
            persona: Detected persona
            
        Returns:
            True if pleasantries should be minimized
        """
        return (
            persona.type == PersonaType.EFFICIENT and
            persona.confidence >= 0.5
        )
    
    def should_redirect_focus(self, persona: Persona) -> bool:
        """
        Determine if response should include focus redirection.
        
        Args:
            persona: Detected persona
            
        Returns:
            True if redirection is recommended
        """
        return (
            persona.type == PersonaType.CHATTY and
            persona.confidence >= 0.5
        )
