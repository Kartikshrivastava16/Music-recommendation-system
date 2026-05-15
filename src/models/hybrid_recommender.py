"""
Hybrid Recommender combining Collaborative and Content-Based Filtering.
Includes Maximal Marginal Relevance (MMR) re-ranking for diversity and
a serendipity boost that surfaces less-obvious but still relevant songs.
"""

import pandas as pd
import numpy as np
from typing import List, Tuple, Dict, Optional
from models.collaborative_filtering import CollaborativeFiltering
from models.content_based_filtering import ContentBasedFiltering
import logging

logger = logging.getLogger(__name__)


class HybridRecommender:
    """
    Hybrid recommendation system combining Collaborative and Content-Based Filtering.

    Diversity & Serendipity
    -----------------------
    ``get_recommendations()`` accepts two optional per-call overrides:

    * ``diversity_lambda`` (0-1): higher values push results toward MMR
      re-ranking so the returned list covers more varied audio features
      rather than clustering around one style.
    * ``serendipity_boost`` (0-1): adds a small reward to songs whose
      features are only loosely similar to the user's history, surfacing
      pleasant surprises without completely ignoring relevance.
    """

    def __init__(self,
                 collaborative_weight: float = 0.6,
                 content_weight: float = 0.4,
                 diversity_lambda: float = 0.3,
                 serendipity_boost: float = 0.15):
        """
        Initialize hybrid recommender.

        Args:
            collaborative_weight: Weight for collaborative filtering (0-1).
            content_weight: Weight for content-based filtering (0-1).
            diversity_lambda: MMR trade-off between relevance and diversity
                (0 = pure relevance, 1 = pure diversity). Default 0.3.
            serendipity_boost: Extra score given to songs with low-to-medium
                similarity to the user's history (0 disables). Default 0.15.
        """
        self.collaborative_weight = collaborative_weight
        self.content_weight = content_weight
        self.diversity_lambda = diversity_lambda
        self.serendipity_boost = serendipity_boost

        self.collaborative_model: Optional[CollaborativeFiltering] = None
        self.content_model: Optional[ContentBasedFiltering] = None
        self.user_item_matrix: Optional[pd.DataFrame] = None
        self.song_features: Optional[pd.DataFrame] = None

    # ------------------------------------------------------------------
    # Training
    # ------------------------------------------------------------------

    def fit(self, user_item_matrix: pd.DataFrame, song_features: pd.DataFrame) -> None:
        """
        Train both recommendation models.

        Args:
            user_item_matrix: User-item rating matrix (users × songs).
            song_features: Song feature DataFrame (must include song_id column).
        """
        self.user_item_matrix = user_item_matrix
        self.song_features = song_features

        self.collaborative_model = CollaborativeFiltering()
        self.collaborative_model.fit(user_item_matrix)

        self.content_model = ContentBasedFiltering()
        self.content_model.fit(song_features)

        logger.info(
            f"HybridRecommender fitted: {len(user_item_matrix)} users, "
            f"{len(song_features)} songs"
        )

    # ------------------------------------------------------------------
    # Main recommendation entry point
    # ------------------------------------------------------------------

    def get_recommendations(self,
                            user_id: int,
                            num_recommendations: int = 10,
                            diversity_lambda: Optional[float] = None,
                            serendipity_boost: Optional[float] = None
                            ) -> List[Tuple[int, float]]:
        """
        Get hybrid recommendations for a user.

        Args:
            user_id: Target user ID.
            num_recommendations: Number of final recommendations to return.
            diversity_lambda: Per-call override (0 = pure relevance, 1 = pure diversity).
            serendipity_boost: Per-call override (0 disables the novelty bonus).

        Returns:
            List of (song_id, score) tuples, re-ranked for diversity when
            diversity_lambda > 0.
        """
        lam   = self.diversity_lambda   if diversity_lambda  is None else diversity_lambda
        boost = self.serendipity_boost  if serendipity_boost is None else serendipity_boost

        # Gather a large candidate pool (3× final size) from both models
        candidate_pool: Dict[int, float] = {}

        for song_id, score in self.get_collaborative_recommendations(
                user_id, num_recommendations * 3):
            candidate_pool[song_id] = candidate_pool.get(song_id, 0.0) + score * self.collaborative_weight

        for song_id, score in self.get_content_based_recommendations(
                user_id, num_recommendations * 3):
            candidate_pool[song_id] = candidate_pool.get(song_id, 0.0) + score * self.content_weight

        if not candidate_pool:
            return []

        # Serendipity boost before ranking
        if boost > 0:
            candidate_pool = self._apply_serendipity_boost(user_id, candidate_pool, boost)

        # Sort by relevance score descending
        sorted_candidates = sorted(candidate_pool.items(), key=lambda x: x[1], reverse=True)

        # MMR re-ranking for diversity
        if lam > 0 and self.content_model is not None:
            return self._mmr_rerank(sorted_candidates, num_recommendations, lam)
        return sorted_candidates[:num_recommendations]

    # ------------------------------------------------------------------
    # Individual model recommendation helpers
    # ------------------------------------------------------------------

    def get_collaborative_recommendations(self,
                                          user_id: int,
                                          num_recommendations: int = 10
                                          ) -> List[Tuple[int, float]]:
        """Get recommendations using collaborative filtering only."""
        if self.collaborative_model is None:
            return []
        return self.collaborative_model.get_recommendations(user_id, num_recommendations)

    def get_content_based_recommendations(self,
                                          user_id: int,
                                          num_recommendations: int = 10
                                          ) -> List[Tuple[int, float]]:
        """
        Get recommendations using content-based filtering only.

        Identifies the user's highly-rated songs and finds audio-similar songs
        they haven't heard yet.
        """
        if self.content_model is None or self.user_item_matrix is None:
            return []

        if user_id not in self.user_item_matrix.index:
            return []

        user_ratings  = self.user_item_matrix.loc[user_id]
        rated_songs   = user_ratings[user_ratings > 0].index.tolist()

        if not rated_songs:
            return []

        accumulated: Dict[int, float] = {}
        for song_id in rated_songs:
            rating = float(user_ratings[song_id])
            for similar_id, similarity in self.content_model.get_recommendations(
                    song_id, num_recommendations * 2):
                if similar_id not in rated_songs:
                    weighted = similarity * rating
                    accumulated[similar_id] = max(accumulated.get(similar_id, 0.0), weighted)

        sorted_recs = sorted(accumulated.items(), key=lambda x: x[1], reverse=True)
        return sorted_recs[:num_recommendations]

    # ------------------------------------------------------------------
    # Similarity helpers
    # ------------------------------------------------------------------

    def get_similar_users(self, user_id: int, n_users: int = 5) -> List[Tuple[int, float]]:
        """Return the n most similar users to user_id."""
        if self.collaborative_model is None:
            return []
        return self.collaborative_model.get_similar_users(user_id, n_users)

    def get_similar_songs(self, song_id: int, n_songs: int = 5) -> List[Tuple[int, float]]:
        """Return the n most similar songs to song_id."""
        if self.content_model is None:
            return []
        return self.content_model.get_recommendations(song_id, n_songs)

    # ------------------------------------------------------------------
    # Explanation
    # ------------------------------------------------------------------

    def get_explanations(self, user_id: int, song_id: int) -> Dict:
        """
        Explain why a song was recommended to a user.

        Returns:
            Dict with 'song_id', 'user_id', and 'reasons' list.
        """
        explanation: Dict = {
            'song_id': song_id,
            'user_id': user_id,
            'reasons': []
        }

        if self.collaborative_model:
            collab_recs = self.collaborative_model.get_recommendations(user_id, 50)
            if any(s == song_id for s, _ in collab_recs):
                explanation['reasons'].append("Similar users liked this song")

        if self.content_model:
            content_recs = self.get_content_based_recommendations(user_id, 50)
            if any(s == song_id for s, _ in content_recs):
                explanation['reasons'].append("Similar to songs you rated highly")

        if not explanation['reasons']:
            explanation['reasons'].append("Recommended based on your listening patterns")

        return explanation

    # ------------------------------------------------------------------
    # Diversity helpers (MMR + Serendipity)
    # ------------------------------------------------------------------

    def _mmr_rerank(self,
                    candidates: List[Tuple[int, float]],
                    k: int,
                    lam: float) -> List[Tuple[int, float]]:
        """
        Maximal Marginal Relevance re-ranking.

        At each step selects the candidate that maximises:
            MMR = (1 - lam) * relevance_score
                  - lam * max_similarity_to_already_selected

        Args:
            candidates: Relevance-sorted (song_id, score) list.
            k: Number of items to select.
            lam: Trade-off (0 = relevance only, 1 = diversity only).

        Returns:
            Re-ranked list of up to k (song_id, score) tuples.
        """
        if not candidates or self.content_model is None:
            return candidates[:k]

        sim_matrix = self.content_model.song_feature_similarity
        scores     = {s: sc for s, sc in candidates}
        remaining  = [s for s, _ in candidates]
        selected:  List[Tuple[int, float]] = []

        while remaining and len(selected) < k:
            if not selected:
                best = remaining[0]
            else:
                selected_ids = [s for s, _ in selected]
                best, best_mmr = None, float('-inf')

                for sid in remaining:
                    relevance = (1 - lam) * scores[sid]

                    if sid in sim_matrix.index:
                        sims = [
                            sim_matrix.loc[sid, sel]
                            for sel in selected_ids
                            if sel in sim_matrix.columns
                        ]
                        max_sim = max(sims) if sims else 0.0
                    else:
                        max_sim = 0.0

                    mmr = relevance - lam * max_sim
                    if mmr > best_mmr:
                        best_mmr = mmr
                        best = sid

            if best is None:
                break
            selected.append((best, scores[best]))
            remaining.remove(best)

        return selected

    def _apply_serendipity_boost(self,
                                  user_id: int,
                                  recommendations: Dict[int, float],
                                  boost: float) -> Dict[int, float]:
        """
        Add a small score bonus to songs that are somewhat novel relative to
        the user's listening history (average similarity in the 0.2-0.5 range).
        Uses a Gaussian bell-curve centred at similarity=0.35 so that very
        familiar songs (>0.7) and completely alien songs (<0.1) get no bonus.

        Args:
            user_id: Target user ID.
            recommendations: Current {song_id: score} dict.
            boost: Maximum bonus to add (scaled 0-1 by the novelty factor).

        Returns:
            Updated recommendations dict with serendipity bonuses applied.
        """
        if self.content_model is None or self.user_item_matrix is None:
            return recommendations

        if user_id not in self.user_item_matrix.index:
            return recommendations

        sim_matrix   = self.content_model.song_feature_similarity
        user_ratings = self.user_item_matrix.loc[user_id]
        listened     = user_ratings[user_ratings > 0].index.tolist()

        if not listened:
            return recommendations

        boosted = dict(recommendations)
        for song_id in recommendations:
            if song_id not in sim_matrix.index:
                continue

            sims = [
                sim_matrix.loc[song_id, lid]
                for lid in listened
                if lid in sim_matrix.columns
            ]
            if not sims:
                continue

            avg_sim = float(np.mean(sims))
            # Bell-curve peaking at avg_sim = 0.35, std = 0.15
            novelty_factor = float(np.exp(-((avg_sim - 0.35) ** 2) / (2 * 0.15 ** 2)))
            boosted[song_id] = recommendations[song_id] + boost * novelty_factor

        return boosted
