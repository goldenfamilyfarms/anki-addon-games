"""
Tests for the GameWindow class.

This module contains unit tests for the GameWindow, testing:
- Window creation as a separate PyQt window (Requirement 9.1)
- Animation playback within 100ms (Requirement 9.3)
- Aspect ratio preservation during resizing (Requirement 9.4)
- Theme switching with visual transitions
- State display updates
- Window position persistence

Requirements: 9.1, 9.3, 9.4, 9.5, 9.6, 9.7
"""

import time
from unittest.mock import MagicMock

import pytest

from data.models import (
    Animation,
    AnimationType,
    Level,
    ProgressionState,
    Theme,
)
from core.theme_manager import ThemeManager
from data.data_manager import DataManager
from ui.animation_engine import AnimationEngine
from ui.asset_manager import AssetManager
from ui.game_window import GameWindow, AspectRatioWidget, StatsBar, PYQT_VERSION


# Skip all tests if PyQt is not available
pytestmark = [
    pytest.mark.skipif(PYQT_VERSION == 0, reason="PyQt not available"),
]


# Fixtures

@pytest.fixture
def mock_data_manager(tmp_path):
    """Create a mock DataManager for testing."""
    db_path = tmp_path / "test.db"
    dm = DataManager(db_path)
    dm.initialize_database()
    return dm


@pytest.fixture
def theme_manager(mock_data_manager):
    """Create a ThemeManager instance for testing."""
    return ThemeManager(mock_data_manager)


@pytest.fixture
def asset_manager():
    """Create an AssetManager instance for testing."""
    return AssetManager(assets_root="test_assets")


@pytest.fixture
def animation_engine(asset_manager):
    """Create an AnimationEngine instance for testing."""
    return AnimationEngine(asset_manager)


@pytest.fixture
def game_window(theme_manager, animation_engine, qtbot):
    """Create a GameWindow instance for testing."""
    window = GameWindow(theme_manager, animation_engine)
    if PYQT_VERSION > 0:
        qtbot.addWidget(window)
    yield window
    # Cleanup handled by qtbot


@pytest.fixture
def sample_progression_state():
    """Create a sample progression state for testing."""
    return ProgressionState(
        total_points=1500,
        total_cards_reviewed=100,
        correct_answers=85,
        current_streak=10,
        best_streak=25,
        levels_unlocked=3,
        levels_completed=2,
        session_accuracy=0.85,
        session_health=75,
    )


@pytest.fixture
def sample_animation():
    """Create a sample animation for testing."""
    return Animation(
        type=AnimationType.COLLECT,
        theme=Theme.MARIO,
        sprite_sheet="mario/characters/mario_run.png",
        frames=[0, 1, 2, 3],
        fps=30,
        loop=False
    )


@pytest.fixture
def sample_level():
    """Create a sample level for testing."""
    return Level(
        id="mario_level_1",
        theme=Theme.MARIO,
        level_number=1,
        name="World 1-1",
        description="The classic first level",
        unlocked=True,
        completed=False
    )


# Test GameWindow Creation

class TestGameWindowCreation:
    """Tests for GameWindow creation and initialization."""
    
    def test_create_game_window(self, game_window):
        """Test that GameWindow can be created (Requirement 9.1)."""
        assert game_window is not None
        assert game_window.theme_manager is not None
        assert game_window.animation_engine is not None
    
    def test_window_is_separate(self, game_window):
        """Test that GameWindow is a separate window (Requirement 9.1)."""
        if PYQT_VERSION == 0:
            pytest.skip("PyQt not available")
        
        # Check window flags indicate it's a separate window
        from PyQt6.QtCore import Qt
        flags = game_window.windowFlags()
        assert flags & Qt.WindowType.Window
    
    def test_window_has_title(self, game_window):
        """Test that window has appropriate title."""
        if PYQT_VERSION == 0:
            pytest.skip("PyQt not available")
        
        title = game_window.windowTitle()
        assert "NintendAnki" in title
    
    def test_window_has_minimum_size(self, game_window):
        """Test that window has minimum size set."""
        if PYQT_VERSION == 0:
            pytest.skip("PyQt not available")
        
        min_size = game_window.minimumSize()
        assert min_size.width() >= 400
        assert min_size.height() >= 300
    
    def test_initial_theme(self, game_window, theme_manager):
        """Test that window initializes with correct theme."""
        expected_theme = theme_manager.get_current_theme()
        assert game_window.get_current_theme() == expected_theme


# Test Animation Playback

class TestAnimationPlayback:
    """Tests for animation playback functionality."""
    
    def test_show_animation(self, game_window, sample_animation):
        """Test playing an animation."""
        # Mock the animation engine's play method
        game_window.animation_engine.play_animation = MagicMock()
        
        game_window.show_animation(sample_animation)
        
        game_window.animation_engine.play_animation.assert_called_once()
    
    def test_animation_response_time(self, game_window, sample_animation):
        """Test that animation starts within 100ms (Requirement 9.3)."""
        # Mock the animation engine
        game_window.animation_engine.play_animation = MagicMock()
        
        start_time = time.perf_counter()
        game_window.show_animation(sample_animation)
        elapsed_ms = (time.perf_counter() - start_time) * 1000
        
        # Should complete within 100ms
        assert elapsed_ms < 100
    
    def test_animation_complete_callback(self, game_window, sample_animation):
        """Test animation complete callback."""
        callback = MagicMock()
        game_window.set_animation_complete_callback(callback)
        
        # Trigger the internal callback
        game_window._on_animation_complete_internal()
        
        callback.assert_called_once()
    
    def test_is_animation_playing(self, game_window):
        """Test checking if animation is playing."""
        game_window.animation_engine.is_playing = MagicMock(return_value=True)
        assert game_window.is_animation_playing() is True
        
        game_window.animation_engine.is_playing = MagicMock(return_value=False)
        assert game_window.is_animation_playing() is False


# Test Display Updates

class TestDisplayUpdates:
    """Tests for display update functionality."""
    
    def test_update_display(self, game_window, sample_progression_state):
        """Test updating the display with progression state."""
        game_window.update_display(sample_progression_state)
        
        assert game_window.get_current_state() == sample_progression_state
    
    def test_update_display_updates_stats_bar(self, game_window, sample_progression_state):
        """Test that update_display updates the stats bar."""
        if PYQT_VERSION == 0:
            pytest.skip("PyQt not available")
        
        # Mock the stats bar update method
        game_window._stats_bar.update_stats = MagicMock()
        
        game_window.update_display(sample_progression_state)
        
        game_window._stats_bar.update_stats.assert_called_once()
    
    def test_show_level(self, game_window, sample_level):
        """Test displaying a level."""
        game_window.show_level(sample_level)
        
        # Level should be stored
        assert game_window._current_level == sample_level


# Test Theme Switching

class TestThemeSwitching:
    """Tests for theme switching functionality."""
    
    def test_switch_theme(self, game_window):
        """Test switching themes."""
        initial_theme = game_window.get_current_theme()
        
        # Switch to a different theme
        new_theme = Theme.ZELDA if initial_theme != Theme.ZELDA else Theme.DKC
        game_window.switch_theme(new_theme)
        
        assert game_window.get_current_theme() == new_theme
    
    def test_switch_theme_updates_title(self, game_window):
        """Test that theme switch updates window title."""
        if PYQT_VERSION == 0:
            pytest.skip("PyQt not available")
        
        game_window.switch_theme(Theme.ZELDA)
        
        title = game_window.windowTitle()
        assert "Zelda" in title
    
    def test_switch_theme_all_themes(self, game_window):
        """Test switching to all available themes."""
        for theme in Theme:
            game_window.switch_theme(theme)
            assert game_window.get_current_theme() == theme


# Test Aspect Ratio Preservation

class TestAspectRatioPreservation:
    """Tests for aspect ratio preservation (Requirement 9.4)."""
    
    def test_set_aspect_ratio(self, game_window):
        """Test setting aspect ratio."""
        if PYQT_VERSION == 0:
            pytest.skip("PyQt not available")
        
        game_window.set_aspect_ratio(4/3)
        assert game_window.get_aspect_ratio() == pytest.approx(4/3, rel=0.01)
    
    def test_default_aspect_ratio(self, game_window):
        """Test default aspect ratio is 16:9."""
        ratio = game_window.get_aspect_ratio()
        assert ratio == pytest.approx(16/9, rel=0.01)


# Test Window Position Persistence

class TestWindowPositionPersistence:
    """Tests for window position persistence (Requirement 9.5)."""
    
    def test_save_position(self, game_window):
        """Test saving window position."""
        if PYQT_VERSION == 0:
            pytest.skip("PyQt not available")
        
        # Should not raise an error
        game_window.save_position()
    
    def test_restore_position(self, game_window):
        """Test restoring window position."""
        if PYQT_VERSION == 0:
            pytest.skip("PyQt not available")
        
        # Should not raise an error
        game_window.restore_position()
    
    def test_position_persistence_round_trip(self, game_window):
        """Test that window position is preserved after save/restore (Requirement 9.5)."""
        if PYQT_VERSION == 0:
            pytest.skip("PyQt not available")
        
        try:
            from PyQt6.QtCore import QSettings
        except ImportError:
            from PyQt5.QtCore import QSettings
        
        # Set a specific position and size
        game_window.move(100, 150)
        game_window.resize(900, 700)
        
        # Save the position
        game_window.save_position()
        
        # Change position
        game_window.move(500, 500)
        game_window.resize(400, 300)
        
        # Restore position
        game_window.restore_position()
        
        # Verify position was restored (with some tolerance for window decorations)
        pos = game_window.pos()
        size = game_window.size()
        
        # Position should be close to original (may vary slightly due to window manager)
        assert abs(pos.x() - 100) < 50
        assert abs(pos.y() - 150) < 50
        
        # Size should be close to original
        assert abs(size.width() - 900) < 50
        assert abs(size.height() - 700) < 50
    
    def test_restore_position_centers_when_no_saved_state(self, theme_manager, animation_engine, qtbot):
        """Test that window centers on screen when no saved position exists."""
        if PYQT_VERSION == 0:
            pytest.skip("PyQt not available")
        
        try:
            from PyQt6.QtCore import QSettings
        except ImportError:
            from PyQt5.QtCore import QSettings
        
        # Clear any saved settings
        settings = QSettings(GameWindow.SETTINGS_ORG, GameWindow.SETTINGS_APP)
        settings.clear()
        
        # Create a new window
        window = GameWindow(theme_manager, animation_engine)
        qtbot.addWidget(window)
        
        # Restore position (should center since no saved state)
        window.restore_position()
        
        # Window should be visible and have reasonable position
        # (exact centering depends on screen size)
        assert window.pos().x() >= 0
        assert window.pos().y() >= 0
        
        window.close()
    
    def test_close_event_saves_position(self, game_window):
        """Test that closing the window saves position (Requirement 9.5)."""
        if PYQT_VERSION == 0:
            pytest.skip("PyQt not available")
        
        try:
            from PyQt6.QtCore import QSettings
            from PyQt6.QtGui import QCloseEvent
        except ImportError:
            from PyQt5.QtCore import QSettings
            from PyQt5.QtGui import QCloseEvent
        
        # Set a specific position
        game_window.move(200, 250)
        game_window.resize(850, 650)
        
        # Trigger close event
        close_event = QCloseEvent()
        game_window.closeEvent(close_event)
        
        # Verify settings were saved
        settings = QSettings(GameWindow.SETTINGS_ORG, GameWindow.SETTINGS_APP)
        geometry = settings.value("geometry")
        
        assert geometry is not None


# Test Minimize to Tray

class TestMinimizeToTray:
    """Tests for minimize to tray functionality (Requirement 9.7)."""
    
    def test_minimize_to_tray(self, game_window):
        """Test minimizing to system tray (Requirement 9.7)."""
        if PYQT_VERSION == 0:
            pytest.skip("PyQt not available")
        
        # Should not raise an error even if tray is not available
        game_window.minimize_to_tray()
    
    def test_minimize_to_tray_hides_window(self, game_window):
        """Test that minimize_to_tray hides the window (Requirement 9.7)."""
        if PYQT_VERSION == 0:
            pytest.skip("PyQt not available")
        
        # Show the window first
        game_window.show()
        
        # Minimize to tray
        game_window.minimize_to_tray()
        
        # Window should be hidden (or minimized if tray not available)
        # Note: isVisible() may still return True if minimized normally
        # The key is that the window is not in normal visible state
        if game_window._tray_icon is not None:
            assert not game_window.isVisible()
    
    def test_minimize_to_tray_shows_tray_icon(self, game_window):
        """Test that minimize_to_tray shows the tray icon (Requirement 9.7)."""
        if PYQT_VERSION == 0:
            pytest.skip("PyQt not available")
        
        try:
            from PyQt6.QtWidgets import QSystemTrayIcon
        except ImportError:
            from PyQt5.QtWidgets import QSystemTrayIcon
        
        # Skip if system tray is not available
        if not QSystemTrayIcon.isSystemTrayAvailable():
            pytest.skip("System tray not available")
        
        # Show the window first
        game_window.show()
        
        # Minimize to tray
        game_window.minimize_to_tray()
        
        # Tray icon should be visible
        if game_window._tray_icon is not None:
            assert game_window._tray_icon.isVisible()
    
    def test_restore_from_tray(self, game_window):
        """Test restoring window from system tray (Requirement 9.7)."""
        if PYQT_VERSION == 0:
            pytest.skip("PyQt not available")
        
        try:
            from PyQt6.QtWidgets import QSystemTrayIcon
        except ImportError:
            from PyQt5.QtWidgets import QSystemTrayIcon
        
        # Skip if system tray is not available
        if not QSystemTrayIcon.isSystemTrayAvailable():
            pytest.skip("System tray not available")
        
        # Show, minimize, then restore
        game_window.show()
        game_window.minimize_to_tray()
        game_window._restore_from_tray()
        
        # Window should be visible again
        assert game_window.isVisible()
        
        # Tray icon should be hidden
        if game_window._tray_icon is not None:
            assert not game_window._tray_icon.isVisible()
    
    def test_minimize_to_tray_fallback_when_tray_unavailable(self, theme_manager, animation_engine, qtbot):
        """Test that minimize_to_tray falls back to normal minimize when tray unavailable."""
        if PYQT_VERSION == 0:
            pytest.skip("PyQt not available")
        
        # Create window and manually set tray_icon to None to simulate unavailable tray
        window = GameWindow(theme_manager, animation_engine)
        qtbot.addWidget(window)
        window._tray_icon = None
        
        # Show the window
        window.show()
        
        # Minimize to tray should fall back to normal minimize
        window.minimize_to_tray()
        
        # Window should be minimized (not hidden)
        assert window.isMinimized()
        
        window.close()


# Test Window Continues Functioning When Closed (Requirement 9.6)

class TestWindowCloseBehavior:
    """Tests for window close behavior (Requirement 9.6)."""
    
    def test_close_event_emits_signal(self, game_window):
        """Test that closing window emits window_closed signal (Requirement 9.6)."""
        if PYQT_VERSION == 0:
            pytest.skip("PyQt not available")
        
        try:
            from PyQt6.QtGui import QCloseEvent
        except ImportError:
            from PyQt5.QtGui import QCloseEvent
        
        # Track if signal was emitted
        signal_received = []
        game_window.window_closed.connect(lambda: signal_received.append(True))
        
        # Trigger close event
        close_event = QCloseEvent()
        game_window.closeEvent(close_event)
        
        # Signal should have been emitted
        assert len(signal_received) == 1
    
    def test_close_event_stops_animation(self, game_window):
        """Test that closing window stops any running animation."""
        if PYQT_VERSION == 0:
            pytest.skip("PyQt not available")
        
        try:
            from PyQt6.QtGui import QCloseEvent
        except ImportError:
            from PyQt5.QtGui import QCloseEvent
        
        # Mock the animation engine
        game_window.animation_engine.stop_animation = MagicMock()
        
        # Trigger close event
        close_event = QCloseEvent()
        game_window.closeEvent(close_event)
        
        # Animation should be stopped
        game_window.animation_engine.stop_animation.assert_called_once()
    
    def test_close_event_hides_tray_icon(self, game_window):
        """Test that closing window hides tray icon."""
        if PYQT_VERSION == 0:
            pytest.skip("PyQt not available")
        
        try:
            from PyQt6.QtGui import QCloseEvent
        except ImportError:
            from PyQt5.QtGui import QCloseEvent
        
        # Mock the tray icon if it exists
        if game_window._tray_icon is not None:
            game_window._tray_icon.hide = MagicMock()
        
        # Trigger close event
        close_event = QCloseEvent()
        game_window.closeEvent(close_event)
        
        # Tray icon should be hidden
        if game_window._tray_icon is not None:
            game_window._tray_icon.hide.assert_called()


# Test StatsBar

class TestStatsBar:
    """Tests for the StatsBar widget."""
    
    def test_create_stats_bar(self):
        """Test creating a StatsBar."""
        if PYQT_VERSION == 0:
            pytest.skip("PyQt not available")
        
        stats_bar = StatsBar()
        assert stats_bar is not None
    
    def test_update_stats(self, sample_progression_state):
        """Test updating stats bar with progression state."""
        if PYQT_VERSION == 0:
            pytest.skip("PyQt not available")
        
        stats_bar = StatsBar()
        
        # Should not raise an error
        stats_bar.update_stats(sample_progression_state, Theme.MARIO)


# Test AspectRatioWidget

class TestAspectRatioWidget:
    """Tests for the AspectRatioWidget."""
    
    def test_create_aspect_ratio_widget(self):
        """Test creating an AspectRatioWidget."""
        if PYQT_VERSION == 0:
            pytest.skip("PyQt not available")
        
        widget = AspectRatioWidget(16/9)
        assert widget is not None
        assert widget.aspect_ratio == pytest.approx(16/9, rel=0.01)
    
    def test_set_aspect_ratio(self):
        """Test setting aspect ratio."""
        if PYQT_VERSION == 0:
            pytest.skip("PyQt not available")
        
        widget = AspectRatioWidget(16/9)
        widget.set_aspect_ratio(4/3)
        assert widget.aspect_ratio == pytest.approx(4/3, rel=0.01)
    
    def test_set_content(self):
        """Test setting content widget."""
        if PYQT_VERSION == 0:
            pytest.skip("PyQt not available")
        
        try:
            from PyQt6.QtWidgets import QLabel
        except ImportError:
            from PyQt5.QtWidgets import QLabel
        
        widget = AspectRatioWidget(16/9)
        content = QLabel("Test")
        
        # Should not raise an error
        widget.set_content(content)


# Test Edge Cases

class TestEdgeCases:
    """Tests for edge cases and error handling."""
    
    def test_update_display_none_state(self, game_window):
        """Test that get_current_state returns None initially."""
        # Before any update, state should be None
        window = GameWindow(game_window.theme_manager, game_window.animation_engine)
        assert window.get_current_state() is None
        window.close()
    
    def test_show_animation_without_pyqt(self, theme_manager, animation_engine, sample_animation):
        """Test show_animation gracefully handles missing PyQt."""
        # This test verifies the code path when PyQt is not available
        # The actual behavior depends on PYQT_VERSION
        window = GameWindow(theme_manager, animation_engine)
        
        # Mock the animation engine
        window.animation_engine.play_animation = MagicMock()
        
        # Should not raise an error
        window.show_animation(sample_animation)
        
        window.close()
    
    def test_switch_theme_updates_stats_with_state(self, game_window, sample_progression_state):
        """Test that theme switch updates stats bar when state exists."""
        if PYQT_VERSION == 0:
            pytest.skip("PyQt not available")
        
        # First set a state
        game_window.update_display(sample_progression_state)
        
        # Mock the stats bar
        game_window._stats_bar.update_stats = MagicMock()
        
        # Switch theme
        game_window.switch_theme(Theme.DKC)
        
        # Stats bar should be updated with new theme
        game_window._stats_bar.update_stats.assert_called()


# Test Integration

class TestIntegration:
    """Integration tests for GameWindow."""
    
    def test_full_workflow(self, game_window, sample_progression_state, sample_animation, sample_level):
        """Test a full workflow of using the GameWindow."""
        if PYQT_VERSION == 0:
            pytest.skip("PyQt not available")
        
        # Mock animation engine
        game_window.animation_engine.play_animation = MagicMock()
        
        # 1. Update display with initial state
        game_window.update_display(sample_progression_state)
        assert game_window.get_current_state() == sample_progression_state
        
        # 2. Play an animation
        game_window.show_animation(sample_animation)
        game_window.animation_engine.play_animation.assert_called()
        
        # 3. Switch theme
        game_window.switch_theme(Theme.ZELDA)
        assert game_window.get_current_theme() == Theme.ZELDA
        
        # 4. Show a level
        game_window.show_level(sample_level)
        assert game_window._current_level == sample_level
        
        # 5. Update state again
        new_state = ProgressionState(
            total_points=2000,
            total_cards_reviewed=120,
            correct_answers=100,
            current_streak=15,
            best_streak=25,
            levels_unlocked=4,
            levels_completed=3,
            session_accuracy=0.90,
            session_health=80,
        )
        game_window.update_display(new_state)
        assert game_window.get_current_state() == new_state
    
    def test_theme_manager_integration(self, mock_data_manager, animation_engine):
        """Test GameWindow integration with ThemeManager."""
        if PYQT_VERSION == 0:
            pytest.skip("PyQt not available")
        
        # Create theme manager and set initial theme
        tm = ThemeManager(mock_data_manager)
        tm.set_theme(Theme.MARIO)
        
        # Create game window
        window = GameWindow(tm, animation_engine)
        
        # Window should have same theme as manager
        assert window.get_current_theme() == Theme.MARIO
        
        # Change theme via window
        window.switch_theme(Theme.DKC)
        assert window.get_current_theme() == Theme.DKC
        
        window.close()
