"""
Test API endpoints
"""

import unittest
import json
import pandas as pd
import tempfile
import os
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

# Import the Flask app
from api.app import app

class TestAPIEndpoints(unittest.TestCase):
    """Test API endpoints"""
    
    @classmethod
    def setUpClass(cls):
        """Set up test client"""
        cls.app = app
        cls.app.config['TESTING'] = True
        cls.client = cls.app.test_client()
    
    def test_health_check(self):
        """Test health check endpoint"""
        response = self.client.get('/health')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['status'], 'healthy')
    
    def test_not_found(self):
        """Test 404 error handling"""
        response = self.client.get('/api/nonexistent')
        self.assertEqual(response.status_code, 404)
    
    def test_recommendations_invalid_user(self):
        """Test recommendations with invalid user ID"""
        response = self.client.get('/api/recommendations/invalid')
        self.assertEqual(response.status_code, 400)
    
    def test_similar_users_invalid_user(self):
        """Test similar users with invalid user ID"""
        response = self.client.get('/api/similar-users/-1')
        self.assertEqual(response.status_code, 400)
    
    def test_similar_songs_invalid_song(self):
        """Test similar songs with invalid song ID"""
        response = self.client.get('/api/similar-songs/0')
        self.assertEqual(response.status_code, 400)
    
    def test_feedback_missing_data(self):
        """Test feedback endpoint with missing data"""
        response = self.client.post('/api/feedback', json={})
        self.assertEqual(response.status_code, 400)
    
    def test_feedback_invalid_rating(self):
        """Test feedback with invalid rating"""
        response = self.client.post('/api/feedback', json={
            'user_id': 1,
            'song_id': 1,
            'rating': 10  # Invalid: should be 1-5
        })
        self.assertEqual(response.status_code, 400)
    
    def test_stats_endpoint(self):
        """Test stats endpoint"""
        response = self.client.get('/api/stats')
        if response.status_code == 200:
            data = json.loads(response.data)
            self.assertIn('total_songs', data)
            self.assertIn('total_users', data)


class TestAPIFormat(unittest.TestCase):
    """Test API response formats"""
    
    def setUp(self):
        """Set up test client"""
        self.app = app
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()
    
    def test_health_response_format(self):
        """Test health check response format"""
        response = self.client.get('/health')
        self.assertEqual(response.content_type, 'application/json')
        
        data = json.loads(response.data)
        self.assertIn('status', data)
        self.assertIn('service', data)
    
    def test_error_response_format(self):
        """Test error response format"""
        response = self.client.get('/api/recommendations/invalid')
        self.assertEqual(response.content_type, 'application/json')
        
        data = json.loads(response.data)
        self.assertIn('error', data)


if __name__ == '__main__':
    unittest.main()
