"""
Test models module
"""

import unittest
import pandas as pd
import numpy as np
from pathlib import Path
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from models.collaborative_filtering import CollaborativeFiltering
from models.content_based_filtering import ContentBasedFiltering
from models.hybrid_recommender import HybridRecommender

class TestCollaborativeFiltering(unittest.TestCase):
    """Test collaborative filtering model"""
    
    def setUp(self):
        """Create sample data"""
        # Create user-item matrix
        self.user_item_matrix = pd.DataFrame({
            1: [5, 0, 3, 0, 4],
            2: [4, 0, 3, 0, 5],
            3: [0, 5, 0, 4, 0],
            4: [0, 4, 0, 5, 0],
            5: [3, 0, 4, 0, 2],
        }, index=[1, 2, 3, 4, 5])
        
        self.model = CollaborativeFiltering()
        self.model.fit(self.user_item_matrix)
    
    def test_model_initialization(self):
        """Test model initialization"""
        self.assertIsNotNone(self.model.user_similarities)
        self.assertIsNotNone(self.model.item_similarities)
    
    def test_user_based_recommendations(self):
        """Test user-based recommendations"""
        recommendations = self.model.get_user_based_recommendations(1, num_recommendations=3)
        self.assertIsInstance(recommendations, list)
        self.assertLessEqual(len(recommendations), 3)

class TestContentBasedFiltering(unittest.TestCase):
    """Test content-based filtering model"""
    
    def setUp(self):
        """Create sample data"""
        self.song_features = pd.DataFrame({
            'song_id': [1, 2, 3, 4, 5],
            'tempo': [120, 130, 125, 115, 140],
            'energy': [0.7, 0.8, 0.75, 0.6, 0.85],
            'danceability': [0.8, 0.85, 0.8, 0.7, 0.9],
        })
        
        self.model = ContentBasedFiltering()
        self.model.fit(self.song_features)
    
    def test_model_initialization(self):
        """Test model initialization"""
        self.assertIsNotNone(self.model.song_feature_similarity)
    
    def test_recommendations(self):
        """Test content-based recommendations"""
        recommendations = self.model.get_recommendations(1, num_recommendations=3)
        self.assertIsInstance(recommendations, list)
        self.assertLessEqual(len(recommendations), 3)

if __name__ == '__main__':
    unittest.main()
