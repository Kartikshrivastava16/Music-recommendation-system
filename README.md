# Music Recommendation System

A production-ready machine-learning system that suggests songs based on user preferences,
listening history, and audio features — using collaborative filtering, content-based filtering,
and a diversity-aware hybrid approach that continuously learns from user feedback.

---

## Features

- **Collaborative Filtering** — user-user cosine similarity to find neighbours and recommend songs they loved
- **Content-Based Filtering** — audio feature cosine similarity (tempo, energy, danceability, valence, acousticness, instrumentalness)
- **Hybrid Recommender** — weighted combination (60 % collaborative / 40 % content) with configurable weights
- **MMR Diversity Re-ranking** — Maximal Marginal Relevance keeps recommendation lists varied rather than clustering around one style
- **Serendipity Boost** — bell-curve novelty bonus surfaces pleasant surprises without straying too far from taste
- **Auto-Retraining** — `FeedbackManager` automatically refits the model after every N new ratings (default 10)
- **Model & Feature Caching** — trained model and audio features are persisted to disk so restarts are instant
- **REST API** — Flask with blueprints, CORS, and a browser UI
- **Full Test Suite** — 50+ unit tests covering models, data pipeline, and API endpoints

---

## Project Structure

```
Music Recommendation System/
├── src/
│   ├── main.py                          # CLI entry point
│   ├── config.py                        # All configuration (reads .env)
│   ├── api/
│   │   ├── app.py                       # Flask app + model initialisation
│   │   ├── index.html                   # Browser UI
│   │   ├── static/css/styles.css
│   │   ├── static/js/app.js
│   │   └── routes/
│   │       ├── recommendations.py       # GET /api/recommendations/<user_id>
│   │       ├── feedback.py              # POST /api/feedback
│   │       ├── similar.py               # GET /api/similar-users|songs/<id>
│   │       └── stats.py                 # GET /api/stats  POST /api/retrain  PATCH /api/settings
│   ├── models/
│   │   ├── collaborative_filtering.py
│   │   ├── content_based_filtering.py
│   │   ├── hybrid_recommender.py        # MMR + serendipity
│   │   └── feedback_manager.py          # Auto-retrain
│   ├── data/
│   │   ├── loader.py
│   │   └── processor.py
│   ├── features/
│   │   ├── audio_features.py            # librosa extraction + CSV mode
│   │   └── feature_engineer.py          # Derived features (popularity, avg rating)
│   └── utils/
│       ├── logger.py
│       └── validators.py
├── models/
│   └── model_saver.py                   # save_model / load_model (pickle)
├── features/
│   └── feature_cache.py                 # save_features / load_features (pickle)
├── data/
│   ├── songs.csv                        # 55 songs with audio features
│   ├── users.csv                        # 25 users
│   └── listening_history.csv            # 110+ ratings
├── logs/
│   └── app.log                          # Runtime log file
├── tests/
│   ├── test_models.py
│   ├── test_data.py
│   └── test_api.py
├── requirements.txt
├── Makefile
└── .env                                 # Environment overrides
```

---

## Quick Start

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Run the CLI
```bash
cd src
python main.py
```

### 3. Start the API server
```bash
cd src
python -m api.app
# Open http://localhost:5000 in your browser
```

### 4. Test API endpoints
```bash
# Health check
curl http://localhost:5000/api/health

# Hybrid recommendations (with diversity + serendipity)
curl "http://localhost:5000/api/recommendations/1?n=10&diversity=0.3&serendipity=0.15"

# Collaborative-only
curl "http://localhost:5000/api/recommendations/collaborative/1?n=5"

# Record feedback (triggers auto-retrain after threshold)
curl -X POST http://localhost:5000/api/feedback \
  -H "Content-Type: application/json" \
  -d '{"user_id": 1, "song_id": 5, "rating": 4.5}'

# System stats (shows diversity settings + retrain status)
curl http://localhost:5000/api/stats

# Manual retrain
curl -X POST http://localhost:5000/api/retrain

# Update settings at runtime
curl -X PATCH http://localhost:5000/api/settings \
  -H "Content-Type: application/json" \
  -d '{"diversity_lambda": 0.5, "serendipity_boost": 0.2, "retrain_threshold": 20}'
```

### 5. Run tests
```bash
pytest tests/ -v
# With coverage
pytest tests/ --cov=src --cov-report=html
```

---

## Configuration

All settings are read from `.env` (or environment variables):

| Variable | Default | Description |
|---|---|---|
| `COLLABORATIVE_WEIGHT` | `0.6` | Weight for collaborative filtering |
| `CONTENT_WEIGHT` | `0.4` | Weight for content-based filtering |
| `DIVERSITY_LAMBDA` | `0.3` | MMR diversity (0 = relevance, 1 = variety) |
| `SERENDIPITY_BOOST` | `0.15` | Novelty bonus for unexpected discoveries |
| `RETRAIN_THRESHOLD` | `10` | New ratings before auto-retrain fires |
| `NUM_RECOMMENDATIONS` | `10` | Default result count |
| `API_HOST` | `0.0.0.0` | Flask host |
| `API_PORT` | `5000` | Flask port |
| `LOG_LEVEL` | `INFO` | Logging verbosity |

---

## How It Works

```
User Request
    │
    ▼
Collaborative Filtering (60%)     Content-Based Filtering (40%)
Find similar users → their songs  Find audio-similar songs to user's history
    │                                      │
    └──────── Weighted combination ────────┘
                      │
              Serendipity Boost
        (reward mildly novel songs)
                      │
              MMR Re-ranking
        (pick diverse final list)
                      │
              Top N Recommendations

User Feedback → FeedbackManager → auto-retrain every N ratings
                                → save_model() caches to disk
```

---

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/health` | Health check |
| GET | `/api/recommendations/<user_id>` | Hybrid recommendations (`?n`, `?diversity`, `?serendipity`) |
| GET | `/api/recommendations/collaborative/<user_id>` | Collaborative only |
| GET | `/api/recommendations/content-based/<user_id>` | Content-based only |
| POST | `/api/feedback` | Record a rating |
| GET | `/api/similar-users/<user_id>` | Similar users |
| GET | `/api/similar-songs/<song_id>` | Similar songs |
| GET | `/api/stats` | System statistics |
| POST | `/api/retrain` | Manual model retrain |
| PATCH | `/api/settings` | Update diversity/serendipity/threshold at runtime |
