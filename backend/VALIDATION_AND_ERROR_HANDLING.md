# Input Validation and Error Handling

This document describes the comprehensive input validation and error handling implemented in the Interview Practice Partner API.

## Overview

The API now includes robust validation and error handling to ensure:
- Invalid inputs are caught early with clear error messages
- Service failures are handled gracefully with appropriate HTTP status codes
- Storage errors don't break the user experience (graceful degradation)
- Ollama connection issues provide helpful retry guidance

## Request Validation (Task 11.1)

### POST /api/start

**Validations:**
- **Role validation**: Checks if the role exists in the available roles list
  - Returns 400 with list of available roles if invalid
- **Mode validation**: Ensures mode is either "chat" or "voice"
  - Returns 400 with valid options if invalid
- **Ollama health check**: Verifies Ollama service is available before starting
  - Returns 503 if Ollama is not running

**Example error responses:**
```json
{
  "detail": "Invalid role 'invalid_role'. Available roles: backend_engineer, sales_associate, retail_associate"
}
```

### POST /api/answer

**Validations:**
- **Session ID format**: Validates UUID format
  - Returns 400 if not a valid UUID
- **Session existence**: Checks if session exists
  - Returns 404 if session not found
- **Answer not empty**: Ensures answer is not blank
  - Returns 400 with helpful message
- **Answer length**: Limits answers to 2000 words
  - Returns 400 with word count if exceeded

**Example error responses:**
```json
{
  "detail": "Answer too long (2150 words). Please keep your response under 2000 words."
}
```

### POST /api/feedback

**Validations:**
- **Session ID format**: Validates UUID format
- **Session existence**: Checks if session exists
- **Sufficient data**: Ensures at least one question was answered
  - Returns 400 if insufficient data

### GET /api/history

**Validations:**
- **Limit parameter**: Validates limit is positive and under 1000
  - Returns 400 if limit < 1 or limit > 1000

### GET /api/session/{session_id}

**Validations:**
- **Session ID format**: Validates UUID format
- **Session existence**: Checks if session exists in storage

## Error Handlers (Task 11.2)

### Global Exception Handlers

Implemented in `main.py` to catch exceptions across all endpoints:

1. **OllamaConnectionError** (503 Service Unavailable)
   - Triggered when Ollama server is unreachable
   - Includes retry logic with exponential backoff (already in OllamaClient)
   - Returns helpful message about ensuring Ollama is running

2. **OllamaGenerationError** (500 Internal Server Error)
   - Triggered when LLM generation fails
   - Returns message suggesting retry

3. **SessionNotFoundError** (404 Not Found)
   - Triggered when session doesn't exist
   - Returns clear message about expired/deleted session

4. **InvalidSessionStateError** (400 Bad Request)
   - Triggered when operation is invalid for current session state
   - Returns specific error message from exception

5. **General Exception Handler** (500 Internal Server Error)
   - Catch-all for unexpected errors
   - Logs error details for debugging
   - Returns generic error message to user

### Graceful Degradation

Storage errors are handled with graceful degradation:
- Session data is maintained in memory even if storage fails
- Storage failures are logged but don't break the API response
- Users can continue their interview even if persistence fails

**Example:**
```python
try:
    storage_service.save_session(session)
except Exception as storage_error:
    # Log error but continue - session is in memory
    print(f"Warning: Failed to persist session to storage: {storage_error}")
```

### Retry Logic

The OllamaClient already implements retry logic with exponential backoff:
- **Max retries**: 3 attempts
- **Initial delay**: 1 second
- **Backoff**: Exponential (1s, 2s, 4s)
- **Retryable errors**: Connection errors, timeouts, request exceptions
- **Non-retryable**: HTTP errors (4xx, 5xx)

## HTTP Status Codes

The API uses appropriate HTTP status codes:

- **200 OK**: Successful GET requests
- **201 Created**: Successful session creation
- **400 Bad Request**: Invalid input or request
- **404 Not Found**: Resource not found
- **500 Internal Server Error**: Unexpected server error
- **503 Service Unavailable**: Ollama service unavailable

## Testing

A comprehensive test suite is available in `test_validation.py` that verifies:
- Invalid role validation
- Invalid mode validation
- Invalid session ID format validation
- Empty answer validation
- Answer length validation
- Nonexistent session validation
- Invalid limit parameter validation
- All error messages are clear and helpful

Run tests with:
```bash
python test_validation.py
```

## Error Message Guidelines

All error messages follow these principles:
1. **Clear**: Explain what went wrong
2. **Actionable**: Suggest how to fix it
3. **User-friendly**: Avoid technical jargon when possible
4. **Specific**: Include relevant details (e.g., word count, available options)

## Future Improvements

Potential enhancements:
- Rate limiting for API endpoints
- Request ID tracking for debugging
- Structured logging with log levels
- Metrics collection for error rates
- Circuit breaker pattern for Ollama calls
- Custom error codes for client-side handling
