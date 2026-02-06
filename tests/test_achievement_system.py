"""
Unit tests for the AchievementSystem.

Tests cover achievement tracking, unlocking, progress calculation,
and persistence functionality.

Requirements: 14.1, 14.2, 14.3, 14.4, 14.5, 14.6
"""

import pytest

from data.data_manager import DataManager
from data.models import ProgressionState
from core.achievement_system import AchievementSystem


@pytest.fixture
def temp_db(tmp_path):
    """Create a temporary database for testing."""
    db_path = tmp_path / "test_game.db"
    data_manager = DataManager(db_path)
    data_manager.initialize_database()
    return data_manager


@pytest.fixture
def achievement_system(temp_db):
    """Create an AchievementSystem instance with a temporary database."""
    return AchievementSystem(temp_db)


@pytest.fixture
def default_state():
    """Create a default ProgressionState for testing."""
    return ProgressionState(
        total_points=0,
        total_cards_reviewed=0,
        correct_answers=0,
        current_streak=0,
        best_streak=0,
        levels_unlocked=0,
        levels_completed=0,
        session_accuracy=1.0,
        session_health=100,
    )


class TestAchievementInitialization:
    """Tests for AchievementSystem initialization."""
    
    def test_all_achievements_defined(self, achievement_system):
        """All predefined achievements should be initialized."""
        achievements = achievement_system.get_all_achievements()
        
        # Count expected achievements from all categories
        expected_count = sum(
            len(achievements_list) 
            for achievements_list in AchievementSystem.ACHIEVEMENT_DEFINITIONS.values()
        )
        
        assert len(achievements) == expected_count
    
    def test_achievements_start_locked(self, achievement_system):
        """All achievements should start in locked state."""
        achievements = achievement_system.get_all_achievements()
        
        for achievement in achievements:
            assert achievement.unlocked is False
            assert achievement.unlock_date is None
    
    def test_achievements_have_required_fields(self, achievement_system):
        """Each achievement should have all required fields."""
        achievements = achievement_system.get_all_achievements()
        
        for achievement in achievements:
            assert achievement.id is not None
            assert achievement.name is not None
            assert achievement.description is not None
            assert achievement.icon is not None
            assert achievement.reward_currency >= 0
            assert achievement.target > 0


class TestCardsReviewedAchievements:
    """Tests for cards reviewed achievements - Requirement 14.6"""
    
    def test_unlock_cards_100(self, achievement_system, default_state):
        """Achievement should unlock at 100 cards reviewed."""
        default_state.total_cards_reviewed = 100
        
        newly_unlocked = achievement_system.check_achievements(default_state)
        
        unlocked_ids = [a.id for a in newly_unlocked]
        assert "cards_100" in unlocked_ids
    
    def test_unlock_cards_500(self, achievement_system, default_state):
        """Achievement should unlock at 500 cards reviewed."""
        default_state.total_cards_reviewed = 500
        
        newly_unlocked = achievement_system.check_achievements(default_state)
        
        unlocked_ids = [a.id for a in newly_unlocked]
        assert "cards_500" in unlocked_ids
    
    def test_unlock_cards_1000(self, achievement_system, default_state):
        """Achievement should unlock at 1000 cards reviewed."""
        default_state.total_cards_reviewed = 1000
        
        newly_unlocked = achievement_system.check_achievements(default_state)
        
        unlocked_ids = [a.id for a in newly_unlocked]
        assert "cards_1000" in unlocked_ids
    
    def test_unlock_cards_5000(self, achievement_system, default_state):
        """Achievement should unlock at 5000 cards reviewed."""
        default_state.total_cards_reviewed = 5000
        
        newly_unlocked = achievement_system.check_achievements(default_state)
        
        unlocked_ids = [a.id for a in newly_unlocked]
        assert "cards_5000" in unlocked_ids
    
    def test_no_unlock_below_threshold(self, achievement_system, default_state):
        """No achievement should unlock below the threshold."""
        default_state.total_cards_reviewed = 99
        
        newly_unlocked = achievement_system.check_achievements(default_state)
        
        unlocked_ids = [a.id for a in newly_unlocked]
        assert "cards_100" not in unlocked_ids
    
    def test_multiple_cards_achievements_unlock_together(self, achievement_system, default_state):
        """Multiple achievements can unlock at once if thresholds are met."""
        default_state.total_cards_reviewed = 1000
        
        newly_unlocked = achievement_system.check_achievements(default_state)
        
        unlocked_ids = [a.id for a in newly_unlocked]
        assert "cards_100" in unlocked_ids
        assert "cards_500" in unlocked_ids
        assert "cards_1000" in unlocked_ids


class TestStreakAchievements:
    """Tests for streak achievements - Requirement 14.6"""
    
    def test_unlock_streak_10(self, achievement_system, default_state):
        """Achievement should unlock at streak of 10."""
        default_state.current_streak = 10
        
        newly_unlocked = achievement_system.check_achievements(default_state)
        
        unlocked_ids = [a.id for a in newly_unlocked]
        assert "streak_10" in unlocked_ids
    
    def test_unlock_streak_25(self, achievement_system, default_state):
        """Achievement should unlock at streak of 25."""
        default_state.current_streak = 25
        
        newly_unlocked = achievement_system.check_achievements(default_state)
        
        unlocked_ids = [a.id for a in newly_unlocked]
        assert "streak_25" in unlocked_ids
    
    def test_unlock_streak_50(self, achievement_system, default_state):
        """Achievement should unlock at streak of 50."""
        default_state.current_streak = 50
        
        newly_unlocked = achievement_system.check_achievements(default_state)
        
        unlocked_ids = [a.id for a in newly_unlocked]
        assert "streak_50" in unlocked_ids
    
    def test_unlock_streak_100(self, achievement_system, default_state):
        """Achievement should unlock at streak of 100."""
        default_state.current_streak = 100
        
        newly_unlocked = achievement_system.check_achievements(default_state)
        
        unlocked_ids = [a.id for a in newly_unlocked]
        assert "streak_100" in unlocked_ids
    
    def test_best_streak_counts_for_achievement(self, achievement_system, default_state):
        """Best streak should count for achievement even if current streak is lower."""
        default_state.current_streak = 5
        default_state.best_streak = 25
        
        newly_unlocked = achievement_system.check_achievements(default_state)
        
        unlocked_ids = [a.id for a in newly_unlocked]
        assert "streak_10" in unlocked_ids
        assert "streak_25" in unlocked_ids


class TestAccuracyAchievements:
    """Tests for accuracy achievements - Requirement 14.6"""
    
    def test_unlock_accuracy_90(self, achievement_system, default_state):
        """Achievement should unlock at 90% session accuracy."""
        default_state.total_cards_reviewed = 10
        default_state.session_accuracy = 0.90
        
        newly_unlocked = achievement_system.check_achievements(default_state)
        
        unlocked_ids = [a.id for a in newly_unlocked]
        assert "accuracy_90" in unlocked_ids
    
    def test_unlock_accuracy_95(self, achievement_system, default_state):
        """Achievement should unlock at 95% session accuracy."""
        default_state.total_cards_reviewed = 10
        default_state.session_accuracy = 0.95
        
        newly_unlocked = achievement_system.check_achievements(default_state)
        
        unlocked_ids = [a.id for a in newly_unlocked]
        assert "accuracy_95" in unlocked_ids
    
    def test_unlock_accuracy_100(self, achievement_system, default_state):
        """Achievement should unlock at 100% session accuracy."""
        default_state.total_cards_reviewed = 10
        default_state.session_accuracy = 1.0
        
        newly_unlocked = achievement_system.check_achievements(default_state)
        
        unlocked_ids = [a.id for a in newly_unlocked]
        assert "accuracy_100" in unlocked_ids
    
    def test_no_accuracy_achievement_without_reviews(self, achievement_system, default_state):
        """No accuracy achievement should unlock without any reviews."""
        default_state.total_cards_reviewed = 0
        default_state.session_accuracy = 1.0
        
        newly_unlocked = achievement_system.check_achievements(default_state)
        
        unlocked_ids = [a.id for a in newly_unlocked]
        assert "accuracy_100" not in unlocked_ids


class TestLevelAchievements:
    """Tests for level completion achievements - Requirement 14.6"""
    
    def test_unlock_levels_1(self, achievement_system, default_state):
        """Achievement should unlock at 1 level completed."""
        default_state.levels_completed = 1
        
        newly_unlocked = achievement_system.check_achievements(default_state)
        
        unlocked_ids = [a.id for a in newly_unlocked]
        assert "levels_1" in unlocked_ids
    
    def test_unlock_levels_5(self, achievement_system, default_state):
        """Achievement should unlock at 5 levels completed."""
        default_state.levels_completed = 5
        
        newly_unlocked = achievement_system.check_achievements(default_state)
        
        unlocked_ids = [a.id for a in newly_unlocked]
        assert "levels_5" in unlocked_ids
    
    def test_unlock_levels_10(self, achievement_system, default_state):
        """Achievement should unlock at 10 levels completed."""
        default_state.levels_completed = 10
        
        newly_unlocked = achievement_system.check_achievements(default_state)
        
        unlocked_ids = [a.id for a in newly_unlocked]
        assert "levels_10" in unlocked_ids
    
    def test_unlock_levels_25(self, achievement_system, default_state):
        """Achievement should unlock at 25 levels completed."""
        default_state.levels_completed = 25
        
        newly_unlocked = achievement_system.check_achievements(default_state)
        
        unlocked_ids = [a.id for a in newly_unlocked]
        assert "levels_25" in unlocked_ids


class TestThemeSpecificAchievements:
    """Tests for theme-specific achievements - Requirement 14.6"""
    
    def test_unlock_mario_coins_100(self, achievement_system, default_state):
        """Mario coins achievement should unlock at 100 coins."""
        theme_state = {"mario_coins": 100}
        
        newly_unlocked = achievement_system.check_achievements(default_state, theme_state)
        
        unlocked_ids = [a.id for a in newly_unlocked]
        assert "mario_coins_100" in unlocked_ids
    
    def test_unlock_mario_coins_500(self, achievement_system, default_state):
        """Mario coins achievement should unlock at 500 coins."""
        theme_state = {"mario_coins": 500}
        
        newly_unlocked = achievement_system.check_achievements(default_state, theme_state)
        
        unlocked_ids = [a.id for a in newly_unlocked]
        assert "mario_coins_500" in unlocked_ids
    
    def test_unlock_mario_star_powerup(self, achievement_system, default_state):
        """Mario star achievement should unlock when star is earned."""
        theme_state = {"mario_stars": 1}
        
        newly_unlocked = achievement_system.check_achievements(default_state, theme_state)
        
        unlocked_ids = [a.id for a in newly_unlocked]
        assert "mario_powerup_star" in unlocked_ids
    
    def test_unlock_zelda_boss_1(self, achievement_system, default_state):
        """Zelda boss achievement should unlock at 1 boss defeated."""
        theme_state = {"zelda_bosses_defeated": 1}
        
        newly_unlocked = achievement_system.check_achievements(default_state, theme_state)
        
        unlocked_ids = [a.id for a in newly_unlocked]
        assert "zelda_boss_1" in unlocked_ids
    
    def test_unlock_zelda_boss_5(self, achievement_system, default_state):
        """Zelda boss achievement should unlock at 5 bosses defeated."""
        theme_state = {"zelda_bosses_defeated": 5}
        
        newly_unlocked = achievement_system.check_achievements(default_state, theme_state)
        
        unlocked_ids = [a.id for a in newly_unlocked]
        assert "zelda_boss_5" in unlocked_ids
    
    def test_unlock_zelda_hearts(self, achievement_system, default_state):
        """Zelda hearts achievement should unlock at 10 hearts."""
        theme_state = {"zelda_hearts": 10}
        
        newly_unlocked = achievement_system.check_achievements(default_state, theme_state)
        
        unlocked_ids = [a.id for a in newly_unlocked]
        assert "zelda_hearts_10" in unlocked_ids
    
    def test_unlock_dkc_bananas_100(self, achievement_system, default_state):
        """DKC bananas achievement should unlock at 100 bananas."""
        theme_state = {"dkc_bananas": 100}
        
        newly_unlocked = achievement_system.check_achievements(default_state, theme_state)
        
        unlocked_ids = [a.id for a in newly_unlocked]
        assert "dkc_bananas_100" in unlocked_ids
    
    def test_unlock_dkc_bananas_1000(self, achievement_system, default_state):
        """DKC bananas achievement should unlock at 1000 bananas."""
        theme_state = {"dkc_bananas": 1000}
        
        newly_unlocked = achievement_system.check_achievements(default_state, theme_state)
        
        unlocked_ids = [a.id for a in newly_unlocked]
        assert "dkc_bananas_1000" in unlocked_ids
    
    def test_unlock_dkc_time_trial(self, achievement_system, default_state):
        """DKC time trial achievement should unlock when time trial is completed."""
        theme_state = {"dkc_time_trials_completed": 1}
        
        newly_unlocked = achievement_system.check_achievements(default_state, theme_state)
        
        unlocked_ids = [a.id for a in newly_unlocked]
        assert "dkc_time_trial" in unlocked_ids


class TestAchievementPersistence:
    """Tests for achievement persistence - Requirement 14.4"""
    
    def test_unlocked_achievements_persist(self, temp_db, default_state):
        """Unlocked achievements should persist to database."""
        achievement_system = AchievementSystem(temp_db)
        default_state.total_cards_reviewed = 100
        
        achievement_system.check_achievements(default_state)
        
        # Create new instance to verify persistence
        new_achievement_system = AchievementSystem(temp_db)
        achievement = new_achievement_system.get_achievement_by_id("cards_100")
        
        assert achievement is not None
        assert achievement.unlocked is True
    
    def test_unlock_date_persists(self, temp_db, default_state):
        """Unlock date should persist to database."""
        achievement_system = AchievementSystem(temp_db)
        default_state.total_cards_reviewed = 100
        
        achievement_system.check_achievements(default_state)
        
        # Create new instance to verify persistence
        new_achievement_system = AchievementSystem(temp_db)
        achievement = new_achievement_system.get_achievement_by_id("cards_100")
        
        assert achievement.unlock_date is not None
    
    def test_progress_persists(self, temp_db, default_state):
        """Achievement progress should persist to database."""
        achievement_system = AchievementSystem(temp_db)
        default_state.total_cards_reviewed = 50  # Halfway to 100
        
        achievement_system.check_achievements(default_state)
        
        # Create new instance to verify persistence
        new_achievement_system = AchievementSystem(temp_db)
        progress = new_achievement_system.get_progress("cards_100")
        
        assert progress.current == 50


class TestAchievementProgress:
    """Tests for get_progress method - Requirement 14.1"""
    
    def test_progress_calculation(self, achievement_system, default_state):
        """Progress should be calculated correctly."""
        default_state.total_cards_reviewed = 50
        achievement_system.check_achievements(default_state)
        
        progress = achievement_system.get_progress("cards_100")
        
        assert progress.current == 50
        assert progress.target == 100
        assert progress.percentage == 0.5
    
    def test_progress_capped_at_target(self, achievement_system, default_state):
        """Progress should not exceed target."""
        default_state.total_cards_reviewed = 200
        achievement_system.check_achievements(default_state)
        
        progress = achievement_system.get_progress("cards_100")
        
        assert progress.current == 100
        assert progress.percentage == 1.0
    
    def test_progress_for_nonexistent_achievement(self, achievement_system):
        """Getting progress for nonexistent achievement should raise KeyError."""
        with pytest.raises(KeyError):
            achievement_system.get_progress("nonexistent_achievement")


class TestGetAllAchievements:
    """Tests for get_all_achievements method - Requirement 14.5"""
    
    def test_returns_all_achievements(self, achievement_system):
        """Should return all defined achievements."""
        achievements = achievement_system.get_all_achievements()
        
        # Verify we have achievements from each category
        ids = [a.id for a in achievements]
        
        assert "cards_100" in ids
        assert "streak_10" in ids
        assert "accuracy_90" in ids
        assert "levels_1" in ids
        assert "mario_coins_100" in ids
        assert "zelda_boss_1" in ids
        assert "dkc_bananas_100" in ids
    
    def test_includes_unlock_status(self, achievement_system, default_state):
        """Achievements should include unlock status."""
        default_state.total_cards_reviewed = 100
        achievement_system.check_achievements(default_state)
        
        achievements = achievement_system.get_all_achievements()
        cards_100 = next(a for a in achievements if a.id == "cards_100")
        
        assert cards_100.unlocked is True
    
    def test_includes_unlock_date(self, achievement_system, default_state):
        """Unlocked achievements should include unlock date."""
        default_state.total_cards_reviewed = 100
        achievement_system.check_achievements(default_state)
        
        achievements = achievement_system.get_all_achievements()
        cards_100 = next(a for a in achievements if a.id == "cards_100")
        
        assert cards_100.unlock_date is not None


class TestAchievementNotifications:
    """Tests for achievement unlock notifications - Requirement 14.3"""
    
    def test_returns_newly_unlocked(self, achievement_system, default_state):
        """check_achievements should return newly unlocked achievements."""
        default_state.total_cards_reviewed = 100
        
        newly_unlocked = achievement_system.check_achievements(default_state)
        
        assert len(newly_unlocked) > 0
        assert any(a.id == "cards_100" for a in newly_unlocked)
    
    def test_does_not_return_already_unlocked(self, achievement_system, default_state):
        """Already unlocked achievements should not be returned again."""
        default_state.total_cards_reviewed = 100
        
        # First check unlocks the achievement
        first_unlocked = achievement_system.check_achievements(default_state)
        assert any(a.id == "cards_100" for a in first_unlocked)
        
        # Second check should not return it again
        second_unlocked = achievement_system.check_achievements(default_state)
        assert not any(a.id == "cards_100" for a in second_unlocked)
    
    def test_returns_empty_when_no_new_unlocks(self, achievement_system, default_state):
        """Should return empty list when no new achievements are unlocked."""
        default_state.total_cards_reviewed = 50  # Not enough for any achievement
        
        newly_unlocked = achievement_system.check_achievements(default_state)
        
        # Filter out any achievements that might have been unlocked
        cards_achievements = [a for a in newly_unlocked if a.id.startswith("cards_")]
        assert len(cards_achievements) == 0


class TestHelperMethods:
    """Tests for helper methods."""
    
    def test_get_unlocked_achievements(self, achievement_system, default_state):
        """get_unlocked_achievements should return only unlocked achievements."""
        default_state.total_cards_reviewed = 100
        achievement_system.check_achievements(default_state)
        
        unlocked = achievement_system.get_unlocked_achievements()
        
        assert all(a.unlocked for a in unlocked)
        assert any(a.id == "cards_100" for a in unlocked)
    
    def test_get_locked_achievements(self, achievement_system, default_state):
        """get_locked_achievements should return only locked achievements."""
        default_state.total_cards_reviewed = 100
        achievement_system.check_achievements(default_state)
        
        locked = achievement_system.get_locked_achievements()
        
        assert all(not a.unlocked for a in locked)
        assert not any(a.id == "cards_100" for a in locked)
    
    def test_get_achievement_by_id(self, achievement_system):
        """get_achievement_by_id should return the correct achievement."""
        achievement = achievement_system.get_achievement_by_id("cards_100")
        
        assert achievement is not None
        assert achievement.id == "cards_100"
        assert achievement.name == "First Steps"
    
    def test_get_achievement_by_id_not_found(self, achievement_system):
        """get_achievement_by_id should return None for nonexistent ID."""
        achievement = achievement_system.get_achievement_by_id("nonexistent")
        
        assert achievement is None
    
    def test_get_total_reward_currency(self, achievement_system, default_state):
        """get_total_reward_currency should sum rewards from unlocked achievements."""
        default_state.total_cards_reviewed = 500
        achievement_system.check_achievements(default_state)
        
        total = achievement_system.get_total_reward_currency()
        
        # cards_100 (50) + cards_500 (100) = 150
        assert total >= 150
    
    def test_get_completion_percentage(self, achievement_system, default_state):
        """get_completion_percentage should calculate correctly."""
        initial_percentage = achievement_system.get_completion_percentage()
        assert initial_percentage == 0.0
        
        default_state.total_cards_reviewed = 100
        achievement_system.check_achievements(default_state)
        
        new_percentage = achievement_system.get_completion_percentage()
        assert new_percentage > 0.0
    
    def test_reset_achievements(self, achievement_system, default_state):
        """reset_achievements should reset all achievements to locked state."""
        default_state.total_cards_reviewed = 100
        achievement_system.check_achievements(default_state)
        
        # Verify achievement is unlocked
        assert achievement_system.get_achievement_by_id("cards_100").unlocked is True
        
        # Reset
        achievement_system.reset_achievements()
        
        # Verify achievement is locked again
        assert achievement_system.get_achievement_by_id("cards_100").unlocked is False
