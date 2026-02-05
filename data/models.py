"""
Data models and enums for NintendAnki.

This module defines all the core data structures used throughout the add-on,
including enums for themes and power-up types, and dataclasses for game state,
progression, scoring, achievements, and configuration.

Requirements: 2.1, 3.1, 8.3
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional


class Theme(str, Enum):
    """Available game themes.
    
    Each theme provides a unique visual style and game mechanics:
    - MARIO: Side-scrolling platformer with coin collection
    - ZELDA: Adventure exploration with boss battles
    - DKC: Jungle world with collectibles and time trials
    """
    MARIO = "mario"
    ZELDA = "zelda"
    DKC = "dkc"


class PowerUpType(str, Enum):
    """Types of power-ups available in the game.
    
    Power-ups are theme-specific and provide various bonuses.
    """
    # Mario specific power-ups
    MUSHROOM = "mushroom"
    FIRE_FLOWER = "fire_flower"
    STAR = "star"
    LEAF = "leaf"
    CAPE_FEATHER = "cape_feather"
    TANUKI_SUIT = "tanuki_suit"
    FROG_SUIT = "frog_suit"
    HAMMER_SUIT = "hammer_suit"
    ICE_FLOWER = "ice_flower"
    PROPELLER_MUSHROOM = "propeller_mushroom"
    MINI_MUSHROOM = "mini_mushroom"
    MEGA_MUSHROOM = "mega_mushroom"
    YOSHI_EGG = "yoshi_egg"
    POW_BLOCK = "pow_block"
    ONE_UP_MUSHROOM = "1up_mushroom"
    COIN = "coin"
    
    # Zelda specific power-ups
    HEART_CONTAINER = "heart_container"
    RUPEES = "rupees"
    BOW = "bow"
    BOMB_BAG = "bomb_bag"
    FAIRY = "fairy"
    POTION = "potion"
    HOOKSHOT = "hookshot"
    BOOMERANG = "boomerang"
    SHIELD = "shield"
    SWORD = "sword"
    BOMB = "bomb"
    MAP = "map"
    COMPASS = "compass"
    
    # Donkey Kong Country specific power-ups
    BANANA = "banana"
    BARREL = "barrel"
    ANIMAL_BUDDY = "animal_buddy"
    GOLDEN_BANANA = "golden_banana"
    DK_COIN = "dk_coin"
    BEAN = "bean"
    CRATE = "crate"
    HELMET = "helmet"
    SPRING_SHOES = "spring_shoes"
    PINEAPPLE = "pineapple"
    GUITAR = "guitar"
    TROPHY = "trophy"
    
    # Universal power-ups
    EXTRA_LIFE = "extra_life"
    TIME_EXTEND = "time_extend"
    SHIELD_BOOST = "shield_boost"
    SPEED_BOOST = "speed_boost"
    INVINCIBILITY = "invincibility"
    HEALTH_RECOVERY = "health_recovery"
    TIME_FREEZE = "time_freeze"
    DOUBLE_POINTS = "double_points"
    MULTIPLIER = "multiplier"
    SPECIAL_ABILITY = "special_ability"
    BONUS_LEVEL = "bonus_level"
    SECRET_ITEM = "secret_item"
    RANDOM_POWERUP = "random_powerup"


class CollectibleType(str, Enum):
    """Types of collectible items."""
    # In-game collectibles
    COIN = "coin"
    GEM = "gem"
    STAR = "star"
    HEART = "heart"
    BANANA = "banana"
    RUPEE = "rupee"
    DK_COIN = "dk_coin"
    COSMIC_DUST = "cosmic_dust"
    
    # Cosmetic items
    COSMETIC = "cosmetic"
    CHARACTER_SKIN = "character_skin"
    EMOTE = "emote"
    AVATAR_FRAME = "avatar_frame"
    BACKGROUND = "background"
    TITLE = "title"
    BADGE = "badge"
    TROPHY = "trophy"
    MEDAL = "medal"
    CERTIFICATE = "certificate"
    
    # Special items
    ITEM = "item"
    ARTIFACT = "artifact"
    MYSTERY_BOX = "mystery_box"
    LOOT_CRATE = "loot_crate"
    SPECIAL_EDITION = "special_edition"
    EVENT_ITEM = "event_item"
    LIMITED_EDITION = "limited_edition"
    SEASONAL_ITEM = "seasonal_item"
    VIRTUAL_CURRENCY = "virtual_currency"


class AnimationType(str, Enum):
    """Types of animations that can be played."""
    # Visual effects
    SPIN = "spin"
    GLOW = "glow"
    PULSE = "pulse"
    BOUNCE = "bounce"
    FADE = "fade"
    SLIDE = "slide"
    ZOOM = "zoom"
    WAVE = "wave"
    TWINKLE = "twinkle"
    ROTATE = "rotate"
    COLOR_SHIFT = "color_shift"
    
    # Game actions
    COLLECT = "collect"
    DAMAGE = "damage"
    POWER_UP = "power_up"
    LEVEL_UP = "level_up"
    RARE_FIND = "rare_find"
    
    # Character states
    IDLE = "idle"
    INTERACT = "interact"
    JUMP = "jump"
    RUN = "run"
    ATTACK = "attack"
    VICTORY = "victory"
    DEFEAT = "defeat"



@dataclass
class ReviewResult:
    """Represents the result of a card review.
    
    This dataclass captures all relevant information about a single
    card review event from Anki.
    
    Attributes:
        card_id: Unique identifier of the reviewed card
        deck_id: Unique identifier of the deck containing the card
        is_correct: True if the answer was correct (Good/Easy), False otherwise
        ease: The ease button pressed (1=Again, 2=Hard, 3=Good, 4=Easy)
        timestamp: When the review occurred
        interval: The interval until next review
        next_review: When the next review is scheduled
        repetitions: Number of times this card has been reviewed
        lapses: Number of times the card was forgotten
        quality: Quality rating of the response
        user_id: Optional user identifier
        review_id: Optional unique review identifier
        notes: Optional notes about the review
    """
    card_id: str
    deck_id: str
    is_correct: bool
    ease: int
    timestamp: datetime
    interval: int
    next_review: datetime
    repetitions: int
    lapses: int
    quality: int
    user_id: Optional[str] = None
    review_id: Optional[str] = None
    notes: Optional[str] = None


@dataclass
class ProgressionState:
    """Current state of user progression.
    
    Tracks all progression-related data across all decks and themes.
    This is the unified progression system that persists between sessions.
    
    Attributes:
        user_id: Unique identifier for the user
        level: Current player level
        experience_points: Total experience points earned
        coins_collected: Total coins collected
        achievements_unlocked: List of unlocked achievement IDs
        last_updated: When the state was last updated
        total_points: Total points earned across all decks and themes
        total_cards_reviewed: Total number of cards reviewed
        correct_answers: Total number of correct answers
        incorrect_answers: Total number of incorrect answers
        current_streak: Current consecutive correct answers
        highest_streak: Highest streak ever achieved (alias for best_streak)
        best_streak: Best streak ever achieved
        levels_completed: Number of levels completed
        levels_unlocked: Number of levels unlocked (1 per 50 correct answers)
        sessions_played: Total number of sessions played
        session_accuracy: Accuracy in the current session (0.0 to 1.0)
        session_health: Current health in session (0 to 100), resets each session
    """
    user_id: str = ""
    level: int = 1
    experience_points: int = 0
    coins_collected: int = 0
    achievements_unlocked: List[str] = field(default_factory=list)
    last_updated: datetime = field(default_factory=datetime.utcnow)
    total_points: int = 0
    total_cards_reviewed: int = 0
    correct_answers: int = 0
    incorrect_answers: int = 0
    current_streak: int = 0
    highest_streak: int = 0
    best_streak: int = 0
    levels_completed: int = 0
    levels_unlocked: int = 0
    sessions_played: int = 0
    session_accuracy: float = 0.0
    session_health: int = 0


@dataclass
class ScoreResult:
    """Result of score calculation.
    
    Contains the breakdown of points earned from a single review,
    including base points, multipliers, and bonuses.
    
    Attributes:
        base_points: Base points before multipliers
        multiplier: Combo multiplier applied (1.0, 1.5, 2.0, or 3.0)
        bonus_points: Additional bonus points (e.g., accuracy bonus)
        total_points: Final total points earned
        streak_broken: True if this review broke the streak
    """
    base_points: int
    multiplier: float
    bonus_points: int
    total_points: int
    streak_broken: bool


@dataclass
class PenaltyResult:
    """Result of penalty calculation.
    
    Contains the penalties applied for a wrong answer.
    
    Attributes:
        health_reduction: Amount to reduce health (0.0 to 1.0)
        currency_lost: Amount of currency lost
        streak_lost: The streak count that was lost
    """
    health_reduction: float
    currency_lost: int
    streak_lost: int


@dataclass
class Achievement:
    """Represents an achievement.
    
    Achievements are milestones that users can unlock by reaching
    certain goals (cards reviewed, streaks, accuracy, etc.).
    
    Attributes:
        id: Unique identifier for the achievement
        name: Display name of the achievement
        description: Description of how to unlock the achievement
        icon: Path or identifier for the achievement icon
        reward_currency: Currency awarded when unlocked
        unlocked: Whether the achievement has been unlocked
        unlock_date: When the achievement was unlocked (None if not unlocked)
        progress: Current progress toward the achievement (optional)
        target: Target value to unlock the achievement (optional)
    """
    id: str
    name: str
    description: str
    icon: str
    reward_currency: int
    unlocked: bool = False
    unlock_date: Optional[datetime] = None
    progress: int = 0
    target: int = 0


@dataclass
class AchievementProgress:
    """Progress toward a specific achievement.
    
    Attributes:
        achievement_id: ID of the achievement
        current: Current progress value
        target: Target value to unlock
        percentage: Percentage complete (0.0 to 1.0)
    """
    achievement_id: str
    current: int
    target: int
    percentage: float



@dataclass
class PowerUp:
    """Represents a power-up in the user's inventory.
    
    Power-ups provide temporary or permanent bonuses during gameplay.
    They are earned through correct answers or purchased with currency.
    
    Attributes:
        id: Unique identifier for this power-up instance
        type: The type of power-up
        theme: The theme this power-up belongs to (None for universal)
        name: Display name of the power-up
        description: Description of the power-up's effect
        icon: Path or identifier for the power-up icon
        quantity: Number of this power-up in inventory
        duration_seconds: Duration of effect when activated (0 for instant/permanent)
        acquired_at: When the power-up was acquired
    """
    id: str
    type: PowerUpType
    theme: Optional[Theme]
    name: str
    description: str
    icon: str
    quantity: int = 1
    duration_seconds: int = 0
    acquired_at: Optional[datetime] = None


@dataclass
class ActivePowerUp:
    """Represents an active power-up with remaining duration.
    
    Attributes:
        powerup_id: ID of the power-up that was activated
        powerup: Reference to the PowerUp
        activated_at: When the power-up was activated
        duration_seconds: Total duration of the effect
        remaining_seconds: Remaining time for the effect
    """
    powerup_id: str
    powerup: PowerUp
    activated_at: datetime
    duration_seconds: int
    remaining_seconds: float


@dataclass
class Level:
    """Represents a playable level.
    
    Levels are unlocked by earning correct answers (1 per 50 correct).
    Each theme has its own set of levels with unique designs.
    
    Attributes:
        id: Unique identifier for the level
        theme: The theme this level belongs to
        level_number: The level number within the theme
        name: Display name of the level
        description: Description of the level
        unlocked: Whether the level has been unlocked
        completed: Whether the level has been completed
        best_accuracy: Best accuracy achieved on this level (0.0 to 1.0)
        completion_date: When the level was first completed
        rewards_claimed: Whether completion rewards have been claimed
    """
    id: str
    theme: Theme
    level_number: int
    name: str
    description: str = ""
    unlocked: bool = False
    completed: bool = False
    best_accuracy: Optional[float] = None
    completion_date: Optional[datetime] = None
    rewards_claimed: bool = False


@dataclass
class LevelReward:
    """Rewards earned from completing a level.
    
    Attributes:
        level_id: ID of the completed level
        currency_earned: Currency awarded
        powerup_earned: Power-up awarded (if any)
        achievement_unlocked: Achievement unlocked (if any)
    """
    level_id: str
    currency_earned: int
    powerup_earned: Optional[PowerUp] = None
    achievement_unlocked: Optional[Achievement] = None


@dataclass
class LevelProgress:
    """Overall level progress statistics.
    
    Attributes:
        total_levels: Total number of levels available
        levels_unlocked: Number of levels unlocked
        levels_completed: Number of levels completed
        completion_percentage: Percentage of levels completed
    """
    total_levels: int
    levels_unlocked: int
    levels_completed: int
    completion_percentage: float



@dataclass
class Collectible:
    """Represents a collectible item (cosmetic, character, or item).
    
    Collectibles can be earned through gameplay or purchased with currency.
    
    Attributes:
        id: Unique identifier for the collectible
        type: Type of collectible (cosmetic, character, item)
        theme: Theme this collectible belongs to (None for universal)
        name: Display name of the collectible
        description: Description of the collectible
        icon: Path or identifier for the collectible icon
        owned: Whether the user owns this collectible
        equipped: Whether the collectible is currently equipped
        acquired_at: When the collectible was acquired
        price: Price in currency to purchase (0 if not purchasable)
    """
    id: str
    type: CollectibleType
    theme: Optional[Theme]
    name: str
    description: str
    icon: str
    owned: bool = False
    equipped: bool = False
    acquired_at: Optional[datetime] = None
    price: int = 0


@dataclass
class Cosmetic(Collectible):
    """A cosmetic collectible with no gameplay effect.
    
    Cosmetics are visual customizations that don't affect gameplay.
    """
    pass


@dataclass
class ShopItem:
    """An item available for purchase in the shop.
    
    Attributes:
        id: Unique identifier for the shop item
        name: Display name of the item
        description: Description of the item
        icon: Path or identifier for the item icon
        price: Price in currency
        item_type: Type of item (character, cosmetic, powerup)
        owned: Whether the user already owns this item
    """
    id: str
    name: str
    description: str
    icon: str
    price: int
    item_type: str
    owned: bool = False


@dataclass
class ThemeState:
    """Theme-specific state data.
    
    Each theme tracks its own specific data (coins, bananas, hearts, etc.).
    
    Attributes:
        theme: The theme this state belongs to
        coins: Coins collected (Mario theme)
        bananas: Bananas collected (DKC theme)
        hearts: Hearts/health (Zelda theme)
        map_progress: JSON-serializable map progress data
        extra_data: Additional theme-specific data
    """
    theme: Theme
    coins: int = 0
    bananas: int = 0
    hearts: int = 3
    map_progress: Optional[Dict] = None
    extra_data: Optional[Dict] = None


@dataclass
class ThemeStats:
    """Theme-specific statistics for dashboard display.
    
    Attributes:
        theme: The theme these stats belong to
        primary_collectible_name: Name of the primary collectible (coins/bananas/etc)
        primary_collectible_count: Count of primary collectible
        secondary_stat_name: Name of secondary stat (if any)
        secondary_stat_value: Value of secondary stat
        completion_percentage: Theme-specific completion percentage
    """
    theme: Theme
    primary_collectible_name: str
    primary_collectible_count: int
    secondary_stat_name: Optional[str] = None
    secondary_stat_value: Optional[int] = None
    completion_percentage: float = 0.0



@dataclass
class GameConfig:
    """User-configurable game settings.
    
    Contains all settings that users can customize to adjust difficulty,
    rewards, animations, and accessibility options.
    
    Attributes:
        base_points: Base points awarded for correct answers (default: 10)
        penalty_health_reduction: Health reduction for wrong answers (default: 0.1)
        penalty_currency_loss: Currency lost for wrong answers (default: 1)
        streak_multiplier_5: Multiplier at 5+ streak (default: 1.5)
        streak_multiplier_10: Multiplier at 10+ streak (default: 2.0)
        streak_multiplier_20: Multiplier at 20+ streak (default: 3.0)
        accuracy_bonus_threshold: Accuracy threshold for bonus (default: 0.9)
        accuracy_bonus_multiplier: Bonus multiplier for high accuracy (default: 1.25)
        cards_per_level: Correct answers needed to unlock a level (default: 50)
        cards_per_powerup: Correct answers needed to earn a power-up (default: 100)
        animation_speed: Animation speed multiplier (default: 1.0)
        animations_enabled: Whether animations are enabled (default: True)
        colorblind_mode: Colorblind mode setting (default: None)
        sound_enabled: Whether sound effects are enabled (default: True)
        sound_volume: Sound volume level 0.0-1.0 (default: 0.7)
    """
    # Difficulty settings
    base_points: int = 10
    penalty_health_reduction: float = 0.1
    penalty_currency_loss: int = 1
    
    # Reward settings
    streak_multiplier_5: float = 1.5
    streak_multiplier_10: float = 2.0
    streak_multiplier_20: float = 3.0
    accuracy_bonus_threshold: float = 0.9
    accuracy_bonus_multiplier: float = 1.25
    
    # Unlock settings
    cards_per_level: int = 50
    cards_per_powerup: int = 100
    
    # Animation settings
    animation_speed: float = 1.0
    animations_enabled: bool = True
    
    # Accessibility settings
    colorblind_mode: Optional[str] = None  # "deuteranopia", "protanopia", "tritanopia"
    sound_enabled: bool = True
    sound_volume: float = 0.7


@dataclass
class GameState:
    """Complete game state for persistence.
    
    This dataclass represents the entire game state that needs to be
    persisted to the database. It includes all progression data,
    achievements, power-ups, levels, and theme-specific state.
    
    Attributes:
        progression: Current progression state
        achievements: List of all achievements with their status
        powerups: List of power-ups in inventory
        levels: List of all levels with their status
        currency: Current currency balance
        cosmetics: List of owned cosmetics
        theme: Currently selected theme
        theme_specific: Theme-specific state for each theme
    """
    progression: ProgressionState
    achievements: List[Achievement] = field(default_factory=list)
    powerups: List[PowerUp] = field(default_factory=list)
    levels: List[Level] = field(default_factory=list)
    currency: int = 0
    cosmetics: List[Cosmetic] = field(default_factory=list)
    theme: Theme = Theme.MARIO
    theme_specific: Dict[Theme, ThemeState] = field(default_factory=dict)
    
    def __post_init__(self):
        """Initialize theme-specific state for all themes if not provided."""
        for t in Theme:
            if t not in self.theme_specific:
                self.theme_specific[t] = ThemeState(theme=t)


@dataclass
class Animation:
    """Represents an animation to be played.
    
    Attributes:
        type: Type of animation
        theme: Theme the animation belongs to
        sprite_sheet: Path to the sprite sheet
        frames: List of frame indices
        fps: Frames per second
        loop: Whether the animation should loop
    """
    type: AnimationType
    theme: Theme
    sprite_sheet: str
    frames: List[int] = field(default_factory=list)
    fps: int = 30
    loop: bool = False


@dataclass
class LevelView:
    """Visual representation of a level.
    
    Attributes:
        level: The level being displayed
        background: Path to background image
        character_position: Current character position (x, y)
        collectibles_visible: List of visible collectibles
    """
    level: Level
    background: str
    character_position: tuple = (0, 0)
    collectibles_visible: List[Collectible] = field(default_factory=list)
