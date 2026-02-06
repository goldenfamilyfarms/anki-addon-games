"""
SettingsPanel for NintendAnki.

This module implements the SettingsPanel class, a PyQt QDialog that allows
users to customize game settings including difficulty, reward rates,
animation settings, and accessibility options.

Requirements: 12.1, 12.2, 12.3, 12.4, 12.5, 12.6, 12.7
"""

import logging
from typing import Optional

from data.models import GameConfig
from data.config_manager import ConfigManager

logger = logging.getLogger(__name__)

# Try to import PyQt6 first, then fall back to PyQt5
try:
    from PyQt6.QtWidgets import (
        QDialog, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
        QTabWidget, QPushButton, QScrollArea, QFrame,
        QGridLayout, QGroupBox, QSpinBox, QDoubleSpinBox,
        QSlider, QCheckBox, QComboBox, QMessageBox,
    )
    from PyQt6.QtCore import Qt, pyqtSignal
    PYQT_VERSION = 6
except ImportError:
    try:
        from PyQt5.QtWidgets import (
            QDialog, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
            QTabWidget, QPushButton, QScrollArea, QFrame,
            QGridLayout, QGroupBox, QSpinBox, QDoubleSpinBox,
            QSlider, QCheckBox, QComboBox, QMessageBox,
        )
        from PyQt5.QtCore import Qt, pyqtSignal
        PYQT_VERSION = 5
    except ImportError:
        PYQT_VERSION = 0
        logger.warning("PyQt not available - SettingsPanel will have limited functionality")


# Define base classes based on PyQt availability
if PYQT_VERSION > 0:
    _WidgetBase = QWidget
    _DialogBase = QDialog
else:
    _WidgetBase = object
    _DialogBase = object


class DifficultySettingsWidget(_WidgetBase):
    """Widget for difficulty settings (points, penalties).
    
    Requirements: 12.1
    """
    
    if PYQT_VERSION > 0:
        settings_changed = pyqtSignal()
    
    def __init__(self, parent: Optional[QWidget] = None):
        if PYQT_VERSION == 0:
            return
        super().__init__(parent)
        self._setup_ui()
    
    def _setup_ui(self) -> None:
        if PYQT_VERSION == 0:
            return
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        
        # Points Settings Group
        points_group = QGroupBox("Point Values")
        points_layout = QGridLayout(points_group)
        points_layout.setSpacing(10)
        
        # Base points
        points_layout.addWidget(QLabel("Base Points per Correct Answer:"), 0, 0)
        self._base_points_spin = QSpinBox()
        self._base_points_spin.setRange(1, 100)
        self._base_points_spin.setValue(10)
        self._base_points_spin.setToolTip("Points awarded for each correct answer")
        self._base_points_spin.valueChanged.connect(self._on_setting_changed)
        points_layout.addWidget(self._base_points_spin, 0, 1)
        
        layout.addWidget(points_group)
        
        # Penalty Settings Group
        penalty_group = QGroupBox("Penalty Settings")
        penalty_layout = QGridLayout(penalty_group)
        penalty_layout.setSpacing(10)
        
        # Health reduction
        penalty_layout.addWidget(QLabel("Health Reduction per Wrong Answer:"), 0, 0)
        self._health_reduction_spin = QDoubleSpinBox()
        self._health_reduction_spin.setRange(0.01, 0.5)
        self._health_reduction_spin.setSingleStep(0.01)
        self._health_reduction_spin.setValue(0.1)
        self._health_reduction_spin.setDecimals(2)
        self._health_reduction_spin.setSuffix(" (10% = 0.10)")
        self._health_reduction_spin.setToolTip("Percentage of health lost for wrong answers")
        self._health_reduction_spin.valueChanged.connect(self._on_setting_changed)
        penalty_layout.addWidget(self._health_reduction_spin, 0, 1)
        
        # Currency loss
        penalty_layout.addWidget(QLabel("Currency Lost per Wrong Answer:"), 1, 0)
        self._currency_loss_spin = QSpinBox()
        self._currency_loss_spin.setRange(0, 50)
        self._currency_loss_spin.setValue(1)
        self._currency_loss_spin.setToolTip("Amount of currency lost for wrong answers")
        self._currency_loss_spin.valueChanged.connect(self._on_setting_changed)
        penalty_layout.addWidget(self._currency_loss_spin, 1, 1)
        
        layout.addWidget(penalty_group)
        layout.addStretch()
    
    def _on_setting_changed(self) -> None:
        if PYQT_VERSION > 0:
            self.settings_changed.emit()
    
    def get_settings(self) -> dict:
        """Get current difficulty settings."""
        if PYQT_VERSION == 0:
            return {}
        return {
            'base_points': self._base_points_spin.value(),
            'penalty_health_reduction': self._health_reduction_spin.value(),
            'penalty_currency_loss': self._currency_loss_spin.value(),
        }
    
    def set_settings(self, config: GameConfig) -> None:
        """Set difficulty settings from config."""
        if PYQT_VERSION == 0:
            return
        self._base_points_spin.setValue(config.base_points)
        self._health_reduction_spin.setValue(config.penalty_health_reduction)
        self._currency_loss_spin.setValue(config.penalty_currency_loss)


class RewardRateSettingsWidget(_WidgetBase):
    """Widget for reward rate settings (multipliers, thresholds).
    
    Requirements: 12.2
    """
    
    if PYQT_VERSION > 0:
        settings_changed = pyqtSignal()
    
    def __init__(self, parent: Optional[QWidget] = None):
        if PYQT_VERSION == 0:
            return
        super().__init__(parent)
        self._setup_ui()
    
    def _setup_ui(self) -> None:
        if PYQT_VERSION == 0:
            return
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        
        # Streak Multipliers Group
        multiplier_group = QGroupBox("Streak Multipliers")
        multiplier_layout = QGridLayout(multiplier_group)
        multiplier_layout.setSpacing(10)
        
        # 5+ streak multiplier
        multiplier_layout.addWidget(QLabel("5+ Streak Multiplier:"), 0, 0)
        self._mult_5_spin = QDoubleSpinBox()
        self._mult_5_spin.setRange(1.0, 5.0)
        self._mult_5_spin.setSingleStep(0.1)
        self._mult_5_spin.setValue(1.5)
        self._mult_5_spin.setDecimals(1)
        self._mult_5_spin.setSuffix("x")
        self._mult_5_spin.setToolTip("Point multiplier at 5+ correct streak")
        self._mult_5_spin.valueChanged.connect(self._on_setting_changed)
        multiplier_layout.addWidget(self._mult_5_spin, 0, 1)
        
        # 10+ streak multiplier
        multiplier_layout.addWidget(QLabel("10+ Streak Multiplier:"), 1, 0)
        self._mult_10_spin = QDoubleSpinBox()
        self._mult_10_spin.setRange(1.0, 5.0)
        self._mult_10_spin.setSingleStep(0.1)
        self._mult_10_spin.setValue(2.0)
        self._mult_10_spin.setDecimals(1)
        self._mult_10_spin.setSuffix("x")
        self._mult_10_spin.setToolTip("Point multiplier at 10+ correct streak")
        self._mult_10_spin.valueChanged.connect(self._on_setting_changed)
        multiplier_layout.addWidget(self._mult_10_spin, 1, 1)
        
        # 20+ streak multiplier
        multiplier_layout.addWidget(QLabel("20+ Streak Multiplier:"), 2, 0)
        self._mult_20_spin = QDoubleSpinBox()
        self._mult_20_spin.setRange(1.0, 5.0)
        self._mult_20_spin.setSingleStep(0.1)
        self._mult_20_spin.setValue(3.0)
        self._mult_20_spin.setDecimals(1)
        self._mult_20_spin.setSuffix("x")
        self._mult_20_spin.setToolTip("Point multiplier at 20+ correct streak")
        self._mult_20_spin.valueChanged.connect(self._on_setting_changed)
        multiplier_layout.addWidget(self._mult_20_spin, 2, 1)
        
        layout.addWidget(multiplier_group)
        
        # Accuracy Bonus Group
        accuracy_group = QGroupBox("Accuracy Bonus")
        accuracy_layout = QGridLayout(accuracy_group)
        accuracy_layout.setSpacing(10)
        
        # Accuracy threshold
        accuracy_layout.addWidget(QLabel("Accuracy Threshold:"), 0, 0)
        self._accuracy_threshold_spin = QDoubleSpinBox()
        self._accuracy_threshold_spin.setRange(0.5, 1.0)
        self._accuracy_threshold_spin.setSingleStep(0.05)
        self._accuracy_threshold_spin.setValue(0.9)
        self._accuracy_threshold_spin.setDecimals(2)
        self._accuracy_threshold_spin.setSuffix(" (90% = 0.90)")
        self._accuracy_threshold_spin.setToolTip("Minimum accuracy to receive bonus")
        self._accuracy_threshold_spin.valueChanged.connect(self._on_setting_changed)
        accuracy_layout.addWidget(self._accuracy_threshold_spin, 0, 1)
        
        # Accuracy bonus multiplier
        accuracy_layout.addWidget(QLabel("Accuracy Bonus Multiplier:"), 1, 0)
        self._accuracy_mult_spin = QDoubleSpinBox()
        self._accuracy_mult_spin.setRange(1.0, 3.0)
        self._accuracy_mult_spin.setSingleStep(0.05)
        self._accuracy_mult_spin.setValue(1.25)
        self._accuracy_mult_spin.setDecimals(2)
        self._accuracy_mult_spin.setSuffix("x")
        self._accuracy_mult_spin.setToolTip("Bonus multiplier when accuracy threshold is met")
        self._accuracy_mult_spin.valueChanged.connect(self._on_setting_changed)
        accuracy_layout.addWidget(self._accuracy_mult_spin, 1, 1)
        
        layout.addWidget(accuracy_group)

        # Unlock Thresholds Group
        unlock_group = QGroupBox("Unlock Thresholds")
        unlock_layout = QGridLayout(unlock_group)
        unlock_layout.setSpacing(10)
        
        # Cards per level
        unlock_layout.addWidget(QLabel("Correct Answers per Level:"), 0, 0)
        self._cards_per_level_spin = QSpinBox()
        self._cards_per_level_spin.setRange(10, 200)
        self._cards_per_level_spin.setValue(50)
        self._cards_per_level_spin.setToolTip("Correct answers needed to unlock a new level")
        self._cards_per_level_spin.valueChanged.connect(self._on_setting_changed)
        unlock_layout.addWidget(self._cards_per_level_spin, 0, 1)
        
        # Cards per power-up
        unlock_layout.addWidget(QLabel("Correct Answers per Power-Up:"), 1, 0)
        self._cards_per_powerup_spin = QSpinBox()
        self._cards_per_powerup_spin.setRange(20, 500)
        self._cards_per_powerup_spin.setValue(100)
        self._cards_per_powerup_spin.setToolTip("Correct answers needed to earn a power-up")
        self._cards_per_powerup_spin.valueChanged.connect(self._on_setting_changed)
        unlock_layout.addWidget(self._cards_per_powerup_spin, 1, 1)
        
        layout.addWidget(unlock_group)
        layout.addStretch()
    
    def _on_setting_changed(self) -> None:
        if PYQT_VERSION > 0:
            self.settings_changed.emit()
    
    def get_settings(self) -> dict:
        """Get current reward rate settings."""
        if PYQT_VERSION == 0:
            return {}
        return {
            'streak_multiplier_5': self._mult_5_spin.value(),
            'streak_multiplier_10': self._mult_10_spin.value(),
            'streak_multiplier_20': self._mult_20_spin.value(),
            'accuracy_bonus_threshold': self._accuracy_threshold_spin.value(),
            'accuracy_bonus_multiplier': self._accuracy_mult_spin.value(),
            'cards_per_level': self._cards_per_level_spin.value(),
            'cards_per_powerup': self._cards_per_powerup_spin.value(),
        }
    
    def set_settings(self, config: GameConfig) -> None:
        """Set reward rate settings from config."""
        if PYQT_VERSION == 0:
            return
        self._mult_5_spin.setValue(config.streak_multiplier_5)
        self._mult_10_spin.setValue(config.streak_multiplier_10)
        self._mult_20_spin.setValue(config.streak_multiplier_20)
        self._accuracy_threshold_spin.setValue(config.accuracy_bonus_threshold)
        self._accuracy_mult_spin.setValue(config.accuracy_bonus_multiplier)
        self._cards_per_level_spin.setValue(config.cards_per_level)
        self._cards_per_powerup_spin.setValue(config.cards_per_powerup)


class AnimationSettingsWidget(_WidgetBase):
    """Widget for animation settings (speed, enable/disable).
    
    Requirements: 12.3, 12.4
    """
    
    if PYQT_VERSION > 0:
        settings_changed = pyqtSignal()
    
    def __init__(self, parent: Optional[QWidget] = None):
        if PYQT_VERSION == 0:
            return
        super().__init__(parent)
        self._setup_ui()
    
    def _setup_ui(self) -> None:
        if PYQT_VERSION == 0:
            return
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        
        # Animation Control Group
        control_group = QGroupBox("Animation Control")
        control_layout = QVBoxLayout(control_group)
        control_layout.setSpacing(10)
        
        # Enable/disable animations
        self._animations_enabled_check = QCheckBox("Enable Animations")
        self._animations_enabled_check.setChecked(True)
        self._animations_enabled_check.setToolTip(
            "Enable or disable all game animations. "
            "Disabling creates a 'stats only' mode."
        )
        self._animations_enabled_check.stateChanged.connect(self._on_animation_toggle)
        control_layout.addWidget(self._animations_enabled_check)
        
        # Stats only mode info
        self._stats_only_label = QLabel(
            "ℹ️ When animations are disabled, the game runs in 'Stats Only' mode. "
            "Progress is still tracked but no visual animations are shown."
        )
        self._stats_only_label.setWordWrap(True)
        self._stats_only_label.setStyleSheet("color: #666; font-size: 11px; padding: 5px;")
        control_layout.addWidget(self._stats_only_label)
        
        layout.addWidget(control_group)
        
        # Animation Speed Group
        speed_group = QGroupBox("Animation Speed")
        speed_layout = QGridLayout(speed_group)
        speed_layout.setSpacing(10)
        
        # Speed slider
        speed_layout.addWidget(QLabel("Animation Speed:"), 0, 0)
        
        speed_container = QHBoxLayout()
        self._speed_slider = QSlider(
            Qt.Orientation.Horizontal if PYQT_VERSION == 6 else Qt.Horizontal
        )
        self._speed_slider.setRange(25, 200)  # 0.25x to 2.0x
        self._speed_slider.setValue(100)  # 1.0x default
        self._speed_slider.setTickPosition(
            QSlider.TickPosition.TicksBelow if PYQT_VERSION == 6 else QSlider.TicksBelow
        )
        self._speed_slider.setTickInterval(25)
        self._speed_slider.setToolTip("Adjust animation playback speed")
        self._speed_slider.valueChanged.connect(self._on_speed_changed)
        speed_container.addWidget(self._speed_slider)
        
        self._speed_label = QLabel("1.0x")
        self._speed_label.setMinimumWidth(50)
        self._speed_label.setStyleSheet("font-weight: bold; color: #2196F3;")
        speed_container.addWidget(self._speed_label)
        
        speed_layout.addLayout(speed_container, 0, 1)
        
        # Speed presets
        preset_layout = QHBoxLayout()
        preset_layout.addWidget(QLabel("Presets:"))
        
        slow_btn = QPushButton("Slow (0.5x)")
        slow_btn.clicked.connect(lambda: self._set_speed(50))
        preset_layout.addWidget(slow_btn)
        
        normal_btn = QPushButton("Normal (1.0x)")
        normal_btn.clicked.connect(lambda: self._set_speed(100))
        preset_layout.addWidget(normal_btn)
        
        fast_btn = QPushButton("Fast (1.5x)")
        fast_btn.clicked.connect(lambda: self._set_speed(150))
        preset_layout.addWidget(fast_btn)
        
        preset_layout.addStretch()
        speed_layout.addLayout(preset_layout, 1, 0, 1, 2)
        
        layout.addWidget(speed_group)
        layout.addStretch()
    
    def _on_animation_toggle(self, state: int) -> None:
        if PYQT_VERSION == 0:
            return
        enabled = state == (Qt.CheckState.Checked.value if PYQT_VERSION == 6 else Qt.Checked)
        self._speed_slider.setEnabled(enabled)
        self.settings_changed.emit()
    
    def _on_speed_changed(self, value: int) -> None:
        if PYQT_VERSION == 0:
            return
        speed = value / 100.0
        self._speed_label.setText(f"{speed:.2f}x")
        self.settings_changed.emit()
    
    def _set_speed(self, value: int) -> None:
        if PYQT_VERSION == 0:
            return
        self._speed_slider.setValue(value)

    def get_settings(self) -> dict:
        """Get current animation settings."""
        if PYQT_VERSION == 0:
            return {}
        return {
            'animations_enabled': self._animations_enabled_check.isChecked(),
            'animation_speed': self._speed_slider.value() / 100.0,
        }
    
    def set_settings(self, config: GameConfig) -> None:
        """Set animation settings from config."""
        if PYQT_VERSION == 0:
            return
        self._animations_enabled_check.setChecked(config.animations_enabled)
        self._speed_slider.setValue(int(config.animation_speed * 100))
        self._speed_slider.setEnabled(config.animations_enabled)
    
    def is_stats_only_mode(self) -> bool:
        """Check if stats-only mode is enabled (animations disabled).
        
        Requirements: 12.4
        """
        if PYQT_VERSION == 0:
            return False
        return not self._animations_enabled_check.isChecked()


class AccessibilitySettingsWidget(_WidgetBase):
    """Widget for accessibility settings (colorblind modes, sound).
    
    Requirements: 12.5, 12.6, 12.7
    """
    
    if PYQT_VERSION > 0:
        settings_changed = pyqtSignal()
    
    def __init__(self, parent: Optional[QWidget] = None):
        if PYQT_VERSION == 0:
            return
        super().__init__(parent)
        self._setup_ui()
    
    def _setup_ui(self) -> None:
        if PYQT_VERSION == 0:
            return
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        
        # Colorblind Mode Group
        colorblind_group = QGroupBox("Colorblind Mode")
        colorblind_layout = QVBoxLayout(colorblind_group)
        colorblind_layout.setSpacing(10)
        
        mode_layout = QHBoxLayout()
        mode_layout.addWidget(QLabel("Color Vision Mode:"))
        
        self._colorblind_combo = QComboBox()
        self._colorblind_combo.addItem("Normal Vision", None)
        self._colorblind_combo.addItem("Deuteranopia (Red-Green)", "deuteranopia")
        self._colorblind_combo.addItem("Protanopia (Red-Green)", "protanopia")
        self._colorblind_combo.addItem("Tritanopia (Blue-Yellow)", "tritanopia")
        self._colorblind_combo.setToolTip(
            "Select a colorblind mode to adjust game colors for better visibility"
        )
        self._colorblind_combo.currentIndexChanged.connect(self._on_setting_changed)
        mode_layout.addWidget(self._colorblind_combo)
        mode_layout.addStretch()
        
        colorblind_layout.addLayout(mode_layout)
        
        # Colorblind mode descriptions
        self._colorblind_info = QLabel(
            "ℹ️ Colorblind modes adjust the game's color palette to improve "
            "visibility for users with different types of color vision deficiency."
        )
        self._colorblind_info.setWordWrap(True)
        self._colorblind_info.setStyleSheet("color: #666; font-size: 11px; padding: 5px;")
        colorblind_layout.addWidget(self._colorblind_info)
        
        layout.addWidget(colorblind_group)
        
        # Sound Settings Group
        sound_group = QGroupBox("Sound Settings")
        sound_layout = QVBoxLayout(sound_group)
        sound_layout.setSpacing(10)
        
        # Enable/disable sound
        self._sound_enabled_check = QCheckBox("Enable Sound Effects")
        self._sound_enabled_check.setChecked(True)
        self._sound_enabled_check.setToolTip("Enable or disable all game sound effects")
        self._sound_enabled_check.stateChanged.connect(self._on_sound_toggle)
        sound_layout.addWidget(self._sound_enabled_check)
        
        # Volume slider
        volume_layout = QHBoxLayout()
        volume_layout.addWidget(QLabel("Volume:"))
        
        self._volume_slider = QSlider(
            Qt.Orientation.Horizontal if PYQT_VERSION == 6 else Qt.Horizontal
        )
        self._volume_slider.setRange(0, 100)
        self._volume_slider.setValue(70)  # 0.7 default
        self._volume_slider.setTickPosition(
            QSlider.TickPosition.TicksBelow if PYQT_VERSION == 6 else QSlider.TicksBelow
        )
        self._volume_slider.setTickInterval(10)
        self._volume_slider.setToolTip("Adjust sound effect volume")
        self._volume_slider.valueChanged.connect(self._on_volume_changed)
        volume_layout.addWidget(self._volume_slider)
        
        self._volume_label = QLabel("70%")
        self._volume_label.setMinimumWidth(50)
        self._volume_label.setStyleSheet("font-weight: bold; color: #2196F3;")
        volume_layout.addWidget(self._volume_label)
        
        sound_layout.addLayout(volume_layout)
        
        # Volume presets
        preset_layout = QHBoxLayout()
        preset_layout.addWidget(QLabel("Presets:"))
        
        mute_btn = QPushButton("Mute")
        mute_btn.clicked.connect(lambda: self._set_volume(0))
        preset_layout.addWidget(mute_btn)
        
        low_btn = QPushButton("Low (30%)")
        low_btn.clicked.connect(lambda: self._set_volume(30))
        preset_layout.addWidget(low_btn)
        
        medium_btn = QPushButton("Medium (70%)")
        medium_btn.clicked.connect(lambda: self._set_volume(70))
        preset_layout.addWidget(medium_btn)
        
        full_btn = QPushButton("Full (100%)")
        full_btn.clicked.connect(lambda: self._set_volume(100))
        preset_layout.addWidget(full_btn)
        
        preset_layout.addStretch()
        sound_layout.addLayout(preset_layout)
        
        layout.addWidget(sound_group)
        layout.addStretch()

    def _on_setting_changed(self) -> None:
        if PYQT_VERSION > 0:
            self.settings_changed.emit()
    
    def _on_sound_toggle(self, state: int) -> None:
        if PYQT_VERSION == 0:
            return
        enabled = state == (Qt.CheckState.Checked.value if PYQT_VERSION == 6 else Qt.Checked)
        self._volume_slider.setEnabled(enabled)
        self.settings_changed.emit()
    
    def _on_volume_changed(self, value: int) -> None:
        if PYQT_VERSION == 0:
            return
        self._volume_label.setText(f"{value}%")
        self.settings_changed.emit()
    
    def _set_volume(self, value: int) -> None:
        if PYQT_VERSION == 0:
            return
        self._volume_slider.setValue(value)
    
    def get_settings(self) -> dict:
        """Get current accessibility settings."""
        if PYQT_VERSION == 0:
            return {}
        colorblind_mode = self._colorblind_combo.currentData()
        return {
            'colorblind_mode': colorblind_mode,
            'sound_enabled': self._sound_enabled_check.isChecked(),
            'sound_volume': self._volume_slider.value() / 100.0,
        }
    
    def set_settings(self, config: GameConfig) -> None:
        """Set accessibility settings from config."""
        if PYQT_VERSION == 0:
            return
        # Set colorblind mode
        index = 0
        for i in range(self._colorblind_combo.count()):
            if self._colorblind_combo.itemData(i) == config.colorblind_mode:
                index = i
                break
        self._colorblind_combo.setCurrentIndex(index)
        
        # Set sound settings
        self._sound_enabled_check.setChecked(config.sound_enabled)
        self._volume_slider.setValue(int(config.sound_volume * 100))
        self._volume_slider.setEnabled(config.sound_enabled)


class SettingsPanel(_DialogBase):
    """Settings configuration panel.
    
    A PyQt QDialog that allows users to customize game settings including:
    - Difficulty settings (point values, penalty severity)
    - Reward rate settings (multipliers, unlock thresholds)
    - Animation settings (speed, enable/disable)
    - Accessibility settings (colorblind modes, sound)
    
    Requirements: 12.1, 12.2, 12.3, 12.4, 12.5, 12.6, 12.7
    """
    
    if PYQT_VERSION > 0:
        settings_saved = pyqtSignal()
    
    def __init__(self, config_manager: ConfigManager, parent: Optional[QWidget] = None):
        if PYQT_VERSION == 0:
            logger.warning("PyQt not available - SettingsPanel cannot be created")
            return
        super().__init__(parent)
        self._config_manager = config_manager
        self._has_unsaved_changes = False
        self._setup_ui()
        self._connect_signals()
        self.load_settings()
    
    def _setup_ui(self) -> None:
        if PYQT_VERSION == 0:
            return
        self.setWindowTitle("NintendAnki Settings")
        self.setMinimumSize(500, 550)
        self.resize(600, 650)
        
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(10)
        
        # Header
        header_label = QLabel("⚙️ Settings")
        header_label.setStyleSheet(
            "font-size: 20px; font-weight: bold; color: #1976D2; padding: 10px;"
        )
        header_label.setAlignment(
            Qt.AlignmentFlag.AlignCenter if PYQT_VERSION == 6 else Qt.AlignCenter
        )
        main_layout.addWidget(header_label)
        
        # Tab widget for settings categories
        self._tab_widget = QTabWidget()
        self._tab_widget.setStyleSheet(
            "QTabWidget::pane { border: 1px solid #ddd; border-radius: 5px; }"
            "QTabBar::tab { padding: 8px 16px; }"
            "QTabBar::tab:selected { background-color: #E3F2FD; }"
        )
        
        # Difficulty tab
        self._difficulty_widget = DifficultySettingsWidget()
        self._tab_widget.addTab(self._difficulty_widget, "🎯 Difficulty")
        
        # Reward rates tab
        self._reward_widget = RewardRateSettingsWidget()
        self._tab_widget.addTab(self._reward_widget, "🏆 Rewards")
        
        # Animation tab
        self._animation_widget = AnimationSettingsWidget()
        self._tab_widget.addTab(self._animation_widget, "🎬 Animation")
        
        # Accessibility tab
        self._accessibility_widget = AccessibilitySettingsWidget()
        self._tab_widget.addTab(self._accessibility_widget, "♿ Accessibility")
        
        main_layout.addWidget(self._tab_widget)
        
        # Unsaved changes indicator
        self._unsaved_label = QLabel("⚠️ You have unsaved changes")
        self._unsaved_label.setStyleSheet(
            "color: #FF9800; font-weight: bold; padding: 5px;"
        )
        self._unsaved_label.setAlignment(
            Qt.AlignmentFlag.AlignCenter if PYQT_VERSION == 6 else Qt.AlignCenter
        )
        self._unsaved_label.setVisible(False)
        main_layout.addWidget(self._unsaved_label)

        # Footer buttons
        footer_layout = QHBoxLayout()
        
        self._reset_btn = QPushButton("🔄 Reset to Defaults")
        self._reset_btn.setStyleSheet(
            "QPushButton { background-color: #FF9800; color: white; "
            "border-radius: 3px; padding: 8px 20px; }"
            "QPushButton:hover { background-color: #F57C00; }"
        )
        self._reset_btn.clicked.connect(self.reset_to_defaults)
        footer_layout.addWidget(self._reset_btn)
        
        footer_layout.addStretch()
        
        self._save_btn = QPushButton("💾 Save")
        self._save_btn.setStyleSheet(
            "QPushButton { background-color: #4CAF50; color: white; "
            "border-radius: 3px; padding: 8px 20px; }"
            "QPushButton:hover { background-color: #388E3C; }"
        )
        self._save_btn.clicked.connect(self.save_settings)
        footer_layout.addWidget(self._save_btn)
        
        self._cancel_btn = QPushButton("Cancel")
        self._cancel_btn.setStyleSheet(
            "QPushButton { background-color: #757575; color: white; "
            "border-radius: 3px; padding: 8px 20px; }"
            "QPushButton:hover { background-color: #616161; }"
        )
        self._cancel_btn.clicked.connect(self._on_cancel)
        footer_layout.addWidget(self._cancel_btn)
        
        main_layout.addLayout(footer_layout)
    
    def _connect_signals(self) -> None:
        if PYQT_VERSION == 0:
            return
        # Connect all widget signals to track changes
        self._difficulty_widget.settings_changed.connect(self._on_settings_changed)
        self._reward_widget.settings_changed.connect(self._on_settings_changed)
        self._animation_widget.settings_changed.connect(self._on_settings_changed)
        self._accessibility_widget.settings_changed.connect(self._on_settings_changed)
    
    def _on_settings_changed(self) -> None:
        """Handle settings change from any widget."""
        if PYQT_VERSION == 0:
            return
        self._has_unsaved_changes = True
        self._unsaved_label.setVisible(True)
    
    def _on_cancel(self) -> None:
        """Handle cancel button click."""
        if PYQT_VERSION == 0:
            return
        if self._has_unsaved_changes:
            reply = QMessageBox.question(
                self,
                "Unsaved Changes",
                "You have unsaved changes. Are you sure you want to close?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                if PYQT_VERSION == 6 else QMessageBox.Yes | QMessageBox.No,
                QMessageBox.StandardButton.No if PYQT_VERSION == 6 else QMessageBox.No
            )
            if reply == (QMessageBox.StandardButton.Yes if PYQT_VERSION == 6 else QMessageBox.Yes):
                self.close()
        else:
            self.close()
    
    def load_settings(self) -> None:
        """Load current settings into UI.
        
        Loads settings from the ConfigManager and populates all UI widgets.
        """
        if PYQT_VERSION == 0:
            return
        config = self._config_manager.load_config()
        
        self._difficulty_widget.set_settings(config)
        self._reward_widget.set_settings(config)
        self._animation_widget.set_settings(config)
        self._accessibility_widget.set_settings(config)
        
        self._has_unsaved_changes = False
        self._unsaved_label.setVisible(False)

    def save_settings(self) -> None:
        """Save UI settings to config.
        
        Collects settings from all UI widgets and saves them via ConfigManager.
        """
        if PYQT_VERSION == 0:
            return
        
        # Collect settings from all widgets
        difficulty = self._difficulty_widget.get_settings()
        rewards = self._reward_widget.get_settings()
        animation = self._animation_widget.get_settings()
        accessibility = self._accessibility_widget.get_settings()
        
        # Create new config
        config = GameConfig(
            # Difficulty
            base_points=difficulty.get('base_points', 10),
            penalty_health_reduction=difficulty.get('penalty_health_reduction', 0.1),
            penalty_currency_loss=difficulty.get('penalty_currency_loss', 1),
            # Rewards
            streak_multiplier_5=rewards.get('streak_multiplier_5', 1.5),
            streak_multiplier_10=rewards.get('streak_multiplier_10', 2.0),
            streak_multiplier_20=rewards.get('streak_multiplier_20', 3.0),
            accuracy_bonus_threshold=rewards.get('accuracy_bonus_threshold', 0.9),
            accuracy_bonus_multiplier=rewards.get('accuracy_bonus_multiplier', 1.25),
            cards_per_level=rewards.get('cards_per_level', 50),
            cards_per_powerup=rewards.get('cards_per_powerup', 100),
            # Animation
            animation_speed=animation.get('animation_speed', 1.0),
            animations_enabled=animation.get('animations_enabled', True),
            # Accessibility
            colorblind_mode=accessibility.get('colorblind_mode'),
            sound_enabled=accessibility.get('sound_enabled', True),
            sound_volume=accessibility.get('sound_volume', 0.7),
        )
        
        # Save to config manager
        self._config_manager.save_config(config)
        
        self._has_unsaved_changes = False
        self._unsaved_label.setVisible(False)
        
        # Emit signal
        self.settings_saved.emit()
        
        # Show confirmation
        QMessageBox.information(
            self,
            "Settings Saved",
            "Your settings have been saved successfully.",
            QMessageBox.StandardButton.Ok if PYQT_VERSION == 6 else QMessageBox.Ok
        )
    
    def reset_to_defaults(self) -> None:
        """Reset all settings to defaults.
        
        Resets all settings to their default values and updates the UI.
        """
        if PYQT_VERSION == 0:
            return
        
        reply = QMessageBox.question(
            self,
            "Reset to Defaults",
            "Are you sure you want to reset all settings to their default values?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            if PYQT_VERSION == 6 else QMessageBox.Yes | QMessageBox.No,
            QMessageBox.StandardButton.No if PYQT_VERSION == 6 else QMessageBox.No
        )
        
        if reply == (QMessageBox.StandardButton.Yes if PYQT_VERSION == 6 else QMessageBox.Yes):
            config = self._config_manager.reset_to_defaults()
            
            self._difficulty_widget.set_settings(config)
            self._reward_widget.set_settings(config)
            self._animation_widget.set_settings(config)
            self._accessibility_widget.set_settings(config)
            
            self._has_unsaved_changes = False
            self._unsaved_label.setVisible(False)
            
            QMessageBox.information(
                self,
                "Settings Reset",
                "All settings have been reset to their default values.",
                QMessageBox.StandardButton.Ok if PYQT_VERSION == 6 else QMessageBox.Ok
            )

    def closeEvent(self, event) -> None:
        """Handle window close event."""
        if PYQT_VERSION == 0:
            return
        if self._has_unsaved_changes:
            reply = QMessageBox.question(
                self,
                "Unsaved Changes",
                "You have unsaved changes. Are you sure you want to close?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                if PYQT_VERSION == 6 else QMessageBox.Yes | QMessageBox.No,
                QMessageBox.StandardButton.No if PYQT_VERSION == 6 else QMessageBox.No
            )
            if reply == (QMessageBox.StandardButton.No if PYQT_VERSION == 6 else QMessageBox.No):
                event.ignore()
                return
        super().closeEvent(event)
    
    # Accessor methods for testing
    def get_difficulty_widget(self) -> DifficultySettingsWidget:
        """Get the difficulty settings widget."""
        return self._difficulty_widget
    
    def get_reward_widget(self) -> RewardRateSettingsWidget:
        """Get the reward rate settings widget."""
        return self._reward_widget
    
    def get_animation_widget(self) -> AnimationSettingsWidget:
        """Get the animation settings widget."""
        return self._animation_widget
    
    def get_accessibility_widget(self) -> AccessibilitySettingsWidget:
        """Get the accessibility settings widget."""
        return self._accessibility_widget
    
    def get_current_tab_index(self) -> int:
        """Get the current tab index."""
        if PYQT_VERSION == 0:
            return -1
        return self._tab_widget.currentIndex()
    
    def has_unsaved_changes(self) -> bool:
        """Check if there are unsaved changes."""
        return self._has_unsaved_changes
    
    def is_stats_only_mode(self) -> bool:
        """Check if stats-only mode is enabled.
        
        Requirements: 12.4
        """
        return self._animation_widget.is_stats_only_mode()
