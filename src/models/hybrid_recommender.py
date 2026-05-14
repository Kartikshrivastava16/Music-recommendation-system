"""
Hybrid Recommender combining Collaborative and Content-Based Filtering
"""

import pandas as pd
import numpy as np
from typing import List, Tuple, Dict
from models.collaborative_filtering import CollaborativeFiltering
from models.content_based_filtering import ContentBasedFiltering

class HybridRecommender:
    """Hybrid recommendation system combining multiple approaches"""
    
    def __init__(self, collaborative_weight: float = 0.6, 
                 content_weight: float = 0.4):
        """
        Initialize hybrid recommender
        
        Args:
            collaborative_weight: Weight for collaborative filtering (0-1)
            content_weight: Weight for content-based filtering (0-1)
        """
        self.collaborative_weight = collaborative_weight
        self.content_weight = content_weight
        
        self.collaborative_model = None
        self.content_model = None
    
    def fit(self, user_item_matrix: pd.DataFrame, song_features: pd.DataFrame):
        """
        Train both recommendation models
        
        Args:
            user_item_matrix: User-item rating matrix
            song_features: Song feature DataFrame
        """
        # Train collaborative filtering
        self.collaborative_model = CollaborativeFiltering()
        self.collaborative_model.fit(user_item_matrix)
        
        # Train content-based filtering
        self.content_model = ContentBasedFiltering()
        self.content_model.fit(song_features)
    
    def get_recommendations(self, user_id: int,
                           user_item_matrix: pd.DataFrame,
                           num_recommendations: int = 10) -> List[Tuple[int, float]]:
        """
        Get hybrid recommendations for a user
        
        Args:
            user_id: Target user ID
            user_item_matrix: User-item rating matrix
            num_recommendations: Number of recommendations
        
        Returns:
            List of (song_id, score) tuples
        """
        recommendations = {}
        
        # Collaborative filtering recommendations
        collab_recs = self.collaborative_model.get_user_based_recommendations(
            user_id, num_recommendations * 2
        )
        
        for song_id, score in collab_recs:
            weighted_score = score * self.collaborative_weight
            recommendations[song_id] = recommendations.get(song_id, 0) + weighted_score
        
        # Content-based recommendations
        content_recs = self.content_model.get_user_recommendations(
            user_id, user_item_matrix, num_recommendations * 2
        )
        
        for song_id, score in content_recs:
            # Normalize content-based scores
            normalized_score = score / 5.0 if score > 0 else 0
            weighted_score = normalized_score * self.content_weight
            recommendations[song_id] = recommendations.get(song_id, 0) + weighted_score
        
        # Sort and return top recommendations
        sorted_recs = sorted(recommendations.items(), key=lambda x: x[1], reverse=True)
        return sorted_recs[:num_recommendations]
    
    def get_explanations(self, user_id: int, song_id: int) -> Dict[str, any]:
        """
        Get explanation for why a song was recommended
        
        Returns:
            Dictionary with recommendation reasons
        """
        explanation = {
            'song_id': song_id,
            'user_id': user_id,
            'reasons': []
        }
        
        # Check if recommended by collaborative filtering
        if self.collaborative_model:
            explanation['reasons'].append("Similar users liked this song")
        
        # Check if recommended by content-based filtering
        if self.content_model:
            explanation['reasons'].append("Similar to songs you rated highly")
        
        return explanation
