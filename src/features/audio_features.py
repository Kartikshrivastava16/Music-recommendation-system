"""
Audio feature extraction module.
Extracts numerical audio features from song files using librosa,
and aligns them with the songs DataFrame so they can be fed directly
into ContentBasedFiltering.
"""

import numpy as np
import pandas as pd
import logging
from pathlib import Path
from typing import Optional, List

logger = logging.getLogger(__name__)

# librosa is an optional heavy dependency; we guard the import so the rest
# of the project still works when it is not installed.
try:
    import librosa
    LIBROSA_AVAILABLE = True
except ImportError:
    LIBROSA_AVAILABLE = False
    logger.warning(
        "librosa is not installed. Audio extraction from files will be "
        "unavailable. Install it with: pip install librosa"
    )


# ---------------------------------------------------------------------------
# Feature columns that must be present in songs.csv for the system to work.
# These are also the columns that extract_from_file() returns.
# ---------------------------------------------------------------------------
REQUIRED_AUDIO_COLUMNS: List[str] = [
    "tempo",
    "energy",
    "danceability",
    "valence",
    "acousticness",
    "instrumentalness",
]


class AudioFeatureExtractor:
    """
    Extract audio features from songs.

    Two modes:
    - CSV mode  : read pre-computed features already in songs.csv (default,
                  no audio files needed).
    - File mode : compute features from .mp3/.wav files using librosa.
    """

    def __init__(self, audio_dir: Optional[str] = None, sample_rate: int = 22050):
        """
        Args:
            audio_dir: Directory containing audio files.  Only required for
                       file-based extraction.
            sample_rate: Sample rate passed to librosa (default 22050).
        """
        self.audio_dir = Path(audio_dir) if audio_dir else None
        self.sample_rate = sample_rate

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def extract_from_dataframe(self, songs_df: pd.DataFrame) -> pd.DataFrame:
        """
        Return a feature DataFrame built from columns already in songs_df.

        This is the primary path used by the system: songs.csv ships with
        pre-computed features, so no audio files are needed.

        Args:
            songs_df: DataFrame loaded by DataLoader (must contain song_id
                      and the REQUIRED_AUDIO_COLUMNS).

        Returns:
            DataFrame with song_id + available numeric feature columns,
            with any missing required columns filled with 0.
        """
        result = songs_df[["song_id"]].copy()

        for col in REQUIRED_AUDIO_COLUMNS:
            if col in songs_df.columns:
                result[col] = pd.to_numeric(songs_df[col], errors="coerce").fillna(0.0)
            else:
                logger.warning(f"Column '{col}' missing from songs data – filling with 0")
                result[col] = 0.0

        # Carry over any extra numeric columns (e.g. liveness, speechiness)
        extra_numeric = [
            c for c in songs_df.select_dtypes(include=[np.number]).columns
            if c not in result.columns and c != "song_id"
        ]
        for col in extra_numeric:
            result[col] = songs_df[col].fillna(0.0)

        logger.info(
            f"Extracted features for {len(result)} songs "
            f"({len(result.columns) - 1} feature columns)"
        )
        return result

    def extract_from_file(self, audio_path: str) -> Optional[dict]:
        """
        Compute audio features from a single audio file using librosa.

        Returns a dict with feature names as keys, or None on failure.
        Requires librosa to be installed.

        Args:
            audio_path: Path to an .mp3 or .wav file.
        """
        if not LIBROSA_AVAILABLE:
            logger.error("librosa is required for file-based feature extraction")
            return None

        try:
            y, sr = librosa.load(audio_path, sr=self.sample_rate, mono=True)

            # Tempo
            tempo, _ = librosa.beat.beat_track(y=y, sr=sr)

            # RMS energy
            rms = float(np.mean(librosa.feature.rms(y=y)))
            energy = float(np.clip(rms * 10, 0, 1))

            # Spectral centroid → proxy for brightness / danceability
            centroid = np.mean(librosa.feature.spectral_centroid(y=y, sr=sr))
            danceability = float(np.clip(centroid / 4000, 0, 1))

            # Zero-crossing rate → proxy for acousticness (inverted)
            zcr = float(np.mean(librosa.feature.zero_crossing_rate(y=y)))
            acousticness = float(np.clip(1 - zcr * 20, 0, 1))

            # Chroma mean → proxy for valence
            chroma = np.mean(librosa.feature.chroma_stft(y=y, sr=sr))
            valence = float(np.clip(chroma, 0, 1))

            # Spectral flatness → proxy for instrumentalness
            flatness = float(np.mean(librosa.feature.spectral_flatness(y=y)))
            instrumentalness = float(np.clip(flatness * 50, 0, 1))

            return {
                "tempo":            float(tempo),
                "energy":           energy,
                "danceability":     danceability,
                "valence":          valence,
                "acousticness":     acousticness,
                "instrumentalness": instrumentalness,
            }

        except Exception as e:
            logger.error(f"Feature extraction failed for '{audio_path}': {e}")
            return None

    def extract_from_directory(self, songs_df: pd.DataFrame) -> pd.DataFrame:
        """
        Compute features for all songs whose audio files exist in audio_dir,
        then merge with songs_df (falling back to CSV values for missing files).

        Args:
            songs_df: Songs DataFrame (must have song_id and title columns).

        Returns:
            Feature DataFrame as returned by extract_from_dataframe(), with
            file-computed values replacing CSV values where files were found.
        """
        if self.audio_dir is None or not self.audio_dir.exists():
            logger.warning("audio_dir not set or does not exist – falling back to CSV features")
            return self.extract_from_dataframe(songs_df)

        base = self.extract_from_dataframe(songs_df)
        updated = 0

        for _, row in songs_df.iterrows():
            song_id = row["song_id"]
            # Try common filename patterns
            candidates = [
                self.audio_dir / f"{song_id}.mp3",
                self.audio_dir / f"{song_id}.wav",
                self.audio_dir / f"{row.get('title', '')} - {row.get('artist', '')}.mp3",
            ]
            for path in candidates:
                if path.exists():
                    features = self.extract_from_file(str(path))
                    if features:
                        for col, val in features.items():
                            base.loc[base["song_id"] == song_id, col] = val
                        updated += 1
                    break

        logger.info(f"Updated features from audio files for {updated}/{len(songs_df)} songs")
        return base

    # ------------------------------------------------------------------
    # Convenience
    # ------------------------------------------------------------------

    @staticmethod
    def validate_features(features_df: pd.DataFrame) -> bool:
        """
        Check that a feature DataFrame has all required columns and no NaNs
        in those columns.

        Returns True if valid, False otherwise.
        """
        missing = [c for c in REQUIRED_AUDIO_COLUMNS if c not in features_df.columns]
        if missing:
            logger.warning(f"Missing required feature columns: {missing}")
            return False

        nan_cols = [
            c for c in REQUIRED_AUDIO_COLUMNS
            if features_df[c].isna().any()
        ]
        if nan_cols:
            logger.warning(f"NaN values found in feature columns: {nan_cols}")
            return False

        return True
