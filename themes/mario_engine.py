"""
MarioEngine for NintendAnki.

This module implements the MarioEngine class that provides Mario-themed
game mechanics including side-scrolling levels, coin collection, and
accuracy-based power-up rewards.

Requirements: 4.1, 4.2, 4.3, 4.4, 4.5, 4.6, 4.7, 4.8
"""

from dataclasses import dataclass, field
from typing import List, Optional, TYPE_CHECKING

from core.theme_manager import ThemeEngine
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

if TYPE_CHECKING:
    from data.data_manager import DataManager


@dataclass
class LevelSelectionView:
    """Visual representation of the Mario level selection screen.
    
    Displays available levels in a world map style, showing which
    levels are unlocked, completed, and available to play.
    
    Attributes:
        levels: List of levels to display
        current_level: Currently selected level
        world_name: Name of the current world
        background: Path to background image
        level_positions: Positions of levels on the map (level_id -> (x, y))
    """
    levels: List[Level]
    current_level: Optional[Level] = None
    world_name: str = "World 1"
    background: str = "assets/mario/level_select_bg.png"
    level_positions: dict = field(default_factory=dict)


@dataclass
class MarioPowerUp:
    """Mario-specific power-up with additional metadata.
    
    Extends the base PowerUp with Mario-specific attributes.
    
    Attributes:
        powerup: The base PowerUp instance
        accuracy_threshold: Minimum accuracy required to earn this power-up
        effect_description: Description of the power-up's effect
    """
    powerup: PowerUp
    accuracy_threshold: float
    effect_description: str


class MarioEngine(ThemeEngine):
    """Mario theme engine with side-scrolling mechanics.
    
    Implements the ThemeEngine interface with Mario-specific behavior:
    - Correct answers: Character moves forward and collects a coin
    - Wrong answers: Character takes damage
    - Accuracy rewards: Mushroom (95%+), Fire Flower (98%+), Star (100%)
    - Level selection: World map style level selection screen
    
    Requirements: 4.1, 4.2, 4.3, 4.4, 4.5, 4.6, 4.7, 4.8
    
    Attributes:
        data_manager: DataManager for accessing game state
        _coin_count: Running count of coins collected in current session
    """
    
    # Accuracy thresholds for power-up rewards (Requirements 4.4, 4.5, 4.6)
    MUSHROOM_THRESHOLD = 0.95
    FIRE_FLOWER_THRESHOLD = 0.98
    STAR_THRESHOLD = 1.0
    
    # Animation configuration
    DEFAULT_FPS = 30
    COLLECT_FRAMES = [0, 1, 2, 3, 4, 5]  # Coin collection animation frames
    DAMAGE_FRAMES = [0, 1, 2, 3]  # Damage animation frames
    RUN_FRAMES = [0, 1, 2, 3, 4, 5, 6, 7]  # Running animation frames
    JUMP_FRAMES = [0, 1, 2, 3]  # Jump animation frames
    
    def __init__(self, data_manager: 'DataManager'):
        """Initialize the MarioEngine.
        
        Args:
            data_manager: DataManager for accessing game state and theme data
        """
        self.data_manager = data_manager
        self._coin_count = 0
        self._load_theme_state()
    
    def _load_theme_state(self) -> None:
        """Load Mario-specific state from the database."""
        game_state = self.data_manager.load_state()
        theme_state = game_state.theme_specific.get(Theme.MARIO)
        if theme_state:
            self._coin_count = theme_state.coins
    
    def get_animation_for_correct(self) -> Animation:
        """Get animation to play for correct answer.
        
        Returns an animation showing Mario running forward and collecting
        a coin. The animation includes the character movement and coin
        collection visual effect.
        
        Requirements: 4.2, 4.7
        
        Returns:
            Animation for coin collection
        """
        return Animation(
            type=AnimationType.COLLECT,
            theme=Theme.MARIO,
            sprite_sheet="assets/mario/mario_collect_coin.png",
            frames=self.COLLECT_FRAMES,
            fps=self.DEFAULT_FPS,
            loop=False
        )
    
    def get_animation_for_wrong(self) -> Animation:
        """Get animation to play for wrong answer.
        
        Returns an animation showing Mario taking damage. The animation
        includes the character flinching and a damage visual effect.
        
        Requirements: 4.3, 4.7
        
        Returns:
            Animation for taking damage
        """
        return Animation(
            type=AnimationType.DAMAGE,
            theme=Theme.MARIO,
            sprite_sheet="assets/mario/mario_damage.png",
            frames=self.DAMAGE_FRAMES,
            fps=self.DEFAULT_FPS,
            loop=False
        )
    
    def get_collectible_for_correct(self) -> Collectible:
        """Get collectible earned for correct answer.
        
        Returns a coin collectible that is added to the player's
        collection when they answer correctly.
        
        Requirements: 4.2
        
        Returns:
            Coin collectible
        """
        return Collectible(
            id="mario_coin",
            type=CollectibleType.COIN,
            theme=Theme.MARIO,
            name="Coin",
            description="A shiny gold coin collected for a correct answer",
            icon="assets/mario/coin.png",
            owned=True
        )
    
    def get_level_view(self, level: Level) -> LevelView:
        """Get the visual representation of a level.
        
        Returns a LevelView configured for Mario-style side-scrolling
        gameplay with appropriate background and collectible positions.
        
        Requirements: 4.1
        
        Args:
            level: The level to get the view for
            
        Returns:
            LevelView with Mario-style visual representation
        """
        # Generate collectible positions based on level number
        collectibles = self._generate_level_collectibles(level)
        
        return LevelView(
            level=level,
            background=f"assets/mario/level_{level.level_number}_bg.png",
            character_position=(50, 300),  # Starting position
            collectibles_visible=collectibles
        )
    
    def _generate_level_collectibles(self, level: Level) -> List[Collectible]:
        """Generate collectibles for a level.
        
        Creates a list of coin collectibles positioned throughout the level.
        
        Args:
            level: The level to generate collectibles for
            
        Returns:
            List of collectibles for the level
        """
        collectibles = []
        # Generate coins based on level number (more coins in higher levels)
        num_coins = 5 + (level.level_number * 2)
        
        for i in range(num_coins):
            collectibles.append(Collectible(
                id=f"level_{level.level_number}_coin_{i}",
                type=CollectibleType.COIN,
                theme=Theme.MARIO,
                name="Coin",
                description="A collectible coin",
                icon="assets/mario/coin.png",
                owned=False
            ))
        
        return collectibles
    
    def get_dashboard_stats(self) -> ThemeStats:
        """Get theme-specific stats for dashboard.
        
        Returns Mario-specific statistics including coin count and
        star count for display in the dashboard.
        
        Returns:
            ThemeStats with Mario-specific statistics
        """
        # Load current state from database
        game_state = self.data_manager.load_state()
        theme_state = game_state.theme_specific.get(Theme.MARIO)
        
        coins = theme_state.coins if theme_state else 0
        
        # Calculate stars earned (from 100% accuracy completions)
        stars = self._count_stars_earned()
        
        # Calculate completion percentage based on levels completed
        completion = self._calculate_completion_percentage()
        
        return ThemeStats(
            theme=Theme.MARIO,
            primary_collectible_name="Coins",
            primary_collectible_count=coins,
            secondary_stat_name="Stars",
            secondary_stat_value=stars,
            completion_percentage=completion
        )
    
    def _count_stars_earned(self) -> int:
        """Count the number of star power-ups earned.
        
        Returns:
            Number of stars earned from 100% accuracy completions
        """
        game_state = self.data_manager.load_state()
        star_count = 0
        
        for powerup in game_state.powerups:
            if powerup.type == PowerUpType.STAR and powerup.theme == Theme.MARIO:
                star_count += powerup.quantity
        
        return star_count
    
    def _calculate_completion_percentage(self) -> float:
        """Calculate the Mario theme completion percentage.
        
        Based on levels completed vs total available levels.
        
        Returns:
            Completion percentage (0.0 to 1.0)
        """
        game_state = self.data_manager.load_state()
        
        mario_levels = [l for l in game_state.levels if l.theme == Theme.MARIO]
        if not mario_levels:
            return 0.0
        
        completed = sum(1 for l in mario_levels if l.completed)
        return completed / len(mario_levels)
    
    def get_powerup_for_accuracy(self, accuracy: float) -> Optional[MarioPowerUp]:
        """Get power-up based on level accuracy.
        
        Awards power-ups based on the accuracy achieved in a level:
        - 95%+ accuracy: Mushroom power-up
        - 98%+ accuracy: Fire Flower power-up  
        - 100% accuracy: Star power-up
        
        The highest applicable power-up is awarded (e.g., 100% accuracy
        awards a Star, not all three power-ups).
        
        Requirements: 4.4, 4.5, 4.6
        
        Args:
            accuracy: The accuracy achieved (0.0 to 1.0)
            
        Returns:
            MarioPowerUp if accuracy meets threshold, None otherwise
        """
        # Validate accuracy is in valid range
        if accuracy < 0.0 or accuracy > 1.0:
            return None
        
        # Check thresholds from highest to lowest (Requirement 4.6, 4.5, 4.4)
        if accuracy >= self.STAR_THRESHOLD:
            return self._create_star_powerup()
        elif accuracy >= self.FIRE_FLOWER_THRESHOLD:
            return self._create_fire_flower_powerup()
        elif accuracy >= self.MUSHROOM_THRESHOLD:
            return self._create_mushroom_powerup()
        
        return None
    
    def _create_mushroom_powerup(self) -> MarioPowerUp:
        """Create a mushroom power-up.
        
        Requirements: 4.4
        
        Returns:
            MarioPowerUp for mushroom
        """
        powerup = PowerUp(
            id="mario_mushroom",
            type=PowerUpType.MUSHROOM,
            theme=Theme.MARIO,
            name="Super Mushroom",
            description="Grow bigger and gain an extra hit point",
            icon="assets/mario/mushroom.png",
            quantity=1,
            duration_seconds=0  # Permanent until hit
        )
        
        return MarioPowerUp(
            powerup=powerup,
            accuracy_threshold=self.MUSHROOM_THRESHOLD,
            effect_description="Awarded for achieving 95%+ accuracy in a level"
        )
    
    def _create_fire_flower_powerup(self) -> MarioPowerUp:
        """Create a fire flower power-up.
        
        Requirements: 4.5
        
        Returns:
            MarioPowerUp for fire flower
        """
        powerup = PowerUp(
            id="mario_fire_flower",
            type=PowerUpType.FIRE_FLOWER,
            theme=Theme.MARIO,
            name="Fire Flower",
            description="Gain the ability to throw fireballs",
            icon="assets/mario/fire_flower.png",
            quantity=1,
            duration_seconds=0  # Permanent until hit
        )
        
        return MarioPowerUp(
            powerup=powerup,
            accuracy_threshold=self.FIRE_FLOWER_THRESHOLD,
            effect_description="Awarded for achieving 98%+ accuracy in a level"
        )
    
    def _create_star_powerup(self) -> MarioPowerUp:
        """Create a star power-up.
        
        Requirements: 4.6
        
        Returns:
            MarioPowerUp for star
        """
        powerup = PowerUp(
            id="mario_star",
            type=PowerUpType.STAR,
            theme=Theme.MARIO,
            name="Super Star",
            description="Become invincible for a limited time",
            icon="assets/mario/star.png",
            quantity=1,
            duration_seconds=30  # 30 seconds of invincibility
        )
        
        return MarioPowerUp(
            powerup=powerup,
            accuracy_threshold=self.STAR_THRESHOLD,
            effect_description="Awarded for achieving 100% accuracy in a level"
        )
    
    def get_level_selection_view(self) -> LevelSelectionView:
        """Get Mario-style level selection screen.
        
        Returns a level selection view showing all available levels
        in a world map style, with unlocked levels highlighted and
        completed levels marked.
        
        Requirements: 4.8
        
        Returns:
            LevelSelectionView with available Mario levels
        """
        game_state = self.data_manager.load_state()
        
        # Get all Mario levels
        mario_levels = [l for l in game_state.levels if l.theme == Theme.MARIO]
        
        # Sort by level number
        mario_levels.sort(key=lambda l: l.level_number)
        
        # Find current level (first unlocked but not completed, or last completed)
        current_level = None
        for level in mario_levels:
            if level.unlocked and not level.completed:
                current_level = level
                break
        
        if current_level is None and mario_levels:
            # All levels completed or none unlocked - show last unlocked
            unlocked_levels = [l for l in mario_levels if l.unlocked]
            if unlocked_levels:
                current_level = unlocked_levels[-1]
        
        # Generate level positions on the map
        level_positions = self._generate_level_positions(mario_levels)
        
        # Determine world name based on levels
        world_name = self._get_world_name(mario_levels)
        
        return LevelSelectionView(
            levels=mario_levels,
            current_level=current_level,
            world_name=world_name,
            background="assets/mario/world_map.png",
            level_positions=level_positions
        )
    
    def _generate_level_positions(self, levels: List[Level]) -> dict:
        """Generate positions for levels on the world map.
        
        Creates a dictionary mapping level IDs to (x, y) positions
        for display on the level selection screen.
        
        Args:
            levels: List of levels to position
            
        Returns:
            Dictionary mapping level_id to (x, y) position
        """
        positions = {}
        
        # Create a winding path for levels
        base_x = 100
        base_y = 400
        x_spacing = 120
        y_offset = 50
        
        for i, level in enumerate(levels):
            # Create a winding path pattern
            x = base_x + (i * x_spacing)
            y = base_y + (y_offset * ((-1) ** i))  # Alternate up/down
            positions[level.id] = (x, y)
        
        return positions
    
    def _get_world_name(self, levels: List[Level]) -> str:
        """Get the world name based on level progress.
        
        Args:
            levels: List of Mario levels
            
        Returns:
            World name string
        """
        if not levels:
            return "World 1"
        
        # Determine world based on highest unlocked level
        max_unlocked = 0
        for level in levels:
            if level.unlocked:
                max_unlocked = max(max_unlocked, level.level_number)
        
        # World changes every 8 levels
        world_number = (max_unlocked // 8) + 1
        return f"World {world_number}"
    
    def get_run_animation(self) -> Animation:
        """Get the running animation for Mario.
        
        Requirements: 4.7
        
        Returns:
            Animation for Mario running
        """
        return Animation(
            type=AnimationType.RUN,
            theme=Theme.MARIO,
            sprite_sheet="assets/mario/mario_run.png",
            frames=self.RUN_FRAMES,
            fps=self.DEFAULT_FPS,
            loop=True
        )
    
    def get_jump_animation(self) -> Animation:
        """Get the jumping animation for Mario.
        
        Requirements: 4.7
        
        Returns:
            Animation for Mario jumping
        """
        return Animation(
            type=AnimationType.JUMP,
            theme=Theme.MARIO,
            sprite_sheet="assets/mario/mario_jump.png",
            frames=self.JUMP_FRAMES,
            fps=self.DEFAULT_FPS,
            loop=False
        )
    
    def get_idle_animation(self) -> Animation:
        """Get the idle animation for Mario.
        
        Requirements: 4.7
        
        Returns:
            Animation for Mario idle state
        """
        return Animation(
            type=AnimationType.IDLE,
            theme=Theme.MARIO,
            sprite_sheet="assets/mario/mario_idle.png",
            frames=[0, 1],
            fps=15,  # Slower for idle
            loop=True
        )
    
    def add_coin(self) -> int:
        """Add a coin to the player's collection.
        
        Increments the coin count and persists to database.
        
        Returns:
            New total coin count
        """
        self._coin_count += 1
        
        # Persist to database
        game_state = self.data_manager.load_state()
        theme_state = game_state.theme_specific.get(Theme.MARIO)
        if theme_state:
            theme_state.coins = self._coin_count
            self.data_manager.save_state(game_state)
        
        return self._coin_count
    
    def get_coin_count(self) -> int:
        """Get the current coin count.
        
        Returns:
            Current number of coins collected
        """
        return self._coin_count
