const API_URL = 'http://localhost:5000';

/* ── Song catalogue (matches songs.csv) ──────────────────────────── */
const SONGS = {
  1:  { title:'Blinding Lights',      artist:'The Weeknd',       genre:'Synthwave',   emoji:'🌃', energy:.73, dance:.80, valence:.33, acoust:.10 },
  2:  { title:'Shape of You',         artist:'Ed Sheeran',       genre:'Pop',         emoji:'🎸', energy:.65, dance:.83, valence:.93, acoust:.16 },
  3:  { title:'One Dance',            artist:'Drake',            genre:'Hip-Hop',     emoji:'🎤', energy:.62, dance:.62, valence:.53, acoust:.06 },
  4:  { title:'Levitating',           artist:'Dua Lipa',         genre:'Pop',         emoji:'✨', energy:.80, dance:.79, valence:.86, acoust:.04 },
  5:  { title:'Heat Waves',           artist:'Glass Animals',    genre:'Indie Pop',   emoji:'🌊', energy:.64, dance:.68, valence:.69, acoust:.22 },
  6:  { title:'As It Was',            artist:'Harry Styles',     genre:'Pop',         emoji:'🌸', energy:.63, dance:.54, valence:.90, acoust:.29 },
  7:  { title:'Anti-Hero',            artist:'Taylor Swift',     genre:'Pop',         emoji:'🦸', energy:.50, dance:.58, valence:.21, acoust:.18 },
  8:  { title:'Tití',                 artist:'Bad Bunny',        genre:'Latin',       emoji:'🌴', energy:.70, dance:.60, valence:.80, acoust:.35 },
  9:  { title:'Bohemian Rhapsody',    artist:'Queen',            genre:'Rock',        emoji:'🎭', energy:.40, dance:.33, valence:.23, acoust:.28 },
  10: { title:'Stairway to Heaven',   artist:'Led Zeppelin',     genre:'Rock',        emoji:'🎸', energy:.40, dance:.34, valence:.21, acoust:.14 },
  11: { title:'Hotel California',     artist:'Eagles',           genre:'Rock',        emoji:'🏨', energy:.42, dance:.38, valence:.27, acoust:.33 },
  12: { title:'Imagine',             artist:'John Lennon',      genre:'Pop',         emoji:'🕊️', energy:.27, dance:.28, valence:.53, acoust:.51 },
  13: { title:'Someone Like You',     artist:'Adele',            genre:'Pop',         emoji:'💔', energy:.34, dance:.33, valence:.65, acoust:.42 },
  14: { title:'Thriller',             artist:'Michael Jackson',  genre:'Pop',         emoji:'🕺', energy:.84, dance:.76, valence:.65, acoust:.00 },
  15: { title:'Uptown Funk',          artist:'Mark Ronson',      genre:'Funk',        emoji:'🕺', energy:.77, dance:.85, valence:.84, acoust:.08 },
  16: { title:'Dance the Night',      artist:'Dua Lipa',         genre:'Dance Pop',   emoji:'💃', energy:.80, dance:.82, valence:.82, acoust:.06 },
  17: { title:'Good as Hell',         artist:'Lizzo',            genre:'Hip-Hop',     emoji:'💪', energy:.77, dance:.72, valence:.97, acoust:.10 },
  18: { title:'Sunroof',              artist:'Nicky Youre',      genre:'Indie Pop',   emoji:'☀️', energy:.72, dance:.68, valence:.76, acoust:.16 },
  19: { title:'Get Lucky',            artist:'Daft Punk',        genre:'Funk',        emoji:'🍀', energy:.80, dance:.69, valence:.70, acoust:.00 },
  20: { title:'Midnight City',        artist:'M83',              genre:'Electronic',  emoji:'🌆', energy:.58, dance:.47, valence:.66, acoust:.08 },
  21: { title:'Sweet Dreams',         artist:'Eurythmics',       genre:'Synth-pop',   emoji:'😴', energy:.85, dance:.60, valence:.65, acoust:.04 },
  22: { title:'Never Gonna Give You Up', artist:'Rick Astley',   genre:'Pop',         emoji:'🎵', energy:.76, dance:.76, valence:.85, acoust:.06 },
  23: { title:"Don't Stop Me Now",    artist:'Queen',            genre:'Rock',        emoji:'🚀', energy:.92, dance:.62, valence:.87, acoust:.02 },
  24: { title:'Wonderwall',           artist:'Oasis',            genre:'Rock',        emoji:'🧱', energy:.59, dance:.46, valence:.79, acoust:.19 },
  25: { title:'Smells Like Teen Spirit', artist:'Nirvana',       genre:'Grunge',      emoji:'🎸', energy:.91, dance:.58, valence:.14, acoust:.10 },
  26: { title:'Rolling in the Deep',  artist:'Adele',            genre:'Pop',         emoji:'🔥', energy:.72, dance:.55, valence:.22, acoust:.12 },
  27: { title:'Hey Ya!',              artist:'Outkast',          genre:'Alternative', emoji:'🎉', energy:.86, dance:.87, valence:.94, acoust:.02 },
  28: { title:'Lose Yourself',        artist:'Eminem',           genre:'Hip-Hop',     emoji:'🎤', energy:.91, dance:.45, valence:.30, acoust:.03 },
  29: { title:'Back to Black',        artist:'Amy Winehouse',    genre:'Soul',        emoji:'🖤', energy:.50, dance:.45, valence:.12, acoust:.38 },
  30: { title:'Take Five',            artist:'Dave Brubeck',     genre:'Jazz',        emoji:'🎷', energy:.35, dance:.22, valence:.45, acoust:.60 },
  31: { title:'River Flows in You',   artist:'Yiruma',           genre:'Classical',   emoji:'🎹', energy:.12, dance:.10, valence:.20, acoust:.90 },
  32: { title:'Clair de Lune',        artist:'Debussy',          genre:'Classical',   emoji:'🌙', energy:.10, dance:.08, valence:.15, acoust:.95 },
  33: { title:'Bad Guy',              artist:'Billie Eilish',    genre:'Pop',         emoji:'😈', energy:.40, dance:.49, valence:.20, acoust:.50 },
  34: { title:'Shake It Off',         artist:'Taylor Swift',     genre:'Pop',         emoji:'✨', energy:.80, dance:.90, valence:.95, acoust:.05 },
  35: { title:'Closer',               artist:'The Chainsmokers', genre:'Electronic',  emoji:'🎧', energy:.60, dance:.70, valence:.30, acoust:.10 },
  36: { title:'HUMBLE.',              artist:'Kendrick Lamar',   genre:'Hip-Hop',     emoji:'👑', energy:.85, dance:.40, valence:.20, acoust:.02 },
  37: { title:'Heroes',               artist:'David Bowie',      genre:'Rock',        emoji:'🦸', energy:.65, dance:.55, valence:.60, acoust:.20 },
  38: { title:'Electric Feel',        artist:'MGMT',             genre:'Indie',       emoji:'⚡', energy:.70, dance:.66, valence:.67, acoust:.12 },
  39: { title:'The Less I Know The Better', artist:'Tame Impala',genre:'Indie',       emoji:'🌀', energy:.68, dance:.60, valence:.40, acoust:.25 },
  40: { title:'Summertime',           artist:'George Gershwin',  genre:'Jazz',        emoji:'☀️', energy:.30, dance:.40, valence:.50, acoust:.60 },
  41: { title:'Calm Before the Storm',artist:'The Midnight',     genre:'Synthwave',   emoji:'🌃', energy:.64, dance:.58, valence:.41, acoust:.12 },
  42: { title:'Golden Hour',          artist:'JVKE',             genre:'Pop',         emoji:'🌅', energy:.58, dance:.62, valence:.83, acoust:.15 },
  43: { title:'Afterglow',            artist:'Ed Sheeran',       genre:'Pop',         emoji:'🌇', energy:.49, dance:.57, valence:.72, acoust:.22 },
  44: { title:'Despacito',            artist:'Luis Fonsi',       genre:'Latin',       emoji:'💃', energy:.79, dance:.82, valence:.86, acoust:.08 },
  45: { title:'Take On Me',           artist:'a-ha',             genre:'Synth-pop',   emoji:'✏️', energy:.83, dance:.61, valence:.76, acoust:.03 },
  46: { title:'Paint It Black',       artist:'The Rolling Stones',genre:'Rock',       emoji:'🖌️', energy:.71, dance:.48, valence:.33, acoust:.19 },
  47: { title:'Cigarette Daydreams',  artist:'Cage the Elephant',genre:'Alternative', emoji:'🚬', energy:.54, dance:.53, valence:.39, acoust:.27 },
  48: { title:'No Role Modelz',       artist:'J. Cole',          genre:'Hip-Hop',     emoji:'🎤', energy:.82, dance:.73, valence:.46, acoust:.11 },
  49: { title:'Bloom',                artist:'The Paper Kites',  genre:'Indie',       emoji:'🌸', energy:.32, dance:.44, valence:.52, acoust:.67 },
  50: { title:'Moon River',           artist:'Audrey Hepburn',   genre:'Jazz',        emoji:'🌙', energy:.22, dance:.18, valence:.31, acoust:.78 },
  51: { title:'Experience',           artist:'Ludovico Einaudi', genre:'Classical',   emoji:'🎹', energy:.15, dance:.12, valence:.18, acoust:.94 },
  52: { title:'Good 4 U',             artist:'Olivia Rodrigo',   genre:'Pop',         emoji:'😤', energy:.88, dance:.68, valence:.63, acoust:.04 },
  53: { title:'Industry Baby',        artist:'Lil Nas X',        genre:'Hip-Hop',     emoji:'🎺', energy:.89, dance:.78, valence:.55, acoust:.05 },
  54: { title:'Unstoppable',          artist:'Sia',              genre:'Pop',         emoji:'💥', energy:.83, dance:.60, valence:.73, acoust:.02 },
  55: { title:'Sunset Lover',         artist:'Petit Biscuit',    genre:'Electronic',  emoji:'🌅', energy:.66, dance:.61, valence:.50, acoust:.18 },
};

const GENRE_COLORS = {
  'Pop':        ['#ede9fe','#5b21b6'], 'Rock':       ['#fee2e2','#991b1b'],
  'Hip-Hop':    ['#fef3c7','#92400e'], 'Electronic': ['#dbeafe','#1e40af'],
  'Indie Pop':  ['#fce7f3','#9d174d'], 'Indie':      ['#fce7f3','#9d174d'],
  'Jazz':       ['#fef9c3','#713f12'], 'Classical':  ['#f0fdf4','#14532d'],
  'Funk':       ['#fff7ed','#9a3412'], 'Latin':      ['#fdf4ff','#6b21a8'],
  'Synthwave':  ['#eef2ff','#3730a3'], 'Synth-pop':  ['#eef2ff','#3730a3'],
  'Dance Pop':  ['#ffe4e6','#9f1239'], 'Alternative':['#f0fdf4','#166534'],
  'Soul':       ['#fff7ed','#92400e'], 'Grunge':     ['#f1f5f9','#1e293b'],
};

function genreStyle(genre) {
  const [bg, fg] = GENRE_COLORS[genre] || ['#f3f4f6','#374151'];
  return `background:${bg};color:${fg}`;
}

/* ── Tab navigation ───────────────────────────────────────────────── */
document.querySelectorAll('.nav-item').forEach(btn => {
  btn.addEventListener('click', () => {
    const tab = btn.dataset.tab;
    document.querySelectorAll('.nav-item').forEach(b => b.classList.remove('active'));
    document.querySelectorAll('.tab-panel').forEach(p => p.classList.remove('active'));
    btn.classList.add('active');
    document.getElementById(tab).classList.add('active');
  });
});

/* ── Slider update ────────────────────────────────────────────────── */
function updateSlider(sliderId, valId) {
  document.getElementById(valId).textContent =
    parseFloat(document.getElementById(sliderId).value).toFixed(2);
}

/* ── Star rating ──────────────────────────────────────────────────── */
let currentRating = 5;
document.querySelectorAll('.star').forEach(star => {
  star.addEventListener('click', () => {
    currentRating = parseInt(star.dataset.val);
    document.getElementById('feedbackRating').value = currentRating;
    refreshStars(currentRating);
  });
  star.addEventListener('mouseover', () => refreshStars(parseInt(star.dataset.val)));
  star.addEventListener('mouseout',  () => refreshStars(currentRating));
});
function refreshStars(n) {
  document.querySelectorAll('.star').forEach(s =>
    s.classList.toggle('active', parseInt(s.dataset.val) <= n));
}
refreshStars(5);

/* ── Health check ─────────────────────────────────────────────────── */
async function checkHealth() {
  try {
    const r = await fetch(`${API_URL}/api/health`);
    const ok = r.ok;
    document.getElementById('statusDot').className  = 'status-dot ' + (ok ? 'online' : 'offline');
    document.getElementById('statusText').textContent = ok ? 'System online' : 'API offline';
  } catch {
    document.getElementById('statusDot').className  = 'status-dot offline';
    document.getElementById('statusText').textContent = 'Cannot reach API';
  }
}
checkHealth();
setInterval(checkHealth, 30000);

/* ── Toast ────────────────────────────────────────────────────────── */
function showToast(msg, type = '') {
  let container = document.querySelector('.toast-container');
  if (!container) {
    container = document.createElement('div');
    container.className = 'toast-container';
    document.body.appendChild(container);
  }
  const icon = type === 'success' ? 'ti-check' : type === 'error' ? 'ti-x' : 'ti-info-circle';
  const t = document.createElement('div');
  t.className = `toast ${type}`;
  t.innerHTML = `<i class="ti ${icon}"></i> ${msg}`;
  container.appendChild(t);
  setTimeout(() => t.remove(), 3500);
}

/* ── Recommendations ──────────────────────────────────────────────── */
async function getRecommendations() {
  const userId      = document.getElementById('userId').value;
  const method      = document.getElementById('method').value;
  const count       = document.getElementById('count').value;
  const diversity   = document.getElementById('diversity').value;
  const serendipity = document.getElementById('serendipity').value;

  if (!userId) { showToast('Please enter a User ID', 'error'); return; }

  showSkeletons('results', 8);

  try {
    let endpoint = `/api/recommendations/${userId}?n=${count}&diversity=${diversity}&serendipity=${serendipity}`;
    if (method === 'collaborative') endpoint = `/api/recommendations/collaborative/${userId}?n=${count}`;
    if (method === 'content')       endpoint = `/api/recommendations/content-based/${userId}?n=${count}`;

    const res  = await fetch(`${API_URL}${endpoint}`);
    const data = await res.json();

    if (res.ok) renderRecommendations(data, method);
    else { showError('results', data.error || 'Failed to get recommendations'); }
  } catch (e) {
    showError('results', 'Could not reach the API. Is the server running?');
  }
}

function renderRecommendations(data, method) {
  const el = document.getElementById('results');
  if (!data.recommendations || data.recommendations.length === 0) {
    el.innerHTML = emptyState('ti-music-off', 'No recommendations found for this user.');
    return;
  }

  const methodLabels = { hybrid:'Hybrid','collaborative':'Collaborative','content':'Content-Based' };
  const badgeClass   = { hybrid:'badge-hybrid','collaborative':'badge-collab','content':'badge-content' };
  const methodKey    = method === 'hybrid' ? 'hybrid' : method;

  let html = `<div class="results-header">
    <h2>${data.recommendations.length} Recommendations</h2>
    <div class="results-meta">
      <span class="method-badge ${badgeClass[methodKey]}">${methodLabels[methodKey] || method}</span>
      ${method === 'hybrid' && data.diversity_lambda !== undefined
        ? `<span style="font-size:12px">Diversity <strong>${parseFloat(data.diversity_lambda).toFixed(2)}</strong>
           &nbsp;·&nbsp; Serendipity <strong>${parseFloat(data.serendipity_boost).toFixed(2)}</strong></span>`
        : ''}
    </div>
  </div><div class="song-grid">`;

  data.recommendations.forEach((rec, i) => {
    const s   = SONGS[rec.song_id] || { title:`Song #${rec.song_id}`, artist:'Unknown', genre:'Unknown', emoji:'🎵', energy:.5, dance:.5, valence:.5, acoust:.5 };
    const pct = Math.round(rec.score * 100);
    const [gbg, gfg] = GENRE_COLORS[s.genre] || ['#f3f4f6','#374151'];

    html += `<div class="song-card" style="animation-delay:${i * 0.05}s">
      <div class="song-rank">#${i + 1}</div>
      <div class="song-art" style="background:${gbg}">${s.emoji}</div>
      <div class="song-title" title="${s.title}">${s.title}</div>
      <div class="song-artist">${s.artist}</div>
      <div class="song-tags">
        <span class="genre-tag" style="background:${gbg};color:${gfg}">${s.genre}</span>
      </div>
      <div class="score-bar-wrap">
        <div class="score-bar-label"><span>Match score</span><span><strong>${pct}%</strong></span></div>
        <div class="score-bar-bg"><div class="score-bar-fill" style="width:${Math.min(pct,100)}%"></div></div>
      </div>
      <div class="audio-features">
        ${featBar('Energy',   s.energy,  'feat-energy')}
        ${featBar('Dance',    s.dance,   'feat-dance')}
        ${featBar('Mood',     s.valence, 'feat-valence')}
        ${featBar('Acoustic', s.acoust,  'feat-acoust')}
      </div>
    </div>`;
  });

  html += '</div>';
  el.innerHTML = html;
}

function featBar(label, val, cls) {
  const pct = Math.round(val * 100);
  return `<div class="feat ${cls}">
    <span class="feat-label">${label}</span>
    <div class="feat-bar-bg"><div class="feat-bar-fill" style="width:${pct}%"></div></div>
  </div>`;
}

/* ── Similar ──────────────────────────────────────────────────────── */
async function getSimilar() {
  const type  = document.getElementById('similarType').value;
  const id    = document.getElementById('similarId').value;
  const count = document.getElementById('similarCount').value;

  if (!id) { showToast('Please enter an ID', 'error'); return; }

  showSkeletons('similarResults', 5, true);

  try {
    const ep  = type === 'songs'
      ? `/api/similar-songs/${id}?n=${count}`
      : `/api/similar-users/${id}?n=${count}`;
    const res  = await fetch(`${API_URL}${ep}`);
    const data = await res.json();
    if (res.ok) renderSimilar(data, type);
    else showError('similarResults', data.error || 'Failed to find similar items');
  } catch {
    showError('similarResults', 'Could not reach the API.');
  }
}

function renderSimilar(data, type) {
  const el    = document.getElementById('similarResults');
  const items = type === 'users' ? (data.similar_users || []) : (data.similar_songs || []);

  if (!items.length) {
    el.innerHTML = emptyState('ti-search-off', `No similar ${type} found.`); return;
  }

  let html = `<div class="similar-list">`;
  items.forEach((item, i) => {
    const isUser = type === 'users';
    const id     = isUser ? item.user_id : item.song_id;
    const pct    = Math.round(item.similarity * 100);
    const s      = !isUser ? (SONGS[id] || null) : null;
    const name   = isUser ? `User #${id}` : (s ? s.title : `Song #${id}`);
    const sub    = isUser ? `Listener ID ${id}` : (s ? `${s.artist} · ${s.genre}` : '');
    const icon   = isUser ? 'ti-user' : 'ti-music';

    html += `<div class="similar-card">
      <div class="similar-rank">${i + 1}</div>
      <div style="width:32px;text-align:center;font-size:20px;color:var(--purple)">
        <i class="ti ${icon}" aria-hidden="true"></i>
      </div>
      <div class="similar-info">
        <div class="similar-name">${name}</div>
        ${sub ? `<div class="similar-sub">${sub}</div>` : ''}
      </div>
      <div class="similarity-bar-wrap">
        <div class="similarity-bar-bg">
          <div class="similarity-bar-fill" style="width:${pct}%"></div>
        </div>
      </div>
      <span class="similarity-pill">${pct}%</span>
    </div>`;
  });

  html += '</div>';
  el.innerHTML = html;
}

function clearSimilarResults() { document.getElementById('similarResults').innerHTML = ''; }

/* ── Feedback ─────────────────────────────────────────────────────── */
async function recordFeedback() {
  const userId = document.getElementById('feedbackUserId').value;
  const songId = document.getElementById('feedbackSongId').value;
  const rating = document.getElementById('feedbackRating').value;

  if (!userId || !songId) { showToast('Fill in User ID and Song ID', 'error'); return; }

  try {
    const res  = await fetch(`${API_URL}/api/feedback`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ user_id: +userId, song_id: +songId, rating: +rating }),
    });
    const data = await res.json();
    if (res.ok) {
      const s   = SONGS[+songId];
      const msg = s ? `Rated "${s.title}" ${rating}/5 ⭐` : `Rated Song #${songId}: ${rating}/5 ⭐`;
      document.getElementById('feedbackResult').innerHTML =
        `<div class="alert alert-success"><i class="ti ti-check"></i> ${msg}</div>`;
      showToast(msg, 'success');
      setTimeout(clearFeedback, 3000);
    } else {
      document.getElementById('feedbackResult').innerHTML =
        `<div class="alert alert-error"><i class="ti ti-x"></i> ${data.error || 'Failed to record feedback'}</div>`;
    }
  } catch {
    document.getElementById('feedbackResult').innerHTML =
      `<div class="alert alert-error"><i class="ti ti-x"></i> Could not reach the API.</div>`;
  }
}

function clearFeedback() {
  document.getElementById('feedbackUserId').value = '1';
  document.getElementById('feedbackSongId').value = '1';
  currentRating = 5;
  document.getElementById('feedbackRating').value = '5';
  refreshStars(5);
  document.getElementById('feedbackResult').innerHTML = '';
}

/* ── Stats ────────────────────────────────────────────────────────── */
async function getStats() {
  document.getElementById('statsResult').innerHTML = '<div style="padding:20px;color:var(--gray-400)">Loading…</div>';
  try {
    const res  = await fetch(`${API_URL}/api/stats`);
    const data = await res.json();
    if (res.ok) renderStats(data);
    else document.getElementById('statsResult').innerHTML =
      `<div class="alert alert-error"><i class="ti ti-x"></i> ${data.error}</div>`;
  } catch {
    document.getElementById('statsResult').innerHTML =
      `<div class="alert alert-error"><i class="ti ti-x"></i> Could not reach the API.</div>`;
  }
}

function renderStats(d) {
  const w  = d.model_weights    || {};
  const ds = d.diversity_settings || {};
  const r  = d.auto_retrain     || {};
  const progress = r.retrain_threshold
    ? Math.min(100, Math.round((r.new_feedback_since_last_retrain / r.retrain_threshold) * 100))
    : 0;

  document.getElementById('statsResult').innerHTML = `
    <div class="stats-grid">
      ${statCard('ti-music',      d.total_songs        || 0, 'Total Songs',        'songs in catalogue')}
      ${statCard('ti-users',      d.total_users        || 0, 'Total Users',        'registered listeners')}
      ${statCard('ti-activity',   d.total_interactions || 0, 'Interactions',       'ratings recorded')}
      ${statCard('ti-chart-bar',  pct(w.collaborative),     'Collab. Weight',     'collaborative filtering')}
      ${statCard('ti-wavesaw',    pct(w.content_based),     'Content Weight',     'audio-feature filtering')}
      ${statCard('ti-arrows-shuffle', fmt(ds.diversity_lambda), 'Diversity λ',    'MMR re-ranking')}
      ${statCard('ti-wand',       fmt(ds.serendipity_boost),   'Serendipity',     'novelty bonus')}
    </div>

    <div class="settings-section">
      <h2><i class="ti ti-settings" aria-hidden="true"></i> Active Settings</h2>
      ${settingRow('Collaborative weight',  pct(w.collaborative),      'Share given to user-similarity model', 'green')}
      ${settingRow('Content-based weight',  pct(w.content_based),      'Share given to audio-feature model',   'green')}
      ${settingRow('Diversity lambda',       fmt(ds.diversity_lambda),  'MMR trade-off (0 = relevant, 1 = varied)', '')}
      ${settingRow('Serendipity boost',      fmt(ds.serendipity_boost), 'Bonus for pleasantly novel songs',     '')}
      ${r.retrain_threshold ? settingRow('Retrain threshold',  r.retrain_threshold + ' ratings', 'New ratings before auto-refit', 'amber') : ''}
    </div>

    <div class="retrain-status">
      <div class="retrain-info">
        <h3><i class="ti ti-refresh" aria-hidden="true"></i> Auto-Retrain</h3>
        <p>${r.auto_retrain_enabled ? '✓ Enabled' : '✗ Disabled'} · ${r.new_feedback_since_last_retrain ?? 0} new since last retrain</p>
      </div>
      <div class="retrain-progress">
        <div class="retrain-bar-bg">
          <div class="retrain-bar-fill" style="width:${progress}%"></div>
        </div>
        <div class="retrain-pct">${progress}% toward next retrain</div>
      </div>
    </div>`;
}

function statCard(icon, val, label, sub) {
  return `<div class="stat-card">
    <div class="stat-label"><i class="ti ${icon}" aria-hidden="true"></i> ${label}</div>
    <div class="stat-value">${val}</div>
    <div class="stat-sub">${sub}</div>
  </div>`;
}

function settingRow(name, val, desc, type) {
  return `<div class="setting-row">
    <div class="setting-info">
      <div class="setting-name">${name}</div>
      <div class="setting-desc">${desc}</div>
    </div>
    <span class="setting-value ${type}">${val}</span>
  </div>`;
}

async function triggerRetrain() {
  const btn = document.querySelector('.btn-success');
  btn.disabled = true;
  btn.innerHTML = '<i class="ti ti-loader-2" style="animation:spin 1s linear infinite"></i> Retraining…';

  try {
    const res  = await fetch(`${API_URL}/api/retrain`, { method: 'POST' });
    const data = await res.json();
    if (res.ok) {
      showToast('Model retrained successfully!', 'success');
      getStats();
    } else {
      showToast(data.error || 'Retrain failed', 'error');
    }
  } catch {
    showToast('Could not reach the API.', 'error');
  } finally {
    btn.disabled = false;
    btn.innerHTML = '<i class="ti ti-player-play"></i> Retrain Model';
  }
}

/* ── Helpers ──────────────────────────────────────────────────────── */
function showSkeletons(targetId, n, list = false) {
  const el = document.getElementById(targetId);
  if (list) {
    el.innerHTML = Array(n).fill(0).map(() => `
      <div class="skeleton-card" style="height:60px;margin-bottom:10px;border-radius:12px">
        <div class="skeleton-line w60"></div><div class="skeleton-line w40"></div>
      </div>`).join('');
  } else {
    el.innerHTML = `<div class="loading-grid">${
      Array(n).fill(0).map(() => `
        <div class="skeleton-card">
          <div class="skeleton-line w40"></div>
          <div class="skeleton-line w80"></div>
          <div class="skeleton-line w60"></div>
          <div class="skeleton-line w40" style="margin-top:20px"></div>
        </div>`).join('')
    }</div>`;
  }
}

function showError(targetId, msg) {
  document.getElementById(targetId).innerHTML =
    `<div class="alert alert-error" style="margin-top:12px">
       <i class="ti ti-alert-triangle"></i> ${msg}
     </div>`;
}

function emptyState(icon, msg) {
  return `<div class="empty-state"><i class="ti ${icon}" aria-hidden="true"></i><p>${msg}</p></div>`;
}

function clearResults() { document.getElementById('results').innerHTML = ''; }

function pct(v) { return v !== undefined ? (parseFloat(v) * 100).toFixed(0) + '%' : '—'; }
function fmt(v) { return v !== undefined ? parseFloat(v).toFixed(2)          : '—'; }

/* spinner keyframe injected inline */
const style = document.createElement('style');
style.textContent = '@keyframes spin { to { transform: rotate(360deg); } }';
document.head.appendChild(style);
