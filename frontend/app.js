// Configuration
const API_BASE_URL = 'http://localhost:8000/api';

// State Management
const state = {
    currentScreen: 'start',
    sessionId: null,
    currentRole: null,
    currentMode: 'chat',
    questionNumber: 0,
    isProcessing: false,
    voiceEnabled: false,
    isRecording: false,
    mediaRecorder: null,
    audioChunks: []
};

// DOM Elements
const elements = {
    // Screens
    startScreen: document.getElementById('startScreen'),
    chatScreen: document.getElementById('chatScreen'),
    feedbackScreen: document.getElementById('feedbackScreen'),
    historyScreen: document.getElementById('historyScreen'),
    
    // Start Screen
    roleSelect: document.getElementById('roleSelect'),
    startBtn: document.getElementById('startBtn'),
    historyBtn: document.getElementById('historyBtn'),
    chatModeBtn: document.getElementById('chatModeBtn'),
    voiceModeBtn: document.getElementById('voiceModeBtn'),
    voiceStatusMsg: document.getElementById('voiceStatusMsg'),
    
    // Chat Screen
    roleDisplay: document.getElementById('roleDisplay'),
    questionCounter: document.getElementById('questionCounter'),
    chatMessages: document.getElementById('chatMessages'),
    answerInput: document.getElementById('answerInput'),
    sendBtn: document.getElementById('sendBtn'),
    endBtn: document.getElementById('endBtn'),
    voiceControls: document.getElementById('voiceControls'),
    recordBtn: document.getElementById('recordBtn'),
    recordingStatus: document.getElementById('recordingStatus'),
    transcriptionPreview: document.getElementById('transcriptionPreview'),
    
    // Feedback Screen
    commScore: document.getElementById('commScore'),
    techScore: document.getElementById('techScore'),
    structScore: document.getElementById('structScore'),
    overallScore: document.getElementById('overallScore'),
    strengthsList: document.getElementById('strengthsList'),
    improvementsList: document.getElementById('improvementsList'),
    overallFeedback: document.getElementById('overallFeedback'),
    newInterviewBtn: document.getElementById('newInterviewBtn'),
    viewHistoryBtn: document.getElementById('viewHistoryBtn'),
    
    // History Screen
    historyList: document.getElementById('historyList'),
    backBtn: document.getElementById('backBtn'),
    
    // Overlays
    loadingOverlay: document.getElementById('loadingOverlay'),
    errorToast: document.getElementById('errorToast')
};

// Initialize App
function init() {
    setupEventListeners();
    checkVoiceAvailability();
    showScreen('start');
}

// Event Listeners
function setupEventListeners() {
    // Start Screen
    elements.roleSelect.addEventListener('change', handleRoleChange);
    elements.startBtn.addEventListener('click', handleStartInterview);
    elements.historyBtn.addEventListener('click', () => showHistoryScreen());
    elements.chatModeBtn.addEventListener('click', () => handleModeChange('chat'));
    elements.voiceModeBtn.addEventListener('click', () => handleModeChange('voice'));
    
    // Chat Screen
    elements.sendBtn.addEventListener('click', handleSendAnswer);
    elements.answerInput.addEventListener('keydown', handleInputKeydown);
    elements.endBtn.addEventListener('click', handleEndInterview);
    
    // Voice Controls
    elements.recordBtn.addEventListener('mousedown', handleRecordStart);
    elements.recordBtn.addEventListener('mouseup', handleRecordStop);
    elements.recordBtn.addEventListener('touchstart', handleRecordStart);
    elements.recordBtn.addEventListener('touchend', handleRecordStop);
    
    // Feedback Screen
    elements.newInterviewBtn.addEventListener('click', handleNewInterview);
    elements.viewHistoryBtn.addEventListener('click', () => showHistoryScreen());
    
    // History Screen
    elements.backBtn.addEventListener('click', () => showScreen('start'));
}

function handleRoleChange() {
    const role = elements.roleSelect.value;
    elements.startBtn.disabled = !role;
}

function handleInputKeydown(e) {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        handleSendAnswer();
    }
}

// Screen Management
function showScreen(screenName) {
    // Hide all screens
    document.querySelectorAll('.screen').forEach(screen => {
        screen.classList.remove('active');
    });
    
    // Show requested screen
    const screenMap = {
        'start': elements.startScreen,
        'chat': elements.chatScreen,
        'feedback': elements.feedbackScreen,
        'history': elements.historyScreen
    };
    
    if (screenMap[screenName]) {
        screenMap[screenName].classList.add('active');
        state.currentScreen = screenName;
    }
}

function showLoading(show = true) {
    if (show) {
        elements.loadingOverlay.classList.add('active');
    } else {
        elements.loadingOverlay.classList.remove('active');
    }
}

function showError(message) {
    elements.errorToast.textContent = message;
    elements.errorToast.classList.add('active');
    
    setTimeout(() => {
        elements.errorToast.classList.remove('active');
    }, 5000);
}

// API Functions
async function apiRequest(endpoint, method = 'GET', body = null) {
    try {
        const options = {
            method,
            headers: {
                'Content-Type': 'application/json'
            }
        };
        
        if (body) {
            options.body = JSON.stringify(body);
        }
        
        const response = await fetch(`${API_BASE_URL}${endpoint}`, options);
        
        if (!response.ok) {
            const errorData = await response.json().catch(() => ({}));
            throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
        }
        
        return await response.json();
    } catch (error) {
        console.error('API request failed:', error);
        throw error;
    }
}

// Interview Flow Functions
async function handleStartInterview() {
    const role = elements.roleSelect.value;
    if (!role || state.isProcessing) return;
    
    state.isProcessing = true;
    showLoading(true);
    
    try {
        const response = await apiRequest('/start', 'POST', {
            role: role,
            mode: state.currentMode
        });
        
        state.sessionId = response.session_id;
        state.currentRole = role;
        state.questionNumber = response.question_number || 1;
        
        // Setup chat screen
        elements.roleDisplay.textContent = formatRoleName(role);
        updateQuestionCounter();
        elements.chatMessages.innerHTML = '';
        elements.answerInput.value = '';
        elements.transcriptionPreview.textContent = '';
        elements.transcriptionPreview.style.display = 'none';
        
        // Show/hide voice controls based on mode
        if (state.currentMode === 'voice') {
            elements.voiceControls.style.display = 'flex';
            elements.answerInput.style.display = 'none';
        } else {
            elements.voiceControls.style.display = 'none';
            elements.answerInput.style.display = 'block';
        }
        
        // Add first question
        addMessage('interviewer', response.question, false);
        
        // Speak question if in voice mode
        if (state.currentMode === 'voice') {
            await speakText(response.question);
        }
        
        showScreen('chat');
        
        if (state.currentMode === 'chat') {
            elements.answerInput.focus();
        }
        
    } catch (error) {
        showError('Failed to start interview: ' + error.message);
    } finally {
        state.isProcessing = false;
        showLoading(false);
    }
}

async function handleSendAnswer() {
    const answer = elements.answerInput.value.trim();
    if (!answer || state.isProcessing) return;
    
    state.isProcessing = true;
    elements.sendBtn.disabled = true;
    showLoading(true);
    
    try {
        // Add user's answer to chat
        addMessage('user', answer, false);
        elements.answerInput.value = '';
        
        // Send to API
        const response = await apiRequest('/answer', 'POST', {
            session_id: state.sessionId,
            answer: answer
        });
        
        // Handle response based on type
        if (response.type === 'question') {
            // Next question
            state.questionNumber = response.question_number || state.questionNumber + 1;
            updateQuestionCounter();
            addMessage('interviewer', response.content, false);
            
            // Speak question if in voice mode
            if (state.currentMode === 'voice') {
                await speakText(response.content);
            }
            
        } else if (response.type === 'followup') {
            // Follow-up question
            addMessage('interviewer', response.content, true);
            
            // Speak follow-up if in voice mode
            if (state.currentMode === 'voice') {
                await speakText(response.content);
            }
            
        } else if (response.type === 'complete') {
            // Interview complete, get feedback
            await handleGetFeedback();
            return;
        }
        
        // Clear transcription preview
        elements.transcriptionPreview.textContent = '';
        elements.transcriptionPreview.style.display = 'none';
        
        if (state.currentMode === 'chat') {
            elements.answerInput.focus();
        }
        
    } catch (error) {
        showError('Failed to send answer: ' + error.message);
    } finally {
        state.isProcessing = false;
        elements.sendBtn.disabled = false;
        showLoading(false);
    }
}

async function handleEndInterview() {
    if (!confirm('Are you sure you want to end this interview and get feedback?')) {
        return;
    }
    
    await handleGetFeedback();
}

async function handleGetFeedback() {
    if (state.isProcessing) return;
    
    state.isProcessing = true;
    showLoading(true);
    
    try {
        const response = await apiRequest('/feedback', 'POST', {
            session_id: state.sessionId
        });
        
        displayFeedback(response);
        showScreen('feedback');
        
    } catch (error) {
        showError('Failed to get feedback: ' + error.message);
    } finally {
        state.isProcessing = false;
        showLoading(false);
    }
}

function handleNewInterview() {
    // Reset state
    state.sessionId = null;
    state.currentRole = null;
    state.questionNumber = 0;
    elements.roleSelect.value = '';
    elements.startBtn.disabled = true;
    
    showScreen('start');
}

// Chat UI Functions
function addMessage(type, content, isFollowup = false) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${type}`;
    
    if (isFollowup) {
        messageDiv.classList.add('followup');
    }
    
    const label = document.createElement('div');
    label.className = 'message-label';
    label.textContent = type === 'interviewer' 
        ? (isFollowup ? 'Follow-up Question' : 'Interviewer')
        : 'You';
    
    const bubble = document.createElement('div');
    bubble.className = 'message-bubble';
    bubble.textContent = content;
    
    messageDiv.appendChild(label);
    messageDiv.appendChild(bubble);
    elements.chatMessages.appendChild(messageDiv);
    
    // Scroll to bottom
    elements.chatMessages.scrollTop = elements.chatMessages.scrollHeight;
}

function updateQuestionCounter() {
    elements.questionCounter.textContent = `Question ${state.questionNumber}`;
}

// Feedback Display Functions
function displayFeedback(feedback) {
    // Display scores
    elements.commScore.textContent = feedback.scores.communication;
    elements.techScore.textContent = feedback.scores.technical_knowledge;
    elements.structScore.textContent = feedback.scores.structure;
    
    const average = (
        feedback.scores.communication + 
        feedback.scores.technical_knowledge + 
        feedback.scores.structure
    ) / 3;
    elements.overallScore.textContent = average.toFixed(1);
    
    // Display strengths
    elements.strengthsList.innerHTML = '';
    feedback.strengths.forEach(strength => {
        const li = document.createElement('li');
        li.textContent = strength;
        elements.strengthsList.appendChild(li);
    });
    
    // Display improvements
    elements.improvementsList.innerHTML = '';
    feedback.improvements.forEach(improvement => {
        const li = document.createElement('li');
        li.textContent = improvement;
        elements.improvementsList.appendChild(li);
    });
    
    // Display overall feedback
    elements.overallFeedback.textContent = feedback.overall_feedback;
}

// History Functions
async function showHistoryScreen() {
    showLoading(true);
    
    try {
        const history = await apiRequest('/history', 'GET');
        displayHistory(history);
        showScreen('history');
        
    } catch (error) {
        showError('Failed to load history: ' + error.message);
    } finally {
        showLoading(false);
    }
}

function displayHistory(sessions) {
    elements.historyList.innerHTML = '';
    
    if (!sessions || sessions.length === 0) {
        const emptyDiv = document.createElement('div');
        emptyDiv.className = 'empty-history';
        emptyDiv.innerHTML = `
            <p>No interview history yet</p>
            <p>Start your first practice interview to see your progress here!</p>
        `;
        elements.historyList.appendChild(emptyDiv);
        return;
    }
    
    sessions.forEach(session => {
        const itemDiv = document.createElement('div');
        itemDiv.className = 'history-item';
        itemDiv.onclick = () => showSessionDetails(session.session_id);
        
        const headerDiv = document.createElement('div');
        headerDiv.className = 'history-header';
        
        const roleSpan = document.createElement('span');
        roleSpan.className = 'history-role';
        roleSpan.textContent = formatRoleName(session.role);
        
        const scoreSpan = document.createElement('span');
        scoreSpan.className = 'history-score';
        scoreSpan.textContent = session.score ? session.score.toFixed(1) : 'N/A';
        
        headerDiv.appendChild(roleSpan);
        headerDiv.appendChild(scoreSpan);
        
        const dateDiv = document.createElement('div');
        dateDiv.className = 'history-date';
        dateDiv.textContent = formatDate(session.date);
        
        const statusSpan = document.createElement('span');
        statusSpan.className = `history-status ${session.status}`;
        statusSpan.textContent = session.status;
        
        itemDiv.appendChild(headerDiv);
        itemDiv.appendChild(dateDiv);
        itemDiv.appendChild(statusSpan);
        
        elements.historyList.appendChild(itemDiv);
    });
}

async function showSessionDetails(sessionId) {
    showLoading(true);
    
    try {
        const session = await apiRequest(`/session/${sessionId}`, 'GET');
        
        // Display session transcript and feedback
        if (session.feedback) {
            displayFeedback(session.feedback);
            showScreen('feedback');
        } else {
            showError('Session details not available');
        }
        
    } catch (error) {
        showError('Failed to load session details: ' + error.message);
    } finally {
        showLoading(false);
    }
}

// Utility Functions
function formatRoleName(role) {
    const roleMap = {
        'backend_engineer': 'Backend Engineer',
        'sales_associate': 'Sales Associate',
        'retail_associate': 'Retail Associate'
    };
    return roleMap[role] || role;
}

function formatDate(dateString) {
    const date = new Date(dateString);
    const options = { 
        year: 'numeric', 
        month: 'long', 
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    };
    return date.toLocaleDateString('en-US', options);
}

// Start the app when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
} else {
    init();
}


// Voice Mode Functions

async function checkVoiceAvailability() {
    try {
        const response = await apiRequest('/voice/status', 'GET');
        state.voiceEnabled = response.voice_enabled;
        
        if (!state.voiceEnabled) {
            elements.voiceModeBtn.disabled = true;
            elements.voiceStatusMsg.textContent = '⚠️ Voice mode requires additional setup';
            elements.voiceStatusMsg.style.display = 'block';
        }
    } catch (error) {
        console.error('Failed to check voice availability:', error);
        state.voiceEnabled = false;
        elements.voiceModeBtn.disabled = true;
    }
}

function handleModeChange(mode) {
    if (mode === 'voice' && !state.voiceEnabled) {
        showError('Voice mode is not available. Please install required dependencies.');
        return;
    }
    
    state.currentMode = mode;
    
    // Update button states
    elements.chatModeBtn.classList.toggle('active', mode === 'chat');
    elements.voiceModeBtn.classList.toggle('active', mode === 'voice');
}

async function handleRecordStart(e) {
    e.preventDefault();
    
    if (state.isRecording || state.isProcessing) return;
    
    try {
        // Request microphone access
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        
        state.audioChunks = [];
        state.mediaRecorder = new MediaRecorder(stream);
        
        state.mediaRecorder.ondataavailable = (event) => {
            if (event.data.size > 0) {
                state.audioChunks.push(event.data);
            }
        };
        
        state.mediaRecorder.onstop = async () => {
            // Stop all tracks
            stream.getTracks().forEach(track => track.stop());
            
            // Process the recording
            await processRecording();
        };
        
        state.mediaRecorder.start();
        state.isRecording = true;
        
        // Update UI
        elements.recordBtn.classList.add('recording');
        elements.recordingStatus.textContent = '🔴 Recording... (Release to stop)';
        elements.recordingStatus.style.display = 'block';
        
    } catch (error) {
        console.error('Failed to start recording:', error);
        showError('Failed to access microphone. Please check permissions.');
    }
}

function handleRecordStop(e) {
    e.preventDefault();
    
    if (!state.isRecording) return;
    
    state.isRecording = false;
    
    if (state.mediaRecorder && state.mediaRecorder.state !== 'inactive') {
        state.mediaRecorder.stop();
    }
    
    // Update UI
    elements.recordBtn.classList.remove('recording');
    elements.recordingStatus.textContent = '⏳ Processing...';
}

async function processRecording() {
    try {
        // Create audio blob
        const audioBlob = new Blob(state.audioChunks, { type: 'audio/wav' });
        
        // Convert to base64
        const reader = new FileReader();
        reader.readAsDataURL(audioBlob);
        
        reader.onloadend = async () => {
            const base64Audio = reader.result.split(',')[1];
            
            // Transcribe audio
            try {
                const response = await apiRequest('/voice/transcribe', 'POST', {
                    audio_data: base64Audio,
                    language: 'en'
                });
                
                // Display transcription
                elements.transcriptionPreview.textContent = `📝 "${response.transcription}"`;
                elements.transcriptionPreview.style.display = 'block';
                elements.answerInput.value = response.transcription;
                
                // Clear status
                elements.recordingStatus.style.display = 'none';
                
                // Auto-focus send button
                elements.sendBtn.focus();
                
            } catch (error) {
                console.error('Transcription failed:', error);
                showError('Failed to transcribe audio: ' + error.message);
                elements.recordingStatus.style.display = 'none';
            }
        };
        
    } catch (error) {
        console.error('Failed to process recording:', error);
        showError('Failed to process recording: ' + error.message);
        elements.recordingStatus.style.display = 'none';
    }
}

async function speakText(text) {
    if (state.currentMode !== 'voice') return;
    
    try {
        const response = await apiRequest('/voice/synthesize', 'POST', {
            text: text,
            format: 'wav'
        });
        
        // Decode base64 audio
        const audioData = atob(response.audio_data);
        const audioArray = new Uint8Array(audioData.length);
        for (let i = 0; i < audioData.length; i++) {
            audioArray[i] = audioData.charCodeAt(i);
        }
        
        // Create audio blob and play
        const audioBlob = new Blob([audioArray], { type: 'audio/wav' });
        const audioUrl = URL.createObjectURL(audioBlob);
        const audio = new Audio(audioUrl);
        
        audio.play().catch(error => {
            console.error('Failed to play audio:', error);
        });
        
    } catch (error) {
        console.error('Speech synthesis failed:', error);
        // Don't show error to user - just fall back to text
    }
}
