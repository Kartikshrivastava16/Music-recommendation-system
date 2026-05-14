"""
Test models module
"""

import unittest
import pandas as pd
import numpy as np
from pathlib import Path
import sys
import tempfile
import os

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from models.collaborative_filtering import CollaborativeFiltering
from models.content_based_filtering import ContentBasedFiltering
from models.hybrid_recommender import HybridRecommender
from models.feedback_manager import FeedbackManager
from data.processor import DataProcessor
from utils.validators import (
    validate_user_id, validate_song_id, validate_rating,
    validate_email, validate_number
)

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
        self.assertIsNotNone(self.model.user_similarity)
        self.assertEqual(self.model.n_neighbors, 10)
    
    def test_get_similar_users(self):
        """Test finding similar users"""
        similar_users = self.model.get_similar_users(1, n_neighbors=2)
        self.assertIsInstance(similar_users, list)
        self.assertLessEqual(len(similar_users), 2)
    
    def test_get_recommendations(self):
        """Test user-based recommendations"""
        recommendations = self.model.get_recommendations(1, num_recommendations=3)
        self.assertIsInstance(recommendations, list)
        self.assertLessEqual(len(recommendations), 3)
        
        # Check format
        if len(recommendations) > 0:
            song_id, score = recommendations[0]
            self.assertIsInstance(song_id, (int, np.integer))
            self.assertIsInstance(score, (int, float))
    
    def test_recommendations_exclude_rated(self):
        """Test excluding rated items from recommendations"""
        recommendations = self.model.get_recommendations(1, num_recommendations=5, exclude_rated=True)
        rated_songs = [1, 3, 5]  # Songs rated by user 1
        
        for song_id, _ in recommendations:
            self.assertNotIn(song_id, rated_songs)


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
        self.assertEqual(len(self.model.song_features), 5)
    
    def test_get_recommendations(self):
        """Test content-based recommendations"""
        recommendations = self.model.get_recommendations(1, num_recommendations=3)
        self.assertIsInstance(recommendations, list)
        self.assertLessEqual(len(recommendations), 3)
        
        # Recommendations should not include the song itself
        for song_id, _ in recommendations:
            self.assertNotEqual(song_id, 1)
    
    def test_recommendation_scores(self):
        """Test that scores are between 0 and 1"""
        recommendations = self.model.get_recommendations(1, num_recommendations=5)
        
        for _, score in recommendations:
            self.assertGreaterEqual(score, 0)
            self.assertLessEqual(score, 1)


class TestHybridRecommender(unittest.TestCase):
    """Test hybrid recommendation system"""
    
    def setUp(self):
        """Create sample data"""
        self.user_item_matrix = pd.DataFrame({
            1: [5, 0, 3, 0, 4],
            2: [4, 0, 3, 0, 5],
            3: [0, 5, 0, 4, 0],
            4: [0, 4, 0, 5, 0],
            5: [3, 0, 4, 0, 2],
        }, index=[1, 2, 3, 4, 5])
        
        self.song_features = pd.DataFrame({
            'song_id': [1, 2, 3, 4, 5],
            'tempo': [120, 130, 125, 115, 140],
            'energy': [0.7, 0.8, 0.75, 0.6, 0.85],
            'danceability': [0.8, 0.85, 0.8, 0.7, 0.9],
        })
        
        self.recommender = HybridRecommender(collaborative_weight=0.6, content_weight=0.4)
        self.recommender.fit(self.user_item_matrix, self.song_features)
    
    def test_initialization(self):
        """Test hybrid recommender initialization"""
        self.assertEqual(self.recommender.collaborative_weight, 0.6)
        self.assertEqual(self.recommender.content_weight, 0.4)
    
    def test_get_recommendations(self):
        """Test hybrid recommendations"""
        recommendations = self.recommender.get_recommendations(1, num_recommendations=3)
        self.assertIsInstance(recommendations, list)
        self.assertLessEqual(len(recommendations), 3)
    
    def test_get_collaborative_recommendations(self):
        """Test collaborative recommendations"""
        recommendations = self.recommender.get_collaborative_recommendations(1, num_recommendations=3)
        self.assertIsInstance(recommendations, list)
    
    def test_get_content_based_recommendations(self):
        """Test content-based recommendations"""
        recommendations = self.recommender.get_content_based_recommendations(1, num_recommendations=3)
        self.assertIsInstance(recommendations, list)
    
    def test_get_similar_users(self):
        """Test finding similar users"""
        similar_users = self.recommender.get_similar_users(1, n_users=2)
        self.assertIsInstance(similar_users, list)
    
    def test_get_similar_songs(self):
        """Test finding similar songs"""
        similar_songs = self.recommender.get_similar_songs(1, n_songs=3)
        self.assertIsInstance(similar_songs, list)


class TestDataProcessor(unittest.TestCase):
    """Test data processor"""
    
    def setUp(self):
        """Create sample data"""
        self.processor = DataProcessor()
        self.history = pd.DataFrame({
            'user_id': [1, 1, 2, 2, 3],
            'song_id': [1, 2, 1, 3, 2],
            'rating': [5, 4, 3, 5, 4]
        })
    
    def test_create_user_item_matrix(self):
        """Test user-item matrix creation"""
        matrix = self.processor.create_user_item_matrix(self.history)
        self.assertIsInstance(matrix, pd.DataFrame)
        self.assertEqual(matrix.shape[0], 3)  # 3 users
        self.assertEqual(matrix.shape[1], 3)  # 3 songs
    
    def test_normalize_ratings(self):
        """Test rating normalization"""
        ratings = pd.Series([1, 2, 3, 4, 5])
        normalized = self.processor.normalize_ratings(ratings)
        
        self.assertGreaterEqual(normalized.min(), 0)
        self.assertLessEqual(normalized.max(), 1)
    
    def test_denormalize_ratings(self):
        """Test rating denormalization"""
        normalized = np.array([0, 0.25, 0.5, 0.75, 1.0])
        denormalized = self.processor.denormalize_ratings(normalized)
        
        self.assertEqual(denormalized[0], 1)
        self.assertEqual(denormalized[-1], 5)


class TestFeedbackManager(unittest.TestCase):
    """Test feedback manager"""
    
    def setUp(self):
        """Create temporary file for testing"""
        self.temp_dir = tempfile.mkdtemp()
        self.history_file = os.path.join(self.temp_dir, "history.csv")
        
        # Create initial file
        df = pd.DataFrame({
            'user_id': [1, 1, 2],
            'song_id': [1, 2, 1],
            'rating': [5, 4, 3],
            'timestamp': ['2024-01-01T10:00:00', '2024-01-02T11:00:00', '2024-01-03T12:00:00']
        })
        df.to_csv(self.history_file, index=False)
        
        self.manager = FeedbackManager(self.history_file)
    
    def tearDown(self):
        """Clean up temporary files"""
        if os.path.exists(self.history_file):
            os.remove(self.history_file)
        os.rmdir(self.temp_dir)
    
    def test_record_feedback(self):
        """Test recording feedback"""
        result = self.manager.record_feedback(2, 2, 4)
        self.assertTrue(result)
        
        # Verify it was written
        df = pd.read_csv(self.history_file)
        self.assertEqual(len(df), 4)
    
    def test_get_user_feedback_stats(self):
        """Test getting user feedback stats"""
        stats = self.manager.get_user_feedback_stats(1)
        self.assertEqual(stats['user_id'], 1)
        self.assertEqual(stats['total_ratings'], 2)
        self.assertAlmostEqual(stats['average_rating'], 4.5)


class TestValidators(unittest.TestCase):
    """Test input validators"""
    
    def test_validate_user_id(self):
        """Test user ID validation"""
        self.assertTrue(validate_user_id(1))
        self.assertTrue(validate_user_id(100))
        self.assertFalse(validate_user_id(0))
        self.assertFalse(validate_user_id(-1))
        self.assertFalse(validate_user_id("abc"))
    
    def test_validate_song_id(self):
        """Test song ID validation"""
        self.assertTrue(validate_song_id(1))
        self.assertTrue(validate_song_id(25))
        self.assertFalse(validate_song_id(0))
        self.assertFalse(validate_song_id(-5))
        self.assertFalse(validate_song_id("xyz"))
    
    def test_validate_rating(self):
        """Test rating validation"""
        self.assertTrue(validate_rating(1))
        self.assertTrue(validate_rating(3.5))
        self.assertTrue(validate_rating(5))
        self.assertFalse(validate_rating(0))
        self.assertFalse(validate_rating(6))
        self.assertFalse(validate_rating("4"))
    
    def test_validate_email(self):
        """Test email validation"""
        self.assertTrue(validate_email("user@example.com"))
        self.assertFalse(validate_email("invalid-email"))
        self.assertFalse(validate_email("@example.com"))
    
    def test_validate_number(self):
        """Test number validation"""
        self.assertTrue(validate_number(5))
        self.assertTrue(validate_number(5, min_val=0, max_val=10))
        self.assertFalse(validate_number(15, min_val=0, max_val=10))
        self.assertFalse(validate_number("abc"))


if __name__ == '__main__':
    unittest.main()
