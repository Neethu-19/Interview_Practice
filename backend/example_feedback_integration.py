"""
Example: FeedbackEngine Integration

Demonstrates how to use the FeedbackEngine to generate performance feedback
for interview sessions.
"""

from uuid import uuid4
from datetime import datetime
from models.data_models import Role, Message, MessageType
from services.ollama_client import OllamaClient
from services.prompt_generator import PromptGenerator
from services.feedback_engine import FeedbackEngine, FeedbackEngineError


def example_basic_feedback():
    """Example: Generate basic feedback for an interview"""
    print("=" * 70)
    print("Example 1: Basic Feedback Generation")
    print("=" * 70)
    
    # Initialize services
    ollama_client = OllamaClient(
        base_url="http://localhost:11434",
        model="llama3.1:8b"
    )
    
    prompt_generator = PromptGenerator()
    
    feedback_engine = FeedbackEngine(
        ollama_client=ollama_client,
        prompt_generator=prompt_generator,
        timeout_seconds=10,
        temperature=0.3  # Lower temperature for more consistent feedback
    )
    
    # Create role
    role = Role(
        name="sales_associate",
        display_name="Sales Associate",
        questions=[
            "How do you handle a difficult customer?",
            "Tell me about a time you exceeded your sales target."
        ],
        evaluation_criteria={
            "customer_service": "Demonstrates empathy and problem-solving",
            "sales_skills": "Shows ability to close deals and meet targets",
            "communication": "Clear and persuasive communication"
        }
    )
    
    # Create interview transcript
    transcript = [
        Message(
            type=MessageType.QUESTION,
            content="How do you handle a difficult customer?",
            timestamp=datetime.now()
        ),
        Message(
            type=MessageType.ANSWER,
            content="I always stay calm and listen to their concerns first. I try to understand the root cause of their frustration and then work with them to find a solution. For example, last month a customer was upset about a delayed order. I apologized, explained what happened, and offered a discount on their next purchase. They left happy and became a regular customer.",
            timestamp=datetime.now()
        ),
        Message(
            type=MessageType.QUESTION,
            content="Tell me about a time you exceeded your sales target.",
            timestamp=datetime.now()
        ),
        Message(
            type=MessageType.ANSWER,
            content="In Q3 last year, my target was $50,000 but I achieved $68,000. I did this by building relationships with customers, following up on leads promptly, and upselling complementary products. I also studied our product catalog thoroughly so I could make better recommendations.",
            timestamp=datetime.now()
        )
    ]
    
    # Generate feedback
    session_id = uuid4()
    
    try:
        print(f"\nGenerating feedback for session: {session_id}")
        print(f"Role: {role.display_name}")
        print(f"Transcript length: {len(transcript)} messages\n")
        
        feedback = feedback_engine.generate_feedback(
            session_id=session_id,
            role=role,
            transcript=transcript
        )
        
        print("✓ Feedback generated successfully!\n")
        print("-" * 70)
        print("FEEDBACK REPORT")
        print("-" * 70)
        
        print(f"\nScores:")
        print(f"  Communication: {feedback.scores.communication}/5")
        print(f"  Technical Knowledge: {feedback.scores.technical_knowledge}/5")
        print(f"  Structure: {feedback.scores.structure}/5")
        print(f"  Average: {feedback.scores.average}/5")
        
        print(f"\nStrengths:")
        for i, strength in enumerate(feedback.strengths, 1):
            print(f"  {i}. {strength}")
        
        print(f"\nAreas for Improvement:")
        for i, improvement in enumerate(feedback.improvements, 1):
            print(f"  {i}. {improvement}")
        
        print(f"\nOverall Feedback:")
        print(f"  {feedback.overall_feedback}")
        
        print("\n" + "=" * 70 + "\n")
        
    except FeedbackEngineError as e:
        print(f"❌ Error generating feedback: {e}")


def example_with_error_handling():
    """Example: Feedback generation with comprehensive error handling"""
    print("=" * 70)
    print("Example 2: Feedback Generation with Error Handling")
    print("=" * 70)
    
    # Initialize services
    ollama_client = OllamaClient(
        base_url="http://localhost:11434",
        model="llama3.1:8b",
        max_retries=3
    )
    
    prompt_generator = PromptGenerator()
    
    feedback_engine = FeedbackEngine(
        ollama_client=ollama_client,
        prompt_generator=prompt_generator,
        timeout_seconds=10
    )
    
    # Create minimal test data
    role = Role(
        name="backend_engineer",
        display_name="Backend Engineer",
        questions=["Describe your experience with APIs."],
        evaluation_criteria={"technical": "API knowledge"}
    )
    
    transcript = [
        Message(
            type=MessageType.QUESTION,
            content="Describe your experience with APIs.",
            timestamp=datetime.now()
        ),
        Message(
            type=MessageType.ANSWER,
            content="I have built REST APIs using FastAPI and Flask. I understand HTTP methods, status codes, and authentication.",
            timestamp=datetime.now()
        )
    ]
    
    session_id = uuid4()
    
    try:
        print(f"\nAttempting to generate feedback...")
        
        # Check Ollama health first
        if not ollama_client.check_health():
            print("⚠️  Warning: Ollama server may not be available")
            print("   Attempting generation anyway...\n")
        
        feedback = feedback_engine.generate_feedback(
            session_id=session_id,
            role=role,
            transcript=transcript
        )
        
        print("✓ Feedback generated successfully!")
        print(f"  Average score: {feedback.scores.average}/5")
        print(f"  Generated at: {feedback.generated_at}")
        
    except FeedbackEngineError as e:
        print(f"❌ Feedback generation failed: {e}")
        print("\nTroubleshooting:")
        print("  1. Ensure Ollama is running: ollama serve")
        print("  2. Check if model is available: ollama list")
        print("  3. Pull model if needed: ollama pull llama3.1:8b")
    
    print("\n" + "=" * 70 + "\n")


def example_transcript_metrics():
    """Example: Calculate transcript metrics"""
    print("=" * 70)
    print("Example 3: Transcript Metrics Calculation")
    print("=" * 70)
    
    # Initialize feedback engine
    ollama_client = OllamaClient()
    prompt_generator = PromptGenerator()
    feedback_engine = FeedbackEngine(
        ollama_client=ollama_client,
        prompt_generator=prompt_generator
    )
    
    # Create sample transcript
    transcript = [
        Message(
            type=MessageType.QUESTION,
            content="What is your experience?",
            timestamp=datetime.now()
        ),
        Message(
            type=MessageType.ANSWER,
            content="I have five years of experience in software development, working primarily with Python and JavaScript.",
            timestamp=datetime.now()
        ),
        Message(
            type=MessageType.FOLLOWUP,
            content="Can you elaborate on your Python experience?",
            timestamp=datetime.now()
        ),
        Message(
            type=MessageType.ANSWER,
            content="I've built web applications using Django and FastAPI, created data processing pipelines, and automated various tasks.",
            timestamp=datetime.now()
        ),
        Message(
            type=MessageType.QUESTION,
            content="How do you handle challenges?",
            timestamp=datetime.now()
        ),
        Message(
            type=MessageType.ANSWER,
            content="I break down problems into smaller parts, research solutions, and collaborate with team members when needed.",
            timestamp=datetime.now()
        )
    ]
    
    # Calculate metrics
    metrics = feedback_engine.calculate_scores_from_transcript(transcript)
    
    print("\nTranscript Metrics:")
    print(f"  Total answers: {metrics['total_answers']}")
    print(f"  Average answer length: {metrics['avg_answer_length']} words")
    print(f"  Total words: {metrics['total_words']}")
    
    print("\n" + "=" * 70 + "\n")


def main():
    """Run all examples"""
    print("\n" + "=" * 70)
    print("FEEDBACK ENGINE INTEGRATION EXAMPLES")
    print("=" * 70 + "\n")
    
    # Run examples
    example_basic_feedback()
    example_with_error_handling()
    example_transcript_metrics()
    
    print("=" * 70)
    print("Examples completed!")
    print("=" * 70)


if __name__ == "__main__":
    main()
