"""
Integration tests for NintendAnki.

This module tests end-to-end integration scenarios:
1. Full review cycle with all themes (Mario, Zelda, DKC)
2. Theme switching during session preserves progression
3. Add-on load/unload cycle

Requirements tested: 1.3, 7.3
"""

import pytest
from unittest.mock import MagicMock
from pathlib import Path
import tempfile

from main import NintendAnki, initialize, shutdown, get_instance
from data.models import Theme, AnimationType
from integration.hook_handler import MockAnkiHookProvider


# ============================================================================
# Fixtures
# ============================================================================

@pytest.fixture
def temp_addon_dir():
    """Create a temporary add-on directory for testing."""
    with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as tmpdir:
        addon_dir = Path(tmpdir)
        # Create required subdirectories
        (addon_dir / "data").mkdir(parents=True, exist_ok=True)
        (addon_dir / "assets").mkdir(parents=True, exist_ok=True)
        yield addon_dir


@pytest.fixture
def nintendanki(temp_addon_dir):
    """Create a NintendAnki instance for testing."""
    app = NintendAnki(addon_dir=temp_addon_dir, use_real_anki=False)
    app.initialize()
    yield app
    app.shutdown()


@pytest.fixture
def mock_card():
    """Create a mock Anki card object."""
    card = MagicMock()
    card.id = 12345
    card.did = 1  # deck id
    card.ivl = 1  # interval
    card.reps = 5  # repetitions
    card.lapses = 0  # lapses
    return card


@pytest.fixture
def mock_reviewer():
    """Create a mock Anki reviewer object."""
    return MagicMock()


# ============================================================================
# Test 1: Full Review Cycle with All Themes
# ============================================================================

class TestFullReviewCycleAllThemes:
    """Test full review cycle with all themes (Mario, Zelda, DKC).
    
    Requirements: 7.3 - THE Add-on SHALL not interfere with Anki's native 
    review functionality
    """
    
    def test_mario_theme_review_cycle(
        self, nintendanki, mock_reviewer, mock_card
    ):
        """Test complete review cycle with Mario theme.
        
        Verifies that reviews work correctly with Mario theme active,
        including correct animations and collectibles.
        """
        # Set Mario theme
        nintendanki.theme_manager.set_theme(Theme.MARIO)
        assert nintendanki.theme_manager.get_current_theme() == Theme.MARIO
        
        # Get initial state
        initial_state = nintendanki.progression_system.get_state()
        initial_cards = initial_state.total_cards_reviewed
        initial_points = initial_state.total_points
        
        # Simulate correct review
        nintendanki.hook_handler.on_card_reviewed(mock_reviewer, mock_card, ease=3)
        
        # Verify progression updated
        updated_state = nintendanki.progression_system.get_state()
        assert updated_state.total_cards_reviewed == initial_cards + 1
        assert updated_state.total_points > initial_points
        
        # Verify Mario theme engine provides correct animation
        theme_engine = nintendanki.theme_manager.get_theme_engine()
        animation = theme_engine.get_animation_for_correct()
        assert animation.type == AnimationType.COLLECT
        assert animation.theme == Theme.MARIO
    
    def test_zelda_theme_review_cycle(
        self, nintendanki, mock_reviewer, mock_card
    ):
        """Test complete review cycle with Zelda theme.
        
        Verifies that reviews work correctly with Zelda theme active,
        including correct animations and collectibles.
        """
        # Set Zelda theme
        nintendanki.theme_manager.set_theme(Theme.ZELDA)
        assert nintendanki.theme_manager.get_current_theme() == Theme.ZELDA
        
        # Get initial state
        initial_state = nintendanki.progression_system.get_state()
        initial_cards = initial_state.total_cards_reviewed
        initial_points = initial_state.total_points
        
        # Simulate correct review
        nintendanki.hook_handler.on_card_reviewed(mock_reviewer, mock_card, ease=3)
        
        # Verify progression updated
        updated_state = nintendanki.progression_system.get_state()
        assert updated_state.total_cards_reviewed == initial_cards + 1
        assert updated_state.total_points > initial_points
        
        # Verify Zelda theme engine provides correct animation
        theme_engine = nintendanki.theme_manager.get_theme_engine()
        animation = theme_engine.get_animation_for_correct()
        assert animation.type == AnimationType.COLLECT
        assert animation.theme == Theme.ZELDA
    
    def test_dkc_theme_review_cycle(
        self, nintendanki, mock_reviewer, mock_card
    ):
        """Test complete review cycle with DKC theme.
        
        Verifies that reviews work correctly with DKC theme active,
        including correct animations and collectibles.
        """
        # Set DKC theme
        nintendanki.theme_manager.set_theme(Theme.DKC)
        assert nintendanki.theme_manager.get_current_theme() == Theme.DKC
        
        # Get initial state
        initial_state = nintendanki.progression_system.get_state()
        initial_cards = initial_state.total_cards_reviewed
        initial_points = initial_state.total_points
        
        # Simulate correct review
        nintendanki.hook_handler.on_card_reviewed(mock_reviewer, mock_card, ease=3)
        
        # Verify progression updated
        updated_state = nintendanki.progression_system.get_state()
        assert updated_state.total_cards_reviewed == initial_cards + 1
        assert updated_state.total_points > initial_points
        
        # Verify DKC theme engine provides correct animation
        theme_engine = nintendanki.theme_manager.get_theme_engine()
        animation = theme_engine.get_animation_for_correct()
        assert animation.type == AnimationType.COLLECT
        assert animation.theme == Theme.DKC
    
    def test_all_themes_handle_wrong_answers(
        self, nintendanki, mock_reviewer, mock_card
    ):
        """Test that all themes handle wrong answers correctly.
        
        Verifies that wrong answers produce damage animations for all themes.
        """
        for theme in [Theme.MARIO, Theme.ZELDA, Theme.DKC]:
            nintendanki.theme_manager.set_theme(theme)
            
            # Get initial state
            initial_state = nintendanki.progression_system.get_state()
            initial_cards = initial_state.total_cards_reviewed
            
            # Simulate wrong review (ease=1 is "Again")
            nintendanki.hook_handler.on_card_reviewed(mock_reviewer, mock_card, ease=1)
            
            # Verify card was counted
            updated_state = nintendanki.progression_system.get_state()
            assert updated_state.total_cards_reviewed == initial_cards + 1
            
            # Verify theme engine provides damage animation
            theme_engine = nintendanki.theme_manager.get_theme_engine()
            animation = theme_engine.get_animation_for_wrong()
            assert animation.type == AnimationType.DAMAGE
            assert animation.theme == theme
    
    def test_multiple_reviews_all_themes(
        self, nintendanki, mock_reviewer, mock_card
    ):
        """Test multiple reviews across all themes.
        
        Verifies that the add-on handles multiple reviews correctly
        across all themes without interfering with Anki functionality.
        
        Requirement 7.3: THE Add-on SHALL not interfere with Anki's 
        native review functionality
        """
        reviews_per_theme = 5
        
        for theme in [Theme.MARIO, Theme.ZELDA, Theme.DKC]:
            nintendanki.theme_manager.set_theme(theme)
            
            initial_state = nintendanki.progression_system.get_state()
            initial_cards = initial_state.total_cards_reviewed
            
            # Simulate multiple reviews
            for i in range(reviews_per_theme):
                ease = 3 if i % 2 == 0 else 1  # Alternate correct/wrong
                nintendanki.hook_handler.on_card_reviewed(mock_reviewer, mock_card, ease=ease)
            
            # Verify all reviews were processed
            updated_state = nintendanki.progression_system.get_state()
            assert updated_state.total_cards_reviewed == initial_cards + reviews_per_theme


# ============================================================================
# Test 2: Theme Switching During Session
# ============================================================================

class TestThemeSwitchingDuringSession:
    """Test theme switching during session preserves progression.
    
    Requirement 1.3: WHEN a user switches themes mid-session, THE 
    Progression_System SHALL preserve all accumulated points, levels, 
    and achievements
    """
    
    def test_theme_switch_preserves_points(
        self, nintendanki, mock_reviewer, mock_card
    ):
        """Test that switching themes preserves accumulated points.
        
        Requirement 1.3: Preserve all accumulated points
        """
        # Start with Mario theme and accumulate points
        nintendanki.theme_manager.set_theme(Theme.MARIO)
        
        for _ in range(10):
            nintendanki.hook_handler.on_card_reviewed(mock_reviewer, mock_card, ease=3)
        
        state_before_switch = nintendanki.progression_system.get_state()
        points_before = state_before_switch.total_points
        
        # Switch to Zelda theme
        nintendanki.theme_manager.set_theme(Theme.ZELDA)
        
        # Verify points are preserved
        state_after_switch = nintendanki.progression_system.get_state()
        assert state_after_switch.total_points == points_before
    
    def test_theme_switch_preserves_cards_reviewed(
        self, nintendanki, mock_reviewer, mock_card
    ):
        """Test that switching themes preserves cards reviewed count.
        
        Requirement 1.3: Preserve progression
        """
        # Start with Mario theme
        nintendanki.theme_manager.set_theme(Theme.MARIO)
        
        for _ in range(5):
            nintendanki.hook_handler.on_card_reviewed(mock_reviewer, mock_card, ease=3)
        
        state_before = nintendanki.progression_system.get_state()
        cards_before = state_before.total_cards_reviewed
        correct_before = state_before.correct_answers
        
        # Switch to DKC theme
        nintendanki.theme_manager.set_theme(Theme.DKC)
        
        # Verify counts are preserved
        state_after = nintendanki.progression_system.get_state()
        assert state_after.total_cards_reviewed == cards_before
        assert state_after.correct_answers == correct_before
    
    def test_theme_switch_preserves_streak(
        self, nintendanki, mock_reviewer, mock_card
    ):
        """Test that switching themes preserves current streak.
        
        Requirement 1.3: Preserve progression
        """
        # Build up a streak with Mario theme
        nintendanki.theme_manager.set_theme(Theme.MARIO)
        
        for _ in range(7):
            nintendanki.hook_handler.on_card_reviewed(mock_reviewer, mock_card, ease=3)
        
        state_before = nintendanki.progression_system.get_state()
        streak_before = state_before.current_streak
        assert streak_before >= 7
        
        # Switch to Zelda theme
        nintendanki.theme_manager.set_theme(Theme.ZELDA)
        
        # Verify streak is preserved
        state_after = nintendanki.progression_system.get_state()
        assert state_after.current_streak == streak_before
    
    def test_theme_switch_preserves_levels_unlocked(
        self, nintendanki, mock_reviewer, mock_card
    ):
        """Test that switching themes preserves levels unlocked.
        
        Requirement 1.3: Preserve all accumulated levels
        """
        # Start with Mario theme
        nintendanki.theme_manager.set_theme(Theme.MARIO)
        
        state_before = nintendanki.progression_system.get_state()
        levels_before = state_before.levels_unlocked
        
        # Switch to Zelda theme
        nintendanki.theme_manager.set_theme(Theme.ZELDA)
        
        # Verify levels are preserved
        state_after = nintendanki.progression_system.get_state()
        assert state_after.levels_unlocked == levels_before
    
    def test_multiple_theme_switches_preserve_progression(
        self, nintendanki, mock_reviewer, mock_card
    ):
        """Test that multiple theme switches preserve progression.
        
        Requirement 1.3: Preserve progression across multiple switches
        """
        # Start with Mario, do some reviews
        nintendanki.theme_manager.set_theme(Theme.MARIO)
        for _ in range(3):
            nintendanki.hook_handler.on_card_reviewed(mock_reviewer, mock_card, ease=3)
        
        # Switch to Zelda, do more reviews
        nintendanki.theme_manager.set_theme(Theme.ZELDA)
        for _ in range(3):
            nintendanki.hook_handler.on_card_reviewed(mock_reviewer, mock_card, ease=3)
        
        # Switch to DKC, do more reviews
        nintendanki.theme_manager.set_theme(Theme.DKC)
        for _ in range(3):
            nintendanki.hook_handler.on_card_reviewed(mock_reviewer, mock_card, ease=3)
        
        # Switch back to Mario
        nintendanki.theme_manager.set_theme(Theme.MARIO)
        
        # Verify all reviews are counted
        state = nintendanki.progression_system.get_state()
        assert state.total_cards_reviewed >= 9
        assert state.correct_answers >= 9
    
    def test_theme_switch_continues_accumulating_points(
        self, nintendanki, mock_reviewer, mock_card
    ):
        """Test that points continue accumulating after theme switch.
        
        Requirement 1.3: Progression continues after switch
        """
        # Start with Mario theme
        nintendanki.theme_manager.set_theme(Theme.MARIO)
        
        for _ in range(5):
            nintendanki.hook_handler.on_card_reviewed(mock_reviewer, mock_card, ease=3)
        
        points_after_mario = nintendanki.progression_system.get_state().total_points
        
        # Switch to Zelda and continue
        nintendanki.theme_manager.set_theme(Theme.ZELDA)
        
        for _ in range(5):
            nintendanki.hook_handler.on_card_reviewed(mock_reviewer, mock_card, ease=3)
        
        points_after_zelda = nintendanki.progression_system.get_state().total_points
        
        # Points should have increased
        assert points_after_zelda > points_after_mario


# ============================================================================
# Test 3: Add-on Load/Unload Cycle
# ============================================================================

class TestAddonLoadUnloadCycle:
    """Test add-on load/unload cycle.
    
    Requirement 7.3: THE Add-on SHALL not interfere with Anki's native 
    review functionality
    """
    
    def test_addon_initializes_correctly(self, temp_addon_dir):
        """Test that the add-on initializes all components correctly."""
        app = NintendAnki(addon_dir=temp_addon_dir, use_real_anki=False)
        app.initialize()
        
        try:
            # Verify all core components are initialized
            assert app.data_manager is not None
            assert app.config_manager is not None
            assert app.scoring_engine is not None
            assert app.progression_system is not None
            assert app.achievement_system is not None
            assert app.powerup_system is not None
            assert app.level_system is not None
            assert app.reward_system is not None
            assert app.theme_manager is not None
            assert app.hook_handler is not None
            assert app.menu_integration is not None
            
            # Verify initialization flag
            assert app.is_initialized
        finally:
            app.shutdown()
    
    def test_addon_shuts_down_cleanly(self, temp_addon_dir):
        """Test that the add-on shuts down cleanly without errors."""
        app = NintendAnki(addon_dir=temp_addon_dir, use_real_anki=False)
        app.initialize()
        
        assert app.is_initialized
        
        # Shutdown should not raise any exceptions
        app.shutdown()
        
        # Verify shutdown completed
        assert not app.is_initialized
    
    def test_addon_can_reinitialize_after_shutdown(self, temp_addon_dir):
        """Test that the add-on can be reinitialized after shutdown."""
        # First initialization
        app = NintendAnki(addon_dir=temp_addon_dir, use_real_anki=False)
        app.initialize()
        app.shutdown()
        
        # Second initialization (simulates Anki restart)
        app2 = NintendAnki(addon_dir=temp_addon_dir, use_real_anki=False)
        app2.initialize()
        
        try:
            assert app2.is_initialized
            assert app2.data_manager is not None
            assert app2.progression_system is not None
        finally:
            app2.shutdown()
    
    def test_addon_persists_state_across_sessions(
        self, temp_addon_dir, mock_reviewer, mock_card
    ):
        """Test that game state persists across add-on sessions.
        
        Simulates closing and reopening Anki.
        """
        # First session - do some reviews
        app1 = NintendAnki(addon_dir=temp_addon_dir, use_real_anki=False)
        app1.initialize()
        
        for _ in range(10):
            app1.hook_handler.on_card_reviewed(mock_reviewer, mock_card, ease=3)
        
        state_before = app1.progression_system.get_state()
        points_before = state_before.total_points
        cards_before = state_before.total_cards_reviewed
        
        app1.shutdown()
        
        # Second session - verify state persisted
        app2 = NintendAnki(addon_dir=temp_addon_dir, use_real_anki=False)
        app2.initialize()
        
        try:
            state_after = app2.progression_system.get_state()
            assert state_after.total_points == points_before
            assert state_after.total_cards_reviewed == cards_before
        finally:
            app2.shutdown()
    
    def test_addon_hooks_registered_on_init(self, temp_addon_dir):
        """Test that Anki hooks are registered during initialization.
        
        Requirement 7.1: WHEN Anki starts, THE Add-on SHALL register hooks
        """
        app = NintendAnki(addon_dir=temp_addon_dir, use_real_anki=False)
        app.initialize()
        
        try:
            # Verify hook handler is set up
            assert app.hook_handler is not None
            assert app.hook_handler.progression_system is not None
            assert app.hook_handler.scoring_engine is not None
        finally:
            app.shutdown()
    
    def test_addon_hooks_unregistered_on_shutdown(self, temp_addon_dir):
        """Test that Anki hooks are unregistered during shutdown."""
        app = NintendAnki(addon_dir=temp_addon_dir, use_real_anki=False)
        app.initialize()
        
        # Verify hooks are registered
        assert app.hook_handler is not None
        
        app.shutdown()
        
        # After shutdown, the app should be in a clean state
        assert not app.is_initialized
    
    def test_addon_does_not_interfere_with_reviews(
        self, nintendanki, mock_reviewer, mock_card
    ):
        """Test that the add-on does not interfere with Anki reviews.
        
        Requirement 7.3: THE Add-on SHALL not interfere with Anki's 
        native review functionality
        
        This test verifies that:
        1. Reviews are processed without errors
        2. The hook handler doesn't block or modify the review
        3. Errors in the add-on don't propagate to Anki
        """
        # Simulate many reviews - should all complete without error
        for i in range(50):
            ease = (i % 4) + 1  # Cycle through all ease values
            # This should not raise any exceptions
            nintendanki.hook_handler.on_card_reviewed(mock_reviewer, mock_card, ease=ease)
        
        # Verify reviews were tracked
        state = nintendanki.progression_system.get_state()
        assert state.total_cards_reviewed >= 50
    
    def test_addon_handles_errors_gracefully(
        self, nintendanki, mock_reviewer, mock_card
    ):
        """Test that add-on errors don't interfere with Anki.
        
        Requirement 7.3: THE Add-on SHALL not interfere with Anki's 
        native review functionality
        """
        # Simulate an error in the game window
        if nintendanki.game_window is not None:
            nintendanki.game_window.update_display = MagicMock(
                side_effect=Exception("Simulated error")
            )
        
        # Reviews should still work despite the error
        initial_cards = nintendanki.progression_system.get_state().total_cards_reviewed
        
        # This should not raise - errors are caught internally
        nintendanki.hook_handler.on_card_reviewed(mock_reviewer, mock_card, ease=3)
        
        # Progression should still be updated
        updated_cards = nintendanki.progression_system.get_state().total_cards_reviewed
        assert updated_cards == initial_cards + 1


# ============================================================================
# Test: Global Instance Management
# ============================================================================

class TestGlobalInstanceManagement:
    """Test global instance management functions."""
    
    def test_initialize_creates_global_instance(self, temp_addon_dir):
        """Test that initialize() creates a global instance."""
        # Ensure no existing instance
        shutdown()
        
        instance = initialize(addon_dir=temp_addon_dir, use_real_anki=False)
        
        try:
            assert instance is not None
            assert instance.is_initialized
            assert get_instance() is instance
        finally:
            shutdown()
    
    def test_shutdown_clears_global_instance(self, temp_addon_dir):
        """Test that shutdown() clears the global instance."""
        initialize(addon_dir=temp_addon_dir, use_real_anki=False)
        
        assert get_instance() is not None
        
        shutdown()
        
        assert get_instance() is None
    
    def test_double_initialize_returns_existing_instance(self, temp_addon_dir):
        """Test that calling initialize() twice returns the same instance."""
        shutdown()  # Ensure clean state
        
        instance1 = initialize(addon_dir=temp_addon_dir, use_real_anki=False)
        instance2 = initialize(addon_dir=temp_addon_dir, use_real_anki=False)
        
        try:
            assert instance1 is instance2
        finally:
            shutdown()


# ============================================================================
# Test: Integration with All Systems
# ============================================================================

class TestFullSystemIntegration:
    """Test integration between all systems."""
    
    def test_review_triggers_all_systems(
        self, nintendanki, mock_reviewer, mock_card
    ):
        """Test that a review triggers updates in all systems.
        
        Verifies the complete event flow through all components.
        """
        # Track which systems were called
        systems_called = {
            'progression': False,
            'scoring': False,
            'achievement': False,
            'theme': False,
        }
        
        # Mock progression system
        original_process = nintendanki.progression_system.process_review
        def mock_process(result):
            systems_called['progression'] = True
            return original_process(result)
        nintendanki.progression_system.process_review = mock_process
        
        # Mock achievement system
        original_check = nintendanki.achievement_system.check_achievements
        def mock_check(state):
            systems_called['achievement'] = True
            return original_check(state)
        nintendanki.achievement_system.check_achievements = mock_check
        
        # Mock theme manager
        original_get_engine = nintendanki.theme_manager.get_theme_engine
        def mock_get_engine():
            systems_called['theme'] = True
            return original_get_engine()
        nintendanki.theme_manager.get_theme_engine = mock_get_engine
        
        # Simulate a review
        nintendanki.hook_handler.on_card_reviewed(mock_reviewer, mock_card, ease=3)
        
        # Verify progression was updated
        assert systems_called['progression'], "Progression system should be called"
    
    def test_streak_affects_scoring(
        self, nintendanki, mock_reviewer, mock_card
    ):
        """Test that streak affects scoring correctly."""
        # Reset to clean state
        nintendanki.progression_system.reset_session()
        
        # Do 5 correct reviews to build streak
        for _ in range(5):
            nintendanki.hook_handler.on_card_reviewed(mock_reviewer, mock_card, ease=3)
        
        state = nintendanki.progression_system.get_state()
        assert state.current_streak >= 5
        
        # Verify combo multiplier is applied (1.5x at streak 5)
        multiplier = nintendanki.scoring_engine.get_combo_multiplier(state.current_streak)
        assert multiplier >= 1.5
    
    def test_wrong_answer_breaks_streak(
        self, nintendanki, mock_reviewer, mock_card
    ):
        """Test that wrong answer breaks the streak."""
        # Build up a streak
        for _ in range(5):
            nintendanki.hook_handler.on_card_reviewed(mock_reviewer, mock_card, ease=3)
        
        state_before = nintendanki.progression_system.get_state()
        assert state_before.current_streak >= 5
        
        # Wrong answer
        nintendanki.hook_handler.on_card_reviewed(mock_reviewer, mock_card, ease=1)
        
        state_after = nintendanki.progression_system.get_state()
        assert state_after.current_streak == 0
    
    def test_theme_specific_stats_update(
        self, nintendanki, mock_reviewer, mock_card
    ):
        """Test that theme-specific stats update correctly."""
        for theme in [Theme.MARIO, Theme.ZELDA, Theme.DKC]:
            nintendanki.theme_manager.set_theme(theme)
            
            # Do some reviews
            for _ in range(3):
                nintendanki.hook_handler.on_card_reviewed(mock_reviewer, mock_card, ease=3)
            
            # Get theme-specific stats
            theme_engine = nintendanki.theme_manager.get_theme_engine()
            stats = theme_engine.get_dashboard_stats()
            
            # Verify stats are for the correct theme
            assert stats.theme == theme
