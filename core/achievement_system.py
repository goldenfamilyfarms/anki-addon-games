"""
AchievementSystem for NintendAnki.

This module implements the AchievementSystem class that tracks and unlocks
achievements based on user progress milestones.

Requirements: 14.1, 14.2, 14.3, 14.4, 14.5, 14.6
"""

from datetime import datetime
from typing import Dict, List, Optional

from data.data_manager import DataManager
from data.models import (
    Achievement,
    AchievementProgress,
    ProgressionState,
)


class AchievementSystem:
    """Tracks and unlocks achievements based on user progress.
    
    The AchievementSystem is responsible for:
    - Defining all achievements (cards reviewed, streaks, accuracy, levels, theme-specific)
    - Checking if achievements should be unlocked based on progression state
    - Tracking progress toward each achievement
    - Persisting achievement data to the database
    
    Attributes:
        data_manager: DataManager for persisting achievement state
        _achievements: Dictionary of all achievements by ID
        _unlocked_ids: Set of already unlocked achievement IDs
    """
    
    # Achievement definitions organized by category
    # Format: (id, name, description, icon, reward_currency, target)
    ACHIEVEMENT_DEFINITIONS = {
        # Cards Reviewed achievements (Requirement 14.6)
        "cards_reviewed": [
            ("cards_100", "First Steps", "Review 100 cards", "assets/achievements/cards_100.png", 50, 100),
            ("cards_500", "Getting Serious", "Review 500 cards", "assets/achievements/cards_500.png", 100, 500),
            ("cards_1000", "Dedicated Learner", "Review 1000 cards", "assets/achievements/cards_1000.png", 200, 1000),
            ("cards_5000", "Study Master", "Review 5000 cards", "assets/achievements/cards_5000.png", 500, 5000),
        ],
        # Streak achievements (Requirement 14.6)
        "streaks": [
            ("streak_10", "On a Roll", "Achieve a streak of 10 correct answers", "assets/achievements/streak_10.png", 25, 10),
            ("streak_25", "Unstoppable", "Achieve a streak of 25 correct answers", "assets/achievements/streak_25.png", 75, 25),
            ("streak_50", "Streak Master", "Achieve a streak of 50 correct answers", "assets/achievements/streak_50.png", 150, 50),
            ("streak_100", "Perfect Memory", "Achieve a streak of 100 correct answers", "assets/achievements/streak_100.png", 300, 100),
        ],
        # Accuracy achievements (Requirement 14.6)
        "accuracy": [
            ("accuracy_90", "Sharp Mind", "Achieve 90% accuracy in a session", "assets/achievements/accuracy_90.png", 50, 90),
            ("accuracy_95", "Near Perfect", "Achieve 95% accuracy in a session", "assets/achievements/accuracy_95.png", 100, 95),
            ("accuracy_100", "Flawless", "Achieve 100% accuracy in a session", "assets/achievements/accuracy_100.png", 250, 100),
        ],
        # Levels completed achievements (Requirement 14.6)
        "levels": [
            ("levels_1", "Level Up!", "Complete your first level", "assets/achievements/levels_1.png", 25, 1),
            ("levels_5", "Rising Star", "Complete 5 levels", "assets/achievements/levels_5.png", 75, 5),
            ("levels_10", "Veteran Player", "Complete 10 levels", "assets/achievements/levels_10.png", 150, 10),
            ("levels_25", "Level Champion", "Complete 25 levels", "assets/achievements/levels_25.png", 300, 25),
        ],
        # Theme-specific milestones (Requirement 14.6)
        "mario_theme": [
            ("mario_coins_100", "Coin Collector", "Collect 100 coins in Mario theme", "assets/achievements/mario_coins.png", 50, 100),
            ("mario_coins_500", "Gold Hoarder", "Collect 500 coins in Mario theme", "assets/achievements/mario_coins_500.png", 150, 500),
            ("mario_powerup_star", "Star Power", "Earn a Star power-up in Mario theme", "assets/achievements/mario_star.png", 100, 1),
        ],
        "zelda_theme": [
            ("zelda_boss_1", "Boss Slayer", "Defeat your first boss in Zelda theme", "assets/achievements/zelda_boss.png", 75, 1),
            ("zelda_boss_5", "Dungeon Master", "Defeat 5 bosses in Zelda theme", "assets/achievements/zelda_boss_5.png", 200, 5),
            ("zelda_hearts_10", "Heart Collector", "Collect 10 heart containers in Zelda theme", "assets/achievements/zelda_hearts.png", 100, 10),
        ],
        "dkc_theme": [
            ("dkc_bananas_100", "Banana Bunch", "Collect 100 bananas in DKC theme", "assets/achievements/dkc_bananas.png", 50, 100),
            ("dkc_bananas_1000", "Banana King", "Collect 1000 bananas in DKC theme", "assets/achievements/dkc_bananas_1000.png", 200, 1000),
            ("dkc_time_trial", "Speed Runner", "Complete a time trial in DKC theme", "assets/achievements/dkc_time_trial.png", 75, 1),
        ],
    }
    
    def __init__(self, data_manager: DataManager):
        """Initialize the AchievementSystem.
        
        Args:
            data_manager: DataManager for persisting achievement state
        """
        self.data_manager = data_manager
        self._achievements: Dict[str, Achievement] = {}
        self._unlocked_ids: set = set()
        
        # Initialize all achievements
        self._initialize_achievements()
        
        # Load existing achievement state from database
        self._load_achievements_from_db()
    
    def _initialize_achievements(self) -> None:
        """Initialize all achievement definitions.
        
        Creates Achievement objects for all predefined achievements.
        """
        for category, achievements in self.ACHIEVEMENT_DEFINITIONS.items():
            for achievement_id, name, description, icon, reward, target in achievements:
                self._achievements[achievement_id] = Achievement(
                    id=achievement_id,
                    name=name,
                    description=description,
                    icon=icon,
                    reward_currency=reward,
                    unlocked=False,
                    unlock_date=None,
                    progress=0,
                    target=target,
                )
    
    def _load_achievements_from_db(self) -> None:
        """Load existing achievement state from the database.
        
        Updates achievement progress and unlock status from persisted data.
        """
        game_state = self.data_manager.load_state()
        
        for saved_achievement in game_state.achievements:
            if saved_achievement.id in self._achievements:
                # Update the achievement with saved state
                self._achievements[saved_achievement.id].unlocked = saved_achievement.unlocked
                self._achievements[saved_achievement.id].unlock_date = saved_achievement.unlock_date
                self._achievements[saved_achievement.id].progress = saved_achievement.progress
                
                if saved_achievement.unlocked:
                    self._unlocked_ids.add(saved_achievement.id)
    
    def check_achievements(self, state: ProgressionState, 
                          theme_state: Optional[Dict] = None) -> List[Achievement]:
        """Check if any achievements should be unlocked.
        
        Evaluates the current progression state against all achievement
        criteria and unlocks any achievements that have been earned.
        
        Args:
            state: Current ProgressionState to check against
            theme_state: Optional dictionary with theme-specific data
                        (coins, bananas, hearts, bosses_defeated, etc.)
        
        Returns:
            List of newly unlocked achievements
            
        Requirements: 14.1, 14.2, 14.3
        """
        newly_unlocked: List[Achievement] = []
        theme_state = theme_state or {}
        
        # Check cards reviewed achievements
        for achievement in self._get_category_achievements("cards_reviewed"):
            if achievement.id not in self._unlocked_ids:
                self._update_progress(achievement, state.total_cards_reviewed)
                if state.total_cards_reviewed >= achievement.target:
                    self._unlock_achievement(achievement)
                    newly_unlocked.append(achievement)
        
        # Check streak achievements (use best_streak for permanent achievements)
        for achievement in self._get_category_achievements("streaks"):
            if achievement.id not in self._unlocked_ids:
                # Use the higher of current_streak or best_streak
                best = max(state.current_streak, state.best_streak)
                self._update_progress(achievement, best)
                if best >= achievement.target:
                    self._unlock_achievement(achievement)
                    newly_unlocked.append(achievement)
        
        # Check accuracy achievements (session-based)
        # Only check if there have been reviews in the session
        if state.total_cards_reviewed > 0:
            accuracy_percent = int(state.session_accuracy * 100)
            for achievement in self._get_category_achievements("accuracy"):
                if achievement.id not in self._unlocked_ids:
                    self._update_progress(achievement, accuracy_percent)
                    if accuracy_percent >= achievement.target:
                        self._unlock_achievement(achievement)
                        newly_unlocked.append(achievement)
        
        # Check levels completed achievements
        for achievement in self._get_category_achievements("levels"):
            if achievement.id not in self._unlocked_ids:
                self._update_progress(achievement, state.levels_completed)
                if state.levels_completed >= achievement.target:
                    self._unlock_achievement(achievement)
                    newly_unlocked.append(achievement)
        
        # Check theme-specific achievements
        newly_unlocked.extend(self._check_theme_achievements(theme_state))
        
        # Persist updated achievements to database
        if newly_unlocked:
            self._save_achievements_to_db()
        
        return newly_unlocked
    
    def _check_theme_achievements(self, theme_state: Dict) -> List[Achievement]:
        """Check theme-specific achievements.
        
        Args:
            theme_state: Dictionary with theme-specific data
        
        Returns:
            List of newly unlocked theme achievements
        """
        newly_unlocked: List[Achievement] = []
        
        # Mario theme achievements
        mario_coins = theme_state.get("mario_coins", 0)
        mario_stars = theme_state.get("mario_stars", 0)
        
        for achievement in self._get_category_achievements("mario_theme"):
            if achievement.id not in self._unlocked_ids:
                if achievement.id == "mario_coins_100":
                    self._update_progress(achievement, mario_coins)
                    if mario_coins >= achievement.target:
                        self._unlock_achievement(achievement)
                        newly_unlocked.append(achievement)
                elif achievement.id == "mario_coins_500":
                    self._update_progress(achievement, mario_coins)
                    if mario_coins >= achievement.target:
                        self._unlock_achievement(achievement)
                        newly_unlocked.append(achievement)
                elif achievement.id == "mario_powerup_star":
                    self._update_progress(achievement, mario_stars)
                    if mario_stars >= achievement.target:
                        self._unlock_achievement(achievement)
                        newly_unlocked.append(achievement)
        
        # Zelda theme achievements
        zelda_bosses = theme_state.get("zelda_bosses_defeated", 0)
        zelda_hearts = theme_state.get("zelda_hearts", 0)
        
        for achievement in self._get_category_achievements("zelda_theme"):
            if achievement.id not in self._unlocked_ids:
                if achievement.id == "zelda_boss_1":
                    self._update_progress(achievement, zelda_bosses)
                    if zelda_bosses >= achievement.target:
                        self._unlock_achievement(achievement)
                        newly_unlocked.append(achievement)
                elif achievement.id == "zelda_boss_5":
                    self._update_progress(achievement, zelda_bosses)
                    if zelda_bosses >= achievement.target:
                        self._unlock_achievement(achievement)
                        newly_unlocked.append(achievement)
                elif achievement.id == "zelda_hearts_10":
                    self._update_progress(achievement, zelda_hearts)
                    if zelda_hearts >= achievement.target:
                        self._unlock_achievement(achievement)
                        newly_unlocked.append(achievement)
        
        # DKC theme achievements
        dkc_bananas = theme_state.get("dkc_bananas", 0)
        dkc_time_trials = theme_state.get("dkc_time_trials_completed", 0)
        
        for achievement in self._get_category_achievements("dkc_theme"):
            if achievement.id not in self._unlocked_ids:
                if achievement.id == "dkc_bananas_100":
                    self._update_progress(achievement, dkc_bananas)
                    if dkc_bananas >= achievement.target:
                        self._unlock_achievement(achievement)
                        newly_unlocked.append(achievement)
                elif achievement.id == "dkc_bananas_1000":
                    self._update_progress(achievement, dkc_bananas)
                    if dkc_bananas >= achievement.target:
                        self._unlock_achievement(achievement)
                        newly_unlocked.append(achievement)
                elif achievement.id == "dkc_time_trial":
                    self._update_progress(achievement, dkc_time_trials)
                    if dkc_time_trials >= achievement.target:
                        self._unlock_achievement(achievement)
                        newly_unlocked.append(achievement)
        
        return newly_unlocked
    
    def _get_category_achievements(self, category: str) -> List[Achievement]:
        """Get all achievements in a category.
        
        Args:
            category: Category name from ACHIEVEMENT_DEFINITIONS
        
        Returns:
            List of Achievement objects in the category
        """
        if category not in self.ACHIEVEMENT_DEFINITIONS:
            return []
        
        return [
            self._achievements[achievement_id]
            for achievement_id, _, _, _, _, _ in self.ACHIEVEMENT_DEFINITIONS[category]
            if achievement_id in self._achievements
        ]
    
    def _update_progress(self, achievement: Achievement, current_value: int) -> None:
        """Update progress for an achievement.
        
        Args:
            achievement: Achievement to update
            current_value: Current progress value
        """
        # Cap progress at target (don't exceed 100%)
        achievement.progress = min(current_value, achievement.target)
    
    def _unlock_achievement(self, achievement: Achievement) -> None:
        """Unlock an achievement.
        
        Args:
            achievement: Achievement to unlock
        """
        achievement.unlocked = True
        achievement.unlock_date = datetime.now()
        achievement.progress = achievement.target
        self._unlocked_ids.add(achievement.id)
    
    def _save_achievements_to_db(self) -> None:
        """Save all achievements to the database.
        
        Requirements: 14.4
        """
        game_state = self.data_manager.load_state()
        game_state.achievements = list(self._achievements.values())
        self.data_manager.save_state(game_state)
    
    def get_all_achievements(self) -> List[Achievement]:
        """Get all achievements with their unlock status.
        
        Returns a list of all achievements, including both locked and
        unlocked achievements with their current progress.
        
        Returns:
            List of all Achievement objects
            
        Requirements: 14.5
        """
        return list(self._achievements.values())
    
    def get_progress(self, achievement_id: str) -> AchievementProgress:
        """Get progress toward a specific achievement.
        
        Args:
            achievement_id: ID of the achievement to check
        
        Returns:
            AchievementProgress with current progress details
            
        Raises:
            KeyError: If achievement_id is not found
        """
        if achievement_id not in self._achievements:
            raise KeyError(f"Achievement '{achievement_id}' not found")
        
        achievement = self._achievements[achievement_id]
        
        # Calculate percentage (avoid division by zero)
        if achievement.target > 0:
            percentage = min(achievement.progress / achievement.target, 1.0)
        else:
            percentage = 1.0 if achievement.unlocked else 0.0
        
        return AchievementProgress(
            achievement_id=achievement_id,
            current=achievement.progress,
            target=achievement.target,
            percentage=percentage,
        )
    
    def get_unlocked_achievements(self) -> List[Achievement]:
        """Get all unlocked achievements.
        
        Returns:
            List of unlocked Achievement objects
        """
        return [a for a in self._achievements.values() if a.unlocked]
    
    def get_locked_achievements(self) -> List[Achievement]:
        """Get all locked achievements.
        
        Returns:
            List of locked Achievement objects
        """
        return [a for a in self._achievements.values() if not a.unlocked]
    
    def get_achievement_by_id(self, achievement_id: str) -> Optional[Achievement]:
        """Get a specific achievement by ID.
        
        Args:
            achievement_id: ID of the achievement to retrieve
        
        Returns:
            Achievement if found, None otherwise
        """
        return self._achievements.get(achievement_id)
    
    def get_total_reward_currency(self) -> int:
        """Get total reward currency from all unlocked achievements.
        
        Returns:
            Total currency earned from achievements
        """
        return sum(a.reward_currency for a in self._achievements.values() if a.unlocked)
    
    def get_completion_percentage(self) -> float:
        """Get overall achievement completion percentage.
        
        Returns:
            Percentage of achievements unlocked (0.0 to 1.0)
        """
        total = len(self._achievements)
        if total == 0:
            return 0.0
        unlocked = len(self._unlocked_ids)
        return unlocked / total
    
    def reset_achievements(self) -> None:
        """Reset all achievements to locked state.
        
        This is primarily for testing purposes.
        """
        self._unlocked_ids.clear()
        for achievement in self._achievements.values():
            achievement.unlocked = False
            achievement.unlock_date = None
            achievement.progress = 0
        self._save_achievements_to_db()
