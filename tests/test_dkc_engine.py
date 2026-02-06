"""
Unit tests for DKCEngine.

Tests the DKCEngine class functionality including:
- Animation generation for correct/wrong answers
- Collectible generation
- Time trial mechanics
- World completion tracking
- Banana management

Requirements: 6.1, 6.2, 6.3, 6.4, 6.5, 6.6, 6.7, 6.8
"""

import pytest
from datetime import datetime

from themes.dkc_engine import (
    DKCEngine,
    TimeTrial,
    TimeTrialReward,
    JungleWorld,
    CARDS_FOR_FULL_COMPLETION,
)
from core.theme_manager import ThemeEngine
from data.data_manager import DataManager
from data.models import (
    Animation,
    AnimationType,
    Collectible,
    CollectibleType,
    Level,
    LevelView,
    Theme,
    ThemeStats,
)


@pytest.fixture
def temp_db_path(tmp_path):
    """Create a temporary database path for testing."""
    return tmp_path / "test_nintendanki.db"


@pytest.fixture
def data_manager(temp_db_path):
    """Create a DataManager with a temporary database."""
    dm = DataManager(temp_db_path)
    dm.initialize_database()
    return dm


@pytest.fixture
def dkc_engine(data_manager):
    """Create a DKCEngine for testing."""
    return DKCEngine(data_manager)


class TestDKCEngineInitialization:
    """Tests for DKCEngine initialization."""
    
    def test_dkc_engine_is_theme_engine(self, dkc_engine):
        """Test that DKCEngine is a ThemeEngine subclass."""
        assert isinstance(dkc_engine, ThemeEngine)
    
    def test_dkc_engine_initializes_with_data_manager(self, data_manager):
        """Test that DKCEngine initializes with a DataManager."""
        engine = DKCEngine(data_manager)
        assert engine.data_manager is data_manager
    
    def test_dkc_engine_initializes_with_zero_bananas(self, dkc_engine):
        """Test that DKCEngine initializes with 0 bananas."""
        assert dkc_engine.get_banana_count() == 0
    
    def test_dkc_engine_initializes_with_no_active_time_trial(self, dkc_engine):
        """Test that DKCEngine initializes with no active time trial."""
        assert dkc_engine.get_active_time_trial() is None
    
    def test_dkc_engine_initializes_with_bonus_world_locked(self, dkc_engine):
        """Test that DKCEngine initializes with bonus world locked."""
        assert dkc_engine.is_bonus_world_unlocked() is False
    
    def test_dkc_engine_loads_banana_count(self, data_manager):
        """Test that DKCEngine loads banana count from database."""
        # Set up bananas in database
        state = data_manager.load_state()
        state.theme_specific[Theme.DKC].bananas = 100
        data_manager.save_state(state)
        
        # Create engine - should load bananas
        engine = DKCEngine(data_manager)
        assert engine.get_banana_count() == 100


class TestGetAnimationForCorrect:
    """Tests for get_animation_for_correct method.
    
    Requirements: 6.2
    """
    
    def test_returns_animation(self, dkc_engine):
        """Test that get_animation_for_correct returns an Animation."""
        animation = dkc_engine.get_animation_for_correct()
        assert isinstance(animation, Animation)
    
    def test_animation_type_is_collect(self, dkc_engine):
        """Test that animation type is COLLECT for banana collection."""
        animation = dkc_engine.get_animation_for_correct()
        assert animation.type == AnimationType.COLLECT
    
    def test_animation_theme_is_dkc(self, dkc_engine):
        """Test that animation theme is DKC."""
        animation = dkc_engine.get_animation_for_correct()
        assert animation.theme == Theme.DKC
    
    def test_animation_has_sprite_sheet(self, dkc_engine):
        """Test that animation has a sprite sheet path."""
        animation = dkc_engine.get_animation_for_correct()
        assert animation.sprite_sheet is not None
        assert "dkc" in animation.sprite_sheet.lower()
    
    def test_animation_has_frames(self, dkc_engine):
        """Test that animation has frame data."""
        animation = dkc_engine.get_animation_for_correct()
        assert len(animation.frames) > 0
    
    def test_animation_fps_is_valid(self, dkc_engine):
        """Test that animation FPS is at least 30 (Requirement 9.2)."""
        animation = dkc_engine.get_animation_for_correct()
        assert animation.fps >= 30


class TestGetAnimationForWrong:
    """Tests for get_animation_for_wrong method.
    
    Requirements: 6.3
    """
    
    def test_returns_animation(self, dkc_engine):
        """Test that get_animation_for_wrong returns an Animation."""
        animation = dkc_engine.get_animation_for_wrong()
        assert isinstance(animation, Animation)
    
    def test_animation_type_is_damage(self, dkc_engine):
        """Test that animation type is DAMAGE for banana loss."""
        animation = dkc_engine.get_animation_for_wrong()
        assert animation.type == AnimationType.DAMAGE
    
    def test_animation_theme_is_dkc(self, dkc_engine):
        """Test that animation theme is DKC."""
        animation = dkc_engine.get_animation_for_wrong()
        assert animation.theme == Theme.DKC
    
    def test_animation_has_sprite_sheet(self, dkc_engine):
        """Test that animation has a sprite sheet path."""
        animation = dkc_engine.get_animation_for_wrong()
        assert animation.sprite_sheet is not None
        assert "dkc" in animation.sprite_sheet.lower()
    
    def test_animation_has_frames(self, dkc_engine):
        """Test that animation has frame data."""
        animation = dkc_engine.get_animation_for_wrong()
        assert len(animation.frames) > 0


class TestGetCollectibleForCorrect:
    """Tests for get_collectible_for_correct method."""
    
    def test_returns_collectible(self, dkc_engine):
        """Test that get_collectible_for_correct returns a Collectible."""
        collectible = dkc_engine.get_collectible_for_correct()
        assert isinstance(collectible, Collectible)
    
    def test_collectible_is_banana(self, dkc_engine):
        """Test that collectible is a banana."""
        collectible = dkc_engine.get_collectible_for_correct()
        assert collectible.type == CollectibleType.BANANA
    
    def test_collectible_theme_is_dkc(self, dkc_engine):
        """Test that collectible theme is DKC."""
        collectible = dkc_engine.get_collectible_for_correct()
        assert collectible.theme == Theme.DKC
    
    def test_collectible_is_owned(self, dkc_engine):
        """Test that collectible is marked as owned."""
        collectible = dkc_engine.get_collectible_for_correct()
        assert collectible.owned is True


class TestStartTimeTrial:
    """Tests for start_time_trial method.
    
    Requirements: 6.4
    """
    
    def test_returns_time_trial(self, dkc_engine):
        """Test that start_time_trial returns a TimeTrial."""
        trial = dkc_engine.start_time_trial()
        assert isinstance(trial, TimeTrial)
    
    def test_time_trial_has_unique_id(self, dkc_engine):
        """Test that each time trial has a unique ID."""
        trial1 = dkc_engine.start_time_trial()
        trial2 = dkc_engine.start_time_trial()
        assert trial1.id != trial2.id
    
    def test_time_trial_uses_default_duration(self, dkc_engine):
        """Test that time trial uses default duration when not specified."""
        trial = dkc_engine.start_time_trial()
        assert trial.duration_seconds == dkc_engine.DEFAULT_TIME_TRIAL_DURATION
    
    def test_time_trial_uses_custom_duration(self, dkc_engine):
        """Test that time trial uses custom duration when specified."""
        trial = dkc_engine.start_time_trial(duration_seconds=120)
        assert trial.duration_seconds == 120
    
    def test_time_trial_is_active(self, dkc_engine):
        """Test that new time trial is active."""
        trial = dkc_engine.start_time_trial()
        assert trial.active is True
        assert trial.completed is False
    
    def test_time_trial_has_started_at(self, dkc_engine):
        """Test that time trial has a start time."""
        trial = dkc_engine.start_time_trial()
        assert trial.started_at is not None
        assert isinstance(trial.started_at, datetime)
    
    def test_time_trial_remaining_equals_duration(self, dkc_engine):
        """Test that remaining time equals duration at start."""
        trial = dkc_engine.start_time_trial(duration_seconds=90)
        assert trial.remaining_seconds == 90.0
    
    def test_time_trial_sets_active_trial(self, dkc_engine):
        """Test that starting a trial sets it as active."""
        trial = dkc_engine.start_time_trial()
        assert dkc_engine.get_active_time_trial() == trial
    
    def test_is_time_trial_active(self, dkc_engine):
        """Test is_time_trial_active returns correct status."""
        assert dkc_engine.is_time_trial_active() is False
        dkc_engine.start_time_trial()
        assert dkc_engine.is_time_trial_active() is True


class TestCompleteTimeTrial:
    """Tests for complete_time_trial method.
    
    Requirements: 6.5, 6.6
    """
    
    def test_returns_time_trial_reward(self, dkc_engine):
        """Test that complete_time_trial returns a TimeTrialReward."""
        trial = dkc_engine.start_time_trial()
        reward = dkc_engine.complete_time_trial(trial, cards_completed=5)
        assert isinstance(reward, TimeTrialReward)
    
    def test_reward_has_trial_id(self, dkc_engine):
        """Test that reward has the correct trial ID."""
        trial = dkc_engine.start_time_trial()
        reward = dkc_engine.complete_time_trial(trial, cards_completed=5)
        assert reward.trial_id == trial.id
    
    def test_base_bananas_from_cards(self, dkc_engine):
        """Test that base bananas are calculated from cards completed."""
        trial = dkc_engine.start_time_trial()
        reward = dkc_engine.complete_time_trial(trial, cards_completed=10)
        expected_base = 10 * dkc_engine.BANANAS_PER_CARD
        assert reward.base_bananas == expected_base
    
    def test_bonus_bananas_from_remaining_time(self, dkc_engine):
        """Test that bonus bananas are proportional to remaining time.
        
        Requirements: 6.5
        """
        trial = dkc_engine.start_time_trial(duration_seconds=60)
        # Simulate some time passing but not all
        trial.remaining_seconds = 30.0
        
        reward = dkc_engine.complete_time_trial(trial, cards_completed=5)
        expected_bonus = int(30.0 * dkc_engine.BONUS_BANANAS_PER_SECOND)
        assert reward.bonus_bananas == expected_bonus
    
    def test_no_bonus_when_time_expired(self, dkc_engine):
        """Test that no bonus bananas when time has expired.
        
        Requirements: 6.6
        """
        trial = dkc_engine.start_time_trial(duration_seconds=60)
        trial.remaining_seconds = 0.0
        
        reward = dkc_engine.complete_time_trial(trial, cards_completed=5)
        assert reward.bonus_bananas == 0
    
    def test_total_bananas_is_sum(self, dkc_engine):
        """Test that total bananas is sum of base and bonus."""
        trial = dkc_engine.start_time_trial(duration_seconds=60)
        trial.remaining_seconds = 20.0
        
        reward = dkc_engine.complete_time_trial(trial, cards_completed=5)
        assert reward.total_bananas == reward.base_bananas + reward.bonus_bananas
    
    def test_trial_marked_completed(self, dkc_engine):
        """Test that trial is marked as completed."""
        trial = dkc_engine.start_time_trial()
        dkc_engine.complete_time_trial(trial, cards_completed=5)
        assert trial.completed is True
        assert trial.active is False
    
    def test_clears_active_trial(self, dkc_engine):
        """Test that completing a trial clears the active trial."""
        trial = dkc_engine.start_time_trial()
        assert dkc_engine.get_active_time_trial() is not None
        dkc_engine.complete_time_trial(trial, cards_completed=5)
        assert dkc_engine.get_active_time_trial() is None
    
    def test_bananas_added_to_count(self, dkc_engine):
        """Test that earned bananas are added to player's count."""
        initial_bananas = dkc_engine.get_banana_count()
        trial = dkc_engine.start_time_trial()
        reward = dkc_engine.complete_time_trial(trial, cards_completed=5)
        
        assert dkc_engine.get_banana_count() == initial_bananas + reward.total_bananas
    
    def test_reward_tracks_cards_completed(self, dkc_engine):
        """Test that reward tracks cards completed."""
        trial = dkc_engine.start_time_trial()
        reward = dkc_engine.complete_time_trial(trial, cards_completed=15)
        assert reward.cards_completed == 15
    
    def test_reward_tracks_time_remaining(self, dkc_engine):
        """Test that reward tracks time remaining."""
        trial = dkc_engine.start_time_trial(duration_seconds=60)
        trial.remaining_seconds = 25.5
        
        reward = dkc_engine.complete_time_trial(trial, cards_completed=5)
        assert reward.time_remaining == 25.5


class TestUpdateTimeTrial:
    """Tests for update_time_trial method."""
    
    def test_returns_none_when_no_active_trial(self, dkc_engine):
        """Test that update returns None when no trial is active."""
        result = dkc_engine.update_time_trial(1.0)
        assert result is None
    
    def test_decrements_remaining_time(self, dkc_engine):
        """Test that remaining time is decremented."""
        trial = dkc_engine.start_time_trial(duration_seconds=60)
        dkc_engine.update_time_trial(10.0)
        assert trial.remaining_seconds == 50.0
    
    def test_marks_inactive_when_time_expires(self, dkc_engine):
        """Test that trial is marked inactive when time expires.
        
        Requirements: 6.6
        """
        trial = dkc_engine.start_time_trial(duration_seconds=10)
        dkc_engine.update_time_trial(15.0)
        assert trial.active is False
        assert trial.remaining_seconds == 0
    
    def test_remaining_time_not_negative(self, dkc_engine):
        """Test that remaining time doesn't go negative."""
        trial = dkc_engine.start_time_trial(duration_seconds=10)
        dkc_engine.update_time_trial(100.0)
        assert trial.remaining_seconds == 0


class TestGetWorldCompletion:
    """Tests for get_world_completion method.
    
    Requirements: 6.7
    """
    
    def test_returns_float(self, dkc_engine):
        """Test that get_world_completion returns a float."""
        completion = dkc_engine.get_world_completion()
        assert isinstance(completion, float)
    
    def test_zero_completion_initially(self, dkc_engine):
        """Test that completion is 0 initially."""
        completion = dkc_engine.get_world_completion()
        assert completion == 0.0
    
    def test_completion_increases_with_cards(self, data_manager):
        """Test that completion increases with cards reviewed."""
        state = data_manager.load_state()
        state.progression.total_cards_reviewed = 100
        data_manager.save_state(state)
        
        engine = DKCEngine(data_manager)
        completion = engine.get_world_completion()
        
        expected = 100 / CARDS_FOR_FULL_COMPLETION
        assert completion == expected
    
    def test_completion_capped_at_one(self, data_manager):
        """Test that completion is capped at 1.0."""
        state = data_manager.load_state()
        state.progression.total_cards_reviewed = CARDS_FOR_FULL_COMPLETION * 2
        data_manager.save_state(state)
        
        engine = DKCEngine(data_manager)
        completion = engine.get_world_completion()
        
        assert completion == 1.0
    
    def test_completion_is_monotonically_increasing(self, data_manager):
        """Test that completion increases monotonically with cards.
        
        Requirements: 6.7
        """
        completions = []
        for cards in [0, 50, 100, 200, 300, 400, 500]:
            state = data_manager.load_state()
            state.progression.total_cards_reviewed = cards
            data_manager.save_state(state)
            
            engine = DKCEngine(data_manager)
            completions.append(engine.get_world_completion())
        
        # Verify monotonically increasing
        for i in range(1, len(completions)):
            assert completions[i] >= completions[i-1]


class TestBonusWorldUnlock:
    """Tests for bonus world unlock functionality.
    
    Requirements: 6.8
    """
    
    def test_bonus_world_locked_initially(self, dkc_engine):
        """Test that bonus world is locked initially."""
        assert dkc_engine.is_bonus_world_unlocked() is False
    
    def test_bonus_world_unlocks_at_100_percent(self, data_manager):
        """Test that bonus world unlocks at 100% completion.
        
        Requirements: 6.8
        """
        state = data_manager.load_state()
        state.progression.total_cards_reviewed = CARDS_FOR_FULL_COMPLETION
        data_manager.save_state(state)
        
        engine = DKCEngine(data_manager)
        # Trigger completion check
        engine.get_world_completion()
        
        assert engine.is_bonus_world_unlocked() is True
    
    def test_bonus_world_not_unlocked_below_100(self, data_manager):
        """Test that bonus world is not unlocked below 100%."""
        state = data_manager.load_state()
        state.progression.total_cards_reviewed = CARDS_FOR_FULL_COMPLETION - 1
        data_manager.save_state(state)
        
        engine = DKCEngine(data_manager)
        engine.get_world_completion()
        
        assert engine.is_bonus_world_unlocked() is False
    
    def test_bonus_world_persists(self, data_manager):
        """Test that bonus world unlock status persists."""
        # Unlock bonus world
        state = data_manager.load_state()
        state.progression.total_cards_reviewed = CARDS_FOR_FULL_COMPLETION
        data_manager.save_state(state)
        
        engine1 = DKCEngine(data_manager)
        engine1.get_world_completion()
        assert engine1.is_bonus_world_unlocked() is True
        
        # Create new engine - should still be unlocked
        engine2 = DKCEngine(data_manager)
        assert engine2.is_bonus_world_unlocked() is True


class TestGetBananaCount:
    """Tests for get_banana_count method."""
    
    def test_returns_int(self, dkc_engine):
        """Test that get_banana_count returns an int."""
        count = dkc_engine.get_banana_count()
        assert isinstance(count, int)
    
    def test_initial_count_is_zero(self, dkc_engine):
        """Test that initial banana count is 0."""
        assert dkc_engine.get_banana_count() == 0
    
    def test_reflects_database_value(self, data_manager):
        """Test that count reflects database value."""
        state = data_manager.load_state()
        state.theme_specific[Theme.DKC].bananas = 42
        data_manager.save_state(state)
        
        engine = DKCEngine(data_manager)
        assert engine.get_banana_count() == 42


class TestBananaManagement:
    """Tests for banana management methods."""
    
    def test_add_bananas_increments_count(self, dkc_engine):
        """Test that add_bananas increments the count."""
        initial = dkc_engine.get_banana_count()
        dkc_engine.add_bananas(5)
        assert dkc_engine.get_banana_count() == initial + 5
    
    def test_add_bananas_default_is_one(self, dkc_engine):
        """Test that add_bananas defaults to adding 1."""
        initial = dkc_engine.get_banana_count()
        dkc_engine.add_bananas()
        assert dkc_engine.get_banana_count() == initial + 1
    
    def test_add_bananas_returns_new_count(self, dkc_engine):
        """Test that add_bananas returns the new count."""
        new_count = dkc_engine.add_bananas(10)
        assert new_count == 10
    
    def test_add_bananas_persists(self, data_manager):
        """Test that add_bananas persists to database."""
        engine = DKCEngine(data_manager)
        engine.add_bananas(25)
        
        # Create new engine to verify persistence
        engine2 = DKCEngine(data_manager)
        assert engine2.get_banana_count() == 25
    
    def test_remove_bananas_decrements_count(self, dkc_engine):
        """Test that remove_bananas decrements the count."""
        dkc_engine.add_bananas(20)
        dkc_engine.remove_bananas(5)
        assert dkc_engine.get_banana_count() == 15
    
    def test_remove_bananas_uses_default(self, dkc_engine):
        """Test that remove_bananas uses default loss amount.
        
        Requirements: 6.3
        """
        dkc_engine.add_bananas(20)
        dkc_engine.remove_bananas()
        expected = 20 - dkc_engine.BANANAS_LOST_ON_WRONG
        assert dkc_engine.get_banana_count() == expected
    
    def test_remove_bananas_minimum_zero(self, dkc_engine):
        """Test that banana count doesn't go below 0."""
        dkc_engine.add_bananas(5)
        dkc_engine.remove_bananas(100)
        assert dkc_engine.get_banana_count() == 0
    
    def test_remove_bananas_returns_new_count(self, dkc_engine):
        """Test that remove_bananas returns the new count."""
        dkc_engine.add_bananas(20)
        new_count = dkc_engine.remove_bananas(5)
        assert new_count == 15


class TestGetLevelView:
    """Tests for get_level_view method.
    
    Requirements: 6.1
    """
    
    def test_returns_level_view(self, dkc_engine):
        """Test that get_level_view returns a LevelView."""
        level = Level(id="test_level", theme=Theme.DKC, level_number=1, name="Test Level")
        view = dkc_engine.get_level_view(level)
        assert isinstance(view, LevelView)
    
    def test_level_view_has_background(self, dkc_engine):
        """Test that level view has a background image."""
        level = Level(id="test_level", theme=Theme.DKC, level_number=1, name="Test Level")
        view = dkc_engine.get_level_view(level)
        assert view.background is not None
        assert "dkc" in view.background.lower()
    
    def test_level_view_has_character_position(self, dkc_engine):
        """Test that level view has a character starting position."""
        level = Level(id="test_level", theme=Theme.DKC, level_number=1, name="Test Level")
        view = dkc_engine.get_level_view(level)
        assert view.character_position is not None
        assert len(view.character_position) == 2
    
    def test_level_view_has_collectibles(self, dkc_engine):
        """Test that level view has collectibles."""
        level = Level(id="test_level", theme=Theme.DKC, level_number=1, name="Test Level")
        view = dkc_engine.get_level_view(level)
        assert isinstance(view.collectibles_visible, list)
        assert len(view.collectibles_visible) > 0
    
    def test_higher_levels_have_more_collectibles(self, dkc_engine):
        """Test that higher level numbers have more collectibles."""
        level1 = Level(id="level_1", theme=Theme.DKC, level_number=1, name="Level 1")
        level5 = Level(id="level_5", theme=Theme.DKC, level_number=5, name="Level 5")
        
        view1 = dkc_engine.get_level_view(level1)
        view5 = dkc_engine.get_level_view(level5)
        
        assert len(view5.collectibles_visible) > len(view1.collectibles_visible)
    
    def test_every_fifth_level_has_dk_coin(self, dkc_engine):
        """Test that every fifth level has a DK coin collectible."""
        level5 = Level(id="level_5", theme=Theme.DKC, level_number=5, name="Level 5")
        view5 = dkc_engine.get_level_view(level5)
        
        dk_coins = [c for c in view5.collectibles_visible if c.type == CollectibleType.DK_COIN]
        assert len(dk_coins) >= 1


class TestGetDashboardStats:
    """Tests for get_dashboard_stats method."""
    
    def test_returns_theme_stats(self, dkc_engine):
        """Test that get_dashboard_stats returns ThemeStats."""
        stats = dkc_engine.get_dashboard_stats()
        assert isinstance(stats, ThemeStats)
    
    def test_stats_theme_is_dkc(self, dkc_engine):
        """Test that stats theme is DKC."""
        stats = dkc_engine.get_dashboard_stats()
        assert stats.theme == Theme.DKC
    
    def test_stats_primary_collectible_is_bananas(self, dkc_engine):
        """Test that primary collectible is bananas."""
        stats = dkc_engine.get_dashboard_stats()
        assert stats.primary_collectible_name == "Bananas"
    
    def test_stats_secondary_stat_is_dk_coins(self, dkc_engine):
        """Test that secondary stat is DK coins."""
        stats = dkc_engine.get_dashboard_stats()
        assert stats.secondary_stat_name == "DK Coins"
    
    def test_stats_reflects_banana_count(self, data_manager):
        """Test that stats reflects actual banana count."""
        state = data_manager.load_state()
        state.theme_specific[Theme.DKC].bananas = 42
        data_manager.save_state(state)
        
        engine = DKCEngine(data_manager)
        stats = engine.get_dashboard_stats()
        
        assert stats.primary_collectible_count == 42
    
    def test_stats_reflects_completion(self, data_manager):
        """Test that stats reflects world completion."""
        state = data_manager.load_state()
        state.progression.total_cards_reviewed = 250
        data_manager.save_state(state)
        
        engine = DKCEngine(data_manager)
        stats = engine.get_dashboard_stats()
        
        expected_completion = 250 / CARDS_FOR_FULL_COMPLETION
        assert stats.completion_percentage == expected_completion


class TestGetJungleWorlds:
    """Tests for get_jungle_worlds method.
    
    Requirements: 6.1, 6.8
    """
    
    def test_returns_list_of_worlds(self, dkc_engine):
        """Test that get_jungle_worlds returns a list."""
        worlds = dkc_engine.get_jungle_worlds()
        assert isinstance(worlds, list)
        assert all(isinstance(w, JungleWorld) for w in worlds)
    
    def test_has_five_main_worlds(self, dkc_engine):
        """Test that there are 5 main worlds."""
        worlds = dkc_engine.get_jungle_worlds()
        main_worlds = [w for w in worlds if not w.is_bonus_world]
        assert len(main_worlds) == 5
    
    def test_first_world_always_unlocked(self, dkc_engine):
        """Test that the first world is always unlocked."""
        worlds = dkc_engine.get_jungle_worlds()
        assert worlds[0].unlocked is True
    
    def test_worlds_have_names(self, dkc_engine):
        """Test that all worlds have names."""
        worlds = dkc_engine.get_jungle_worlds()
        for world in worlds:
            assert world.name is not None
            assert len(world.name) > 0
    
    def test_bonus_world_not_in_list_initially(self, dkc_engine):
        """Test that bonus world is not in list initially."""
        worlds = dkc_engine.get_jungle_worlds()
        bonus_worlds = [w for w in worlds if w.is_bonus_world]
        assert len(bonus_worlds) == 0
    
    def test_bonus_world_in_list_when_unlocked(self, data_manager):
        """Test that bonus world is in list when unlocked.
        
        Requirements: 6.8
        """
        state = data_manager.load_state()
        state.progression.total_cards_reviewed = CARDS_FOR_FULL_COMPLETION
        data_manager.save_state(state)
        
        engine = DKCEngine(data_manager)
        engine.get_world_completion()  # Trigger unlock check
        
        worlds = engine.get_jungle_worlds()
        bonus_worlds = [w for w in worlds if w.is_bonus_world]
        assert len(bonus_worlds) == 1
        assert bonus_worlds[0].name == "Lost World"
    
    def test_worlds_unlock_progressively(self, data_manager):
        """Test that worlds unlock as completion increases."""
        # At 0% - only first world unlocked
        engine = DKCEngine(data_manager)
        worlds = engine.get_jungle_worlds()
        unlocked = [w for w in worlds if w.unlocked and not w.is_bonus_world]
        assert len(unlocked) == 1
        
        # At 50% - more worlds unlocked
        state = data_manager.load_state()
        state.progression.total_cards_reviewed = int(CARDS_FOR_FULL_COMPLETION * 0.5)
        data_manager.save_state(state)
        
        engine2 = DKCEngine(data_manager)
        worlds2 = engine2.get_jungle_worlds()
        unlocked2 = [w for w in worlds2 if w.unlocked and not w.is_bonus_world]
        assert len(unlocked2) > len(unlocked)


class TestSpriteAnimations:
    """Tests for sprite animation methods."""
    
    def test_get_run_animation(self, dkc_engine):
        """Test get_run_animation returns valid animation."""
        animation = dkc_engine.get_run_animation()
        
        assert isinstance(animation, Animation)
        assert animation.type == AnimationType.RUN
        assert animation.theme == Theme.DKC
        assert animation.loop is True  # Running should loop
    
    def test_get_idle_animation(self, dkc_engine):
        """Test get_idle_animation returns valid animation."""
        animation = dkc_engine.get_idle_animation()
        
        assert isinstance(animation, Animation)
        assert animation.type == AnimationType.IDLE
        assert animation.theme == Theme.DKC
        assert animation.loop is True  # Idle should loop
    
    def test_get_victory_animation(self, dkc_engine):
        """Test get_victory_animation returns valid animation."""
        animation = dkc_engine.get_victory_animation()
        
        assert isinstance(animation, Animation)
        assert animation.type == AnimationType.VICTORY
        assert animation.theme == Theme.DKC
        assert animation.loop is False  # Victory should not loop


class TestTimeTrialDataclass:
    """Tests for TimeTrial dataclass."""
    
    def test_time_trial_defaults(self):
        """Test TimeTrial default values."""
        trial = TimeTrial(id="test", duration_seconds=60)
        
        assert trial.started_at is None
        assert trial.remaining_seconds == 0.0
        assert trial.cards_completed == 0
        assert trial.active is False
        assert trial.completed is False


class TestTimeTrialRewardDataclass:
    """Tests for TimeTrialReward dataclass."""
    
    def test_time_trial_reward_creation(self):
        """Test TimeTrialReward creation."""
        reward = TimeTrialReward(
            trial_id="test",
            base_bananas=25,
            bonus_bananas=40,
            total_bananas=65,
            time_remaining=20.0,
            cards_completed=5
        )
        
        assert reward.trial_id == "test"
        assert reward.base_bananas == 25
        assert reward.bonus_bananas == 40
        assert reward.total_bananas == 65
        assert reward.time_remaining == 20.0
        assert reward.cards_completed == 5


class TestJungleWorldDataclass:
    """Tests for JungleWorld dataclass."""
    
    def test_jungle_world_defaults(self):
        """Test JungleWorld default values."""
        world = JungleWorld(id="test", name="Test World")
        
        assert world.completion_percentage == 0.0
        assert world.is_bonus_world is False
        assert world.unlocked is True
        assert world.levels == []
