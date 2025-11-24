# InterviewSessionManager

## Overview

The `InterviewSessionManager` is the core orchestration component that manages interview sessions from creation to completion. It coordinates between all other services (role loader, Ollama client, prompt generator, persona handler) to provide a seamless interview experience.

## Key Features

### 1. Session Creation
- Creates new interview sessions with unique IDs
- Validates role selection
- Supports both chat and voice modes
- Returns first question immediately

### 2. Question Sequencing
- Retrieves questions sequentially from role configuration
- Tracks current question index
- Formats questions with context (question number, total questions)
- Adapts question presentation based on detected persona

### 3. Answer Processing
- Saves user answers to session history
- Detects user persona from interaction patterns
- Determines if follow-up questions are needed
- Returns appropriate next action (follow-up, next question, or completion)

### 4. Follow-up Logic
- Uses LLM to analyze answer completeness
- Generates contextual follow-up questions
- Enforces max 3 follow-ups per question rule
- Gracefully handles LLM failures with fallback behavior

### 5. Session State Tracking
- Maintains current question index
- Tracks follow-up count per question
- Stores complete conversation history
- Monitors detected persona throughout session

### 6. Session Completion
- Marks sessions as completed
- Preserves full conversation history
- Enables feedback generation (task 8)

## Usage Example

```python
from services.interview_session_manager import InterviewSessionManager

# Initialize manager
manager = InterviewSessionManager()

# Create session
session, first_question = manager.create_session(
    role="backend_engineer",
    mode="chat"
)

print(f"Session ID: {session.session_id}")
print(f"First Question: {first_question}")

# Process answer
response = manager.process_answer(
    session_id=session.session_id,
    answer="I have 5 years of Python experience..."
)

if response['type'] == 'followup':
    print(f"Follow-up: {response['content']}")
elif response['type'] == 'question':
    print(f"Next Question: {response['content']}")
elif response['type'] == 'complete':
    print("Interview complete!")

# Check progress
progress = manager.get_session_progress(session.session_id)
print(f"Progress: {progress['progress_percentage']}%")

# End session
completed_session = manager.end_session(session.session_id)
```

## API Reference

### `create_session(role: str, mode: str) -> Tuple[Session, str]`
Creates a new interview session.

**Parameters:**
- `role`: Role name (e.g., "backend_engineer")
- `mode`: Interaction mode ("chat" or "voice")

**Returns:**
- Tuple of (Session object, first question text)

**Raises:**
- `SessionManagerError`: If role is invalid

### `get_next_question(session_id: UUID) -> str`
Retrieves the next question for the session.

**Parameters:**
- `session_id`: Session identifier

**Returns:**
- Next question text

**Raises:**
- `SessionNotFoundError`: If session doesn't exist
- `InvalidSessionStateError`: If no more questions

### `process_answer(session_id: UUID, answer: str) -> Dict`
Processes user's answer and determines next action.

**Parameters:**
- `session_id`: Session identifier
- `answer`: User's answer text

**Returns:**
- Dictionary with:
  - `type`: "followup" | "question" | "complete"
  - `content`: Response text
  - `question_number`: Current question number
  - `persona`: Detected Persona object

**Raises:**
- `SessionNotFoundError`: If session doesn't exist
- `InvalidSessionStateError`: If session is not active
- `ValueError`: If answer is empty

### `should_ask_followup(session_id: UUID, answer: str, question: str) -> Tuple[bool, Optional[str]]`
Determines if a follow-up question should be asked.

**Parameters:**
- `session_id`: Session identifier
- `answer`: User's answer
- `question`: Original question

**Returns:**
- Tuple of (should_ask: bool, followup_question: Optional[str])

### `end_session(session_id: UUID) -> Session`
Finalizes and completes an interview session.

**Parameters:**
- `session_id`: Session identifier

**Returns:**
- Completed Session object

### `get_session(session_id: UUID) -> Session`
Retrieves a session by ID.

**Parameters:**
- `session_id`: Session identifier

**Returns:**
- Session object

### `get_session_transcript(session_id: UUID) -> List[Dict]`
Gets formatted transcript of session messages.

**Parameters:**
- `session_id`: Session identifier

**Returns:**
- List of message dictionaries

### `get_session_progress(session_id: UUID) -> Dict`
Gets progress information for a session.

**Parameters:**
- `session_id`: Session identifier

**Returns:**
- Dictionary with progress metrics

## Implementation Details

### In-Memory Storage
Currently uses in-memory dictionary for session storage. This will be replaced with SQLite database in task 9.

### Follow-up Generation
Uses Ollama LLM to analyze answer completeness. If LLM is unavailable, defaults to no follow-up (graceful degradation).

### Persona Detection
Integrates with PersonaHandler to detect user behavior patterns and adapt responses accordingly.

### Max Follow-ups Rule
Enforces maximum 3 follow-ups per question by checking `session.followup_count` before generating follow-ups.

## Testing

Run tests with:
```bash
python test_session_manager.py
```

Run integration demo with:
```bash
python example_session_integration.py
```

## Requirements Satisfied

This implementation satisfies the following requirements from the spec:

- **1.3**: Conducts mock interview using role-appropriate questions
- **1.4**: Processes and evaluates responses
- **2.1**: Analyzes response content for depth, clarity, completeness
- **2.2**: Generates contextual follow-up questions
- **2.3**: Ensures follow-ups relate to previous response
- **2.4**: Limits follow-ups to maximum of 3 per question
- **2.5**: Proceeds to next question when response is comprehensive

## Next Steps

Task 8 will implement the FeedbackEngine that uses the session transcript to generate performance feedback.
