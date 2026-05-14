"""
Flask API Application for Music Recommendations
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
import sys
from pathlib import Path
from config import API_HOST, API_PORT, DEBUG, NUM_RECOMMENDATIONS
from utils.logger import get_logger
from utils.validators import validate_user_id, validate_song_id, validate_num_recommendations

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from data import DataLoader
from data.processor import DataProcessor
from models.hybrid_recommender import HybridRecommender

# Initialize Flask app
app = Flask(__name__)
CORS(app)
logger = get_logger(__name__)

# Global models (loaded once)
recommender = None
user_item_matrix = None
data_loader = None

def initialize_models():
    """Initialize recommendation models"""
    global recommender, user_item_matrix, data_loader
    
    try:
        # Load data
        data_loader = DataLoader(data_dir="data")
        songs, users, history = data_loader.load_all()
        
        # Process data
        processor = DataProcessor()
        user_item_matrix = processor.create_user_item_matrix(history)
        
        # Prepare features
        song_features = songs.copy()
        feature_cols = [col for col in songs.columns if col not in ['song_id', 'title', 'artist']]
        
        if len(feature_cols) == 0:
            import numpy as np
            for feat in ['tempo', 'energy', 'danceability', 'valence']:
                song_features[feat] = np.random.rand(len(songs))
        
        # Train models
        recommender = HybridRecommender()
        recommender.fit(user_item_matrix, song_features)
        
        logger.info("Models initialized successfully")
        return True
        
    except Exception as e:
        logger.error(f"Error initializing models: {e}")
        return False

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'Music Recommendation System'
    }), 200

@app.route('/api/recommendations/<int:user_id>', methods=['GET'])
def get_recommendations(user_id):
    """Get personalized recommendations for a user"""
    try:
        # Validate input
        if not validate_user_id(user_id):
            return jsonify({'error': 'Invalid user ID'}), 400
        
        # Get number of recommendations
        num_recs = request.args.get('num', NUM_RECOMMENDATIONS, type=int)
        if not validate_num_recommendations(num_recs):
            return jsonify({'error': 'Invalid number of recommendations'}), 400
        
        if recommender is None:
            return jsonify({'error': 'Models not initialized'}), 500
        
        # Get recommendations
        recommendations = recommender.get_recommendations(
            user_id,
            user_item_matrix,
            num_recommendations=num_recs
        )
        
        result = {
            'user_id': user_id,
            'recommendations': [
                {'song_id': song_id, 'score': float(score)}
                for song_id, score in recommendations
            ]
        }
        
        return jsonify(result), 200
        
    except Exception as e:
        logger.error(f"Error getting recommendations: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/feedback', methods=['POST'])
def submit_feedback():
    """Submit user feedback on recommendations"""
    try:
        data = request.get_json()
        
        if not data or 'user_id' not in data or 'song_id' not in data:
            return jsonify({'error': 'Missing required fields'}), 400
        
        user_id = data['user_id']
        song_id = data['song_id']
        rating = data.get('rating', 3)
        
        # Validate
        if not validate_user_id(user_id) or not validate_song_id(song_id):
            return jsonify({'error': 'Invalid IDs'}), 400
        
        # Store feedback (in production, save to database)
        logger.info(f"Feedback received - User: {user_id}, Song: {song_id}, Rating: {rating}")
        
        return jsonify({
            'status': 'success',
            'message': 'Feedback recorded'
        }), 200
        
    except Exception as e:
        logger.error(f"Error submitting feedback: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/songs/<int:song_id>', methods=['GET'])
def get_song_info(song_id):
    """Get information about a specific song"""
    try:
        if not validate_song_id(song_id):
            return jsonify({'error': 'Invalid song ID'}), 400
        
        if data_loader is None:
            return jsonify({'error': 'Data not loaded'}), 500
        
        song = data_loader.get_song_info(song_id)
        
        if song is None:
            return jsonify({'error': 'Song not found'}), 404
        
        return jsonify(song.to_dict()), 200
        
    except Exception as e:
        logger.error(f"Error getting song info: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/users/<int:user_id>/history', methods=['GET'])
def get_user_history(user_id):
    """Get user's listening history"""
    try:
        if not validate_user_id(user_id):
            return jsonify({'error': 'Invalid user ID'}), 400
        
        if data_loader is None:
            return jsonify({'error': 'Data not loaded'}), 500
        
        history = data_loader.get_user_ratings(user_id)
        
        return jsonify({
            'user_id': user_id,
            'listening_history': history.to_dict('records')
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting user history: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/train', methods=['POST'])
def train_models():
    """Retrain the recommendation models"""
    try:
        if initialize_models():
            return jsonify({
                'status': 'success',
                'message': 'Models retrained successfully'
            }), 200
        else:
            return jsonify({
                'status': 'error',
                'message': 'Failed to retrain models'
            }), 500
            
    except Exception as e:
        logger.error(f"Error training models: {e}")
        return jsonify({'error': str(e)}), 500

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    logger.info("Initializing Music Recommendation API...")
    
    if not initialize_models():
        logger.error("Failed to initialize models. Check data files in 'data/' directory.")
        sys.exit(1)
    
    logger.info(f"Starting API server on {API_HOST}:{API_PORT}")
    app.run(host=API_HOST, port=API_PORT, debug=DEBUG)
