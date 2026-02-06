"""
Main entry point for NintendAnki add-on.

This module initializes all managers and systems, wires dependencies between
components, and registers Anki hooks on add-on load. It provides the main
entry point for the NintendAnki gamification add-on.

Requirements: 7.1, 7.2
"""

import logging
from pathlib import Path
from typing import Optional, TYPE_CHECKING

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# Data layer imports
from data.data_manager import DataManager
from data.config_manager import ConfigManager
from data.models import GameConfig, Theme

# Core layer imports
from core.scoring_engine import ScoringEngine
from core.progression_system import ProgressionSystem
from core.achievement_system import AchievementSystem
from core.powerup_system import PowerUpSystem
from core.level_system import LevelSystem
from core.reward_system import RewardSystem
from core.theme_manager import ThemeManager

# Integration layer imports
from integration.hook_handler import HookHandler, MockAnkiHookProvider
from integration.menu_integration import MenuIntegration, MockAnkiMenuProvider

# UI layer imports
from ui.asset_manager import AssetManager
from ui.animation_engine import AnimationEngine
from ui.game_window import GameWindow
from ui.dashboard import Dashboard
from ui.settings_panel import SettingsPanel


class NintendAnki:
    """Main application class for NintendAnki add-on.
    
    This class manages the lifecycle of all components and provides
    the main entry point for the add-on. It handles:
    - Initialization of all managers and systems
    - Wiring dependencies between components
    - Registration of Anki hooks on load
    - Clean shutdown on unload
    
    Requirements: 7.1, 7.2
    
    Attributes:
        addon_dir: Path to the add-on directory
        data_manager: DataManager for SQLite persistence
        config_manager: ConfigManager for JSON configuration
        scoring_engine: ScoringEngine for score calculations
        progression_system: ProgressionSystem for unified progression
        achievement_system: AchievementSystem for tracking achievements
        powerup_system: PowerUpSystem for managing power-ups
        level_system: LevelSystem for level management
        reward_system: RewardSystem for currency and rewards
        theme_manager: ThemeManager for theme selection
        asset_manager: AssetManager for sprite loading
        animation_engine: AnimationEngine for animations
        game_window: GameWindow for game display
        dashboard: Dashboard for stats display
        settings_panel: SettingsPanel for configuration
        hook_handler: HookHandler for Anki integration
        menu_integration: MenuIntegration for UI integration
    """
    
    def __init__(self, addon_dir: Optional[Path] = None, use_real_anki: bool = False):
        """Initialize the NintendAnki add-on.
        
        Args:
            addon_dir: Path to the add-on directory. Defaults to current directory.
            use_real_anki: If True, use real Anki hooks/menus. If False, use mocks.
        """
        self.addon_dir = addon_dir or Path(__file__).parent
        self._use_real_anki = use_real_anki
        self._initialized = False
        
        # Component references (initialized in _initialize_components)
        self.data_manager: Optional[DataManager] = None
        self.config_manager: Optional[ConfigManager] = None
        self.scoring_engine: Optional[ScoringEngine] = None
        self.progression_system: Optional[ProgressionSystem] = None
        self.achievement_system: Optional[AchievementSystem] = None
        self.powerup_system: Optional[PowerUpSystem] = None
        self.level_system: Optional[LevelSystem] = None
        self.reward_system: Optional[RewardSystem] = None
        self.theme_manager: Optional[ThemeManager] = None
        self.asset_manager: Optional[AssetManager] = None
        self.animation_engine: Optional[AnimationEngine] = None
        self.game_window: Optional[GameWindow] = None
        self.dashboard: Optional[Dashboard] = None
        self.settings_panel: Optional[SettingsPanel] = None
        self.hook_handler: Optional[HookHandler] = None
        self.menu_integration: Optional[MenuIntegration] = None
        
        logger.info(f"NintendAnki initializing from: {self.addon_dir}")
    
    def initialize(self) -> None:
        """Initialize all components and wire dependencies.
        
        This method performs the full initialization sequence:
        1. Initialize data layer (DataManager, ConfigManager)
        2. Initialize core systems (ScoringEngine, ProgressionSystem, etc.)
        3. Initialize UI components (GameWindow, Dashboard, SettingsPanel)
        4. Initialize integration components (HookHandler, MenuIntegration)
        5. Wire all dependencies between components
        6. Register Anki hooks
        
        Requirements: 7.1, 7.2
        """
        if self._initialized:
            logger.warning("NintendAnki already initialized")
            return
        
        try:
            # Step 1: Initialize data layer
            self._initialize_data_layer()
            
            # Step 2: Initialize core systems
            self._initialize_core_systems()
            
            # Step 3: Initialize UI components
            self._initialize_ui_components()
            
            # Step 4: Initialize integration components
            self._initialize_integration_components()
            
            # Step 5: Wire dependencies
            self._wire_dependencies()
            
            # Step 6: Register Anki hooks (Requirement 7.1)
            self._register_hooks()
            
            self._initialized = True
            logger.info("NintendAnki initialization complete")
            
        except Exception as e:
            logger.error(f"Failed to initialize NintendAnki: {e}")
            raise
    
    def _initialize_data_layer(self) -> None:
        """Initialize data layer components (DataManager, ConfigManager)."""
        logger.debug("Initializing data layer...")
        
        # Database path
        db_path = self.addon_dir / "data" / "nintendanki.db"
        
        # Config path
        config_path = self.addon_dir / "data" / "config.json"
        
        # Initialize DataManager
        self.data_manager = DataManager(db_path)
        self.data_manager.initialize_database()
        logger.debug(f"DataManager initialized with database: {db_path}")
        
        # Initialize ConfigManager
        self.config_manager = ConfigManager(config_path)
        logger.debug(f"ConfigManager initialized with config: {config_path}")
    
    def _initialize_core_systems(self) -> None:
        """Initialize core game systems."""
        logger.debug("Initializing core systems...")
        
        # Load configuration
        config = self.config_manager.load_config()
        
        # Initialize ScoringEngine (depends on config)
        self.scoring_engine = ScoringEngine(config)
        logger.debug("ScoringEngine initialized")
        
        # Initialize ProgressionSystem (depends on DataManager, ScoringEngine, config)
        self.progression_system = ProgressionSystem(
            data_manager=self.data_manager,
            scoring_engine=self.scoring_engine,
            config=config
        )
        logger.debug("ProgressionSystem initialized")
        
        # Initialize AchievementSystem (depends on DataManager)
        self.achievement_system = AchievementSystem(self.data_manager)
        logger.debug("AchievementSystem initialized")
        
        # Initialize PowerUpSystem (depends on DataManager)
        self.powerup_system = PowerUpSystem(self.data_manager)
        logger.debug("PowerUpSystem initialized")
        
        # Initialize LevelSystem (depends on DataManager)
        self.level_system = LevelSystem(self.data_manager)
        logger.debug("LevelSystem initialized")
        
        # Initialize RewardSystem (depends on DataManager)
        self.reward_system = RewardSystem(self.data_manager)
        logger.debug("RewardSystem initialized")
        
        # Initialize ThemeManager (depends on DataManager)
        self.theme_manager = ThemeManager(
            data_manager=self.data_manager,
            progression_system=self.progression_system
        )
        logger.debug("ThemeManager initialized")
    
    def _initialize_ui_components(self) -> None:
        """Initialize UI layer components."""
        logger.debug("Initializing UI components...")
        
        # Assets path
        assets_path = self.addon_dir / "assets"
        
        # Initialize AssetManager
        self.asset_manager = AssetManager(assets_path)
        logger.debug(f"AssetManager initialized with assets: {assets_path}")
        
        # Initialize AnimationEngine (depends on AssetManager)
        self.animation_engine = AnimationEngine(self.asset_manager)
        logger.debug("AnimationEngine initialized")
        
        # Initialize GameWindow (depends on ThemeManager, AnimationEngine)
        try:
            self.game_window = GameWindow(
                theme_manager=self.theme_manager,
                animation_engine=self.animation_engine
            )
            logger.debug("GameWindow initialized")
        except Exception as e:
            logger.warning(f"GameWindow initialization failed (PyQt may not be available): {e}")
            self.game_window = None
        
        # Initialize Dashboard (depends on ProgressionSystem, AchievementSystem, ThemeManager, PowerUpSystem)
        try:
            self.dashboard = Dashboard(
                progression_system=self.progression_system,
                achievement_system=self.achievement_system,
                theme_manager=self.theme_manager,
                powerup_system=self.powerup_system
            )
            logger.debug("Dashboard initialized")
        except Exception as e:
            logger.warning(f"Dashboard initialization failed (PyQt may not be available): {e}")
            self.dashboard = None
        
        # Initialize SettingsPanel (depends on ConfigManager)
        try:
            self.settings_panel = SettingsPanel(self.config_manager)
            logger.debug("SettingsPanel initialized")
        except Exception as e:
            logger.warning(f"SettingsPanel initialization failed (PyQt may not be available): {e}")
            self.settings_panel = None
    
    def _initialize_integration_components(self) -> None:
        """Initialize integration layer components."""
        logger.debug("Initializing integration components...")
        
        # Determine hook provider based on environment
        if self._use_real_anki:
            try:
                from integration.hook_handler import RealAnkiHookProvider
                hook_provider = RealAnkiHookProvider()
                logger.debug("Using RealAnkiHookProvider")
            except Exception as e:
                logger.warning(f"Failed to create RealAnkiHookProvider, using mock: {e}")
                hook_provider = MockAnkiHookProvider()
        else:
            hook_provider = MockAnkiHookProvider()
            logger.debug("Using MockAnkiHookProvider")
        
        # Initialize HookHandler (depends on ProgressionSystem, ScoringEngine)
        self.hook_handler = HookHandler(
            progression_system=self.progression_system,
            scoring_engine=self.scoring_engine,
            hook_provider=hook_provider
        )
        logger.debug("HookHandler initialized")
        
        # Determine menu provider based on environment
        if self._use_real_anki:
            try:
                from integration.menu_integration import RealAnkiMenuProvider
                menu_provider = RealAnkiMenuProvider()
                logger.debug("Using RealAnkiMenuProvider")
            except Exception as e:
                logger.warning(f"Failed to create RealAnkiMenuProvider, using mock: {e}")
                menu_provider = MockAnkiMenuProvider()
        else:
            menu_provider = MockAnkiMenuProvider()
            logger.debug("Using MockAnkiMenuProvider")
        
        # Initialize MenuIntegration (depends on Dashboard, GameWindow, SettingsPanel)
        self.menu_integration = MenuIntegration(
            dashboard=self.dashboard,
            game_window=self.game_window,
            settings_panel=self.settings_panel,
            menu_provider=menu_provider
        )
        logger.debug("MenuIntegration initialized")
    
    def _wire_dependencies(self) -> None:
        """Wire dependencies between components.
        
        This method sets up cross-component references and callbacks
        that couldn't be established during individual initialization.
        
        The event flow is:
        1. Card review happens in Anki
        2. HookHandler receives the event via Anki hooks
        3. HookHandler notifies ProgressionSystem and ScoringEngine (via process_review)
        4. HookHandler notifies registered callbacks (GameWindow, Dashboard)
        5. ProgressionSystem updates state and checks for unlocks
        6. ThemeManager provides theme-specific animations via get_theme_engine()
        7. GameWindow displays the animation and updates stats
        
        Requirements: 7.2, 7.4
        """
        logger.debug("Wiring dependencies...")
        
        # 1. Connect ThemeManager to ProgressionSystem for theme sync
        # This ensures power-ups are granted for the correct theme
        if self.theme_manager and self.progression_system:
            self.theme_manager.set_progression_system(self.progression_system)
            logger.debug("Connected ThemeManager to ProgressionSystem")
        
        # 2. Connect HookHandler to notify GameWindow on review events
        # This implements the complete event flow from review to UI (Requirement 7.4)
        if self.game_window is not None:
            def on_review_game_window(review_result):
                """Update game window when a card is reviewed.
                
                This callback implements the event flow:
                - HookHandler → ProgressionSystem (already done in on_card_reviewed)
                - ProgressionSystem → ThemeManager (via get_theme_engine)
                - ThemeManager → GameWindow (via show_animation)
                
                Requirements: 7.2, 7.4
                """
                try:
                    # Get updated progression state from ProgressionSystem
                    state = self.progression_system.get_state()
                    
                    # Update GameWindow display with current state (Requirement 7.4)
                    self.game_window.update_display(state)
                    
                    # Get theme-specific animation from ThemeManager
                    theme_engine = self.theme_manager.get_theme_engine()
                    if review_result.is_correct:
                        animation = theme_engine.get_animation_for_correct()
                    else:
                        animation = theme_engine.get_animation_for_wrong()
                    
                    # Display animation in GameWindow (Requirement 7.4)
                    self.game_window.show_animation(animation)
                    
                    # Check for achievements based on updated state
                    new_achievements = self.achievement_system.check_achievements(state)
                    if new_achievements:
                        logger.info(f"New achievements unlocked: {[a.name for a in new_achievements]}")
                    
                    # Check for level unlocks (every 50 correct answers)
                    new_level = self.progression_system.check_level_unlock()
                    if new_level is not None:
                        logger.info(f"New level unlocked: {new_level}")
                    
                    # Check for power-up grants (every 100 correct answers)
                    new_powerup = self.progression_system.check_powerup_grant()
                    if new_powerup is not None:
                        logger.info(f"New power-up granted: {new_powerup.name}")
                        
                except Exception as e:
                    # Log error but don't propagate - must not interfere with Anki
                    logger.error(f"Error in game window review callback: {e}")
            
            self.hook_handler.add_review_callback(on_review_game_window)
            logger.debug("Connected HookHandler to GameWindow (Requirement 7.4)")
        
        # 3. Connect HookHandler to notify Dashboard on review events
        # This ensures the dashboard updates in real-time (Requirement 10.7)
        if self.dashboard is not None:
            def on_review_dashboard(review_result):
                """Refresh dashboard when a card is reviewed.
                
                Requirements: 10.7 - Dashboard updates in real-time
                """
                try:
                    self.dashboard.refresh()
                except Exception as e:
                    logger.error(f"Error in dashboard review callback: {e}")
            
            self.hook_handler.add_review_callback(on_review_dashboard)
            logger.debug("Connected HookHandler to Dashboard (Requirement 10.7)")
        
        # 4. Connect GameWindow to ThemeManager for theme change notifications
        # This ensures the GameWindow updates when the theme changes
        if self.game_window is not None and self.theme_manager is not None:
            # Store original set_theme to wrap it
            original_set_theme = self.theme_manager.set_theme
            
            def set_theme_with_ui_update(theme):
                """Wrapper that updates GameWindow when theme changes."""
                original_set_theme(theme)
                # Update GameWindow with new theme
                self.game_window.switch_theme(theme)
                logger.debug(f"GameWindow theme switched to {theme.value}")
            
            # Replace set_theme with wrapped version
            self.theme_manager.set_theme = set_theme_with_ui_update
            logger.debug("Connected ThemeManager to GameWindow for theme changes")
        
        logger.debug("Dependencies wired successfully - Event flow complete")
    
    def _register_hooks(self) -> None:
        """Register Anki hooks for card review events.
        
        Requirements: 7.1 - WHEN Anki starts, THE Add-on SHALL register hooks
                           for card review events
        """
        logger.debug("Registering Anki hooks...")
        
        # Register hooks with Anki (Requirement 7.1)
        self.hook_handler.register_hooks()
        
        # Set up menu items and toolbar
        self.menu_integration.setup()
        
        logger.info("Anki hooks registered successfully")
    
    def shutdown(self) -> None:
        """Clean shutdown of all components.
        
        This method should be called when the add-on is unloaded to ensure
        proper cleanup of resources.
        """
        if not self._initialized:
            return
        
        logger.info("Shutting down NintendAnki...")
        
        try:
            # Unregister hooks
            if self.hook_handler:
                self.hook_handler.unregister_hooks()
            
            # Teardown menu integration
            if self.menu_integration:
                self.menu_integration.teardown()
            
            # Close UI windows
            if self.game_window:
                try:
                    self.game_window.close()
                except Exception:
                    pass
            
            if self.dashboard:
                try:
                    self.dashboard.close()
                except Exception:
                    pass
            
            if self.settings_panel:
                try:
                    self.settings_panel.close()
                except Exception:
                    pass
            
            self._initialized = False
            logger.info("NintendAnki shutdown complete")
            
        except Exception as e:
            logger.error(f"Error during shutdown: {e}")
    
    def show_game_window(self) -> None:
        """Show the game window."""
        if self.game_window:
            self.game_window.show()
            self.game_window.restore_position()
    
    def show_dashboard(self) -> None:
        """Show the dashboard."""
        if self.dashboard:
            self.dashboard.refresh()
            self.dashboard.show()
    
    def show_settings(self) -> None:
        """Show the settings panel."""
        if self.settings_panel:
            self.settings_panel.load_settings()
            self.settings_panel.show()
    
    @property
    def is_initialized(self) -> bool:
        """Check if the add-on is initialized."""
        return self._initialized


# Global instance for Anki add-on integration
_nintendanki_instance: Optional[NintendAnki] = None


def get_instance() -> Optional[NintendAnki]:
    """Get the global NintendAnki instance.
    
    Returns:
        The global NintendAnki instance, or None if not initialized.
    """
    return _nintendanki_instance


def initialize(addon_dir: Optional[Path] = None, use_real_anki: bool = False) -> NintendAnki:
    """Initialize the global NintendAnki instance.
    
    This function should be called when the add-on loads to set up
    all components and register Anki hooks.
    
    Args:
        addon_dir: Path to the add-on directory.
        use_real_anki: If True, use real Anki hooks/menus.
    
    Returns:
        The initialized NintendAnki instance.
        
    Requirements: 7.1, 7.2
    """
    global _nintendanki_instance
    
    if _nintendanki_instance is not None:
        logger.warning("NintendAnki already initialized, returning existing instance")
        return _nintendanki_instance
    
    _nintendanki_instance = NintendAnki(addon_dir, use_real_anki)
    _nintendanki_instance.initialize()
    
    return _nintendanki_instance


def shutdown() -> None:
    """Shutdown the global NintendAnki instance.
    
    This function should be called when the add-on unloads to ensure
    proper cleanup of resources.
    """
    global _nintendanki_instance
    
    if _nintendanki_instance is not None:
        _nintendanki_instance.shutdown()
        _nintendanki_instance = None


# Anki add-on entry point
# When running inside Anki, this code will be executed on add-on load
if __name__ != "__main__":
    try:
        # Check if we're running inside Anki
        from aqt import mw
        if mw is not None:
            # Initialize with real Anki integration
            addon_path = Path(__file__).parent
            initialize(addon_path, use_real_anki=True)
            logger.info("NintendAnki add-on loaded successfully")
    except ImportError:
        # Not running inside Anki, skip automatic initialization
        logger.debug("Not running inside Anki, skipping automatic initialization")
    except Exception as e:
        logger.error(f"Failed to load NintendAnki add-on: {e}")
