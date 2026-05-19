// ========== Dashboard Initialization ==========

document.addEventListener('DOMContentLoaded', async () => {
    protectPage();
    updateNavigation();
    await loadDashboard();
});

// ========== Load Dashboard Data ==========

async function loadDashboard() {
    try {
        showLoader('Loading dashboard...');
        
        // Load statistics
        await loadStatistics();
        
        // Load charts
        await loadCharts();
        
        // Load recent analyses
        await loadRecentAnalyses();
        
        // Load provider performance
        await loadProviderPerformance();
        
        hideLoader();
    } catch (error) {
        showNotification(`Error loading dashboard: ${error.message}`, 'error');
        console.error(error);
        hideLoader();
    }
}

// ========== Load Statistics ==========

async function loadStatistics() {
    try {
        const data = await apiRequest('/analyses/statistics/');
        
        document.getElementById('totalAnalyses').textContent = data.total_analyses;
        document.getElementById('avgConfidence').textContent = (data.average_confidence * 100).toFixed(1) + '%';
        
        // Find most detected emotion
        let mostDetected = 'N/A';
        let maxCount = 0;
        
        for (const [emotion, count] of Object.entries(data.emotion_distribution)) {
            if (count > maxCount) {
                maxCount = count;
                mostDetected = emotion;
            }
        }
        
        document.getElementById('mostDetected').textContent = mostDetected.charAt(0).toUpperCase() + mostDetected.slice(1);
    } catch (error) {
        console.error('Error loading statistics:', error);
    }
}

// ========== Load Charts ==========

async function loadCharts() {
    try {
        const data = await apiRequest('/analyses/statistics/');
        
        // Emotion Distribution Chart
        const emotionCtx = document.getElementById('emotionChart').getContext('2d');
        const emotionLabels = Object.keys(data.emotion_distribution);
        const emotionData = Object.values(data.emotion_distribution);
        
        new Chart(emotionCtx, {
            type: 'doughnut',
            data: {
                labels: emotionLabels.map(e => e.charAt(0).toUpperCase() + e.slice(1)),
                datasets: [{
                    data: emotionData,
                    backgroundColor: [
                        '#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0', '#9966FF',
                        '#FF9F40', '#FF6384', '#C9CBCF', '#4BC0C0', '#36A2EB'
                    ],
                    borderColor: '#fff',
                    borderWidth: 2
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        position: 'bottom'
                    }
                }
            }
        });
        
        // Analysis Type Distribution Chart
        const typeCtx = document.getElementById('analysisTypeChart').getContext('2d');
        const typeLabels = Object.keys(data.analysis_types);
        const typeData = Object.values(data.analysis_types);
        
        new Chart(typeCtx, {
            type: 'bar',
            data: {
                labels: typeLabels.map(t => t.charAt(0).toUpperCase() + t.slice(1)),
                datasets: [{
                    label: 'Count',
                    data: typeData,
                    backgroundColor: '#6366f1',
                    borderColor: '#4f46e5',
                    borderWidth: 2
                }]
            },
            options: {
                responsive: true,
                indexAxis: 'x',
                plugins: {
                    legend: {
                        display: false
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            stepSize: 1
                        }
                    }
                }
            }
        });
    } catch (error) {
        console.error('Error loading charts:', error);
    }
}

// ========== Load Recent Analyses ==========

async function loadRecentAnalyses() {
    try {
        const data = await apiRequest('/analyses/?page=1');
        
        const recentList = document.getElementById('recentList');
        recentList.innerHTML = '';
        
        if (data.results && data.results.length > 0) {
            data.results.slice(0, 5).forEach(analysis => {
                const analysisItem = document.createElement('div');
                analysisItem.className = 'analysis-item';
                analysisItem.innerHTML = `
                    <div class="analysis-item-info">
                        <div class="analysis-item-emotion">
                            ${getEmoji(analysis.emotion)} ${analysis.emotion.charAt(0).toUpperCase() + analysis.emotion.slice(1)}
                        </div>
                        <div class="analysis-item-time">
                            ${new Date(analysis.created_at).toLocaleString()}
                        </div>
                    </div>
                    <div>
                        <strong>${(analysis.confidence * 100).toFixed(1)}%</strong>
                    </div>
                `;
                recentList.appendChild(analysisItem);
            });
        } else {
            recentList.innerHTML = '<p style="text-align: center; color: var(--light-text-secondary);">No analyses yet</p>';
        }
    } catch (error) {
        console.error('Error loading recent analyses:', error);
    }
}

// ========== Load Provider Performance ==========

async function loadProviderPerformance() {
    try {
        // This would require an admin endpoint or user-specific endpoint
        const data = await apiRequest('/analyses/statistics/');
        
        const providerStats = document.getElementById('providerStats');
        providerStats.innerHTML = '';
        
        if (data.provider_distribution) {
            for (const [provider, count] of Object.entries(data.provider_distribution)) {
                const stat = document.createElement('div');
                stat.className = 'provider-stat';
                stat.innerHTML = `
                    <span>${provider.charAt(0).toUpperCase() + provider.slice(1)}</span>
                    <strong>${count} uses</strong>
                `;
                providerStats.appendChild(stat);
            }
        }
    } catch (error) {
        console.error('Error loading provider performance:', error);
    }
}

// ========== Timeline Chart ==========

async function loadTimelineChart() {
    try {
        const data = await apiRequest('/history/');
        
        if (data.results && data.results.length > 0) {
            const timelineCtx = document.getElementById('emotionTimeline').getContext('2d');
            
            // Group by date and get average confidence
            const timeline = {};
            data.results.forEach(item => {
                const date = new Date(item.date).toLocaleDateString();
                if (!timeline[date]) {
                    timeline[date] = { count: 0, totalConfidence: 0 };
                }
                timeline[date].count++;
                timeline[date].totalConfidence += item.average_confidence || 0;
            });
            
            const dates = Object.keys(timeline).sort();
            const confidences = dates.map(date => 
                (timeline[date].totalConfidence / timeline[date].count * 100).toFixed(1)
            );
            
            new Chart(timelineCtx, {
                type: 'line',
                data: {
                    labels: dates,
                    datasets: [{
                        label: 'Average Confidence (%)',
                        data: confidences,
                        borderColor: '#6366f1',
                        backgroundColor: 'rgba(99, 102, 241, 0.1)',
                        tension: 0.4,
                        fill: true
                    }]
                },
                options: {
                    responsive: true,
                    scales: {
                        y: {
                            min: 0,
                            max: 100
                        }
                    }
                }
            });
        }
    } catch (error) {
        console.error('Error loading timeline chart:', error);
    }
}

// Load timeline when document is ready
document.addEventListener('DOMContentLoaded', loadTimelineChart);

// ========== Refresh Dashboard ==========

function refreshDashboard() {
    loadDashboard();
    showNotification('Dashboard refreshed', 'info');
}

// Auto-refresh dashboard every 30 seconds
setInterval(loadDashboard, 30000);
