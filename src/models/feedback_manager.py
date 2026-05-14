"""
Feedback manager for recording and managing user interactions
"""

import pandas as pd
from pathlib import Path
from datetime import datetime
from typing import Optional
import logging

logger = logging.getLogger(__name__)

class FeedbackManager:
    """Manage user feedback and learning from interactions"""
    
    def __init__(self, history_file: str = "data/listening_history.csv"):
        """
        Initialize feedback manager
        
        Args:
            history_file: Path to listening history CSV file
        """
        self.history_file = Path(history_file)
        self.feedback_buffer = []
    
    def record_feedback(self, user_id: int, song_id: int, rating: float, 
                       timestamp: Optional[str] = None) -> bool:
        """
        Record user feedback on a song
        
        Args:
            user_id: User ID
            song_id: Song ID
            rating: Rating value (1-5)
            timestamp: Optional timestamp (defaults to current time)
        
        Returns:
            True if successful, False otherwise
        """
        try:
            if timestamp is None:
                timestamp = datetime.now().isoformat()
            
            # Add to buffer
            feedback = {
                'user_id': user_id,
                'song_id': song_id,
                'rating': rating,
                'timestamp': timestamp
            }
            self.feedback_buffer.append(feedback)
            
            # Append to file
            if self.history_file.exists():
                # Load existing data
                df = pd.read_csv(self.history_file)
                
                # Check if this rating already exists
                existing = df[(df['user_id'] == user_id) & (df['song_id'] == song_id)]
                if len(existing) > 0:
                    # Update existing rating
                    df.loc[(df['user_id'] == user_id) & (df['song_id'] == song_id), 'rating'] = rating
                    df.loc[(df['user_id'] == user_id) & (df['song_id'] == song_id), 'timestamp'] = timestamp
                else:
                    # Add new rating
                    new_row = pd.DataFrame([feedback])
                    df = pd.concat([df, new_row], ignore_index=True)
            else:
                # Create new file
                df = pd.DataFrame([feedback])
            
            df.to_csv(self.history_file, index=False)
            logger.info(f"Feedback recorded: user {user_id}, song {song_id}, rating {rating}")
            return True
        
        except Exception as e:
            logger.error(f"Error recording feedback: {str(e)}")
            return False
    
    def get_recent_feedback(self, limit: int = 100) -> list:
        """
        Get recent feedback entries
        
        Args:
            limit: Maximum number of entries to return
        
        Returns:
            List of recent feedback entries
        """
        if len(self.feedback_buffer) >= limit:
            return self.feedback_buffer[-limit:]
        return self.feedback_buffer
    
    def flush_buffer(self) -> bool:
        """
        Save buffered feedback to file
        
        Returns:
            True if successful
        """
        if len(self.feedback_buffer) == 0:
            return True
        
        try:
            if self.history_file.exists():
                df = pd.read_csv(self.history_file)
                new_rows = pd.DataFrame(self.feedback_buffer)
                df = pd.concat([df, new_rows], ignore_index=True)
            else:
                df = pd.DataFrame(self.feedback_buffer)
            
            df.to_csv(self.history_file, index=False)
            self.feedback_buffer = []
            logger.info("Feedback buffer flushed to file")
            return True
        
        except Exception as e:
            logger.error(f"Error flushing feedback buffer: {str(e)}")
            return False
    
    def get_user_feedback_stats(self, user_id: int) -> dict:
        """
        Get feedback statistics for a user
        
        Args:
            user_id: User ID
        
        Returns:
            Dictionary with statistics
        """
        try:
            if self.history_file.exists():
                df = pd.read_csv(self.history_file)
                user_feedback = df[df['user_id'] == user_id]
                
                if len(user_feedback) == 0:
                    return {
                        'user_id': user_id,
                        'total_ratings': 0,
                        'average_rating': 0,
                        'min_rating': 0,
                        'max_rating': 0
                    }
                
                return {
                    'user_id': user_id,
                    'total_ratings': len(user_feedback),
                    'average_rating': float(user_feedback['rating'].mean()),
                    'min_rating': float(user_feedback['rating'].min()),
                    'max_rating': float(user_feedback['rating'].max()),
                    'std_rating': float(user_feedback['rating'].std())
                }
            return {}
        
        except Exception as e:
            logger.error(f"Error getting user feedback stats: {str(e)}")
            return {}
    
    def get_song_feedback_stats(self, song_id: int) -> dict:
        """
        Get feedback statistics for a song
        
        Args:
            song_id: Song ID
        
        Returns:
            Dictionary with statistics
        """
        try:
            if self.history_file.exists():
                df = pd.read_csv(self.history_file)
                song_feedback = df[df['song_id'] == song_id]
                
                if len(song_feedback) == 0:
                    return {
                        'song_id': song_id,
                        'total_ratings': 0,
                        'average_rating': 0
                    }
                
                return {
                    'song_id': song_id,
                    'total_ratings': len(song_feedback),
                    'average_rating': float(song_feedback['rating'].mean()),
                    'min_rating': float(song_feedback['rating'].min()),
                    'max_rating': float(song_feedback['rating'].max())
                }
            return {}
        
        except Exception as e:
            logger.error(f"Error getting song feedback stats: {str(e)}")
            return {}
