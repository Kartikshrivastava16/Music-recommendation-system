"""
Flask API for Music Recommendation System

All route logic is separated into blueprint modules in routes/ for modularity.
On startup the system tries to load a cached model + features from disk;
if none exists it trains from scratch and caches the result.
"""

from flask import Flask, jsonify, send_file
from flask_cors import CORS
import logging
import sys
from pathlib import Path

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from config import (
    API_HOST, API_PORT, DEBUG,
    COLLABORATIVE_WEIGHT, CONTENT_WEIGHT,
    DIVERSITY_LAMBDA, SERENDIPITY_BOOST,
    RETRAIN_THRESHOLD
)
from data.loader import DataLoader
from data.processor import DataProcessor
from models.hybrid_recommender import HybridRecommender
from models.feedback_manager import FeedbackManager

# Root-level persistence helpers (models/ and features/ folders)
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from models.model_saver import save_model, load_model, model_exists
from features.feature_cache import save_features, load_features, features_exist

# Initialize Flask app
app = Flask(__name__, static_folder=str(Path(__file__).parent / 'static'))
CORS(app)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Globals
recommender:     HybridRecommender = None
feedback_manager: FeedbackManager  = None
data_loader:      DataLoader        = None


def initialize_models():
    """
    Initialize recommendation models and data.

    Strategy:
    1. Try loading a cached model + features from disk (fast restart).
    2. If not found, train from scratch, then cache both to disk.
    3. Wire up the auto-retrain callback in FeedbackManager.
    """
    global recommender, feedback_manager, data_loader

    try:
        logger.info("Initializing models...")

        # ── Load raw data ──────────────────────────────────────────────
        # Resolve `data/` directory (support running from `src/` or repo root)
        repo_root = Path(__file__).resolve().parent.parent.parent
        candidates = [Path.cwd(), Path(__file__).resolve().parent, Path(__file__).resolve().parent.parent, repo_root]
        data_dir = None
        for base in candidates:
            candidate = (base / "data")
            if candidate.exists():
                data_dir = candidate.resolve()
                logger.info(f"Using data directory: {data_dir}")
                break
        if data_dir is None:
            # If repo-root `data/` exists prefer it; otherwise fall back to cwd/data
            if (repo_root / "data").exists():
                data_dir = (repo_root / "data").resolve()
            else:
                data_dir = Path("data")

        data_loader = DataLoader(data_dir=str(data_dir))
        songs, users, history = data_loader.load_all()
        logger.info(f"Loaded {len(songs)} songs, {len(users)} users, {len(history)} history records")

        processor        = DataProcessor()
        user_item_matrix = processor.create_user_item_matrix(history)

        # ── Load or build song features ───────────────────────────────
        if features_exist():
            song_features = load_features()
            logger.info("Loaded cached audio features from features/audio_features.pkl")
        else:
            from features.audio_features import AudioFeatureExtractor
            extractor     = AudioFeatureExtractor()
            song_features = extractor.extract_from_dataframe(songs)
            save_features(song_features)
            logger.info("Audio features computed and cached to features/audio_features.pkl")

        # ── Load or train recommender ─────────────────────────────────
        if model_exists():
            recommender = load_model()
            # Re-fit on fresh data so ratings/history are always current
            recommender.fit(user_item_matrix, song_features)
            logger.info("Loaded cached model from models/trained_model.pkl and re-fitted on latest data")
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

        # ── Auto-retrain callback ─────────────────────────────────────
        _song_features = song_features  # captured in closure

        def _retrain_callback():
            """Reload history from disk, refit, and re-cache the model."""
            try:
                fresh_history = data_loader.load_listening_history()
                fresh_matrix  = DataProcessor().create_user_item_matrix(fresh_history)
                recommender.fit(fresh_matrix, _song_features)
                save_model(recommender)
                logger.info("Auto-retrain complete — model re-cached to disk")
            except Exception as err:
                logger.error(f"Auto-retrain callback error: {err}")

        feedback_manager = FeedbackManager(
            history_file=str((data_dir / "listening_history.csv")),
            retrain_callback=_retrain_callback,
            retrain_threshold=RETRAIN_THRESHOLD,
        )
        logger.info(f"Auto-retrain enabled: every {RETRAIN_THRESHOLD} new ratings")

        inject_models_into_routes()
        logger.info("Models initialized successfully")
        return True

    except Exception as e:
        logger.error(f"Error initializing models: {e}", exc_info=True)
        return False


def inject_models_into_routes():
    """Push initialized model/manager references into every route blueprint."""
    from .routes import recommendations as rec_module
    rec_module.recommender      = recommender
    rec_module.feedback_manager = feedback_manager

    from .routes import feedback as fb_module
    fb_module.feedback_manager  = feedback_manager

    from .routes import similar as sim_module
    sim_module.recommender      = recommender

    from .routes import stats as stats_module
    stats_module.recommender      = recommender
    stats_module.feedback_manager = feedback_manager


# ── Routes ────────────────────────────────────────────────────────────────

@app.route('/', methods=['GET'])
def home():
    """Serve the web UI."""
    try:
        html_file = Path(__file__).parent / 'index.html'
        return send_file(html_file)
    except Exception as e:
        logger.error(f"Error serving home page: {e}")
        return jsonify({
            'service': 'Music Recommendation System API',
            'version': '1.0.0',
            'status': 'active',
            'endpoints': {
                'health':        'GET  /api/health',
                'recommendations':'GET  /api/recommendations/<user_id>?n=10&diversity=0.3&serendipity=0.15',
                'collaborative': 'GET  /api/recommendations/collaborative/<user_id>',
                'content_based': 'GET  /api/recommendations/content-based/<user_id>',
                'feedback':      'POST /api/feedback',
                'similar_users': 'GET  /api/similar-users/<user_id>?n=5',
                'similar_songs': 'GET  /api/similar-songs/<song_id>?n=5',
                'stats':         'GET  /api/stats',
                'retrain':       'POST /api/retrain',
                'settings':      'PATCH /api/settings',
            }
        }), 200


@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404


@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500


# ── Register blueprints ────────────────────────────────────────────────────
from .routes.recommendations import recommendations_bp
from .routes.feedback        import feedback_bp
from .routes.similar         import similar_bp
from .routes.stats           import stats_bp

app.register_blueprint(recommendations_bp)
app.register_blueprint(feedback_bp)
app.register_blueprint(similar_bp)
app.register_blueprint(stats_bp)


if __name__ == '__main__':
    if initialize_models():
        app.run(host=API_HOST, port=API_PORT, debug=DEBUG)
    else:
        logger.error("Failed to initialize models. Exiting.")
        sys.exit(1)
