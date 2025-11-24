# FeedbackEngine Service

## Overview

The `FeedbackEngine` generates comprehensive performance feedback for interview sessions using LLM analysis. It evaluates interview transcripts and produces structured feedback with scores, strengths, and actionable improvements.

## Features

- **LLM-Powered Analysis**: Uses Ollama to analyze interview performance
- **Structured Feedback**: Generates consistent, validated feedback reports
- **Score Validation**: Ensures all scores are within 1-5 range with automatic clamping
- **Timeout Protection**: Guarantees feedback generation completes within 10 seconds
- **Error Handling**: Comprehensive error handling with specific exception types
- **Fallback Generation**: Provides fallback feedback if LLM output is incomplete

## Usage

### Basic Usage

```python
from uuid import uuid4
from services.ollama_client import OllamaClient
from services.prompt_generator import PromptGenerator
from services.feedback_engine import FeedbackEngine
from models.data_models import Role, Message, MessageType

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
    temperature=0.3
)

# Create role and transcript
role = Role(
    name="backend_engineer",
    display_name="Backend Engineer",
    questions=["Tell me about your experience..."],
    evaluation_criteria={"technical": "API knowledge"}
)

transcript = [
    Message(
        type=MessageType.QUESTION,
        content="Tell me about your experience with APIs.",
        timestamp=datetime.now()
    ),
    Message(
        type=MessageType.ANSWER,
        content="I have 3 years of experience building REST APIs...",
        timestamp=datetime.now()
    )
]

# Generate feedback
session_id = uuid4()
feedback = feedback_engine.generate_feedback(
    session_id=session_id,
    role=role,
    transcript=transcript
)

# Access feedback data
print(f"Communication Score: {feedback.scores.communication}/5")
print(f"Average Score: {feedback.scores.average}/5")
print(f"Strengths: {feedback.strengths}")
print(f"Improvements: {feedback.improvements}")
print(f"Overall: {feedback.overall_feedback}")
```

### With Error Handling

```python
from services.feedback_engine import (
    FeedbackEngine,
    FeedbackEngineError,
    FeedbackTimeoutError,
    FeedbackValidationError
)

try:
    feedback = feedback_engine.generate_feedback(
        session_id=session_id,
        role=role,
        transcript=transcript
    )
    print("✓ Feedback generated successfully!")
    
except FeedbackTimeoutError as e:
    print(f"Timeout: {e}")
    # Handle timeout - maybe retry or use cached feedback
    
except FeedbackValidationError as e:
    print(f"Validation error: {e}")
    # Handle invalid feedback - maybe regenerate
    
except FeedbackEngineError as e:
    print(f"Generation error: {e}")
    # Handle general errors - check Ollama connection
```

## API Reference

### FeedbackEngine Class

#### Constructor

```python
FeedbackEngine(
    ollama_client: OllamaClient,
    prompt_generator: PromptGenerator,
    timeout_seconds: int = 10,
    temperature: float = 0.3
)
```

**Parameters:**
- `ollama_client`: Client for LLM communication
- `prompt_generator`: Generator for feedback prompts
- `timeout_seconds`: Maximum time for feedback generation (default: 10)
- `temperature`: LLM temperature for consistency (default: 0.3)

#### Methods

##### generate_feedback()

```python
def generate_feedback(
    session_id: UUID,
    role: Role,
    transcript: List[Message]
) -> FeedbackReport
```

Generate comprehensive feedback for an interview session.

**Parameters:**
- `session_id`: UUID of the interview session
- `role`: Role object with evaluation criteria
- `transcript`: List of Message objects from the interview

**Returns:**
- `FeedbackReport`: Structured feedback with scores, strengths, improvements

**Raises:**
- `FeedbackTimeoutError`: If generation exceeds timeout
- `FeedbackValidationError`: If generated feedback is invalid
- `FeedbackEngineError`: For other generation errors

##### calculate_scores_from_transcript()

```python
def calculate_scores_from_transcript(
    transcript: List[Message]
) -> Dict[str, float]
```

Calculate basic metrics from transcript for debugging/analysis.

**Parameters:**
- `transcript`: List of Message objects

**Returns:**
- Dictionary with metrics: `total_answers`, `avg_answer_length`, `total_words`

## Feedback Structure

The generated `FeedbackReport` contains:

```python
{
    "session_id": UUID,
    "scores": {
        "communication": 1-5,        # Clarity, conciseness, articulation
        "technical_knowledge": 1-5,  # Accuracy, depth, relevance
        "structure": 1-5             # Organization, examples, completeness
    },
    "strengths": [
        "Specific strength 1",
        "Specific strength 2",
        "Specific strength 3"
    ],
    "improvements": [
        "Actionable improvement 1",
        "Actionable improvement 2",
        "Actionable improvement 3"
    ],
    "overall_feedback": "2-3 sentence summary of performance",
    "generated_at": datetime
}
```

## Score Validation

Scores are automatically validated and clamped:

- **Valid Range**: 1-5 (inclusive)
- **Below 1**: Clamped to 1
- **Above 5**: Clamped to 5
- **Non-integer**: Raises `FeedbackValidationError`
- **Missing**: Raises `FeedbackValidationError`

## Timeout Handling

The engine enforces a configurable timeout (default 10 seconds):

1. Timer starts when `generate_feedback()` is called
2. LLM generation is performed
3. Elapsed time is checked after generation
4. If exceeded, `FeedbackTimeoutError` is raised

**Note**: The timeout check occurs after LLM generation completes, so actual time may slightly exceed the limit.

## Error Handling

### Exception Hierarchy

```
FeedbackEngineError (base)
├── FeedbackTimeoutError
└── FeedbackValidationError
```

### Common Errors

**Ollama Connection Error:**
```python
FeedbackEngineError: LLM generation failed: Failed to connect to Ollama
```
**Solution**: Ensure Ollama is running (`ollama serve`)

**Invalid Feedback Format:**
```python
FeedbackValidationError: Strengths must be a list
```
**Solution**: Check LLM output format, may need to adjust prompt

**Timeout Exceeded:**
```python
FeedbackTimeoutError: Feedback generation took 12.5s, exceeding 10s limit
```
**Solution**: Increase timeout or optimize prompt

## Testing

Run the test suite:

```bash
python backend/test_feedback_engine.py
```

Run integration examples:

```bash
python backend/example_feedback_integration.py
```

## Requirements

- Python 3.10+
- Ollama server running locally
- Model downloaded (e.g., `ollama pull llama3.1:8b`)
- Dependencies: `pydantic`, `requests`

## Performance

- **Target Time**: < 10 seconds per feedback generation
- **Typical Time**: 3-7 seconds (depends on model and transcript length)
- **LLM Temperature**: 0.3 (lower for consistency)
- **Max Tokens**: 1000 (sufficient for structured feedback)

## Design Decisions

1. **Low Temperature (0.3)**: Ensures consistent, reliable feedback across sessions
2. **Structured Output**: Uses JSON format for reliable parsing
3. **Score Clamping**: Prevents invalid scores from breaking the system
4. **Fallback Generation**: Provides basic feedback if LLM output is incomplete
5. **Timeout Enforcement**: Guarantees timely response for user experience

## Future Enhancements

- [ ] Caching for similar transcripts
- [ ] Batch feedback generation
- [ ] Custom scoring rubrics per role
- [ ] Comparative feedback (vs. previous sessions)
- [ ] Confidence scores for feedback quality
