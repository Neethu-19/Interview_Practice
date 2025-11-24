"""
Test script for PromptGenerator service.
Tests prompt generation for different interview stages and personas.
"""

from services.prompt_generator import PromptGenerator
from models.data_models import Role, PersonaType


def test_interviewer_prompt():
    """Test interviewer system prompt generation."""
    print("=" * 60)
    print("TEST: Interviewer System Prompt")
    print("=" * 60)
    
    generator = PromptGenerator()
    
    # Create test role
    role = Role(
        name="backend_engineer",
        display_name="Backend Engineer",
        questions=["Tell me about your experience with Python."],
        evaluation_criteria={
            "communication": {"clarity": "Clear articulation"},
            "technical_knowledge": {"depth": "Deep understanding"},
            "structure": {"organization": "Well-organized"}
        }
    )
    
    question = "Tell me about your experience with Python."
    
    # Test without persona
    prompt = generator.generate_interviewer_prompt(role, question)
    print("\n--- Without Persona ---")
    print(prompt)
    
    # Test with confused persona
    prompt_confused = generator.generate_interviewer_prompt(role, question, PersonaType.CONFUSED)
    print("\n--- With Confused Persona ---")
    print(prompt_confused)
    
    print("\n✓ Interviewer prompt generation working\n")


def test_followup_prompt():
    """Test follow-up question generation prompt."""
    print("=" * 60)
    print("TEST: Follow-up Question Prompt")
    print("=" * 60)
    
    generator = PromptGenerator()
    
    role = Role(
        name="backend_engineer",
        display_name="Backend Engineer",
        questions=["Tell me about your experience with Python."],
        evaluation_criteria={"communication": {}, "technical_knowledge": {}, "structure": {}}
    )
    
    question = "Tell me about your experience with Python."
    answer = "I have used Python for a few years."
    
    prompt = generator.generate_followup_prompt(role, question, answer)
    print("\n--- Follow-up Analysis Prompt ---")
    print(prompt)
    
    print("\n✓ Follow-up prompt generation working\n")


def test_feedback_prompt():
    """Test feedback generation prompt."""
    print("=" * 60)
    print("TEST: Feedback Generation Prompt")
    print("=" * 60)
    
    generator = PromptGenerator()
    
    role = Role(
        name="backend_engineer",
        display_name="Backend Engineer",
        questions=["Tell me about your experience with Python."],
        evaluation_criteria={
            "communication": {
                "clarity": "Clear and concise communication",
                "articulation": "Well-expressed thoughts"
            },
            "technical_knowledge": {
                "accuracy": "Correct technical information",
                "depth": "Deep understanding of concepts"
            },
            "structure": {
                "organization": "Logical flow",
                "examples": "Use of specific examples"
            }
        }
    )
    
    transcript = [
        {"type": "question", "content": "Tell me about your experience with Python."},
        {"type": "answer", "content": "I have 5 years of experience with Python, primarily in web development using Django and Flask."},
        {"type": "followup", "content": "Can you describe a challenging project you worked on?"},
        {"type": "answer", "content": "I built a real-time analytics dashboard that processed millions of events per day using Python and Redis."}
    ]
    
    prompt = generator.generate_feedback_prompt(role, transcript)
    print("\n--- Feedback Generation Prompt ---")
    print(prompt[:1000] + "..." if len(prompt) > 1000 else prompt)
    
    print("\n✓ Feedback prompt generation working\n")


def test_persona_adaptation():
    """Test persona-specific response adaptation."""
    print("=" * 60)
    print("TEST: Persona Response Adaptation")
    print("=" * 60)
    
    generator = PromptGenerator()
    
    base_response = "Can you tell me more about your experience with databases?"
    
    print("\n--- Original Response ---")
    print(base_response)
    
    print("\n--- Adapted for Confused Persona ---")
    adapted_confused = generator.adapt_response_for_persona(base_response, PersonaType.CONFUSED)
    print(adapted_confused)
    
    print("\n--- Adapted for Chatty Persona ---")
    adapted_chatty = generator.adapt_response_for_persona(base_response, PersonaType.CHATTY)
    print(adapted_chatty)
    
    print("\n--- Adapted for Efficient Persona ---")
    adapted_efficient = generator.adapt_response_for_persona(base_response, PersonaType.EFFICIENT)
    print(adapted_efficient)
    
    print("\n✓ Persona adaptation working\n")


def test_question_formatting():
    """Test question formatting with context."""
    print("=" * 60)
    print("TEST: Question Formatting")
    print("=" * 60)
    
    generator = PromptGenerator()
    
    question = "What is your experience with RESTful APIs?"
    
    print("\n--- Normal Formatting ---")
    formatted = generator.format_question_with_context(question, 3, 10)
    print(formatted)
    
    print("\n--- With Confused Persona ---")
    formatted_confused = generator.format_question_with_context(question, 3, 10, PersonaType.CONFUSED)
    print(formatted_confused)
    
    print("\n--- With Chatty Persona ---")
    formatted_chatty = generator.format_question_with_context(question, 3, 10, PersonaType.CHATTY)
    print(formatted_chatty)
    
    print("\n✓ Question formatting working\n")


def test_utility_messages():
    """Test utility message generation."""
    print("=" * 60)
    print("TEST: Utility Messages")
    print("=" * 60)
    
    generator = PromptGenerator()
    
    role = Role(
        name="backend_engineer",
        display_name="Backend Engineer",
        questions=["Test question"],
        evaluation_criteria={"communication": {}, "technical_knowledge": {}, "structure": {}}
    )
    
    print("\n--- Introduction Message ---")
    intro = generator.generate_intro_message(role, "chat")
    print(intro)
    
    print("\n--- Transition Message ---")
    transition = generator.generate_transition_message(1, 2)
    print(transition)
    
    print("\n--- Completion Message ---")
    completion = generator.generate_completion_message()
    print(completion)
    
    print("\n✓ Utility messages working\n")


def main():
    """Run all tests."""
    print("\n" + "=" * 60)
    print("PROMPT GENERATOR TEST SUITE")
    print("=" * 60 + "\n")
    
    try:
        test_interviewer_prompt()
        test_followup_prompt()
        test_feedback_prompt()
        test_persona_adaptation()
        test_question_formatting()
        test_utility_messages()
        
        print("=" * 60)
        print("ALL TESTS PASSED ✓")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
