"""
Flask API for Music Recommendation System
"""

from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import logging
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from config import (
    API_HOST, API_PORT, DEBUG, NUM_RECOMMENDATIONS,
    COLLABORATIVE_WEIGHT, CONTENT_WEIGHT
)
from data.loader import DataLoader
from data.processor import DataProcessor
from models.hybrid_recommender import HybridRecommender
from models.feedback_manager import FeedbackManager
from utils.validators import validate_user_id, validate_song_id, validate_rating

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
        
        logger.info("Models initialized successfully")
        return True
    
    except Exception as e:
        logger.error(f"Error initializing models: {str(e)}")
        return False

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
                'health': 'GET /health - Health check',
                'recommendations': 'GET /api/recommendations/<user_id>?n=10 - Get hybrid recommendations',
                'collaborative': 'GET /api/recommendations/collaborative/<user_id> - Collaborative filtering',
                'content_based': 'GET /api/recommendations/content-based/<user_id> - Content-based filtering',
                'feedback': 'POST /api/feedback - Record user feedback',
                'similar_users': 'GET /api/similar-users/<user_id>?n=5 - Find similar users',
                'similar_songs': 'GET /api/similar-songs/<song_id>?n=5 - Find similar songs',
                'stats': 'GET /api/stats - System statistics'
            }
        }), 200

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'Music Recommendation System API'
    }), 200

@app.route('/api/recommendations/<int:user_id>', methods=['GET'])
def get_recommendations(user_id):
    """
    Get recommendations for a user
    
    Query parameters:
    - n: number of recommendations (default: 10)
    - min_score: minimum confidence score (default: 0.0)
    
    Returns:
        JSON array of recommendations with song_id and score
    """
    try:
        # Validate user
        if not validate_user_id(user_id):
            return jsonify({'error': 'Invalid user ID'}), 400
        
        # Get parameters
        n_recommendations = request.args.get('n', NUM_RECOMMENDATIONS, type=int)
        min_score = request.args.get('min_score', 0.0, type=float)
        
        if n_recommendations < 1 or n_recommendations > 100:
            n_recommendations = NUM_RECOMMENDATIONS
        
        # Get recommendations
        recommendations = recommender.get_recommendations(
            user_id=user_id,
            num_recommendations=n_recommendations
        )
        
        # Filter by minimum score
        filtered_recommendations = [
            {'song_id': song_id, 'score': float(score)}
            for song_id, score in recommendations
            if score >= min_score
        ]
        
        return jsonify({
            'user_id': user_id,
            'recommendations': filtered_recommendations,
            'count': len(filtered_recommendations)
        }), 200
    
    except Exception as e:
        logger.error(f"Error getting recommendations: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/recommendations/collaborative/<int:user_id>', methods=['GET'])
def get_collaborative_recommendations(user_id):
    """Get recommendations using only collaborative filtering"""
    try:
        if not validate_user_id(user_id):
            return jsonify({'error': 'Invalid user ID'}), 400
        
        n_recommendations = request.args.get('n', NUM_RECOMMENDATIONS, type=int)
        
        recommendations = recommender.get_collaborative_recommendations(
            user_id=user_id,
            num_recommendations=n_recommendations
        )
        
        return jsonify({
            'user_id': user_id,
            'method': 'collaborative_filtering',
            'recommendations': [
                {'song_id': song_id, 'score': float(score)}
                for song_id, score in recommendations
            ]
        }), 200
    
    except Exception as e:
        logger.error(f"Error in collaborative recommendations: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/recommendations/content-based/<int:user_id>', methods=['GET'])
def get_content_based_recommendations(user_id):
    """Get recommendations using only content-based filtering"""
    try:
        if not validate_user_id(user_id):
            return jsonify({'error': 'Invalid user ID'}), 400
        
        n_recommendations = request.args.get('n', NUM_RECOMMENDATIONS, type=int)
        
        recommendations = recommender.get_content_based_recommendations(
            user_id=user_id,
            num_recommendations=n_recommendations
        )
        
        return jsonify({
            'user_id': user_id,
            'method': 'content_based_filtering',
            'recommendations': [
                {'song_id': song_id, 'score': float(score)}
                for song_id, score in recommendations
            ]
        }), 200
    
    except Exception as e:
        logger.error(f"Error in content-based recommendations: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/feedback', methods=['POST'])
def record_feedback():
    """
    Record user feedback on a song
    
    Request body:
    {
        "user_id": int,
        "song_id": int,
        "rating": float (1-5),
        "timestamp": str (optional, ISO format)
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400
        
        user_id = data.get('user_id')
        song_id = data.get('song_id')
        rating = data.get('rating')
        timestamp = data.get('timestamp')
        
        # Validate inputs
        if not validate_user_id(user_id):
            return jsonify({'error': 'Invalid user ID'}), 400
        
        if not validate_song_id(song_id):
            return jsonify({'error': 'Invalid song ID'}), 400
        
        if not validate_rating(rating):
            return jsonify({'error': 'Rating must be between 1 and 5'}), 400
        
        # Record feedback
        success = feedback_manager.record_feedback(user_id, song_id, rating, timestamp)
        
        if success:
            return jsonify({
                'status': 'success',
                'message': 'Feedback recorded',
                'user_id': user_id,
                'song_id': song_id,
                'rating': rating
            }), 201
        else:
            return jsonify({'error': 'Failed to record feedback'}), 500
    
    except Exception as e:
        logger.error(f"Error recording feedback: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/similar-users/<int:user_id>', methods=['GET'])
def get_similar_users(user_id):
    """Get users similar to the given user"""
    try:
        if not validate_user_id(user_id):
            return jsonify({'error': 'Invalid user ID'}), 400
        
        n_users = request.args.get('n', 5, type=int)
        similar_users = recommender.get_similar_users(user_id, n_users)
        
        return jsonify({
            'user_id': user_id,
            'similar_users': [
                {'user_id': uid, 'similarity': float(sim)}
                for uid, sim in similar_users
            ]
        }), 200
    
    except Exception as e:
        logger.error(f"Error getting similar users: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/similar-songs/<int:song_id>', methods=['GET'])
def get_similar_songs(song_id):
    """Get songs similar to the given song"""
    try:
        if not validate_song_id(song_id):
            return jsonify({'error': 'Invalid song ID'}), 400
        
        n_songs = request.args.get('n', 5, type=int)
        similar_songs = recommender.get_similar_songs(song_id, n_songs)
        
        return jsonify({
            'song_id': song_id,
            'similar_songs': [
                {'song_id': sid, 'similarity': float(sim)}
                for sid, sim in similar_songs
            ]
        }), 200
    
    except Exception as e:
        logger.error(f"Error getting similar songs: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Get system statistics"""
    try:
        total_interactions = 0
        if recommender.user_item_matrix is not None:
            total_interactions = int(recommender.user_item_matrix.values.astype(bool).sum().sum())
        
        stats = {
            'total_songs': int(len(recommender.song_features)) if recommender.song_features is not None else 0,
            'total_users': int(len(recommender.user_item_matrix)) if recommender.user_item_matrix is not None else 0,
            'total_interactions': total_interactions,
            'collaborative_weight': float(COLLABORATIVE_WEIGHT),
            'content_weight': float(CONTENT_WEIGHT)
        }
        return jsonify(stats), 200
    
    except Exception as e:
        logger.error(f"Error getting stats: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    # Initialize models on startup
    if initialize_models():
        app.run(host=API_HOST, port=API_PORT, debug=DEBUG)
    else:
        logger.error("Failed to initialize models. Exiting.")
        sys.exit(1)
