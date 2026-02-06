"""
Tests for the SettingsPanel module.

This module contains unit tests for the SettingsPanel class and its
component widgets (DifficultySettingsWidget, RewardRateSettingsWidget,
AnimationSettingsWidget, AccessibilitySettingsWidget).

Requirements: 12.1, 12.2, 12.3, 12.4, 12.5, 12.6, 12.7
"""

import pytest
from pathlib import Path
from unittest.mock import MagicMock, patch
import sys
import tempfile

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from data.models import GameConfig
from data.config_manager import ConfigManager


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
def temp_config_path(tmp_path):
    """Create a temporary config path."""
    return tmp_path / "test_config.json"


@pytest.fixture
def config_manager(temp_config_path):
    """Create a ConfigManager instance with a temporary config file."""
    return ConfigManager(temp_config_path)


class TestSettingsPanelCreation:
    """Tests for SettingsPanel creation and initialization."""
    
    def test_settings_panel_can_be_created(self, qapp, config_manager):
        """Test that SettingsPanel can be instantiated.
        
        Requirements: 12.1, 12.2, 12.3, 12.4, 12.5, 12.6, 12.7
        """
        from ui.settings_panel import SettingsPanel
        
        panel = SettingsPanel(config_manager=config_manager)
        
        assert panel is not None
        panel.close()
    
    def test_settings_panel_has_tabbed_interface(self, qapp, config_manager):
        """Test that SettingsPanel has a tabbed interface with all required tabs.
        
        Requirements: 12.1, 12.2, 12.3, 12.5
        """
        from ui.settings_panel import SettingsPanel
        
        panel = SettingsPanel(config_manager=config_manager)
        
        # Check that all tabs exist
        assert panel._tab_widget.count() == 4
        
        # Verify tab names contain expected content
        tab_texts = [panel._tab_widget.tabText(i) for i in range(4)]
        assert any("Difficulty" in t for t in tab_texts)
        assert any("Reward" in t for t in tab_texts)
        assert any("Animation" in t for t in tab_texts)
        assert any("Accessibility" in t for t in tab_texts)
        
        panel.close()
    
    def test_settings_panel_loads_settings_on_creation(self, qapp, config_manager):
        """Test that SettingsPanel loads settings when created.
        
        Requirements: 12.1
        """
        from ui.settings_panel import SettingsPanel
        
        # Save custom config first
        custom_config = GameConfig(base_points=25)
        config_manager.save_config(custom_config)
        
        panel = SettingsPanel(config_manager=config_manager)
        
        # Verify settings were loaded
        difficulty = panel.get_difficulty_widget()
        assert difficulty._base_points_spin.value() == 25
        
        panel.close()


class TestDifficultySettings:
    """Tests for difficulty settings functionality.
    
    Requirements: 12.1
    """
    
    def test_difficulty_widget_displays_base_points(self, qapp, config_manager):
        """Test that difficulty widget displays base points setting.
        
        Requirements: 12.1
        """
        from ui.settings_panel import SettingsPanel
        
        panel = SettingsPanel(config_manager=config_manager)
        difficulty = panel.get_difficulty_widget()
        
        # Default should be 10
        assert difficulty._base_points_spin.value() == 10
        
        panel.close()
    
    def test_difficulty_widget_allows_base_points_adjustment(self, qapp, config_manager):
        """Test that base points can be adjusted.
        
        Requirements: 12.1
        """
        from ui.settings_panel import SettingsPanel
        
        panel = SettingsPanel(config_manager=config_manager)
        difficulty = panel.get_difficulty_widget()
        
        # Change base points
        difficulty._base_points_spin.setValue(20)
        
        settings = difficulty.get_settings()
        assert settings['base_points'] == 20
        
        panel.close()
    
    def test_difficulty_widget_displays_health_penalty(self, qapp, config_manager):
        """Test that difficulty widget displays health penalty setting.
        
        Requirements: 12.1
        """
        from ui.settings_panel import SettingsPanel
        
        panel = SettingsPanel(config_manager=config_manager)
        difficulty = panel.get_difficulty_widget()
        
        # Default should be 0.1 (10%)
        assert abs(difficulty._health_reduction_spin.value() - 0.1) < 0.01
        
        panel.close()
    
    def test_difficulty_widget_allows_penalty_adjustment(self, qapp, config_manager):
        """Test that penalty severity can be adjusted.
        
        Requirements: 12.1
        """
        from ui.settings_panel import SettingsPanel
        
        panel = SettingsPanel(config_manager=config_manager)
        difficulty = panel.get_difficulty_widget()
        
        # Change health reduction
        difficulty._health_reduction_spin.setValue(0.2)
        difficulty._currency_loss_spin.setValue(5)
        
        settings = difficulty.get_settings()
        assert abs(settings['penalty_health_reduction'] - 0.2) < 0.01
        assert settings['penalty_currency_loss'] == 5
        
        panel.close()
    
    def test_difficulty_settings_emit_change_signal(self, qapp, config_manager):
        """Test that changing difficulty settings emits a signal.
        
        Requirements: 12.1
        """
        from ui.settings_panel import SettingsPanel
        
        panel = SettingsPanel(config_manager=config_manager)
        
        # Initially no unsaved changes
        assert not panel.has_unsaved_changes()
        
        # Change a setting
        difficulty = panel.get_difficulty_widget()
        difficulty._base_points_spin.setValue(15)
        
        # Should now have unsaved changes
        assert panel.has_unsaved_changes()
        
        panel.close()


class TestRewardRateSettings:
    """Tests for reward rate settings functionality.
    
    Requirements: 12.2
    """
    
    def test_reward_widget_displays_streak_multipliers(self, qapp, config_manager):
        """Test that reward widget displays streak multiplier settings.
        
        Requirements: 12.2
        """
        from ui.settings_panel import SettingsPanel
        
        panel = SettingsPanel(config_manager=config_manager)
        reward = panel.get_reward_widget()
        
        # Check default multipliers
        assert abs(reward._mult_5_spin.value() - 1.5) < 0.1
        assert abs(reward._mult_10_spin.value() - 2.0) < 0.1
        assert abs(reward._mult_20_spin.value() - 3.0) < 0.1
        
        panel.close()
    
    def test_reward_widget_allows_multiplier_adjustment(self, qapp, config_manager):
        """Test that streak multipliers can be adjusted.
        
        Requirements: 12.2
        """
        from ui.settings_panel import SettingsPanel
        
        panel = SettingsPanel(config_manager=config_manager)
        reward = panel.get_reward_widget()
        
        # Change multipliers
        reward._mult_5_spin.setValue(1.8)
        reward._mult_10_spin.setValue(2.5)
        reward._mult_20_spin.setValue(4.0)
        
        settings = reward.get_settings()
        assert abs(settings['streak_multiplier_5'] - 1.8) < 0.1
        assert abs(settings['streak_multiplier_10'] - 2.5) < 0.1
        assert abs(settings['streak_multiplier_20'] - 4.0) < 0.1
        
        panel.close()
    
    def test_reward_widget_displays_accuracy_threshold(self, qapp, config_manager):
        """Test that reward widget displays accuracy threshold setting.
        
        Requirements: 12.2
        """
        from ui.settings_panel import SettingsPanel
        
        panel = SettingsPanel(config_manager=config_manager)
        reward = panel.get_reward_widget()
        
        # Default should be 0.9 (90%)
        assert abs(reward._accuracy_threshold_spin.value() - 0.9) < 0.01
        
        panel.close()
    
    def test_reward_widget_allows_threshold_adjustment(self, qapp, config_manager):
        """Test that unlock thresholds can be adjusted.
        
        Requirements: 12.2
        """
        from ui.settings_panel import SettingsPanel
        
        panel = SettingsPanel(config_manager=config_manager)
        reward = panel.get_reward_widget()
        
        # Change thresholds
        reward._cards_per_level_spin.setValue(75)
        reward._cards_per_powerup_spin.setValue(150)
        
        settings = reward.get_settings()
        assert settings['cards_per_level'] == 75
        assert settings['cards_per_powerup'] == 150
        
        panel.close()
    
    def test_reward_settings_emit_change_signal(self, qapp, config_manager):
        """Test that changing reward settings emits a signal.
        
        Requirements: 12.2
        """
        from ui.settings_panel import SettingsPanel
        
        panel = SettingsPanel(config_manager=config_manager)
        
        # Initially no unsaved changes
        assert not panel.has_unsaved_changes()
        
        # Change a setting
        reward = panel.get_reward_widget()
        reward._mult_5_spin.setValue(2.0)
        
        # Should now have unsaved changes
        assert panel.has_unsaved_changes()
        
        panel.close()


class TestAnimationSettings:
    """Tests for animation settings functionality.
    
    Requirements: 12.3, 12.4
    """
    
    def test_animation_widget_displays_speed_setting(self, qapp, config_manager):
        """Test that animation widget displays speed setting.
        
        Requirements: 12.3
        """
        from ui.settings_panel import SettingsPanel
        
        panel = SettingsPanel(config_manager=config_manager)
        animation = panel.get_animation_widget()
        
        # Default speed should be 1.0x (100 on slider)
        assert animation._speed_slider.value() == 100
        
        panel.close()
    
    def test_animation_widget_allows_speed_adjustment(self, qapp, config_manager):
        """Test that animation speed can be adjusted.
        
        Requirements: 12.3
        """
        from ui.settings_panel import SettingsPanel
        
        panel = SettingsPanel(config_manager=config_manager)
        animation = panel.get_animation_widget()
        
        # Change speed to 1.5x
        animation._speed_slider.setValue(150)
        
        settings = animation.get_settings()
        assert abs(settings['animation_speed'] - 1.5) < 0.01
        
        panel.close()
    
    def test_animation_widget_displays_enable_toggle(self, qapp, config_manager):
        """Test that animation widget displays enable/disable toggle.
        
        Requirements: 12.4
        """
        from ui.settings_panel import SettingsPanel
        
        panel = SettingsPanel(config_manager=config_manager)
        animation = panel.get_animation_widget()
        
        # Default should be enabled
        assert animation._animations_enabled_check.isChecked()
        
        panel.close()
    
    def test_animation_widget_allows_disable(self, qapp, config_manager):
        """Test that animations can be disabled (stats-only mode).
        
        Requirements: 12.4
        """
        from ui.settings_panel import SettingsPanel
        
        panel = SettingsPanel(config_manager=config_manager)
        animation = panel.get_animation_widget()
        
        # Disable animations
        animation._animations_enabled_check.setChecked(False)
        
        settings = animation.get_settings()
        assert settings['animations_enabled'] is False
        
        panel.close()
    
    def test_stats_only_mode_when_animations_disabled(self, qapp, config_manager):
        """Test that stats-only mode is active when animations are disabled.
        
        Requirements: 12.4
        """
        from ui.settings_panel import SettingsPanel
        
        panel = SettingsPanel(config_manager=config_manager)
        animation = panel.get_animation_widget()
        
        # Initially not in stats-only mode
        assert not animation.is_stats_only_mode()
        assert not panel.is_stats_only_mode()
        
        # Disable animations
        animation._animations_enabled_check.setChecked(False)
        
        # Now in stats-only mode
        assert animation.is_stats_only_mode()
        assert panel.is_stats_only_mode()
        
        panel.close()
    
    def test_speed_slider_disabled_when_animations_disabled(self, qapp, config_manager):
        """Test that speed slider is disabled when animations are disabled.
        
        Requirements: 12.4
        """
        from ui.settings_panel import SettingsPanel
        
        panel = SettingsPanel(config_manager=config_manager)
        animation = panel.get_animation_widget()
        
        # Initially enabled
        assert animation._speed_slider.isEnabled()
        
        # Disable animations
        animation._animations_enabled_check.setChecked(False)
        
        # Speed slider should be disabled
        assert not animation._speed_slider.isEnabled()
        
        panel.close()
    
    def test_animation_settings_emit_change_signal(self, qapp, config_manager):
        """Test that changing animation settings emits a signal.
        
        Requirements: 12.3
        """
        from ui.settings_panel import SettingsPanel
        
        panel = SettingsPanel(config_manager=config_manager)
        
        # Initially no unsaved changes
        assert not panel.has_unsaved_changes()
        
        # Change a setting
        animation = panel.get_animation_widget()
        animation._speed_slider.setValue(75)
        
        # Should now have unsaved changes
        assert panel.has_unsaved_changes()
        
        panel.close()


class TestAccessibilitySettings:
    """Tests for accessibility settings functionality.
    
    Requirements: 12.5, 12.6, 12.7
    """
    
    def test_accessibility_widget_displays_colorblind_options(self, qapp, config_manager):
        """Test that accessibility widget displays colorblind mode options.
        
        Requirements: 12.5
        """
        from ui.settings_panel import SettingsPanel
        
        panel = SettingsPanel(config_manager=config_manager)
        accessibility = panel.get_accessibility_widget()
        
        # Should have 4 options: Normal, Deuteranopia, Protanopia, Tritanopia
        assert accessibility._colorblind_combo.count() == 4
        
        panel.close()
    
    def test_accessibility_widget_allows_colorblind_mode_selection(self, qapp, config_manager):
        """Test that colorblind mode can be selected.
        
        Requirements: 12.5
        """
        from ui.settings_panel import SettingsPanel
        
        panel = SettingsPanel(config_manager=config_manager)
        accessibility = panel.get_accessibility_widget()
        
        # Select deuteranopia
        accessibility._colorblind_combo.setCurrentIndex(1)
        
        settings = accessibility.get_settings()
        assert settings['colorblind_mode'] == "deuteranopia"
        
        # Select protanopia
        accessibility._colorblind_combo.setCurrentIndex(2)
        
        settings = accessibility.get_settings()
        assert settings['colorblind_mode'] == "protanopia"
        
        # Select tritanopia
        accessibility._colorblind_combo.setCurrentIndex(3)
        
        settings = accessibility.get_settings()
        assert settings['colorblind_mode'] == "tritanopia"
        
        panel.close()
    
    def test_accessibility_widget_displays_sound_toggle(self, qapp, config_manager):
        """Test that accessibility widget displays sound enable/disable toggle.
        
        Requirements: 12.6
        """
        from ui.settings_panel import SettingsPanel
        
        panel = SettingsPanel(config_manager=config_manager)
        accessibility = panel.get_accessibility_widget()
        
        # Default should be enabled
        assert accessibility._sound_enabled_check.isChecked()
        
        panel.close()
    
    def test_accessibility_widget_allows_sound_disable(self, qapp, config_manager):
        """Test that sound effects can be disabled.
        
        Requirements: 12.6
        """
        from ui.settings_panel import SettingsPanel
        
        panel = SettingsPanel(config_manager=config_manager)
        accessibility = panel.get_accessibility_widget()
        
        # Disable sound
        accessibility._sound_enabled_check.setChecked(False)
        
        settings = accessibility.get_settings()
        assert settings['sound_enabled'] is False
        
        panel.close()
    
    def test_accessibility_widget_displays_volume_slider(self, qapp, config_manager):
        """Test that accessibility widget displays volume slider.
        
        Requirements: 12.7
        """
        from ui.settings_panel import SettingsPanel
        
        panel = SettingsPanel(config_manager=config_manager)
        accessibility = panel.get_accessibility_widget()
        
        # Default volume should be 70%
        assert accessibility._volume_slider.value() == 70
        
        panel.close()
    
    def test_accessibility_widget_allows_volume_adjustment(self, qapp, config_manager):
        """Test that sound volume can be adjusted.
        
        Requirements: 12.7
        """
        from ui.settings_panel import SettingsPanel
        
        panel = SettingsPanel(config_manager=config_manager)
        accessibility = panel.get_accessibility_widget()
        
        # Change volume to 50%
        accessibility._volume_slider.setValue(50)
        
        settings = accessibility.get_settings()
        assert abs(settings['sound_volume'] - 0.5) < 0.01
        
        panel.close()
    
    def test_volume_slider_disabled_when_sound_disabled(self, qapp, config_manager):
        """Test that volume slider is disabled when sound is disabled.
        
        Requirements: 12.6, 12.7
        """
        from ui.settings_panel import SettingsPanel
        
        panel = SettingsPanel(config_manager=config_manager)
        accessibility = panel.get_accessibility_widget()
        
        # Initially enabled
        assert accessibility._volume_slider.isEnabled()
        
        # Disable sound
        accessibility._sound_enabled_check.setChecked(False)
        
        # Volume slider should be disabled
        assert not accessibility._volume_slider.isEnabled()
        
        panel.close()
    
    def test_accessibility_settings_emit_change_signal(self, qapp, config_manager):
        """Test that changing accessibility settings emits a signal.
        
        Requirements: 12.5
        """
        from ui.settings_panel import SettingsPanel
        
        panel = SettingsPanel(config_manager=config_manager)
        
        # Initially no unsaved changes
        assert not panel.has_unsaved_changes()
        
        # Change a setting
        accessibility = panel.get_accessibility_widget()
        accessibility._colorblind_combo.setCurrentIndex(1)
        
        # Should now have unsaved changes
        assert panel.has_unsaved_changes()
        
        panel.close()


class TestSettingsPersistence:
    """Tests for settings save and load functionality."""
    
    def test_save_settings_persists_to_config(self, qapp, config_manager):
        """Test that save_settings persists settings to config file.
        
        Requirements: 12.1, 12.2, 12.3, 12.5, 12.6, 12.7
        """
        from ui.settings_panel import SettingsPanel
        
        panel = SettingsPanel(config_manager=config_manager)
        
        # Change some settings
        difficulty = panel.get_difficulty_widget()
        difficulty._base_points_spin.setValue(25)
        
        reward = panel.get_reward_widget()
        reward._mult_5_spin.setValue(2.0)
        
        animation = panel.get_animation_widget()
        animation._speed_slider.setValue(150)
        
        accessibility = panel.get_accessibility_widget()
        accessibility._colorblind_combo.setCurrentIndex(1)  # deuteranopia
        accessibility._volume_slider.setValue(50)
        
        # Save settings (mock the message box)
        with patch.object(panel, 'settings_saved') as mock_signal:
            with patch('ui.settings_panel.QMessageBox.information'):
                panel.save_settings()
        
        # Verify settings were saved
        config = config_manager.load_config()
        assert config.base_points == 25
        assert abs(config.streak_multiplier_5 - 2.0) < 0.1
        assert abs(config.animation_speed - 1.5) < 0.01
        assert config.colorblind_mode == "deuteranopia"
        assert abs(config.sound_volume - 0.5) < 0.01
        
        panel.close()
    
    def test_load_settings_restores_from_config(self, qapp, config_manager):
        """Test that load_settings restores settings from config file.
        
        Requirements: 12.1, 12.2, 12.3, 12.5, 12.6, 12.7
        """
        from ui.settings_panel import SettingsPanel
        
        # Save custom config
        custom_config = GameConfig(
            base_points=30,
            streak_multiplier_5=1.8,
            animation_speed=0.75,
            colorblind_mode="protanopia",
            sound_volume=0.3
        )
        config_manager.save_config(custom_config)
        
        # Create panel - should load settings
        panel = SettingsPanel(config_manager=config_manager)
        
        # Verify settings were loaded
        difficulty = panel.get_difficulty_widget()
        assert difficulty._base_points_spin.value() == 30
        
        reward = panel.get_reward_widget()
        assert abs(reward._mult_5_spin.value() - 1.8) < 0.1
        
        animation = panel.get_animation_widget()
        assert animation._speed_slider.value() == 75
        
        accessibility = panel.get_accessibility_widget()
        assert accessibility._colorblind_combo.currentData() == "protanopia"
        assert accessibility._volume_slider.value() == 30
        
        panel.close()
    
    def test_reset_to_defaults_restores_default_values(self, qapp, config_manager):
        """Test that reset_to_defaults restores default values.
        
        Requirements: 12.1, 12.2, 12.3, 12.5, 12.6, 12.7
        """
        from ui.settings_panel import SettingsPanel
        
        if PYQT_VERSION == 6:
            from PyQt6.QtWidgets import QMessageBox
            yes_value = QMessageBox.StandardButton.Yes
        else:
            from PyQt5.QtWidgets import QMessageBox
            yes_value = QMessageBox.Yes
        
        # Save custom config
        custom_config = GameConfig(
            base_points=50,
            streak_multiplier_5=3.0,
            animation_speed=2.0,
            colorblind_mode="tritanopia",
            sound_volume=0.1
        )
        config_manager.save_config(custom_config)
        
        panel = SettingsPanel(config_manager=config_manager)
        
        # Reset to defaults (mock the message boxes)
        with patch('ui.settings_panel.QMessageBox.question', return_value=yes_value):
            with patch('ui.settings_panel.QMessageBox.information'):
                panel.reset_to_defaults()
        
        # Verify default values
        difficulty = panel.get_difficulty_widget()
        assert difficulty._base_points_spin.value() == 10
        
        reward = panel.get_reward_widget()
        assert abs(reward._mult_5_spin.value() - 1.5) < 0.1
        
        animation = panel.get_animation_widget()
        assert animation._speed_slider.value() == 100
        
        accessibility = panel.get_accessibility_widget()
        assert accessibility._colorblind_combo.currentData() is None
        assert accessibility._volume_slider.value() == 70
        
        panel.close()


class TestUnsavedChangesHandling:
    """Tests for unsaved changes handling."""
    
    def test_unsaved_changes_indicator_hidden_initially(self, qapp, config_manager):
        """Test that unsaved changes indicator is hidden initially."""
        from ui.settings_panel import SettingsPanel
        
        panel = SettingsPanel(config_manager=config_manager)
        
        assert not panel._unsaved_label.isVisible()
        
        panel.close()
    
    def test_unsaved_changes_indicator_shown_after_change(self, qapp, config_manager):
        """Test that unsaved changes indicator is shown after a change."""
        from ui.settings_panel import SettingsPanel
        
        panel = SettingsPanel(config_manager=config_manager)
        
        # Make a change
        difficulty = panel.get_difficulty_widget()
        difficulty._base_points_spin.setValue(15)
        
        # Check internal state (visibility depends on widget being shown)
        assert panel.has_unsaved_changes()
        
        panel.close()
    
    def test_unsaved_changes_indicator_hidden_after_save(self, qapp, config_manager):
        """Test that unsaved changes indicator is hidden after save."""
        from ui.settings_panel import SettingsPanel
        
        panel = SettingsPanel(config_manager=config_manager)
        
        # Make a change
        difficulty = panel.get_difficulty_widget()
        difficulty._base_points_spin.setValue(15)
        
        # Verify change was tracked
        assert panel.has_unsaved_changes()
        
        # Save (mock the message box)
        with patch('ui.settings_panel.QMessageBox.information'):
            panel.save_settings()
        
        # Verify no more unsaved changes
        assert not panel.has_unsaved_changes()
        
        panel.close()
    
    def test_has_unsaved_changes_returns_correct_state(self, qapp, config_manager):
        """Test that has_unsaved_changes returns correct state."""
        from ui.settings_panel import SettingsPanel
        
        panel = SettingsPanel(config_manager=config_manager)
        
        # Initially no changes
        assert not panel.has_unsaved_changes()
        
        # Make a change
        difficulty = panel.get_difficulty_widget()
        difficulty._base_points_spin.setValue(15)
        
        # Now has changes
        assert panel.has_unsaved_changes()
        
        # Save
        with patch('ui.settings_panel.QMessageBox.information'):
            panel.save_settings()
        
        # No more changes
        assert not panel.has_unsaved_changes()
        
        panel.close()


class TestWidgetUnit:
    """Unit tests for individual settings widgets."""
    
    def test_difficulty_widget_creation(self, qapp):
        """Test DifficultySettingsWidget can be created."""
        from ui.settings_panel import DifficultySettingsWidget
        
        widget = DifficultySettingsWidget()
        assert widget is not None
    
    def test_difficulty_widget_get_settings(self, qapp):
        """Test DifficultySettingsWidget.get_settings method."""
        from ui.settings_panel import DifficultySettingsWidget
        
        widget = DifficultySettingsWidget()
        widget._base_points_spin.setValue(15)
        widget._health_reduction_spin.setValue(0.15)
        widget._currency_loss_spin.setValue(3)
        
        settings = widget.get_settings()
        assert settings['base_points'] == 15
        assert abs(settings['penalty_health_reduction'] - 0.15) < 0.01
        assert settings['penalty_currency_loss'] == 3
    
    def test_difficulty_widget_set_settings(self, qapp):
        """Test DifficultySettingsWidget.set_settings method."""
        from ui.settings_panel import DifficultySettingsWidget
        
        widget = DifficultySettingsWidget()
        config = GameConfig(
            base_points=20,
            penalty_health_reduction=0.25,
            penalty_currency_loss=5
        )
        
        widget.set_settings(config)
        
        assert widget._base_points_spin.value() == 20
        assert abs(widget._health_reduction_spin.value() - 0.25) < 0.01
        assert widget._currency_loss_spin.value() == 5
    
    def test_reward_widget_creation(self, qapp):
        """Test RewardRateSettingsWidget can be created."""
        from ui.settings_panel import RewardRateSettingsWidget
        
        widget = RewardRateSettingsWidget()
        assert widget is not None
    
    def test_reward_widget_get_settings(self, qapp):
        """Test RewardRateSettingsWidget.get_settings method."""
        from ui.settings_panel import RewardRateSettingsWidget
        
        widget = RewardRateSettingsWidget()
        widget._mult_5_spin.setValue(1.8)
        widget._mult_10_spin.setValue(2.5)
        widget._mult_20_spin.setValue(4.0)
        widget._accuracy_threshold_spin.setValue(0.85)
        widget._accuracy_mult_spin.setValue(1.5)
        widget._cards_per_level_spin.setValue(75)
        widget._cards_per_powerup_spin.setValue(150)
        
        settings = widget.get_settings()
        assert abs(settings['streak_multiplier_5'] - 1.8) < 0.1
        assert abs(settings['streak_multiplier_10'] - 2.5) < 0.1
        assert abs(settings['streak_multiplier_20'] - 4.0) < 0.1
        assert abs(settings['accuracy_bonus_threshold'] - 0.85) < 0.01
        assert abs(settings['accuracy_bonus_multiplier'] - 1.5) < 0.01
        assert settings['cards_per_level'] == 75
        assert settings['cards_per_powerup'] == 150

    def test_reward_widget_set_settings(self, qapp):
        """Test RewardRateSettingsWidget.set_settings method."""
        from ui.settings_panel import RewardRateSettingsWidget
        
        widget = RewardRateSettingsWidget()
        config = GameConfig(
            streak_multiplier_5=2.0,
            streak_multiplier_10=3.0,
            streak_multiplier_20=4.5,
            accuracy_bonus_threshold=0.95,
            accuracy_bonus_multiplier=1.75,
            cards_per_level=100,
            cards_per_powerup=200
        )
        
        widget.set_settings(config)
        
        assert abs(widget._mult_5_spin.value() - 2.0) < 0.1
        assert abs(widget._mult_10_spin.value() - 3.0) < 0.1
        assert abs(widget._mult_20_spin.value() - 4.5) < 0.1
        assert abs(widget._accuracy_threshold_spin.value() - 0.95) < 0.01
        assert abs(widget._accuracy_mult_spin.value() - 1.75) < 0.01
        assert widget._cards_per_level_spin.value() == 100
        assert widget._cards_per_powerup_spin.value() == 200
    
    def test_animation_widget_creation(self, qapp):
        """Test AnimationSettingsWidget can be created."""
        from ui.settings_panel import AnimationSettingsWidget
        
        widget = AnimationSettingsWidget()
        assert widget is not None
    
    def test_animation_widget_get_settings(self, qapp):
        """Test AnimationSettingsWidget.get_settings method."""
        from ui.settings_panel import AnimationSettingsWidget
        
        widget = AnimationSettingsWidget()
        widget._animations_enabled_check.setChecked(False)
        widget._speed_slider.setValue(75)
        
        settings = widget.get_settings()
        assert settings['animations_enabled'] is False
        assert abs(settings['animation_speed'] - 0.75) < 0.01
    
    def test_animation_widget_set_settings(self, qapp):
        """Test AnimationSettingsWidget.set_settings method."""
        from ui.settings_panel import AnimationSettingsWidget
        
        widget = AnimationSettingsWidget()
        config = GameConfig(
            animations_enabled=False,
            animation_speed=1.5
        )
        
        widget.set_settings(config)
        
        assert not widget._animations_enabled_check.isChecked()
        assert widget._speed_slider.value() == 150
    
    def test_accessibility_widget_creation(self, qapp):
        """Test AccessibilitySettingsWidget can be created."""
        from ui.settings_panel import AccessibilitySettingsWidget
        
        widget = AccessibilitySettingsWidget()
        assert widget is not None
    
    def test_accessibility_widget_get_settings(self, qapp):
        """Test AccessibilitySettingsWidget.get_settings method."""
        from ui.settings_panel import AccessibilitySettingsWidget
        
        widget = AccessibilitySettingsWidget()
        widget._colorblind_combo.setCurrentIndex(2)  # protanopia
        widget._sound_enabled_check.setChecked(False)
        widget._volume_slider.setValue(40)
        
        settings = widget.get_settings()
        assert settings['colorblind_mode'] == "protanopia"
        assert settings['sound_enabled'] is False
        assert abs(settings['sound_volume'] - 0.4) < 0.01
    
    def test_accessibility_widget_set_settings(self, qapp):
        """Test AccessibilitySettingsWidget.set_settings method."""
        from ui.settings_panel import AccessibilitySettingsWidget
        
        widget = AccessibilitySettingsWidget()
        config = GameConfig(
            colorblind_mode="tritanopia",
            sound_enabled=False,
            sound_volume=0.25
        )
        
        widget.set_settings(config)
        
        assert widget._colorblind_combo.currentData() == "tritanopia"
        assert not widget._sound_enabled_check.isChecked()
        assert widget._volume_slider.value() == 25


class TestTabNavigation:
    """Tests for tab navigation functionality."""
    
    def test_get_current_tab_index(self, qapp, config_manager):
        """Test get_current_tab_index method."""
        from ui.settings_panel import SettingsPanel
        
        panel = SettingsPanel(config_manager=config_manager)
        
        # Default should be first tab (0)
        assert panel.get_current_tab_index() == 0
        
        # Switch to second tab
        panel._tab_widget.setCurrentIndex(1)
        assert panel.get_current_tab_index() == 1
        
        # Switch to third tab
        panel._tab_widget.setCurrentIndex(2)
        assert panel.get_current_tab_index() == 2
        
        # Switch to fourth tab
        panel._tab_widget.setCurrentIndex(3)
        assert panel.get_current_tab_index() == 3
        
        panel.close()
