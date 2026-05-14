"""
Flask API for Music Recommendation System

This module serves as the main Flask application entry point.
All route logic has been separated into individual blueprint modules
in the routes/ directory for better modularity and maintainability.
"""

from flask import Flask, jsonify, send_file
from flask_cors import CORS
import logging
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from config import API_HOST, API_PORT, DEBUG, COLLABORATIVE_WEIGHT, CONTENT_WEIGHT
from data.loader import DataLoader
from data.processor import DataProcessor
from models.hybrid_recommender import HybridRecommender
from models.feedback_manager import FeedbackManager

# Initialize Flask app
app = Flask(__name__, static_folder=str(Path(__file__).parent))
CORS(app)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global variables for models
recommender = None
feedback_manager = None
data_loader = None

def initialize_models():
    """Initialize recommendation models and data"""
    global recommender, feedback_manager, data_loader
    
    try:
        logger.info("Initializing models...")
        
        # Load data
        data_loader = DataLoader(data_dir="data")
        songs, users, history = data_loader.load_all()
        
        logger.info(f"Loaded {len(songs)} songs, {len(users)} users, {len(history)} history records")
        
        # Process data
        processor = DataProcessor()
        user_item_matrix = processor.create_user_item_matrix(history)
        song_features = songs.copy()
        
        # Initialize and train hybrid recommender
        recommender = HybridRecommender(
            collaborative_weight=COLLABORATIVE_WEIGHT,
            content_weight=CONTENT_WEIGHT
        )
        recommender.fit(user_item_matrix, song_features)
        
        # Initialize feedback manager
        feedback_manager = FeedbackManager(history_file="data/listening_history.csv")
        
        # Inject models into route modules
        inject_models_into_routes()
        
        logger.info("Models initialized successfully")
        return True
    
    except Exception as e:
        logger.error(f"Error initializing models: {str(e)}")
        return False

def inject_models_into_routes():
    """Inject initialized models into route blueprints"""
    import routes.recommendations as rec_module
    rec_module.recommender = recommender
    
    import routes.feedback as fb_module
    fb_module.feedback_manager = feedback_manager
    
    import routes.similar as sim_module
    sim_module.recommender = recommender
    
    import routes.stats as stats_module
    stats_module.recommender = recommender

@app.route('/', methods=['GET'])
def home():
    """Root endpoint - Serve the web interface"""
    try:
        html_file = Path(__file__).parent / 'index.html'
        return send_file(html_file)
    except Exception as e:
        logger.error(f"Error serving home page: {str(e)}")
        return jsonify({
            'service': 'Music Recommendation System API',
            'version': '1.0.0',
            'status': 'active',
            'message': 'Web interface not available, but API is working',
            'endpoints': {
                'health': 'GET /api/health - Health check',
                'recommendations': 'GET /api/recommendations/<user_id>?n=10 - Get hybrid recommendations',
                'collaborative': 'GET /api/recommendations/collaborative/<user_id> - Collaborative filtering',
                'content_based': 'GET /api/recommendations/content-based/<user_id> - Content-based filtering',
                'feedback': 'POST /api/feedback - Record user feedback',
                'similar_users': 'GET /api/similar-users/<user_id>?n=5 - Find similar users',
                'similar_songs': 'GET /api/similar-songs/<song_id>?n=5 - Find similar songs',
                'stats': 'GET /api/stats - System statistics'
            }
        }), 200

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    return jsonify({'error': 'Internal server error'}), 500

# Register route blueprints
from routes.recommendations import recommendations_bp
from routes.feedback import feedback_bp
from routes.similar import similar_bp
from routes.stats import stats_bp

app.register_blueprint(recommendations_bp)
app.register_blueprint(feedback_bp)
app.register_blueprint(similar_bp)
app.register_blueprint(stats_bp)

if __name__ == '__main__':
    # Initialize models on startup
    if initialize_models():
        app.run(host=API_HOST, port=API_PORT, debug=DEBUG)
    else:
        logger.error("Failed to initialize models. Exiting.")
        sys.exit(1)

