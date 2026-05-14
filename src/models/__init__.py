"""
Collaborative Filtering Recommendation Model
"""

import numpy as np
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from typing import List, Tuple, Dict

class CollaborativeFiltering:
    """User-based and Item-based Collaborative Filtering"""
    
    def __init__(self, similarity_threshold: float = 0.3):
        self.similarity_threshold = similarity_threshold
        self.user_similarities = None
        self.item_similarities = None
        self.user_item_matrix = None
    
    def fit(self, user_item_matrix: pd.DataFrame):
        """Train the collaborative filtering model"""
        self.user_item_matrix = user_item_matrix
        
        # Compute user similarity (users with similar rating patterns)
        self.user_similarities = cosine_similarity(user_item_matrix)
        self.user_similarities = pd.DataFrame(
            self.user_similarities,
            index=user_item_matrix.index,
            columns=user_item_matrix.index
        )
        
        # Compute item similarity (items rated similarly by users)
        self.item_similarities = cosine_similarity(user_item_matrix.T)
        self.item_similarities = pd.DataFrame(
            self.item_similarities,
            index=user_item_matrix.columns,
            columns=user_item_matrix.columns
        )
    
    def get_user_based_recommendations(self, user_id: int, 
                                      num_recommendations: int = 10) -> List[Tuple[int, float]]:
        """
        Recommend items based on similar users' preferences
        
        Args:
            user_id: Target user ID
            num_recommendations: Number of recommendations to return
        
        Returns:
            List of (song_id, score) tuples
        """
        if user_id not in self.user_similarities.index:
            return []
        
        # Get similar users
        user_similarities = self.user_similarities[user_id]
        similar_users = user_similarities[user_similarities > self.similarity_threshold].index
        similar_users = similar_users[similar_users != user_id]
        
        # Get recommendations from similar users
        recommendations = {}
        for similar_user in similar_users:
            similarity_score = user_similarities[similar_user]
            
            # Songs rated by similar user but not by target user
            similar_user_ratings = self.user_item_matrix.loc[similar_user]
            target_user_ratings = self.user_item_matrix.loc[user_id]
            
            unrated_items = target_user_ratings[target_user_ratings == 0].index
            
            for item in unrated_items:
                if similar_user_ratings[item] > 0:
                    weighted_rating = similar_user_ratings[item] * similarity_score
                    
                    if item in recommendations:
                        recommendations[item] += weighted_rating
                    else:
                        recommendations[item] = weighted_rating
        
        # Sort and return top recommendations
        sorted_recs = sorted(recommendations.items(), key=lambda x: x[1], reverse=True)
        return sorted_recs[:num_recommendations]
    
    def get_item_based_recommendations(self, user_id: int,
                                      num_recommendations: int = 10) -> List[Tuple[int, float]]:
        """
        Recommend items similar to items the user liked
        
        Args:
            user_id: Target user ID
            num_recommendations: Number of recommendations to return
        
        Returns:
            List of (song_id, score) tuples
        """
        if user_id not in self.user_item_matrix.index:
            return []
        
        # Get items user has rated highly
        user_ratings = self.user_item_matrix.loc[user_id]
        high_rated_items = user_ratings[user_ratings > 3].index
        
        if len(high_rated_items) == 0:
            return []
        
        # Get similar items
        recommendations = {}
        for item in high_rated_items:
            item_sims = self.item_similarities[item]
            similar_items = item_sims[item_sims > self.similarity_threshold].index
            
            for similar_item in similar_items:
                if similar_item != item and user_ratings[similar_item] == 0:
                    similarity_score = item_sims[similar_item]
                    user_rating = user_ratings[item]
                    weighted_score = similarity_score * user_rating
                    
                    if similar_item in recommendations:
                        recommendations[similar_item] += weighted_score
                    else:
                        recommendations[similar_item] = weighted_score
        
        # Sort and return top recommendations
        sorted_recs = sorted(recommendations.items(), key=lambda x: x[1], reverse=True)
        return sorted_recs[:num_recommendations]
