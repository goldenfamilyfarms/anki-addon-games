"""
Data layer for NintendAnki.

This package contains all data models, enums, and persistence managers
for the NintendAnki add-on.
"""

from data.config_manager import ConfigManager
from data.data_manager import DataManager
from data.models import (
    # Enums
    Theme,
    PowerUpType,
    CollectibleType,
    AnimationType,
    
    # Core result dataclasses
    ReviewResult,
    ProgressionState,
    ScoreResult,
    PenaltyResult,
    
    # Achievement dataclasses
    Achievement,
    AchievementProgress,
    
    # Power-up dataclasses
    PowerUp,
    ActivePowerUp,
    
    # Level dataclasses
    Level,
    LevelReward,
    LevelProgress,
    
    # Collectible dataclasses
    Collectible,
    Cosmetic,
    ShopItem,
    
    # State dataclasses
    ThemeState,
    ThemeStats,
    GameConfig,
    GameState,
    
    # Animation dataclasses
    Animation,
    LevelView,
)

__all__ = [
    # Managers
    "ConfigManager",
    "DataManager",
    
    # Enums
    "Theme",
    "PowerUpType",
    "CollectibleType",
    "AnimationType",
    
    # Core result dataclasses
    "ReviewResult",
    "ProgressionState",
    "ScoreResult",
    "PenaltyResult",
    
    # Achievement dataclasses
    "Achievement",
    "AchievementProgress",
    
    # Power-up dataclasses
    "PowerUp",
    "ActivePowerUp",
    
    # Level dataclasses
    "Level",
    "LevelReward",
    "LevelProgress",
    
    # Collectible dataclasses
    "Collectible",
    "Cosmetic",
    "ShopItem",
    
    # State dataclasses
    "ThemeState",
    "ThemeStats",
    "GameConfig",
    "GameState",
    
    # Animation dataclasses
    "Animation",
    "LevelView",
]
