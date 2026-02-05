"""
ProgressionSystem for NintendAnki.

This module implements the ProgressionSystem class that manages unified
progression across all decks and themes, including points, levels, and power-ups.

Requirements: 2.1, 2.2, 2.3, 2.4, 2.5, 3.5
"""

from datetime import datetime
from typing import Optional
import uuid

from data.data_manager import DataManager
from data.models import (
    GameConfig,
    PowerUp,
    PowerUpType,
    ProgressionState,
    ReviewResult,
    Theme,
)
from core.scoring_engine import ScoringEngine


class ProgressionSystem:
    """Manages unified progression across all decks and themes.
    
    The ProgressionSystem is responsible for:
    - Processing card reviews and updating progression state
    - Tracking total points, cards reviewed, and correct answers
    - Managing level unlocks (1 per 50 correct answers)
    - Managing power-up grants (1 per 100 correct answers)
    - Resetting session-specific state (health, session accuracy)
    
    Attributes:
        data_manager: DataManager for persisting progression state
        scoring_engine: ScoringEngine for calculating scores
        config: GameConfig containing progression parameters
        _state: Current progression state
        _session_correct: Correct answers in current session (for accuracy)
        _session_total: Total reviews in current session (for accuracy)
        _last_level_unlock_threshold: Last threshold at which a level was unlocked
        _last_powerup_grant_threshold: Last threshold at which a power-up was granted
    """
    
    # Power-up definitions for each theme
    THEME_POWERUPS = {
        Theme.MARIO: [
            (PowerUpType.MUSHROOM, "Mushroom", "Grants an extra life"),
            (PowerUpType.FIRE_FLOWER, "Fire Flower", "Shoot fireballs at enemies"),
            (PowerUpType.STAR, "Star", "Temporary invincibility"),
        ],
        Theme.ZELDA: [
            (PowerUpType.HEART_CONTAINER, "Heart Container", "Increases max health"),
            (PowerUpType.FAIRY, "Fairy", "Revives you when health reaches zero"),
            (PowerUpType.POTION, "Potion", "Restores health"),
        ],
        Theme.DKC: [
            (PowerUpType.GOLDEN_BANANA, "Golden Banana", "Bonus bananas"),
            (PowerUpType.BARREL, "Barrel", "Launch to new areas"),
            (PowerUpType.ANIMAL_BUDDY, "Animal Buddy", "Summon a helper animal"),
        ],
    }
    
    def __init__(self, data_manager: DataManager, scoring_engine: ScoringEngine, 
                 config: Optional[GameConfig] = None):
        """Initialize the ProgressionSystem.
        
        Args:
            data_manager: DataManager for persisting progression state
            scoring_engine: ScoringEngine for calculating scores
            config: Optional GameConfig for progression parameters (uses defaults if None)
        """
        self.data_manager = data_manager
        self.scoring_engine = scoring_engine
        self.config = config or GameConfig()
        
        # Load initial state from database
        game_state = self.data_manager.load_state()
        self._state = game_state.progression
        self._current_theme = game_state.theme
        
        # Session tracking for accuracy calculation
        self._session_correct = 0
        self._session_total = 0
        
        # Track thresholds for level/powerup grants to avoid duplicate grants
        self._last_level_unlock_threshold = (
            self._state.correct_answers // self.config.cards_per_level
        ) * self.config.cards_per_level
        self._last_powerup_grant_threshold = (
            self._state.correct_answers // self.config.cards_per_powerup
        ) * self.config.cards_per_powerup
    
    def process_review(self, result: ReviewResult) -> ProgressionState:
        """Process a card review and update progression.
        
        This method:
        1. Updates total cards reviewed count
        2. Updates correct answers count (if correct)
        3. Calculates and adds points using the scoring engine
        4. Updates streak (increment on correct, reset on wrong)
        5. Updates session accuracy
        6. Updates session health (reduce on wrong answer)
        7. Updates levels_unlocked based on correct answers
        8. Persists the updated state
        
        Args:
            result: ReviewResult containing the review details
            
        Returns:
            Updated ProgressionState
            
        Requirements: 2.1, 2.2, 2.3
        """
        # Update total cards reviewed
        self._state.total_cards_reviewed += 1
        self._session_total += 1
        
        if result.is_correct:
            # Update correct answers count
            self._state.correct_answers += 1
            self._session_correct += 1
            
            # Calculate score using scoring engine
            score_result = self.scoring_engine.calculate_score(
                is_correct=True,
                current_streak=self._state.current_streak,
                session_accuracy=self._state.session_accuracy
            )
            
            # Update total points
            self._state.total_points += score_result.total_points
            
            # Update streak
            self._state.current_streak += 1
            if self._state.current_streak > self._state.best_streak:
                self._state.best_streak = self._state.current_streak
        else:
            # Wrong answer - calculate penalty
            penalty_result = self.scoring_engine.calculate_penalty(
                current_health=self._state.session_health / 100.0  # Convert to float for scoring engine
            )
            
            # Reset streak
            self._state.current_streak = 0
            
            # Reduce session health (convert health_reduction from float to int percentage)
            health_reduction_int = int(penalty_result.health_reduction * 100)
            self._state.session_health = max(
                0, 
                self._state.session_health - health_reduction_int
            )
        
        # Update session accuracy
        if self._session_total > 0:
            self._state.session_accuracy = self._session_correct / self._session_total
        
        # Update levels_unlocked based on correct answers
        # One level per cards_per_level (default 50) correct answers
        self._state.levels_unlocked = (
            self._state.correct_answers // self.config.cards_per_level
        )
        
        # Persist the updated state
        self.data_manager.save_progression(self._state)
        
        return self._state
    
    def get_state(self) -> ProgressionState:
        """Get current progression state.
        
        Returns:
            Current ProgressionState
        """
        return self._state
    
    def check_level_unlock(self) -> Optional[int]:
        """Check if a new level should be unlocked.
        
        A new level is unlocked every cards_per_level (default 50) correct answers.
        This method checks if the current correct_answers count has crossed
        a new threshold since the last check.
        
        Returns:
            Level number if unlocked, None otherwise
            
        Requirements: 2.4
        """
        current_threshold = (
            self._state.correct_answers // self.config.cards_per_level
        ) * self.config.cards_per_level
        
        if current_threshold > self._last_level_unlock_threshold:
            # A new level should be unlocked
            self._last_level_unlock_threshold = current_threshold
            # Return the level number (1-indexed)
            level_number = self._state.correct_answers // self.config.cards_per_level
            return level_number
        
        return None
    
    def check_powerup_grant(self) -> Optional[PowerUp]:
        """Check if a power-up should be granted.
        
        A power-up is granted every cards_per_powerup (default 100) correct answers.
        This method checks if the current correct_answers count has crossed
        a new threshold since the last check.
        
        Returns:
            PowerUp if granted, None otherwise
            
        Requirements: 2.5
        """
        current_threshold = (
            self._state.correct_answers // self.config.cards_per_powerup
        ) * self.config.cards_per_powerup
        
        if current_threshold > self._last_powerup_grant_threshold:
            # A new power-up should be granted
            self._last_powerup_grant_threshold = current_threshold
            
            # Create a theme-appropriate power-up
            powerup = self._create_powerup_for_theme(self._current_theme)
            return powerup
        
        return None
    
    def reset_session(self) -> None:
        """Reset session-specific state (health, session accuracy).
        
        This method resets:
        - Session health to full (100)
        - Session accuracy to 1.0 (100%)
        - Session tracking counters
        
        Note: This does NOT reset the current streak, as streaks persist
        across sessions according to the design.
        
        Requirements: 3.5
        """
        self._state.session_health = 100
        self._state.session_accuracy = 1.0
        self._session_correct = 0
        self._session_total = 0
    
    def set_current_theme(self, theme: Theme) -> None:
        """Set the current theme for power-up grants.
        
        Args:
            theme: The theme to set as current
        """
        self._current_theme = theme
    
    def _create_powerup_for_theme(self, theme: Theme) -> PowerUp:
        """Create a power-up appropriate for the given theme.
        
        Cycles through available power-ups for the theme based on
        how many power-ups have been granted.
        
        Args:
            theme: The theme to create a power-up for
            
        Returns:
            A new PowerUp instance
        """
        theme_powerups = self.THEME_POWERUPS.get(theme, self.THEME_POWERUPS[Theme.MARIO])
        
        # Cycle through power-ups based on grant count
        powerup_count = self._state.correct_answers // self.config.cards_per_powerup
        powerup_index = (powerup_count - 1) % len(theme_powerups)
        
        powerup_type, name, description = theme_powerups[powerup_index]
        
        return PowerUp(
            id=f"powerup_{uuid.uuid4().hex[:8]}",
            type=powerup_type,
            theme=theme,
            name=name,
            description=description,
            icon=f"assets/{theme.value}/{powerup_type.value}.png",
            quantity=1,
            duration_seconds=0,  # Instant/permanent power-ups by default
            acquired_at=datetime.now()
        )
