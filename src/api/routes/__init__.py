"""API route blueprints for Music Recommendation System"""

from flask import Blueprint

def create_blueprints():
    """Create and return all API blueprints"""
    from .recommendations import recommendations_bp
    from .feedback import feedback_bp
    from .similar import similar_bp
    from .stats import stats_bp
    
    return [recommendations_bp, feedback_bp, similar_bp, stats_bp]
