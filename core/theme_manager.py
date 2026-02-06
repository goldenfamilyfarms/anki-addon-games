"""
ThemeManager for NintendAnki.

This module implements the ThemeManager class that manages theme selection
and switching, persisting the user's theme choice to the database.

Requirements: 1.1, 1.2, 1.3, 1.4, 1.5, 1.6
"""

from abc import ABC, abstractmethod
from typing import Optional, TYPE_CHECKING

from data.data_manager import DataManager
from data.models import (
    Animation,
    AnimationType,
    Collectible,
    Level,
    LevelView,
    Theme,
    ThemeStats,
)

if TYPE_CHECKING:
    from core.progression_system import ProgressionSystem


class ThemeEngine(ABC):
    """Abstract base class for theme-specific engines.
    
    Each theme (Mario, Zelda, DKC) has its own engine that provides
    theme-specific animations, collectibles, level views, and stats.
    
    Requirements: 4.1, 5.1, 6.1
    """
    
    @abstractmethod
    def get_animation_for_correct(self) -> Animation:
        """Get animation to play for correct answer.
        
        Returns:
            Animation to play when user answers correctly
        """
        pass
    
    @abstractmethod
    def get_animation_for_wrong(self) -> Animation:
        """Get animation to play for wrong answer.
        
        Returns:
            Animation to play when user answers incorrectly
        """
        pass
    
    @abstractmethod
    def get_collectible_for_correct(self) -> Collectible:
        """Get collectible earned for correct answer.
        
        Returns:
            Collectible item earned for correct answer
        """
        pass
    
    @abstractmethod
    def get_level_view(self, level: Level) -> LevelView:
        """Get the visual representation of a level.
        
        Args:
            level: The level to get the view for
            
        Returns:
            LevelView with visual representation data
        """
        pass
    
    @abstractmethod
    def get_dashboard_stats(self) -> ThemeStats:
        """Get theme-specific stats for dashboard.
        
        Returns:
            ThemeStats with theme-specific statistics
        """
        pass


class PlaceholderThemeEngine(ThemeEngine):
    """Placeholder theme engine for themes not yet fully implemented.
    
    This provides basic functionality until the actual theme engines
    (MarioEngine, ZeldaEngine, DKCEngine) are implemented.
    """
    
    def __init__(self, theme: Theme, data_manager: DataManager):
        """Initialize the placeholder engine.
        
        Args:
            theme: The theme this engine represents
            data_manager: DataManager for accessing theme state
        """
        self.theme = theme
        self.data_manager = data_manager
    
    def get_animation_for_correct(self) -> Animation:
        """Get animation to play for correct answer."""
        return Animation(
            type=AnimationType.COLLECT,
            theme=self.theme,
            sprite_sheet=f"assets/{self.theme.value}/collect.png",
            frames=[0, 1, 2, 3],
            fps=30,
            loop=False
        )
    
    def get_animation_for_wrong(self) -> Animation:
        """Get animation to play for wrong answer."""
        return Animation(
            type=AnimationType.DAMAGE,
            theme=self.theme,
            sprite_sheet=f"assets/{self.theme.value}/damage.png",
            frames=[0, 1, 2, 3],
            fps=30,
            loop=False
        )
    
    def get_collectible_for_correct(self) -> Collectible:
        """Get collectible earned for correct answer."""
        from data.models import CollectibleType
        
        # Theme-specific collectibles
        collectible_map = {
            Theme.MARIO: ("coin", CollectibleType.COIN, "A shiny gold coin"),
            Theme.ZELDA: ("rupee", CollectibleType.RUPEE, "A green rupee"),
            Theme.DKC: ("banana", CollectibleType.BANANA, "A yellow banana"),
        }
        
        name, ctype, desc = collectible_map.get(
            self.theme, 
            ("coin", CollectibleType.COIN, "A collectible item")
        )
        
        return Collectible(
            id=f"{self.theme.value}_{name}",
            type=ctype,
            theme=self.theme,
            name=name.capitalize(),
            description=desc,
            icon=f"assets/{self.theme.value}/{name}.png",
            owned=True
        )
    
    def get_level_view(self, level: Level) -> LevelView:
        """Get the visual representation of a level."""
        return LevelView(
            level=level,
            background=f"assets/{self.theme.value}/background.png",
            character_position=(0, 0),
            collectibles_visible=[]
        )
    
    def get_dashboard_stats(self) -> ThemeStats:
        """Get theme-specific stats for dashboard."""
        # Load theme state from database
        game_state = self.data_manager.load_state()
        theme_state = game_state.theme_specific.get(self.theme)
        
        # Theme-specific stat names and values
        if self.theme == Theme.MARIO:
            return ThemeStats(
                theme=self.theme,
                primary_collectible_name="Coins",
                primary_collectible_count=theme_state.coins if theme_state else 0,
                secondary_stat_name="Stars",
                secondary_stat_value=0,
                completion_percentage=0.0
            )
        elif self.theme == Theme.ZELDA:
            return ThemeStats(
                theme=self.theme,
                primary_collectible_name="Rupees",
                primary_collectible_count=0,
                secondary_stat_name="Hearts",
                secondary_stat_value=theme_state.hearts if theme_state else 3,
                completion_percentage=0.0
            )
        else:  # DKC
            return ThemeStats(
                theme=self.theme,
                primary_collectible_name="Bananas",
                primary_collectible_count=theme_state.bananas if theme_state else 0,
                secondary_stat_name="DK Coins",
                secondary_stat_value=0,
                completion_percentage=0.0
            )


class ThemeManager:
    """Manages theme selection and switching.
    
    The ThemeManager is responsible for:
    - Storing and retrieving the current theme from the database
    - Providing methods to get/set the current theme
    - Returning the appropriate theme engine for the current theme
    - Ensuring theme switching preserves progression data
    
    Requirements: 1.1, 1.2, 1.3, 1.4, 1.5, 1.6
    
    Attributes:
        data_manager: DataManager for persisting theme selection
        _current_theme: Currently active theme
        _theme_engines: Cache of theme engine instances
        _progression_system: Optional reference to ProgressionSystem for theme sync
    """
    
    # Available themes for selection (Requirement 1.1)
    AVAILABLE_THEMES = [Theme.MARIO, Theme.ZELDA, Theme.DKC]
    
    def __init__(self, data_manager: DataManager, 
                 progression_system: Optional['ProgressionSystem'] = None):
        """Initialize the ThemeManager.
        
        Args:
            data_manager: DataManager for persisting theme selection
            progression_system: Optional ProgressionSystem to sync theme changes
        """
        self.data_manager = data_manager
        self._progression_system = progression_system
        
        # Load current theme from database (Requirement 1.6)
        game_state = self.data_manager.load_state()
        self._current_theme = game_state.theme
        
        # Cache for theme engines
        self._theme_engines: dict[Theme, ThemeEngine] = {}
    
    def get_current_theme(self) -> Theme:
        """Get the currently active theme.
        
        Returns:
            The currently selected Theme
            
        Requirements: 1.6
        """
        return self._current_theme
    
    def set_theme(self, theme: Theme) -> None:
        """Switch to a new theme.
        
        This method:
        1. Validates the theme is one of the available options
        2. Updates the current theme in memory
        3. Persists the theme selection to the database
        4. Notifies the progression system of the theme change
        
        Note: Theme switching preserves all progression data (Requirement 1.3).
        The progression state (points, levels, achievements) is stored
        independently of the theme and is not modified during theme switches.
        
        Args:
            theme: The theme to switch to
            
        Raises:
            ValueError: If the theme is not a valid Theme enum value
            
        Requirements: 1.2, 1.3, 1.5
        """
        # Validate theme
        if not isinstance(theme, Theme):
            raise ValueError(f"Invalid theme: {theme}. Must be a Theme enum value.")
        
        if theme not in self.AVAILABLE_THEMES:
            raise ValueError(f"Theme {theme} is not available. "
                           f"Available themes: {self.AVAILABLE_THEMES}")
        
        # Update current theme in memory
        self._current_theme = theme
        
        # Persist theme selection to database (Requirement 1.5)
        # Load current state, update theme, and save
        game_state = self.data_manager.load_state()
        game_state.theme = theme
        self.data_manager.save_state(game_state)
        
        # Notify progression system of theme change (for power-up grants)
        if self._progression_system is not None:
            self._progression_system.set_current_theme(theme)
    
    def get_theme_engine(self) -> ThemeEngine:
        """Get the engine for the current theme.
        
        Returns a cached theme engine instance for the current theme.
        If no engine exists for the theme, creates a placeholder engine.
        
        Returns:
            ThemeEngine for the current theme
            
        Requirements: 1.2
        """
        if self._current_theme not in self._theme_engines:
            # Create placeholder engine until actual engines are implemented
            self._theme_engines[self._current_theme] = PlaceholderThemeEngine(
                self._current_theme, 
                self.data_manager
            )
        
        return self._theme_engines[self._current_theme]
    
    def register_theme_engine(self, theme: Theme, engine: ThemeEngine) -> None:
        """Register a theme engine for a specific theme.
        
        This allows actual theme engines (MarioEngine, ZeldaEngine, DKCEngine)
        to be registered once they are implemented.
        
        Args:
            theme: The theme to register the engine for
            engine: The ThemeEngine instance to register
        """
        self._theme_engines[theme] = engine
    
    def get_available_themes(self) -> list[Theme]:
        """Get list of available themes for selection.
        
        Returns:
            List of available Theme enum values
            
        Requirements: 1.1
        """
        return list(self.AVAILABLE_THEMES)
    
    def set_progression_system(self, progression_system: 'ProgressionSystem') -> None:
        """Set the progression system reference.
        
        This allows the ThemeManager to notify the ProgressionSystem
        when the theme changes, ensuring power-ups are granted for
        the correct theme.
        
        Args:
            progression_system: The ProgressionSystem instance
        """
        self._progression_system = progression_system
        # Sync current theme to progression system
        self._progression_system.set_current_theme(self._current_theme)
