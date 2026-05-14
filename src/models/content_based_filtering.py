"""
Content-Based Filtering Recommendation Model
"""

import numpy as np
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from typing import List, Tuple, Dict

class ContentBasedFiltering:
    """Content-based recommendation system using audio features"""
    
    def __init__(self, similarity_threshold: float = 0.3):
        self.similarity_threshold = similarity_threshold
        self.song_features = None
        self.song_feature_similarity = None
    
    def fit(self, song_features: pd.DataFrame):
        """
        Train content-based model with song audio features
        
        Args:
            song_features: DataFrame with song features and feature columns
        """
        # Extract only numeric feature columns (exclude song_id and text columns)
        numeric_cols = song_features.select_dtypes(include=[np.number]).columns.tolist()
        
        # Remove song_id if it's in numeric columns
        if 'song_id' in numeric_cols:
            numeric_cols.remove('song_id')
        
        self.song_features = song_features
        
        # Compute similarity between songs based on audio features
        features_matrix = song_features[numeric_cols].fillna(0).values
        self.song_feature_similarity = cosine_similarity(features_matrix)
        self.song_feature_similarity = pd.DataFrame(
            self.song_feature_similarity,
            index=song_features['song_id'].values,
            columns=song_features['song_id'].values
        )
    
    def get_recommendations(self, song_id: int,
                           num_recommendations: int = 10) -> List[Tuple[int, float]]:
        """
        Recommend songs similar to a given song
        
        Args:
            song_id: Reference song ID
            num_recommendations: Number of recommendations
        
        Returns:
            List of (song_id, similarity_score) tuples
        """
        if song_id not in self.song_feature_similarity.index:
            return []
        
        # Get similarity scores for this song
        similarities = self.song_feature_similarity[song_id]
        
        # Filter by threshold and exclude the song itself
        recommendations = similarities[
            (similarities > self.similarity_threshold) &
            (similarities.index != song_id)
        ].sort_values(ascending=False)
        
        return list(zip(recommendations.index, recommendations.values))[:num_recommendations]
    
    def get_user_recommendations(self, user_id: int,
                               user_item_matrix: pd.DataFrame,
                               num_recommendations: int = 10) -> List[Tuple[int, float]]:
        """
        Recommend songs based on user's liked songs
        
        Args:
            user_id: Target user ID
            user_item_matrix: User-item rating matrix
            num_recommendations: Number of recommendations
        
        Returns:
            List of (song_id, score) tuples
        """
        if user_id not in user_item_matrix.index:
            return []
        
        # Get songs user has rated highly
        user_ratings = user_item_matrix.loc[user_id]
        high_rated_songs = user_ratings[user_ratings > 3].index
        
        if len(high_rated_songs) == 0:
            return []
        
        # Accumulate recommendations from similar songs
        recommendations = {}
        for song_id in high_rated_songs:
            similar_songs = self.get_recommendations(song_id, num_recommendations=50)
            rating = user_ratings[song_id]
            
            for rec_song_id, similarity in similar_songs:
                if user_ratings.get(rec_song_id, 0) == 0:  # Not rated yet
                    score = similarity * rating
                    
                    if rec_song_id in recommendations:
                        recommendations[rec_song_id] += score
                    else:
                        recommendations[rec_song_id] = score
        
        # Sort and return top recommendations
        sorted_recs = sorted(recommendations.items(), key=lambda x: x[1], reverse=True)
        return sorted_recs[:num_recommendations]
