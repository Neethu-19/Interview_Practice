// Configuration
const API_BASE_URL = 'http://localhost:8000/api';

// State Management
const state = {
    currentScreen: 'start',
    sessionId: null,
    currentRole: null,
    questionNumber: 0,
    isProcessing: false
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
    
    // Chat Screen
    roleDisplay: document.getElementById('roleDisplay'),
    questionCounter: document.getElementById('questionCounter'),
    chatMessages: document.getElementById('chatMessages'),
    answerInput: document.getElementById('answerInput'),
    sendBtn: document.getElementById('sendBtn'),
    endBtn: document.getElementById('endBtn'),
    
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
    showScreen('start');
}

// Event Listeners
function setupEventListeners() {
    // Start Screen
    elements.roleSelect.addEventListener('change', handleRoleChange);
    elements.startBtn.addEventListener('click', handleStartInterview);
    elements.historyBtn.addEventListener('click', () => showHistoryScreen());
    
    // Chat Screen
    elements.sendBtn.addEventListener('click', handleSendAnswer);
    elements.answerInput.addEventListener('keydown', handleInputKeydown);
    elements.endBtn.addEventListener('click', handleEndInterview);
    
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
            mode: 'chat'
        });
        
        state.sessionId = response.session_id;
        state.currentRole = role;
        state.questionNumber = response.question_number || 1;
        
        // Setup chat screen
        elements.roleDisplay.textContent = formatRoleName(role);
        updateQuestionCounter();
        elements.chatMessages.innerHTML = '';
        elements.answerInput.value = '';
        
        // Add first question
        addMessage('interviewer', response.question, false);
        
        showScreen('chat');
        elements.answerInput.focus();
        
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
            
        } else if (response.type === 'followup') {
            // Follow-up question
            addMessage('interviewer', response.content, true);
            
        } else if (response.type === 'complete') {
            // Interview complete, get feedback
            await handleGetFeedback();
            return;
        }
        
        elements.answerInput.focus();
        
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
