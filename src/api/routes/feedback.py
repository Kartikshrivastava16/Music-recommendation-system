"""Feedback endpoints for the Music Recommendation System API"""

from flask import Blueprint, request, jsonify
import logging
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from utils.validators import validate_user_id, validate_song_id, validate_rating

# Create blueprint
feedback_bp = Blueprint('feedback', __name__, url_prefix='/api')

# Logger
logger = logging.getLogger(__name__)

# Global reference - will be set by app.py
feedback_manager = None

@feedback_bp.route('/feedback', methods=['POST'])
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
    
    Returns:
        JSON confirmation with status
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
