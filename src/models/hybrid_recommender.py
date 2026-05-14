"""
Hybrid Recommender combining Collaborative and Content-Based Filtering
"""

import pandas as pd
import numpy as np
from typing import List, Tuple, Dict, Optional
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
        self.user_item_matrix = None
        self.song_features = None
    
    def fit(self, user_item_matrix: pd.DataFrame, song_features: pd.DataFrame):
        """
        Train both recommendation models
        
        Args:
            user_item_matrix: User-item rating matrix
            song_features: Song feature DataFrame
        """
        self.user_item_matrix = user_item_matrix
        self.song_features = song_features
        
        # Train collaborative filtering
        self.collaborative_model = CollaborativeFiltering()
        self.collaborative_model.fit(user_item_matrix)
        
        # Train content-based filtering
        self.content_model = ContentBasedFiltering()
        self.content_model.fit(song_features)
    
    def get_recommendations(self, user_id: int,
                           num_recommendations: int = 10) -> List[Tuple[int, float]]:
        """
        Get hybrid recommendations for a user
        
        Args:
            user_id: Target user ID
            num_recommendations: Number of recommendations
        
        Returns:
            List of (song_id, score) tuples
        """
        recommendations = {}
        
        # Collaborative filtering recommendations
        collab_recs = self.get_collaborative_recommendations(user_id, num_recommendations * 2)
        for song_id, score in collab_recs:
            weighted_score = score * self.collaborative_weight
            recommendations[song_id] = recommendations.get(song_id, 0) + weighted_score
        
        # Content-based recommendations
        content_recs = self.get_content_based_recommendations(user_id, num_recommendations * 2)
        for song_id, score in content_recs:
            weighted_score = score * self.content_weight
            recommendations[song_id] = recommendations.get(song_id, 0) + weighted_score
        
        # Sort and return top recommendations
        sorted_recs = sorted(recommendations.items(), key=lambda x: x[1], reverse=True)
        return sorted_recs[:num_recommendations]
    
    def get_collaborative_recommendations(self, user_id: int,
                                        num_recommendations: int = 10) -> List[Tuple[int, float]]:
        """Get recommendations using collaborative filtering"""
        if self.collaborative_model is None:
            return []
        
        return self.collaborative_model.get_recommendations(user_id, num_recommendations)
    
    def get_content_based_recommendations(self, user_id: int,
                                         num_recommendations: int = 10) -> List[Tuple[int, float]]:
        """Get recommendations using content-based filtering"""
        if self.content_model is None or self.user_item_matrix is None:
            return []
        
        # Get user's rated songs
        if user_id not in self.user_item_matrix.index:
            return []
        
        user_ratings = self.user_item_matrix.loc[user_id]
        rated_songs = user_ratings[user_ratings > 0].index.tolist()
        
        if not rated_songs:
            return []
        
        # Get songs similar to highly rated songs
        recommendations = {}
        
        for song_id in rated_songs:
            rating = user_ratings[song_id]
            similar_songs = self.content_model.get_recommendations(song_id, num_recommendations * 2)
            
            for similar_song_id, similarity in similar_songs:
                # Don't recommend songs the user has already rated
                if similar_song_id not in rated_songs:
                    weighted_score = similarity * rating
                    recommendations[similar_song_id] = max(
                        recommendations.get(similar_song_id, 0),
                        weighted_score
                    )
        
        sorted_recs = sorted(recommendations.items(), key=lambda x: x[1], reverse=True)
        return sorted_recs[:num_recommendations]
    
    def get_similar_users(self, user_id: int, n_users: int = 5) -> List[Tuple[int, float]]:
        """Get users similar to the given user"""
        if self.collaborative_model is None:
            return []
        
        return self.collaborative_model.get_similar_users(user_id, n_users)
    
    def get_similar_songs(self, song_id: int, n_songs: int = 5) -> List[Tuple[int, float]]:
        """Get songs similar to the given song"""
        if self.content_model is None:
            return []
        
        return self.content_model.get_recommendations(song_id, n_songs)
    
    def get_explanations(self, user_id: int, song_id: int) -> Dict:
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
            collab_recs = self.collaborative_model.get_recommendations(user_id, 50)
            if any(s == song_id for s, _ in collab_recs):
                explanation['reasons'].append("Similar users liked this song")
        
        # Check if recommended by content-based filtering
        if self.content_model:
            content_recs = self.get_content_based_recommendations(user_id, 50)
            if any(s == song_id for s, _ in content_recs):
                explanation['reasons'].append("Similar to songs you rated highly")
        
        return explanation
