"""
Unit tests for ScoringEngine.

Tests the scoring logic including base points, combo multipliers,
accuracy bonuses, and penalties.

Requirements: 3.1, 3.2, 3.3, 3.4
"""

import pytest
from core.scoring_engine import ScoringEngine
from data.models import GameConfig, ScoreResult, PenaltyResult


class TestScoringEngineInit:
    """Tests for ScoringEngine initialization."""
    
    def test_init_with_default_config(self):
        """Test initialization with default GameConfig."""
        config = GameConfig()
        engine = ScoringEngine(config)
        
        assert engine.config == config
        assert engine.config.base_points == 10
    
    def test_init_with_custom_config(self):
        """Test initialization with custom GameConfig."""
        config = GameConfig(base_points=20, penalty_currency_loss=5)
        engine = ScoringEngine(config)
        
        assert engine.config.base_points == 20
        assert engine.config.penalty_currency_loss == 5


class TestGetComboMultiplier:
    """Tests for get_combo_multiplier method.
    
    Validates: Requirement 3.3 - Combo multiplier tiers
    """
    
    @pytest.fixture
    def engine(self):
        """Create a ScoringEngine with default config."""
        return ScoringEngine(GameConfig())
    
    def test_no_multiplier_for_streak_0(self, engine):
        """Streak of 0 should have 1.0x multiplier."""
        assert engine.get_combo_multiplier(0) == 1.0
    
    def test_no_multiplier_for_streak_1_to_4(self, engine):
        """Streaks 1-4 should have 1.0x multiplier."""
        for streak in range(1, 5):
            assert engine.get_combo_multiplier(streak) == 1.0
    
    def test_multiplier_1_5x_for_streak_5(self, engine):
        """Streak of 5 should have 1.5x multiplier."""
        assert engine.get_combo_multiplier(5) == 1.5
    
    def test_multiplier_1_5x_for_streak_5_to_9(self, engine):
        """Streaks 5-9 should have 1.5x multiplier."""
        for streak in range(5, 10):
            assert engine.get_combo_multiplier(streak) == 1.5
    
    def test_multiplier_2x_for_streak_10(self, engine):
        """Streak of 10 should have 2.0x multiplier."""
        assert engine.get_combo_multiplier(10) == 2.0
    
    def test_multiplier_2x_for_streak_10_to_19(self, engine):
        """Streaks 10-19 should have 2.0x multiplier."""
        for streak in range(10, 20):
            assert engine.get_combo_multiplier(streak) == 2.0
    
    def test_multiplier_3x_for_streak_20(self, engine):
        """Streak of 20 should have 3.0x multiplier."""
        assert engine.get_combo_multiplier(20) == 3.0
    
    def test_multiplier_3x_for_streak_above_20(self, engine):
        """Streaks above 20 should have 3.0x multiplier."""
        assert engine.get_combo_multiplier(25) == 3.0
        assert engine.get_combo_multiplier(50) == 3.0
        assert engine.get_combo_multiplier(100) == 3.0
    
    def test_custom_multiplier_values(self):
        """Test with custom multiplier values in config."""
        config = GameConfig(
            streak_multiplier_5=2.0,
            streak_multiplier_10=3.0,
            streak_multiplier_20=5.0
        )
        engine = ScoringEngine(config)
        
        assert engine.get_combo_multiplier(5) == 2.0
        assert engine.get_combo_multiplier(10) == 3.0
        assert engine.get_combo_multiplier(20) == 5.0


class TestCalculateScore:
    """Tests for calculate_score method.
    
    Validates: Requirements 3.1, 3.3, 3.4
    """
    
    @pytest.fixture
    def engine(self):
        """Create a ScoringEngine with default config."""
        return ScoringEngine(GameConfig())
    
    def test_correct_answer_base_points(self, engine):
        """Correct answer with no streak should award base points."""
        result = engine.calculate_score(
            is_correct=True,
            current_streak=0,
            session_accuracy=0.5
        )
        
        assert result.base_points == 10
        assert result.multiplier == 1.0
        assert result.bonus_points == 0
        assert result.total_points == 10
        assert result.streak_broken is False
    
    def test_wrong_answer_no_points(self, engine):
        """Wrong answer should award no points and break streak."""
        result = engine.calculate_score(
            is_correct=False,
            current_streak=10,
            session_accuracy=0.95
        )
        
        assert result.base_points == 0
        assert result.multiplier == 1.0
        assert result.bonus_points == 0
        assert result.total_points == 0
        assert result.streak_broken is True
    
    def test_correct_answer_with_streak_5(self, engine):
        """Correct answer reaching streak 5 should get 1.5x multiplier."""
        # current_streak=4 means after this answer, streak will be 5
        result = engine.calculate_score(
            is_correct=True,
            current_streak=4,
            session_accuracy=0.5
        )
        
        assert result.base_points == 10
        assert result.multiplier == 1.5
        assert result.total_points == 15  # 10 * 1.5 = 15
        assert result.streak_broken is False
    
    def test_correct_answer_with_streak_10(self, engine):
        """Correct answer reaching streak 10 should get 2.0x multiplier."""
        result = engine.calculate_score(
            is_correct=True,
            current_streak=9,
            session_accuracy=0.5
        )
        
        assert result.base_points == 10
        assert result.multiplier == 2.0
        assert result.total_points == 20  # 10 * 2.0 = 20
    
    def test_correct_answer_with_streak_20(self, engine):
        """Correct answer reaching streak 20 should get 3.0x multiplier."""
        result = engine.calculate_score(
            is_correct=True,
            current_streak=19,
            session_accuracy=0.5
        )
        
        assert result.base_points == 10
        assert result.multiplier == 3.0
        assert result.total_points == 30  # 10 * 3.0 = 30
    
    def test_accuracy_bonus_at_90_percent(self, engine):
        """Session accuracy of 90% should trigger accuracy bonus."""
        result = engine.calculate_score(
            is_correct=True,
            current_streak=0,
            session_accuracy=0.9
        )
        
        assert result.base_points == 10
        assert result.bonus_points == 2  # 10 * 0.25 = 2.5 -> 2
        assert result.total_points == 12  # 10 + 2 = 12
    
    def test_accuracy_bonus_at_95_percent(self, engine):
        """Session accuracy of 95% should trigger accuracy bonus."""
        result = engine.calculate_score(
            is_correct=True,
            current_streak=0,
            session_accuracy=0.95
        )
        
        assert result.bonus_points == 2  # 10 * 0.25 = 2.5 -> 2
        assert result.total_points == 12
    
    def test_no_accuracy_bonus_below_90_percent(self, engine):
        """Session accuracy below 90% should not trigger bonus."""
        result = engine.calculate_score(
            is_correct=True,
            current_streak=0,
            session_accuracy=0.89
        )
        
        assert result.bonus_points == 0
        assert result.total_points == 10
    
    def test_combined_multiplier_and_accuracy_bonus(self, engine):
        """Test combo multiplier combined with accuracy bonus."""
        result = engine.calculate_score(
            is_correct=True,
            current_streak=9,  # Will become streak 10 -> 2.0x
            session_accuracy=0.95
        )
        
        # base_points = 10
        # multiplied_points = 10 * 2.0 = 20
        # bonus_points = 20 * 0.25 = 5
        # total = 20 + 5 = 25
        assert result.base_points == 10
        assert result.multiplier == 2.0
        assert result.bonus_points == 5
        assert result.total_points == 25
    
    def test_custom_base_points(self):
        """Test with custom base points."""
        config = GameConfig(base_points=20)
        engine = ScoringEngine(config)
        
        result = engine.calculate_score(
            is_correct=True,
            current_streak=0,
            session_accuracy=0.5
        )
        
        assert result.base_points == 20
        assert result.total_points == 20
    
    def test_custom_accuracy_threshold(self):
        """Test with custom accuracy bonus threshold."""
        config = GameConfig(accuracy_bonus_threshold=0.8)
        engine = ScoringEngine(config)
        
        # 85% accuracy should now trigger bonus
        result = engine.calculate_score(
            is_correct=True,
            current_streak=0,
            session_accuracy=0.85
        )
        
        assert result.bonus_points == 2  # 10 * 0.25 = 2.5 -> 2


class TestCalculatePenalty:
    """Tests for calculate_penalty method.
    
    Validates: Requirement 3.2 - Penalties for wrong answers
    """
    
    @pytest.fixture
    def engine(self):
        """Create a ScoringEngine with default config."""
        return ScoringEngine(GameConfig())
    
    def test_default_penalty_values(self, engine):
        """Test default penalty values."""
        result = engine.calculate_penalty(current_health=1.0)
        
        assert result.health_reduction == 0.1  # 10% health reduction
        assert result.currency_lost == 1  # 1 coin lost
    
    def test_penalty_with_low_health(self, engine):
        """Penalty calculation doesn't depend on current health."""
        result = engine.calculate_penalty(current_health=0.2)
        
        # Penalty is always the same regardless of current health
        assert result.health_reduction == 0.1
        assert result.currency_lost == 1
    
    def test_custom_penalty_values(self):
        """Test with custom penalty values."""
        config = GameConfig(
            penalty_health_reduction=0.2,
            penalty_currency_loss=5
        )
        engine = ScoringEngine(config)
        
        result = engine.calculate_penalty(current_health=1.0)
        
        assert result.health_reduction == 0.2  # 20% health reduction
        assert result.currency_lost == 5  # 5 coins lost
    
    def test_penalty_streak_lost_is_zero(self, engine):
        """Streak lost is set to 0 (caller should set actual value)."""
        result = engine.calculate_penalty(current_health=1.0)
        
        # The streak_lost field is 0 because the engine doesn't track streak
        # The caller (ProgressionSystem) should set the actual streak value
        assert result.streak_lost == 0


class TestScoringEngineEdgeCases:
    """Edge case tests for ScoringEngine."""
    
    @pytest.fixture
    def engine(self):
        """Create a ScoringEngine with default config."""
        return ScoringEngine(GameConfig())
    
    def test_very_high_streak(self, engine):
        """Test with very high streak value."""
        result = engine.calculate_score(
            is_correct=True,
            current_streak=999,
            session_accuracy=0.5
        )
        
        # Should still use 3.0x multiplier
        assert result.multiplier == 3.0
        assert result.total_points == 30
    
    def test_perfect_accuracy(self, engine):
        """Test with 100% session accuracy."""
        result = engine.calculate_score(
            is_correct=True,
            current_streak=0,
            session_accuracy=1.0
        )
        
        assert result.bonus_points == 2
        assert result.total_points == 12
    
    def test_zero_accuracy(self, engine):
        """Test with 0% session accuracy."""
        result = engine.calculate_score(
            is_correct=True,
            current_streak=0,
            session_accuracy=0.0
        )
        
        assert result.bonus_points == 0
        assert result.total_points == 10
    
    def test_negative_streak_treated_as_zero(self, engine):
        """Negative streak should be treated as no streak."""
        # This shouldn't happen in practice, but test defensive behavior
        result = engine.get_combo_multiplier(-1)
        assert result == 1.0
