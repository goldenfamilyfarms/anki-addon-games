"""
Theme engines for NintendAnki.

This package contains theme-specific engine implementations:
- MarioEngine: Mario-style side-scrolling with coin collection
- ZeldaEngine: Zelda-style exploration with boss battles
- DKCEngine: DKC-style collectibles and time trials
"""

from themes.mario_engine import MarioEngine

__all__ = ["MarioEngine"]
