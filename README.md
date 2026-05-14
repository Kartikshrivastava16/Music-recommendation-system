# Music Recommendation System

An intelligent ML-based music recommendation system that suggests songs based on user preferences, listening history, and audio features. The system uses collaborative filtering and content-based filtering techniques to discover music that aligns with user tastes.

## Features

- **Collaborative Filtering**: Finds similar users and recommends songs they liked
- **Content-Based Filtering**: Analyzes audio features (tempo, genre, mood) to match with user preferences
- **Audio Feature Analysis**: Extracts and analyzes song characteristics
- **User Learning**: Continuously learns from user interactions to improve recommendations
- **Listening History Tracking**: Maintains user listening patterns and preferences
- **Real-time Recommendations**: Generates personalized recommendations on demand

## Project Structure

```
Music Recommendation System/
├── src/
│   ├── __init__.py
│   ├── main.py                      # Application entry point
│   ├── config.py                    # Configuration settings
│   ├── models/
│   │   ├── __init__.py
│   │   ├── collaborative_filtering.py
│   │   ├── content_based_filtering.py
│   │   └── hybrid_recommender.py
│   ├── data/
│   │   ├── __init__.py
│   │   ├── loader.py               # Data loading utilities
│   │   └── processor.py            # Data processing and normalization
│   ├── features/
│   │   ├── __init__.py
│   │   ├── audio_features.py       # Audio feature extraction
│   │   └── feature_engineer.py     # Feature engineering
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── logger.py               # Logging utilities
│   │   └── validators.py           # Input validation
│   └── api/
│       ├── __init__.py
│       ├── app.py                  # Flask/FastAPI application
│       └── routes.py               # API endpoints
├── data/
│   ├── songs.csv                   # Song data (placeholder)
│   ├── users.csv                   # User data (placeholder)
│   └── listening_history.csv       # Listening history (placeholder)
├── tests/
│   ├── __init__.py
│   ├── test_models.py
│   ├── test_features.py
│   └── test_api.py
├── requirements.txt                 # Python dependencies
├── setup.py                         # Package setup
├── .env.example                     # Environment variables template
├── .gitignore                       # Git ignore file
└── Makefile                         # Common commands
```

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd "Music Recommendation System"
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Running the Application

```bash
python src/main.py
```

### Starting the API Server

```bash
python src/api/app.py
```

### Running Tests

```bash
pytest tests/
```

## API Endpoints

- `GET /api/recommendations/<user_id>` - Get personalized recommendations for a user
- `POST /api/feedback` - Submit user feedback on recommendations
- `GET /api/songs/<song_id>/features` - Get audio features of a song
- `GET /api/users/<user_id>/history` - Get user's listening history
- `POST /api/train` - Train the recommendation model

## Technologies Used

- **Python 3.9+**: Core programming language
- **scikit-learn**: Machine learning algorithms
- **pandas**: Data manipulation and analysis
- **numpy**: Numerical computations
- **Flask/FastAPI**: Web framework for API
- **librosa**: Audio feature extraction
- **sqlite3**: Database for user data

## Configuration

Copy `.env.example` to `.env` and update with your settings:

```
DATABASE_URL=sqlite:///music_recommendations.db
MODEL_PATH=./models/trained_model.pkl
LOG_LEVEL=INFO
```

## Development

### Code Style

Follow PEP 8 guidelines. Use `black` for code formatting and `flake8` for linting:

```bash
black src/
flake8 src/
```

### Contributing

1. Create a feature branch
2. Commit changes
3. Push to the branch
4. Create a Pull Request

## Performance Optimization

- Caching recommendations for popular users
- Batch processing of recommendations
- Model serialization for quick loading
- Efficient similarity computations using vectorized operations

## Future Enhancements

- [ ] Deep learning models (Neural Collaborative Filtering)
- [ ] Real-time streaming recommendations
- [ ] Genre classification using neural networks
- [ ] Mood detection from audio
- [ ] Social recommendations
- [ ] A/B testing framework
- [ ] Advanced feature engineering

## License

MIT License

## Contact

For questions or issues, please create an issue in the repository.
