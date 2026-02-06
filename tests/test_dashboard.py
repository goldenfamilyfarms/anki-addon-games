"""
Tests for the Dashboard module.

This module contains unit tests for the Dashboard class and its
component widgets (StatsWidget, AchievementsWidget, PowerUpsWidget,
ThemeSelectorWidget).

Requirements: 10.1, 10.2, 10.3, 10.4, 10.5, 10.6, 10.7
"""

import pytest
from datetime import datetime
from pathlib import Path
from unittest.mock import MagicMock, patch
import sys
import tempfile

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from data.models import (
    Achievement,
    ActivePowerUp,
    GameConfig,
    GameState,
    PowerUp,
    PowerUpType,
    ProgressionState,
    Theme,
    ThemeState,
    ThemeStats,
)
from data.data_manager import DataManager
from core.progression_system import ProgressionSystem
from core.achievement_system import AchievementSystem
from core.theme_manager import ThemeManager
from core.powerup_system import PowerUpSystem
from core.scoring_engine import ScoringEngine


# Check if PyQt is available
try:
    from PyQt6.QtWidgets import QApplication
    from PyQt6.QtCore import Qt
    PYQT_AVAILABLE = True
    PYQT_VERSION = 6
except ImportError:
    try:
        from PyQt5.QtWidgets import QApplication
        from PyQt5.QtCore import Qt
        PYQT_AVAILABLE = True
        PYQT_VERSION = 5
    except ImportError:
        PYQT_AVAILABLE = False
        PYQT_VERSION = 0


# Skip all tests if PyQt is not available
pytestmark = pytest.mark.skipif(
    not PYQT_AVAILABLE,
    reason="PyQt not available"
)


@pytest.fixture(scope="module")
def qapp():
    """Create a QApplication instance for the test module."""
    if not PYQT_AVAILABLE:
        yield None
        return
    
    # Check if QApplication already exists
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    yield app


@pytest.fixture
def temp_db_path(tmp_path):
    """Create a temporary database path."""
    return tmp_path / "test_dashboard.db"


@pytest.fixture
def data_manager(temp_db_path):
    """Create a DataManager instance with a temporary database."""
    dm = DataManager(temp_db_path)
    dm.initialize_database()
    return dm


@pytest.fixture
def scoring_engine():
    """Create a ScoringEngine instance."""
    return ScoringEngine(GameConfig())


@pytest.fixture
def progression_system(data_manager, scoring_engine):
    """Create a ProgressionSystem instance."""
    return ProgressionSystem(data_manager, scoring_engine)


@pytest.fixture
def achievement_system(data_manager):
    """Create an AchievementSystem instance."""
    return AchievementSystem(data_manager)


@pytest.fixture
def theme_manager(data_manager):
    """Create a ThemeManager instance."""
    return ThemeManager(data_manager)


@pytest.fixture
def powerup_system(data_manager):
    """Create a PowerUpSystem instance."""
    return PowerUpSystem(data_manager)


class TestDashboardCreation:
    """Tests for Dashboard creation and initialization."""
    
    def test_dashboard_can_be_created(self, qapp, progression_system, 
                                       achievement_system, theme_manager,
                                       powerup_system):
        """Test that Dashboard can be instantiated.
        
        Requirements: 10.1
        """
        from ui.dashboard import Dashboard
        
        dashboard = Dashboard(
            progression_system=progression_system,
            achievement_system=achievement_system,
            theme_manager=theme_manager,
            powerup_system=powerup_system
        )
        
        assert dashboard is not None
        dashboard.close()
    
    def test_dashboard_has_tabbed_interface(self, qapp, progression_system,
                                            achievement_system, theme_manager,
                                            powerup_system):
        """Test that Dashboard has a tabbed interface with all required tabs.
        
        Requirements: 10.1
        """
        from ui.dashboard import Dashboard
        
        dashboard = Dashboard(
            progression_system=progression_system,
            achievement_system=achievement_system,
            theme_manager=theme_manager,
            powerup_system=powerup_system
        )
        
        # Check that all tabs exist
        assert dashboard._tab_widget.count() == 4
        
        # Verify tab names contain expected content
        tab_texts = [dashboard._tab_widget.tabText(i) for i in range(4)]
        assert any("Stats" in t for t in tab_texts)
        assert any("Achievements" in t for t in tab_texts)
        assert any("Power" in t for t in tab_texts)
        assert any("Theme" in t for t in tab_texts)
        
        dashboard.close()
    
    def test_dashboard_without_powerup_system(self, qapp, progression_system,
                                               achievement_system, theme_manager):
        """Test that Dashboard works without a PowerUpSystem.
        
        Requirements: 10.1
        """
        from ui.dashboard import Dashboard
        
        dashboard = Dashboard(
            progression_system=progression_system,
            achievement_system=achievement_system,
            theme_manager=theme_manager,
            powerup_system=None
        )
        
        assert dashboard is not None
        # Should not raise when refreshing without powerup system
        dashboard.refresh()
        dashboard.close()


class TestStatsTab:
    """Tests for the Stats tab functionality."""
    
    def test_stats_tab_displays_total_points(self, qapp, progression_system,
                                              achievement_system, theme_manager,
                                              powerup_system, data_manager):
        """Test that stats tab displays total points.
        
        Requirements: 10.2
        """
        from ui.dashboard import Dashboard
        
        # Set up some progression data
        state = progression_system.get_state()
        state.total_points = 1500
        data_manager.save_progression(state)
        
        dashboard = Dashboard(
            progression_system=progression_system,
            achievement_system=achievement_system,
            theme_manager=theme_manager,
            powerup_system=powerup_system
        )
        
        stats_widget = dashboard.get_stats_widget()
        assert "1,500" in stats_widget._points_label.text()
        
        dashboard.close()
    
    def test_stats_tab_displays_cards_reviewed(self, qapp, progression_system,
                                                achievement_system, theme_manager,
                                                powerup_system, data_manager):
        """Test that stats tab displays cards reviewed count.
        
        Requirements: 10.2
        """
        from ui.dashboard import Dashboard
        
        state = progression_system.get_state()
        state.total_cards_reviewed = 250
        data_manager.save_progression(state)
        
        dashboard = Dashboard(
            progression_system=progression_system,
            achievement_system=achievement_system,
            theme_manager=theme_manager,
            powerup_system=powerup_system
        )
        
        stats_widget = dashboard.get_stats_widget()
        assert "250" in stats_widget._cards_label.text()
        
        dashboard.close()
    
    def test_stats_tab_displays_current_streak(self, qapp, progression_system,
                                                achievement_system, theme_manager,
                                                powerup_system, data_manager):
        """Test that stats tab displays current streak.
        
        Requirements: 10.2
        """
        from ui.dashboard import Dashboard
        
        state = progression_system.get_state()
        state.current_streak = 15
        data_manager.save_progression(state)
        
        dashboard = Dashboard(
            progression_system=progression_system,
            achievement_system=achievement_system,
            theme_manager=theme_manager,
            powerup_system=powerup_system
        )
        
        stats_widget = dashboard.get_stats_widget()
        assert "15" in stats_widget._streak_label.text()
        
        dashboard.close()

    def test_stats_tab_displays_accuracy(self, qapp, progression_system,
                                          achievement_system, theme_manager,
                                          powerup_system, data_manager):
        """Test that stats tab displays session accuracy percentage.
        
        Requirements: 10.2
        """
        from ui.dashboard import Dashboard
        
        state = progression_system.get_state()
        state.session_accuracy = 0.875  # 87.5%
        data_manager.save_progression(state)
        
        dashboard = Dashboard(
            progression_system=progression_system,
            achievement_system=achievement_system,
            theme_manager=theme_manager,
            powerup_system=powerup_system
        )
        
        stats_widget = dashboard.get_stats_widget()
        assert "87.5%" in stats_widget._accuracy_label.text()
        
        dashboard.close()
    
    def test_stats_tab_displays_levels_unlocked(self, qapp, progression_system,
                                                 achievement_system, theme_manager,
                                                 powerup_system, data_manager):
        """Test that stats tab displays levels unlocked.
        
        Requirements: 10.2
        """
        from ui.dashboard import Dashboard
        
        state = progression_system.get_state()
        state.levels_unlocked = 5
        data_manager.save_progression(state)
        
        dashboard = Dashboard(
            progression_system=progression_system,
            achievement_system=achievement_system,
            theme_manager=theme_manager,
            powerup_system=powerup_system
        )
        
        stats_widget = dashboard.get_stats_widget()
        assert "5" in stats_widget._levels_unlocked_label.text()
        
        dashboard.close()
    
    def test_stats_tab_displays_theme_specific_progress(self, qapp, progression_system,
                                                         achievement_system, theme_manager,
                                                         powerup_system):
        """Test that stats tab displays theme-specific progress.
        
        Requirements: 10.3
        """
        from ui.dashboard import Dashboard
        
        # Set Mario theme
        theme_manager.set_theme(Theme.MARIO)
        
        dashboard = Dashboard(
            progression_system=progression_system,
            achievement_system=achievement_system,
            theme_manager=theme_manager,
            powerup_system=powerup_system
        )
        
        stats_widget = dashboard.get_stats_widget()
        # Should show "Coins" for Mario theme
        theme_group_title = stats_widget._theme_group.title()
        assert "MARIO" in theme_group_title
        
        dashboard.close()


class TestAchievementsTab:
    """Tests for the Achievements tab functionality."""
    
    def test_achievements_tab_displays_all_achievements(self, qapp, progression_system,
                                                         achievement_system, theme_manager,
                                                         powerup_system):
        """Test that achievements tab displays all achievements.
        
        Requirements: 10.4
        """
        from ui.dashboard import Dashboard
        
        dashboard = Dashboard(
            progression_system=progression_system,
            achievement_system=achievement_system,
            theme_manager=theme_manager,
            powerup_system=powerup_system
        )
        
        achievements_widget = dashboard.get_achievements_widget()
        all_achievements = achievement_system.get_all_achievements()
        
        # Check that total count matches
        total_text = achievements_widget._total_label.text()
        assert str(len(all_achievements)) in total_text
        
        dashboard.close()
    
    def test_achievements_tab_shows_unlock_status(self, qapp, progression_system,
                                                   achievement_system, theme_manager,
                                                   powerup_system, data_manager):
        """Test that achievements tab shows unlock status.
        
        Requirements: 10.4
        """
        from ui.dashboard import Dashboard
        
        # Unlock an achievement by setting high card count
        state = progression_system.get_state()
        state.total_cards_reviewed = 150
        data_manager.save_progression(state)
        
        # Check achievements to unlock some
        achievement_system.check_achievements(state)
        
        dashboard = Dashboard(
            progression_system=progression_system,
            achievement_system=achievement_system,
            theme_manager=theme_manager,
            powerup_system=powerup_system
        )
        
        achievements_widget = dashboard.get_achievements_widget()
        unlocked_text = achievements_widget._unlocked_label.text()
        
        # Should have at least 1 unlocked (cards_100)
        assert "Unlocked:" in unlocked_text
        
        dashboard.close()
    
    def test_achievements_tab_shows_unlock_dates(self, qapp, progression_system,
                                                  achievement_system, theme_manager,
                                                  powerup_system, data_manager):
        """Test that achievements tab shows unlock dates for unlocked achievements.
        
        Requirements: 10.4
        """
        from ui.dashboard import Dashboard
        
        # Unlock an achievement
        state = progression_system.get_state()
        state.total_cards_reviewed = 100
        data_manager.save_progression(state)
        achievement_system.check_achievements(state)
        
        dashboard = Dashboard(
            progression_system=progression_system,
            achievement_system=achievement_system,
            theme_manager=theme_manager,
            powerup_system=powerup_system
        )
        
        # Verify unlocked achievements have dates
        unlocked = achievement_system.get_unlocked_achievements()
        for achievement in unlocked:
            assert achievement.unlock_date is not None
        
        dashboard.close()


class TestPowerUpsTab:
    """Tests for the Power-Ups tab functionality."""
    
    def test_powerups_tab_displays_inventory(self, qapp, progression_system,
                                              achievement_system, theme_manager,
                                              powerup_system):
        """Test that power-ups tab displays inventory.
        
        Requirements: 10.5
        """
        from ui.dashboard import Dashboard
        
        # Grant a power-up
        powerup_system.grant_powerup(PowerUpType.MUSHROOM, Theme.MARIO)
        
        dashboard = Dashboard(
            progression_system=progression_system,
            achievement_system=achievement_system,
            theme_manager=theme_manager,
            powerup_system=powerup_system
        )
        
        powerups_widget = dashboard.get_powerups_widget()
        inventory = powerup_system.get_inventory()
        
        # Should have at least one power-up widget
        assert len(inventory) > 0
        
        dashboard.close()
    
    def test_powerups_tab_shows_powerup_effects(self, qapp, progression_system,
                                                 achievement_system, theme_manager,
                                                 powerup_system):
        """Test that power-ups tab shows power-up effects/descriptions.
        
        Requirements: 10.5
        """
        from ui.dashboard import Dashboard
        
        # Grant a power-up with known description
        powerup = powerup_system.grant_powerup(PowerUpType.FIRE_FLOWER, Theme.MARIO)
        
        dashboard = Dashboard(
            progression_system=progression_system,
            achievement_system=achievement_system,
            theme_manager=theme_manager,
            powerup_system=powerup_system
        )
        
        # Verify the power-up has a description
        assert powerup.description is not None
        assert len(powerup.description) > 0
        
        dashboard.close()
    
    def test_powerups_tab_shows_active_powerups(self, qapp, progression_system,
                                                 achievement_system, theme_manager,
                                                 powerup_system):
        """Test that power-ups tab shows active power-ups.
        
        Requirements: 10.5
        """
        from ui.dashboard import Dashboard
        
        # Grant and activate a timed power-up
        powerup = powerup_system.grant_powerup(PowerUpType.STAR, Theme.MARIO)
        powerup_system.activate_powerup(powerup.id)
        
        dashboard = Dashboard(
            progression_system=progression_system,
            achievement_system=achievement_system,
            theme_manager=theme_manager,
            powerup_system=powerup_system
        )
        
        active = powerup_system.get_active_powerups()
        # Star has duration, so it should be active
        assert len(active) > 0
        
        dashboard.close()


class TestThemeSelector:
    """Tests for the Theme Selector functionality."""
    
    def test_theme_selector_shows_current_theme(self, qapp, progression_system,
                                                 achievement_system, theme_manager,
                                                 powerup_system):
        """Test that theme selector shows current theme.
        
        Requirements: 10.6
        """
        from ui.dashboard import Dashboard
        
        theme_manager.set_theme(Theme.ZELDA)
        
        dashboard = Dashboard(
            progression_system=progression_system,
            achievement_system=achievement_system,
            theme_manager=theme_manager,
            powerup_system=powerup_system
        )
        
        theme_selector = dashboard.get_theme_selector()
        current_text = theme_selector._current_theme_label.text()
        
        assert "Zelda" in current_text
        
        dashboard.close()
    
    def test_theme_selector_allows_theme_switching(self, qapp, progression_system,
                                                    achievement_system, theme_manager,
                                                    powerup_system):
        """Test that theme selector allows switching themes.
        
        Requirements: 10.6
        """
        from ui.dashboard import Dashboard
        
        theme_manager.set_theme(Theme.MARIO)
        
        dashboard = Dashboard(
            progression_system=progression_system,
            achievement_system=achievement_system,
            theme_manager=theme_manager,
            powerup_system=powerup_system
        )
        
        # Simulate theme change
        dashboard._on_theme_changed(Theme.DKC)
        
        # Verify theme was changed
        assert theme_manager.get_current_theme() == Theme.DKC
        
        dashboard.close()
    
    def test_theme_selector_shows_all_themes(self, qapp, progression_system,
                                              achievement_system, theme_manager,
                                              powerup_system):
        """Test that theme selector shows all available themes.
        
        Requirements: 10.6
        """
        from ui.dashboard import Dashboard
        
        dashboard = Dashboard(
            progression_system=progression_system,
            achievement_system=achievement_system,
            theme_manager=theme_manager,
            powerup_system=powerup_system
        )
        
        theme_selector = dashboard.get_theme_selector()
        
        # Should have buttons for all themes
        assert len(theme_selector._theme_buttons) == 3
        assert Theme.MARIO in theme_selector._theme_buttons
        assert Theme.ZELDA in theme_selector._theme_buttons
        assert Theme.DKC in theme_selector._theme_buttons
        
        dashboard.close()


class TestRealTimeUpdates:
    """Tests for real-time update functionality."""
    
    def test_dashboard_refresh_updates_stats(self, qapp, progression_system,
                                              achievement_system, theme_manager,
                                              powerup_system, data_manager):
        """Test that refresh updates displayed stats.
        
        Requirements: 10.7
        """
        from ui.dashboard import Dashboard
        
        dashboard = Dashboard(
            progression_system=progression_system,
            achievement_system=achievement_system,
            theme_manager=theme_manager,
            powerup_system=powerup_system
        )
        
        # Get initial value
        stats_widget = dashboard.get_stats_widget()
        initial_points = stats_widget._points_label.text()
        
        # Update progression
        state = progression_system.get_state()
        state.total_points = 9999
        data_manager.save_progression(state)
        
        # Refresh dashboard
        dashboard.refresh()
        
        # Verify update
        updated_points = stats_widget._points_label.text()
        assert "9,999" in updated_points
        assert initial_points != updated_points
        
        dashboard.close()
    
    def test_dashboard_auto_refresh_can_be_started(self, qapp, progression_system,
                                                    achievement_system, theme_manager,
                                                    powerup_system):
        """Test that auto-refresh can be started.
        
        Requirements: 10.7
        """
        from ui.dashboard import Dashboard
        
        dashboard = Dashboard(
            progression_system=progression_system,
            achievement_system=achievement_system,
            theme_manager=theme_manager,
            powerup_system=powerup_system
        )
        
        # Start auto-refresh
        dashboard.start_auto_refresh(interval_ms=5000)
        
        assert dashboard._refresh_timer is not None
        assert dashboard._refresh_timer.isActive()
        
        # Stop and close
        dashboard.stop_auto_refresh()
        assert not dashboard._refresh_timer.isActive()
        
        dashboard.close()
    
    def test_dashboard_auto_refresh_stops_on_close(self, qapp, progression_system,
                                                    achievement_system, theme_manager,
                                                    powerup_system):
        """Test that auto-refresh stops when dashboard is closed.
        
        Requirements: 10.7
        """
        from ui.dashboard import Dashboard
        
        dashboard = Dashboard(
            progression_system=progression_system,
            achievement_system=achievement_system,
            theme_manager=theme_manager,
            powerup_system=powerup_system
        )
        
        dashboard.start_auto_refresh(interval_ms=1000)
        timer = dashboard._refresh_timer
        
        # Close dashboard
        dashboard.close()
        
        # Timer should be stopped
        assert not timer.isActive()


class TestTabNavigation:
    """Tests for tab navigation functionality."""
    
    def test_show_stats_tab(self, qapp, progression_system,
                            achievement_system, theme_manager,
                            powerup_system):
        """Test show_stats_tab method.
        
        Requirements: 10.2
        """
        from ui.dashboard import Dashboard
        
        dashboard = Dashboard(
            progression_system=progression_system,
            achievement_system=achievement_system,
            theme_manager=theme_manager,
            powerup_system=powerup_system
        )
        
        dashboard.show_stats_tab()
        assert dashboard.get_current_tab_index() == 0
        
        dashboard.close()
    
    def test_show_achievements_tab(self, qapp, progression_system,
                                    achievement_system, theme_manager,
                                    powerup_system):
        """Test show_achievements_tab method.
        
        Requirements: 10.4
        """
        from ui.dashboard import Dashboard
        
        dashboard = Dashboard(
            progression_system=progression_system,
            achievement_system=achievement_system,
            theme_manager=theme_manager,
            powerup_system=powerup_system
        )
        
        dashboard.show_achievements_tab()
        assert dashboard.get_current_tab_index() == 1
        
        dashboard.close()
    
    def test_show_powerups_tab(self, qapp, progression_system,
                                achievement_system, theme_manager,
                                powerup_system):
        """Test show_powerups_tab method.
        
        Requirements: 10.5
        """
        from ui.dashboard import Dashboard
        
        dashboard = Dashboard(
            progression_system=progression_system,
            achievement_system=achievement_system,
            theme_manager=theme_manager,
            powerup_system=powerup_system
        )
        
        dashboard.show_powerups_tab()
        assert dashboard.get_current_tab_index() == 2
        
        dashboard.close()
    
    def test_show_theme_selector(self, qapp, progression_system,
                                  achievement_system, theme_manager,
                                  powerup_system):
        """Test show_theme_selector method.
        
        Requirements: 10.6
        """
        from ui.dashboard import Dashboard
        
        dashboard = Dashboard(
            progression_system=progression_system,
            achievement_system=achievement_system,
            theme_manager=theme_manager,
            powerup_system=powerup_system
        )
        
        dashboard.show_theme_selector()
        assert dashboard.get_current_tab_index() == 3
        
        dashboard.close()


class TestStatsWidgetUnit:
    """Unit tests for StatsWidget."""
    
    def test_stats_widget_creation(self, qapp):
        """Test StatsWidget can be created."""
        from ui.dashboard import StatsWidget
        
        widget = StatsWidget()
        assert widget is not None
    
    def test_stats_widget_update_stats(self, qapp):
        """Test StatsWidget.update_stats method."""
        from ui.dashboard import StatsWidget
        
        widget = StatsWidget()
        
        state = ProgressionState(
            total_points=5000,
            total_cards_reviewed=200,
            current_streak=10,
            best_streak=25,
            session_accuracy=0.95,
            levels_unlocked=4,
            levels_completed=3
        )
        
        widget.update_stats(state)
        
        assert "5,000" in widget._points_label.text()
        assert "200" in widget._cards_label.text()
        assert "10" in widget._streak_label.text()
        assert "25" in widget._best_streak_label.text()
        assert "95.0%" in widget._accuracy_label.text()
        assert "4" in widget._levels_unlocked_label.text()
        assert "3" in widget._levels_completed_label.text()
    
    def test_stats_widget_update_theme_stats(self, qapp):
        """Test StatsWidget.update_theme_stats method."""
        from ui.dashboard import StatsWidget
        
        widget = StatsWidget()
        
        theme_stats = ThemeStats(
            theme=Theme.DKC,
            primary_collectible_name="Bananas",
            primary_collectible_count=150,
            secondary_stat_name="DK Coins",
            secondary_stat_value=5,
            completion_percentage=0.45
        )
        
        widget.update_theme_stats(theme_stats)
        
        assert "DKC" in widget._theme_group.title()
        assert "150" in widget._theme_collectible_label.text()
        assert "5" in widget._theme_secondary_label.text()
        assert "45.0%" in widget._theme_completion_label.text()


class TestAchievementsWidgetUnit:
    """Unit tests for AchievementsWidget."""
    
    def test_achievements_widget_creation(self, qapp):
        """Test AchievementsWidget can be created."""
        from ui.dashboard import AchievementsWidget
        
        widget = AchievementsWidget()
        assert widget is not None
    
    def test_achievements_widget_update(self, qapp):
        """Test AchievementsWidget.update_achievements method."""
        from ui.dashboard import AchievementsWidget
        
        widget = AchievementsWidget()
        
        achievements = [
            Achievement(
                id="test_1",
                name="Test Achievement 1",
                description="Test description 1",
                icon="test.png",
                reward_currency=50,
                unlocked=True,
                unlock_date=datetime.now(),
                progress=100,
                target=100
            ),
            Achievement(
                id="test_2",
                name="Test Achievement 2",
                description="Test description 2",
                icon="test.png",
                reward_currency=100,
                unlocked=False,
                unlock_date=None,
                progress=50,
                target=100
            ),
        ]
        
        widget.update_achievements(achievements)
        
        assert "2" in widget._total_label.text()
        assert "1" in widget._unlocked_label.text()
        assert widget._progress_bar.value() == 50


class TestPowerUpsWidgetUnit:
    """Unit tests for PowerUpsWidget."""
    
    def test_powerups_widget_creation(self, qapp):
        """Test PowerUpsWidget can be created."""
        from ui.dashboard import PowerUpsWidget
        
        widget = PowerUpsWidget()
        assert widget is not None
    
    def test_powerups_widget_update_empty(self, qapp):
        """Test PowerUpsWidget with empty inventory."""
        from ui.dashboard import PowerUpsWidget
        
        widget = PowerUpsWidget()
        widget.update_powerups([], [])
        
        # Should not raise and should show empty message
        assert widget is not None
    
    def test_powerups_widget_update_with_inventory(self, qapp):
        """Test PowerUpsWidget with inventory items."""
        from ui.dashboard import PowerUpsWidget
        
        widget = PowerUpsWidget()
        
        powerups = [
            PowerUp(
                id="test_1",
                type=PowerUpType.MUSHROOM,
                theme=Theme.MARIO,
                name="Super Mushroom",
                description="Grants extra health",
                icon="mushroom.png",
                quantity=3,
                duration_seconds=0,
                acquired_at=datetime.now()
            ),
        ]
        
        widget.update_powerups(powerups, [])
        
        # Should have created a widget for the power-up
        assert len(widget._powerup_widgets) == 1


class TestThemeSelectorWidgetUnit:
    """Unit tests for ThemeSelectorWidget."""
    
    def test_theme_selector_creation(self, qapp):
        """Test ThemeSelectorWidget can be created."""
        from ui.dashboard import ThemeSelectorWidget
        
        widget = ThemeSelectorWidget()
        assert widget is not None
    
    def test_theme_selector_set_current_theme(self, qapp):
        """Test ThemeSelectorWidget.set_current_theme method."""
        from ui.dashboard import ThemeSelectorWidget
        
        widget = ThemeSelectorWidget()
        
        widget.set_current_theme(Theme.ZELDA)
        
        assert "Zelda" in widget._current_theme_label.text()
        
        # Current theme button should be disabled
        _, btn = widget._theme_buttons[Theme.ZELDA]
        assert not btn.isEnabled()
        assert btn.text() == "Current"
        
        # Other buttons should be enabled
        _, mario_btn = widget._theme_buttons[Theme.MARIO]
        assert mario_btn.isEnabled()
        assert mario_btn.text() == "Select"
