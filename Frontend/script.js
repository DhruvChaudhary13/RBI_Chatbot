// API Configuration
const API_URL = 'http://localhost:8000/ask';

// DOM Elements
const chatMessages = document.getElementById('chatMessages');
const userInput = document.getElementById('userInput');
const sendBtn = document.getElementById('sendBtn');
const clearChatBtn = document.getElementById('clearChatBtn');
const exportChatBtn = document.getElementById('exportChatBtn');
const typingIndicator = document.getElementById('typingIndicator');

// Chat State
let conversationHistory = [];

// Session Management
function getSessionId() {
    let sessionId = localStorage.getItem('chat_session_id');
    if (!sessionId) {
        sessionId = 'session_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
        localStorage.setItem('chat_session_id', sessionId);
    }
    return sessionId;
}

// API Functions
async function askQuestion(question) {
    try {
        const response = await fetch(API_URL, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ 
                question: question,
                session_id: getSessionId()
            })
        });
        
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        return {
            answer: data.answer,
            sources_count: data.sources_count,
            has_sources: data.has_sources,
            response_time: data.response_time
        };
        
    } catch (error) {
        console.error('API Error:', error);
        
        if (error.message.includes('Failed to fetch')) {
            throw new Error('Cannot connect to API server. Please ensure:\n1. API server is running (python api.py)\n2. Server is running on port 8000\n3. Run "python main.py" and select option 1 to setup system first');
        }
        throw error;
    }
}

// System Health Check
async function checkSystemHealth() {
    try {
        const response = await fetch('http://localhost:8000/health');
        const data = await response.json();
        
        if (!data.chatbot_ready) {
            showSystemWarning('Chatbot system not ready. Please run "python main.py" and select option 1 to setup the system.');
        } else {
            console.log('✅ System is healthy');
        }
    } catch (error) {
        showSystemWarning('Cannot connect to API server. Please start the server with: python api.py');
    }
}

function showSystemWarning(message) {
    // Check if warning already exists
    if (document.querySelector('.system-warning')) return;
    
    const warningDiv = document.createElement('div');
    warningDiv.className = 'system-warning';
    warningDiv.innerHTML = `
        <i class="fas fa-exclamation-triangle"></i>
        <span>${message}</span>
        <button onclick="this.parentElement.remove()">Dismiss</button>
    `;
    document.querySelector('.chat-header').after(warningDiv);
}

// Main Send Message Function
async function sendMessage() {
    const question = userInput.value.trim();
    if (!question) return;
    
    // Clear input
    userInput.value = '';
    userInput.style.height = 'auto';
    
    // Add user message to chat
    addMessage(question, 'user');
    
    // Show typing indicator
    typingIndicator.style.display = 'flex';
    chatMessages.scrollTop = chatMessages.scrollHeight;
    
    try {
        // Call API
        const response = await askQuestion(question);
        
        // Hide typing indicator
        typingIndicator.style.display = 'none';
        
        // Add bot response
        addMessage(response.answer, 'bot', response.sources_count);
        
        // Save to history
        saveToHistory(question, response);
        
    } catch (error) {
        console.error('Error:', error);
        typingIndicator.style.display = 'none';
        addMessage(error.message || 'Sorry, I encountered an error. Please try again.', 'bot', 0, true);
    }
}

// Add Message to Chat
function addMessage(text, sender, sourcesCount = 0, isError = false) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${sender}-message`;
    
    const time = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    
    messageDiv.innerHTML = `
        <div class="message-avatar">
            <i class="fas ${sender === 'user' ? 'fa-user' : 'fa-robot'}"></i>
        </div>
        <div class="message-content">
            <div class="message-bubble ${isError ? 'error' : ''}">
                ${formatMessage(text)}
            </div>
            <div class="message-time">${time}</div>
            ${sender === 'bot' && sourcesCount > 0 ? `
                <div class="source-info">
                    <i class="fas fa-database"></i>
                    Based on ${sourcesCount} relevant document${sourcesCount > 1 ? 's' : ''}
                </div>
            ` : ''}
        </div>
    `;
    
    chatMessages.appendChild(messageDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

// Format Message (handle markdown-like syntax)
function formatMessage(text) {
    // Escape HTML
    let formatted = escapeHtml(text);
    
    // Convert line breaks to <br>
    formatted = formatted.replace(/\n/g, '<br>');
    
    // Convert bullet points
    formatted = formatted.replace(/[•\-*]\s+(.+?)(?=<br>|$)/g, '<li>$1</li>');
    if (formatted.includes('<li>') && !formatted.includes('<ul>')) {
        formatted = '<ul>' + formatted + '</ul>';
    }
    
    // Convert numbered lists
    formatted = formatted.replace(/(\d+)\.\s+(.+?)(?=<br>|$)/g, '<li>$2</li>');
    if (formatted.includes('<li>') && !formatted.includes('<ul>') && !formatted.includes('<ol>')) {
        formatted = '<ol>' + formatted + '</ol>';
    }
    
    return formatted;
}

// Escape HTML to prevent XSS
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Save to Local Storage
function saveToHistory(question, response) {
    conversationHistory.unshift({
        question: question,
        answer: response.answer,
        timestamp: new Date().toISOString(),
        sources: response.sources_count
    });
    
    // Keep only last 50 conversations
    if (conversationHistory.length > 50) {
        conversationHistory = conversationHistory.slice(0, 50);
    }
    
    localStorage.setItem('chatHistory', JSON.stringify(conversationHistory));
}

// Load Conversation History
function loadConversationHistory() {
    const saved = localStorage.getItem('chatHistory');
    if (saved) {
        conversationHistory = JSON.parse(saved);
        // Optionally display last conversation as welcome back
        if (conversationHistory.length > 0) {
            console.log(`Loaded ${conversationHistory.length} previous conversations`);
        }
    }
}

// Clear Chat
function clearChat() {
    if (confirm('Are you sure you want to clear all messages?')) {
        // Keep the welcome message
        chatMessages.innerHTML = `
            <div class="welcome-message">
                <div class="welcome-icon">
                    <i class="fas fa-robot"></i>
                </div>
                <h2>Welcome to RBI Regulatory Chatbot</h2>
                <p>Ask me anything about RBI regulations, NBFCs, banking guidelines, and financial compliance.</p>
                <div class="feature-highlights">
                    <span><i class="fas fa-check"></i> Instant Answers</span>
                    <span><i class="fas fa-check"></i> Source Verified</span>
                    <span><i class="fas fa-check"></i> 24/7 Available</span>
                </div>
            </div>
        `;
        localStorage.removeItem('chatHistory');
        conversationHistory = [];
    }
}

// Export Chat
function exportChat() {
    const messages = Array.from(document.querySelectorAll('.message')).map(msg => {
        const sender = msg.classList.contains('user-message') ? 'User' : 'RBI Assistant';
        const text = msg.querySelector('.message-bubble').innerText;
        const time = msg.querySelector('.message-time').innerText;
        return `[${time}] ${sender}: ${text}`;
    }).join('\n\n');
    
    const blob = new Blob([messages], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `rbi-chat-export-${new Date().toISOString().slice(0,19)}.txt`;
    a.click();
    URL.revokeObjectURL(url);
}

// Auto-resize textarea
function autoResizeTextarea() {
    userInput.addEventListener('input', function() {
        this.style.height = 'auto';
        this.style.height = Math.min(this.scrollHeight, 120) + 'px';
    });
}

// Setup Event Listeners
function setupEventListeners() {
    sendBtn.addEventListener('click', sendMessage);
    clearChatBtn.addEventListener('click', clearChat);
    exportChatBtn.addEventListener('click', exportChat);
    
    userInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    });
    
    // Sample question buttons
    document.querySelectorAll('.sample-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            const question = btn.getAttribute('data-question');
            userInput.value = question;
            sendMessage();
        });
    });
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    loadConversationHistory();
    setupEventListeners();
    autoResizeTextarea();
    checkSystemHealth();
});