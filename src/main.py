"""
Main application entry point
"""

import sys
from pathlib import Path
from config import NUM_RECOMMENDATIONS
from utils.logger import get_logger
from data import DataLoader
from data.processor import DataProcessor
from models.hybrid_recommender import HybridRecommender

logger = get_logger(__name__)

def main():
    """Main application flow"""
    try:
        logger.info("Starting Music Recommendation System...")
        
        # Load data
        logger.info("Loading data...")
        data_loader = DataLoader(data_dir="data")
        
        # Check if data files exist
        data_dir = Path("data")
        if not data_dir.exists():
            logger.warning("Data directory not found. Creating sample data structure...")
            data_dir.mkdir(exist_ok=True)
            logger.info("Please add songs.csv, users.csv, and listening_history.csv to the data folder")
            return
        
        try:
            songs, users, history = data_loader.load_all()
            logger.info(f"Loaded {len(songs)} songs, {len(users)} users, {len(history)} history records")
        except FileNotFoundError as e:
            logger.error(f"Data files not found: {e}")
            logger.info("Please ensure the following CSV files exist in the data folder:")
            logger.info("  - songs.csv (with columns: song_id, title, artist, genre, etc.)")
            logger.info("  - users.csv (with columns: user_id, name, etc.)")
            logger.info("  - listening_history.csv (with columns: user_id, song_id, rating, timestamp)")
            return
        
        # Process data
        logger.info("Processing data...")
        processor = DataProcessor()
        user_item_matrix = processor.create_user_item_matrix(history)
        logger.info(f"Created user-item matrix: {user_item_matrix.shape}")
        
        # Prepare song features (using existing columns or defaults)
        song_features = songs.copy()
        feature_cols = [col for col in songs.columns if col not in ['song_id', 'title', 'artist']]
        
        if len(feature_cols) == 0:
            logger.warning("No audio features found in songs data. Using random features for demo.")
            import numpy as np
            for feat in ['tempo', 'energy', 'danceability', 'valence']:
                song_features[feat] = np.random.rand(len(songs))
        
        # Train hybrid recommender
        logger.info("Training recommendation models...")
        recommender = HybridRecommender(
            collaborative_weight=0.6,
            content_weight=0.4
        )
        recommender.fit(user_item_matrix, song_features)
        logger.info("Models trained successfully!")
        
        # Get sample recommendations
        if len(users) > 0:
            sample_user = users.iloc[0]['user_id']
            logger.info(f"Getting recommendations for user {sample_user}...")
            
            recommendations = recommender.get_recommendations(
                sample_user,
                user_item_matrix,
                num_recommendations=NUM_RECOMMENDATIONS
            )
            
            if recommendations:
                logger.info("Top recommendations:")
                for i, (song_id, score) in enumerate(recommendations, 1):
                    song = songs[songs['song_id'] == song_id]
                    title = song['title'].values[0] if len(song) > 0 else "Unknown"
                    logger.info(f"  {i}. {title} (Score: {score:.4f})")
            else:
                logger.info("No recommendations available")
        
        logger.info("Application completed successfully!")
        
    except Exception as e:
        logger.error(f"Application error: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()
