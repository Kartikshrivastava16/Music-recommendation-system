"""
Configuration module for Music Recommendation System
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
env_file = Path(__file__).parent.parent / ".env"
if env_file.exists():
    load_dotenv(env_file)

# Database Configuration
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///music_recommendations.db")
MODEL_PATH = os.getenv("MODEL_PATH", "./models/trained_model.pkl")

# Recommendation Configuration
NUM_RECOMMENDATIONS = int(os.getenv("NUM_RECOMMENDATIONS", 10))
SIMILARITY_THRESHOLD = float(os.getenv("SIMILARITY_THRESHOLD", 0.3))
MIN_RATING = int(os.getenv("MIN_RATING", 1))
MAX_RATING = int(os.getenv("MAX_RATING", 5))

# Weighted Hybrid Approach
COLLABORATIVE_WEIGHT = float(os.getenv("COLLABORATIVE_WEIGHT", 0.6))
CONTENT_WEIGHT = float(os.getenv("CONTENT_WEIGHT", 0.4))

# Diversity & Serendipity
DIVERSITY_LAMBDA = float(os.getenv("DIVERSITY_LAMBDA", 0.3))
SERENDIPITY_BOOST = float(os.getenv("SERENDIPITY_BOOST", 0.15))

# Auto-Retraining
RETRAIN_THRESHOLD = int(os.getenv("RETRAIN_THRESHOLD", 10))

# API Configuration
API_HOST = os.getenv("API_HOST", "0.0.0.0")
API_PORT = int(os.getenv("API_PORT", 5000))
DEBUG = os.getenv("DEBUG", "False").lower() == "true"

# Logging Configuration
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FILE = os.getenv("LOG_FILE", "logs/app.log")

# Feature Configuration
ENABLE_AUDIO_FEATURES = os.getenv("ENABLE_AUDIO_FEATURES", "True").lower() == "true"
AUDIO_FEATURES_PATH = os.getenv("AUDIO_FEATURES_PATH", "./features/audio_features.pkl")

# Create necessary directories
Path("logs").mkdir(exist_ok=True)
Path("models").mkdir(exist_ok=True)
Path("features").mkdir(exist_ok=True)
