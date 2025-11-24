# Interview Practice Partner - Frontend

A simple, clean web interface for the Interview Practice Partner application.

## Features

- **Role Selection**: Choose from Backend Engineer, Sales Associate, or Retail Associate roles
- **Interactive Chat**: Real-time conversation with the AI interviewer
- **Follow-up Questions**: Visual distinction for follow-up questions
- **Structured Feedback**: Detailed performance scores and actionable recommendations
- **Interview History**: View past interviews and track progress over time
- **Responsive Design**: Works on desktop and mobile devices

## Getting Started

### Prerequisites

- The backend server must be running on `http://localhost:8000`
- Ollama must be running with a compatible model (llama3.1:8b, mistral:7b, or qwen2.5:7b)

### Running the Frontend

The frontend is automatically served by the FastAPI backend when you run:

```bash
cd backend
python main.py
```

Then open your browser and navigate to:
```
http://localhost:8000
```

### Alternative: Serve Separately

If you want to serve the frontend separately (e.g., for development):

```bash
cd frontend
python -m http.server 8080
```

Then update the `API_BASE_URL` in `app.js` if needed.

## Usage

### Starting an Interview

1. Select a role from the dropdown menu
2. Click "Start Interview"
3. Answer each question thoughtfully
4. The AI will ask follow-up questions if your answer needs more detail
5. Click "End Interview" when ready to receive feedback

### Viewing Feedback

After completing an interview, you'll see:
- **Performance Scores**: Communication, Technical Knowledge, and Structure (1-5 scale)
- **Strengths**: Top 3 things you did well
- **Areas for Improvement**: Top 3 areas with actionable advice
- **Overall Feedback**: Comprehensive assessment of your performance

### Viewing History

Click "View History" to see all your past interviews:
- Role practiced
- Date and time
- Overall score
- Session status

Click on any session to view its detailed feedback.

## File Structure

```
frontend/
├── index.html      # Main HTML structure
├── styles.css      # All styling and responsive design
├── app.js          # JavaScript logic and API integration
└── README.md       # This file
```

## API Integration

The frontend communicates with the backend via REST API:

- `POST /api/start` - Start a new interview session
- `POST /api/answer` - Submit an answer and get next question
- `POST /api/feedback` - Get final feedback for a session
- `GET /api/history` - Retrieve interview history
- `GET /api/session/{session_id}` - Get specific session details

## Customization

### Changing Colors

Edit `styles.css` to customize the color scheme. Main colors:
- Primary: `#667eea` (purple-blue)
- Secondary: `#764ba2` (purple)
- Background gradient: `linear-gradient(135deg, #667eea 0%, #764ba2 100%)`

### Adding New Roles

1. Add the role to the backend's `config/roles.json`
2. Update the role dropdown in `index.html`
3. Update the `formatRoleName()` function in `app.js`

### Modifying API Endpoint

Change the `API_BASE_URL` constant in `app.js`:

```javascript
const API_BASE_URL = 'http://your-server:port/api';
```

## Browser Support

- Chrome/Edge (latest)
- Firefox (latest)
- Safari (latest)
- Mobile browsers (iOS Safari, Chrome Mobile)

## Troubleshooting

### "Failed to start interview"
- Ensure the backend server is running
- Check that Ollama is running and has a model loaded
- Verify the API_BASE_URL is correct

### "Failed to load history"
- Check that the database file exists and is accessible
- Ensure you have completed at least one interview

### Styling Issues
- Clear browser cache
- Check browser console for CSS loading errors
- Ensure all files are in the correct directory

## Future Enhancements

- Voice mode support (speech-to-text and text-to-speech)
- Real-time typing indicators
- Progress tracking charts
- Export interview transcripts
- Dark mode toggle
- Keyboard shortcuts
