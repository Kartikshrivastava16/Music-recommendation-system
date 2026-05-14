"""
Collaborative Filtering Recommendation Model using User-Based approach
"""

import numpy as np
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from typing import List, Tuple, Dict, Optional

class CollaborativeFiltering:
    """Collaborative filtering using user-user similarity"""
    
    def __init__(self, similarity_threshold: float = 0.1, n_neighbors: int = 10):
        """
        Initialize collaborative filtering model
        
        Args:
            similarity_threshold: Minimum similarity score to consider
            n_neighbors: Number of similar users to consider
        """
        self.similarity_threshold = similarity_threshold
        self.n_neighbors = n_neighbors
        self.user_item_matrix = None
        self.user_similarity = None
        self.user_ids = None
    
    def fit(self, user_item_matrix: pd.DataFrame):
        """
        Train collaborative filtering model
        
        Args:
            user_item_matrix: User-item rating matrix (users x items)
        """
        self.user_item_matrix = user_item_matrix
        self.user_ids = user_item_matrix.index.values
        
        # Compute user-user similarity using cosine similarity
        # Handle missing values by using 0 for unrated items
        matrix_filled = user_item_matrix.fillna(0).values
        self.user_similarity = cosine_similarity(matrix_filled)
        self.user_similarity = pd.DataFrame(
            self.user_similarity,
            index=self.user_ids,
            columns=self.user_ids
        )
    
    def get_similar_users(self, user_id: int, n_neighbors: Optional[int] = None) -> List[Tuple[int, float]]:
        """
        Find users similar to the given user
        
        Args:
            user_id: Target user ID
            n_neighbors: Number of similar users to return
        
        Returns:
            List of (user_id, similarity_score) tuples
        """
        if n_neighbors is None:
            n_neighbors = self.n_neighbors
        
        if user_id not in self.user_similarity.index:
            return []
        
        # Get similarity scores for this user
        similarities = self.user_similarity[user_id].sort_values(ascending=False)
        
        # Filter by threshold and exclude the user themselves
        similar_users = [
            (uid, score) for uid, score in similarities.items()
            if uid != user_id and score >= self.similarity_threshold
        ]
        
        return similar_users[:n_neighbors]
    
    def get_recommendations(self, user_id: int, 
                           num_recommendations: int = 10,
                           exclude_rated: bool = True) -> List[Tuple[int, float]]:
        """
        Get recommendations for a user based on similar users' preferences
        
        Args:
            user_id: Target user ID
            num_recommendations: Number of recommendations to return
            exclude_rated: Whether to exclude items the user has already rated
        
        Returns:
            List of (item_id, predicted_score) tuples
        """
        if user_id not in self.user_similarity.index:
            return []
        
        # Find similar users
        similar_users = self.get_similar_users(user_id)
        if not similar_users:
            return []
        
        # Get weighted average of similar users' ratings
        recommendations = {}
        user_row = self.user_item_matrix.loc[user_id]
        
        for similar_user_id, similarity_score in similar_users:
            similar_user_row = self.user_item_matrix.loc[similar_user_id]
            
            # For each item the similar user rated
            for item_id, rating in similar_user_row.items():
                if rating > 0:  # Only consider rated items
                    # Skip if user already rated this item
                    if exclude_rated and user_row[item_id] > 0:
                        continue
                    
                    # Add weighted rating
                    if item_id not in recommendations:
                        recommendations[item_id] = {'score': 0, 'weight': 0}
                    
                    recommendations[item_id]['score'] += rating * similarity_score
                    recommendations[item_id]['weight'] += similarity_score
        
        # Calculate weighted average scores
        final_recommendations = []
        for item_id, values in recommendations.items():
            if values['weight'] > 0:
                avg_score = values['score'] / values['weight']
                final_recommendations.append((item_id, avg_score))
        
        # Sort by score and return top N
        final_recommendations.sort(key=lambda x: x[1], reverse=True)
        return final_recommendations[:num_recommendations]
