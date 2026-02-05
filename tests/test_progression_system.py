"""
Unit tests for ProgressionSystem.

Tests the ProgressionSystem class that manages unified progression
across all decks and themes.

Requirements: 2.1, 2.2, 2.3, 2.4, 2.5, 3.5
"""

import pytest
from datetime import datetime
from pathlib import Path
from unittest.mock import MagicMock

from core.progression_system import ProgressionSystem
from core.scoring_engine import ScoringEngine
from data.data_manager import DataManager
from data.models import (
    GameConfig,
    GameState,
    PowerUp,
    PowerUpType,
    ProgressionState,
    ReviewResult,
    Theme,
)


@pytest.fixture
def temp_db_path(tmp_path):
    """Create a temporary database path."""
    return tmp_path / "test_progression.db"


@pytest.fixture
def data_manager(temp_db_path):
    """Create a DataManager with initialized database."""
    dm = DataManager(temp_db_path)
    dm.initialize_database()
    return dm


@pytest.fixture
def config():
    """Create a default GameConfig."""
    return GameConfig()


@pytest.fixture
def scoring_engine(config):
    """Create a ScoringEngine with default config."""
    return ScoringEngine(config)


@pytest.fixture
def progression_system(data_manager, scoring_engine, config):
    """Create a ProgressionSystem with dependencies."""
    return ProgressionSystem(data_manager, scoring_engine, config)


def create_review_result(is_correct: bool, card_id: str = "1", deck_id: str = "1") -> ReviewResult:
    """Helper to create a ReviewResult."""
    now = datetime.now()
    return ReviewResult(
        card_id=card_id,
        deck_id=deck_id,
        is_correct=is_correct,
        ease=3 if is_correct else 1,
        timestamp=now,
        interval=1,
        next_review=now,
        repetitions=1,
        lapses=0,
        quality=3 if is_correct else 1
    )


class TestProgressionSystemInit:
    """Tests for ProgressionSystem initialization."""
    
    def test_init_with_empty_database(self, data_manager, scoring_engine, config):
        """Test initialization with an empty database."""
        ps = ProgressionSystem(data_manager, scoring_engine, config)
        
        state = ps.get_state()
        assert state.total_points == 0
        assert state.total_cards_reviewed == 0
        assert state.correct_answers == 0
        assert state.current_streak == 0
        assert state.levels_unlocked == 0
    
    def test_init_loads_existing_state(self, data_manager, scoring_engine, config):
        """Test that initialization loads existing state from database."""
        # First, save some state
        existing_state = ProgressionState(
            total_points=500,
            total_cards_reviewed=100,
            correct_answers=80,
            current_streak=5,
            best_streak=10,
            levels_unlocked=1
        )
        data_manager.save_progression(existing_state)
        
        # Create new ProgressionSystem - should load existing state
        ps = ProgressionSystem(data_manager, scoring_engine, config)
        
        state = ps.get_state()
        assert state.total_points == 500
        assert state.total_cards_reviewed == 100
        assert state.correct_answers == 80
        assert state.current_streak == 5
        assert state.best_streak == 10


class TestProcessReview:
    """Tests for process_review method."""
    
    def test_process_correct_answer_updates_points(self, progression_system):
        """Test that correct answer adds points. (Req 2.1, 2.2)"""
        result = create_review_result(is_correct=True)
        
        state = progression_system.process_review(result)
        
        # Base points is 10 by default
        assert state.total_points >= 10
    
    def test_process_correct_answer_updates_cards_reviewed(self, progression_system):
        """Test that correct answer increments cards reviewed. (Req 2.3)"""
        result = create_review_result(is_correct=True)
        
        state = progression_system.process_review(result)
        
        assert state.total_cards_reviewed == 1
    
    def test_process_correct_answer_updates_correct_answers(self, progression_system):
        """Test that correct answer increments correct_answers count."""
        result = create_review_result(is_correct=True)
        
        state = progression_system.process_review(result)
        
        assert state.correct_answers == 1
    
    def test_process_correct_answer_increments_streak(self, progression_system):
        """Test that correct answer increments streak."""
        result = create_review_result(is_correct=True)
        
        state = progression_system.process_review(result)
        
        assert state.current_streak == 1
        
        # Another correct answer
        state = progression_system.process_review(result)
        assert state.current_streak == 2
    
    def test_process_wrong_answer_resets_streak(self, progression_system):
        """Test that wrong answer resets streak to 0."""
        # Build up a streak
        correct = create_review_result(is_correct=True)
        progression_system.process_review(correct)
        progression_system.process_review(correct)
        progression_system.process_review(correct)
        
        state = progression_system.get_state()
        assert state.current_streak == 3
        
        # Wrong answer resets streak
        wrong = create_review_result(is_correct=False)
        state = progression_system.process_review(wrong)
        
        assert state.current_streak == 0
    
    def test_process_wrong_answer_updates_cards_reviewed(self, progression_system):
        """Test that wrong answer still increments cards reviewed. (Req 2.3)"""
        result = create_review_result(is_correct=False)
        
        state = progression_system.process_review(result)
        
        assert state.total_cards_reviewed == 1
    
    def test_process_wrong_answer_does_not_add_points(self, progression_system):
        """Test that wrong answer does not add points."""
        result = create_review_result(is_correct=False)
        
        state = progression_system.process_review(result)
        
        assert state.total_points == 0
    
    def test_process_wrong_answer_reduces_health(self, progression_system):
        """Test that wrong answer reduces session health."""
        # First reset session to get full health
        progression_system.reset_session()
        
        result = create_review_result(is_correct=False)
        
        state = progression_system.process_review(result)
        
        # Default penalty is 10% (10 points on 0-100 scale)
        assert state.session_health == 90
    
    def test_process_review_updates_session_accuracy(self, progression_system):
        """Test that session accuracy is updated correctly."""
        correct = create_review_result(is_correct=True)
        wrong = create_review_result(is_correct=False)
        
        # 2 correct, 1 wrong = 66.67% accuracy
        progression_system.process_review(correct)
        progression_system.process_review(correct)
        state = progression_system.process_review(wrong)
        
        assert abs(state.session_accuracy - (2/3)) < 0.01
    
    def test_process_review_updates_best_streak(self, progression_system):
        """Test that best_streak is updated when current streak exceeds it."""
        correct = create_review_result(is_correct=True)
        wrong = create_review_result(is_correct=False)
        
        # Build streak of 3
        for _ in range(3):
            progression_system.process_review(correct)
        
        state = progression_system.get_state()
        assert state.best_streak == 3
        
        # Break streak
        progression_system.process_review(wrong)
        
        # Build new streak of 2
        for _ in range(2):
            progression_system.process_review(correct)
        
        state = progression_system.get_state()
        # Best streak should still be 3
        assert state.best_streak == 3
        
        # Build streak to 4
        for _ in range(3):
            progression_system.process_review(correct)
        
        state = progression_system.get_state()
        # Best streak should now be 5
        assert state.best_streak == 5
    
    def test_process_review_persists_state(self, data_manager, scoring_engine, config):
        """Test that process_review persists state to database."""
        ps = ProgressionSystem(data_manager, scoring_engine, config)
        
        result = create_review_result(is_correct=True)
        ps.process_review(result)
        
        # Create new ProgressionSystem to load from database
        ps2 = ProgressionSystem(data_manager, scoring_engine, config)
        state = ps2.get_state()
        
        assert state.total_cards_reviewed == 1
        assert state.correct_answers == 1


class TestLevelUnlock:
    """Tests for level unlock functionality."""
    
    def test_levels_unlocked_after_50_correct(self, progression_system):
        """Test that 1 level is unlocked after 50 correct answers. (Req 2.4)"""
        correct = create_review_result(is_correct=True)
        
        # Process 50 correct answers
        for _ in range(50):
            state = progression_system.process_review(correct)
        
        assert state.levels_unlocked == 1
    
    def test_levels_unlocked_after_100_correct(self, progression_system):
        """Test that 2 levels are unlocked after 100 correct answers. (Req 2.4)"""
        correct = create_review_result(is_correct=True)
        
        # Process 100 correct answers
        for _ in range(100):
            state = progression_system.process_review(correct)
        
        assert state.levels_unlocked == 2
    
    def test_check_level_unlock_returns_level_number(self, progression_system):
        """Test that check_level_unlock returns the level number when unlocked."""
        correct = create_review_result(is_correct=True)
        
        # Process 49 correct answers - no unlock yet
        for _ in range(49):
            progression_system.process_review(correct)
        
        unlock = progression_system.check_level_unlock()
        assert unlock is None
        
        # 50th correct answer triggers unlock
        progression_system.process_review(correct)
        unlock = progression_system.check_level_unlock()
        
        assert unlock == 1
    
    def test_check_level_unlock_only_returns_once(self, progression_system):
        """Test that check_level_unlock only returns level once per threshold."""
        correct = create_review_result(is_correct=True)
        
        # Process 50 correct answers
        for _ in range(50):
            progression_system.process_review(correct)
        
        # First check returns level
        unlock = progression_system.check_level_unlock()
        assert unlock == 1
        
        # Second check returns None (already granted)
        unlock = progression_system.check_level_unlock()
        assert unlock is None
    
    def test_wrong_answers_dont_count_for_levels(self, progression_system):
        """Test that wrong answers don't count toward level unlocks."""
        correct = create_review_result(is_correct=True)
        wrong = create_review_result(is_correct=False)
        
        # Process 25 correct and 25 wrong
        for _ in range(25):
            progression_system.process_review(correct)
            progression_system.process_review(wrong)
        
        state = progression_system.get_state()
        # Only 25 correct answers, not enough for level unlock
        assert state.levels_unlocked == 0


class TestPowerUpGrant:
    """Tests for power-up grant functionality."""
    
    def test_powerup_granted_after_100_correct(self, progression_system):
        """Test that a power-up is granted after 100 correct answers. (Req 2.5)"""
        correct = create_review_result(is_correct=True)
        
        # Process 99 correct answers - no powerup yet
        for _ in range(99):
            progression_system.process_review(correct)
        
        powerup = progression_system.check_powerup_grant()
        assert powerup is None
        
        # 100th correct answer triggers powerup
        progression_system.process_review(correct)
        powerup = progression_system.check_powerup_grant()
        
        assert powerup is not None
        assert isinstance(powerup, PowerUp)
    
    def test_powerup_is_theme_appropriate(self, progression_system):
        """Test that granted power-up matches current theme."""
        correct = create_review_result(is_correct=True)
        
        # Set theme to Zelda
        progression_system.set_current_theme(Theme.ZELDA)
        
        # Process 100 correct answers
        for _ in range(100):
            progression_system.process_review(correct)
        
        powerup = progression_system.check_powerup_grant()
        
        assert powerup is not None
        assert powerup.theme == Theme.ZELDA
        assert powerup.type in [
            PowerUpType.HEART_CONTAINER,
            PowerUpType.FAIRY,
            PowerUpType.POTION
        ]
    
    def test_check_powerup_grant_only_returns_once(self, progression_system):
        """Test that check_powerup_grant only returns powerup once per threshold."""
        correct = create_review_result(is_correct=True)
        
        # Process 100 correct answers
        for _ in range(100):
            progression_system.process_review(correct)
        
        # First check returns powerup
        powerup = progression_system.check_powerup_grant()
        assert powerup is not None
        
        # Second check returns None (already granted)
        powerup = progression_system.check_powerup_grant()
        assert powerup is None
    
    def test_multiple_powerups_granted(self, progression_system):
        """Test that multiple power-ups are granted at correct intervals."""
        correct = create_review_result(is_correct=True)
        powerups_granted = 0
        
        # Process 250 correct answers
        for i in range(250):
            progression_system.process_review(correct)
            powerup = progression_system.check_powerup_grant()
            if powerup is not None:
                powerups_granted += 1
        
        # Should have granted 2 power-ups (at 100 and 200)
        assert powerups_granted == 2


class TestResetSession:
    """Tests for reset_session method."""
    
    def test_reset_session_restores_health(self, progression_system):
        """Test that reset_session restores health to full. (Req 3.5)"""
        # First reset to get full health
        progression_system.reset_session()
        
        wrong = create_review_result(is_correct=False)
        
        # Reduce health with wrong answers
        for _ in range(5):
            progression_system.process_review(wrong)
        
        state = progression_system.get_state()
        assert state.session_health < 100
        
        # Reset session
        progression_system.reset_session()
        
        state = progression_system.get_state()
        assert state.session_health == 100
    
    def test_reset_session_restores_accuracy(self, progression_system):
        """Test that reset_session restores session accuracy."""
        wrong = create_review_result(is_correct=False)
        
        # Reduce accuracy with wrong answers
        for _ in range(5):
            progression_system.process_review(wrong)
        
        state = progression_system.get_state()
        assert state.session_accuracy == 0.0
        
        # Reset session
        progression_system.reset_session()
        
        state = progression_system.get_state()
        assert state.session_accuracy == 1.0
    
    def test_reset_session_preserves_total_progress(self, progression_system):
        """Test that reset_session preserves total progress."""
        correct = create_review_result(is_correct=True)
        
        # Build up some progress
        for _ in range(10):
            progression_system.process_review(correct)
        
        state = progression_system.get_state()
        total_points = state.total_points
        total_reviewed = state.total_cards_reviewed
        correct_answers = state.correct_answers
        
        # Reset session
        progression_system.reset_session()
        
        state = progression_system.get_state()
        # Total progress should be preserved
        assert state.total_points == total_points
        assert state.total_cards_reviewed == total_reviewed
        assert state.correct_answers == correct_answers


class TestComboMultiplier:
    """Tests for combo multiplier integration."""
    
    def test_streak_5_applies_multiplier(self, progression_system):
        """Test that streak of 5+ applies 1.5x multiplier."""
        correct = create_review_result(is_correct=True)
        
        # Build streak to 4 (no multiplier yet)
        for _ in range(4):
            progression_system.process_review(correct)
        
        state = progression_system.get_state()
        points_at_4 = state.total_points
        
        # 5th correct answer should get 1.5x multiplier
        progression_system.process_review(correct)
        
        state = progression_system.get_state()
        points_gained = state.total_points - points_at_4
        
        # Should be 15 points (10 * 1.5) + accuracy bonus (25% of 15 = 3.75 -> 3)
        # With 100% accuracy, we get: 15 + 3 = 18 points
        # Base calculation: 10 * 1.5 = 15, bonus = int(15 * 0.25) = 3, total = 18
        assert points_gained == 18
    
    def test_streak_10_applies_multiplier(self, progression_system):
        """Test that streak of 10+ applies 2.0x multiplier."""
        correct = create_review_result(is_correct=True)
        
        # Build streak to 9
        for _ in range(9):
            progression_system.process_review(correct)
        
        state = progression_system.get_state()
        points_at_9 = state.total_points
        
        # 10th correct answer should get 2.0x multiplier
        progression_system.process_review(correct)
        
        state = progression_system.get_state()
        points_gained = state.total_points - points_at_9
        
        # Should be 20 points (10 * 2.0) + accuracy bonus (25% of 20 = 5)
        # With 100% accuracy, we get: 20 + 5 = 25 points
        assert points_gained == 25


class TestHealthReduction:
    """Tests for health reduction on wrong answers."""
    
    def test_health_reduces_by_10_percent(self, progression_system):
        """Test that health reduces by 10% per wrong answer."""
        # First reset session to get full health
        progression_system.reset_session()
        
        wrong = create_review_result(is_correct=False)
        
        state = progression_system.process_review(wrong)
        assert state.session_health == 90
        
        state = progression_system.process_review(wrong)
        assert state.session_health == 80
    
    def test_health_does_not_go_below_zero(self, progression_system):
        """Test that health cannot go below 0."""
        # First reset session to get full health
        progression_system.reset_session()
        
        wrong = create_review_result(is_correct=False)
        
        # 15 wrong answers would be -50 health without clamping
        for _ in range(15):
            state = progression_system.process_review(wrong)
        
        assert state.session_health >= 0
