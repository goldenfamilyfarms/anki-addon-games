"""
GameWindow for NintendAnki.

This module implements the GameWindow class, a separate PyQt QMainWindow
that displays game animations and current state. It supports theme switching,
aspect ratio preservation during resizing, and real-time state updates.

Requirements: 9.1, 9.3, 9.4
"""

import logging
from typing import Optional, Callable

from data.models import (
    Animation,
    Level,
    ProgressionState,
    Theme,
)
from core.theme_manager import ThemeManager
from ui.animation_engine import AnimationEngine

# Configure logging
logger = logging.getLogger(__name__)


# Try to import PyQt6 first, then fall back to PyQt5
try:
    from PyQt6.QtWidgets import (
        QMainWindow,
        QWidget,
        QVBoxLayout,
        QHBoxLayout,
        QLabel,
        QFrame,
        QSizePolicy,
        QSystemTrayIcon,
        QMenu,
        QApplication,
    )
    from PyQt6.QtCore import Qt, QTimer, QSize, QSettings, pyqtSignal
    from PyQt6.QtGui import QPixmap, QResizeEvent, QCloseEvent, QAction, QIcon
    PYQT_VERSION = 6
except ImportError:
    try:
        from PyQt5.QtWidgets import (
            QMainWindow,
            QWidget,
            QVBoxLayout,
            QHBoxLayout,
            QLabel,
            QSizePolicy,
            QSystemTrayIcon,
            QMenu,
            QApplication,
            QAction,
        )
        from PyQt5.QtCore import Qt, QSettings, pyqtSignal
        from PyQt5.QtGui import QResizeEvent, QCloseEvent
        PYQT_VERSION = 5
    except ImportError:
        PYQT_VERSION = 0
        logger.warning("PyQt not available - GameWindow will have limited functionality")


class AspectRatioWidget(QWidget if PYQT_VERSION > 0 else object):
    """A widget that maintains aspect ratio when resized.
    
    This widget ensures that its contents maintain a fixed aspect ratio
    during window resizing, as required by Requirement 9.4.
    
    Attributes:
        aspect_ratio: The width/height ratio to maintain
        _content_widget: The widget containing the actual content
    """
    
    def __init__(self, aspect_ratio: float = 16/9, parent: Optional[QWidget] = None):
        """Initialize the AspectRatioWidget.
        
        Args:
            aspect_ratio: Width/height ratio to maintain (default 16:9)
            parent: Parent widget
        """
        if PYQT_VERSION == 0:
            return
            
        super().__init__(parent)
        self.aspect_ratio = aspect_ratio
        self._content_widget: Optional[QWidget] = None
        
        # Set up layout
        self._layout = QVBoxLayout(self)
        self._layout.setContentsMargins(0, 0, 0, 0)
        self._layout.setSpacing(0)
        
        # Container for centered content
        self._container = QWidget()
        self._container_layout = QVBoxLayout(self._container)
        self._container_layout.setContentsMargins(0, 0, 0, 0)
        self._container_layout.setAlignment(Qt.AlignmentFlag.AlignCenter if PYQT_VERSION == 6 else Qt.AlignCenter)
        
        self._layout.addWidget(self._container)
    
    def set_content(self, widget: QWidget) -> None:
        """Set the content widget that should maintain aspect ratio.
        
        Args:
            widget: The widget to display with maintained aspect ratio
        """
        if PYQT_VERSION == 0:
            return
            
        # Remove old content if any
        if self._content_widget is not None:
            self._container_layout.removeWidget(self._content_widget)
            self._content_widget.setParent(None)
        
        self._content_widget = widget
        self._container_layout.addWidget(widget)
        self._update_content_size()
    
    def set_aspect_ratio(self, ratio: float) -> None:
        """Set the aspect ratio to maintain.
        
        Args:
            ratio: Width/height ratio
        """
        self.aspect_ratio = ratio
        self._update_content_size()
    
    def resizeEvent(self, event: QResizeEvent) -> None:
        """Handle resize events to maintain aspect ratio.
        
        Args:
            event: The resize event
        """
        if PYQT_VERSION == 0:
            return
            
        super().resizeEvent(event)
        self._update_content_size()
    
    def _update_content_size(self) -> None:
        """Update the content widget size to maintain aspect ratio."""
        if PYQT_VERSION == 0 or self._content_widget is None:
            return
        
        # Get available size
        available_width = self.width()
        available_height = self.height()
        
        if available_width <= 0 or available_height <= 0:
            return
        
        # Calculate size that fits within available space while maintaining ratio
        if available_width / available_height > self.aspect_ratio:
            # Height is the limiting factor
            new_height = available_height
            new_width = int(new_height * self.aspect_ratio)
        else:
            # Width is the limiting factor
            new_width = available_width
            new_height = int(new_width / self.aspect_ratio)
        
        # Apply size to content widget
        self._content_widget.setFixedSize(new_width, new_height)


class StatsBar(QWidget if PYQT_VERSION > 0 else object):
    """A widget displaying game statistics (points, streak, health).
    
    Shows real-time game stats in a horizontal bar at the top of the window.
    """
    
    def __init__(self, parent: Optional[QWidget] = None):
        """Initialize the StatsBar.
        
        Args:
            parent: Parent widget
        """
        if PYQT_VERSION == 0:
            return
            
        super().__init__(parent)
        self._setup_ui()
    
    def _setup_ui(self) -> None:
        """Set up the stats bar UI."""
        if PYQT_VERSION == 0:
            return
            
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 5, 10, 5)
        layout.setSpacing(20)
        
        # Points display
        self._points_label = QLabel("Points: 0")
        self._points_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        layout.addWidget(self._points_label)
        
        # Streak display
        self._streak_label = QLabel("Streak: 0")
        self._streak_label.setStyleSheet("font-weight: bold; font-size: 14px; color: #FF8C00;")
        layout.addWidget(self._streak_label)
        
        # Health display
        self._health_label = QLabel("Health: 100%")
        self._health_label.setStyleSheet("font-weight: bold; font-size: 14px; color: #32CD32;")
        layout.addWidget(self._health_label)
        
        # Accuracy display
        self._accuracy_label = QLabel("Accuracy: 0%")
        self._accuracy_label.setStyleSheet("font-weight: bold; font-size: 14px; color: #4169E1;")
        layout.addWidget(self._accuracy_label)
        
        # Theme display
        self._theme_label = QLabel("Theme: Mario")
        self._theme_label.setStyleSheet("font-weight: bold; font-size: 14px; color: #9932CC;")
        layout.addWidget(self._theme_label)
        
        # Add stretch to push everything to the left
        layout.addStretch()
        
        # Set background
        self.setAutoFillBackground(True)
        self.setStyleSheet("background-color: #2D2D2D; border-radius: 5px;")
    
    def update_stats(self, state: ProgressionState, theme: Theme) -> None:
        """Update the displayed statistics.
        
        Args:
            state: Current progression state
            theme: Current theme
        """
        if PYQT_VERSION == 0:
            return
            
        self._points_label.setText(f"Points: {state.total_points:,}")
        self._streak_label.setText(f"Streak: {state.current_streak}")
        
        # Health as percentage (session_health is 0-100)
        health_pct = state.session_health
        self._health_label.setText(f"Health: {health_pct}%")
        
        # Color health based on value
        if health_pct > 60:
            self._health_label.setStyleSheet("font-weight: bold; font-size: 14px; color: #32CD32;")
        elif health_pct > 30:
            self._health_label.setStyleSheet("font-weight: bold; font-size: 14px; color: #FFA500;")
        else:
            self._health_label.setStyleSheet("font-weight: bold; font-size: 14px; color: #FF4500;")
        
        # Accuracy as percentage
        accuracy_pct = int(state.session_accuracy * 100)
        self._accuracy_label.setText(f"Accuracy: {accuracy_pct}%")
        
        # Theme name
        theme_name = theme.value.capitalize()
        self._theme_label.setText(f"Theme: {theme_name}")




class GameWindow(QMainWindow if PYQT_VERSION > 0 else object):
    """Separate window for game display and animations.
    
    The GameWindow is a standalone PyQt QMainWindow that displays game
    animations and current state. It is separate from Anki's main window
    (Requirement 9.1) and supports:
    
    - Playing animations with the AnimationEngine (Requirement 9.3)
    - Maintaining aspect ratios during resizing (Requirement 9.4)
    - Theme switching with visual transitions
    - Real-time state updates showing points, streak, health
    
    Requirements: 9.1, 9.3, 9.4
    
    Attributes:
        theme_manager: ThemeManager for theme operations
        animation_engine: AnimationEngine for playing animations
        _current_theme: Currently displayed theme
        _aspect_ratio_widget: Widget maintaining aspect ratio
        _stats_bar: Widget showing game statistics
        _animation_display: Label for displaying animations
        _tray_icon: System tray icon for minimize-to-tray
    """
    
    # Signal emitted when window is closed
    if PYQT_VERSION > 0:
        window_closed = pyqtSignal()
        theme_changed = pyqtSignal(Theme)
    
    # Default window settings
    DEFAULT_WIDTH = 800
    DEFAULT_HEIGHT = 600
    DEFAULT_ASPECT_RATIO = 16 / 9
    
    # Settings keys for position persistence
    SETTINGS_ORG = "NintendAnki"
    SETTINGS_APP = "GameWindow"
    
    def __init__(
        self,
        theme_manager: ThemeManager,
        animation_engine: AnimationEngine,
        parent: Optional[QWidget] = None
    ):
        """Initialize the GameWindow.
        
        Creates a separate PyQt window (Requirement 9.1) with a game display
        area, stats bar, and animation support.
        
        Args:
            theme_manager: ThemeManager for theme operations
            animation_engine: AnimationEngine for playing animations
            parent: Optional parent widget
        """
        if PYQT_VERSION == 0:
            logger.error("PyQt not available - GameWindow cannot be created")
            self.theme_manager = theme_manager
            self.animation_engine = animation_engine
            return
        
        super().__init__(parent)
        
        self.theme_manager = theme_manager
        self.animation_engine = animation_engine
        self._current_theme = theme_manager.get_current_theme()
        
        # Track current state
        self._current_state: Optional[ProgressionState] = None
        self._current_level: Optional[Level] = None
        
        # System tray icon
        self._tray_icon: Optional[QSystemTrayIcon] = None
        
        # Animation callbacks
        self._on_animation_complete: Optional[Callable] = None
        
        # Set up the window
        self._setup_window()
        self._setup_ui()
        self._setup_tray_icon()
        
        # Apply initial theme
        self._apply_theme_style(self._current_theme)
        
        logger.debug(f"GameWindow initialized with theme: {self._current_theme.value}")
    
    def _setup_window(self) -> None:
        """Set up the main window properties."""
        if PYQT_VERSION == 0:
            return
        
        # Window title and flags (Requirement 9.1 - separate window)
        self.setWindowTitle("NintendAnki - Game Window")
        self.setMinimumSize(400, 300)
        self.resize(self.DEFAULT_WIDTH, self.DEFAULT_HEIGHT)
        
        # Window flags - ensure it's a separate window
        self.setWindowFlags(
            Qt.WindowType.Window if PYQT_VERSION == 6 else Qt.Window
        )
    
    def _setup_ui(self) -> None:
        """Set up the user interface components."""
        if PYQT_VERSION == 0:
            return
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)
        
        # Stats bar at the top
        self._stats_bar = StatsBar()
        main_layout.addWidget(self._stats_bar)
        
        # Game display area with aspect ratio preservation (Requirement 9.4)
        self._aspect_ratio_widget = AspectRatioWidget(self.DEFAULT_ASPECT_RATIO)
        
        # Animation display label
        self._animation_display = QLabel()
        self._animation_display.setAlignment(
            Qt.AlignmentFlag.AlignCenter if PYQT_VERSION == 6 else Qt.AlignCenter
        )
        self._animation_display.setStyleSheet(
            "background-color: #1A1A1A; border: 2px solid #444; border-radius: 10px;"
        )
        self._animation_display.setSizePolicy(
            QSizePolicy.Policy.Expanding if PYQT_VERSION == 6 else QSizePolicy.Expanding,
            QSizePolicy.Policy.Expanding if PYQT_VERSION == 6 else QSizePolicy.Expanding
        )
        self._animation_display.setMinimumSize(200, 150)
        
        # Set placeholder text
        self._animation_display.setText("Game Display\n\nWaiting for card reviews...")
        self._animation_display.setStyleSheet(
            "background-color: #1A1A1A; border: 2px solid #444; "
            "border-radius: 10px; color: #888; font-size: 16px;"
        )
        
        self._aspect_ratio_widget.set_content(self._animation_display)
        main_layout.addWidget(self._aspect_ratio_widget, stretch=1)
        
        # Status bar
        self.statusBar().showMessage("Ready")
    
    def _setup_tray_icon(self) -> None:
        """Set up the system tray icon for minimize-to-tray."""
        if PYQT_VERSION == 0:
            return
        
        # Check if system tray is available
        if not QSystemTrayIcon.isSystemTrayAvailable():
            logger.debug("System tray not available")
            return
        
        self._tray_icon = QSystemTrayIcon(self)
        
        # Create tray menu
        tray_menu = QMenu()
        
        if PYQT_VERSION == 6:
            show_action = QAction("Show Window", self)
            show_action.triggered.connect(self._restore_from_tray)
            tray_menu.addAction(show_action)
            
            quit_action = QAction("Quit", self)
            quit_action.triggered.connect(self.close)
            tray_menu.addAction(quit_action)
        else:
            show_action = tray_menu.addAction("Show Window")
            show_action.triggered.connect(self._restore_from_tray)
            
            quit_action = tray_menu.addAction("Quit")
            quit_action.triggered.connect(self.close)
        
        self._tray_icon.setContextMenu(tray_menu)
        self._tray_icon.activated.connect(self._on_tray_activated)
        
        # Set tooltip
        self._tray_icon.setToolTip("NintendAnki Game Window")
    
    def _on_tray_activated(self, reason) -> None:
        """Handle tray icon activation.
        
        Args:
            reason: Activation reason
        """
        if PYQT_VERSION == 0:
            return
        
        # Double-click to restore
        trigger_reason = (
            QSystemTrayIcon.ActivationReason.DoubleClick 
            if PYQT_VERSION == 6 
            else QSystemTrayIcon.DoubleClick
        )
        if reason == trigger_reason:
            self._restore_from_tray()
    
    def _restore_from_tray(self) -> None:
        """Restore the window from system tray."""
        if PYQT_VERSION == 0:
            return
        
        self.show()
        self.raise_()
        self.activateWindow()
        
        if self._tray_icon:
            self._tray_icon.hide()
    
    def show_animation(self, animation: Animation) -> None:
        """Play an animation in the game window.
        
        Plays the specified animation using the AnimationEngine. The animation
        must start within 100ms of being called (Requirement 9.3).
        
        Args:
            animation: Animation to play
        """
        if PYQT_VERSION == 0:
            logger.debug(f"Animation requested but PyQt not available: {animation.type}")
            return
        
        logger.debug(f"Playing animation: {animation.type.value}")
        
        # Clear placeholder text
        self._animation_display.setText("")
        
        # Play the animation using the animation engine
        self.animation_engine.play_animation(
            animation,
            target=self._animation_display,
            on_complete=self._on_animation_complete_internal
        )
        
        # Update status bar
        self.statusBar().showMessage(f"Playing: {animation.type.value}")
    
    def _on_animation_complete_internal(self) -> None:
        """Internal callback when animation completes."""
        if PYQT_VERSION == 0:
            return
        
        self.statusBar().showMessage("Ready")
        
        # Call external callback if set
        if self._on_animation_complete:
            self._on_animation_complete()
    
    def set_animation_complete_callback(self, callback: Optional[Callable]) -> None:
        """Set a callback to be called when animations complete.
        
        Args:
            callback: Function to call when animation completes
        """
        self._on_animation_complete = callback
    
    def update_display(self, state: ProgressionState) -> None:
        """Update the display with current game state.
        
        Updates the stats bar and any other state-dependent UI elements.
        
        Args:
            state: Current progression state
        """
        if PYQT_VERSION == 0:
            logger.debug("Display update requested but PyQt not available")
            return
        
        self._current_state = state
        
        # Update stats bar
        self._stats_bar.update_stats(state, self._current_theme)
        
        # Update status bar with summary
        self.statusBar().showMessage(
            f"Points: {state.total_points:,} | "
            f"Streak: {state.current_streak} | "
            f"Cards: {state.total_cards_reviewed}"
        )
        
        logger.debug(f"Display updated: points={state.total_points}, streak={state.current_streak}")
    
    def switch_theme(self, theme: Theme) -> None:
        """Switch the visual theme of the game window.
        
        Transitions to the new theme's visual style. The transition should
        complete within 2 seconds (Requirement 1.4).
        
        Args:
            theme: Theme to switch to
        """
        if PYQT_VERSION == 0:
            self._current_theme = theme
            logger.debug(f"Theme switch requested but PyQt not available: {theme.value}")
            return
        
        logger.debug(f"Switching theme from {self._current_theme.value} to {theme.value}")
        
        old_theme = self._current_theme
        self._current_theme = theme
        
        # Apply theme-specific styling
        self._apply_theme_style(theme)
        
        # Update stats bar with new theme
        if self._current_state:
            self._stats_bar.update_stats(self._current_state, theme)
        
        # Emit theme changed signal
        if hasattr(self, 'theme_changed'):
            self.theme_changed.emit(theme)
        
        # Update status bar
        self.statusBar().showMessage(f"Theme changed to {theme.value.capitalize()}")
        
        logger.info(f"Theme switched from {old_theme.value} to {theme.value}")
    
    def _apply_theme_style(self, theme: Theme) -> None:
        """Apply theme-specific styling to the window.
        
        Args:
            theme: Theme to apply
        """
        if PYQT_VERSION == 0:
            return
        
        # Theme-specific color schemes
        theme_styles = {
            Theme.MARIO: {
                "primary": "#E52521",  # Mario red
                "secondary": "#049CD8",  # Mario blue
                "background": "#5C94FC",  # Sky blue
                "accent": "#FBD000",  # Coin gold
            },
            Theme.ZELDA: {
                "primary": "#1B8A2F",  # Zelda green
                "secondary": "#8B4513",  # Brown
                "background": "#2F4F2F",  # Dark green
                "accent": "#FFD700",  # Rupee gold
            },
            Theme.DKC: {
                "primary": "#8B4513",  # Brown
                "secondary": "#228B22",  # Forest green
                "background": "#2E8B57",  # Sea green
                "accent": "#FFD700",  # Banana yellow
            },
        }
        
        style = theme_styles.get(theme, theme_styles[Theme.MARIO])
        
        # Apply window style
        self.setStyleSheet(f"""
            QMainWindow {{
                background-color: {style['background']};
            }}
            QStatusBar {{
                background-color: #2D2D2D;
                color: white;
            }}
        """)
        
        # Update animation display border color
        self._animation_display.setStyleSheet(f"""
            background-color: #1A1A1A;
            border: 3px solid {style['primary']};
            border-radius: 10px;
            color: #888;
            font-size: 16px;
        """)
        
        # Update window title
        self.setWindowTitle(f"NintendAnki - {theme.value.capitalize()} Theme")
    
    def show_level(self, level: Level) -> None:
        """Display a playable level.
        
        Args:
            level: Level to display
        """
        if PYQT_VERSION == 0:
            logger.debug(f"Level display requested but PyQt not available: {level.name}")
            return
        
        self._current_level = level
        
        # Get level view from theme engine
        theme_engine = self.theme_manager.get_theme_engine()
        _ = theme_engine.get_level_view(level)  # Reserved for future use with level backgrounds
        
        # Update display with level info
        self._animation_display.setText(
            f"Level {level.level_number}: {level.name}\n\n"
            f"{level.description}"
        )
        
        self.statusBar().showMessage(f"Level: {level.name}")
        
        logger.debug(f"Displaying level: {level.name}")
    
    def minimize_to_tray(self) -> None:
        """Minimize the window to system tray."""
        if PYQT_VERSION == 0:
            return
        
        if self._tray_icon is None:
            logger.debug("System tray not available, minimizing normally")
            self.showMinimized()
            return
        
        self.hide()
        self._tray_icon.show()
        self._tray_icon.showMessage(
            "NintendAnki",
            "Game window minimized to tray. Double-click to restore.",
            QSystemTrayIcon.MessageIcon.Information if PYQT_VERSION == 6 else QSystemTrayIcon.Information,
            2000
        )
        
        logger.debug("Window minimized to tray")
    
    def restore_position(self) -> None:
        """Restore window position from saved state."""
        if PYQT_VERSION == 0:
            return
        
        settings = QSettings(self.SETTINGS_ORG, self.SETTINGS_APP)
        
        # Restore geometry
        geometry = settings.value("geometry")
        if geometry:
            self.restoreGeometry(geometry)
            logger.debug("Window position restored from settings")
        else:
            # Center on screen if no saved position
            self._center_on_screen()
    
    def save_position(self) -> None:
        """Save current window position."""
        if PYQT_VERSION == 0:
            return
        
        settings = QSettings(self.SETTINGS_ORG, self.SETTINGS_APP)
        settings.setValue("geometry", self.saveGeometry())
        
        logger.debug("Window position saved to settings")
    
    def _center_on_screen(self) -> None:
        """Center the window on the screen."""
        if PYQT_VERSION == 0:
            return
        
        screen = QApplication.primaryScreen()
        if screen:
            screen_geometry = screen.availableGeometry()
            window_geometry = self.frameGeometry()
            center_point = screen_geometry.center()
            window_geometry.moveCenter(center_point)
            self.move(window_geometry.topLeft())
    
    def closeEvent(self, event: QCloseEvent) -> None:
        """Handle window close event.
        
        Saves window position before closing.
        
        Args:
            event: Close event
        """
        if PYQT_VERSION == 0:
            return
        
        # Save position before closing
        self.save_position()
        
        # Hide tray icon
        if self._tray_icon:
            self._tray_icon.hide()
        
        # Stop any running animation
        self.animation_engine.stop_animation()
        
        # Emit closed signal
        if hasattr(self, 'window_closed'):
            self.window_closed.emit()
        
        logger.debug("GameWindow closed")
        
        super().closeEvent(event)
    
    def resizeEvent(self, event: QResizeEvent) -> None:
        """Handle window resize event.
        
        The AspectRatioWidget handles maintaining sprite aspect ratios
        (Requirement 9.4).
        
        Args:
            event: Resize event
        """
        if PYQT_VERSION == 0:
            return
        
        super().resizeEvent(event)
        
        # Log resize for debugging
        new_size = event.size()
        logger.debug(f"Window resized to {new_size.width()}x{new_size.height()}")
    
    def get_current_theme(self) -> Theme:
        """Get the currently displayed theme.
        
        Returns:
            Current theme
        """
        return self._current_theme
    
    def get_current_state(self) -> Optional[ProgressionState]:
        """Get the current progression state.
        
        Returns:
            Current state or None if not set
        """
        return self._current_state
    
    def is_animation_playing(self) -> bool:
        """Check if an animation is currently playing.
        
        Returns:
            True if animation is playing
        """
        return self.animation_engine.is_playing()
    
    def set_aspect_ratio(self, ratio: float) -> None:
        """Set the aspect ratio for the game display.
        
        Args:
            ratio: Width/height ratio
        """
        if PYQT_VERSION == 0:
            return
        
        self._aspect_ratio_widget.set_aspect_ratio(ratio)
        logger.debug(f"Aspect ratio set to {ratio}")
    
    def get_aspect_ratio(self) -> float:
        """Get the current aspect ratio.
        
        Returns:
            Current aspect ratio
        """
        if PYQT_VERSION == 0:
            return self.DEFAULT_ASPECT_RATIO
        
        return self._aspect_ratio_widget.aspect_ratio
