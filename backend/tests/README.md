# Test Suite Documentation

This directory contains automated tests for the Interview Practice Partner application.

## Test Structure

The test suite is organized into three main categories:

### 1. Unit Tests (`test_unit_*.py`)
Tests for individual components in isolation:
- `test_unit_persona_handler.py` - PersonaHandler detection and adaptation logic
- `test_unit_prompt_generator.py` - PromptGenerator template rendering
- `test_unit_feedback_engine.py` - FeedbackEngine score calculation and validation
- `test_unit_session_manager.py` - InterviewSessionManager state transitions

### 2. Integration Tests (`test_integration_*.py`)
Tests for API endpoints and complete workflows:
- `test_integration_api.py` - All API endpoints and complete interview flows

### 3. Persona Behavior Tests (`test_persona_*.py`)
End-to-end tests for different user personas:
- `test_persona_behaviors.py` - Confused, Efficient, Chatty, and Edge Case personas

## Running Tests

### Prerequisites

1. Install test dependencies:
```bash
pip install -r requirements.txt
```

2. (Optional) Start Ollama for tests that require LLM:
```bash
ollama serve
```

### Run All Tests

```bash
# Using pytest directly
pytest tests/

# Using the test runner script
python run_tests.py all
```

### Run Specific Test Categories

```bash
# Unit tests only
pytest tests/test_unit_*.py
python run_tests.py unit

# Integration tests only
pytest tests/test_integration_*.py
python run_tests.py integration

# Persona behavior tests only
pytest tests/test_persona_*.py
python run_tests.py persona
```

### Run Specific Test Files

```bash
# Run a single test file
pytest tests/test_unit_persona_handler.py

# Run a specific test class
pytest tests/test_unit_persona_handler.py::TestPersonaDetection

# Run a specific test function
pytest tests/test_unit_persona_handler.py::TestPersonaDetection::test_confused_persona_short_answer
```

### Run with Different Verbosity

```bash
# Verbose output
pytest -v tests/

# Quiet output
pytest -q tests/

# Very verbose with full output
pytest -vv tests/
```

## Test Coverage

### PersonaHandler Tests
- ✓ Confused persona detection (short answers, questions)
- ✓ Efficient persona detection (direct language, concise answers)
- ✓ Chatty persona detection (long answers, off-topic)
- ✓ Edge case persona detection (spam, suspicious requests)
- ✓ Normal persona detection
- ✓ Response adaptation for each persona
- ✓ Persona guidance messages

### PromptGenerator Tests
- ✓ Interviewer system prompt generation
- ✓ Follow-up question prompts
- ✓ Feedback generation prompts
- ✓ Question formatting with context
- ✓ Persona-specific adaptations
- ✓ Utility messages (intro, transition, completion)

### FeedbackEngine Tests
- ✓ Score validation (1-5 range)
- ✓ Score clamping for out-of-range values
- ✓ Three items validation (strengths/improvements)
- ✓ Feedback structure validation
- ✓ Average score calculation

### SessionManager Tests
- ✓ Session creation with valid/invalid roles
- ✓ Session retrieval
- ✓ Answer processing
- ✓ Follow-up logic and counting
- ✓ Max 3 follow-ups enforcement
- ✓ Session completion
- ✓ Session progress tracking
- ✓ Transcript retrieval

### API Integration Tests
- ✓ Basic endpoints (root, health)
- ✓ Start endpoint (valid/invalid roles)
- ✓ Answer endpoint (valid/empty/invalid)
- ✓ Complete interview flow
- ✓ Follow-up question generation
- ✓ History endpoint
- ✓ Session transcript endpoint
- ✓ Feedback endpoint
- ✓ Error handling

### Persona Behavior Tests
- ✓ Confused user handling and guidance
- ✓ Efficient user minimal follow-ups
- ✓ Chatty user redirection
- ✓ Edge case user boundaries
- ✓ Persona transitions
- ✓ Persona reflection in feedback

## Test Dependencies

Tests that require external services:
- **Ollama**: FeedbackEngine tests and some integration tests require Ollama to be running
- **Database**: Tests use in-memory SQLite, no setup required

Tests will automatically skip if dependencies are not available.

## Writing New Tests

### Test File Naming
- Unit tests: `test_unit_<component>.py`
- Integration tests: `test_integration_<feature>.py`
- Persona tests: `test_persona_<aspect>.py`

### Test Function Naming
- Use descriptive names: `test_<what>_<condition>_<expected>`
- Example: `test_confused_persona_short_answer`

### Using Fixtures
Common fixtures are defined in `conftest.py`:
- `sample_role` - Sample role for testing
- `ollama_client` - OllamaClient instance
- `prompt_generator` - PromptGenerator instance
- `persona_handler` - PersonaHandler instance
- `feedback_engine` - FeedbackEngine instance
- `session_manager` - InterviewSessionManager instance

### Example Test

```python
def test_my_feature(persona_handler):
    """Test description"""
    # Arrange
    answer = "Test answer"
    history = []
    
    # Act
    result = persona_handler.detect_persona(answer, history)
    
    # Assert
    assert result.type == PersonaType.NORMAL
```

## Continuous Integration

These tests are designed to run in CI/CD pipelines:
- Fast unit tests run on every commit
- Integration tests run on pull requests
- Full test suite runs before deployment

## Troubleshooting

### Tests Fail with "Ollama not available"
Some tests require Ollama to be running. Either:
1. Start Ollama: `ollama serve`
2. Skip those tests: `pytest -k "not requires_ollama"`

### Import Errors
Make sure you're running tests from the backend directory:
```bash
cd backend
pytest tests/
```

### Database Errors
Tests use in-memory SQLite. If you see database errors, check that:
1. SQLite is available (should be built into Python)
2. No file locks on `interview_practice.db`

## Test Metrics

Current test coverage:
- **Unit Tests**: 40+ test cases
- **Integration Tests**: 30+ test cases
- **Persona Tests**: 20+ test cases
- **Total**: 90+ automated tests

Target execution time:
- Unit tests: < 5 seconds
- Integration tests: < 30 seconds (without Ollama)
- Full suite: < 60 seconds (with Ollama)
