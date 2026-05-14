"""Statistics and health check endpoints for the Music Recommendation System API"""

from flask import Blueprint, jsonify
import logging
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from config import COLLABORATIVE_WEIGHT, CONTENT_WEIGHT

# Create blueprint
stats_bp = Blueprint('stats', __name__, url_prefix='/api')

# Logger
logger = logging.getLogger(__name__)

# Global reference - will be set by app.py
recommender = None

@stats_bp.route('/health', methods=['GET'])
def health_check():
    """
    Health check endpoint
    
    Returns:
        JSON status response
    """
    return jsonify({
        'status': 'healthy',
        'service': 'Music Recommendation System API'
    }), 200

@stats_bp.route('/stats', methods=['GET'])
def get_stats():
    """
    Get system statistics
    
    Returns:
        JSON with system statistics including total songs, users, interactions, and weights
    """
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
