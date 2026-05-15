"""Root-level models package.

This file makes the top-level `models` directory importable as a package
so `src/main.py` can import `models.model_saver` when the repository root
is added to `sys.path`.
"""

__all__ = ["model_saver"]
