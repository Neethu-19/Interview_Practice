# Interview Practice Partner 🎯

An AI-powered mock interview system that provides adaptive questioning and detailed feedback to help you prepare for job interviews.

## Features

- **Multiple Job Roles**: Practice for Backend Engineer, Sales Associate, or Retail Associate positions
- **Adaptive Questioning**: AI asks follow-up questions based on your answers (max 3 per question)
- **Persona Detection**: System adapts to different user communication styles (Confused, Efficient, Chatty)
- **Detailed Feedback**: Get scored on communication, technical knowledge, and structure (1-5 scale)
- **Interview History**: Track your progress over time with session transcripts
- **Voice Mode**: speech-to-text and text-to-speech support
- **Modern Web UI**: Clean, responsive interface for seamless practice
- **Local & Private**: Runs entirely on your machine using Ollama - no external API calls

## Table of Contents

- [Quick Start](#quick-start)
- [Detailed Setup Instructions](#detailed-setup-instructions)
- [Architecture Overview](#architecture-overview)
- [Usage Guide](#usage-guide)
- [API Documentation](#api-documentation)
- [Configuration](#configuration)
- [Troubleshooting](#troubleshooting)
- [Development](#development)

## Quick Start

### Prerequisites

1. **Python 3.10+** installed
2. **Ollama** installed and running ([Download here](https://ollama.ai/download))
3. A compatible LLM model (llama3.1:8b recommended)

### Installation

1. Clone this repository:
```bash
git clone https://github.com/Neethu-19/Interview_Practice.git
cd Interview_Practice
```

2. Install Python dependencies:
```bash
cd backend
pip install -r requirements.txt
```

3. Pull an Ollama model:
```bash
ollama pull llama3.1:8b
```

### Running the Application

1. Start Ollama (if not already running):
```bash
ollama serve
```

2. Start the backend server:
```bash
cd backend
python main.py
```

3. Open your browser and navigate to:
```
http://localhost:8000
```

## Detailed Setup Instructions

### Step 1: Install Ollama

Ollama is a local LLM server that runs AI models on your machine.

**Windows:**
1. Download the installer from [ollama.ai/download](https://ollama.ai/download)
2. Run the installer and follow the prompts
3. Ollama will start automatically as a system service

**macOS:**
```bash
# Using Homebrew
brew install ollama

# Or download from ollama.ai/download
```

**Linux:**
```bash
curl -fsSL https://ollama.ai/install.sh | sh
```

**Verify Installation:**
```bash
ollama --version
```

### Step 2: Download an LLM Model

The system supports multiple models. We recommend starting with llama3.1:8b for best results:

```bash
# Recommended model (requires ~4.7GB)
ollama pull llama3.1:8b

# Alternative models:
ollama pull mistral:7b      # Faster, good for quick responses
ollama pull qwen2.5:7b      # Good multilingual support
```

**Verify Model Installation:**
```bash
ollama list
```

You should see your downloaded model in the list.

### Step 3: Set Up Python Environment

**Create Virtual Environment (Recommended):**

```bash
# Windows
cd backend
python -m venv venv
venv\Scripts\activate

# macOS/Linux
cd backend
python3 -m venv venv
source venv/bin/activate
```

**Install Dependencies:**

```bash
pip install -r requirements.txt
```

**Required Dependencies:**
- `fastapi` - Web framework for building APIs
- `uvicorn` - ASGI server for running FastAPI
- `pydantic` - Data validation and settings management
- `requests` - HTTP library for Ollama communication
- `python-dotenv` - Environment variable management

**Optional Dependencies (for voice mode):**
- `faster-whisper` - Speech-to-text
- `piper-tts` - Text-to-speech

### Step 4: Initialize Database

The database is automatically created on first run. To manually initialize:

```bash
cd backend
python -c "from storage.database import init_db; init_db()"
```

This creates `interview_practice.db` with the required schema.

### Step 5: Start the Application

**Start Ollama Server:**
```bash
# Usually runs automatically, but if needed:
ollama serve
```

**Start Backend Server:**
```bash
cd backend
python main.py
```

You should see:
```
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

**Access the Application:**
Open your browser to `http://localhost:8000`

### Step 6: Verify Setup

Run the verification script to check all components:

```bash
cd backend
python verify_ollama.py
```

This checks:
- Ollama server connectivity
- Model availability
- API response quality

## Architecture Overview

### System Architecture

The Interview Practice Partner follows a modular, service-oriented architecture:

```
┌─────────────────────────────────────────────────────────────┐
│                        Frontend Layer                        │
│  ┌──────────────────┐              ┌──────────────────┐    │
│  │   Chat UI        │              │   Voice UI       │    │
│  │  (HTML/CSS/JS)   │              │  (STT + TTS)     │    │
│  └──────────────────┘              └──────────────────┘    │
└─────────────────────────────────────────────────────────────┘
                            │
                            │ REST API
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                     FastAPI Backend                         │
│  ┌──────────────────────────────────────────────────────┐   │
│  │              API Endpoints Layer                     │   │
│  └──────────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────────┐   │
│  │           Interview Session Manager                  │   │
│  │  - Tracks conversation state                         │   │
│  │  - Manages question flow                             │   │
│  │  - Enforces follow-up limits                         │   │
│  └──────────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  Prompt Generator  │  Persona Handler  │  Feedback   │   │
│  │  - System prompts  │  - Detects style  │  Engine     │   │
│  │  - Follow-ups      │  - Adapts tone    │  - Scoring  │   │
│  └──────────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────────┐   │
│  │              Ollama Client Layer                     │   │
│  │  - HTTP communication with Ollama                    │   │
│  │  - Retry logic and error handling                    │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                            │
                            │ HTTP API
                            ▼
┌──────────────────────────────────────────────────────────┐
│                    Ollama Server                             │
│  ┌──────────────────────────────────────────────────────┐  │
│  │   Local LLM (llama3.1:8b / mistral:7b / qwen2.5:7b) │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                   SQLite Database                            │
│  - Session history                                           │
│  - Conversation transcripts                                  │
│  - Feedback reports                                          │
└─────────────────────────────────────────────────────────────┘
```

### Design Decisions

**Why FastAPI?**
- **Performance**: Async support enables handling multiple concurrent interview sessions
- **Developer Experience**: Auto-generated API documentation at `/docs`
- **Type Safety**: Built-in Pydantic integration for data validation
- **Modern**: Native WebSocket support for future real-time features

**Why Ollama?**
- **Privacy**: All data stays local - no external API calls or data sharing
- **Cost**: No per-token charges - unlimited usage once installed
- **Speed**: Local inference is faster than API calls for small models
- **Flexibility**: Easy to swap models or experiment with different LLMs
- **Offline**: Works without internet connection

**Why Session-Based Architecture?**
- **Context Preservation**: Maintains full conversation history for intelligent follow-ups
- **State Management**: Tracks progress through interview questions and follow-up counts
- **Persistence**: Enables interview history and progress tracking over time
- **Scalability**: Sessions can be distributed across multiple servers if needed

**Why Persona Detection?**
- **Adaptability**: System responds appropriately to different communication styles
- **User Experience**: Reduces frustration for confused users, respects efficient users
- **Realism**: Mimics how real interviewers adapt to candidate behavior
- **Intelligence**: Demonstrates context-aware behavior beyond simple Q&A

### Key Components

#### 1. Role Loader (`services/role_loader.py`)
- Loads interview questions from `config/roles.json`
- Validates role configurations
- Provides role-specific evaluation criteria
- Supports easy addition of new roles

#### 2. Prompt Generator (`services/prompt_generator.py`)
- Creates system prompts for interviewer persona
- Generates follow-up question prompts based on user responses
- Formats feedback evaluation prompts with scoring rubrics
- Handles variable substitution and context injection

#### 3. Persona Handler (`services/persona_handler.py`)
Detects and adapts to four user personas:
- **Confused**: Short answers (<30 words), asks questions → Provides guidance
- **Efficient**: Direct, concise responses → Minimizes back-and-forth
- **Chatty**: Long answers (>200 words), off-topic → Politely redirects
- **Edge Case**: Invalid inputs, out-of-scope → Clear boundaries

#### 4. Interview Session Manager (`services/interview_session_manager.py`)
- Creates and manages interview sessions
- Tracks conversation state (current question, follow-up count)
- Enforces max 3 follow-ups per question rule
- Coordinates between all service components
- Determines when to ask follow-ups vs. move to next question

#### 5. Feedback Engine (`services/feedback_engine.py`)
- Generates structured performance feedback using LLM
- Calculates scores (1-5) for:
  - Communication (clarity, conciseness, articulation)
  - Technical Knowledge (accuracy, depth, relevance)
  - Structure (organization, examples, completeness)
- Extracts top 3 strengths and improvements
- Ensures feedback generation completes within 10 seconds

#### 6. Ollama Client (`services/ollama_client.py`)
- HTTP client for Ollama API (`http://localhost:11434/api/generate`)
- Implements retry logic with exponential backoff
- Health check to verify Ollama availability
- Structured output parsing for JSON responses

#### 7. Storage Service (`storage/storage_service.py`)
- SQLite database operations
- Saves sessions, messages, and feedback
- Retrieves interview history and transcripts
- Handles database initialization and migrations

## Usage Guide

### Basic Interview Flow

1. **Select a Role**: Choose from the dropdown menu (Backend Engineer, Sales Associate, Retail Associate)
2. **Start Interview**: Click "Start Interview" button
3. **Answer Questions**: Type your responses thoughtfully
4. **Follow-up Questions**: The AI may ask up to 3 follow-ups per question if your answer needs more detail
5. **End Interview**: Click "End Interview" when ready
6. **Review Feedback**: Receive detailed performance analysis with scores and recommendations
7. **Track Progress**: View your interview history to see improvement over time

### Understanding Feedback Scores

Each interview is scored on three dimensions (1-5 scale):

**Communication Score:**
- 5: Exceptionally clear, concise, and articulate
- 4: Clear and well-structured with minor improvements possible
- 3: Generally understandable but could be more concise or clear
- 2: Somewhat unclear or rambling
- 1: Difficult to understand or very disorganized

**Technical Knowledge Score:**
- 5: Demonstrates deep expertise with accurate, detailed responses
- 4: Strong knowledge with good examples
- 3: Adequate knowledge but lacks depth or examples
- 2: Limited knowledge or some inaccuracies
- 1: Significant gaps in knowledge

**Structure Score:**
- 5: Perfectly organized with clear introduction, body, and conclusion
- 4: Well-structured with good flow
- 3: Adequate structure but could be better organized
- 2: Somewhat disorganized or incomplete
- 1: Lacks structure or misses key points

### Tips for Better Scores

**For Communication:**
- Be clear and concise - avoid rambling
- Use specific examples to illustrate points
- Structure answers with beginning, middle, and end

**For Technical Knowledge:**
- Provide specific details and examples
- Explain your reasoning and thought process
- Demonstrate understanding beyond surface level

**For Structure:**
- Answer all parts of the question
- Use frameworks (e.g., STAR method for behavioral questions)
- Organize thoughts before responding

### Persona Adaptation

The system detects your communication style and adapts:

**If you're confused or uncertain:**
- System provides clarifying questions
- Offers examples and guidance
- Breaks down complex questions

**If you prefer efficiency:**
- System keeps interactions concise
- Minimizes unnecessary dialogue
- Focuses on core questions

**If you tend to be chatty:**
- System politely redirects off-topic responses
- Helps you stay focused on the question
- Encourages conciseness

## API Documentation

### Base URL
```
http://localhost:8000/api
```

### Interactive Documentation
FastAPI provides auto-generated interactive API docs:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

### Endpoints

#### 1. Start Interview

**POST** `/api/start`

Start a new interview session for a specific role.

**Request Body:**
```json
{
  "role": "backend_engineer",
  "mode": "chat"
}
```

**Parameters:**
- `role` (string, required): One of `backend_engineer`, `sales_associate`, `retail_associate`
- `mode` (string, required): One of `chat`, `voice`

**Response (200 OK):**
```json
{
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "question": "Tell me about your experience with backend development.",
  "question_number": 1,
  "total_questions": 8
}
```

**Example:**
```bash
curl -X POST http://localhost:8000/api/start \
  -H "Content-Type: application/json" \
  -d '{"role": "backend_engineer", "mode": "chat"}'
```

#### 2. Submit Answer

**POST** `/api/answer`

Submit an answer to the current question and receive the next question or follow-up.

**Request Body:**
```json
{
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "answer": "I have 3 years of experience building REST APIs with Python and FastAPI..."
}
```

**Response Types:**

**Next Question (200 OK):**
```json
{
  "type": "question",
  "content": "How do you handle database migrations in production?",
  "question_number": 2,
  "total_questions": 8
}
```

**Follow-up Question (200 OK):**
```json
{
  "type": "followup",
  "content": "Can you provide a specific example of a challenging API you built?",
  "question_number": 1,
  "followup_count": 1
}
```

**Interview Complete (200 OK):**
```json
{
  "type": "complete",
  "message": "Interview complete! Click 'Get Feedback' to see your results.",
  "session_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

**Example:**
```bash
curl -X POST http://localhost:8000/api/answer \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "550e8400-e29b-41d4-a716-446655440000",
    "answer": "I have extensive experience with FastAPI..."
  }'
```

#### 3. Get Feedback

**POST** `/api/feedback`

Generate and retrieve detailed performance feedback for a completed interview.

**Request Body:**
```json
{
  "session_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

**Response (200 OK):**
```json
{
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "scores": {
    "communication": 4,
    "technical_knowledge": 3,
    "structure": 4,
    "average": 3.67
  },
  "strengths": [
    "Clear and articulate communication style",
    "Good use of specific examples from experience",
    "Well-structured responses with logical flow"
  ],
  "improvements": [
    "Provide more technical depth in API design discussions",
    "Include specific metrics or outcomes from projects",
    "Address scalability considerations more explicitly"
  ],
  "overall_feedback": "You demonstrated strong communication skills and provided well-structured answers. Your responses showed practical experience, though adding more technical depth and specific metrics would strengthen your answers. Focus on discussing system design trade-offs and scalability considerations in future interviews."
}
```

**Example:**
```bash
curl -X POST http://localhost:8000/api/feedback \
  -H "Content-Type: application/json" \
  -d '{"session_id": "550e8400-e29b-41d4-a716-446655440000"}'
```

#### 4. Get Interview History

**GET** `/api/history`

Retrieve all past interview sessions.

**Response (200 OK):**
```json
{
  "sessions": [
    {
      "session_id": "550e8400-e29b-41d4-a716-446655440000",
      "role": "backend_engineer",
      "date": "2024-11-24T10:30:00Z",
      "score": 3.67,
      "status": "completed"
    },
    {
      "session_id": "660e8400-e29b-41d4-a716-446655440001",
      "role": "sales_associate",
      "date": "2024-11-23T14:15:00Z",
      "score": 4.0,
      "status": "completed"
    }
  ],
  "total_interviews": 2,
  "average_score": 3.84
}
```

**Example:**
```bash
curl http://localhost:8000/api/history
```

#### 5. Get Session Details

**GET** `/api/session/{session_id}`

Retrieve full transcript and feedback for a specific session.

**Response (200 OK):**
```json
{
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "role": "backend_engineer",
  "mode": "chat",
  "created_at": "2024-11-24T10:30:00Z",
  "completed_at": "2024-11-24T10:45:00Z",
  "transcript": [
    {
      "type": "question",
      "content": "Tell me about your experience with backend development.",
      "timestamp": "2024-11-24T10:30:05Z"
    },
    {
      "type": "answer",
      "content": "I have 3 years of experience...",
      "timestamp": "2024-11-24T10:31:20Z"
    }
  ],
  "feedback": {
    "scores": { "communication": 4, "technical_knowledge": 3, "structure": 4 },
    "strengths": ["..."],
    "improvements": ["..."],
    "overall_feedback": "..."
  }
}
```

**Example:**
```bash
curl http://localhost:8000/api/session/550e8400-e29b-41d4-a716-446655440000
```

### Error Responses

**400 Bad Request:**
```json
{
  "detail": "Invalid role. Must be one of: backend_engineer, sales_associate, retail_associate"
}
```

**404 Not Found:**
```json
{
  "detail": "Session not found"
}
```

**500 Internal Server Error:**
```json
{
  "detail": "Ollama service unavailable. Please ensure Ollama is running."
}
```

### Sample Interview Flow

Here's a complete example of an interview session:

```bash
# 1. Start interview
SESSION_ID=$(curl -s -X POST http://localhost:8000/api/start \
  -H "Content-Type: application/json" \
  -d '{"role": "backend_engineer", "mode": "chat"}' \
  | jq -r '.session_id')

echo "Session ID: $SESSION_ID"

# 2. Answer first question
curl -X POST http://localhost:8000/api/answer \
  -H "Content-Type: application/json" \
  -d "{
    \"session_id\": \"$SESSION_ID\",
    \"answer\": \"I have 3 years of experience building scalable REST APIs with Python, FastAPI, and PostgreSQL. I've worked on microservices architectures handling millions of requests per day.\"
  }"

# 3. Continue answering questions...
# (Repeat for each question)

# 4. Get feedback
curl -X POST http://localhost:8000/api/feedback \
  -H "Content-Type: application/json" \
  -d "{\"session_id\": \"$SESSION_ID\"}"

# 5. View history
curl http://localhost:8000/api/history
```

## Project Structure

```
Interview_Practice/
├── backend/
│   ├── api/
│   │   └── endpoints.py          # FastAPI route handlers
│   ├── config/
│   │   └── roles.json            # Interview questions by role
│   ├── models/
│   │   └── data_models.py        # Pydantic models
│   ├── services/
│   │   ├── ollama_client.py      # LLM communication
│   │   ├── role_loader.py        # Role configuration loader
│   │   ├── prompt_generator.py   # Prompt templates
│   │   ├── persona_handler.py    # User persona detection
│   │   ├── interview_session_manager.py  # Session orchestration
│   │   ├── feedback_engine.py    # Feedback generation
│   │   └── voice_service.py      # Speech-to-text & text-to-speech
│   ├── storage/
│   │   ├── database.py           # Database schema
│   │   └── storage_service.py    # Data persistence
│   ├── main.py                   # Application entry point
│   ├── requirements.txt          # Python dependencies
│   └── *.py                      # Test and verification scripts
├── frontend/
│   ├── index.html                # Main UI
│   ├── styles.css                # Styling
│   └── app.js                    # Frontend logic
├── .kiro/
│   └── specs/
│       └── interview-practice-partner/
│           ├── requirements.md   # Feature requirements
│           ├── design.md         # Architecture design
│           └── tasks.md          # Implementation plan
├── README.md                     # This file
├── FRONTEND_QUICKSTART.md        # Frontend testing guide
└── VOICE_MODE_QUICKSTART.md      # Voice mode setup guide
```

## Configuration

### Environment Variables

Create a `.env` file in the `backend/` directory (optional):

```bash
# Ollama Configuration
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.1:8b

# Server Configuration
HOST=0.0.0.0
PORT=8000

# Database
DATABASE_PATH=interview_practice.db
```

### Customizing Interview Roles

Edit `backend/config/roles.json` to customize or add new roles:

```json
{
  "backend_engineer": {
    "display_name": "Backend Engineer",
    "questions": [
      "Tell me about your experience with backend development.",
      "How do you approach API design?",
      "Describe a challenging technical problem you solved.",
      "How do you ensure code quality and maintainability?",
      "What's your experience with databases and data modeling?",
      "How do you handle errors and edge cases in your code?",
      "Describe your experience with testing and CI/CD.",
      "How do you approach system scalability?"
    ],
    "evaluation_criteria": {
      "technical_depth": "Demonstrates understanding of backend concepts",
      "problem_solving": "Shows analytical thinking and solution design",
      "best_practices": "Mentions testing, documentation, code quality"
    }
  }
}
```

**To add a new role:**

1. Add role configuration to `config/roles.json`
2. Update frontend dropdown in `frontend/index.html`:
```html
<option value="your_new_role">Your New Role</option>
```
3. Update `formatRoleName()` in `frontend/app.js`:
```javascript
function formatRoleName(role) {
    const roleNames = {
        'backend_engineer': 'Backend Engineer',
        'sales_associate': 'Sales Associate',
        'retail_associate': 'Retail Associate',
        'your_new_role': 'Your New Role'
    };
    return roleNames[role] || role;
}
```

### Changing LLM Model

To use a different Ollama model:

1. Pull the model:
```bash
ollama pull mistral:7b
```

2. Update `backend/services/ollama_client.py` or set environment variable:
```python
# In code
self.model = "mistral:7b"

# Or in .env
OLLAMA_MODEL=mistral:7b
```

**Recommended Models:**
- `llama3.1:8b` - Best overall quality (4.7GB)
- `mistral:7b` - Faster responses (4.1GB)
- `qwen2.5:7b` - Good for multilingual (4.4GB)
- `llama3.2:3b` - Lightweight option (2GB)

## Troubleshooting

### Common Issues

#### "Failed to start interview" or "Ollama service unavailable"

**Cause**: Ollama server is not running or model is not loaded.

**Solutions:**
1. Check if Ollama is running:
```bash
# Check service status
ollama list

# If not running, start it
ollama serve
```

2. Verify model is installed:
```bash
ollama list
# Should show your model (e.g., llama3.1:8b)

# If missing, pull it
ollama pull llama3.1:8b
```

3. Test Ollama directly:
```bash
curl http://localhost:11434/api/generate -d '{
  "model": "llama3.1:8b",
  "prompt": "Hello",
  "stream": false
}'
```

4. Check backend logs for specific errors

#### Port Already in Use

**Cause**: Another application is using port 8000.

**Solutions:**
1. Find and stop the process using port 8000:
```bash
# Windows
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# macOS/Linux
lsof -ti:8000 | xargs kill -9
```

2. Or change the port in `backend/main.py`:
```python
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)  # Changed to 8001
```

Then update `API_BASE_URL` in `frontend/app.js`:
```javascript
const API_BASE_URL = 'http://localhost:8001/api';
```

#### Database Errors

**Cause**: Corrupted database or schema mismatch.

**Solutions:**
1. Reset the database:
```bash
cd backend
del interview_practice.db  # Windows
rm interview_practice.db   # macOS/Linux
python main.py  # Will recreate database
```

2. Or manually reinitialize:
```bash
python -c "from storage.database import init_db; init_db()"
```

#### Slow Response Times

**Cause**: LLM model is too large for your hardware or Ollama is not optimized.

**Solutions:**
1. Use a smaller model:
```bash
ollama pull llama3.2:3b  # Smaller, faster model
```

2. Check system resources:
```bash
# Monitor CPU/RAM usage
# Ensure at least 8GB RAM available for 7-8B models
```

3. Adjust Ollama settings (create/edit `~/.ollama/config.json`):
```json
{
  "num_gpu": 1,
  "num_thread": 4
}
```

#### "Answer too long" or Validation Errors

**Cause**: Answer exceeds 2000 word limit or contains invalid characters.

**Solutions:**
1. Keep answers under 2000 words
2. Avoid special characters or formatting in answers
3. Check browser console for specific validation errors

#### Frontend Not Loading

**Cause**: Backend not serving static files or CORS issues.

**Solutions:**
1. Verify backend is running:
```bash
curl http://localhost:8000/
```

2. Check browser console for errors (F12)

3. Clear browser cache and reload

4. Ensure `frontend/` directory is in the correct location relative to `backend/main.py`

#### Voice Mode Not Working

**Cause**: Speech-to-text or text-to-speech dependencies not installed.

**Solutions:**
See [VOICE_MODE_QUICKSTART.md](VOICE_MODE_QUICKSTART.md) for detailed setup instructions.

### Getting Help

If you encounter issues not covered here:

1. **Check Logs**: Look at backend console output for error messages
2. **Verify Setup**: Run `python backend/verify_ollama.py` to check configuration
3. **Test Components**: Run individual test scripts in `backend/test_*.py`
4. **Review Documentation**: Check the design specs in `.kiro/specs/`
5. **Open an Issue**: Report bugs on GitHub with logs and system info

### Debug Mode

Enable debug logging in `backend/main.py`:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

This will show detailed information about:
- API requests and responses
- Ollama communication
- Database operations
- Session state changes

## Development

### Running Tests

The project includes comprehensive test coverage:

```bash
cd backend

# Run all tests
python -m pytest

# Run specific test file
python test_ollama_client.py
python test_session_manager.py
python test_feedback_engine.py

# Run with verbose output
python -m pytest -v

# Run with coverage report
python -m pytest --cov=services --cov=api --cov=storage
```

**Test Files:**
- `test_ollama_client.py` - LLM communication tests
- `test_role_loader.py` - Role configuration tests
- `test_prompt_generator.py` - Prompt template tests
- `test_persona_handler.py` - Persona detection tests
- `test_session_manager.py` - Session management tests
- `test_feedback_engine.py` - Feedback generation tests
- `test_storage.py` - Database operations tests
- `test_api_endpoints.py` - API integration tests
- `test_validation.py` - Input validation tests
- `test_voice_service.py` - Voice mode tests (optional)

### Verification Scripts

Run these to verify individual components:

```bash
cd backend

# Verify Ollama connection and model
python verify_ollama.py

# Test speech-to-text (if voice mode installed)
python verify_speech_to_text.py

# Test text-to-speech (if voice mode installed)
python verify_text_to_speech.py
```

### Code Structure

The codebase follows clean architecture principles:

**Layers:**
1. **API Layer** (`api/endpoints.py`) - HTTP request handling
2. **Service Layer** (`services/`) - Business logic
3. **Storage Layer** (`storage/`) - Data persistence
4. **Models Layer** (`models/`) - Data structures

**Key Principles:**
- **Separation of Concerns**: Each component has a single responsibility
- **Dependency Injection**: Services are loosely coupled
- **Type Safety**: Pydantic models ensure data validation
- **Testability**: Components can be tested in isolation

### Adding New Features

**Example: Adding a new interview question type**

1. Update `config/roles.json` with new questions
2. Modify `services/prompt_generator.py` if special prompts needed
3. Update `services/session_manager.py` if flow logic changes
4. Add tests in `test_session_manager.py`
5. Update frontend if UI changes needed

### Performance Optimization

**Tips for improving response times:**

1. **Use smaller models** for faster inference
2. **Cache common prompts** to reduce generation time
3. **Implement request queuing** for concurrent sessions
4. **Use async/await** for I/O operations
5. **Add Redis** for session state if scaling beyond single server

### Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Write tests for new functionality
4. Ensure all tests pass (`python -m pytest`)
5. Commit changes (`git commit -m 'Add amazing feature'`)
6. Push to branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

## Additional Documentation

- **[Frontend Quick Start](FRONTEND_QUICKSTART.md)** - Detailed frontend testing and customization guide
- **[Voice Mode Setup](VOICE_MODE_QUICKSTART.md)** - Complete voice mode installation and usage
- **[Backend README](backend/README.md)** - Backend-specific documentation
- **[Requirements Document](.kiro/specs/interview-practice-partner/requirements.md)** - Feature requirements and acceptance criteria
- **[Design Document](.kiro/specs/interview-practice-partner/design.md)** - Architecture and design decisions
- **[Implementation Plan](.kiro/specs/interview-practice-partner/tasks.md)** - Development task breakdown

## Available Roles

The system currently supports three job roles, each with 8-10 tailored interview questions:

### Backend Engineer
**Focus Areas:**
- System design and architecture
- API design and best practices
- Database modeling and optimization
- Code quality and testing
- Scalability and performance
- Error handling and debugging

**Sample Questions:**
- "Tell me about your experience with backend development."
- "How do you approach API design?"
- "Describe a challenging technical problem you solved."
- "How do you ensure code quality and maintainability?"

### Sales Associate
**Focus Areas:**
- Customer relationship management
- Sales techniques and closing
- Product knowledge
- Objection handling
- Communication skills
- Goal achievement

**Sample Questions:**
- "Tell me about your sales experience."
- "How do you handle difficult customers?"
- "Describe a time you exceeded your sales targets."
- "How do you build rapport with customers?"

### Retail Associate
**Focus Areas:**
- Customer service excellence
- Product knowledge
- Store operations
- Team collaboration
- Problem-solving
- Multitasking

**Sample Questions:**
- "Tell me about your retail experience."
- "How do you handle multiple customers at once?"
- "Describe a time you resolved a customer complaint."
- "How do you stay motivated during slow periods?"

## Voice Mode (Optional)

The system supports optional voice interaction using speech-to-text and text-to-speech.

**Setup:**
See [VOICE_MODE_QUICKSTART.md](VOICE_MODE_QUICKSTART.md) for complete installation instructions.

**Quick Setup:**
```bash
cd backend
pip install faster-whisper piper-tts
python verify_speech_to_text.py
python verify_text_to_speech.py
```

**Usage:**
1. Select "Voice" mode when starting an interview
2. Click the microphone button to record your answer
3. The system will transcribe your speech and respond with audio

## System Requirements

**Minimum:**
- CPU: 4 cores
- RAM: 8GB
- Storage: 10GB free space
- OS: Windows 10+, macOS 10.15+, or Linux

**Recommended:**
- CPU: 8 cores
- RAM: 16GB
- Storage: 20GB free space
- GPU: Optional, but improves LLM inference speed

**For Voice Mode:**
- Microphone for speech input
- Speakers/headphones for audio output
- Additional 2GB storage for voice models

## Performance Benchmarks

Typical response times on recommended hardware:

| Operation | Time |
|-----------|------|
| Start interview | < 1s |
| Process answer (no follow-up) | 2-3s |
| Generate follow-up question | 3-5s |
| Generate feedback | 5-10s |
| Load history | < 0.5s |

**Factors affecting performance:**
- LLM model size (larger = slower but better quality)
- Hardware specs (CPU/GPU/RAM)
- Answer length (longer answers take more time to process)
- Concurrent sessions (multiple users)

## Security and Privacy

**Data Privacy:**
- All data stays on your local machine
- No external API calls or data transmission
- Interview transcripts stored locally in SQLite
- No telemetry or analytics

**Best Practices:**
- Keep Ollama and dependencies updated
- Use strong passwords if deploying to network
- Regularly backup `interview_practice.db`
- Review and clear old sessions periodically

**For Production Deployment:**
- Add authentication (e.g., JWT tokens)
- Enable HTTPS with SSL certificates
- Implement rate limiting
- Add input sanitization
- Use environment variables for secrets

## Roadmap

**Planned Features:**
- [ ] Multi-language support
- [ ] Custom role creation via UI
- [ ] Video interview mode with body language analysis
- [ ] Peer comparison and benchmarking
- [ ] Adaptive difficulty based on performance
- [ ] Interview scheduling and reminders
- [ ] Mobile app (iOS/Android)
- [ ] Team/organization features
- [ ] Advanced analytics and progress tracking
- [ ] Integration with job boards

## FAQ

**Q: Do I need an internet connection?**
A: No, once Ollama and the model are installed, everything runs locally offline.

**Q: Can I use this for other types of interviews?**
A: Yes! Add custom roles in `config/roles.json` with your own questions.

**Q: How accurate is the feedback?**
A: Feedback quality depends on the LLM model. llama3.1:8b provides good quality. Larger models (13B+) give better feedback but require more resources.

**Q: Can multiple people use this simultaneously?**
A: Yes, the system supports concurrent sessions. Performance depends on your hardware.

**Q: Is my interview data private?**
A: Yes, everything runs locally. No data is sent to external servers.

**Q: Can I export my interview history?**
A: Currently, data is stored in SQLite. You can query the database directly or add export functionality.

**Q: What if I disagree with the feedback?**
A: The feedback is AI-generated and may not always be perfect. Use it as one data point among many in your preparation.

**Q: Can I practice with a friend?**
A: The current version is single-user. Multi-user features are on the roadmap.

## Contributing

We welcome contributions! Here's how you can help:

**Types of Contributions:**
- Bug fixes and issue reports
- New interview roles and questions
- Performance optimizations
- Documentation improvements
- Test coverage expansion
- Feature implementations

**Process:**
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Write tests for new functionality
4. Ensure all tests pass (`python -m pytest`)
5. Follow existing code style and conventions
6. Commit with clear messages (`git commit -m 'Add amazing feature'`)
7. Push to your branch (`git push origin feature/amazing-feature`)
8. Open a Pull Request with description of changes

**Code Style:**
- Follow PEP 8 for Python code
- Use type hints for function signatures
- Write docstrings for public methods
- Keep functions focused and testable
- Add comments for complex logic

## License

MIT License

Copyright (c) 2024 Interview Practice Partner

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

## Acknowledgments

**Built With:**
- [FastAPI](https://fastapi.tiangolo.com/) - Modern Python web framework
- [Ollama](https://ollama.ai/) - Local LLM inference engine
- [Pydantic](https://pydantic-docs.helpmanual.io/) - Data validation
- [SQLite](https://www.sqlite.org/) - Embedded database
- [Uvicorn](https://www.uvicorn.org/) - ASGI server

**Inspired By:**
- Real interview preparation needs
- The power of local-first AI applications
- Open-source AI democratization

**Special Thanks:**
- The Ollama team for making local LLMs accessible
- The FastAPI community for excellent documentation
- All contributors and users providing feedback

## Support

**Need Help?**
- Check the [Troubleshooting](#troubleshooting) section
- Review [Additional Documentation](#additional-documentation)
- Run verification scripts to diagnose issues
- Open an issue on GitHub with details

**Found a Bug?**
Please open an issue with:
- Description of the problem
- Steps to reproduce
- Expected vs actual behavior
- System information (OS, Python version, Ollama version)
- Relevant logs or error messages

**Have a Feature Request?**
Open an issue with:
- Clear description of the feature
- Use case and benefits
- Any implementation ideas

---

**Happy Practicing! 🚀**

*Prepare for your dream job with AI-powered interview practice.*
