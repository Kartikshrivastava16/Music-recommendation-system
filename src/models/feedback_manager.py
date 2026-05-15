"""
Feedback manager for recording and managing user interactions.
Supports auto-retraining of the hybrid recommender after new feedback
once a configurable threshold of new ratings has accumulated.
"""

import pandas as pd
from pathlib import Path
from datetime import datetime
from typing import Optional, Callable
import logging

logger = logging.getLogger(__name__)

class FeedbackManager:
    """Manage user feedback and learning from interactions.
    
    Auto-retraining
    ---------------
    Pass a ``retrain_callback`` (a zero-argument callable that re-fits the
    recommender) and set ``retrain_threshold`` to the number of new ratings
    that should trigger a retrain.  Every time ``record_feedback`` pushes
    ``new_feedback_count`` past a multiple of ``retrain_threshold`` the
    callback is invoked automatically.
    """
    
    def __init__(self,
                 history_file: str = "data/listening_history.csv",
                 retrain_callback: Optional[Callable] = None,
                 retrain_threshold: int = 10):
        """
        Initialize feedback manager.
        
        Args:
            history_file: Path to listening history CSV file.
            retrain_callback: Zero-argument callable that re-fits the
                recommender model.  Called automatically whenever
                ``new_feedback_count`` reaches a new multiple of
                ``retrain_threshold``.  Pass ``None`` to disable auto-retrain.
            retrain_threshold: Number of new ratings between automatic
                retrains (default 10).
        """
        self.history_file = Path(history_file)
        self.feedback_buffer = []
        self.retrain_callback = retrain_callback
        self.retrain_threshold = retrain_threshold
        self.new_feedback_count = 0  # ratings received since last retrain
    
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
            
            # --- auto-retrain trigger ---
            self.new_feedback_count += 1
            if (
                self.retrain_callback is not None
                and self.retrain_threshold > 0
                and self.new_feedback_count % self.retrain_threshold == 0
            ):
                logger.info(
                    f"Auto-retrain triggered after {self.new_feedback_count} "
                    f"new ratings (threshold={self.retrain_threshold})"
                )
                try:
                    self.retrain_callback()
                    logger.info("Auto-retrain completed successfully")
                except Exception as retrain_err:
                    logger.error(f"Auto-retrain failed: {retrain_err}")
            
            return True
        
        except Exception as e:
            logger.error(f"Error recording feedback: {str(e)}")
            return False
    
    def set_retrain_callback(self, callback: Callable, threshold: int = None) -> None:
        """
        Attach or replace the auto-retrain callback at runtime.
        
        Args:
            callback: Zero-argument callable that re-fits the recommender.
            threshold: New threshold value; if None, keeps the existing one.
        """
        self.retrain_callback = callback
        if threshold is not None:
            self.retrain_threshold = threshold
        logger.info(
            f"Retrain callback set (threshold={self.retrain_threshold})"
        )
    
    def reset_feedback_count(self) -> None:
        """Reset the new-feedback counter (e.g. after a manual retrain)."""
        self.new_feedback_count = 0
        logger.info("New-feedback counter reset")
    
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
