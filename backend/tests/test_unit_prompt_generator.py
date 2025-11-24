"""
Unit tests for PromptGenerator
Tests prompt template rendering and formatting
"""
import pytest
from models.data_models import PersonaType


class TestInterviewerPrompt:
    """Test interviewer system prompt generation"""
    
    def test_basic_interviewer_prompt(self, prompt_generator, sample_role):
        """Test basic interviewer prompt without persona"""
        question = "Tell me about your experience."
        prompt = prompt_generator.generate_interviewer_prompt(sample_role, question)
        
        assert sample_role.display_name in prompt
        assert question in prompt
        assert "interview" in prompt.lower()
    
    def test_interviewer_prompt_with_confused_persona(self, prompt_generator, sample_role):
        """Test interviewer prompt adapted for Confused persona"""
        question = "Tell me about your experience."
        prompt = prompt_generator.generate_interviewer_prompt(
            sample_role, question, PersonaType.CONFUSED
        )
        
        assert "guidance" in prompt.lower() or "help" in prompt.lower()
    
    def test_interviewer_prompt_with_chatty_persona(self, prompt_generator, sample_role):
        """Test interviewer prompt adapted for Chatty persona"""
        question = "Tell me about your experience."
        prompt = prompt_generator.generate_interviewer_prompt(
            sample_role, question, PersonaType.CHATTY
        )
        
        assert "concise" in prompt.lower() or "focus" in prompt.lower()


class TestFollowupPrompt:
    """Test follow-up question generation prompts"""
    
    def test_followup_prompt_structure(self, prompt_generator, sample_role):
        """Test follow-up prompt contains necessary elements"""
        question = "Tell me about your experience."
        answer = "I have some experience."
        prompt = prompt_generator.generate_followup_prompt(sample_role, question, answer)
        
        assert question in prompt
        assert answer in prompt
        assert "follow" in prompt.lower()
    
    def test_followup_prompt_includes_role(self, prompt_generator, sample_role):
        """Test follow-up prompt includes role context"""
        question = "Tell me about your experience."
        answer = "I have some experience."
        prompt = prompt_generator.generate_followup_prompt(sample_role, question, answer)
        
        assert sample_role.display_name in prompt or sample_role.name in prompt


class TestFeedbackPrompt:
    """Test feedback generation prompts"""
    
    def test_feedback_prompt_structure(self, prompt_generator, sample_role):
        """Test feedback prompt contains all necessary elements"""
        transcript = [
            {"type": "question", "content": "Question 1"},
            {"type": "answer", "content": "Answer 1"}
        ]
        prompt = prompt_generator.generate_feedback_prompt(sample_role, transcript)
        
        assert "feedback" in prompt.lower() or "evaluate" in prompt.lower()
        assert "Question 1" in prompt
        assert "Answer 1" in prompt
    
    def test_feedback_prompt_includes_criteria(self, prompt_generator, sample_role):
        """Test feedback prompt includes evaluation criteria"""
        transcript = [
            {"type": "question", "content": "Question 1"},
            {"type": "answer", "content": "Answer 1"}
        ]
        prompt = prompt_generator.generate_feedback_prompt(sample_role, transcript)
        
        assert "communication" in prompt.lower()
        assert "technical" in prompt.lower()
        assert "structure" in prompt.lower()


class TestQuestionFormatting:
    """Test question formatting with context"""
    
    def test_basic_question_formatting(self, prompt_generator):
        """Test basic question formatting"""
        question = "What is your experience?"
        formatted = prompt_generator.format_question_with_context(question, 1, 5)
        
        assert question in formatted
        assert "1" in formatted or "first" in formatted.lower()
    
    def test_question_formatting_with_persona(self, prompt_generator):
        """Test question formatting with persona adaptation"""
        question = "What is your experience?"
        formatted = prompt_generator.format_question_with_context(
            question, 1, 5, PersonaType.CONFUSED
        )
        
        assert question in formatted


class TestUtilityMessages:
    """Test utility message generation"""
    
    def test_intro_message(self, prompt_generator, sample_role):
        """Test introduction message generation"""
        intro = prompt_generator.generate_intro_message(sample_role, "chat")
        
        assert len(intro) > 0
        assert sample_role.display_name in intro or "interview" in intro.lower()
    
    def test_transition_message(self, prompt_generator):
        """Test transition message between questions"""
        transition = prompt_generator.generate_transition_message(1, 2)
        
        assert len(transition) > 0
    
    def test_completion_message(self, prompt_generator):
        """Test completion message"""
        completion = prompt_generator.generate_completion_message()
        
        assert len(completion) > 0
        assert "complete" in completion.lower() or "finish" in completion.lower()


class TestPersonaAdaptation:
    """Test persona-specific response adaptation"""
    
    def test_adapt_for_confused(self, prompt_generator):
        """Test adaptation for Confused persona"""
        response = "Next question."
        adapted = prompt_generator.adapt_response_for_persona(response, PersonaType.CONFUSED)
        
        assert len(adapted) >= len(response)
    
    def test_adapt_for_efficient(self, prompt_generator):
        """Test adaptation for Efficient persona"""
        response = "Let me ask you about your experience with databases."
        adapted = prompt_generator.adapt_response_for_persona(response, PersonaType.EFFICIENT)
        
        assert len(adapted) <= len(response)
    
    def test_adapt_for_normal(self, prompt_generator):
        """Test no adaptation for Normal persona"""
        response = "Tell me more."
        adapted = prompt_generator.adapt_response_for_persona(response, PersonaType.NORMAL)
        
        assert adapted == response
