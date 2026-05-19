// ========== Authentication Management ==========

const API_BASE_URL = 'http://localhost:8000/api';

function getToken() {
    return localStorage.getItem('access_token');
}

function isLoggedIn() {
    return !!getToken();
}

function getAuthHeader() {
    return {
        'Authorization': `Bearer ${getToken()}`,
        'Content-Type': 'application/json'
    };
}

function updateNavigation() {
    const authLink = document.getElementById('authLink');
    const logoutBtn = document.getElementById('logoutBtn');
    
    if (isLoggedIn()) {
        if (authLink) authLink.style.display = 'none';
        if (logoutBtn) logoutBtn.style.display = 'block';
    } else {
        if (authLink) authLink.style.display = 'block';
        if (logoutBtn) logoutBtn.style.display = 'none';
    }
}

function logout() {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('username');
    window.location.href = '/';
}

function protectPage() {
    if (!isLoggedIn()) {
        window.location.href = '/login.html';
    }
}

// Initialize navigation on page load
document.addEventListener('DOMContentLoaded', updateNavigation);

// ========== API Request Helper ==========

async function apiRequest(endpoint, options = {}) {
    const url = `${API_BASE_URL}${endpoint}`;
    const defaultOptions = {
        headers: getAuthHeader(),
        ...options
    };
    
    try {
        const response = await fetch(url, defaultOptions);
        
        if (!response.ok) {
            if (response.status === 401) {
                // Unauthorized - redirect to login
                logout();
                throw new Error('Session expired');
            }
            
            let errorMessage = `HTTP ${response.status}`;
            try {
                const errorData = await response.json();
                errorMessage = errorData.detail || errorData.error || errorMessage;
            } catch {}
            
            throw new Error(errorMessage);
        }
        
        return await response.json();
    } catch (error) {
        console.error('API Request Error:', error);
        throw error;
    }
}

// ========== Token Refresh ==========

async function refreshToken() {
    const refreshToken = localStorage.getItem('refresh_token');
    if (!refreshToken) {
        logout();
        throw new Error('No refresh token');
    }
    
    try {
        const response = await fetch(`${API_BASE_URL}/auth/token/refresh/`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ refresh: refreshToken })
        });
        
        if (!response.ok) {
            logout();
            throw new Error('Token refresh failed');
        }
        
        const data = await response.json();
        localStorage.setItem('access_token', data.access);
        return data.access;
    } catch (error) {
        logout();
        throw error;
    }
}

// ========== Theme Management ==========

function initTheme() {
    const savedTheme = localStorage.getItem('theme') || 'light';
    setTheme(savedTheme);
}

function setTheme(theme) {
    const body = document.body;
    if (theme === 'dark') {
        body.classList.remove('light-mode');
        body.classList.add('dark-mode');
    } else {
        body.classList.remove('dark-mode');
        body.classList.add('light-mode');
    }
    localStorage.setItem('theme', theme);
}

function toggleTheme() {
    const currentTheme = localStorage.getItem('theme') || 'light';
    const newTheme = currentTheme === 'light' ? 'dark' : 'light';
    setTheme(newTheme);
}

// Initialize theme on page load
document.addEventListener('DOMContentLoaded', initTheme);

// ========== Emotion Emoji Mapping ==========

const EMOTION_EMOJIS = {
    'happy': '😊',
    'sad': '😢',
    'angry': '😠',
    'fear': '😨',
    'disgust': '🤢',
    'surprise': '😲',
    'neutral': '😐',
    'stressed': '😰',
    'motivated': '💪',
    'confused': '🤔'
};

function getEmoji(emotion) {
    return EMOTION_EMOJIS[emotion.toLowerCase()] || '😐';
}

// ========== Notification System ==========

function showNotification(message, type = 'info', duration = 3000) {
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.textContent = message;
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 1rem 1.5rem;
        background-color: ${type === 'success' ? '#10b981' : type === 'error' ? '#ef4444' : '#3b82f6'};
        color: white;
        border-radius: 8px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        z-index: 9999;
        animation: slideInRight 0.3s ease;
    `;
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.style.animation = 'slideInRight 0.3s ease reverse';
        setTimeout(() => notification.remove(), 300);
    }, duration);
}

// ========== Loading Spinner ==========

function showLoader(message = 'Loading...') {
    const loader = document.createElement('div');
    loader.id = 'global-loader';
    loader.style.cssText = `
        position: fixed;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        z-index: 10000;
        text-align: center;
    `;
    loader.innerHTML = `
        <div style="width: 40px; height: 40px; border: 4px solid rgba(99, 102, 241, 0.1); border-top-color: #6366f1; border-radius: 50%; animation: spin 1s linear infinite; margin: 0 auto 1rem;"></div>
        <p>${message}</p>
    `;
    
    document.body.appendChild(loader);
}

function hideLoader() {
    const loader = document.getElementById('global-loader');
    if (loader) loader.remove();
}
