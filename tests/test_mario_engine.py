"""
Unit tests for MarioEngine.

Tests the MarioEngine class functionality including:
- Animation generation for correct/wrong answers
- Collectible generation
- Accuracy-based power-up rewards
- Level selection view
- Dashboard stats

Requirements: 4.1, 4.2, 4.3, 4.4, 4.5, 4.6, 4.7, 4.8
"""

import pytest
from datetime import datetime

from themes.mario_engine import MarioEngine, MarioPowerUp, LevelSelectionView
from core.theme_manager import ThemeEngine
from data.data_manager import DataManager
from data.models import (
    Animation,
    AnimationType,
    Collectible,
    CollectibleType,
    Level,
    LevelView,
    PowerUp,
    PowerUpType,
    Theme,
    ThemeStats,
)


@pytest.fixture
def temp_db_path(tmp_path):
    """Create a temporary database path for testing."""
    return tmp_path / "test_nintendanki.db"


@pytest.fixture
def data_manager(temp_db_path):
    """Create a DataManager with a temporary database."""
    dm = DataManager(temp_db_path)
    dm.initialize_database()
    return dm


@pytest.fixture
def mario_engine(data_manager):
    """Create a MarioEngine for testing."""
    return MarioEngine(data_manager)


class TestMarioEngineInitialization:
    """Tests for MarioEngine initialization."""
    
    def test_mario_engine_is_theme_engine(self, mario_engine):
        """Test that MarioEngine is a ThemeEngine subclass."""
        assert isinstance(mario_engine, ThemeEngine)
    
    def test_mario_engine_initializes_with_data_manager(self, data_manager):
        """Test that MarioEngine initializes with a DataManager."""
        engine = MarioEngine(data_manager)
        assert engine.data_manager is data_manager
    
    def test_mario_engine_loads_coin_count(self, data_manager):
        """Test that MarioEngine loads coin count from database."""
        # Set up coins in database
        state = data_manager.load_state()
        state.theme_specific[Theme.MARIO].coins = 100
        data_manager.save_state(state)
        
        # Create engine - should load coins
        engine = MarioEngine(data_manager)
        assert engine.get_coin_count() == 100


class TestGetAnimationForCorrect:
    """Tests for get_animation_for_correct method.
    
    Requirements: 4.2, 4.7
    """
    
    def test_returns_animation(self, mario_engine):
        """Test that get_animation_for_correct returns an Animation."""
        animation = mario_engine.get_animation_for_correct()
        assert isinstance(animation, Animation)
    
    def test_animation_type_is_collect(self, mario_engine):
        """Test that animation type is COLLECT for coin collection."""
        animation = mario_engine.get_animation_for_correct()
        assert animation.type == AnimationType.COLLECT
    
    def test_animation_theme_is_mario(self, mario_engine):
        """Test that animation theme is MARIO."""
        animation = mario_engine.get_animation_for_correct()
        assert animation.theme == Theme.MARIO
    
    def test_animation_has_sprite_sheet(self, mario_engine):
        """Test that animation has a sprite sheet path."""
        animation = mario_engine.get_animation_for_correct()
        assert animation.sprite_sheet is not None
        assert "mario" in animation.sprite_sheet.lower()
    
    def test_animation_has_frames(self, mario_engine):
        """Test that animation has frame data."""
        animation = mario_engine.get_animation_for_correct()
        assert len(animation.frames) > 0
    
    def test_animation_fps_is_valid(self, mario_engine):
        """Test that animation FPS is at least 30 (Requirement 9.2)."""
        animation = mario_engine.get_animation_for_correct()
        assert animation.fps >= 30


class TestGetAnimationForWrong:
    """Tests for get_animation_for_wrong method.
    
    Requirements: 4.3, 4.7
    """
    
    def test_returns_animation(self, mario_engine):
        """Test that get_animation_for_wrong returns an Animation."""
        animation = mario_engine.get_animation_for_wrong()
        assert isinstance(animation, Animation)
    
    def test_animation_type_is_damage(self, mario_engine):
        """Test that animation type is DAMAGE."""
        animation = mario_engine.get_animation_for_wrong()
        assert animation.type == AnimationType.DAMAGE
    
    def test_animation_theme_is_mario(self, mario_engine):
        """Test that animation theme is MARIO."""
        animation = mario_engine.get_animation_for_wrong()
        assert animation.theme == Theme.MARIO
    
    def test_animation_has_sprite_sheet(self, mario_engine):
        """Test that animation has a sprite sheet path."""
        animation = mario_engine.get_animation_for_wrong()
        assert animation.sprite_sheet is not None
        assert "mario" in animation.sprite_sheet.lower()
    
    def test_animation_has_frames(self, mario_engine):
        """Test that animation has frame data."""
        animation = mario_engine.get_animation_for_wrong()
        assert len(animation.frames) > 0


class TestGetCollectibleForCorrect:
    """Tests for get_collectible_for_correct method.
    
    Requirements: 4.2
    """
    
    def test_returns_collectible(self, mario_engine):
        """Test that get_collectible_for_correct returns a Collectible."""
        collectible = mario_engine.get_collectible_for_correct()
        assert isinstance(collectible, Collectible)
    
    def test_collectible_is_coin(self, mario_engine):
        """Test that collectible is a coin."""
        collectible = mario_engine.get_collectible_for_correct()
        assert collectible.type == CollectibleType.COIN
    
    def test_collectible_theme_is_mario(self, mario_engine):
        """Test that collectible theme is MARIO."""
        collectible = mario_engine.get_collectible_for_correct()
        assert collectible.theme == Theme.MARIO
    
    def test_collectible_is_owned(self, mario_engine):
        """Test that collectible is marked as owned."""
        collectible = mario_engine.get_collectible_for_correct()
        assert collectible.owned is True


class TestGetPowerupForAccuracy:
    """Tests for get_powerup_for_accuracy method.
    
    Requirements: 4.4, 4.5, 4.6
    """
    
    def test_no_powerup_below_95_percent(self, mario_engine):
        """Test that no power-up is awarded below 95% accuracy."""
        assert mario_engine.get_powerup_for_accuracy(0.0) is None
        assert mario_engine.get_powerup_for_accuracy(0.5) is None
        assert mario_engine.get_powerup_for_accuracy(0.94) is None
        assert mario_engine.get_powerup_for_accuracy(0.949) is None
    
    def test_mushroom_at_95_percent(self, mario_engine):
        """Test that mushroom is awarded at exactly 95% accuracy.
        
        Requirements: 4.4
        """
        result = mario_engine.get_powerup_for_accuracy(0.95)
        
        assert result is not None
        assert isinstance(result, MarioPowerUp)
        assert result.powerup.type == PowerUpType.MUSHROOM
        assert result.accuracy_threshold == 0.95
    
    def test_mushroom_between_95_and_98_percent(self, mario_engine):
        """Test that mushroom is awarded between 95% and 98% accuracy.
        
        Requirements: 4.4
        """
        result = mario_engine.get_powerup_for_accuracy(0.96)
        assert result.powerup.type == PowerUpType.MUSHROOM
        
        result = mario_engine.get_powerup_for_accuracy(0.97)
        assert result.powerup.type == PowerUpType.MUSHROOM
        
        result = mario_engine.get_powerup_for_accuracy(0.979)
        assert result.powerup.type == PowerUpType.MUSHROOM
    
    def test_fire_flower_at_98_percent(self, mario_engine):
        """Test that fire flower is awarded at exactly 98% accuracy.
        
        Requirements: 4.5
        """
        result = mario_engine.get_powerup_for_accuracy(0.98)
        
        assert result is not None
        assert isinstance(result, MarioPowerUp)
        assert result.powerup.type == PowerUpType.FIRE_FLOWER
        assert result.accuracy_threshold == 0.98
    
    def test_fire_flower_between_98_and_100_percent(self, mario_engine):
        """Test that fire flower is awarded between 98% and 100% accuracy.
        
        Requirements: 4.5
        """
        result = mario_engine.get_powerup_for_accuracy(0.99)
        assert result.powerup.type == PowerUpType.FIRE_FLOWER
        
        result = mario_engine.get_powerup_for_accuracy(0.999)
        assert result.powerup.type == PowerUpType.FIRE_FLOWER
    
    def test_star_at_100_percent(self, mario_engine):
        """Test that star is awarded at exactly 100% accuracy.
        
        Requirements: 4.6
        """
        result = mario_engine.get_powerup_for_accuracy(1.0)
        
        assert result is not None
        assert isinstance(result, MarioPowerUp)
        assert result.powerup.type == PowerUpType.STAR
        assert result.accuracy_threshold == 1.0
    
    def test_invalid_accuracy_returns_none(self, mario_engine):
        """Test that invalid accuracy values return None."""
        assert mario_engine.get_powerup_for_accuracy(-0.1) is None
        assert mario_engine.get_powerup_for_accuracy(1.1) is None
        assert mario_engine.get_powerup_for_accuracy(2.0) is None
    
    def test_powerup_has_correct_theme(self, mario_engine):
        """Test that all power-ups have Mario theme."""
        for accuracy in [0.95, 0.98, 1.0]:
            result = mario_engine.get_powerup_for_accuracy(accuracy)
            assert result.powerup.theme == Theme.MARIO
    
    def test_powerup_has_description(self, mario_engine):
        """Test that all power-ups have descriptions."""
        for accuracy in [0.95, 0.98, 1.0]:
            result = mario_engine.get_powerup_for_accuracy(accuracy)
            assert result.powerup.description is not None
            assert len(result.powerup.description) > 0
            assert result.effect_description is not None
            assert len(result.effect_description) > 0


class TestGetLevelSelectionView:
    """Tests for get_level_selection_view method.
    
    Requirements: 4.8
    """
    
    def test_returns_level_selection_view(self, mario_engine):
        """Test that get_level_selection_view returns a LevelSelectionView."""
        view = mario_engine.get_level_selection_view()
        assert isinstance(view, LevelSelectionView)
    
    def test_view_has_levels_list(self, mario_engine):
        """Test that view has a levels list."""
        view = mario_engine.get_level_selection_view()
        assert isinstance(view.levels, list)
    
    def test_view_has_world_name(self, mario_engine):
        """Test that view has a world name."""
        view = mario_engine.get_level_selection_view()
        assert view.world_name is not None
        assert "World" in view.world_name
    
    def test_view_has_background(self, mario_engine):
        """Test that view has a background image path."""
        view = mario_engine.get_level_selection_view()
        assert view.background is not None
        assert "mario" in view.background.lower()
    
    def test_view_with_unlocked_levels(self, data_manager):
        """Test view shows unlocked levels correctly."""
        # Add some Mario levels
        state = data_manager.load_state()
        state.levels = [
            Level(id="mario_1", theme=Theme.MARIO, level_number=1, name="Level 1-1", unlocked=True, completed=True),
            Level(id="mario_2", theme=Theme.MARIO, level_number=2, name="Level 1-2", unlocked=True, completed=False),
            Level(id="mario_3", theme=Theme.MARIO, level_number=3, name="Level 1-3", unlocked=False, completed=False),
        ]
        data_manager.save_state(state)
        
        engine = MarioEngine(data_manager)
        view = engine.get_level_selection_view()
        
        assert len(view.levels) == 3
        # Current level should be the first unlocked but not completed
        assert view.current_level is not None
        assert view.current_level.id == "mario_2"
    
    def test_view_only_shows_mario_levels(self, data_manager):
        """Test that view only shows Mario theme levels."""
        # Add levels from different themes
        state = data_manager.load_state()
        state.levels = [
            Level(id="mario_1", theme=Theme.MARIO, level_number=1, name="Mario Level", unlocked=True),
            Level(id="zelda_1", theme=Theme.ZELDA, level_number=1, name="Zelda Level", unlocked=True),
            Level(id="dkc_1", theme=Theme.DKC, level_number=1, name="DKC Level", unlocked=True),
        ]
        data_manager.save_state(state)
        
        engine = MarioEngine(data_manager)
        view = engine.get_level_selection_view()
        
        assert len(view.levels) == 1
        assert all(l.theme == Theme.MARIO for l in view.levels)
    
    def test_view_levels_sorted_by_number(self, data_manager):
        """Test that levels are sorted by level number."""
        state = data_manager.load_state()
        state.levels = [
            Level(id="mario_3", theme=Theme.MARIO, level_number=3, name="Level 3", unlocked=True),
            Level(id="mario_1", theme=Theme.MARIO, level_number=1, name="Level 1", unlocked=True),
            Level(id="mario_2", theme=Theme.MARIO, level_number=2, name="Level 2", unlocked=True),
        ]
        data_manager.save_state(state)
        
        engine = MarioEngine(data_manager)
        view = engine.get_level_selection_view()
        
        assert view.levels[0].level_number == 1
        assert view.levels[1].level_number == 2
        assert view.levels[2].level_number == 3
    
    def test_view_has_level_positions(self, data_manager):
        """Test that view has positions for each level."""
        state = data_manager.load_state()
        state.levels = [
            Level(id="mario_1", theme=Theme.MARIO, level_number=1, name="Level 1", unlocked=True),
            Level(id="mario_2", theme=Theme.MARIO, level_number=2, name="Level 2", unlocked=True),
        ]
        data_manager.save_state(state)
        
        engine = MarioEngine(data_manager)
        view = engine.get_level_selection_view()
        
        assert len(view.level_positions) == 2
        assert "mario_1" in view.level_positions
        assert "mario_2" in view.level_positions


class TestGetLevelView:
    """Tests for get_level_view method.
    
    Requirements: 4.1
    """
    
    def test_returns_level_view(self, mario_engine):
        """Test that get_level_view returns a LevelView."""
        level = Level(id="test_level", theme=Theme.MARIO, level_number=1, name="Test Level")
        view = mario_engine.get_level_view(level)
        assert isinstance(view, LevelView)
    
    def test_level_view_has_background(self, mario_engine):
        """Test that level view has a background image."""
        level = Level(id="test_level", theme=Theme.MARIO, level_number=1, name="Test Level")
        view = mario_engine.get_level_view(level)
        assert view.background is not None
        assert "mario" in view.background.lower()
    
    def test_level_view_has_character_position(self, mario_engine):
        """Test that level view has a character starting position."""
        level = Level(id="test_level", theme=Theme.MARIO, level_number=1, name="Test Level")
        view = mario_engine.get_level_view(level)
        assert view.character_position is not None
        assert len(view.character_position) == 2
    
    def test_level_view_has_collectibles(self, mario_engine):
        """Test that level view has collectibles."""
        level = Level(id="test_level", theme=Theme.MARIO, level_number=1, name="Test Level")
        view = mario_engine.get_level_view(level)
        assert isinstance(view.collectibles_visible, list)
        assert len(view.collectibles_visible) > 0
    
    def test_higher_levels_have_more_collectibles(self, mario_engine):
        """Test that higher level numbers have more collectibles."""
        level1 = Level(id="level_1", theme=Theme.MARIO, level_number=1, name="Level 1")
        level5 = Level(id="level_5", theme=Theme.MARIO, level_number=5, name="Level 5")
        
        view1 = mario_engine.get_level_view(level1)
        view5 = mario_engine.get_level_view(level5)
        
        assert len(view5.collectibles_visible) > len(view1.collectibles_visible)


class TestGetDashboardStats:
    """Tests for get_dashboard_stats method."""
    
    def test_returns_theme_stats(self, mario_engine):
        """Test that get_dashboard_stats returns ThemeStats."""
        stats = mario_engine.get_dashboard_stats()
        assert isinstance(stats, ThemeStats)
    
    def test_stats_theme_is_mario(self, mario_engine):
        """Test that stats theme is MARIO."""
        stats = mario_engine.get_dashboard_stats()
        assert stats.theme == Theme.MARIO
    
    def test_stats_primary_collectible_is_coins(self, mario_engine):
        """Test that primary collectible is coins."""
        stats = mario_engine.get_dashboard_stats()
        assert stats.primary_collectible_name == "Coins"
    
    def test_stats_secondary_stat_is_stars(self, mario_engine):
        """Test that secondary stat is stars."""
        stats = mario_engine.get_dashboard_stats()
        assert stats.secondary_stat_name == "Stars"
    
    def test_stats_reflects_coin_count(self, data_manager):
        """Test that stats reflects actual coin count."""
        state = data_manager.load_state()
        state.theme_specific[Theme.MARIO].coins = 42
        data_manager.save_state(state)
        
        engine = MarioEngine(data_manager)
        stats = engine.get_dashboard_stats()
        
        assert stats.primary_collectible_count == 42
    
    def test_stats_reflects_star_count(self, data_manager):
        """Test that stats reflects star power-ups earned."""
        state = data_manager.load_state()
        state.powerups = [
            PowerUp(
                id="star_1",
                type=PowerUpType.STAR,
                theme=Theme.MARIO,
                name="Star",
                description="A star",
                icon="star.png",
                quantity=3
            )
        ]
        data_manager.save_state(state)
        
        engine = MarioEngine(data_manager)
        stats = engine.get_dashboard_stats()
        
        assert stats.secondary_stat_value == 3


class TestSpriteAnimations:
    """Tests for sprite animation methods.
    
    Requirements: 4.7
    """
    
    def test_get_run_animation(self, mario_engine):
        """Test get_run_animation returns valid animation."""
        animation = mario_engine.get_run_animation()
        
        assert isinstance(animation, Animation)
        assert animation.type == AnimationType.RUN
        assert animation.theme == Theme.MARIO
        assert animation.loop is True  # Running should loop
    
    def test_get_jump_animation(self, mario_engine):
        """Test get_jump_animation returns valid animation."""
        animation = mario_engine.get_jump_animation()
        
        assert isinstance(animation, Animation)
        assert animation.type == AnimationType.JUMP
        assert animation.theme == Theme.MARIO
        assert animation.loop is False  # Jump should not loop
    
    def test_get_idle_animation(self, mario_engine):
        """Test get_idle_animation returns valid animation."""
        animation = mario_engine.get_idle_animation()
        
        assert isinstance(animation, Animation)
        assert animation.type == AnimationType.IDLE
        assert animation.theme == Theme.MARIO
        assert animation.loop is True  # Idle should loop


class TestCoinManagement:
    """Tests for coin management methods."""
    
    def test_add_coin_increments_count(self, mario_engine):
        """Test that add_coin increments the coin count."""
        initial = mario_engine.get_coin_count()
        mario_engine.add_coin()
        assert mario_engine.get_coin_count() == initial + 1
    
    def test_add_coin_persists_to_database(self, data_manager):
        """Test that add_coin persists to database."""
        engine = MarioEngine(data_manager)
        engine.add_coin()
        engine.add_coin()
        
        # Create new engine to verify persistence
        engine2 = MarioEngine(data_manager)
        assert engine2.get_coin_count() == 2
    
    def test_add_coin_returns_new_count(self, mario_engine):
        """Test that add_coin returns the new count."""
        initial = mario_engine.get_coin_count()
        new_count = mario_engine.add_coin()
        assert new_count == initial + 1


class TestMarioPowerUpDataclass:
    """Tests for MarioPowerUp dataclass."""
    
    def test_mario_powerup_has_powerup(self, mario_engine):
        """Test that MarioPowerUp contains a PowerUp."""
        result = mario_engine.get_powerup_for_accuracy(0.95)
        assert isinstance(result.powerup, PowerUp)
    
    def test_mario_powerup_has_threshold(self, mario_engine):
        """Test that MarioPowerUp has accuracy threshold."""
        result = mario_engine.get_powerup_for_accuracy(0.95)
        assert result.accuracy_threshold == 0.95
    
    def test_mario_powerup_has_effect_description(self, mario_engine):
        """Test that MarioPowerUp has effect description."""
        result = mario_engine.get_powerup_for_accuracy(0.95)
        assert result.effect_description is not None
        assert "95%" in result.effect_description


class TestLevelSelectionViewDataclass:
    """Tests for LevelSelectionView dataclass."""
    
    def test_level_selection_view_defaults(self):
        """Test LevelSelectionView default values."""
        view = LevelSelectionView(levels=[])
        
        assert view.levels == []
        assert view.current_level is None
        assert view.world_name == "World 1"
        assert "level_select" in view.background
        assert view.level_positions == {}
