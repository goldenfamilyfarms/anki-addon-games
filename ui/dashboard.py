"""
Dashboard for NintendAnki.

This module implements the Dashboard class, a PyQt QDialog that displays
user statistics, achievements, power-ups, and provides theme selection.

Requirements: 10.1, 10.2, 10.3, 10.4, 10.5, 10.6, 10.7
"""

import logging
from typing import Optional, List

from data.models import (
    Achievement,
    PowerUp,
    ProgressionState,
    Theme,
    ThemeStats,
)
from core.progression_system import ProgressionSystem
from core.achievement_system import AchievementSystem
from core.theme_manager import ThemeManager
from core.powerup_system import PowerUpSystem

logger = logging.getLogger(__name__)

# Try to import PyQt6 first, then fall back to PyQt5
try:
    from PyQt6.QtWidgets import (
        QDialog, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
        QTabWidget, QPushButton, QScrollArea, QFrame,
        QGridLayout, QGroupBox, QProgressBar,
    )
    from PyQt6.QtCore import Qt, pyqtSignal, QTimer
    PYQT_VERSION = 6
except ImportError:
    try:
        from PyQt5.QtWidgets import (
            QDialog, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
            QTabWidget, QPushButton, QScrollArea, QFrame,
            QGridLayout, QGroupBox, QProgressBar,
        )
        from PyQt5.QtCore import Qt, pyqtSignal, QTimer
        PYQT_VERSION = 5
    except ImportError:
        PYQT_VERSION = 0
        logger.warning("PyQt not available - Dashboard will have limited functionality")


# Define base classes based on PyQt availability
if PYQT_VERSION > 0:
    _WidgetBase = QWidget
    _DialogBase = QDialog
else:
    _WidgetBase = object
    _DialogBase = object


class StatsWidget(_WidgetBase):
    """Widget displaying user statistics. Requirements: 10.2, 10.3"""
    
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
        
        # General Stats Group
        general_group = QGroupBox("General Statistics")
        general_layout = QGridLayout(general_group)
        general_layout.setSpacing(10)
        
        self._points_label = self._create_stat_row(general_layout, 0, "Total Points:", "0")
        self._cards_label = self._create_stat_row(general_layout, 1, "Cards Reviewed:", "0")
        self._streak_label = self._create_stat_row(general_layout, 2, "Current Streak:", "0")
        self._best_streak_label = self._create_stat_row(general_layout, 3, "Best Streak:", "0")
        self._accuracy_label = self._create_stat_row(general_layout, 4, "Session Accuracy:", "0%")
        self._levels_unlocked_label = self._create_stat_row(general_layout, 5, "Levels Unlocked:", "0")
        self._levels_completed_label = self._create_stat_row(general_layout, 6, "Levels Completed:", "0")
        layout.addWidget(general_group)
        
        # Theme-Specific Stats Group
        self._theme_group = QGroupBox("Theme Progress")
        self._theme_layout = QGridLayout(self._theme_group)
        self._theme_layout.setSpacing(10)
        self._theme_collectible_label = self._create_stat_row(self._theme_layout, 0, "Collectibles:", "0")
        self._theme_secondary_label = self._create_stat_row(self._theme_layout, 1, "Secondary:", "0")
        self._theme_completion_label = self._create_stat_row(self._theme_layout, 2, "Completion:", "0%")
        layout.addWidget(self._theme_group)
        layout.addStretch()
    
    def _create_stat_row(self, layout: QGridLayout, row: int, label_text: str, value_text: str) -> QLabel:
        label = QLabel(label_text)
        label.setStyleSheet("font-weight: bold;")
        layout.addWidget(label, row, 0)
        value_label = QLabel(value_text)
        value_label.setStyleSheet("color: #2196F3;")
        layout.addWidget(value_label, row, 1)
        return value_label

    def update_stats(self, state: ProgressionState) -> None:
        if PYQT_VERSION == 0:
            return
        self._points_label.setText(f"{state.total_points:,}")
        self._cards_label.setText(f"{state.total_cards_reviewed:,}")
        self._streak_label.setText(f"{state.current_streak:,}")
        self._best_streak_label.setText(f"{state.best_streak:,}")
        self._accuracy_label.setText(f"{state.session_accuracy * 100:.1f}%")
        self._levels_unlocked_label.setText(f"{state.levels_unlocked:,}")
        self._levels_completed_label.setText(f"{state.levels_completed:,}")
    
    def update_theme_stats(self, theme_stats: ThemeStats) -> None:
        if PYQT_VERSION == 0:
            return
        theme_name = theme_stats.theme.value.upper()
        self._theme_group.setTitle(f"{theme_name} Theme Progress")
        self._theme_layout.itemAtPosition(0, 0).widget().setText(f"{theme_stats.primary_collectible_name}:")
        self._theme_collectible_label.setText(f"{theme_stats.primary_collectible_count:,}")
        if theme_stats.secondary_stat_name:
            self._theme_layout.itemAtPosition(1, 0).widget().setText(f"{theme_stats.secondary_stat_name}:")
            self._theme_secondary_label.setText(f"{theme_stats.secondary_stat_value or 0:,}")
        else:
            self._theme_layout.itemAtPosition(1, 0).widget().setText("Secondary:")
            self._theme_secondary_label.setText("N/A")
        self._theme_completion_label.setText(f"{theme_stats.completion_percentage * 100:.1f}%")


class AchievementsWidget(_WidgetBase):
    """Widget displaying achievements with unlock status and dates. Requirements: 10.4"""
    
    def __init__(self, parent: Optional[QWidget] = None):
        if PYQT_VERSION == 0:
            return
        super().__init__(parent)
        self._achievement_widgets: List[QFrame] = []
        self._setup_ui()
    
    def _setup_ui(self) -> None:
        if PYQT_VERSION == 0:
            return
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(10)
        
        summary_group = QGroupBox("Achievement Summary")
        summary_layout = QHBoxLayout(summary_group)
        self._total_label = QLabel("Total: 0")
        self._unlocked_label = QLabel("Unlocked: 0")
        self._progress_bar = QProgressBar()
        self._progress_bar.setRange(0, 100)
        self._progress_bar.setValue(0)
        summary_layout.addWidget(self._total_label)
        summary_layout.addWidget(self._unlocked_label)
        summary_layout.addWidget(self._progress_bar)
        main_layout.addWidget(summary_group)
        
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff if PYQT_VERSION == 6 else Qt.ScrollBarAlwaysOff
        )
        self._achievements_container = QWidget()
        self._achievements_layout = QVBoxLayout(self._achievements_container)
        self._achievements_layout.setSpacing(5)
        self._achievements_layout.addStretch()
        scroll_area.setWidget(self._achievements_container)
        main_layout.addWidget(scroll_area)

    def update_achievements(self, achievements: List[Achievement]) -> None:
        if PYQT_VERSION == 0:
            return
        for widget in self._achievement_widgets:
            self._achievements_layout.removeWidget(widget)
            widget.deleteLater()
        self._achievement_widgets.clear()
        
        total = len(achievements)
        unlocked = sum(1 for a in achievements if a.unlocked)
        self._total_label.setText(f"Total: {total}")
        self._unlocked_label.setText(f"Unlocked: {unlocked}")
        if total > 0:
            self._progress_bar.setValue(int(unlocked / total * 100))
        
        sorted_achievements = sorted(achievements, key=lambda a: (not a.unlocked, a.name))
        for achievement in sorted_achievements:
            widget = self._create_achievement_widget(achievement)
            self._achievements_layout.insertWidget(self._achievements_layout.count() - 1, widget)
            self._achievement_widgets.append(widget)
    
    def _create_achievement_widget(self, achievement: Achievement) -> QFrame:
        frame = QFrame()
        frame.setFrameShape(QFrame.Shape.StyledPanel if PYQT_VERSION == 6 else QFrame.StyledPanel)
        if achievement.unlocked:
            frame.setStyleSheet("QFrame { background-color: #E8F5E9; border-radius: 5px; padding: 5px; }")
        else:
            frame.setStyleSheet("QFrame { background-color: #FAFAFA; border-radius: 5px; padding: 5px; }")
        
        layout = QHBoxLayout(frame)
        layout.setContentsMargins(10, 5, 10, 5)
        
        info_layout = QVBoxLayout()
        name_label = QLabel(achievement.name)
        name_label.setStyleSheet("font-weight: bold; font-size: 12px;")
        info_layout.addWidget(name_label)
        desc_label = QLabel(achievement.description)
        desc_label.setStyleSheet("color: #666; font-size: 10px;")
        desc_label.setWordWrap(True)
        info_layout.addWidget(desc_label)
        layout.addLayout(info_layout, stretch=1)
        
        status_layout = QVBoxLayout()
        if achievement.unlocked:
            status_label = QLabel("✓ Unlocked")
            status_label.setStyleSheet("color: #4CAF50; font-weight: bold;")
            status_layout.addWidget(status_label)
            if achievement.unlock_date:
                date_str = achievement.unlock_date.strftime("%Y-%m-%d")
                date_label = QLabel(date_str)
                date_label.setStyleSheet("color: #888; font-size: 10px;")
                status_layout.addWidget(date_label)
        else:
            status_label = QLabel("🔒 Locked")
            status_label.setStyleSheet("color: #999;")
            status_layout.addWidget(status_label)
            if achievement.target > 0:
                progress = min(achievement.progress, achievement.target)
                progress_label = QLabel(f"{progress}/{achievement.target}")
                progress_label.setStyleSheet("color: #888; font-size: 10px;")
                status_layout.addWidget(progress_label)
        
        reward_label = QLabel(f"🪙 {achievement.reward_currency}")
        reward_label.setStyleSheet("color: #FFC107; font-size: 10px;")
        status_layout.addWidget(reward_label)
        layout.addLayout(status_layout)
        return frame


class PowerUpsWidget(_WidgetBase):
    """Widget displaying power-ups inventory. Requirements: 10.5"""
    
    def __init__(self, parent: Optional[QWidget] = None):
        if PYQT_VERSION == 0:
            return
        super().__init__(parent)
        self._powerup_widgets: List[QFrame] = []
        self._setup_ui()
    
    def _setup_ui(self) -> None:
        if PYQT_VERSION == 0:
            return
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(10)
        
        active_group = QGroupBox("Active Power-Ups")
        self._active_layout = QVBoxLayout(active_group)
        self._active_layout.addWidget(QLabel("No active power-ups"))
        main_layout.addWidget(active_group)
        
        inventory_group = QGroupBox("Inventory")
        inventory_layout = QVBoxLayout(inventory_group)
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff if PYQT_VERSION == 6 else Qt.ScrollBarAlwaysOff
        )
        self._inventory_container = QWidget()
        self._inventory_layout = QVBoxLayout(self._inventory_container)
        self._inventory_layout.setSpacing(5)
        self._inventory_layout.addStretch()
        scroll_area.setWidget(self._inventory_container)
        inventory_layout.addWidget(scroll_area)
        main_layout.addWidget(inventory_group)
    
    def update_powerups(self, inventory: List[PowerUp], active: Optional[List] = None) -> None:
        if PYQT_VERSION == 0:
            return
        for widget in self._powerup_widgets:
            widget.deleteLater()
        self._powerup_widgets.clear()
        
        while self._active_layout.count() > 0:
            item = self._active_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        if active and len(active) > 0:
            for active_powerup in active:
                widget = self._create_active_powerup_widget(active_powerup)
                self._active_layout.addWidget(widget)
        else:
            self._active_layout.addWidget(QLabel("No active power-ups"))
        
        while self._inventory_layout.count() > 1:
            item = self._inventory_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        if inventory:
            for powerup in inventory:
                if powerup.quantity > 0:
                    widget = self._create_powerup_widget(powerup)
                    self._inventory_layout.insertWidget(self._inventory_layout.count() - 1, widget)
                    self._powerup_widgets.append(widget)
        
        if not inventory or all(p.quantity <= 0 for p in inventory):
            empty_label = QLabel("No power-ups in inventory")
            empty_label.setStyleSheet("color: #888;")
            self._inventory_layout.insertWidget(0, empty_label)

    def _create_powerup_widget(self, powerup: PowerUp) -> QFrame:
        frame = QFrame()
        frame.setFrameShape(QFrame.Shape.StyledPanel if PYQT_VERSION == 6 else QFrame.StyledPanel)
        frame.setStyleSheet("QFrame { background-color: #E3F2FD; border-radius: 5px; padding: 5px; }")
        layout = QHBoxLayout(frame)
        layout.setContentsMargins(10, 5, 10, 5)
        
        info_layout = QVBoxLayout()
        name_label = QLabel(powerup.name)
        name_label.setStyleSheet("font-weight: bold; font-size: 12px;")
        info_layout.addWidget(name_label)
        desc_label = QLabel(powerup.description)
        desc_label.setStyleSheet("color: #666; font-size: 10px;")
        desc_label.setWordWrap(True)
        info_layout.addWidget(desc_label)
        layout.addLayout(info_layout, stretch=1)
        
        status_layout = QVBoxLayout()
        qty_label = QLabel(f"x{powerup.quantity}")
        qty_label.setStyleSheet("font-weight: bold; font-size: 14px; color: #2196F3;")
        status_layout.addWidget(qty_label)
        if powerup.theme:
            theme_label = QLabel(powerup.theme.value.upper())
            theme_label.setStyleSheet("color: #888; font-size: 10px;")
            status_layout.addWidget(theme_label)
        if powerup.duration_seconds > 0:
            duration_label = QLabel(f"⏱ {powerup.duration_seconds}s")
            duration_label.setStyleSheet("color: #FF9800; font-size: 10px;")
            status_layout.addWidget(duration_label)
        layout.addLayout(status_layout)
        return frame
    
    def _create_active_powerup_widget(self, active_powerup) -> QFrame:
        frame = QFrame()
        frame.setFrameShape(QFrame.Shape.StyledPanel if PYQT_VERSION == 6 else QFrame.StyledPanel)
        frame.setStyleSheet("QFrame { background-color: #FFF3E0; border-radius: 5px; padding: 5px; }")
        layout = QHBoxLayout(frame)
        layout.setContentsMargins(10, 5, 10, 5)
        name_label = QLabel(active_powerup.powerup.name)
        name_label.setStyleSheet("font-weight: bold;")
        layout.addWidget(name_label)
        layout.addStretch()
        remaining = int(active_powerup.remaining_seconds)
        time_label = QLabel(f"⏱ {remaining}s remaining")
        time_label.setStyleSheet("color: #FF5722; font-weight: bold;")
        layout.addWidget(time_label)
        return frame


class ThemeSelectorWidget(_WidgetBase):
    """Widget for selecting and switching themes. Requirements: 10.6"""
    
    if PYQT_VERSION > 0:
        theme_changed = pyqtSignal(Theme)
    
    def __init__(self, parent: Optional[QWidget] = None):
        if PYQT_VERSION == 0:
            return
        super().__init__(parent)
        self._current_theme: Optional[Theme] = None
        self._setup_ui()
    
    def _setup_ui(self) -> None:
        if PYQT_VERSION == 0:
            return
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        
        current_group = QGroupBox("Current Theme")
        current_layout = QVBoxLayout(current_group)
        self._current_theme_label = QLabel("No theme selected")
        self._current_theme_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #2196F3;")
        self._current_theme_label.setAlignment(
            Qt.AlignmentFlag.AlignCenter if PYQT_VERSION == 6 else Qt.AlignCenter
        )
        current_layout.addWidget(self._current_theme_label)
        layout.addWidget(current_group)
        
        select_group = QGroupBox("Select Theme")
        select_layout = QVBoxLayout(select_group)
        
        theme_info = {
            Theme.MARIO: ("🍄 Mario", "Side-scrolling adventure with coin collection"),
            Theme.ZELDA: ("⚔️ Zelda", "Exploration and boss battles"),
            Theme.DKC: ("🍌 DKC", "Jungle world with time trials"),
        }
        
        self._theme_buttons: dict = {}
        for theme in Theme:
            name, description = theme_info.get(theme, (theme.value, ""))
            button_frame = QFrame()
            button_frame.setFrameShape(QFrame.Shape.StyledPanel if PYQT_VERSION == 6 else QFrame.StyledPanel)
            button_frame.setStyleSheet(
                "QFrame { background-color: #FAFAFA; border-radius: 5px; }"
                "QFrame:hover { background-color: #E3F2FD; }"
            )
            button_layout = QHBoxLayout(button_frame)
            info_layout = QVBoxLayout()
            name_label = QLabel(name)
            name_label.setStyleSheet("font-weight: bold; font-size: 14px;")
            info_layout.addWidget(name_label)
            desc_label = QLabel(description)
            desc_label.setStyleSheet("color: #666; font-size: 11px;")
            info_layout.addWidget(desc_label)
            button_layout.addLayout(info_layout, stretch=1)
            select_btn = QPushButton("Select")
            select_btn.setStyleSheet(
                "QPushButton { background-color: #2196F3; color: white; border-radius: 3px; padding: 5px 15px; }"
                "QPushButton:hover { background-color: #1976D2; }"
            )
            select_btn.clicked.connect(lambda checked, t=theme: self._on_theme_selected(t))
            button_layout.addWidget(select_btn)
            self._theme_buttons[theme] = (button_frame, select_btn)
            select_layout.addWidget(button_frame)
        layout.addWidget(select_group)
        layout.addStretch()

    def _on_theme_selected(self, theme: Theme) -> None:
        if PYQT_VERSION == 0:
            return
        self.theme_changed.emit(theme)
    
    def set_current_theme(self, theme: Theme) -> None:
        if PYQT_VERSION == 0:
            return
        self._current_theme = theme
        theme_names = {
            Theme.MARIO: "🍄 Mario Theme",
            Theme.ZELDA: "⚔️ Zelda Theme",
            Theme.DKC: "🍌 DKC Theme",
        }
        self._current_theme_label.setText(theme_names.get(theme, theme.value))
        for t, (frame, btn) in self._theme_buttons.items():
            if t == theme:
                frame.setStyleSheet(
                    "QFrame { background-color: #C8E6C9; border-radius: 5px; border: 2px solid #4CAF50; }"
                )
                btn.setText("Current")
                btn.setEnabled(False)
            else:
                frame.setStyleSheet(
                    "QFrame { background-color: #FAFAFA; border-radius: 5px; }"
                    "QFrame:hover { background-color: #E3F2FD; }"
                )
                btn.setText("Select")
                btn.setEnabled(True)


class Dashboard(_DialogBase):
    """Dashboard showing stats and progress. Requirements: 10.1, 10.2, 10.3, 10.4, 10.5, 10.6, 10.7"""
    
    def __init__(self, progression_system: ProgressionSystem, achievement_system: AchievementSystem,
                 theme_manager: ThemeManager, powerup_system: Optional[PowerUpSystem] = None,
                 parent: Optional[QWidget] = None):
        if PYQT_VERSION == 0:
            logger.warning("PyQt not available - Dashboard cannot be created")
            return
        super().__init__(parent)
        self._progression_system = progression_system
        self._achievement_system = achievement_system
        self._theme_manager = theme_manager
        self._powerup_system = powerup_system
        self._refresh_timer: Optional[QTimer] = None
        self._setup_ui()
        self._connect_signals()
        self.refresh()

    def _setup_ui(self) -> None:
        if PYQT_VERSION == 0:
            return
        self.setWindowTitle("NintendAnki Dashboard")
        self.setMinimumSize(500, 600)
        self.resize(600, 700)
        
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(10)
        
        header_label = QLabel("🎮 NintendAnki Dashboard")
        header_label.setStyleSheet("font-size: 20px; font-weight: bold; color: #1976D2; padding: 10px;")
        header_label.setAlignment(Qt.AlignmentFlag.AlignCenter if PYQT_VERSION == 6 else Qt.AlignCenter)
        main_layout.addWidget(header_label)
        
        self._tab_widget = QTabWidget()
        self._tab_widget.setStyleSheet(
            "QTabWidget::pane { border: 1px solid #ddd; border-radius: 5px; }"
            "QTabBar::tab { padding: 8px 16px; }"
            "QTabBar::tab:selected { background-color: #E3F2FD; }"
        )
        
        self._stats_widget = StatsWidget()
        self._tab_widget.addTab(self._stats_widget, "📊 Stats")
        self._achievements_widget = AchievementsWidget()
        self._tab_widget.addTab(self._achievements_widget, "🏆 Achievements")
        self._powerups_widget = PowerUpsWidget()
        self._tab_widget.addTab(self._powerups_widget, "⚡ Power-Ups")
        self._theme_selector = ThemeSelectorWidget()
        self._tab_widget.addTab(self._theme_selector, "🎨 Themes")
        main_layout.addWidget(self._tab_widget)
        
        footer_layout = QHBoxLayout()
        self._refresh_btn = QPushButton("🔄 Refresh")
        self._refresh_btn.setStyleSheet(
            "QPushButton { background-color: #4CAF50; color: white; border-radius: 3px; padding: 8px 20px; }"
            "QPushButton:hover { background-color: #388E3C; }"
        )
        self._refresh_btn.clicked.connect(self.refresh)
        footer_layout.addWidget(self._refresh_btn)
        footer_layout.addStretch()
        close_btn = QPushButton("Close")
        close_btn.setStyleSheet(
            "QPushButton { background-color: #757575; color: white; border-radius: 3px; padding: 8px 20px; }"
            "QPushButton:hover { background-color: #616161; }"
        )
        close_btn.clicked.connect(self.close)
        footer_layout.addWidget(close_btn)
        main_layout.addLayout(footer_layout)
    
    def _connect_signals(self) -> None:
        if PYQT_VERSION == 0:
            return
        self._theme_selector.theme_changed.connect(self._on_theme_changed)
    
    def _on_theme_changed(self, theme: Theme) -> None:
        if PYQT_VERSION == 0:
            return
        self._theme_manager.set_theme(theme)
        self.refresh()

    def refresh(self) -> None:
        """Refresh all displayed data. Requirements: 10.7"""
        if PYQT_VERSION == 0:
            return
        state = self._progression_system.get_state()
        self._stats_widget.update_stats(state)
        theme_engine = self._theme_manager.get_theme_engine()
        theme_stats = theme_engine.get_dashboard_stats()
        self._stats_widget.update_theme_stats(theme_stats)
        achievements = self._achievement_system.get_all_achievements()
        self._achievements_widget.update_achievements(achievements)
        if self._powerup_system:
            inventory = self._powerup_system.get_inventory()
            active = self._powerup_system.get_active_powerups()
            self._powerups_widget.update_powerups(inventory, active)
        else:
            self._powerups_widget.update_powerups([], [])
        current_theme = self._theme_manager.get_current_theme()
        self._theme_selector.set_current_theme(current_theme)
    
    def show_stats_tab(self) -> None:
        if PYQT_VERSION == 0:
            return
        self._tab_widget.setCurrentWidget(self._stats_widget)
    
    def show_achievements_tab(self) -> None:
        if PYQT_VERSION == 0:
            return
        self._tab_widget.setCurrentWidget(self._achievements_widget)
    
    def show_powerups_tab(self) -> None:
        if PYQT_VERSION == 0:
            return
        self._tab_widget.setCurrentWidget(self._powerups_widget)
    
    def show_theme_selector(self) -> None:
        if PYQT_VERSION == 0:
            return
        self._tab_widget.setCurrentWidget(self._theme_selector)
    
    def start_auto_refresh(self, interval_ms: int = 1000) -> None:
        if PYQT_VERSION == 0:
            return
        if self._refresh_timer is None:
            self._refresh_timer = QTimer(self)
            self._refresh_timer.timeout.connect(self.refresh)
        self._refresh_timer.start(interval_ms)
    
    def stop_auto_refresh(self) -> None:
        if PYQT_VERSION == 0:
            return
        if self._refresh_timer:
            self._refresh_timer.stop()
    
    def closeEvent(self, event) -> None:
        self.stop_auto_refresh()
        if PYQT_VERSION > 0:
            super().closeEvent(event)
    
    def get_stats_widget(self) -> StatsWidget:
        return self._stats_widget
    
    def get_achievements_widget(self) -> AchievementsWidget:
        return self._achievements_widget
    
    def get_powerups_widget(self) -> PowerUpsWidget:
        return self._powerups_widget
    
    def get_theme_selector(self) -> ThemeSelectorWidget:
        return self._theme_selector
    
    def get_current_tab_index(self) -> int:
        if PYQT_VERSION == 0:
            return -1
        return self._tab_widget.currentIndex()
