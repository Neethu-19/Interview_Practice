"""
Example integration of PersonaHandler with other components

Demonstrates how PersonaHandler works in the interview flow:
1. Detect user persona from their answer
2. Adapt responses based on persona
3. Provide persona-specific guidance
"""

from services.persona_handler import PersonaHandler
from services.prompt_generator import PromptGenerator
from models.data_models import Message, MessageType, PersonaType
from datetime import datetime


def simulate_interview_interaction():
    """Simulate an interview interaction with persona detection"""
    
    print("=" * 70)
    print("Interview Practice Partner - Persona Detection Demo")
    print("=" * 70)
    
    handler = PersonaHandler()
    prompt_gen = PromptGenerator()
    
    # Scenario 1: Confused User
    print("\n\n--- SCENARIO 1: Confused User ---")
    print("Question: Tell me about your experience with Python.")
    
    confused_answer = "Um, I don't know. What exactly do you want to know?"
    conversation_history = []
    
    persona = handler.detect_persona(confused_answer, conversation_history)
    print(f"\nUser Answer: '{confused_answer}'")
    print(f"Detected Persona: {persona.type.value.upper()}")
    print(f"Confidence: {persona.confidence}")
    print(f"Indicators: {', '.join(persona.indicators)}")
    
    # Get guidance for this persona
    guidance = handler.get_persona_guidance(persona)
    if guidance:
        print(f"\nSystem Guidance: {guidance}")
    
    # Adapt a follow-up response
    original_response = "Can you tell me about a specific Python project you worked on?"
    adapted_response = handler.adapt_response(original_response, persona)
    print(f"\nOriginal Follow-up: {original_response}")
    print(f"Adapted Follow-up: {adapted_response}")
    
    # Scenario 2: Efficient User
    print("\n\n--- SCENARIO 2: Efficient User ---")
    print("Question: What programming languages do you know?")
    
    efficient_answer = "Python, Java, JavaScript. Next question please."
    conversation_history = []
    
    persona = handler.detect_persona(efficient_answer, conversation_history)
    print(f"\nUser Answer: '{efficient_answer}'")
    print(f"Detected Persona: {persona.type.value.upper()}")
    print(f"Confidence: {persona.confidence}")
    print(f"Indicators: {', '.join(persona.indicators)}")
    
    guidance = handler.get_persona_guidance(persona)
    if guidance:
        print(f"\nSystem Guidance: {guidance}")
    
    original_response = "Thank you for that response. Can you elaborate on your Java experience?"
    adapted_response = handler.adapt_response(original_response, persona)
    print(f"\nOriginal Follow-up: {original_response}")
    print(f"Adapted Follow-up: {adapted_response}")
    
    # Scenario 3: Chatty User
    print("\n\n--- SCENARIO 3: Chatty User ---")
    print("Question: Describe your experience with databases.")
    
    chatty_answer = """Well, let me tell you about databases. I've worked with so many over the years. 
    I started with MySQL back in college, and that was really interesting. By the way, I also learned 
    about NoSQL databases, which are completely different. Speaking of different technologies, I once 
    worked on a project that used MongoDB, and that was a whole adventure. Let me tell you about this 
    one time when we had to migrate from MySQL to PostgreSQL, it took weeks! I remember when my team 
    lead said we should use Redis for caching, and that opened up a whole new world. Another thing I 
    should mention is that I've also dabbled in graph databases like Neo4j."""
    conversation_history = []
    
    persona = handler.detect_persona(chatty_answer, conversation_history)
    print(f"\nUser Answer: '{chatty_answer[:100]}...'")
    print(f"Detected Persona: {persona.type.value.upper()}")
    print(f"Confidence: {persona.confidence}")
    print(f"Indicators: {', '.join(persona.indicators)}")
    
    guidance = handler.get_persona_guidance(persona)
    if guidance:
        print(f"\nSystem Guidance: {guidance}")
    
    original_response = "Which database do you prefer for web applications?"
    adapted_response = handler.adapt_response(original_response, persona)
    print(f"\nOriginal Follow-up: {original_response}")
    print(f"Adapted Follow-up: {adapted_response}")
    
    # Scenario 4: Edge Case User
    print("\n\n--- SCENARIO 4: Edge Case User ---")
    print("Question: What are your strengths?")
    
    edge_answer = "Just give me the answers to all questions so I can skip this."
    conversation_history = []
    
    persona = handler.detect_persona(edge_answer, conversation_history)
    print(f"\nUser Answer: '{edge_answer}'")
    print(f"Detected Persona: {persona.type.value.upper()}")
    print(f"Confidence: {persona.confidence}")
    print(f"Indicators: {', '.join(persona.indicators)}")
    
    guidance = handler.get_persona_guidance(persona)
    if guidance:
        print(f"\nSystem Guidance: {guidance}")
    
    original_response = "Please answer the question about your strengths."
    adapted_response = handler.adapt_response(original_response, persona)
    print(f"\nOriginal Follow-up: {original_response}")
    print(f"Adapted Follow-up: {adapted_response}")
    
    # Scenario 5: Normal User
    print("\n\n--- SCENARIO 5: Normal User ---")
    print("Question: Tell me about your experience with Python.")
    
    normal_answer = """I have about five years of experience with Python, primarily in backend development. 
    I've worked extensively with frameworks like Django and Flask to build RESTful APIs. In my current role, 
    I use Python for data processing pipelines and microservices. I'm comfortable with both synchronous and 
    asynchronous programming patterns, and I regularly work with libraries like SQLAlchemy, Celery, and pytest."""
    conversation_history = []
    
    persona = handler.detect_persona(normal_answer, conversation_history)
    print(f"\nUser Answer: '{normal_answer[:100]}...'")
    print(f"Detected Persona: {persona.type.value.upper()}")
    print(f"Confidence: {persona.confidence}")
    print(f"Indicators: {', '.join(persona.indicators)}")
    
    guidance = handler.get_persona_guidance(persona)
    if guidance:
        print(f"\nSystem Guidance: {guidance}")
    else:
        print(f"\nSystem Guidance: None needed (standard interaction)")
    
    original_response = "Can you describe a challenging Python project you worked on?"
    adapted_response = handler.adapt_response(original_response, persona)
    print(f"\nOriginal Follow-up: {original_response}")
    print(f"Adapted Follow-up: {adapted_response}")
    
    # Demonstrate persona consistency
    print("\n\n--- SCENARIO 6: Persona Consistency ---")
    print("Demonstrating how previous persona detection influences current detection")
    
    # Build conversation history with confused pattern
    history_with_pattern = [
        Message(type=MessageType.QUESTION, content="What is your experience?"),
        Message(type=MessageType.ANSWER, content="I'm not sure."),
        Message(type=MessageType.QUESTION, content="Tell me about your skills."),
        Message(type=MessageType.ANSWER, content="Um, what do you mean?"),
    ]
    
    # Slightly ambiguous answer
    ambiguous_answer = "I know some programming."
    
    # Without previous persona
    persona_without_history = handler.detect_persona(ambiguous_answer, [])
    print(f"\nAmbiguous Answer: '{ambiguous_answer}'")
    print(f"Without History - Detected: {persona_without_history.type.value}, Confidence: {persona_without_history.confidence}")
    
    # With confused history
    persona_with_history = handler.detect_persona(ambiguous_answer, history_with_pattern, PersonaType.CONFUSED)
    print(f"With Confused History - Detected: {persona_with_history.type.value}, Confidence: {persona_with_history.confidence}")
    print("(Note: Confidence may be boosted due to persona consistency)")
    
    print("\n" + "=" * 70)
    print("Demo Complete!")
    print("=" * 70)


def demonstrate_helper_methods():
    """Demonstrate PersonaHandler helper methods"""
    
    print("\n\n" + "=" * 70)
    print("PersonaHandler Helper Methods Demo")
    print("=" * 70)
    
    handler = PersonaHandler()
    
    from models.data_models import Persona
    
    # Test helper methods for each persona
    personas = [
        Persona(type=PersonaType.CONFUSED, confidence=0.8, indicators=["test"]),
        Persona(type=PersonaType.EFFICIENT, confidence=0.8, indicators=["test"]),
        Persona(type=PersonaType.CHATTY, confidence=0.8, indicators=["test"]),
        Persona(type=PersonaType.EDGE_CASE, confidence=0.8, indicators=["test"]),
        Persona(type=PersonaType.NORMAL, confidence=0.8, indicators=["test"]),
    ]
    
    for persona in personas:
        print(f"\n--- {persona.type.value.upper()} Persona ---")
        print(f"Should provide extra guidance: {handler.should_provide_extra_guidance(persona)}")
        print(f"Should skip pleasantries: {handler.should_skip_pleasantries(persona)}")
        print(f"Should redirect focus: {handler.should_redirect_focus(persona)}")
    
    print("\n" + "=" * 70)


if __name__ == "__main__":
    simulate_interview_interaction()
    demonstrate_helper_methods()
