"""
Main CLI entry point for the Music Recommendation System.

Run with:
    cd src
    python main.py
"""

import sys
from pathlib import Path

from config import (
    NUM_RECOMMENDATIONS,
    COLLABORATIVE_WEIGHT, CONTENT_WEIGHT,
    DIVERSITY_LAMBDA, SERENDIPITY_BOOST,
    RETRAIN_THRESHOLD
)
from utils.logger import get_logger
from data.loader import DataLoader
from data.processor import DataProcessor
from models.hybrid_recommender import HybridRecommender
from models.feedback_manager import FeedbackManager
from features.audio_features import AudioFeatureExtractor

# Root-level persistence helpers
sys.path.insert(0, str(Path(__file__).parent.parent))
from models.model_saver import save_model, load_model, model_exists
from features.feature_cache import save_features, load_features, features_exist

logger = get_logger(__name__)


def main():
    """Main application flow."""
    try:
        logger.info("Starting Music Recommendation System...")

        # ── Verify data directory ─────────────────────────────────────
        data_dir = Path("data")
        if not data_dir.exists():
            logger.warning("Data directory not found. Creating it now...")
            data_dir.mkdir(exist_ok=True)
            logger.info(
                "Please add songs.csv, users.csv, and listening_history.csv "
                "to the data/ folder, then re-run."
            )
            return

        # ── Load raw data ─────────────────────────────────────────────
        logger.info("Loading data...")
        data_loader = DataLoader(data_dir="data")

        try:
            songs, users, history = data_loader.load_all()
        except FileNotFoundError as e:
            logger.error(f"Data files not found: {e}")
            logger.info(
                "Ensure data/ contains: songs.csv, users.csv, listening_history.csv"
            )
            return

        logger.info(
            f"Loaded {len(songs)} songs, {len(users)} users, "
            f"{len(history)} history records"
        )

        # ── Build user-item matrix ────────────────────────────────────
        logger.info("Processing data...")
        processor        = DataProcessor()
        user_item_matrix = processor.create_user_item_matrix(history)
        logger.info(f"User-item matrix shape: {user_item_matrix.shape}")

        # ── Load or compute song features ─────────────────────────────
        if features_exist():
            song_features = load_features()
            logger.info("Loaded cached audio features from features/audio_features.pkl")
        else:
            extractor     = AudioFeatureExtractor()
            song_features = extractor.extract_from_dataframe(songs)
            save_features(song_features)
            logger.info("Audio features computed and cached to features/audio_features.pkl")

        # ── Load or train recommender ─────────────────────────────────
        logger.info("Initializing recommendation models...")
        if model_exists():
            recommender = load_model()
            recommender.fit(user_item_matrix, song_features)
            logger.info("Loaded cached model and re-fitted on latest data")
        else:
            recommender = HybridRecommender(
                collaborative_weight=COLLABORATIVE_WEIGHT,
                content_weight=CONTENT_WEIGHT,
                diversity_lambda=DIVERSITY_LAMBDA,
                serendipity_boost=SERENDIPITY_BOOST,
            )
            recommender.fit(user_item_matrix, song_features)
            save_model(recommender)
            logger.info("Model trained from scratch and cached to models/trained_model.pkl")

        # ── Wire up auto-retrain ──────────────────────────────────────
        def _retrain():
            logger.info("Auto-retrain triggered — reloading history and refitting...")
            fresh_history = data_loader.load_listening_history()
            fresh_matrix  = DataProcessor().create_user_item_matrix(fresh_history)
            recommender.fit(fresh_matrix, song_features)
            save_model(recommender)
            logger.info("Auto-retrain complete — model re-cached")

        feedback_mgr = FeedbackManager(
            history_file="data/listening_history.csv",
            retrain_callback=_retrain,
            retrain_threshold=RETRAIN_THRESHOLD,
        )
        logger.info(f"Auto-retrain enabled: every {RETRAIN_THRESHOLD} new ratings")

        # ── Demo: recommendations for first user ──────────────────────
        if len(users) > 0:
            sample_user = int(users.iloc[0]['user_id'])
            logger.info(f"Getting recommendations for user {sample_user}...")

            recommendations = recommender.get_recommendations(
                sample_user,
                num_recommendations=NUM_RECOMMENDATIONS,
            )

            if recommendations:
                logger.info("Top recommendations:")
                for i, (song_id, score) in enumerate(recommendations, 1):
                    song  = songs[songs['song_id'] == song_id]
                    title = song['title'].values[0] if len(song) > 0 else "Unknown"
                    artist = song['artist'].values[0] if len(song) > 0 else ""
                    logger.info(f"  {i:2}. {title} — {artist}  (score: {score:.4f})")
            else:
                logger.info("No recommendations available for this user")

        # ── Demo: record a feedback interaction ───────────────────────
        logger.info("Recording a sample feedback interaction...")
        feedback_mgr.record_feedback(user_id=1, song_id=5, rating=4.5)

        logger.info("Application completed successfully!")

    except Exception as e:
        logger.error(f"Application error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
