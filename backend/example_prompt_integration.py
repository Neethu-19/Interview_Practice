"""
Example: PromptGenerator Integration with OllamaClient

Demonstrates how to use PromptGenerator with OllamaClient
for a complete interview flow.
"""

from services.prompt_generator import PromptGenerator
from services.ollama_client import OllamaClient
from services.role_loader import get_role
from models.data_models import PersonaType


def example_followup_generation():
    """Example: Generate and evaluate follow-up questions."""
    print("=" * 60)
    print("EXAMPLE: Follow-up Question Generation")
    print("=" * 60)
    
    # Initialize services
    generator = PromptGenerator()
    client = OllamaClient()
    
    # Check Ollama availability
    if not client.check_health():
        print("⚠️  Ollama server not available. This is a demonstration only.")
        print("   Start Ollama to see actual LLM responses.\n")
        return
    
    # Load role
    role = get_role("backend_engineer")
    if not role:
        print("❌ Role not found")
        return
    
    # Simulate interview scenario
    question = "Tell me about your experience with Python."
    answer = "I have used Python for a few years."
    
    print(f"\nQuestion: {question}")
    print(f"Answer: {answer}")
    print("\n--- Generating Follow-up Analysis ---\n")
    
    # Generate follow-up prompt
    followup_prompt = generator.generate_followup_prompt(role, question, answer)
    
    # Use Ollama to analyze and generate follow-up
    try:
        response = client.generate(
            prompt=followup_prompt,
            temperature=0.7
        )
        
        print(f"LLM Response: {response}")
        
        if response.strip().upper() == "COMPLETE":
            print("\n✓ Answer is complete, no follow-up needed")
        else:
            print(f"\n✓ Follow-up question generated: {response}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print()


def example_persona_adaptation():
    """Example: Adapt responses for different personas."""
    print("=" * 60)
    print("EXAMPLE: Persona-Specific Adaptations")
    print("=" * 60)
    
    generator = PromptGenerator()
    
    base_question = "Can you describe your approach to debugging?"
    
    personas = [
        PersonaType.NORMAL,
        PersonaType.CONFUSED,
        PersonaType.EFFICIENT,
        PersonaType.CHATTY
    ]
    
    for persona in personas:
        print(f"\n--- {persona.value.upper()} Persona ---")
        adapted = generator.adapt_response_for_persona(base_question, persona)
        print(adapted)
    
    print()


def example_complete_interview_prompts():
    """Example: Generate prompts for complete interview flow."""
    print("=" * 60)
    print("EXAMPLE: Complete Interview Flow Prompts")
    print("=" * 60)
    
    generator = PromptGenerator()
    role = get_role("backend_engineer")
    
    if not role:
        print("❌ Role not found")
        return
    
    # 1. Introduction
    print("\n--- 1. INTRODUCTION ---")
    intro = generator.generate_intro_message(role, "chat")
    print(intro)
    
    # 2. First Question
    print("\n--- 2. FIRST QUESTION ---")
    question = role.questions[0]
    formatted_q = generator.format_question_with_context(question, 1, len(role.questions))
    print(formatted_q)
    
    # 3. Interviewer System Prompt
    print("\n--- 3. INTERVIEWER SYSTEM PROMPT ---")
    system_prompt = generator.generate_interviewer_prompt(role, question)
    print(system_prompt[:300] + "...")
    
    # 4. Transition
    print("\n--- 4. TRANSITION TO NEXT QUESTION ---")
    transition = generator.generate_transition_message(1, 2)
    print(transition)
    
    # 5. Completion
    print("\n--- 5. INTERVIEW COMPLETION ---")
    completion = generator.generate_completion_message()
    print(completion)
    
    print()


def main():
    """Run all examples."""
    print("\n" + "=" * 60)
    print("PROMPT GENERATOR INTEGRATION EXAMPLES")
    print("=" * 60 + "\n")
    
    try:
        example_persona_adaptation()
        example_complete_interview_prompts()
        example_followup_generation()
        
        print("=" * 60)
        print("EXAMPLES COMPLETED ✓")
        print("=" * 60)
        print("\nThe PromptGenerator is ready to use in the interview system!")
        print("It provides:")
        print("  • System prompts for interviewer persona")
        print("  • Follow-up question generation prompts")
        print("  • Feedback evaluation prompts with scoring rubric")
        print("  • Persona-specific adaptations")
        print("  • Utility messages for smooth interview flow")
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
