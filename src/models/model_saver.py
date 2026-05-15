"""
Model persistence utilities.
Handles saving and loading trained recommender models to/from disk
so the server can restart without retraining from scratch.
"""

import pickle
import logging
from pathlib import Path
from datetime import datetime
from typing import Optional

logger = logging.getLogger(__name__)

MODEL_DIR = Path(__file__).parent.parent.parent / "models"
MODEL_FILE = MODEL_DIR / "trained_model.pkl"
META_FILE  = MODEL_DIR / "model_meta.txt"


def save_model(recommender, label: str = "hybrid_recommender") -> bool:
    """
    Serialize and save the trained recommender to disk.

    Args:
        recommender: A fitted HybridRecommender instance.
        label: Human-readable tag written to the metadata file.

    Returns:
        True on success, False on failure.
    """
    try:
        MODEL_DIR.mkdir(parents=True, exist_ok=True)

        with open(MODEL_FILE, "wb") as f:
            pickle.dump(recommender, f)

        # Write a plain-text metadata sidecar
        with open(META_FILE, "w") as f:
            f.write(f"label      : {label}\n")
            f.write(f"saved_at   : {datetime.now().isoformat()}\n")
            if recommender.user_item_matrix is not None:
                f.write(f"users      : {len(recommender.user_item_matrix)}\n")
                f.write(f"songs      : {len(recommender.user_item_matrix.columns)}\n")
            f.write(f"collab_w   : {recommender.collaborative_weight}\n")
            f.write(f"content_w  : {recommender.content_weight}\n")
            f.write(f"diversity  : {recommender.diversity_lambda}\n")
            f.write(f"serendipity: {recommender.serendipity_boost}\n")

        logger.info(f"Model saved to {MODEL_FILE}")
        return True

    except Exception as e:
        logger.error(f"Failed to save model: {e}")
        return False


def load_model(path: Optional[Path] = None):
    """
    Load a previously saved recommender from disk.

    Args:
        path: Optional path override; defaults to models/trained_model.pkl.

    Returns:
        Loaded recommender instance, or None if the file doesn't exist / fails.
    """
    target = Path(path) if path else MODEL_FILE

    if not target.exists():
        logger.warning(f"No saved model found at {target}")
        return None

    try:
        with open(target, "rb") as f:
            recommender = pickle.load(f)
        logger.info(f"Model loaded from {target}")
        return recommender

    except Exception as e:
        logger.error(f"Failed to load model: {e}")
        return None


def model_exists() -> bool:
    """Return True if a saved model file is present."""
    return MODEL_FILE.exists()


def get_model_meta() -> dict:
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
