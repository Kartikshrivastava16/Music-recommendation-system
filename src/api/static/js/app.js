const API_URL = 'http://localhost:5000';

function switchTab(tabName) {
    // Hide all tabs
    document.querySelectorAll('.tab-content').forEach(tab => {
        tab.classList.remove('active');
    });
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.classList.remove('active');
    });

    // Show selected tab
    document.getElementById(tabName).classList.add('active');
    event.target.classList.add('active');
}

async function getRecommendations() {
    const userId = document.getElementById('userId').value;
    const method = document.getElementById('method').value;
    const count = document.getElementById('count').value;

    if (!userId) {
        showError('Please enter a User ID');
        return;
    }

    showLoading();

    try {
        let endpoint = `/api/recommendations/${userId}?n=${count}`;
        if (method === 'collaborative') {
            endpoint = `/api/recommendations/collaborative/${userId}?n=${count}`;
        } else if (method === 'content') {
            endpoint = `/api/recommendations/content-based/${userId}?n=${count}`;
        }

        const response = await fetch(`${API_URL}${endpoint}`);
        const data = await response.json();

        if (response.ok) {
            displayRecommendations(data);
        } else {
            showError(data.error || 'Failed to get recommendations');
        }
    } catch (error) {
        showError('Error: ' + error.message);
    }
}

function displayRecommendations(data) {
    const resultsDiv = document.getElementById('results');
    if (!data.recommendations || data.recommendations.length === 0) {
        resultsDiv.innerHTML = '<p style="text-align: center; color: #999;">No recommendations found</p>';
        return;
    }

    let html = '<div class="results">';
    data.recommendations.forEach((rec, index) => {
        const percentage = (rec.score * 100).toFixed(1);
        html += `
            <div class="song-card">
                <div style="font-size: 2em; margin-bottom: 10px;">#${index + 1}</div>
                <div class="song-title">Song ID: ${rec.song_id}</div>
                <div class="song-score">Score: ${percentage}%</div>
            </div>
        `;
    });
    html += '</div>';
    resultsDiv.innerHTML = html;
}

async function getSimilar() {
    const type = document.getElementById('similarType').value;
    const id = document.getElementById('similarId').value;
    const count = document.getElementById('similarCount').value;

    if (!id) {
        showError('Please enter an ID');
        return;
    }

    showLoading();

    try {
        let endpoint = `/api/similar-users/${id}?n=${count}`;
        if (type === 'songs') {
            endpoint = `/api/similar-songs/${id}?n=${count}`;
        }

        const response = await fetch(`${API_URL}${endpoint}`);
        const data = await response.json();

        if (response.ok) {
            displaySimilar(data, type);
        } else {
            showError(data.error || 'Failed to find similar items');
        }
    } catch (error) {
        showError('Error: ' + error.message);
    }
}

function displaySimilar(data, type) {
    const resultsDiv = document.getElementById('results');
    const items = type === 'users' ? (data.similar_users || []) : (data.similar_songs || []);

    if (items.length === 0) {
        resultsDiv.innerHTML = '<p style="text-align: center; color: #999;">No similar items found</p>';
        return;
    }

    let html = '<div class="results">';
    items.forEach((item, index) => {
        const key = type === 'users' ? 'user_id' : 'song_id';
        const percentage = (item.similarity * 100).toFixed(1);
        html += `
            <div class="song-card">
                <div style="font-size: 2em; margin-bottom: 10px;">#${index + 1}</div>
                <div class="song-title">${type === 'users' ? 'User' : 'Song'} ID: ${item[key]}</div>
                <div class="song-score">Similarity: ${percentage}%</div>
            </div>
        `;
    });
    html += '</div>';
    resultsDiv.innerHTML = html;
}

async function recordFeedback() {
    const userId = document.getElementById('feedbackUserId').value;
    const songId = document.getElementById('feedbackSongId').value;
    const rating = document.getElementById('feedbackRating').value;

    if (!userId || !songId || !rating) {
        showErrorInDiv('feedbackResult', 'Please fill all fields');
        return;
    }

    try {
        const response = await fetch(`${API_URL}/api/feedback`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                user_id: parseInt(userId),
                song_id: parseInt(songId),
                rating: parseFloat(rating)
            })
        });

        const data = await response.json();

        if (response.ok) {
            showSuccessInDiv('feedbackResult', `Feedback recorded! Rating: ${rating}/5`);
            clearFeedback();
        } else {
            showErrorInDiv('feedbackResult', data.error || 'Failed to record feedback');
        }
    } catch (error) {
        showErrorInDiv('feedbackResult', 'Error: ' + error.message);
    }
}

async function getStats() {
    try {
        const response = await fetch(`${API_URL}/api/stats`);
        const data = await response.json();

        if (response.ok) {
            displayStats(data);
        } else {
            showErrorInDiv('statsResult', data.error || 'Failed to load statistics');
        }
    } catch (error) {
        showErrorInDiv('statsResult', 'Error: ' + error.message);
    }
}

function displayStats(data) {
    let html = '<div class="stats">';
    html += `<div class="stat-box"><div class="stat-value">${data.total_songs}</div><div class="stat-label">Total Songs</div></div>`;
    html += `<div class="stat-box"><div class="stat-value">${data.total_users}</div><div class="stat-label">Total Users</div></div>`;
    html += `<div class="stat-box"><div class="stat-value">${data.total_interactions}</div><div class="stat-label">Total Interactions</div></div>`;
    html += `<div class="stat-box"><div class="stat-value">${(data.collaborative_weight * 100).toFixed(0)}%</div><div class="stat-label">Collaborative Weight</div></div>`;
    html += `<div class="stat-box"><div class="stat-value">${(data.content_weight * 100).toFixed(0)}%</div><div class="stat-label">Content Weight</div></div>`;
    html += '</div>';
    document.getElementById('statsResult').innerHTML = html;
}

function clearResults() {
    document.getElementById('results').innerHTML = '';
}

function clearFeedback() {
    document.getElementById('feedbackUserId').value = '1';
    document.getElementById('feedbackSongId').value = '1';
    document.getElementById('feedbackRating').value = '5';
    document.getElementById('feedbackResult').innerHTML = '';
}

function showLoading() {
    document.getElementById('results').innerHTML = '<div class="loading">Loading...</div>';
}

function showError(message) {
    document.getElementById('results').innerHTML = `<div class="error">${message}</div>`;
}

function showErrorInDiv(divId, message) {
    document.getElementById(divId).innerHTML = `<div class="error">${message}</div>`;
}

function showSuccessInDiv(divId, message) {
    document.getElementById(divId).innerHTML = `<div class="success">${message}</div>`;
}
