/**
 * Agent Manager Main JavaScript
 * Handles global functionality for the dashboard
 */

// Global socket instance for real-time updates
let socket;

// Initialize application
document.addEventListener('DOMContentLoaded', function() {
    // Initialize Socket.IO connection
    initSocketConnection();
    
    // Set up global event handlers
    setupEventHandlers();
    
    // Check for active sessions
    checkActiveSessions();
});

/**
 * Initialize Socket.IO connection for real-time updates
 */
function initSocketConnection() {
    socket = io();
    
    socket.on('connect', function() {
        console.log('Connected to WebSocket server');
    });
    
    socket.on('disconnect', function() {
        console.log('Disconnected from WebSocket server');
    });
    
    // Listen for session updates
    socket.on('session_update', function(data) {
        console.log('Session update received:', data);
        // This will be handled in the specific page's JS
    });
    
    // Listen for AI status updates
    socket.on('ai_status_update', function(data) {
        console.log('AI status update received:', data);
        // Update UI elements with new AI status
        updateAIStatusIndicator(data.session_id, data.status);
    });
}

/**
 * Set up global event handlers
 */
function setupEventHandlers() {
    // Add any global event handlers here
    document.addEventListener('visibilitychange', function() {
        if (!document.hidden) {
            // When tab becomes visible again, check for updates
            checkActiveSessions();
        }
    });
}

/**
 * Check for active sessions via API
 */
function checkActiveSessions() {
    // This function will be implemented in specific pages
    if (typeof loadSessions === 'function') {
        loadSessions();
    }
}

/**
 * Update AI status indicator in the UI
 */
function updateAIStatusIndicator(sessionId, status) {
    // Find status indicators for this session
    const statusElements = document.querySelectorAll(`[data-session-id="${sessionId}"] .ai-status`);
    
    if (statusElements.length > 0) {
        statusElements.forEach(element => {
            // Update status class and text
            element.className = `badge bg-${status === 'active' ? 'info' : 'warning'} ai-status`;
            element.textContent = status;
        });
    }
}

/**
 * Format timestamp to readable date/time
 */
function formatTimestamp(timestamp) {
    if (!timestamp) return 'N/A';
    const date = new Date(timestamp * 1000);
    return date.toLocaleString();
}

/**
 * Show notification to user
 */
function showNotification(message, type = 'info') {
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `alert alert-${type} notification-toast`;
    notification.innerHTML = `
        <button type="button" class="btn-close float-end" data-bs-dismiss="alert" aria-label="Close"></button>
        <div>${message}</div>
    `;
    
    // Add to notifications container or create one
    let container = document.getElementById('notifications-container');
    if (!container) {
        container = document.createElement('div');
        container.id = 'notifications-container';
        container.className = 'position-fixed top-0 end-0 p-3';
        container.style.zIndex = '1050';
        document.body.appendChild(container);
    }
    
    container.appendChild(notification);
    
    // Auto-remove after 5 seconds
    setTimeout(() => {
        notification.classList.add('fade');
        setTimeout(() => notification.remove(), 500);
    }, 5000);
}