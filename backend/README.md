# Interview Practice Partner - Backend

AI-powered mock interview system built with FastAPI and Ollama.

## Setup

### Prerequisites
- Python 3.10 or higher
- Ollama installed and running locally
- Ollama model downloaded (e.g., `ollama pull llama3.1:8b`)

### Installation

1. Create and activate virtual environment:
```bash
python -m venv venv

# On Windows
venv\Scripts\activate

# On macOS/Linux
source venv/bin/activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure environment:
```bash
copy .env.example .env
# Edit .env with your configuration
```

### Running the Application

```bash
python main.py
```

Or with uvicorn directly:
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`

API documentation: `http://localhost:8000/docs`

## Project Structure

```
backend/
├── api/          # FastAPI endpoints and routes
├── config/       # Configuration management
├── models/       # Pydantic data models
├── services/     # Business logic services
├── storage/      # Data persistence layer
├── main.py       # Application entry point
└── requirements.txt
```

## Development

The project follows a modular architecture:
- **API Layer**: REST endpoints for client interaction
- **Services**: Business logic (session management, feedback generation, etc.)
- **Models**: Data validation and structure
- **Storage**: Database operations and persistence
- **Config**: Environment and application configuration
