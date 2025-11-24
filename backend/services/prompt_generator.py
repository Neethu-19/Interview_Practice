"""
Prompt Generator Service

Generates prompts for different stages of the interview process:
- System prompts for interviewer persona
- Follow-up question generation prompts
- Feedback evaluation prompts with scoring rubric
- Persona-specific prompt adaptations
"""

from typing import Dict, List, Optional
from models.data_models import PersonaType, Role


class PromptGenerator:
    """
    Generates context-aware prompts for the interview system.
    
    Handles prompt generation for:
    - Interviewer system prompts
    - Follow-up question generation
    - Feedback evaluation
    - Persona-specific adaptations
    """
    
    # System prompt templates
    INTERVIEWER_SYSTEM_PROMPT = """You are an expert interview coach conducting a {role_display_name} interview.

Your responsibilities:
1. Ask clear, role-specific questions that assess the candidate's qualifications
2. Listen carefully to responses and evaluate their completeness
3. Ask follow-up questions when answers lack detail or clarity
4. Maintain a professional yet friendly and encouraging tone
5. Help candidates demonstrate their best abilities

Current context:
- Role: {role_display_name}
- Question: {question}

Guidelines:
- Be conversational and natural, not robotic
- Acknowledge responses briefly before moving forward
- Keep the interview flowing smoothly
- Focus on helping the candidate succeed"""

    FOLLOWUP_ANALYSIS_PROMPT = """You are evaluating a candidate's response in a {role_display_name} interview.

Question asked: {question}

Candidate's answer: {answer}

Analyze this answer for:
1. Completeness - Does it fully address all aspects of the question?
2. Depth - Does it provide specific examples or details?
3. Clarity - Is it well-structured and easy to understand?
4. Relevance - Does it stay on topic?

Based on your analysis:
- If the answer is complete, detailed, and clear, respond with exactly: "COMPLETE"
- If the answer needs more detail, is vague, or raises interesting points to explore, generate ONE specific follow-up question

Follow-up question guidelines:
- Ask about specific aspects that were mentioned but not elaborated
- Request examples if the answer was too theoretical
- Clarify ambiguous statements
- Explore interesting points that deserve deeper discussion
- Keep it conversational and encouraging

Respond with either "COMPLETE" or a single follow-up question."""

    FEEDBACK_GENERATION_PROMPT = """You are an expert interview evaluator providing constructive feedback for a {role_display_name} interview.

Interview Transcript:
{transcript}

Evaluation Criteria for {role_display_name}:
{evaluation_criteria}

Provide a comprehensive performance evaluation in the following JSON format:

{{
  "scores": {{
    "communication": <1-5>,
    "technical_knowledge": <1-5>,
    "structure": <1-5>
  }},
  "strengths": [
    "<specific strength 1>",
    "<specific strength 2>",
    "<specific strength 3>"
  ],
  "improvements": [
    "<actionable improvement 1>",
    "<actionable improvement 2>",
    "<actionable improvement 3>"
  ],
  "overall_feedback": "<2-3 sentence summary of performance>"
}}

Scoring Guidelines:
- Communication (1-5): Clarity, conciseness, articulation, professional language
  * 5: Exceptionally clear and articulate
  * 4: Clear and well-expressed
  * 3: Adequate communication with minor issues
  * 2: Unclear or verbose
  * 1: Very difficult to understand

- Technical Knowledge (1-5): Accuracy, depth, relevance to role
  * 5: Expert-level knowledge with deep insights
  * 4: Strong knowledge with good understanding
  * 3: Adequate knowledge for the role
  * 2: Limited knowledge with gaps
  * 1: Insufficient knowledge

- Structure (1-5): Organization, use of examples, completeness
  * 5: Perfectly structured with excellent examples
  * 4: Well-organized with good examples
  * 3: Adequately structured
  * 2: Poorly organized or incomplete
  * 1: Disorganized and incomplete

Requirements:
- Provide exactly 3 strengths and 3 improvements
- Make improvements actionable with specific advice
- Base scores on actual performance, not potential
- Be constructive and encouraging while honest
- Reference specific examples from the interview"""

    # Persona-specific adaptations
    PERSONA_ADAPTATIONS = {
        PersonaType.CONFUSED: {
            "prefix": "I notice you might need some guidance. ",
            "style": "Let me help clarify: ",
            "suffix": " Take your time and feel free to ask if anything is unclear."
        },
        PersonaType.EFFICIENT: {
            "prefix": "",
            "style": "",
            "suffix": ""
        },
        PersonaType.CHATTY: {
            "prefix": "Thank you for sharing. ",
            "style": "Let's focus on the key point: ",
            "suffix": " Please keep your response focused on this specific aspect."
        },
        PersonaType.EDGE_CASE: {
            "prefix": "I understand your concern. ",
            "style": "However, ",
            "suffix": " Let's stay within the scope of the interview."
        },
        PersonaType.NORMAL: {
            "prefix": "",
            "style": "",
            "suffix": ""
        }
    }
    
    def __init__(self):
        """Initialize the PromptGenerator."""
        pass
    
    def generate_interviewer_prompt(
        self,
        role: Role,
        question: str,
        persona: Optional[PersonaType] = None
    ) -> str:
        """
        Generate system prompt for the interviewer persona.
        
        Args:
            role: Role object containing role information
            question: Current interview question
            persona: Optional detected user persona for adaptation
            
        Returns:
            Formatted system prompt string
        """
        base_prompt = self.INTERVIEWER_SYSTEM_PROMPT.format(
            role_display_name=role.display_name,
            question=question
        )
        
        # Add persona-specific adaptations if needed
        if persona and persona != PersonaType.NORMAL:
            adaptation = self._get_persona_adaptation_note(persona)
            base_prompt += f"\n\n{adaptation}"
        
        return base_prompt
    
    def generate_followup_prompt(
        self,
        role: Role,
        question: str,
        answer: str
    ) -> str:
        """
        Generate prompt for follow-up question analysis.
        
        Args:
            role: Role object containing role information
            question: The question that was asked
            answer: The candidate's answer
            
        Returns:
            Formatted prompt for follow-up analysis
        """
        return self.FOLLOWUP_ANALYSIS_PROMPT.format(
            role_display_name=role.display_name,
            question=question,
            answer=answer
        )
    
    def generate_feedback_prompt(
        self,
        role: Role,
        transcript: List[Dict[str, str]]
    ) -> str:
        """
        Generate prompt for feedback evaluation.
        
        Args:
            role: Role object containing role information
            transcript: List of conversation messages (question/answer pairs)
            
        Returns:
            Formatted prompt for feedback generation
        """
        # Format transcript for readability
        formatted_transcript = self._format_transcript(transcript)
        
        # Format evaluation criteria
        formatted_criteria = self._format_evaluation_criteria(role.evaluation_criteria)
        
        return self.FEEDBACK_GENERATION_PROMPT.format(
            role_display_name=role.display_name,
            transcript=formatted_transcript,
            evaluation_criteria=formatted_criteria
        )
    
    def adapt_response_for_persona(
        self,
        response: str,
        persona: PersonaType
    ) -> str:
        """
        Adapt a response based on detected user persona.
        
        Args:
            response: Original response text
            persona: Detected user persona
            
        Returns:
            Adapted response text
        """
        if persona == PersonaType.NORMAL or persona not in self.PERSONA_ADAPTATIONS:
            return response
        
        adaptation = self.PERSONA_ADAPTATIONS[persona]
        
        # Apply persona-specific formatting
        adapted = ""
        if adaptation["prefix"]:
            adapted += adaptation["prefix"]
        
        if adaptation["style"]:
            adapted += adaptation["style"]
        
        adapted += response
        
        if adaptation["suffix"]:
            adapted += adaptation["suffix"]
        
        return adapted
    
    def format_question_with_context(
        self,
        question: str,
        question_number: int,
        total_questions: int,
        persona: Optional[PersonaType] = None
    ) -> str:
        """
        Format a question with contextual information.
        
        Args:
            question: The question text
            question_number: Current question number (1-indexed)
            total_questions: Total number of questions
            persona: Optional detected user persona
            
        Returns:
            Formatted question with context
        """
        # Add question number context
        context = f"Question {question_number} of {total_questions}:\n\n"
        formatted = context + question
        
        # Add persona-specific guidance if needed
        if persona == PersonaType.CONFUSED:
            formatted += "\n\n(Take your time to think through your answer. Feel free to ask for clarification if needed.)"
        elif persona == PersonaType.CHATTY:
            formatted += "\n\n(Please provide a focused response addressing the key points.)"
        
        return formatted
    
    def _format_transcript(self, transcript: List[Dict[str, str]]) -> str:
        """
        Format conversation transcript for prompt inclusion.
        
        Args:
            transcript: List of message dictionaries with 'type' and 'content'
            
        Returns:
            Formatted transcript string
        """
        formatted_lines = []
        
        for i, message in enumerate(transcript, 1):
            msg_type = message.get("type", "unknown")
            content = message.get("content", "")
            
            if msg_type == "question" or msg_type == "followup":
                formatted_lines.append(f"\nInterviewer: {content}")
            elif msg_type == "answer":
                formatted_lines.append(f"Candidate: {content}")
        
        return "\n".join(formatted_lines)
    
    def _format_evaluation_criteria(self, criteria: Dict) -> str:
        """
        Format evaluation criteria for prompt inclusion.
        
        Args:
            criteria: Dictionary of evaluation criteria
            
        Returns:
            Formatted criteria string
        """
        formatted_lines = []
        
        for category, details in criteria.items():
            formatted_lines.append(f"\n{category.replace('_', ' ').title()}:")
            
            if isinstance(details, dict):
                for key, value in details.items():
                    formatted_lines.append(f"  - {key}: {value}")
            elif isinstance(details, list):
                for item in details:
                    formatted_lines.append(f"  - {item}")
            else:
                formatted_lines.append(f"  {details}")
        
        return "\n".join(formatted_lines)
    
    def _get_persona_adaptation_note(self, persona: PersonaType) -> str:
        """
        Get adaptation note for system prompt based on persona.
        
        Args:
            persona: Detected user persona
            
        Returns:
            Adaptation note string
        """
        notes = {
            PersonaType.CONFUSED: (
                "Note: The candidate seems uncertain or confused. "
                "Provide extra guidance, break down complex questions, "
                "and offer examples to help them understand what you're looking for."
            ),
            PersonaType.EFFICIENT: (
                "Note: The candidate prefers efficient, direct communication. "
                "Be concise, skip unnecessary pleasantries, and focus on core questions."
            ),
            PersonaType.CHATTY: (
                "Note: The candidate tends to provide lengthy or off-topic responses. "
                "Politely redirect them to stay focused on the question at hand. "
                "Acknowledge their enthusiasm while guiding them back on track."
            ),
            PersonaType.EDGE_CASE: (
                "Note: The candidate may provide unusual inputs or requests. "
                "Set clear boundaries, explain what's within scope, "
                "and guide them back to the interview format."
            )
        }
        
        return notes.get(persona, "")
    
    def generate_intro_message(self, role: Role, mode: str) -> str:
        """
        Generate welcoming introduction message for interview start.
        
        Args:
            role: Role object for the interview
            mode: Interaction mode (chat or voice)
            
        Returns:
            Introduction message
        """
        mode_text = "voice" if mode == "voice" else "chat"
        
        intro = f"""Welcome to your {role.display_name} interview practice session!

I'll be conducting a mock interview with you today. I'll ask you a series of questions about the role, and you can answer as you would in a real interview. Feel free to take your time with your responses.

After each answer, I may ask follow-up questions to dive deeper into your responses, just like in a real interview. At the end, you'll receive detailed feedback on your performance.

We'll be using {mode_text} mode for this session. Ready to begin?"""
        
        return intro
    
    def generate_transition_message(
        self,
        from_question_num: int,
        to_question_num: int
    ) -> str:
        """
        Generate smooth transition message between questions.
        
        Args:
            from_question_num: Previous question number
            to_question_num: Next question number
            
        Returns:
            Transition message
        """
        transitions = [
            "Great, let's move on to the next question.",
            "Thank you for that response. Let's continue.",
            "Excellent. Now, let's discuss another aspect.",
            "I appreciate your answer. Moving forward,",
            "That's helpful. Let's explore another area."
        ]
        
        # Use question number to deterministically select transition
        # This provides variety while being consistent
        index = (from_question_num + to_question_num) % len(transitions)
        return transitions[index]
    
    def generate_completion_message(self) -> str:
        """
        Generate message for interview completion.
        
        Returns:
            Completion message
        """
        return """Thank you for completing the interview! 

You've answered all the questions. I'll now generate detailed feedback on your performance, including scores for communication, technical knowledge, and structure, along with specific strengths and areas for improvement.

Please wait a moment while I prepare your feedback..."""
