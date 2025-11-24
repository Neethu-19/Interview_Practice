# Interview Practice Partner 🎯

An AI-powered mock interview system that provides adaptive questioning and detailed feedback to help you prepare for job interviews.

## Features

- **Multiple Job Roles**: Practice for Backend Engineer, Sales Associate, or Retail Associate positions
- **Adaptive Questioning**: AI asks follow-up questions based on your answers
- **Detailed Feedback**: Get scored on communication, technical knowledge, and structure
- **Interview History**: Track your progress over time
- **Modern Web UI**: Clean, responsive interface for seamless practice
- **Local & Private**: Runs entirely on your machine using Ollama

## Quick Start

### Prerequisites

1. **Python 3.8+** installed
2. **Ollama** installed and running ([Download here](https://ollama.ai/download))
3. A compatible LLM model (llama3.1:8b, mistral:7b, or qwen2.5:7b)

### Installation

1. Clone this repository:
```bash
git clone https://github.com/Neethu-19/Interview_Practice.git
cd Interview_Practice
```

2. Install Python dependencies:
```bash
cd backend
pip install fastapi uvicorn requests pydantic
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

## Usage

1. **Select a Role**: Choose from the dropdown menu
2. **Start Interview**: Click the button to begin
3. **Answer Questions**: Type your responses and press Enter
4. **Get Feedback**: End the interview to receive detailed performance analysis
5. **Track Progress**: View your interview history and improvement over time

## Project Structure

```
Interview_Practice/
├── backend/
│   ├── api/              # FastAPI endpoints
│   ├── services/         # Core business logic
│   ├── storage/          # Database and persistence
│   ├── models/           # Data models
│   ├── config/           # Role configurations
│   └── main.py           # Application entry point
├── frontend/
│   ├── index.html        # Main UI
│   ├── styles.css        # Styling
│   └── app.js            # Frontend logic
```

## Architecture

- **Backend**: FastAPI REST API with modular service architecture
- **Frontend**: Vanilla JavaScript SPA with clean, modern design
- **AI Engine**: Ollama for local LLM inference
- **Storage**: SQLite for session and feedback persistence

## Key Components

- **Role Loader**: Manages interview questions for different job roles
- **Prompt Generator**: Creates context-aware prompts for the LLM
- **Persona Handler**: Simulates different interviewer personalities
- **Session Manager**: Tracks interview state and conversation flow
- **Feedback Engine**: Analyzes responses and generates detailed feedback

## Configuration

Edit `backend/config/roles.json` to:
- Add new job roles
- Customize interview questions
- Adjust difficulty levels

## Development

### Running Tests

```bash
cd backend
python -m pytest
```

### Adding New Roles

1. Edit `backend/config/roles.json`
2. Add role to frontend dropdown in `frontend/index.html`
3. Update `formatRoleName()` in `frontend/app.js`

## Documentation

- [Frontend Quick Start](FRONTEND_QUICKSTART.md) - Detailed frontend testing guide
- [Backend README](backend/README.md) - Backend architecture and API docs
- [Design Specs](.kiro/specs/interview-practice-partner/) - Complete design documentation

## Troubleshooting

### "Failed to start interview"
- Ensure Ollama is running: `ollama serve`
- Verify model is installed: `ollama list`
- Check backend logs for errors

### Port already in use
Change the port in `backend/main.py`:
```python
uvicorn.run(app, host="0.0.0.0", port=8001)
```

### Database errors
Delete `backend/interviews.db` to reset the database

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

MIT License - feel free to use this project for learning and practice.

## Acknowledgments

- Built with [FastAPI](https://fastapi.tiangolo.com/)
- Powered by [Ollama](https://ollama.ai/)
- Designed for real-world interview preparation

---

**Happy Practicing! 🚀**
