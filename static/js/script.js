// CyberCrawl Spider Robot - Frontend JavaScript

let currentMode = 'STOPPED';
let statusUpdateInterval = null;
let videoReloadAttempts = 0;
const MAX_RELOAD_ATTEMPTS = 3;

// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
    console.log('🕷️ CyberCrawl Interface Loaded');
    
    // Start status updates
    startStatusUpdates();
    updateUIState();
    
    // Setup video feed error handling
    setupVideoFeed();
    
    // Log keyboard shortcuts
    console.log('⌨️ Keyboard shortcuts available in manual mode');
});

// ===== Video Feed Setup =====
function setupVideoFeed() {
    const videoFeed = document.getElementById('videoFeed');
    
    if (!videoFeed) return;
    
    // Handle video load success
    videoFeed.addEventListener('load', function() {
        console.log('✅ Video feed connected');
        videoReloadAttempts = 0;
    });
    
    // Handle video load errors
    videoFeed.addEventListener('error', function() {
        console.error('❌ Video feed error');
        
        if (videoReloadAttempts < MAX_RELOAD_ATTEMPTS) {
            videoReloadAttempts++;
            console.log(`🔄 Retrying video feed (${videoReloadAttempts}/${MAX_RELOAD_ATTEMPTS})...`);
            
            setTimeout(() => {
                videoFeed.src = videoFeed.src.split('?')[0] + '?t=' + Date.now();
            }, 2000);
        } else {
            showToast('Video feed unavailable. Check camera connection.', 'error');
        }
    });
    
    // Refresh feed after 3 seconds to ensure it starts
    setTimeout(() => {
        if (videoFeed) {
            const currentSrc = videoFeed.src;
            videoFeed.src = currentSrc.split('?')[0] + '?t=' + Date.now();
            console.log('🔄 Refreshing video feed...');
        }
    }, 3000);
}

// ===== Status Updates =====
function startStatusUpdates() {
    // Update status every 500ms
    statusUpdateInterval = setInterval(updateStatus, 500);
}

async function updateStatus() {
    try {
        const response = await fetch('/api/status');
        if (!response.ok) throw new Error('Status API failed');
        
        const data = await response.json();
        
        // Update mode
        currentMode = data.mode;
        updateUIState();
        
        // Update distance
        updateDistance(data.distance);
        
        // Update detections
        updateDetections(data.detections);
        
        // Update FPS
        updateFPS(data.fps);
        
        // Update camera status
        updateCameraStatus(data.camera_ready, data.model_loaded);
        
    } catch (error) {
        console.error('Status update error:', error);
        // Don't spam errors, just log them
    }
}

function updateUIState() {
    // Update status badge
    const statusBadge = document.getElementById('statusBadge');
    const statusText = statusBadge.querySelector('.status-text');
    const modeText = document.getElementById('modeText');
    
    // Remove all mode classes
    statusBadge.classList.remove('auto', 'manual', 'stopped');
    
    if (currentMode === 'AUTO') {
        statusBadge.classList.add('auto');
        statusText.textContent = '🤖 AUTO MODE';
        modeText.textContent = 'AUTO';
        modeText.style.color = '#00d4ff';
    } else if (currentMode === 'MANUAL') {
        statusBadge.classList.add('manual');
        statusText.textContent = '⚙️ MANUAL MODE';
        modeText.textContent = 'MANUAL';
        modeText.style.color = '#7b2cbf';
    } else {
        statusBadge.classList.add('stopped');
        statusText.textContent = '⏸️ STOPPED';
        modeText.textContent = 'STOPPED';
        modeText.style.color = '#a0a0b0';
    }
    
    // Update button states
    const btnAutoMode = document.getElementById('btnAutoMode');
    const btnStop = document.getElementById('btnStop');
    const btnManualMode = document.getElementById('btnManualMode');
    const manualControls = document.getElementById('manualControls');
    
    if (currentMode === 'STOPPED') {
        btnAutoMode.disabled = false;
        btnStop.disabled = true;
        btnManualMode.disabled = false;
        manualControls.style.display = 'none';
    } else if (currentMode === 'AUTO') {
        btnAutoMode.disabled = true;
        btnStop.disabled = false;
        btnManualMode.disabled = true;
        manualControls.style.display = 'none';
    } else if (currentMode === 'MANUAL') {
        btnAutoMode.disabled = true;
        btnStop.disabled = false;
        btnManualMode.disabled = true;
        manualControls.style.display = 'block';
    }
}

function updateDistance(distance) {
    const distanceValue = document.getElementById('distanceValue');
    const distanceText = document.getElementById('distanceText');
    
    if (distance > 0) {
        const distStr = `${distance.toFixed(1)} cm`;
        distanceValue.textContent = distStr;
        distanceText.textContent = distStr;
        
        // Color code based on distance
        let color;
        if (distance < 20) {
            color = '#ff006e';  // Red - danger
        } else if (distance < 50) {
            color = '#ffa500';  // Orange - caution
        } else {
            color = '#06ffa5';  // Green - safe
        }
        
        distanceValue.style.color = color;
        distanceText.style.color = color;
    } else {
        distanceValue.textContent = '-- cm';
        distanceText.textContent = '-- cm';
        distanceValue.style.color = '#a0a0b0';
        distanceText.style.color = '#a0a0b0';
    }
}

function updateDetections(detections) {
    const detectionCount = document.getElementById('detectionCount');
    const detectionsList = document.getElementById('detectionsList');
    const detectionsText = document.getElementById('detectionsText');
    
    const count = detections.length;
    
    // Update count badge
    const badgeValue = detectionCount.querySelector('.badge-value');
    badgeValue.textContent = count;
    
    // Update text
    detectionsText.textContent = count;
    detectionsText.style.color = count > 0 ? '#00d4ff' : '#a0a0b0';
    
    // Update list
    detectionsList.innerHTML = '';
    
    if (count === 0) {
        detectionsList.innerHTML = '<p class="no-detections">No objects detected</p>';
    } else {
        detections.forEach(detection => {
            const item = document.createElement('div');
            item.className = 'detection-item';
            
            const conf = Math.round(detection.confidence * 100);
            
            item.innerHTML = `
                <span class="detection-class">${detection.class}</span>
                <span class="detection-conf">${conf}%</span>
            `;
            
            detectionsList.appendChild(item);
        });
    }
}

function updateFPS(fps) {
    const fpsDisplay = document.getElementById('fpsDisplay');
    const fpsText = document.getElementById('fpsText');
    
    if (fps > 0) {
        const fpsStr = `${fps.toFixed(1)} fps`;
        fpsDisplay.textContent = fpsStr;
        fpsText.textContent = fpsStr;
        
        // Color code based on FPS
        let color;
        if (fps >= 15) {
            color = '#06ffa5';  // Green - good
        } else if (fps >= 10) {
            color = '#ffa500';  // Orange - okay
        } else {
            color = '#ff006e';  // Red - poor
        }
        
        fpsDisplay.style.color = color;
        fpsText.style.color = color;
    } else {
        fpsDisplay.textContent = '-- fps';
        fpsText.textContent = '-- fps';
        fpsDisplay.style.color = '#a0a0b0';
        fpsText.style.color = '#a0a0b0';
    }
}

function updateCameraStatus(cameraReady, modelLoaded) {
    const cameraStatus = document.getElementById('cameraStatus');
    const modelStatus = document.getElementById('modelStatus');
    
    // Camera status
    if (cameraReady) {
        cameraStatus.textContent = 'Ready ✅';
        cameraStatus.style.color = '#06ffa5';
    } else {
        cameraStatus.textContent = 'Not Ready ❌';
        cameraStatus.style.color = '#ff006e';
    }
    
    // Model status
    if (modelLoaded) {
        modelStatus.textContent = 'Loaded ✅';
        modelStatus.style.color = '#06ffa5';
    } else {
        modelStatus.textContent = 'Not Loaded ❌';
        modelStatus.style.color = '#ff006e';
    }
}

// ===== Control Functions =====
async function startAutoMode() {
    if (currentMode !== 'STOPPED') {
        showToast('Please stop the robot first', 'error');
        return;
    }
    
    try {
        const response = await fetch('/api/start_auto', {
            method: 'POST'
        });
        const data = await response.json();
        
        if (data.success) {
            showToast('🤖 Auto mode started!', 'success');
            currentMode = 'AUTO';
            updateUIState();
        } else {
            showToast('❌ ' + data.message, 'error');
        }
    } catch (error) {
        showToast('❌ Connection error', 'error');
        console.error('Error:', error);
    }
}

async function stopRobot() {
    try {
        const response = await fetch('/api/stop', {
            method: 'POST'
        });
        const data = await response.json();
        
        if (data.success) {
            showToast('🛑 Robot stopped', 'success');
            currentMode = 'STOPPED';
            updateUIState();
        } else {
            showToast('❌ ' + data.message, 'error');
        }
    } catch (error) {
        showToast('❌ Connection error', 'error');
        console.error('Error:', error);
    }
}

async function enableManualMode() {
    if (currentMode !== 'STOPPED') {
        showToast('Please stop the robot first', 'error');
        return;
    }
    
    try {
        const response = await fetch('/api/manual_mode', {
            method: 'POST'
        });
        const data = await response.json();
        
        if (data.success) {
            showToast('⚙️ Manual mode activated!', 'success');
            currentMode = 'MANUAL';
            updateUIState();
        } else {
            showToast('❌ ' + data.message, 'error');
        }
    } catch (error) {
        showToast('❌ Connection error', 'error');
        console.error('Error:', error);
    }
}

async function manualControl(action) {
    if (currentMode !== 'MANUAL') {
        showToast('Not in manual mode', 'error');
        return;
    }
    
    // Action feedback messages
    const actionMessages = {
        'forward': '⬆️ Moving forward...',
        'backward': '⬇️ Moving backward...',
        'left': '⬅️ Turning left...',
        'right': '➡️ Turning right...',
        'wave': '👋 Waving...',
        'shake': '🤝 Shaking hand...',
        'dance': '💃 Dancing...',
        'stand': '🧍 Standing...',
        'sit': '💺 Sitting...'
    };
    
    // Show feedback
    const message = actionMessages[action] || 'Executing...';
    console.log(message);
    
    try {
        const response = await fetch(`/api/manual_control/${action}`, {
            method: 'POST'
        });
        const data = await response.json();
        
        if (!data.success) {
            showToast('❌ ' + data.message, 'error');
        }
    } catch (error) {
        showToast('❌ Connection error', 'error');
        console.error('Error:', error);
    }
}

// ===== Toast Notifications =====
function showToast(message, type = 'info') {
    const toast = document.getElementById('toast');
    
    toast.textContent = message;
    toast.className = 'toast show';
    
    if (type === 'error') {
        toast.classList.add('error');
    } else if (type === 'success') {
        toast.classList.add('success');
    }
    
    setTimeout(() => {
        toast.classList.remove('show');
    }, 3000);
}

// ===== Keyboard Controls =====
document.addEventListener('keydown', function(event) {
    // Only work in manual mode
    if (currentMode !== 'MANUAL') return;
    
    // Prevent default for arrow keys
    if (['ArrowUp', 'ArrowDown', 'ArrowLeft', 'ArrowRight', ' '].includes(event.key)) {
        event.preventDefault();
    }
    
    switch(event.key) {
        case 'ArrowUp':
        case 'w':
        case 'W':
            manualControl('forward');
            break;
        case 'ArrowDown':
        case 's':
        case 'S':
            manualControl('backward');
            break;
        case 'ArrowLeft':
        case 'a':
        case 'A':
            manualControl('left');
            break;
        case 'ArrowRight':
        case 'd':
        case 'D':
            manualControl('right');
            break;
        case ' ':
            stopRobot();
            break;
    }
});

// ===== Cleanup on page unload =====
window.addEventListener('beforeunload', function() {
    if (statusUpdateInterval) {
        clearInterval(statusUpdateInterval);
    }
});

// Log ready
console.log('✅ CyberCrawl controls ready!');
console.log('🎮 Use arrow keys or WASD in manual mode');
console.log('🛑 Press Space for emergency stop');