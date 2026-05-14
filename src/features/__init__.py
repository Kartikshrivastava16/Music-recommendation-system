"""
Audio features extraction module
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Optional

class AudioFeatureExtractor:
    """Extract and analyze audio features"""
    
    FEATURE_NAMES = [
        'tempo',           # Beats per minute
        'energy',          # 0-1 scale intensity
        'danceability',    # 0-1 scale
        'valence',         # 0-1 scale positivity/mood
        'acousticness',    # 0-1 scale
        'instrumentalness',# 0-1 scale
        'liveness',        # 0-1 scale audience presence
        'speechiness',     # 0-1 scale spoken words
    ]
    
    def __init__(self):
        self.features_cache = {}
        self.feature_stats = None
    
    def extract_features(self, audio_path: str) -> Dict[str, float]:
        """
        Extract audio features from a song file
        
        Args:
            audio_path: Path to audio file
        
        Returns:
            Dictionary of audio features
        """
        features = {}
        
        try:
            import librosa
            y, sr = librosa.load(audio_path)
            
            # Extract features
            features['tempo'] = librosa.beat.tempo(y=y, sr=sr)[0]
            features['energy'] = float(np.sqrt(np.mean(y**2)))
            
            # Spectral features
            spectral_centroids = librosa.feature.spectral_centroid(y=y, sr=sr)[0]
            features['energy'] = float(np.mean(spectral_centroids))
            
            # Zero crossing rate
            zcr = librosa.feature.zero_crossing_rate(y)[0]
            features['speechiness'] = float(np.mean(zcr))
            
            # MFCC
            mfccs = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)
            features['danceability'] = float(np.mean(np.abs(np.diff(mfccs))))
            
            # Default values for other features
            features['valence'] = 0.5
            features['acousticness'] = 0.5
            features['instrumentalness'] = 0.5
            features['liveness'] = 0.5
            
        except ImportError:
            print("librosa not installed, returning default features")
            features = {name: 0.5 for name in self.FEATURE_NAMES}
        except Exception as e:
            print(f"Error extracting features: {e}")
            features = {name: 0.5 for name in self.FEATURE_NAMES}
        
        return features
    
    def get_feature_vector(self, features: Dict[str, float]) -> np.ndarray:
        """Convert feature dictionary to vector"""
        return np.array([features.get(name, 0.5) for name in self.FEATURE_NAMES])
    
    def normalize_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Normalize audio features to 0-1 range"""
        df_copy = df.copy()
        
        for feature in self.FEATURE_NAMES:
            if feature in df_copy.columns:
                min_val = df_copy[feature].min()
                max_val = df_copy[feature].max()
                if max_val != min_val:
                    df_copy[feature] = (df_copy[feature] - min_val) / (max_val - min_val)
        
        return df_copy
    
    def compute_similarity(self, features1: np.ndarray, features2: np.ndarray) -> float:
        """Compute cosine similarity between two feature vectors"""
        dot_product = np.dot(features1, features2)
        magnitude1 = np.linalg.norm(features1)
        magnitude2 = np.linalg.norm(features2)
        
        if magnitude1 == 0 or magnitude2 == 0:
            return 0.0
        
        return dot_product / (magnitude1 * magnitude2)
