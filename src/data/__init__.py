"""
Data loader module for loading song and user data
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Tuple, Optional

class DataLoader:
    """Load and manage music data"""
    
    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(data_dir)
        self.songs_df = None
        self.users_df = None
        self.history_df = None
    
    def load_songs(self, filename: str = "songs.csv") -> pd.DataFrame:
        """Load song data"""
        filepath = self.data_dir / filename
        if filepath.exists():
            self.songs_df = pd.read_csv(filepath)
            return self.songs_df
        else:
            raise FileNotFoundError(f"Songs file not found: {filepath}")
    
    def load_users(self, filename: str = "users.csv") -> pd.DataFrame:
        """Load user data"""
        filepath = self.data_dir / filename
        if filepath.exists():
            self.users_df = pd.read_csv(filepath)
            return self.users_df
        else:
            raise FileNotFoundError(f"Users file not found: {filepath}")
    
    def load_listening_history(self, filename: str = "listening_history.csv") -> pd.DataFrame:
        """Load user listening history with ratings"""
        filepath = self.data_dir / filename
        if filepath.exists():
            self.history_df = pd.read_csv(filepath)
            return self.history_df
        else:
            raise FileNotFoundError(f"History file not found: {filepath}")
    
    def load_all(self) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
        """Load all data files"""
        songs = self.load_songs()
        users = self.load_users()
        history = self.load_listening_history()
        return songs, users, history
    
    def get_user_ratings(self, user_id: int) -> pd.DataFrame:
        """Get all ratings for a specific user"""
        if self.history_df is None:
            self.load_listening_history()
        return self.history_df[self.history_df['user_id'] == user_id]
    
    def get_song_info(self, song_id: int) -> pd.Series:
        """Get information about a specific song"""
        if self.songs_df is None:
            self.load_songs()
        song = self.songs_df[self.songs_df['song_id'] == song_id]
        return song.iloc[0] if not song.empty else None
