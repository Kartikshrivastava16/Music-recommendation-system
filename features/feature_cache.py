"""
Audio feature cache utilities.
Saves and loads pre-computed song feature DataFrames and similarity
matrices so they don't need to be recomputed on every server restart.
"""

import pickle
import logging
import pandas as pd
from pathlib import Path
from datetime import datetime
from typing import Optional

logger = logging.getLogger(__name__)

FEATURES_DIR  = Path(__file__).parent.parent.parent / "features"
FEATURES_FILE = FEATURES_DIR / "audio_features.pkl"
META_FILE     = FEATURES_DIR / "features_meta.txt"


def save_features(song_features: pd.DataFrame, label: str = "audio_features") -> bool:
    """
    Serialize and save the song feature DataFrame to disk.

    Args:
        song_features: DataFrame produced by FeatureEngineer or DataLoader.
        label: Human-readable tag for the metadata sidecar.

    Returns:
        True on success, False on failure.
    """
    try:
        FEATURES_DIR.mkdir(parents=True, exist_ok=True)

        with open(FEATURES_FILE, "wb") as f:
            pickle.dump(song_features, f)

        with open(META_FILE, "w") as f:
            f.write(f"label     : {label}\n")
            f.write(f"saved_at  : {datetime.now().isoformat()}\n")
            f.write(f"songs     : {len(song_features)}\n")
            f.write(f"columns   : {', '.join(song_features.columns.tolist())}\n")

        logger.info(f"Audio features saved to {FEATURES_FILE}")
        return True

    except Exception as e:
        logger.error(f"Failed to save audio features: {e}")
        return False


def load_features(path: Optional[Path] = None) -> Optional[pd.DataFrame]:
    """
    Load a previously saved song feature DataFrame from disk.

    Args:
        path: Optional path override; defaults to features/audio_features.pkl.

    Returns:
        DataFrame on success, None if the file doesn't exist or loading fails.
    """
    target = Path(path) if path else FEATURES_FILE

    if not target.exists():
        logger.warning(f"No saved features found at {target}")
        return None

    try:
        with open(target, "rb") as f:
            features = pickle.load(f)
        logger.info(f"Audio features loaded from {target} ({len(features)} songs)")
        return features

    except Exception as e:
        logger.error(f"Failed to load audio features: {e}")
        return None


def features_exist() -> bool:
    """Return True if a saved features file is present."""
    return FEATURES_FILE.exists()


def get_features_meta() -> dict:
    """
    Read the metadata sidecar and return it as a dict.
    Returns an empty dict if no metadata file exists.
    """
    if not META_FILE.exists():
        return {}

    meta = {}
    try:
        for line in META_FILE.read_text().splitlines():
            if ":" in line:
                key, _, value = line.partition(":")
                meta[key.strip()] = value.strip()
    except Exception:
        pass
    return meta
