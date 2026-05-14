"""Similar items endpoints for the Music Recommendation System API"""

from flask import Blueprint, request, jsonify
import logging
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from utils.validators import validate_user_id, validate_song_id

# Create blueprint
similar_bp = Blueprint('similar', __name__, url_prefix='/api')

# Logger
logger = logging.getLogger(__name__)

# Global reference - will be set by app.py
recommender = None

@similar_bp.route('/similar-users/<int:user_id>', methods=['GET'])
def get_similar_users(user_id):
    """
    Get users similar to the given user
    
    Query parameters:
    - n: number of similar users to return (default: 5)
    
    Returns:
        JSON array of similar users with similarity scores
    """
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

@similar_bp.route('/similar-songs/<int:song_id>', methods=['GET'])
def get_similar_songs(song_id):
    """
    Get songs similar to the given song
    
    Query parameters:
    - n: number of similar songs to return (default: 5)
    
    Returns:
        JSON array of similar songs with similarity scores
    """
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
