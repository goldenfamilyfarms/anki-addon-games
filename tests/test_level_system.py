"""
Unit tests for LevelSystem.

Tests level unlocking, completion, rewards, and progress tracking
across all themes.

Requirements: 15.1, 15.2, 15.3, 15.4, 15.5, 15.6, 15.7
"""

import pytest
from datetime import datetime
from pathlib import Path
import tempfile
import os

from core.level_system import (
    LevelSystem,
    MARIO_LEVELS,
    ZELDA_LEVELS,
    DKC_LEVELS,
    BASE_LEVEL_REWARD,
    THEME_LEVELS,
)
from data.data_manager import DataManager
from data.models import (
    Level,
    LevelProgress,
    LevelReward,
    PowerUpType,
    Theme,
)


@pytest.fixture
def temp_db_path():
    """Create a temporary database path for testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir) / "test_game.db"


@pytest.fixture
def data_manager(temp_db_path):
    """Create a DataManager with a temporary database."""
    dm = DataManager(temp_db_path)
    dm.initialize_database()
    yield dm
    dm.close()  # Close connection before cleanup


@pytest.fixture
def level_system(data_manager):
    """Create a LevelSystem instance for testing."""
    return LevelSystem(data_manager)


class TestLevelSystemInitialization:
    """Tests for LevelSystem initialization."""
    
    def test_initialization_creates_levels(self, level_system):
        """Test that initialization creates all level definitions."""
        # Check that levels exist for all themes
        for theme in Theme:
            levels = level_system.get_all_levels(theme)
            assert len(levels) > 0, f"No levels created for {theme}"
    
    def test_mario_levels_count(self, level_system):
        """Test that Mario theme has correct number of levels."""
        levels = level_system.get_all_levels(Theme.MARIO)
        assert len(levels) == len(MARIO_LEVELS)
    
    def test_zelda_levels_count(self, level_system):
        """Test that Zelda theme has correct number of levels."""
        levels = level_system.get_all_levels(Theme.ZELDA)
        assert len(levels) == len(ZELDA_LEVELS)
    
    def test_dkc_levels_count(self, level_system):
        """Test that DKC theme has correct number of levels."""
        levels = level_system.get_all_levels(Theme.DKC)
        assert len(levels) == len(DKC_LEVELS)
    
    def test_first_level_unlocked_by_default(self, level_system):
        """Test that the first level of each theme is unlocked by default."""
        for theme in Theme:
            levels = level_system.get_all_levels(theme)
            assert levels[0].unlocked, f"First level of {theme} should be unlocked"
    
    def test_subsequent_levels_locked_by_default(self, level_system):
        """Test that levels after the first are locked by default."""
        for theme in Theme:
            levels = level_system.get_all_levels(theme)
            if len(levels) > 1:
                assert not levels[1].unlocked, f"Second level of {theme} should be locked"


class TestUnlockLevel:
    """Tests for unlock_level() method.
    
    Requirements: 15.1, 15.2, 15.4
    """
    
    def test_unlock_next_level(self, level_system):
        """Test unlocking the next level for a theme."""
        # Get initial state
        initial_unlocked = len(level_system.get_available_levels(Theme.MARIO))
        
        # Unlock next level
        unlocked = level_system.unlock_level(Theme.MARIO)
        
        assert unlocked is not None
        assert unlocked.unlocked
        assert len(level_system.get_available_levels(Theme.MARIO)) == initial_unlocked + 1
    
    def test_unlock_returns_correct_level(self, level_system):
        """Test that unlock_level returns the correct next level."""
        # First unlock should be level 2 (level 1 is already unlocked)
        unlocked = level_system.unlock_level(Theme.MARIO)
        
        assert unlocked is not None
        assert unlocked.level_number == 2
    
    def test_unlock_multiple_levels_sequentially(self, level_system):
        """Test unlocking multiple levels in sequence."""
        for expected_level in range(2, 6):  # Unlock levels 2-5
            unlocked = level_system.unlock_level(Theme.ZELDA)
            assert unlocked is not None
            assert unlocked.level_number == expected_level
    
    def test_unlock_all_levels_returns_none(self, level_system):
        """Test that unlock_level returns None when all levels are unlocked."""
        # Unlock all levels
        level_system.unlock_all_levels(Theme.DKC)
        
        # Try to unlock another
        result = level_system.unlock_level(Theme.DKC)
        
        assert result is None
    
    def test_unlock_persists_to_database(self, level_system, data_manager):
        """Test that unlocked levels are persisted to the database."""
        # Unlock a level
        unlocked = level_system.unlock_level(Theme.MARIO)
        level_id = unlocked.id
        
        # Create a new LevelSystem instance to verify persistence
        new_level_system = LevelSystem(data_manager)
        level = new_level_system.get_level(level_id)
        
        assert level is not None
        assert level.unlocked


class TestCompleteLevel:
    """Tests for complete_level() method.
    
    Requirements: 15.2, 15.5, 15.6
    """
    
    def test_complete_level_basic(self, level_system):
        """Test basic level completion."""
        # Get first level (already unlocked)
        levels = level_system.get_all_levels(Theme.MARIO)
        level_id = levels[0].id
        
        # Complete the level
        reward = level_system.complete_level(level_id, 0.85)
        
        assert reward is not None
        assert reward.level_id == level_id
        assert reward.currency_earned >= BASE_LEVEL_REWARD
    
    def test_complete_level_marks_as_completed(self, level_system):
        """Test that completing a level marks it as completed."""
        levels = level_system.get_all_levels(Theme.MARIO)
        level_id = levels[0].id
        
        level_system.complete_level(level_id, 0.90)
        
        level = level_system.get_level(level_id)
        assert level.completed
    
    def test_complete_level_sets_completion_date(self, level_system):
        """Test that completing a level sets the completion date."""
        levels = level_system.get_all_levels(Theme.MARIO)
        level_id = levels[0].id
        
        before = datetime.now()
        level_system.complete_level(level_id, 0.90)
        after = datetime.now()
        
        level = level_system.get_level(level_id)
        assert level.completion_date is not None
        assert before <= level.completion_date <= after
    
    def test_complete_level_updates_best_accuracy(self, level_system):
        """Test that completing a level updates best accuracy."""
        levels = level_system.get_all_levels(Theme.MARIO)
        level_id = levels[0].id
        
        level_system.complete_level(level_id, 0.85)
        level = level_system.get_level(level_id)
        assert level.best_accuracy == 0.85
        
        # Complete again with better accuracy
        level_system.complete_level(level_id, 0.95)
        level = level_system.get_level(level_id)
        assert level.best_accuracy == 0.95
    
    def test_complete_level_keeps_best_accuracy(self, level_system):
        """Test that lower accuracy doesn't overwrite best accuracy."""
        levels = level_system.get_all_levels(Theme.MARIO)
        level_id = levels[0].id
        
        level_system.complete_level(level_id, 0.95)
        level_system.complete_level(level_id, 0.80)
        
        level = level_system.get_level(level_id)
        assert level.best_accuracy == 0.95
    
    def test_complete_locked_level_returns_none(self, level_system):
        """Test that completing a locked level returns None."""
        levels = level_system.get_all_levels(Theme.MARIO)
        # Find a locked level
        locked_level = None
        for level in levels:
            if not level.unlocked:
                locked_level = level
                break
        
        if locked_level:
            result = level_system.complete_level(locked_level.id, 0.90)
            assert result is None
    
    def test_complete_nonexistent_level_returns_none(self, level_system):
        """Test that completing a nonexistent level returns None."""
        result = level_system.complete_level("nonexistent_level_id", 0.90)
        assert result is None
    
    def test_accuracy_clamped_to_valid_range(self, level_system):
        """Test that accuracy is clamped to 0.0-1.0 range."""
        levels = level_system.get_all_levels(Theme.MARIO)
        level_id = levels[0].id
        
        # Test with accuracy > 1.0
        level_system.complete_level(level_id, 1.5)
        level = level_system.get_level(level_id)
        assert level.best_accuracy == 1.0
        
        # Reset and test with accuracy < 0.0
        level_system.reset_level_progress(level_id)
        level_system.complete_level(level_id, -0.5)
        level = level_system.get_level(level_id)
        assert level.best_accuracy == 0.0


class TestLevelRewards:
    """Tests for level completion rewards.
    
    Requirements: 15.5
    """
    
    def test_base_reward_earned(self, level_system):
        """Test that base reward is always earned."""
        levels = level_system.get_all_levels(Theme.MARIO)
        level_id = levels[0].id
        
        reward = level_system.complete_level(level_id, 0.50)
        
        assert reward.currency_earned >= BASE_LEVEL_REWARD
    
    def test_accuracy_bonus_90_percent(self, level_system):
        """Test accuracy bonus at 90%."""
        levels = level_system.get_all_levels(Theme.MARIO)
        level_id = levels[0].id
        
        reward = level_system.complete_level(level_id, 0.90)
        
        # Should get base + 25 bonus
        assert reward.currency_earned == BASE_LEVEL_REWARD + 25
    
    def test_accuracy_bonus_95_percent(self, level_system):
        """Test accuracy bonus at 95%."""
        levels = level_system.get_all_levels(Theme.ZELDA)
        level_id = levels[0].id
        
        reward = level_system.complete_level(level_id, 0.95)
        
        # Should get base + 50 bonus
        assert reward.currency_earned == BASE_LEVEL_REWARD + 50
    
    def test_accuracy_bonus_98_percent(self, level_system):
        """Test accuracy bonus at 98%."""
        levels = level_system.get_all_levels(Theme.DKC)
        level_id = levels[0].id
        
        reward = level_system.complete_level(level_id, 0.98)
        
        # Should get base + 75 bonus
        assert reward.currency_earned == BASE_LEVEL_REWARD + 75
    
    def test_accuracy_bonus_100_percent(self, level_system):
        """Test accuracy bonus at 100%."""
        levels = level_system.get_all_levels(Theme.MARIO)
        level_id = levels[0].id
        
        reward = level_system.complete_level(level_id, 1.0)
        
        # Should get base + 100 bonus
        assert reward.currency_earned == BASE_LEVEL_REWARD + 100
    
    def test_reduced_rewards_on_replay(self, level_system):
        """Test that replaying a level gives reduced rewards."""
        levels = level_system.get_all_levels(Theme.MARIO)
        level_id = levels[0].id
        
        # First completion
        first_reward = level_system.complete_level(level_id, 0.90)
        
        # Second completion
        second_reward = level_system.complete_level(level_id, 0.90)
        
        assert second_reward.currency_earned < first_reward.currency_earned
        assert second_reward.currency_earned == first_reward.currency_earned // 2
    
    def test_mario_powerup_at_95_percent(self, level_system):
        """Test Mario theme awards mushroom at 95% accuracy."""
        levels = level_system.get_all_levels(Theme.MARIO)
        level_id = levels[0].id
        
        reward = level_system.complete_level(level_id, 0.95)
        
        assert reward.powerup_earned is not None
        assert reward.powerup_earned.type == PowerUpType.MUSHROOM
    
    def test_mario_powerup_at_98_percent(self, level_system):
        """Test Mario theme awards fire flower at 98% accuracy."""
        levels = level_system.get_all_levels(Theme.MARIO)
        # Use second level to avoid first completion issue
        level_system.unlock_level(Theme.MARIO)
        levels = level_system.get_all_levels(Theme.MARIO)
        level_id = levels[1].id
        
        reward = level_system.complete_level(level_id, 0.98)
        
        assert reward.powerup_earned is not None
        assert reward.powerup_earned.type == PowerUpType.FIRE_FLOWER
    
    def test_mario_powerup_at_100_percent(self, level_system):
        """Test Mario theme awards star at 100% accuracy."""
        levels = level_system.get_all_levels(Theme.MARIO)
        # Use third level
        level_system.unlock_level(Theme.MARIO)
        level_system.unlock_level(Theme.MARIO)
        levels = level_system.get_all_levels(Theme.MARIO)
        level_id = levels[2].id
        
        reward = level_system.complete_level(level_id, 1.0)
        
        assert reward.powerup_earned is not None
        assert reward.powerup_earned.type == PowerUpType.STAR
    
    def test_zelda_powerup_at_95_percent(self, level_system):
        """Test Zelda theme awards heart container at 95% accuracy."""
        levels = level_system.get_all_levels(Theme.ZELDA)
        level_id = levels[0].id
        
        reward = level_system.complete_level(level_id, 0.95)
        
        assert reward.powerup_earned is not None
        assert reward.powerup_earned.type == PowerUpType.HEART_CONTAINER
    
    def test_dkc_powerup_at_95_percent(self, level_system):
        """Test DKC theme awards golden banana at 95% accuracy."""
        levels = level_system.get_all_levels(Theme.DKC)
        level_id = levels[0].id
        
        reward = level_system.complete_level(level_id, 0.95)
        
        assert reward.powerup_earned is not None
        assert reward.powerup_earned.type == PowerUpType.GOLDEN_BANANA
    
    def test_no_powerup_on_replay(self, level_system):
        """Test that replaying a level doesn't award power-ups."""
        levels = level_system.get_all_levels(Theme.MARIO)
        level_id = levels[0].id
        
        # First completion with 100% accuracy
        first_reward = level_system.complete_level(level_id, 1.0)
        assert first_reward.powerup_earned is not None
        
        # Second completion with 100% accuracy
        second_reward = level_system.complete_level(level_id, 1.0)
        assert second_reward.powerup_earned is None


class TestGetAvailableLevels:
    """Tests for get_available_levels() method.
    
    Requirements: 15.2, 15.3, 15.4
    """
    
    def test_returns_only_unlocked_levels(self, level_system):
        """Test that only unlocked levels are returned."""
        levels = level_system.get_available_levels(Theme.MARIO)
        
        for level in levels:
            assert level.unlocked
    
    def test_initial_available_levels(self, level_system):
        """Test initial available levels (only first level)."""
        for theme in Theme:
            levels = level_system.get_available_levels(theme)
            assert len(levels) == 1
            assert levels[0].level_number == 1
    
    def test_available_levels_increases_with_unlocks(self, level_system):
        """Test that available levels increases as levels are unlocked."""
        initial_count = len(level_system.get_available_levels(Theme.MARIO))
        
        level_system.unlock_level(Theme.MARIO)
        level_system.unlock_level(Theme.MARIO)
        
        new_count = len(level_system.get_available_levels(Theme.MARIO))
        assert new_count == initial_count + 2
    
    def test_available_levels_sorted_by_number(self, level_system):
        """Test that available levels are sorted by level number."""
        # Unlock several levels
        for _ in range(5):
            level_system.unlock_level(Theme.ZELDA)
        
        levels = level_system.get_available_levels(Theme.ZELDA)
        
        for i in range(len(levels) - 1):
            assert levels[i].level_number < levels[i + 1].level_number


class TestGetLevelProgress:
    """Tests for get_level_progress() method.
    
    Requirements: 15.2, 15.7
    """
    
    def test_initial_progress(self, level_system):
        """Test initial level progress."""
        progress = level_system.get_level_progress()
        
        # Total levels should be sum of all theme levels
        expected_total = len(MARIO_LEVELS) + len(ZELDA_LEVELS) + len(DKC_LEVELS)
        assert progress.total_levels == expected_total
        
        # Initially 3 levels unlocked (one per theme)
        assert progress.levels_unlocked == 3
        
        # No levels completed initially
        assert progress.levels_completed == 0
        
        # Completion percentage should be 0
        assert progress.completion_percentage == 0.0
    
    def test_progress_after_unlocks(self, level_system):
        """Test progress after unlocking levels."""
        # Unlock some levels
        level_system.unlock_level(Theme.MARIO)
        level_system.unlock_level(Theme.ZELDA)
        
        progress = level_system.get_level_progress()
        
        assert progress.levels_unlocked == 5  # 3 initial + 2 unlocked
    
    def test_progress_after_completions(self, level_system):
        """Test progress after completing levels."""
        # Complete first level of each theme
        for theme in Theme:
            levels = level_system.get_all_levels(theme)
            level_system.complete_level(levels[0].id, 0.90)
        
        progress = level_system.get_level_progress()
        
        assert progress.levels_completed == 3
        assert progress.completion_percentage > 0
    
    def test_completion_percentage_calculation(self, level_system):
        """Test completion percentage calculation."""
        total_levels = level_system.get_level_progress().total_levels
        
        # Complete one level
        levels = level_system.get_all_levels(Theme.MARIO)
        level_system.complete_level(levels[0].id, 0.90)
        
        progress = level_system.get_level_progress()
        
        expected_percentage = (1 / total_levels) * 100.0
        assert abs(progress.completion_percentage - expected_percentage) < 0.01


class TestThemeLevelProgress:
    """Tests for get_theme_level_progress() method."""
    
    def test_mario_theme_progress(self, level_system):
        """Test progress for Mario theme specifically."""
        progress = level_system.get_theme_level_progress(Theme.MARIO)
        
        assert progress.total_levels == len(MARIO_LEVELS)
        assert progress.levels_unlocked == 1
        assert progress.levels_completed == 0
    
    def test_theme_progress_after_unlock(self, level_system):
        """Test theme progress after unlocking a level."""
        level_system.unlock_level(Theme.ZELDA)
        
        progress = level_system.get_theme_level_progress(Theme.ZELDA)
        
        assert progress.levels_unlocked == 2
    
    def test_theme_progress_after_completion(self, level_system):
        """Test theme progress after completing a level."""
        levels = level_system.get_all_levels(Theme.DKC)
        level_system.complete_level(levels[0].id, 0.90)
        
        progress = level_system.get_theme_level_progress(Theme.DKC)
        
        assert progress.levels_completed == 1
        expected_percentage = (1 / len(DKC_LEVELS)) * 100.0
        assert abs(progress.completion_percentage - expected_percentage) < 0.01


class TestHelperMethods:
    """Tests for helper methods."""
    
    def test_get_level(self, level_system):
        """Test getting a specific level by ID."""
        levels = level_system.get_all_levels(Theme.MARIO)
        level_id = levels[0].id
        
        level = level_system.get_level(level_id)
        
        assert level is not None
        assert level.id == level_id
    
    def test_get_nonexistent_level(self, level_system):
        """Test getting a nonexistent level returns None."""
        level = level_system.get_level("nonexistent_id")
        assert level is None
    
    def test_is_level_unlocked(self, level_system):
        """Test is_level_unlocked method."""
        levels = level_system.get_all_levels(Theme.MARIO)
        
        # First level should be unlocked
        assert level_system.is_level_unlocked(levels[0].id)
        
        # Second level should be locked
        if len(levels) > 1:
            assert not level_system.is_level_unlocked(levels[1].id)
    
    def test_is_level_completed(self, level_system):
        """Test is_level_completed method."""
        levels = level_system.get_all_levels(Theme.MARIO)
        level_id = levels[0].id
        
        # Initially not completed
        assert not level_system.is_level_completed(level_id)
        
        # Complete the level
        level_system.complete_level(level_id, 0.90)
        
        # Now should be completed
        assert level_system.is_level_completed(level_id)
    
    def test_get_next_locked_level(self, level_system):
        """Test get_next_locked_level method."""
        next_locked = level_system.get_next_locked_level(Theme.MARIO)
        
        assert next_locked is not None
        assert not next_locked.unlocked
        assert next_locked.level_number == 2
    
    def test_get_next_locked_level_all_unlocked(self, level_system):
        """Test get_next_locked_level when all are unlocked."""
        level_system.unlock_all_levels(Theme.DKC)
        
        next_locked = level_system.get_next_locked_level(Theme.DKC)
        
        assert next_locked is None
    
    def test_get_total_levels_for_theme(self, level_system):
        """Test get_total_levels_for_theme method."""
        assert level_system.get_total_levels_for_theme(Theme.MARIO) == len(MARIO_LEVELS)
        assert level_system.get_total_levels_for_theme(Theme.ZELDA) == len(ZELDA_LEVELS)
        assert level_system.get_total_levels_for_theme(Theme.DKC) == len(DKC_LEVELS)
    
    def test_reset_level_progress(self, level_system):
        """Test reset_level_progress method."""
        levels = level_system.get_all_levels(Theme.MARIO)
        level_id = levels[0].id
        
        # Complete the level
        level_system.complete_level(level_id, 0.95)
        
        # Reset progress
        result = level_system.reset_level_progress(level_id)
        
        assert result
        level = level_system.get_level(level_id)
        assert not level.completed
        assert level.best_accuracy is None
        assert level.completion_date is None
        assert not level.rewards_claimed
    
    def test_reset_nonexistent_level(self, level_system):
        """Test reset_level_progress with nonexistent level."""
        result = level_system.reset_level_progress("nonexistent_id")
        assert not result
    
    def test_unlock_all_levels_specific_theme(self, level_system):
        """Test unlock_all_levels for a specific theme."""
        count = level_system.unlock_all_levels(Theme.MARIO)
        
        # Should unlock all except the first (already unlocked)
        assert count == len(MARIO_LEVELS) - 1
        
        # All Mario levels should be unlocked
        for level in level_system.get_all_levels(Theme.MARIO):
            assert level.unlocked
        
        # Other themes should still have locked levels
        zelda_levels = level_system.get_all_levels(Theme.ZELDA)
        assert not zelda_levels[1].unlocked
    
    def test_unlock_all_levels_all_themes(self, level_system):
        """Test unlock_all_levels for all themes."""
        count = level_system.unlock_all_levels()
        
        # Should unlock all except the 3 initially unlocked
        total_levels = len(MARIO_LEVELS) + len(ZELDA_LEVELS) + len(DKC_LEVELS)
        assert count == total_levels - 3
        
        # All levels should be unlocked
        for theme in Theme:
            for level in level_system.get_all_levels(theme):
                assert level.unlocked


class TestPersistence:
    """Tests for database persistence.
    
    Requirements: 15.6
    """
    
    def test_level_unlock_persists(self, level_system, data_manager):
        """Test that level unlocks persist across instances."""
        # Unlock a level
        unlocked = level_system.unlock_level(Theme.MARIO)
        level_id = unlocked.id
        
        # Create new instance
        new_system = LevelSystem(data_manager)
        
        # Verify level is still unlocked
        level = new_system.get_level(level_id)
        assert level.unlocked
    
    def test_level_completion_persists(self, level_system, data_manager):
        """Test that level completions persist across instances."""
        levels = level_system.get_all_levels(Theme.MARIO)
        level_id = levels[0].id
        
        # Complete the level
        level_system.complete_level(level_id, 0.95)
        
        # Create new instance
        new_system = LevelSystem(data_manager)
        
        # Verify completion persisted
        level = new_system.get_level(level_id)
        assert level.completed
        assert level.best_accuracy == 0.95
        assert level.completion_date is not None
    
    def test_progress_persists(self, level_system, data_manager):
        """Test that overall progress persists across instances."""
        # Make some progress
        level_system.unlock_level(Theme.MARIO)
        level_system.unlock_level(Theme.ZELDA)
        levels = level_system.get_all_levels(Theme.DKC)
        level_system.complete_level(levels[0].id, 0.90)
        
        original_progress = level_system.get_level_progress()
        
        # Create new instance
        new_system = LevelSystem(data_manager)
        new_progress = new_system.get_level_progress()
        
        # Verify progress matches
        assert new_progress.levels_unlocked == original_progress.levels_unlocked
        assert new_progress.levels_completed == original_progress.levels_completed
