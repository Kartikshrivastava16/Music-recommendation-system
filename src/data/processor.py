"""
Data processor module for data transformation and normalization
"""

import pandas as pd
import numpy as np
from typing import Optional

class DataProcessor:
    """Process and normalize data for recommendation models"""
    
    def __init__(self):
        self.scaler = None
        self.encoded_features = {}
    
    def normalize_ratings(self, ratings: pd.Series, min_val: float = 1, max_val: float = 5) -> pd.Series:
        """Normalize ratings to 0-1 range"""
        return (ratings - min_val) / (max_val - min_val)
    
    def denormalize_ratings(self, normalized_ratings: np.ndarray, 
                            min_val: float = 1, max_val: float = 5) -> np.ndarray:
        """Convert normalized ratings back to original scale"""
        return normalized_ratings * (max_val - min_val) + min_val
    
    def create_user_item_matrix(self, history_df: pd.DataFrame) -> pd.DataFrame:
        """Create user-item matrix from listening history"""
        user_item_matrix = history_df.pivot_table(
            index='user_id',
            columns='song_id',
            values='rating',
            fill_value=0
        )
        return user_item_matrix
    
    def handle_missing_values(self, df: pd.DataFrame, strategy: str = 'mean') -> pd.DataFrame:
        """Handle missing values in dataset"""
        df_copy = df.copy()
        
        if strategy == 'mean':
            df_copy.fillna(df_copy.mean(), inplace=True)
        elif strategy == 'median':
            df_copy.fillna(df_copy.median(), inplace=True)
        elif strategy == 'forward_fill':
            df_copy.fillna(method='ffill', inplace=True)
        
        return df_copy
    
    def encode_categorical(self, df: pd.DataFrame, columns: list) -> pd.DataFrame:
        """Encode categorical variables"""
        df_copy = df.copy()
        
        for col in columns:
            if col in df_copy.columns:
                df_copy[col] = pd.Categorical(df_copy[col]).codes
                self.encoded_features[col] = df_copy[col].unique()
        
        return df_copy
    
    def scale_features(self, df: pd.DataFrame, feature_columns: list) -> pd.DataFrame:
        """Scale numerical features to 0-1 range"""
        df_copy = df.copy()
        
        for col in feature_columns:
            if col in df_copy.columns:
                min_val = df_copy[col].min()
                max_val = df_copy[col].max()
                if max_val != min_val:
                    df_copy[col] = (df_copy[col] - min_val) / (max_val - min_val)
        
        return df_copy
