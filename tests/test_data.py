"""
Test data loading and processing
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

from data.loader import DataLoader
from data.processor import DataProcessor

class TestDataLoader(unittest.TestCase):
    """Test data loader"""
    
    def setUp(self):
        """Create temporary CSV files for testing"""
        self.temp_dir = tempfile.mkdtemp()
        
        # Create songs.csv
        songs_df = pd.DataFrame({
            'song_id': [1, 2, 3],
            'title': ['Song A', 'Song B', 'Song C'],
            'artist': ['Artist 1', 'Artist 2', 'Artist 3'],
            'genre': ['Pop', 'Rock', 'Jazz'],
            'tempo': [120, 130, 100],
            'energy': [0.7, 0.8, 0.5]
        })
        songs_df.to_csv(os.path.join(self.temp_dir, 'songs.csv'), index=False)
        
        # Create users.csv
        users_df = pd.DataFrame({
            'user_id': [1, 2, 3],
            'name': ['User A', 'User B', 'User C'],
            'age': [25, 30, 35]
        })
        users_df.to_csv(os.path.join(self.temp_dir, 'users.csv'), index=False)
        
        # Create listening_history.csv
        history_df = pd.DataFrame({
            'user_id': [1, 1, 2, 2, 3],
            'song_id': [1, 2, 1, 3, 2],
            'rating': [5, 4, 3, 5, 4],
            'timestamp': ['2024-01-01T10:00:00', '2024-01-02T11:00:00', 
                         '2024-01-03T12:00:00', '2024-01-04T13:00:00', '2024-01-05T14:00:00']
        })
        history_df.to_csv(os.path.join(self.temp_dir, 'listening_history.csv'), index=False)
        
        self.loader = DataLoader(self.temp_dir)
    
    def tearDown(self):
        """Clean up temporary files"""
        for file in os.listdir(self.temp_dir):
            os.remove(os.path.join(self.temp_dir, file))
        os.rmdir(self.temp_dir)
    
    def test_load_songs(self):
        """Test loading songs"""
        songs = self.loader.load_songs()
        self.assertEqual(len(songs), 3)
        self.assertIn('song_id', songs.columns)
        self.assertIn('title', songs.columns)
    
    def test_load_users(self):
        """Test loading users"""
        users = self.loader.load_users()
        self.assertEqual(len(users), 3)
        self.assertIn('user_id', users.columns)
    
    def test_load_listening_history(self):
        """Test loading listening history"""
        history = self.loader.load_listening_history()
        self.assertEqual(len(history), 5)
        self.assertIn('rating', history.columns)
    
    def test_load_all(self):
        """Test loading all data"""
        songs, users, history = self.loader.load_all()
        self.assertEqual(len(songs), 3)
        self.assertEqual(len(users), 3)
        self.assertEqual(len(history), 5)
    
    def test_get_user_history(self):
        """Test getting user's listening history"""
        self.loader.load_listening_history()
        user_history = self.loader.get_user_history(1)
        self.assertEqual(len(user_history), 2)  # User 1 has 2 ratings
    
    def test_get_song_info(self):
        """Test getting song information"""
        self.loader.load_songs()
        song = self.loader.get_song_info(1)
        self.assertIsNotNone(song)
        self.assertEqual(song['title'], 'Song A')
    
    def test_get_user_info(self):
        """Test getting user information"""
        self.loader.load_users()
        user = self.loader.get_user_info(1)
        self.assertIsNotNone(user)
        self.assertEqual(user['name'], 'User A')


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
        """Test creating user-item matrix"""
        matrix = self.processor.create_user_item_matrix(self.history)
        
        self.assertEqual(matrix.shape[0], 3)  # 3 users
        self.assertEqual(matrix.shape[1], 3)  # 3 songs
        self.assertEqual(matrix.loc[1, 1], 5)  # User 1 rated song 1 as 5
    
    def test_normalize_ratings(self):
        """Test rating normalization"""
        ratings = pd.Series([1, 2, 3, 4, 5])
        normalized = self.processor.normalize_ratings(ratings)
        
        self.assertGreaterEqual(normalized.min(), 0)
        self.assertLessEqual(normalized.max(), 1)
        self.assertEqual(normalized.iloc[0], 0)  # 1 normalized to 0
        self.assertEqual(normalized.iloc[-1], 1)  # 5 normalized to 1
    
    def test_denormalize_ratings(self):
        """Test denormalizing ratings"""
        normalized = np.array([0, 0.25, 0.5, 0.75, 1.0])
        denormalized = self.processor.denormalize_ratings(normalized)
        
        self.assertEqual(denormalized[0], 1)  # 0 normalized becomes 1
        self.assertEqual(denormalized[-1], 5)  # 1 normalized becomes 5


if __name__ == '__main__':
    unittest.main()
