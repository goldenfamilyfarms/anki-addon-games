"""DKCEngine for NintendAnki - DKC themed game mechanics.

This module implements the DKCEngine class that provides DKC-themed
game mechanics including banana collection, time trials, and
world completion tracking.

Requirements: 6.1, 6.2, 6.3, 6.4, 6.5, 6.6, 6.7, 6.8
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional, TYPE_CHECKING
import uuid

from core.theme_manager import ThemeEngine
from data.models import (
    Animation, AnimationType, Collectible, CollectibleType,
    Level, LevelView, Theme, ThemeStats,
)

if TYPE_CHECKING:
    from data.data_manager import DataManager

CARDS_FOR_FULL_COMPLETION = 500


@dataclass
class TimeTrial:
    """Represents a time trial challenge."""
    id: str
    duration_seconds: int
    started_at: Optional[datetime] = None
    remaining_seconds: float = 0.0
    cards_completed: int = 0
    active: bool = False
    completed: bool = False


@dataclass
class TimeTrialReward:
    """Rewards earned from completing a time trial."""
    trial_id: str
    base_bananas: int
    bonus_bananas: int
    total_bananas: int
    time_remaining: float
    cards_completed: int


@dataclass
class JungleWorld:
    """Represents a jungle world in the DKC theme."""
    id: str
    name: str
    completion_percentage: float = 0.0
    is_bonus_world: bool = False
    unlocked: bool = True
    levels: List[Level] = field(default_factory=list)


# Predefined jungle world names
JUNGLE_WORLD_NAMES = [
    "Kongo Jungle",
    "Monkey Mines",
    "Vine Valley",
    "Gorilla Glacier",
    "Kremkroc Industries",
]


class DKCEngine(ThemeEngine):
    """DKC theme engine with collectible and time trial mechanics.
    
    Implements the ThemeEngine interface with DKC-specific behavior:
    - Correct answers: Character collects bananas
    - Wrong answers: Character loses bananas
    - Time trials: Timed challenges for bonus rewards
    - World completion: Track progress toward 100%
    - Bonus world: Unlocks at 100% completion
    
    Requirements: 6.1, 6.2, 6.3, 6.4, 6.5, 6.6, 6.7, 6.8
    
    Attributes:
        data_manager: DataManager for accessing game state
        _banana_count: Running count of bananas collected
        _active_time_trial: Currently active time trial (if any)
        _bonus_world_unlocked: Whether the bonus world is unlocked
    """
    
    # Animation configuration
    DEFAULT_FPS = 30
    COLLECT_FRAMES = [0, 1, 2, 3, 4, 5]  # Banana collection animation frames
    DAMAGE_FRAMES = [0, 1, 2, 3]  # Damage animation frames
    RUN_FRAMES = [0, 1, 2, 3, 4, 5, 6, 7]  # Running animation frames
    IDLE_FRAMES = [0, 1]  # Idle animation frames
    VICTORY_FRAMES = [0, 1, 2, 3, 4]  # Victory animation frames
    
    # Time trial configuration
    DEFAULT_TIME_TRIAL_DURATION = 60  # seconds
    BANANAS_PER_CARD = 5  # Base bananas per card in time trial
    BONUS_BANANAS_PER_SECOND = 2  # Bonus bananas per remaining second
    
    # Banana loss configuration
    BANANAS_LOST_ON_WRONG = 3  # Bananas lost on wrong answer
    
    def __init__(self, data_manager: 'DataManager'):
        """Initialize the DKCEngine.
        
        Args:
            data_manager: DataManager for accessing game state and theme data
        """
        self.data_manager = data_manager
        self._banana_count = 0
        self._active_time_trial: Optional[TimeTrial] = None
        self._bonus_world_unlocked = False
        self._load_theme_state()
    
    def _load_theme_state(self) -> None:
        """Load DKC-specific state from the database."""
        game_state = self.data_manager.load_state()
        theme_state = game_state.theme_specific.get(Theme.DKC)
        if theme_state:
            self._banana_count = theme_state.bananas
            # Load bonus world status from extra_data if available
            if theme_state.extra_data:
                self._bonus_world_unlocked = theme_state.extra_data.get("bonus_world_unlocked", False)
    
    def _save_theme_state(self) -> None:
        """Save DKC-specific state to the database."""
        game_state = self.data_manager.load_state()
        theme_state = game_state.theme_specific.get(Theme.DKC)
        if theme_state:
            theme_state.bananas = self._banana_count
            theme_state.extra_data = {
                "bonus_world_unlocked": self._bonus_world_unlocked,
            }
            self.data_manager.save_state(game_state)

    def get_animation_for_correct(self) -> Animation:
        """Get animation to play for correct answer.
        
        Returns an animation showing DK collecting bananas.
        The animation includes the character movement and banana
        collection visual effect.
        
        Requirements: 6.2
        
        Returns:
            Animation for banana collection
        """
        return Animation(
            type=AnimationType.COLLECT,
            theme=Theme.DKC,
            sprite_sheet="assets/dkc/dk_collect_banana.png",
            frames=self.COLLECT_FRAMES,
            fps=self.DEFAULT_FPS,
            loop=False
        )
    
    def get_animation_for_wrong(self) -> Animation:
        """Get animation to play for wrong answer.
        
        Returns an animation showing DK losing bananas.
        The animation includes the character taking damage and
        bananas flying away.
        
        Requirements: 6.3
        
        Returns:
            Animation for losing bananas
        """
        return Animation(
            type=AnimationType.DAMAGE,
            theme=Theme.DKC,
            sprite_sheet="assets/dkc/dk_damage.png",
            frames=self.DAMAGE_FRAMES,
            fps=self.DEFAULT_FPS,
            loop=False
        )
    
    def get_collectible_for_correct(self) -> Collectible:
        """Get collectible earned for correct answer.
        
        Returns a banana collectible that is added to the player's
        collection when they answer correctly.
        
        Returns:
            Banana collectible
        """
        return Collectible(
            id="dkc_banana",
            type=CollectibleType.BANANA,
            theme=Theme.DKC,
            name="Banana",
            description="A delicious banana collected for a correct answer",
            icon="assets/dkc/banana.png",
            owned=True
        )

    def get_level_view(self, level: Level) -> LevelView:
        """Get the visual representation of a level.
        
        Returns a LevelView configured for DKC-style jungle
        gameplay with appropriate background and collectible positions.
        
        Requirements: 6.1
        
        Args:
            level: The level to get the view for
            
        Returns:
            LevelView with DKC-style visual representation
        """
        # Generate collectible positions based on level number
        collectibles = self._generate_level_collectibles(level)
        
        return LevelView(
            level=level,
            background=f"assets/dkc/jungle_level_{level.level_number}_bg.png",
            character_position=(50, 350),  # Starting position
            collectibles_visible=collectibles
        )
    
    def _generate_level_collectibles(self, level: Level) -> List[Collectible]:
        """Generate collectibles for a level.
        
        Creates a list of banana collectibles positioned throughout the level.
        Every fifth level also includes a DK coin.
        
        Args:
            level: The level to generate collectibles for
            
        Returns:
            List of collectibles for the level
        """
        collectibles = []
        # Generate bananas based on level number (more bananas in higher levels)
        num_bananas = 5 + (level.level_number * 3)
        
        for i in range(num_bananas):
            collectibles.append(Collectible(
                id=f"level_{level.level_number}_banana_{i}",
                type=CollectibleType.BANANA,
                theme=Theme.DKC,
                name="Banana",
                description="A collectible banana",
                icon="assets/dkc/banana.png",
                owned=False
            ))
        
        # Add DK coin every 5th level
        if level.level_number % 5 == 0:
            collectibles.append(Collectible(
                id=f"level_{level.level_number}_dk_coin",
                type=CollectibleType.DK_COIN,
                theme=Theme.DKC,
                name="DK Coin",
                description="A rare DK coin",
                icon="assets/dkc/dk_coin.png",
                owned=False
            ))
        
        return collectibles

    def get_dashboard_stats(self) -> ThemeStats:
        """Get theme-specific stats for dashboard.
        
        Returns DKC-specific statistics including banana count,
        DK coin count, and world completion for display in the dashboard.
        
        Returns:
            ThemeStats with DKC-specific statistics
        """
        # Load current state from database
        game_state = self.data_manager.load_state()
        theme_state = game_state.theme_specific.get(Theme.DKC)
        
        bananas = theme_state.bananas if theme_state else 0
        
        # Count DK coins earned
        dk_coins = self._count_dk_coins()
        
        # Calculate completion percentage
        completion = self.get_world_completion()
        
        return ThemeStats(
            theme=Theme.DKC,
            primary_collectible_name="Bananas",
            primary_collectible_count=bananas,
            secondary_stat_name="DK Coins",
            secondary_stat_value=dk_coins,
            completion_percentage=completion
        )
    
    def _count_dk_coins(self) -> int:
        """Count the number of DK coins earned.
        
        Returns:
            Number of DK coins collected
        """
        game_state = self.data_manager.load_state()
        dk_coin_count = 0
        
        for collectible in game_state.cosmetics:
            if collectible.type == CollectibleType.DK_COIN and collectible.owned:
                dk_coin_count += 1
        
        return dk_coin_count

    # Time Trial Methods (Requirements: 6.4, 6.5, 6.6)
    
    def start_time_trial(self, duration_seconds: int = None) -> TimeTrial:
        """Start a time trial challenge.
        
        Creates a new time trial with the specified duration.
        
        Requirements: 6.4
        
        Args:
            duration_seconds: Duration of the time trial (default: 60 seconds)
            
        Returns:
            TimeTrial instance representing the challenge
        """
        if duration_seconds is None:
            duration_seconds = self.DEFAULT_TIME_TRIAL_DURATION
        
        trial = TimeTrial(
            id=str(uuid.uuid4()),
            duration_seconds=duration_seconds,
            started_at=datetime.now(),
            remaining_seconds=float(duration_seconds),
            cards_completed=0,
            active=True,
            completed=False
        )
        
        self._active_time_trial = trial
        return trial
    
    def complete_time_trial(self, trial: TimeTrial, cards_completed: int) -> TimeTrialReward:
        """Complete a time trial and calculate rewards.
        
        Calculates base bananas from cards completed and bonus bananas
        from remaining time.
        
        Requirements: 6.5, 6.6
        
        Args:
            trial: The time trial to complete
            cards_completed: Number of cards completed during the trial
            
        Returns:
            TimeTrialReward with bananas earned
        """
        # Calculate base bananas from cards
        base_bananas = cards_completed * self.BANANAS_PER_CARD
        
        # Calculate bonus bananas from remaining time (Requirement 6.5)
        bonus_bananas = int(trial.remaining_seconds * self.BONUS_BANANAS_PER_SECOND)
        
        # No bonus if time expired (Requirement 6.6)
        if trial.remaining_seconds <= 0:
            bonus_bananas = 0
        
        total_bananas = base_bananas + bonus_bananas
        
        # Mark trial as completed
        trial.completed = True
        trial.active = False
        trial.cards_completed = cards_completed
        
        # Clear active trial
        if self._active_time_trial and self._active_time_trial.id == trial.id:
            self._active_time_trial = None
        
        # Add bananas to count
        self._banana_count += total_bananas
        self._save_theme_state()
        
        return TimeTrialReward(
            trial_id=trial.id,
            base_bananas=base_bananas,
            bonus_bananas=bonus_bananas,
            total_bananas=total_bananas,
            time_remaining=trial.remaining_seconds,
            cards_completed=cards_completed
        )

    def update_time_trial(self, delta_time: float) -> Optional[TimeTrial]:
        """Update the active time trial timer.
        
        Decrements the remaining time and marks the trial as inactive
        if time expires.
        
        Requirements: 6.6
        
        Args:
            delta_time: Time elapsed since last update (seconds)
            
        Returns:
            Updated TimeTrial or None if no active trial
        """
        if self._active_time_trial is None:
            return None
        
        self._active_time_trial.remaining_seconds -= delta_time
        
        # Ensure remaining time doesn't go negative
        if self._active_time_trial.remaining_seconds <= 0:
            self._active_time_trial.remaining_seconds = 0
            self._active_time_trial.active = False
        
        return self._active_time_trial
    
    def get_active_time_trial(self) -> Optional[TimeTrial]:
        """Get the currently active time trial.
        
        Returns:
            Active TimeTrial or None
        """
        return self._active_time_trial
    
    def is_time_trial_active(self) -> bool:
        """Check if a time trial is currently active.
        
        Returns:
            True if a time trial is active, False otherwise
        """
        return self._active_time_trial is not None and self._active_time_trial.active

    # World Completion Methods (Requirements: 6.7, 6.8)
    
    def get_world_completion(self) -> float:
        """Get world completion percentage.
        
        Calculates completion based on total cards reviewed.
        
        Requirements: 6.7
        
        Returns:
            Completion percentage (0.0 to 1.0)
        """
        game_state = self.data_manager.load_state()
        cards_reviewed = game_state.progression.total_cards_reviewed
        
        completion = cards_reviewed / CARDS_FOR_FULL_COMPLETION
        
        # Cap at 1.0
        completion = min(1.0, completion)
        
        # Check for bonus world unlock (Requirement 6.8)
        if completion >= 1.0 and not self._bonus_world_unlocked:
            self._bonus_world_unlocked = True
            self._save_theme_state()
        
        return completion
    
    def is_bonus_world_unlocked(self) -> bool:
        """Check if the bonus world is unlocked.
        
        Requirements: 6.8
        
        Returns:
            True if bonus world is unlocked, False otherwise
        """
        return self._bonus_world_unlocked

    # Banana Management Methods
    
    def get_banana_count(self) -> int:
        """Get the current banana count.
        
        Returns:
            Current number of bananas collected
        """
        return self._banana_count
    
    def add_bananas(self, amount: int = 1) -> int:
        """Add bananas to the player's collection.
        
        Args:
            amount: Number of bananas to add (default: 1)
            
        Returns:
            New total banana count
        """
        self._banana_count += amount
        self._save_theme_state()
        return self._banana_count
    
    def remove_bananas(self, amount: int = None) -> int:
        """Remove bananas from the player's collection.
        
        Requirements: 6.3
        
        Args:
            amount: Number of bananas to remove (default: BANANAS_LOST_ON_WRONG)
            
        Returns:
            New total banana count
        """
        if amount is None:
            amount = self.BANANAS_LOST_ON_WRONG
        
        self._banana_count = max(0, self._banana_count - amount)
        self._save_theme_state()
        return self._banana_count

    # Jungle World Methods
    
    def get_jungle_worlds(self) -> List[JungleWorld]:
        """Get all jungle worlds.
        
        Returns the list of jungle worlds with their unlock status.
        Worlds unlock progressively as completion increases.
        Bonus world is included only when unlocked.
        
        Requirements: 6.1, 6.8
        
        Returns:
            List of JungleWorld instances
        """
        completion = self.get_world_completion()
        worlds = []
        
        # Create main worlds
        for i, name in enumerate(JUNGLE_WORLD_NAMES):
            # Calculate unlock threshold for each world
            unlock_threshold = i * 0.2  # 0%, 20%, 40%, 60%, 80%
            unlocked = completion >= unlock_threshold or i == 0  # First world always unlocked
            
            world = JungleWorld(
                id=f"world_{i+1}",
                name=name,
                completion_percentage=min(1.0, max(0.0, (completion - unlock_threshold) / 0.2)) if unlocked else 0.0,
                is_bonus_world=False,
                unlocked=unlocked
            )
            worlds.append(world)
        
        # Add bonus world if unlocked (Requirement 6.8)
        if self._bonus_world_unlocked:
            bonus_world = JungleWorld(
                id="bonus_world",
                name="Lost World",
                completion_percentage=0.0,
                is_bonus_world=True,
                unlocked=True
            )
            worlds.append(bonus_world)
        
        return worlds

    # Animation Methods
    
    def get_run_animation(self) -> Animation:
        """Get the running animation for DK.
        
        Returns:
            Animation for DK running
        """
        return Animation(
            type=AnimationType.RUN,
            theme=Theme.DKC,
            sprite_sheet="assets/dkc/dk_run.png",
            frames=self.RUN_FRAMES,
            fps=self.DEFAULT_FPS,
            loop=True
        )
    
    def get_idle_animation(self) -> Animation:
        """Get the idle animation for DK.
        
        Returns:
            Animation for DK idle state
        """
        return Animation(
            type=AnimationType.IDLE,
            theme=Theme.DKC,
            sprite_sheet="assets/dkc/dk_idle.png",
            frames=self.IDLE_FRAMES,
            fps=15,  # Slower for idle
            loop=True
        )
    
    def get_victory_animation(self) -> Animation:
        """Get the victory animation for DK.
        
        Returns:
            Animation for DK victory celebration
        """
        return Animation(
            type=AnimationType.VICTORY,
            theme=Theme.DKC,
            sprite_sheet="assets/dkc/dk_victory.png",
            frames=self.VICTORY_FRAMES,
            fps=self.DEFAULT_FPS,
            loop=False
        )
