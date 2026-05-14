"""
Feature engineering module for creating derived features
"""

import pandas as pd
import numpy as np
from typing import List, Dict

class FeatureEngineer:
    """Create derived features for improved recommendations"""
    
    def __init__(self):
        self.feature_importance = {}
    
    def engineer_user_features(self, user_df: pd.DataFrame, 
                               history_df: pd.DataFrame) -> pd.DataFrame:
        """Engineer user-based features"""
        user_features = user_df.copy()
        
        # Calculate user listening frequency
        listening_counts = history_df.groupby('user_id').size().rename('listening_frequency')
        user_features = user_features.join(listening_counts, on='user_id')
        
        # Calculate average rating
        avg_ratings = history_df.groupby('user_id')['rating'].mean().rename('avg_rating')
        user_features = user_features.join(avg_ratings, on='user_id')
        
        # Calculate rating variance (preference consistency)
        rating_variance = history_df.groupby('user_id')['rating'].var().rename('rating_variance')
        user_features = user_features.join(rating_variance, on='user_id')
        
        # Fill NaN values
        user_features.fillna(0, inplace=True)
        
        return user_features
    
    def engineer_song_features(self, song_df: pd.DataFrame,
                               history_df: pd.DataFrame) -> pd.DataFrame:
        """Engineer song-based features"""
        song_features = song_df.copy()
        
        # Calculate popularity (number of ratings)
        popularity = history_df.groupby('song_id').size().rename('popularity')
        song_features = song_features.join(popularity, on='song_id')
        
        # Calculate average rating
        avg_ratings = history_df.groupby('song_id')['rating'].mean().rename('avg_rating')
        song_features = song_features.join(avg_ratings, on='song_id')
        
        # Calculate rating deviation
        rating_std = history_df.groupby('song_id')['rating'].std().rename('rating_std')
        song_features = song_features.join(rating_std, on='song_id')
        
        # Fill NaN values
        song_features.fillna(0, inplace=True)
        
        return song_features
    
    def create_temporal_features(self, history_df: pd.DataFrame) -> pd.DataFrame:
        """Create time-based features from listening history"""
        temp_df = history_df.copy()
        
        # Assuming there's a timestamp column
        if 'timestamp' in temp_df.columns:
            temp_df['timestamp'] = pd.to_datetime(temp_df['timestamp'])
            temp_df['hour'] = temp_df['timestamp'].dt.hour
            temp_df['day_of_week'] = temp_df['timestamp'].dt.dayofweek
            temp_df['month'] = temp_df['timestamp'].dt.month
        
        return temp_df
    
    def create_interaction_features(self, user_features: pd.DataFrame,
                                   song_features: pd.DataFrame,
                                   history_df: pd.DataFrame) -> pd.DataFrame:
        """Create features based on user-song interactions"""
        interactions = history_df.copy()
        
        # User features
        user_cols = [col for col in user_features.columns if col != 'user_id']
        interactions = interactions.merge(
            user_features.add_prefix('user_'),
            left_on='user_id',
            right_on='user_user_id',
            how='left'
        )
        
        # Song features
        song_cols = [col for col in song_features.columns if col != 'song_id']
        interactions = interactions.merge(
            song_features.add_prefix('song_'),
            left_on='song_id',
            right_on='song_song_id',
            how='left'
        )
        
        # Create interaction features
        if 'user_avg_rating' in interactions.columns and 'song_avg_rating' in interactions.columns:
            interactions['rating_diff'] = (
                interactions['user_avg_rating'] - interactions['song_avg_rating']
            )
        
        return interactions.fillna(0)
