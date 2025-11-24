# Frontend Quick Start Guide

## Testing the Chat UI

### 1. Start the Backend Server

Make sure Ollama is running, then start the FastAPI server:

```bash
cd backend
python main.py
```

The server will start on `http://localhost:8000`

### 2. Access the Frontend

Open your web browser and navigate to:
```
http://localhost:8000
```

You should see the Interview Practice Partner interface.

### 3. Start an Interview

1. Select a role from the dropdown (Backend Engineer, Sales Associate, or Retail Associate)
2. Click "Start Interview"
3. The AI interviewer will ask you the first question
4. Type your answer in the text box and click "Send" (or press Enter)
5. Continue answering questions - the AI may ask follow-up questions
6. Click "End Interview" when you're ready to get feedback

### 4. View Feedback

After ending the interview, you'll see:
- Performance scores (1-5) for Communication, Technical Knowledge, and Structure
- Your top 3 strengths
- Top 3 areas for improvement with actionable advice
- Overall feedback summary

### 5. View History

Click "View History" to see all your past interviews with scores and dates.

## Features to Test

### Chat Interface
- ✅ Message bubbles for interviewer and user
- ✅ Follow-up questions highlighted in yellow
- ✅ Question counter showing progress
- ✅ Smooth scrolling and animations

### Role Selection
- ✅ Dropdown with 3 roles
- ✅ Start button enabled only when role is selected

### Feedback Display
- ✅ Score cards with visual styling
- ✅ Strengths and improvements as bullet lists
- ✅ Overall feedback paragraph
- ✅ Options to start new interview or view history

### History View
- ✅ List of past interviews
- ✅ Click to view detailed feedback
- ✅ Shows role, date, score, and status

### Error Handling
- ✅ Loading overlay during API calls
- ✅ Error toast notifications
- ✅ Graceful handling of network issues

## Keyboard Shortcuts

- **Enter**: Send answer (in chat input)
- **Shift+Enter**: New line (in chat input)

## Troubleshooting

### Frontend doesn't load
- Check that the backend server is running
- Verify you're accessing `http://localhost:8000` (not 8080 or other port)
- Check browser console for errors

### "Failed to start interview"
- Ensure Ollama is running: `ollama serve`
- Verify a model is available: `ollama list`
- Check backend logs for errors

### Styling looks broken
- Hard refresh the page (Ctrl+F5 or Cmd+Shift+R)
- Clear browser cache
- Check that `styles.css` loaded correctly in browser dev tools

## Next Steps

After testing the basic functionality:
1. Try different user personas (confused, efficient, chatty)
2. Test with various answer lengths
3. Complete multiple interviews to build history
4. Test on mobile devices for responsive design

## Development Mode

To modify the frontend while testing:

1. Make changes to HTML/CSS/JS files
2. Refresh the browser (no need to restart backend)
3. Use browser dev tools to debug
4. Check console for JavaScript errors
5. Use Network tab to inspect API calls

Enjoy practicing your interviews! 🎯
