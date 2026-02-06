"""LevelSystem for NintendAnki - manages level unlocking and completion."""

import uuid
from datetime import datetime
from typing import Dict, List, Optional

from data.data_manager import DataManager
from data.models import Level, LevelProgress, LevelReward, PowerUp, PowerUpType, Theme

MARIO_LEVELS = [
    {"name": "World 1-1", "description": "The classic starting level."},
    {"name": "World 1-2", "description": "Underground caverns."},
    {"name": "World 1-3", "description": "Athletic sky level."},
    {"name": "World 1-4", "description": "First castle."},
    {"name": "World 2-1", "description": "Desert land."},
    {"name": "World 2-2", "description": "Quicksand cavern."},
    {"name": "World 2-3", "description": "Pyramid secrets."},
    {"name": "World 2-4", "description": "Desert castle."},
    {"name": "World 3-1", "description": "Water world."},
    {"name": "World 3-2", "description": "Coral reef."},
    {"name": "World 3-3", "description": "Sunken ship."},
    {"name": "World 3-4", "description": "Water castle."},
    {"name": "World 4-1", "description": "Giant land."},
    {"name": "World 4-2", "description": "Giant underground."},
    {"name": "World 4-3", "description": "Giant sky."},
    {"name": "World 4-4", "description": "Giant castle."},
]

ZELDA_LEVELS = [
    {"name": "Kokiri Forest", "description": "Peaceful forest village."},
    {"name": "Deku Tree", "description": "First dungeon."},
    {"name": "Hyrule Field", "description": "Open plains."},
    {"name": "Kakariko Village", "description": "Mountain village."},
    {"name": "Death Mountain", "description": "Treacherous path."},
    {"name": "Dodongo Cavern", "description": "Dinosaur cavern."},
    {"name": "Zora River", "description": "River path."},
    {"name": "Zora Domain", "description": "Underwater kingdom."},
    {"name": "Jabu Jabu", "description": "Giant fish."},
    {"name": "Temple of Time", "description": "Sacred temple."},
    {"name": "Lost Woods", "description": "Forest maze."},
    {"name": "Forest Temple", "description": "Haunted temple."},
    {"name": "Lon Lon Ranch", "description": "Ranch visit."},
    {"name": "Fire Temple", "description": "Volcanic temple."},
    {"name": "Ice Cavern", "description": "Frozen passage."},
    {"name": "Water Temple", "description": "Water dungeon."},
]

DKC_LEVELS = [
    {"name": "Jungle Hijinxs", "description": "Lush jungle."},
    {"name": "Ropey Rampage", "description": "Vines and ropes."},
    {"name": "Reptile Rumble", "description": "Reptilian enemies."},
    {"name": "Coral Capers", "description": "Underwater caves."},
    {"name": "Barrel Canyon", "description": "Barrel cannons."},
    {"name": "Gnawty Lair", "description": "Beaver boss."},
    {"name": "Winky Walkway", "description": "Frog friend."},
    {"name": "Mine Cart", "description": "Dangerous mine."},
    {"name": "Bouncy Bonanza", "description": "Factory tires."},
    {"name": "Stop Go Station", "description": "Signal timing."},
    {"name": "Millstone Mayhem", "description": "Rolling stones."},
    {"name": "Necky Nuts", "description": "Vulture boss."},
    {"name": "Vulture Culture", "description": "Cliff vultures."},
    {"name": "Tree Top Town", "description": "Treetop village."},
    {"name": "Forest Frenzy", "description": "Forest canopy."},
    {"name": "Temple Tempest", "description": "Temple ruins."},
]

THEME_LEVELS = {Theme.MARIO: MARIO_LEVELS, Theme.ZELDA: ZELDA_LEVELS, Theme.DKC: DKC_LEVELS}
BASE_LEVEL_REWARD = 50
ACCURACY_BONUS_THRESHOLDS = [(1.0, 100), (0.98, 75), (0.95, 50), (0.90, 25)]


class LevelSystem:
    """Manages level unlocking and completion.
    
    The LevelSystem is responsible for:
    - Unlocking levels based on correct answers (1 per 50 correct)
    - Tracking which levels have been unlocked and completed
    - Providing level designs for each theme
    - Calculating completion rewards
    
    Requirements: 15.1, 15.2, 15.3, 15.4, 15.5, 15.6, 15.7
    
    Attributes:
        data_manager: DataManager for persisting level state
        _levels: Dictionary of levels by theme
    """
    
    def __init__(self, data_manager: DataManager):
        """Initialize the LevelSystem.
        
        Args:
            data_manager: DataManager for persisting level state
        """
        self.data_manager = data_manager
        self._levels: Dict[Theme, List[Level]] = {}
        self._initialize_levels()
        self._load_levels_from_db()
    
    def _initialize_levels(self) -> None:
        """Initialize level definitions for all themes."""
        for theme in Theme:
            theme_level_defs = THEME_LEVELS.get(theme, [])
            self._levels[theme] = []
            
            for i, level_def in enumerate(theme_level_defs):
                level = Level(
                    id=f"{theme.value}_level_{i + 1}",
                    theme=theme,
                    level_number=i + 1,
                    name=level_def["name"],
                    description=level_def.get("description", ""),
                    unlocked=(i == 0),  # First level is always unlocked
                    completed=False,
                    best_accuracy=None,
                    completion_date=None,
                    rewards_claimed=False
                )
                self._levels[theme].append(level)
    
    def _load_levels_from_db(self) -> None:
        """Load level state from database."""
        game_state = self.data_manager.load_state()
        
        for saved_level in game_state.levels:
            # Find and update the corresponding level
            if saved_level.theme in self._levels:
                for level in self._levels[saved_level.theme]:
                    if level.id == saved_level.id:
                        level.unlocked = saved_level.unlocked
                        level.completed = saved_level.completed
                        level.best_accuracy = saved_level.best_accuracy
                        level.completion_date = saved_level.completion_date
                        level.rewards_claimed = saved_level.rewards_claimed
                        break
    
    def unlock_level(self, theme: Theme) -> Optional[Level]:
        """Unlock the next level for a theme.
        
        Args:
            theme: The theme to unlock a level for
            
        Returns:
            The newly unlocked Level, or None if all levels are unlocked
            
        Requirements: 15.1
        """
        if theme not in self._levels:
            return None
        
        # Find the first locked level
        for level in self._levels[theme]:
            if not level.unlocked:
                level.unlocked = True
                self._save_levels_to_db()
                return level
        
        return None  # All levels already unlocked
    
    def complete_level(self, level_id: str, accuracy: float) -> Optional[LevelReward]:
        """Mark a level as completed and calculate rewards.
        
        Args:
            level_id: ID of the level to complete
            accuracy: Accuracy achieved (0.0 to 1.0)
            
        Returns:
            LevelReward with completion rewards, or None if level not found or locked
            
        Requirements: 15.5
        """
        level = self._find_level_by_id(level_id)
        if level is None:
            return None
        
        # Cannot complete a locked level
        if not level.unlocked:
            return None
        
        # Clamp accuracy to valid range
        accuracy = max(0.0, min(1.0, accuracy))
        
        # Check if this is a replay (already completed)
        is_replay = level.completed
        
        # Update level state
        level.completed = True
        level.completion_date = datetime.now()
        
        # Update best accuracy if this is better
        if level.best_accuracy is None or accuracy > level.best_accuracy:
            level.best_accuracy = accuracy
        
        # Calculate rewards
        currency_earned = BASE_LEVEL_REWARD
        
        # Add accuracy bonus
        for threshold, bonus in ACCURACY_BONUS_THRESHOLDS:
            if accuracy >= threshold:
                currency_earned += bonus
                break
        
        # Reduced rewards on replay
        if is_replay:
            currency_earned = currency_earned // 2
        
        # Determine powerup based on theme and accuracy
        powerup_earned = None
        if not is_replay and accuracy >= 0.95:
            powerup_earned = self._get_powerup_for_accuracy(level.theme, accuracy)
        
        # Mark rewards as claimed
        level.rewards_claimed = True
        
        # Save to database
        self._save_levels_to_db()
        
        return LevelReward(
            level_id=level_id,
            currency_earned=currency_earned,
            powerup_earned=powerup_earned,
            achievement_unlocked=None
        )
    
    def _get_powerup_for_accuracy(self, theme: Theme, accuracy: float) -> Optional[PowerUp]:
        """Get a powerup based on theme and accuracy.
        
        Args:
            theme: The theme of the level
            accuracy: The accuracy achieved
            
        Returns:
            PowerUp if accuracy meets threshold, None otherwise
        """
        if accuracy < 0.95:
            return None
        
        if theme == Theme.MARIO:
            if accuracy >= 1.0:
                powerup_type = PowerUpType.STAR
                name = "Super Star"
            elif accuracy >= 0.98:
                powerup_type = PowerUpType.FIRE_FLOWER
                name = "Fire Flower"
            else:
                powerup_type = PowerUpType.MUSHROOM
                name = "Super Mushroom"
        elif theme == Theme.ZELDA:
            powerup_type = PowerUpType.HEART_CONTAINER
            name = "Heart Container"
        else:  # DKC
            powerup_type = PowerUpType.GOLDEN_BANANA
            name = "Golden Banana"
        
        return PowerUp(
            id=f"{theme.value}_powerup_{powerup_type.value}",
            type=powerup_type,
            theme=theme,
            name=name,
            description=f"Earned for {accuracy*100:.0f}% accuracy",
            icon=f"assets/{theme.value}/{powerup_type.value}.png",
            quantity=1,
            duration_seconds=0
        )
    
    def get_available_levels(self, theme: Theme) -> List[Level]:
        """Get all unlocked levels for a theme.
        
        Args:
            theme: The theme to get levels for
            
        Returns:
            List of unlocked Level objects
            
        Requirements: 15.3
        """
        if theme not in self._levels:
            return []
        
        return [level for level in self._levels[theme] if level.unlocked]
    
    def get_level_progress(self) -> LevelProgress:
        """Get overall level progress stats.
        
        Returns:
            LevelProgress with overall statistics
            
        Requirements: 15.7
        """
        total_levels = sum(len(levels) for levels in self._levels.values())
        levels_unlocked = sum(
            1 for levels in self._levels.values() 
            for level in levels if level.unlocked
        )
        levels_completed = sum(
            1 for levels in self._levels.values() 
            for level in levels if level.completed
        )
        
        completion_percentage = (
            (levels_completed / total_levels) * 100.0 if total_levels > 0 else 0.0
        )
        
        return LevelProgress(
            total_levels=total_levels,
            levels_unlocked=levels_unlocked,
            levels_completed=levels_completed,
            completion_percentage=completion_percentage
        )
    
    def get_theme_level_progress(self, theme: Theme) -> LevelProgress:
        """Get level progress stats for a specific theme.
        
        Args:
            theme: The theme to get progress for
            
        Returns:
            LevelProgress with theme-specific statistics
        """
        if theme not in self._levels:
            return LevelProgress(
                total_levels=0,
                levels_unlocked=0,
                levels_completed=0,
                completion_percentage=0.0
            )
        
        theme_levels = self._levels[theme]
        total_levels = len(theme_levels)
        levels_unlocked = sum(1 for level in theme_levels if level.unlocked)
        levels_completed = sum(1 for level in theme_levels if level.completed)
        
        completion_percentage = (
            (levels_completed / total_levels) * 100.0 if total_levels > 0 else 0.0
        )
        
        return LevelProgress(
            total_levels=total_levels,
            levels_unlocked=levels_unlocked,
            levels_completed=levels_completed,
            completion_percentage=completion_percentage
        )
    
    def _find_level_by_id(self, level_id: str) -> Optional[Level]:
        """Find a level by its ID.
        
        Args:
            level_id: ID of the level to find
            
        Returns:
            Level if found, None otherwise
        """
        for levels in self._levels.values():
            for level in levels:
                if level.id == level_id:
                    return level
        return None
    
    def _save_levels_to_db(self) -> None:
        """Save all levels to the database.
        
        Requirements: 15.6
        """
        game_state = self.data_manager.load_state()
        
        # Flatten all levels into a single list
        all_levels = []
        for levels in self._levels.values():
            all_levels.extend(levels)
        
        game_state.levels = all_levels
        self.data_manager.save_state(game_state)
    
    def get_all_levels(self, theme: Optional[Theme] = None) -> List[Level]:
        """Get all levels, optionally filtered by theme.
        
        Args:
            theme: Optional theme to filter by
            
        Returns:
            List of all Level objects
        """
        if theme is not None:
            return list(self._levels.get(theme, []))
        
        all_levels = []
        for levels in self._levels.values():
            all_levels.extend(levels)
        return all_levels
    
    def get_level(self, level_id: str) -> Optional[Level]:
        """Get a level by its ID.
        
        Args:
            level_id: ID of the level to get
            
        Returns:
            Level if found, None otherwise
        """
        return self._find_level_by_id(level_id)
    
    def unlock_all_levels(self, theme: Optional[Theme] = None) -> int:
        """Unlock all levels for a theme or all themes.
        
        Args:
            theme: Optional theme to unlock levels for. If None, unlocks all themes.
            
        Returns:
            Number of levels unlocked
        """
        count = 0
        themes_to_unlock = [theme] if theme else list(Theme)
        
        for t in themes_to_unlock:
            if t in self._levels:
                for level in self._levels[t]:
                    if not level.unlocked:
                        level.unlocked = True
                        count += 1
        
        if count > 0:
            self._save_levels_to_db()
        
        return count
    
    def is_level_unlocked(self, level_id: str) -> bool:
        """Check if a level is unlocked.
        
        Args:
            level_id: ID of the level to check
            
        Returns:
            True if level is unlocked, False otherwise
        """
        level = self._find_level_by_id(level_id)
        return level.unlocked if level else False
    
    def is_level_completed(self, level_id: str) -> bool:
        """Check if a level is completed.
        
        Args:
            level_id: ID of the level to check
            
        Returns:
            True if level is completed, False otherwise
        """
        level = self._find_level_by_id(level_id)
        return level.completed if level else False
    
    def get_next_locked_level(self, theme: Theme) -> Optional[Level]:
        """Get the next locked level for a theme.
        
        Args:
            theme: The theme to get the next locked level for
            
        Returns:
            The next locked Level, or None if all levels are unlocked
        """
        if theme not in self._levels:
            return None
        
        for level in self._levels[theme]:
            if not level.unlocked:
                return level
        
        return None
    
    def get_total_levels_for_theme(self, theme: Theme) -> int:
        """Get the total number of levels for a theme.
        
        Args:
            theme: The theme to count levels for
            
        Returns:
            Total number of levels for the theme
        """
        return len(self._levels.get(theme, []))
    
    def reset_level_progress(self, level_id: str) -> bool:
        """Reset progress for a specific level.
        
        Args:
            level_id: ID of the level to reset
            
        Returns:
            True if level was reset, False if not found
        """
        level = self._find_level_by_id(level_id)
        if level is None:
            return False
        
        level.completed = False
        level.best_accuracy = None
        level.completion_date = None
        level.rewards_claimed = False
        
        self._save_levels_to_db()
        return True
