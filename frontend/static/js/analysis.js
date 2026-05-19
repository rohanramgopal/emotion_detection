// ========== Main Functions ==========

document.addEventListener('DOMContentLoaded', () => {
    // Initialize page
    updateNavigation();
    initTheme();
});

// ========== Navigation Functions ==========

function switchTab(tabName, clickedBtn) {
    // Hide all tabs
    const tabs = document.querySelectorAll('.tab-content');
    tabs.forEach(tab => tab.classList.remove('active'));
    
    // Show selected tab
    const selectedTab = document.getElementById(tabName);
    if (selectedTab) {
        selectedTab.classList.add('active');
    }
    
    // Update buttons
    const buttons = document.querySelectorAll('.tab-btn');
    buttons.forEach(btn => btn.classList.remove('active'));
    if (clickedBtn) clickedBtn.classList.add('active');
}

// ========== Analysis Functions ==========

async function analyzeText() {
    protectPage();
    
    const text = document.getElementById('textInput').value.trim();
    
    if (!text) {
        showNotification('Please enter some text', 'error');
        return;
    }
    
    const loading = document.getElementById('textLoading');
    loading.classList.remove('hidden');
    
    try {
        const data = await apiRequest('/analyze/text/', {
            method: 'POST',
            body: JSON.stringify({ text })
        });
        
        displayResults(data);
        showNotification('Analysis complete!', 'success');
    } catch (error) {
        showNotification(`Error: ${error.message}`, 'error');
        console.error(error);
    } finally {
        loading.classList.add('hidden');
    }
}

async function analyzeVoice() {
    const transcript = document.getElementById('transcriptText').textContent.trim();
    
    if (!transcript) {
        showNotification('No transcript available. Please record your voice first.', 'error');
        return;
    }
    
    const loading = document.getElementById('voiceLoading');
    loading.classList.remove('hidden');
    
    try {
        const data = await apiRequest('/analyze/voice/', {
            method: 'POST',
            body: JSON.stringify({ transcript })
        });
        
        displayResults(data);
        showNotification('Voice analysis complete!', 'success');
    } catch (error) {
        showNotification(`Error: ${error.message}`, 'error');
        console.error(error);
    } finally {
        loading.classList.add('hidden');
    }
}

async function analyzeImage() {
    protectPage();
    
    const fileInput = document.getElementById('imageInput');
    
    if (!fileInput.files.length) {
        showNotification('Please select an image', 'error');
        return;
    }
    
    const loading = document.getElementById('imageLoading');
    loading.classList.remove('hidden');
    
    try {
        const formData = new FormData();
        formData.append('image', fileInput.files[0]);
        
        const response = await fetch(`${API_BASE_URL}/analyze/image/`, {
            method: 'POST',
            headers: { 'Authorization': `Bearer ${getToken()}` },
            body: formData
        });
        
        if (!response.ok) throw new Error('Image analysis failed');
        
        const data = await response.json();
        displayResults(data);
        showNotification('Image analysis complete!', 'success');
    } catch (error) {
        showNotification(`Error: ${error.message}`, 'error');
        console.error(error);
    } finally {
        loading.classList.add('hidden');
    }
}

async function startLiveAnalysis() {
    protectPage();
    try {
        const stream = await navigator.mediaDevices.getUserMedia({ video: true, audio: false });
        const video = document.getElementById('webcamVideo');
        video.srcObject = stream;
        await video.play();
        document.getElementById('stopLiveBtn').classList.remove('hidden');
        document.getElementById('startLiveBtn').disabled = true;
        document.getElementById('videoContainer').classList.add('active');
        analyzeLiveFrames();
    } catch (error) {
        showNotification(`Camera error: ${error.message}`, 'error');
    }
}

function stopLiveAnalysis() {
    const video = document.getElementById('webcamVideo');
    if (video.srcObject) {
        video.srcObject.getTracks().forEach(t => t.stop());
        video.srcObject = null;
    }
    if (liveAnalysisInterval) { clearInterval(liveAnalysisInterval); liveAnalysisInterval = null; }
    document.getElementById('stopLiveBtn').classList.add('hidden');
    document.getElementById('startLiveBtn').disabled = false;
    document.getElementById('videoContainer').classList.remove('active');
    showNotification('Live analysis stopped', 'info');
}

let liveAnalysisInterval = null;

async function analyzeLiveFrames() {
    const video = document.getElementById('webcamVideo');
    const canvas = document.createElement('canvas');
    const ctx = canvas.getContext('2d');

    liveAnalysisInterval = setInterval(async () => {
        if (!video.srcObject || video.paused || video.videoWidth === 0) return;

        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;
        ctx.drawImage(video, 0, 0);

        // Convert frame to Blob and send as image
        canvas.toBlob(async (blob) => {
            try {
                const formData = new FormData();
                formData.append('image', blob, 'frame.jpg');
                const response = await fetch(`${API_BASE_URL}/analyze/image/`, {
                    method: 'POST',
                    headers: { 'Authorization': `Bearer ${getToken()}` },
                    body: formData
                });
                if (response.ok) {
                    const data = await response.json();
                    const emotion = data.emotion || 'unknown';
                    const conf = ((data.confidence || 0) * 100).toFixed(1);
                    document.getElementById('currentEmotion').textContent = emotion.toUpperCase();
                    document.getElementById('currentConfidence').textContent = conf + '%';
                    document.getElementById('liveEmoji').textContent = getEmoji(emotion);
                }
            } catch (err) {
                console.error('Frame analysis error:', err);
            }
        }, 'image/jpeg', 0.8);
    }, 4000);
}

// ========== Voice Recording ==========

let mediaRecorder;
let audioChunks = [];

let isRecording = false;

async function toggleRecording() {
    const ring = document.getElementById('recordRing');
    const icon = document.getElementById('recordIcon');
    const label = document.getElementById('recordLabel');

    if (!isRecording) {
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            mediaRecorder = new MediaRecorder(stream);
            audioChunks = [];
            mediaRecorder.ondataavailable = (e) => audioChunks.push(e.data);
            isRecording = true;
            ring.classList.add('recording');
            icon.textContent = '⏹';
            label.textContent = 'Recording... Tap to stop & analyze';
            document.getElementById('transcriptText').textContent = '';
            startSpeechRecognition();
            mediaRecorder.start();
        } catch (error) {
            showNotification(`Microphone error: ${error.message}`, 'error');
        }
    } else {
        if (mediaRecorder && mediaRecorder.state !== 'inactive') mediaRecorder.stop();
        if (recognition) recognition.stop();
        isRecording = false;
        ring.classList.remove('recording');
        icon.textContent = '🎙️';
        label.textContent = 'Tap to start recording';
        setTimeout(() => {
            const t = document.getElementById('transcriptText').textContent.trim();
            if (t) analyzeVoice();
            else showNotification('No speech detected. Try again.', 'error');
        }, 600);
    }
}

// ========== Speech Recognition ==========

let recognition;

function startSpeechRecognition() {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    
    if (!SpeechRecognition) {
        showNotification('Speech recognition not supported', 'error');
        return;
    }
    
    recognition = new SpeechRecognition();
    recognition.continuous = true;
    recognition.interimResults = true;
    recognition.lang = 'en-US';
    
    let finalTranscript = '';
    
    recognition.onresult = (event) => {
        let interimTranscript = '';
        
        for (let i = event.resultIndex; i < event.results.length; i++) {
            const transcript = event.results[i][0].transcript;
            
            if (event.results[i].isFinal) {
                finalTranscript += transcript + ' ';
            } else {
                interimTranscript += transcript;
            }
        }
        
        document.getElementById('transcriptText').textContent = finalTranscript + interimTranscript;
        document.getElementById('transcript').classList.remove('hidden');
    };
    
    recognition.onerror = (event) => {
        console.error('Speech recognition error:', event.error);
    };
    
    recognition.onend = () => {
        // Analysis happens when user clicks analyze
    };
    
    recognition.start();
}

// ========== Image Preview ==========

function previewImage() {
    const file = document.getElementById('imageInput').files[0];
    if (file) {
        const reader = new FileReader();
        reader.onload = (e) => {
            const preview = document.getElementById('imagePreview');
            preview.src = e.target.result;
            preview.classList.remove('hidden');
            document.getElementById('analyzeImageBtn').style.display = 'inline-flex';
            document.getElementById('uploadLabel').textContent = file.name;
            document.getElementById('uploadIcon').textContent = '✅';
        };
        reader.readAsDataURL(file);
    }
}

// ========== Display Results ==========

function displayResults(data) {
    const resultsSection = document.getElementById('resultsSection');
    const emotion = (data.emotion || 'neutral').toLowerCase();

    // Emotion display
    document.getElementById('emotionEmoji').textContent = getEmoji(emotion);
    document.getElementById('detectedEmotion').textContent = emotion.charAt(0).toUpperCase() + emotion.slice(1);

    const confidence = (data.confidence || 0) * 100;
    document.getElementById('confidenceBar').style.width = confidence + '%';
    document.getElementById('confidenceText').textContent = `Confidence: ${confidence.toFixed(1)}%`;

    // Reasoning
    document.getElementById('reasonText').textContent = data.reasoning || data.reason || 'Analysis complete';

    // Recommendations
    const recs = data.recommendations || {};
    const music = recs.music || {};

    // Spotify
    const spotifyList = document.getElementById('spotifyList');
    spotifyList.innerHTML = '';
    (music.spotify || []).forEach(url => {
        const a = document.createElement('a');
        a.href = url; a.target = '_blank';
        a.innerHTML = '<span class="pl-icon">🟢</span> Open on Spotify';
        spotifyList.appendChild(a);
    });
    if (!spotifyList.children.length) spotifyList.innerHTML = '<p style="color:var(--text-dim);font-size:0.85rem;">No Spotify links available</p>';

    // YouTube
    const youtubeList = document.getElementById('youtubeList');
    youtubeList.innerHTML = '';
    (music.youtube || []).forEach(url => {
        const a = document.createElement('a');
        a.href = url; a.target = '_blank';
        a.innerHTML = '<span class="pl-icon">🔴</span> Open on YouTube';
        youtubeList.appendChild(a);
    });
    if (!youtubeList.children.length) youtubeList.innerHTML = '<p style="color:var(--text-dim);font-size:0.85rem;">No YouTube links available</p>';

    // Quotes
    const quotesList = document.getElementById('quotesList');
    quotesList.innerHTML = '';
    const quotes = recs.quotes || [];
    quotes.forEach(quote => {
        const div = document.createElement('div');
        div.className = 'quote-item';
        div.textContent = `"${quote}"`;
        quotesList.appendChild(div);
    });
    if (!quotesList.children.length) quotesList.innerHTML = '<p style="color:var(--text-dim);font-size:0.85rem;">No quotes available</p>';

    resultsSection.classList.remove('hidden');
    resultsSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

function newAnalysis() {
    document.getElementById('textInput').value = '';
    document.getElementById('imageInput').value = '';
    document.getElementById('transcriptText').textContent = '';
    document.getElementById('transcript').classList.add('hidden');
    document.getElementById('imagePreview').classList.add('hidden');
    document.getElementById('imagePreview').src = '';
    document.getElementById('analyzeImageBtn').style.display = 'none';
    document.getElementById('uploadLabel').textContent = 'Click here to choose an image';
    document.getElementById('uploadIcon').textContent = '📁';
    document.getElementById('resultsSection').classList.add('hidden');
}
