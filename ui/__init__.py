"""
UI Layer for NintendAnki.

This package contains all UI-related components including:
- AssetManager: Sprite sheet loading and caching
- AnimationEngine: Animation playback and rendering
- GameWindow: Main game display window
- Dashboard: Statistics and progress display
- SettingsPanel: User configuration interface
"""

from ui.asset_manager import AssetManager, Sprite, SpriteSheet
from ui.animation_engine import (
    AnimationEngine,
    AnimationSequence,
    AnimationState,
    AnimationEventType,
)
from ui.game_window import GameWindow, AspectRatioWidget, StatsBar

__all__ = [
    'AssetManager',
    'Sprite',
    'SpriteSheet',
    'AnimationEngine',
    'AnimationSequence',
    'AnimationState',
    'AnimationEventType',
    'GameWindow',
    'AspectRatioWidget',
    'StatsBar',
]
