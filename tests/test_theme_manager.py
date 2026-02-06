"""
Unit tests for ThemeManager.

Tests the ThemeManager class functionality including:
- Getting and setting the current theme
- Theme persistence to database
- Theme engine retrieval
- Theme switching preserves progression

Requirements: 1.1, 1.2, 1.3, 1.4, 1.5, 1.6
"""

import pytest
from unittest.mock import MagicMock

from core.theme_manager import ThemeManager, ThemeEngine, PlaceholderThemeEngine
from data.data_manager import DataManager
from data.models import (
    Theme,
    Animation,
    AnimationType,
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
def theme_manager(data_manager):
    """Create a ThemeManager for testing."""
    return ThemeManager(data_manager)


class TestThemeManagerInitialization:
    """Tests for ThemeManager initialization."""
    
    def test_init_loads_default_theme(self, data_manager):
        """Test that ThemeManager loads the default theme (Mario) on init."""
        tm = ThemeManager(data_manager)
        assert tm.get_current_theme() == Theme.MARIO
    
    def test_init_loads_persisted_theme(self, data_manager):
        """Test that ThemeManager loads a previously persisted theme."""
        # Set theme to Zelda and save
        state = data_manager.load_state()
        state.theme = Theme.ZELDA
        data_manager.save_state(state)
        
        # Create new ThemeManager - should load Zelda
        tm = ThemeManager(data_manager)
        assert tm.get_current_theme() == Theme.ZELDA
    
    def test_init_with_progression_system(self, data_manager):
        """Test initialization with a progression system reference."""
        mock_progression = MagicMock()
        tm = ThemeManager(data_manager, progression_system=mock_progression)
        
        assert tm._progression_system == mock_progression


class TestGetCurrentTheme:
    """Tests for get_current_theme method."""
    
    def test_get_current_theme_returns_mario_by_default(self, theme_manager):
        """Test that default theme is Mario."""
        assert theme_manager.get_current_theme() == Theme.MARIO
    
    def test_get_current_theme_after_set(self, theme_manager):
        """Test get_current_theme returns the theme that was set."""
        theme_manager.set_theme(Theme.ZELDA)
        assert theme_manager.get_current_theme() == Theme.ZELDA
        
        theme_manager.set_theme(Theme.DKC)
        assert theme_manager.get_current_theme() == Theme.DKC


class TestSetTheme:
    """Tests for set_theme method."""
    
    def test_set_theme_mario(self, theme_manager):
        """Test setting theme to Mario."""
        theme_manager.set_theme(Theme.MARIO)
        assert theme_manager.get_current_theme() == Theme.MARIO
    
    def test_set_theme_zelda(self, theme_manager):
        """Test setting theme to Zelda."""
        theme_manager.set_theme(Theme.ZELDA)
        assert theme_manager.get_current_theme() == Theme.ZELDA
    
    def test_set_theme_dkc(self, theme_manager):
        """Test setting theme to DKC."""
        theme_manager.set_theme(Theme.DKC)
        assert theme_manager.get_current_theme() == Theme.DKC
    
    def test_set_theme_persists_to_database(self, theme_manager, data_manager):
        """Test that set_theme persists the selection to database.
        
        Requirements: 1.5
        """
        theme_manager.set_theme(Theme.ZELDA)
        
        # Load state from database and verify theme
        state = data_manager.load_state()
        assert state.theme == Theme.ZELDA
    
    def test_set_theme_invalid_type_raises_error(self, theme_manager):
        """Test that setting an invalid theme type raises ValueError."""
        with pytest.raises(ValueError, match="Invalid theme"):
            theme_manager.set_theme("invalid")
    
    def test_set_theme_notifies_progression_system(self, data_manager):
        """Test that set_theme notifies the progression system."""
        mock_progression = MagicMock()
        tm = ThemeManager(data_manager, progression_system=mock_progression)
        
        tm.set_theme(Theme.DKC)
        
        mock_progression.set_current_theme.assert_called_with(Theme.DKC)


class TestThemePersistence:
    """Tests for theme persistence (round-trip).
    
    Requirements: 1.5, 1.6
    """
    
    def test_theme_persists_across_manager_instances(self, data_manager):
        """Test that theme selection persists across ThemeManager instances."""
        # Create first manager and set theme
        tm1 = ThemeManager(data_manager)
        tm1.set_theme(Theme.DKC)
        
        # Create second manager - should load persisted theme
        tm2 = ThemeManager(data_manager)
        assert tm2.get_current_theme() == Theme.DKC
    
    def test_all_themes_persist_correctly(self, data_manager):
        """Test that all themes can be persisted and restored."""
        for theme in [Theme.MARIO, Theme.ZELDA, Theme.DKC]:
            tm1 = ThemeManager(data_manager)
            tm1.set_theme(theme)
            
            tm2 = ThemeManager(data_manager)
            assert tm2.get_current_theme() == theme


class TestThemeSwitchingPreservesProgression:
    """Tests that theme switching preserves progression data.
    
    Requirements: 1.3
    """
    
    def test_theme_switch_preserves_total_points(self, data_manager):
        """Test that switching themes preserves total points."""
        # Set up initial progression
        state = data_manager.load_state()
        state.progression.total_points = 1000
        state.theme = Theme.MARIO
        data_manager.save_state(state)
        
        # Switch theme
        tm = ThemeManager(data_manager)
        tm.set_theme(Theme.ZELDA)
        
        # Verify points preserved
        new_state = data_manager.load_state()
        assert new_state.progression.total_points == 1000
    
    def test_theme_switch_preserves_levels_unlocked(self, data_manager):
        """Test that switching themes preserves levels unlocked."""
        # Set up initial progression
        state = data_manager.load_state()
        state.progression.levels_unlocked = 5
        state.theme = Theme.MARIO
        data_manager.save_state(state)
        
        # Switch theme
        tm = ThemeManager(data_manager)
        tm.set_theme(Theme.DKC)
        
        # Verify levels preserved
        new_state = data_manager.load_state()
        assert new_state.progression.levels_unlocked == 5
    
    def test_theme_switch_preserves_correct_answers(self, data_manager):
        """Test that switching themes preserves correct answers count."""
        # Set up initial progression
        state = data_manager.load_state()
        state.progression.correct_answers = 250
        state.theme = Theme.ZELDA
        data_manager.save_state(state)
        
        # Switch theme
        tm = ThemeManager(data_manager)
        tm.set_theme(Theme.MARIO)
        
        # Verify correct answers preserved
        new_state = data_manager.load_state()
        assert new_state.progression.correct_answers == 250
    
    def test_theme_switch_preserves_best_streak(self, data_manager):
        """Test that switching themes preserves best streak."""
        # Set up initial progression
        state = data_manager.load_state()
        state.progression.best_streak = 42
        state.theme = Theme.DKC
        data_manager.save_state(state)
        
        # Switch theme
        tm = ThemeManager(data_manager)
        tm.set_theme(Theme.ZELDA)
        
        # Verify best streak preserved
        new_state = data_manager.load_state()
        assert new_state.progression.best_streak == 42
    
    def test_theme_switch_preserves_currency(self, data_manager):
        """Test that switching themes preserves currency."""
        # Set up initial state
        state = data_manager.load_state()
        state.currency = 500
        state.theme = Theme.MARIO
        data_manager.save_state(state)
        
        # Switch theme
        tm = ThemeManager(data_manager)
        tm.set_theme(Theme.ZELDA)
        
        # Verify currency preserved
        new_state = data_manager.load_state()
        assert new_state.currency == 500
    
    def test_multiple_theme_switches_preserve_progression(self, data_manager):
        """Test that multiple theme switches preserve all progression."""
        # Set up initial progression
        state = data_manager.load_state()
        state.progression.total_points = 5000
        state.progression.correct_answers = 300
        state.progression.levels_unlocked = 6
        state.progression.best_streak = 50
        state.currency = 1000
        state.theme = Theme.MARIO
        data_manager.save_state(state)
        
        # Switch themes multiple times
        tm = ThemeManager(data_manager)
        tm.set_theme(Theme.ZELDA)
        tm.set_theme(Theme.DKC)
        tm.set_theme(Theme.MARIO)
        tm.set_theme(Theme.ZELDA)
        
        # Verify all progression preserved
        final_state = data_manager.load_state()
        assert final_state.progression.total_points == 5000
        assert final_state.progression.correct_answers == 300
        assert final_state.progression.levels_unlocked == 6
        assert final_state.progression.best_streak == 50
        assert final_state.currency == 1000


class TestGetThemeEngine:
    """Tests for get_theme_engine method."""
    
    def test_get_theme_engine_returns_engine(self, theme_manager):
        """Test that get_theme_engine returns a ThemeEngine."""
        engine = theme_manager.get_theme_engine()
        assert isinstance(engine, ThemeEngine)
    
    def test_get_theme_engine_returns_placeholder_by_default(self, theme_manager):
        """Test that get_theme_engine returns PlaceholderThemeEngine by default."""
        engine = theme_manager.get_theme_engine()
        assert isinstance(engine, PlaceholderThemeEngine)
    
    def test_get_theme_engine_returns_correct_theme_engine(self, theme_manager):
        """Test that get_theme_engine returns engine for current theme."""
        theme_manager.set_theme(Theme.ZELDA)
        engine = theme_manager.get_theme_engine()
        
        assert isinstance(engine, PlaceholderThemeEngine)
        assert engine.theme == Theme.ZELDA
    
    def test_get_theme_engine_caches_engines(self, theme_manager):
        """Test that theme engines are cached."""
        engine1 = theme_manager.get_theme_engine()
        engine2 = theme_manager.get_theme_engine()
        
        assert engine1 is engine2
    
    def test_get_theme_engine_different_themes_different_engines(self, theme_manager):
        """Test that different themes return different engines."""
        theme_manager.set_theme(Theme.MARIO)
        mario_engine = theme_manager.get_theme_engine()
        
        theme_manager.set_theme(Theme.ZELDA)
        zelda_engine = theme_manager.get_theme_engine()
        
        assert mario_engine is not zelda_engine
        assert mario_engine.theme == Theme.MARIO
        assert zelda_engine.theme == Theme.ZELDA


class TestRegisterThemeEngine:
    """Tests for register_theme_engine method."""
    
    def test_register_theme_engine(self, theme_manager):
        """Test registering a custom theme engine."""
        mock_engine = MagicMock(spec=ThemeEngine)
        theme_manager.register_theme_engine(Theme.MARIO, mock_engine)
        
        theme_manager.set_theme(Theme.MARIO)
        engine = theme_manager.get_theme_engine()
        
        assert engine is mock_engine
    
    def test_register_theme_engine_replaces_placeholder(self, theme_manager):
        """Test that registering an engine replaces the placeholder."""
        # Get placeholder first
        placeholder = theme_manager.get_theme_engine()
        assert isinstance(placeholder, PlaceholderThemeEngine)
        
        # Register custom engine
        mock_engine = MagicMock(spec=ThemeEngine)
        theme_manager.register_theme_engine(Theme.MARIO, mock_engine)
        
        # Should now return custom engine
        engine = theme_manager.get_theme_engine()
        assert engine is mock_engine


class TestGetAvailableThemes:
    """Tests for get_available_themes method."""
    
    def test_get_available_themes_returns_all_themes(self, theme_manager):
        """Test that get_available_themes returns all three themes.
        
        Requirements: 1.1
        """
        themes = theme_manager.get_available_themes()
        
        assert len(themes) == 3
        assert Theme.MARIO in themes
        assert Theme.ZELDA in themes
        assert Theme.DKC in themes
    
    def test_get_available_themes_returns_list(self, theme_manager):
        """Test that get_available_themes returns a list."""
        themes = theme_manager.get_available_themes()
        assert isinstance(themes, list)


class TestSetProgressionSystem:
    """Tests for set_progression_system method."""
    
    def test_set_progression_system(self, theme_manager):
        """Test setting the progression system reference."""
        mock_progression = MagicMock()
        theme_manager.set_progression_system(mock_progression)
        
        assert theme_manager._progression_system is mock_progression
    
    def test_set_progression_system_syncs_theme(self, theme_manager):
        """Test that setting progression system syncs current theme."""
        theme_manager.set_theme(Theme.DKC)
        
        mock_progression = MagicMock()
        theme_manager.set_progression_system(mock_progression)
        
        mock_progression.set_current_theme.assert_called_with(Theme.DKC)


class TestPlaceholderThemeEngine:
    """Tests for PlaceholderThemeEngine."""
    
    @pytest.fixture
    def placeholder_engine(self, data_manager):
        """Create a PlaceholderThemeEngine for testing."""
        return PlaceholderThemeEngine(Theme.MARIO, data_manager)
    
    def test_get_animation_for_correct(self, placeholder_engine):
        """Test get_animation_for_correct returns collect animation."""
        animation = placeholder_engine.get_animation_for_correct()
        
        assert isinstance(animation, Animation)
        assert animation.type == AnimationType.COLLECT
        assert animation.theme == Theme.MARIO
    
    def test_get_animation_for_wrong(self, placeholder_engine):
        """Test get_animation_for_wrong returns damage animation."""
        animation = placeholder_engine.get_animation_for_wrong()
        
        assert isinstance(animation, Animation)
        assert animation.type == AnimationType.DAMAGE
        assert animation.theme == Theme.MARIO
    
    def test_get_collectible_for_correct_mario(self, data_manager):
        """Test Mario theme returns coin collectible."""
        engine = PlaceholderThemeEngine(Theme.MARIO, data_manager)
        collectible = engine.get_collectible_for_correct()
        
        assert collectible.name == "Coin"
    
    def test_get_collectible_for_correct_zelda(self, data_manager):
        """Test Zelda theme returns rupee collectible."""
        engine = PlaceholderThemeEngine(Theme.ZELDA, data_manager)
        collectible = engine.get_collectible_for_correct()
        
        assert collectible.name == "Rupee"
    
    def test_get_collectible_for_correct_dkc(self, data_manager):
        """Test DKC theme returns banana collectible."""
        engine = PlaceholderThemeEngine(Theme.DKC, data_manager)
        collectible = engine.get_collectible_for_correct()
        
        assert collectible.name == "Banana"
    
    def test_get_dashboard_stats_mario(self, data_manager):
        """Test Mario theme dashboard stats."""
        engine = PlaceholderThemeEngine(Theme.MARIO, data_manager)
        stats = engine.get_dashboard_stats()
        
        assert isinstance(stats, ThemeStats)
        assert stats.theme == Theme.MARIO
        assert stats.primary_collectible_name == "Coins"
    
    def test_get_dashboard_stats_zelda(self, data_manager):
        """Test Zelda theme dashboard stats."""
        engine = PlaceholderThemeEngine(Theme.ZELDA, data_manager)
        stats = engine.get_dashboard_stats()
        
        assert stats.theme == Theme.ZELDA
        assert stats.primary_collectible_name == "Rupees"
        assert stats.secondary_stat_name == "Hearts"
    
    def test_get_dashboard_stats_dkc(self, data_manager):
        """Test DKC theme dashboard stats."""
        engine = PlaceholderThemeEngine(Theme.DKC, data_manager)
        stats = engine.get_dashboard_stats()
        
        assert stats.theme == Theme.DKC
        assert stats.primary_collectible_name == "Bananas"
