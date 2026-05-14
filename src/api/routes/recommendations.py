"""Recommendation endpoints for the Music Recommendation System API"""

from flask import Blueprint, request, jsonify
import logging
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from config import NUM_RECOMMENDATIONS
from utils.validators import validate_user_id

# Create blueprint
recommendations_bp = Blueprint('recommendations', __name__, url_prefix='/api/recommendations')

# Logger
logger = logging.getLogger(__name__)

# Global reference - will be set by app.py
recommender = None

@recommendations_bp.route('/<int:user_id>', methods=['GET'])
def get_recommendations(user_id):
    """
    Get hybrid recommendations for a user
    
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

@recommendations_bp.route('/collaborative/<int:user_id>', methods=['GET'])
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

@recommendations_bp.route('/content-based/<int:user_id>', methods=['GET'])
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
