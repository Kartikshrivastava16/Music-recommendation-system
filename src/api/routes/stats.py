"""Statistics, health check, and admin endpoints for the Music Recommendation System API"""

from flask import Blueprint, jsonify, request
import logging
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from config import COLLABORATIVE_WEIGHT, CONTENT_WEIGHT, DIVERSITY_LAMBDA, SERENDIPITY_BOOST, RETRAIN_THRESHOLD

# Create blueprint
stats_bp = Blueprint('stats', __name__, url_prefix='/api')

# Logger
logger = logging.getLogger(__name__)

# Global references - will be set by app.py
recommender = None
feedback_manager = None

@stats_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'Music Recommendation System API'
    }), 200

@stats_bp.route('/stats', methods=['GET'])
def get_stats():
    """
    Get system statistics including diversity/serendipity settings
    and auto-retrain status.
    """
    try:
        total_interactions = 0
        if recommender.user_item_matrix is not None:
            total_interactions = int(recommender.user_item_matrix.values.astype(bool).sum().sum())
        
        retrain_info = {}
        if feedback_manager is not None:
            retrain_info = {
                'retrain_threshold': feedback_manager.retrain_threshold,
                'new_feedback_since_last_retrain': feedback_manager.new_feedback_count,
                'auto_retrain_enabled': feedback_manager.retrain_callback is not None
            }
        
        stats = {
            'total_songs': int(len(recommender.song_features)) if recommender.song_features is not None else 0,
            'total_users': int(len(recommender.user_item_matrix)) if recommender.user_item_matrix is not None else 0,
            'total_interactions': total_interactions,
            'model_weights': {
                'collaborative': float(recommender.collaborative_weight),
                'content_based': float(recommender.content_weight)
            },
            'diversity_settings': {
                'diversity_lambda': float(recommender.diversity_lambda),
                'serendipity_boost': float(recommender.serendipity_boost)
            },
            'auto_retrain': retrain_info
        }
        return jsonify(stats), 200
    
    except Exception as e:
        logger.error(f"Error getting stats: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@stats_bp.route('/retrain', methods=['POST'])
def manual_retrain():
    """
    Manually trigger a model retrain.
    
    Useful after bulk data imports or to reset the auto-retrain counter.
    """
    try:
        if feedback_manager is None or feedback_manager.retrain_callback is None:
            return jsonify({'error': 'No retrain callback configured'}), 503
        
        feedback_manager.retrain_callback()
        feedback_manager.reset_feedback_count()
        
        return jsonify({
            'status': 'success',
            'message': 'Model retrained successfully',
            'new_feedback_count_reset_to': 0
        }), 200
    
    except Exception as e:
        logger.error(f"Error during manual retrain: {str(e)}")
        return jsonify({'error': 'Retrain failed', 'detail': str(e)}), 500

@stats_bp.route('/settings', methods=['PATCH'])
def update_settings():
    """
    Update recommender settings at runtime without restarting the server.
    
    Accepts JSON body with any subset of:
      diversity_lambda   (float 0-1)
      serendipity_boost  (float 0-1)
      retrain_threshold  (int > 0)
    """
    try:
        data = request.get_json() or {}
        updated = {}
        
        if 'diversity_lambda' in data:
            val = float(data['diversity_lambda'])
            recommender.diversity_lambda = max(0.0, min(1.0, val))
            updated['diversity_lambda'] = recommender.diversity_lambda
        
        if 'serendipity_boost' in data:
            val = float(data['serendipity_boost'])
            recommender.serendipity_boost = max(0.0, min(1.0, val))
            updated['serendipity_boost'] = recommender.serendipity_boost
        
        if 'retrain_threshold' in data and feedback_manager is not None:
            val = int(data['retrain_threshold'])
            if val > 0:
                feedback_manager.retrain_threshold = val
                updated['retrain_threshold'] = feedback_manager.retrain_threshold
        
        if not updated:
            return jsonify({'error': 'No valid settings provided'}), 400
        
        return jsonify({'status': 'updated', 'settings': updated}), 200
    
    except Exception as e:
        logger.error(f"Error updating settings: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500
