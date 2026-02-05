"""
Scoring Engine for NintendAnki.

This module implements the ScoringEngine class that calculates scores,
streaks, and multipliers for card reviews.

Requirements: 3.1, 3.2, 3.3, 3.4
"""

from data.models import GameConfig, ScoreResult, PenaltyResult


class ScoringEngine:
    """Calculates scores, streaks, and multipliers.
    
    The ScoringEngine is responsible for:
    - Calculating base points for correct answers
    - Applying combo multipliers based on streak length
    - Applying accuracy bonuses for high session accuracy
    - Calculating penalties for wrong answers
    
    Attributes:
        config: GameConfig containing scoring parameters
    """
    
    def __init__(self, config: GameConfig):
        """Initialize the ScoringEngine with configuration.
        
        Args:
            config: GameConfig containing scoring parameters like base_points,
                   streak multipliers, accuracy bonus settings, and penalty values.
        """
        self.config = config
    
    def calculate_score(self, is_correct: bool, current_streak: int, 
                        session_accuracy: float) -> ScoreResult:
        """Calculate score for a review.
        
        For correct answers:
        - Awards base points (configurable, default 10)
        - Applies combo multiplier based on streak (1.0/1.5/2.0/3.0)
        - Applies accuracy bonus (25% extra) if session accuracy >= 90%
        
        For wrong answers:
        - Returns 0 points with streak_broken=True
        
        Args:
            is_correct: Whether the answer was correct
            current_streak: Current streak count (before this review)
            session_accuracy: Current session accuracy (0.0 to 1.0)
            
        Returns:
            ScoreResult with points earned and multipliers applied
        """
        if not is_correct:
            # Wrong answer: no points, streak is broken
            return ScoreResult(
                base_points=0,
                multiplier=1.0,
                bonus_points=0,
                total_points=0,
                streak_broken=True
            )
        
        # Correct answer: calculate points
        base_points = self.config.base_points
        
        # Get combo multiplier based on current streak
        # Note: current_streak is the streak BEFORE this answer
        # After this correct answer, streak will be current_streak + 1
        # The multiplier is based on the new streak value
        new_streak = current_streak + 1
        multiplier = self.get_combo_multiplier(new_streak)
        
        # Calculate points with multiplier
        multiplied_points = int(base_points * multiplier)
        
        # Calculate accuracy bonus if applicable
        bonus_points = 0
        if session_accuracy >= self.config.accuracy_bonus_threshold:
            # Apply accuracy bonus multiplier (25% extra points)
            bonus_points = int(multiplied_points * (self.config.accuracy_bonus_multiplier - 1.0))
        
        total_points = multiplied_points + bonus_points
        
        return ScoreResult(
            base_points=base_points,
            multiplier=multiplier,
            bonus_points=bonus_points,
            total_points=total_points,
            streak_broken=False
        )
    
    def get_combo_multiplier(self, streak: int) -> float:
        """Get combo multiplier for current streak.
        
        The combo multiplier increases with longer streaks to reward
        consistent correct answers:
        - 1.0x for streak < 5 (no bonus)
        - 1.5x for streak 5-9
        - 2.0x for streak 10-19
        - 3.0x for streak 20+
        
        Args:
            streak: Current streak count
            
        Returns:
            The multiplier to apply to base points (1.0, 1.5, 2.0, or 3.0)
        """
        if streak >= 20:
            return self.config.streak_multiplier_20
        elif streak >= 10:
            return self.config.streak_multiplier_10
        elif streak >= 5:
            return self.config.streak_multiplier_5
        else:
            return 1.0
    
    def calculate_penalty(self, current_health: float) -> PenaltyResult:
        """Calculate penalty for wrong answer.
        
        Wrong answers result in:
        - Health reduction (default 10% of max health)
        - Currency loss (default 1 coin)
        - Streak reset to 0
        
        Args:
            current_health: Current health value (0.0 to 1.0)
            
        Returns:
            PenaltyResult with health reduction and currency loss
        """
        # Health reduction is a fixed percentage (default 10%)
        health_reduction = self.config.penalty_health_reduction
        
        # Currency loss is a fixed amount (default 1)
        currency_lost = self.config.penalty_currency_loss
        
        # Streak is always lost on wrong answer
        # We don't know the actual streak here, so we indicate it's lost
        # The caller should track the actual streak value
        streak_lost = 0  # This will be set by the caller based on actual streak
        
        return PenaltyResult(
            health_reduction=health_reduction,
            currency_lost=currency_lost,
            streak_lost=streak_lost
        )
