# Music Recommendation System - Quick Start Guide

## 🚀 5-Minute Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run the CLI Application
```bash
cd src
python main.py
```

**Output Example:**
```
INFO - Starting Music Recommendation System...
INFO - Loading data...
INFO - Loaded 25 songs, 15 users, 75 history records
INFO - Processing data...
INFO - Training recommendation models...
INFO - Top recommendations for User 1:
  1. Heat Waves (Score: 0.8432)
  2. Levitating (Score: 0.7821)
  3. Blinding Lights (Score: 0.7654)
```

### 3. Start Flask API Server
```bash
cd src
python -m api.app
```

**Output:**
```
 * Serving Flask app 'app'
 * Running on http://0.0.0.0:5000
```

### 4. Test API Endpoints
Open a new terminal and run:

```bash
# Health check
curl http://localhost:5000/health

# Get recommendations for user 1
curl "http://localhost:5000/api/recommendations/1?n=5"

# Get similar users
curl "http://localhost:5000/api/similar-users/1?n=3"

# Record feedback
curl -X POST http://localhost:5000/api/feedback \
  -H "Content-Type: application/json" \
  -d '{"user_id": 1, "song_id": 2, "rating": 5}'
```

### 5. Run Tests
```bash
# Run all tests
pytest tests/ -v

# Run specific test
pytest tests/test_models.py -v
```

---

## 📊 Project Structure

```
Music Recommendation System/
├── src/
│   ├── main.py                          # CLI entry point
│   ├── config.py                        # Configuration
│   ├── api/
│   │   ├── app.py                       # Flask API server
│   │   └── __init__.py
│   ├── models/
│   │   ├── collaborative_filtering.py   # User-based recommendations
│   │   ├── content_based_filtering.py   # Feature-based recommendations
│   │   ├── hybrid_recommender.py        # Combined approach
│   │   ├── feedback_manager.py          # Learning system
│   │   └── __init__.py
│   ├── data/
│   │   ├── loader.py                    # CSV data loading
│   │   ├── processor.py                 # Data transformation
│   │   └── __init__.py
│   ├── features/
│   │   ├── feature_engineer.py          # Feature extraction
│   │   └── __init__.py
│   ├── utils/
│   │   ├── validators.py                # Input validation
│   │   ├── logger.py                    # Logging setup
│   │   └── __init__.py
│   └── __init__.py
├── data/
│   ├── songs.csv                        # Song metadata & features
│   ├── users.csv                        # User information
│   └── listening_history.csv            # User ratings
├── tests/
│   ├── test_models.py                   # Model tests
│   ├── test_data.py                     # Data loading tests
│   └── test_api.py                      # API tests
├── requirements.txt                     # Python dependencies
├── README.md                            # Project overview
└── IMPLEMENTATION_GUIDE.md              # Detailed documentation
```

---

## 🔑 Key API Endpoints

### Get Recommendations
```
GET /api/recommendations/<user_id>?n=10&min_score=0.5
```

Response:
```json
{
  "user_id": 1,
  "recommendations": [
    {"song_id": 5, "score": 0.85},
    {"song_id": 10, "score": 0.78}
  ],
  "count": 2
}
```

### Record User Feedback
```
POST /api/feedback
Content-Type: application/json

{
  "user_id": 1,
  "song_id": 5,
  "rating": 4.5,
  "timestamp": "2024-01-15T10:30:00"
}
```

### Get Similar Users
```
GET /api/similar-users/<user_id>?n=5
```

### Get System Stats
```
GET /api/stats
```

---

## ⚙️ Configuration

Edit `src/config.py` to customize:

```python
# Number of recommendations to return
NUM_RECOMMENDATIONS = 10

# Model weights (must sum to 1.0)
COLLABORATIVE_WEIGHT = 0.6  # 60% user similarity
CONTENT_WEIGHT = 0.4         # 40% song features

# API Server
API_HOST = "0.0.0.0"
API_PORT = 5000
DEBUG = False

# Logging
LOG_LEVEL = "INFO"
LOG_FILE = "logs/app.log"
```

---

## 📈 Sample Data

The project includes sample data:
- **25 Popular Songs** (Blinding Lights, Shape of You, etc.)
- **15 Users** (from 10 different countries)
- **75 Listening Records** (user ratings and timestamps)

To add more data:
1. Update CSV files in the `data/` folder
2. Restart the application
3. API will use new data automatically

---

## 🧪 Testing

```bash
# Run all tests with verbose output
pytest tests/ -v

# Run specific test file
pytest tests/test_models.py -v

# Run specific test class
pytest tests/test_models.py::TestHybridRecommender -v

# Run with code coverage
pytest tests/ --cov=src --cov-report=html

# Run tests matching a pattern
pytest tests/ -k "test_get_recommendations" -v
```

---

## 🔍 How Recommendations Work

### Collaborative Filtering (60%)
1. Find users similar to target user
2. Look at songs they liked
3. Recommend highly-rated songs

### Content-Based Filtering (40%)
1. Get user's favorite songs
2. Find songs with similar audio features
3. Recommend similar songs

### Hybrid Result
- Combine both approaches with weights
- Return top N songs
- Exclude already-rated songs

---

## 🐛 Troubleshooting

**Problem:** `ModuleNotFoundError: No module named 'src'`
```bash
# Solution: Run from src directory
cd src
python main.py
```

**Problem:** `FileNotFoundError: songs.csv not found`
```bash
# Solution: Ensure CSV files exist in data/ folder
ls data/
# Should show: listening_history.csv  songs.csv  users.csv
```

**Problem:** Port 5000 already in use
```bash
# Solution: Change port in config.py or use different port
python -m api.app --port 5001
```

**Problem:** Tests fail with import errors
```bash
# Solution: Install test dependencies
pip install pytest pytest-cov
```

---

## 📚 Learn More

- **IMPLEMENTATION_GUIDE.md** - Detailed feature documentation
- **README.md** - Project overview
- **tests/** - See examples in test files
- **src/api/app.py** - API endpoint definitions

---

## 🎯 What's Next?

1. ✅ Run `python src/main.py` to see recommendations
2. ✅ Start API with `python src/api/app.py`
3. ✅ Test endpoints with curl or Postman
4. ✅ Add your own data to CSV files
5. ✅ Extend with database integration

---

**Happy recommending! 🎵**
