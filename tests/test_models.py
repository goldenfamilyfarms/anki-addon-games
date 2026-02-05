"""
Unit tests for data models.

Tests the basic functionality of all data models and enums defined in data/models.py.
"""

import pytest
from datetime import datetime
from data import (
    Theme,
    PowerUpType,
    CollectibleType,
    AnimationType,
    ReviewResult,
    ProgressionState,
    ScoreResult,
    PenaltyResult,
    Achievement,
    AchievementProgress,
    PowerUp,
    ActivePowerUp,
    Level,
    LevelReward,
    LevelProgress,
    Collectible,
    Cosmetic,
    ShopItem,
    ThemeState,
    ThemeStats,
    GameConfig,
    GameState,
    Animation,
    LevelView,
)


class TestThemeEnum:
    """Tests for the Theme enum."""
    
    def test_theme_values(self):
        """Test that all theme values are correct."""
        assert Theme.MARIO.value == "mario"
        assert Theme.ZELDA.value == "zelda"
        assert Theme.DKC.value == "dkc"
    
    def test_theme_count(self):
        """Test that there are exactly 3 themes."""
        assert len(Theme) == 3


class TestPowerUpTypeEnum:
    """Tests for the PowerUpType enum."""
    
    def test_mario_powerups(self):
        """Test Mario-specific power-up types."""
        assert PowerUpType.MUSHROOM.value == "mushroom"
        assert PowerUpType.FIRE_FLOWER.value == "fire_flower"
        assert PowerUpType.STAR.value == "star"
    
    def test_zelda_powerups(self):
        """Test Zelda-specific power-up types."""
        assert PowerUpType.HEART_CONTAINER.value == "heart_container"
        assert PowerUpType.FAIRY.value == "fairy"
        assert PowerUpType.POTION.value == "potion"
    
    def test_dkc_powerups(self):
        """Test DKC-specific power-up types."""
        assert PowerUpType.BANANA.value == "banana"
        assert PowerUpType.BARREL.value == "barrel"
        assert PowerUpType.ANIMAL_BUDDY.value == "animal_buddy"
    
    def test_universal_powerups(self):
        """Test universal power-up types."""
        assert PowerUpType.DOUBLE_POINTS.value == "double_points"
        assert PowerUpType.SHIELD.value == "shield"
        assert PowerUpType.TIME_FREEZE.value == "time_freeze"


class TestReviewResult:
    """Tests for the ReviewResult dataclass."""
    
    def test_create_review_result(self):
        """Test creating a ReviewResult."""
        now = datetime.now()
        result = ReviewResult(
            card_id="123",
            deck_id="456",
            is_correct=True,
            ease=3,
            timestamp=now,
            interval=1,
            next_review=now,
            repetitions=1,
            lapses=0,
            quality=3
        )
        assert result.card_id == "123"
        assert result.deck_id == "456"
        assert result.is_correct is True
        assert result.ease == 3
        assert result.timestamp == now
    
    def test_review_result_wrong_answer(self):
        """Test ReviewResult for a wrong answer."""
        now = datetime.now()
        result = ReviewResult(
            card_id="1",
            deck_id="1",
            is_correct=False,
            ease=1,
            timestamp=now,
            interval=0,
            next_review=now,
            repetitions=1,
            lapses=1,
            quality=1
        )
        assert result.is_correct is False
        assert result.ease == 1


class TestProgressionState:
    """Tests for the ProgressionState dataclass."""
    
    def test_default_values(self):
        """Test default values for ProgressionState."""
        state = ProgressionState()
        assert state.total_points == 0
        assert state.total_cards_reviewed == 0
        assert state.correct_answers == 0
        assert state.current_streak == 0
        assert state.best_streak == 0
        assert state.levels_unlocked == 0
        assert state.levels_completed == 0
        assert state.session_accuracy == 0.0
        assert state.session_health == 0
    
    def test_custom_values(self):
        """Test creating ProgressionState with custom values."""
        state = ProgressionState(
            total_points=1000,
            total_cards_reviewed=100,
            correct_answers=90,
            current_streak=10,
            best_streak=25,
            levels_unlocked=2,
            levels_completed=1,
            session_accuracy=0.9,
            session_health=80
        )
        assert state.total_points == 1000
        assert state.correct_answers == 90
        assert state.current_streak == 10


class TestScoreResult:
    """Tests for the ScoreResult dataclass."""
    
    def test_create_score_result(self):
        """Test creating a ScoreResult."""
        result = ScoreResult(
            base_points=10,
            multiplier=1.5,
            bonus_points=5,
            total_points=20,
            streak_broken=False
        )
        assert result.base_points == 10
        assert result.multiplier == 1.5
        assert result.bonus_points == 5
        assert result.total_points == 20
        assert result.streak_broken is False


class TestPenaltyResult:
    """Tests for the PenaltyResult dataclass."""
    
    def test_create_penalty_result(self):
        """Test creating a PenaltyResult."""
        result = PenaltyResult(
            health_reduction=0.1,
            currency_lost=1,
            streak_lost=5
        )
        assert result.health_reduction == 0.1
        assert result.currency_lost == 1
        assert result.streak_lost == 5


class TestAchievement:
    """Tests for the Achievement dataclass."""
    
    def test_create_achievement(self):
        """Test creating an Achievement."""
        achievement = Achievement(
            id="first_100",
            name="Century",
            description="Review 100 cards",
            icon="trophy.png",
            reward_currency=50
        )
        assert achievement.id == "first_100"
        assert achievement.name == "Century"
        assert achievement.unlocked is False
        assert achievement.unlock_date is None
    
    def test_unlocked_achievement(self):
        """Test an unlocked Achievement."""
        now = datetime.now()
        achievement = Achievement(
            id="streak_10",
            name="On Fire",
            description="Get a 10 streak",
            icon="fire.png",
            reward_currency=25,
            unlocked=True,
            unlock_date=now
        )
        assert achievement.unlocked is True
        assert achievement.unlock_date == now


class TestPowerUp:
    """Tests for the PowerUp dataclass."""
    
    def test_create_powerup(self):
        """Test creating a PowerUp."""
        powerup = PowerUp(
            id="mushroom_1",
            type=PowerUpType.MUSHROOM,
            theme=Theme.MARIO,
            name="Super Mushroom",
            description="Grow bigger!",
            icon="mushroom.png"
        )
        assert powerup.id == "mushroom_1"
        assert powerup.type == PowerUpType.MUSHROOM
        assert powerup.theme == Theme.MARIO
        assert powerup.quantity == 1
    
    def test_universal_powerup(self):
        """Test creating a universal PowerUp."""
        powerup = PowerUp(
            id="double_points_1",
            type=PowerUpType.DOUBLE_POINTS,
            theme=None,
            name="Double Points",
            description="Double your points!",
            icon="2x.png",
            duration_seconds=60
        )
        assert powerup.theme is None
        assert powerup.duration_seconds == 60


class TestLevel:
    """Tests for the Level dataclass."""
    
    def test_create_level(self):
        """Test creating a Level."""
        level = Level(
            id="mario_1_1",
            theme=Theme.MARIO,
            level_number=1,
            name="World 1-1"
        )
        assert level.id == "mario_1_1"
        assert level.theme == Theme.MARIO
        assert level.level_number == 1
        assert level.unlocked is False
        assert level.completed is False
    
    def test_completed_level(self):
        """Test a completed Level."""
        now = datetime.now()
        level = Level(
            id="mario_1_1",
            theme=Theme.MARIO,
            level_number=1,
            name="World 1-1",
            unlocked=True,
            completed=True,
            best_accuracy=0.95,
            completion_date=now,
            rewards_claimed=True
        )
        assert level.unlocked is True
        assert level.completed is True
        assert level.best_accuracy == 0.95


class TestCollectible:
    """Tests for the Collectible dataclass."""
    
    def test_create_collectible(self):
        """Test creating a Collectible."""
        collectible = Collectible(
            id="mario_hat",
            type=CollectibleType.COSMETIC,
            theme=Theme.MARIO,
            name="Mario's Hat",
            description="The iconic red cap",
            icon="hat.png"
        )
        assert collectible.id == "mario_hat"
        assert collectible.type == CollectibleType.COSMETIC
        assert collectible.owned is False


class TestGameConfig:
    """Tests for the GameConfig dataclass."""
    
    def test_default_values(self):
        """Test default values for GameConfig."""
        config = GameConfig()
        assert config.base_points == 10
        assert config.penalty_health_reduction == 0.1
        assert config.penalty_currency_loss == 1
        assert config.streak_multiplier_5 == 1.5
        assert config.streak_multiplier_10 == 2.0
        assert config.streak_multiplier_20 == 3.0
        assert config.accuracy_bonus_threshold == 0.9
        assert config.accuracy_bonus_multiplier == 1.25
        assert config.cards_per_level == 50
        assert config.cards_per_powerup == 100
        assert config.animation_speed == 1.0
        assert config.animations_enabled is True
        assert config.colorblind_mode is None
        assert config.sound_enabled is True
        assert config.sound_volume == 0.7
    
    def test_custom_config(self):
        """Test GameConfig with custom values."""
        config = GameConfig(
            base_points=20,
            penalty_health_reduction=0.2,
            animations_enabled=False,
            colorblind_mode="deuteranopia"
        )
        assert config.base_points == 20
        assert config.penalty_health_reduction == 0.2
        assert config.animations_enabled is False
        assert config.colorblind_mode == "deuteranopia"


class TestGameState:
    """Tests for the GameState dataclass."""
    
    def test_default_game_state(self):
        """Test creating a GameState with defaults."""
        state = GameState(progression=ProgressionState())
        assert state.progression.total_points == 0
        assert state.currency == 0
        assert state.theme == Theme.MARIO
        assert len(state.achievements) == 0
        assert len(state.powerups) == 0
        assert len(state.levels) == 0
    
    def test_theme_specific_initialization(self):
        """Test that theme-specific state is initialized for all themes."""
        state = GameState(progression=ProgressionState())
        assert Theme.MARIO in state.theme_specific
        assert Theme.ZELDA in state.theme_specific
        assert Theme.DKC in state.theme_specific
    
    def test_game_state_with_data(self):
        """Test GameState with populated data."""
        achievement = Achievement(
            id="test",
            name="Test",
            description="Test achievement",
            icon="test.png",
            reward_currency=10
        )
        powerup = PowerUp(
            id="test_powerup",
            type=PowerUpType.MUSHROOM,
            theme=Theme.MARIO,
            name="Test",
            description="Test",
            icon="test.png"
        )
        state = GameState(
            progression=ProgressionState(total_points=100),
            achievements=[achievement],
            powerups=[powerup],
            currency=50,
            theme=Theme.ZELDA
        )
        assert state.progression.total_points == 100
        assert len(state.achievements) == 1
        assert len(state.powerups) == 1
        assert state.currency == 50
        assert state.theme == Theme.ZELDA


class TestThemeState:
    """Tests for the ThemeState dataclass."""
    
    def test_default_theme_state(self):
        """Test default ThemeState values."""
        state = ThemeState(theme=Theme.MARIO)
        assert state.theme == Theme.MARIO
        assert state.coins == 0
        assert state.bananas == 0
        assert state.hearts == 3
    
    def test_mario_theme_state(self):
        """Test ThemeState for Mario theme."""
        state = ThemeState(theme=Theme.MARIO, coins=100)
        assert state.coins == 100
    
    def test_dkc_theme_state(self):
        """Test ThemeState for DKC theme."""
        state = ThemeState(theme=Theme.DKC, bananas=500)
        assert state.bananas == 500


class TestAnimation:
    """Tests for the Animation dataclass."""
    
    def test_create_animation(self):
        """Test creating an Animation."""
        animation = Animation(
            type=AnimationType.COLLECT,
            theme=Theme.MARIO,
            sprite_sheet="mario_collect.png",
            frames=[0, 1, 2, 3],
            fps=30
        )
        assert animation.type == AnimationType.COLLECT
        assert animation.theme == Theme.MARIO
        assert len(animation.frames) == 4
        assert animation.fps == 30
        assert animation.loop is False
