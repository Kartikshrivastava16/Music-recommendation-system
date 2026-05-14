# Music Recommendation System
This project is an ML-based music recommendation system that suggests songs based on user preferences, listening history, and audio features.

## Project Overview
- Uses collaborative filtering to find similar users
- Uses content-based filtering to analyze audio features
- Combines both approaches in a hybrid recommender
- Includes Flask API for recommendations
- Supports continuous learning from user interactions

## Key Components
1. **Collaborative Filtering** - Finds users with similar tastes
2. **Content-Based Filtering** - Analyzes audio features (tempo, genre, mood, energy, etc.)
3. **Hybrid Recommender** - Combines both approaches with configurable weights
4. **Feature Engineering** - Creates derived features from listening history
5. **Flask API** - Provides REST endpoints for recommendations

## Data Format
CSV files should be placed in the `data/` folder:
- `songs.csv` - Song metadata with audio features
- `users.csv` - User information
- `listening_history.csv` - User ratings/feedback

## Running the Application
- Main app: `python src/main.py`
- API server: `python src/api/app.py`
- Tests: `pytest tests/`
- Make commands: `make help`
