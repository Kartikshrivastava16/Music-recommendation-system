"""
Data loader module for loading recommendation data
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Tuple, Optional
import logging

logger = logging.getLogger(__name__)

class DataLoader:
    """Load data from CSV files"""
    
    def __init__(self, data_dir: str = "data"):
        """
        Initialize data loader
        
        Args:
            data_dir: Directory containing CSV files
        """
        self.data_dir = Path(data_dir)
        self.songs = None
        self.users = None
        self.history = None
    
    def load_songs(self) -> pd.DataFrame:
        """
        Load songs data
        
        Returns:
            DataFrame with columns: song_id, title, artist, genre, tempo, energy, etc.
        """
        songs_path = self.data_dir / "songs.csv"
        
        if not songs_path.exists():
            raise FileNotFoundError(f"Songs file not found: {songs_path}")
        
        self.songs = pd.read_csv(songs_path)
        logger.info(f"Loaded {len(self.songs)} songs")
        
        return self.songs
    
    def load_users(self) -> pd.DataFrame:
        """
        Load users data
        
        Returns:
            DataFrame with columns: user_id, name, age, gender, etc.
        """
        users_path = self.data_dir / "users.csv"
        
        if not users_path.exists():
            raise FileNotFoundError(f"Users file not found: {users_path}")
        
        self.users = pd.read_csv(users_path)
        logger.info(f"Loaded {len(self.users)} users")
        
        return self.users
    
    def load_listening_history(self) -> pd.DataFrame:
        """
        Load listening history/ratings data
        
        Returns:
            DataFrame with columns: user_id, song_id, rating, timestamp
        """
        history_path = self.data_dir / "listening_history.csv"
        
        if not history_path.exists():
            raise FileNotFoundError(f"Listening history file not found: {history_path}")
        
        self.history = pd.read_csv(history_path)
        logger.info(f"Loaded {len(self.history)} listening history records")
        
        return self.history
    
    def load_all(self) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
        """
        Load all data files
        
        Returns:
            Tuple of (songs, users, listening_history) DataFrames
        """
        songs = self.load_songs()
        users = self.load_users()
        history = self.load_listening_history()
        
        return songs, users, history
    
    def validate_data(self) -> bool:
        """
        Validate data integrity
        
        Returns:
            True if valid, False otherwise
        """
        if self.songs is None or self.users is None or self.history is None:
            logger.warning("Data not loaded yet")
            return False
        
        # Check for required columns
        required_song_cols = ['song_id', 'title']
        required_user_cols = ['user_id']
        required_history_cols = ['user_id', 'song_id', 'rating']
        
        for col in required_song_cols:
            if col not in self.songs.columns:
                logger.error(f"Missing column in songs: {col}")
                return False
        
        for col in required_user_cols:
            if col not in self.users.columns:
                logger.error(f"Missing column in users: {col}")
                return False
        
        for col in required_history_cols:
            if col not in self.history.columns:
                logger.error(f"Missing column in history: {col}")
                return False
        
        # Check for duplicate entries
        if self.songs['song_id'].duplicated().any():
            logger.warning("Duplicate song_ids found")
        
        if self.users['user_id'].duplicated().any():
            logger.warning("Duplicate user_ids found")
        
        logger.info("Data validation passed")
        return True
    
    def get_user_history(self, user_id: int) -> pd.DataFrame:
        """Get listening history for a specific user"""
        if self.history is None:
            self.load_listening_history()
        
        return self.history[self.history['user_id'] == user_id]
    
    def get_song_info(self, song_id: int) -> Optional[pd.Series]:
        """Get information for a specific song"""
        if self.songs is None:
            self.load_songs()
        
        song = self.songs[self.songs['song_id'] == song_id]
        if len(song) > 0:
            return song.iloc[0]
        return None
    
    def get_user_info(self, user_id: int) -> Optional[pd.Series]:
        """Get information for a specific user"""
        if self.users is None:
            self.load_users()
        
        user = self.users[self.users['user_id'] == user_id]
        if len(user) > 0:
            return user.iloc[0]
        return None
