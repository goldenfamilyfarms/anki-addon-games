"""
Integration tests for the event flow from review to UI.

This module tests the complete event flow:
1. Card review happens in Anki
2. HookHandler receives the event
3. HookHandler notifies ProgressionSystem and ScoringEngine
4. ProgressionSystem updates state
5. ThemeManager provides theme-specific animations
6. GameWindow displays the animation

Requirements tested: 7.2, 7.4
"""

import pytest
from unittest.mock import MagicMock, patch
from pathlib import Path
import tempfile

from main import NintendAnki
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
# Event Flow Tests (Requirements 7.2, 7.4)
# ============================================================================

class TestEventFlowHookToProgression:
    """Tests for event flow from HookHandler to ProgressionSystem (Requirement 7.2)."""
    
    def test_hook_handler_connected_to_progression_system(self, nintendanki):
        """Test that HookHandler is connected to ProgressionSystem.
        
        Requirement 7.2: WHEN a Card_Review is completed, THE Anki_Hook SHALL 
        notify the Progression_System with the review result.
        """
        assert nintendanki.hook_handler is not None
        assert nintendanki.hook_handler.progression_system is nintendanki.progression_system
    
    def test_hook_handler_connected_to_scoring_engine(self, nintendanki):
        """Test that HookHandler is connected to ScoringEngine."""
        assert nintendanki.hook_handler is not None
        assert nintendanki.hook_handler.scoring_engine is nintendanki.scoring_engine
    
    def test_card_review_updates_progression(
        self, nintendanki, mock_reviewer, mock_card
    ):
        """Test that card review updates progression state.
        
        Requirement 7.2: Notify ProgressionSystem with review result.
        """
        initial_state = nintendanki.progression_system.get_state()
        initial_total = initial_state.total_cards_reviewed
        initial_correct = initial_state.correct_answers
        
        # Simulate a correct card review
        nintendanki.hook_handler.on_card_reviewed(mock_reviewer, mock_card, ease=3)
        
        updated_state = nintendanki.progression_system.get_state()
        assert updated_state.total_cards_reviewed == initial_total + 1
        assert updated_state.correct_answers == initial_correct + 1
    
    def test_card_review_updates_points(
        self, nintendanki, mock_reviewer, mock_card
    ):
        """Test that correct card review adds points."""
        initial_points = nintendanki.progression_system.get_state().total_points
        
        nintendanki.hook_handler.on_card_reviewed(mock_reviewer, mock_card, ease=3)
        
        updated_points = nintendanki.progression_system.get_state().total_points
        assert updated_points > initial_points


class TestEventFlowProgressionToTheme:
    """Tests for event flow from ProgressionSystem to ThemeManager."""
    
    def test_theme_manager_connected_to_progression_system(self, nintendanki):
        """Test that ThemeManager is connected to ProgressionSystem."""
        assert nintendanki.theme_manager is not None
        assert nintendanki.theme_manager._progression_system is nintendanki.progression_system
    
    def test_theme_engine_provides_correct_animation(self, nintendanki):
        """Test that ThemeEngine provides correct animation for correct answer."""
        theme_engine = nintendanki.theme_manager.get_theme_engine()
        animation = theme_engine.get_animation_for_correct()
        
        assert animation is not None
        assert animation.type == AnimationType.COLLECT
    
    def test_theme_engine_provides_wrong_animation(self, nintendanki):
        """Test that ThemeEngine provides damage animation for wrong answer."""
        theme_engine = nintendanki.theme_manager.get_theme_engine()
        animation = theme_engine.get_animation_for_wrong()
        
        assert animation is not None
        assert animation.type == AnimationType.DAMAGE


class TestEventFlowThemeToGameWindow:
    """Tests for event flow from ThemeManager to GameWindow."""
    
    def test_game_window_receives_state_updates(
        self, nintendanki, mock_reviewer, mock_card
    ):
        """Test that GameWindow receives state updates on card review.
        
        Requirement 7.4: WHEN the user is in review mode, THE Game_Window 
        SHALL update in real-time based on review results.
        """
        if nintendanki.game_window is None:
            pytest.skip("GameWindow not available (PyQt not installed)")
        
        # Mock the update_display method to track calls
        original_update = nintendanki.game_window.update_display
        update_calls = []
        
        def mock_update(state):
            update_calls.append(state)
            return original_update(state)
        
        nintendanki.game_window.update_display = mock_update
        
        # Simulate a card review
        nintendanki.hook_handler.on_card_reviewed(mock_reviewer, mock_card, ease=3)
        
        # Verify update_display was called
        assert len(update_calls) > 0
        assert update_calls[0].total_cards_reviewed > 0
    
    def test_game_window_receives_animations(
        self, nintendanki, mock_reviewer, mock_card
    ):
        """Test that GameWindow receives animations on card review.
        
        Requirement 7.4: Game_Window SHALL update in real-time.
        """
        if nintendanki.game_window is None:
            pytest.skip("GameWindow not available (PyQt not installed)")
        
        # Mock the show_animation method to track calls
        original_show = nintendanki.game_window.show_animation
        animation_calls = []
        
        def mock_show(animation):
            animation_calls.append(animation)
            return original_show(animation)
        
        nintendanki.game_window.show_animation = mock_show
        
        # Simulate a correct card review
        nintendanki.hook_handler.on_card_reviewed(mock_reviewer, mock_card, ease=3)
        
        # Verify show_animation was called with correct animation type
        assert len(animation_calls) > 0
        assert animation_calls[0].type == AnimationType.COLLECT
    
    def test_game_window_receives_wrong_animation(
        self, nintendanki, mock_reviewer, mock_card
    ):
        """Test that GameWindow receives damage animation for wrong answer."""
        if nintendanki.game_window is None:
            pytest.skip("GameWindow not available (PyQt not installed)")
        
        # Mock the show_animation method
        animation_calls = []
        original_show = nintendanki.game_window.show_animation
        
        def mock_show(animation):
            animation_calls.append(animation)
            return original_show(animation)
        
        nintendanki.game_window.show_animation = mock_show
        
        # Simulate a wrong card review (ease=1 is "Again")
        nintendanki.hook_handler.on_card_reviewed(mock_reviewer, mock_card, ease=1)
        
        # Verify show_animation was called with damage animation type
        assert len(animation_calls) > 0
        assert animation_calls[0].type == AnimationType.DAMAGE


class TestEventFlowThemeSwitching:
    """Tests for theme switching event flow."""
    
    def test_theme_switch_updates_game_window(self, nintendanki):
        """Test that theme switch updates GameWindow."""
        if nintendanki.game_window is None:
            pytest.skip("GameWindow not available (PyQt not installed)")
        
        # Get initial theme
        initial_theme = nintendanki.theme_manager.get_current_theme()
        
        # Switch to a different theme
        new_theme = Theme.ZELDA if initial_theme != Theme.ZELDA else Theme.MARIO
        nintendanki.theme_manager.set_theme(new_theme)
        
        # Verify GameWindow theme was updated
        assert nintendanki.game_window.get_current_theme() == new_theme
    
    def test_theme_switch_preserves_progression(self, nintendanki, mock_reviewer, mock_card):
        """Test that theme switch preserves progression state.
        
        Requirement 1.3: Theme switching preserves progression.
        """
        # Build up some progression
        for _ in range(5):
            nintendanki.hook_handler.on_card_reviewed(mock_reviewer, mock_card, ease=3)
        
        state_before = nintendanki.progression_system.get_state()
        points_before = state_before.total_points
        cards_before = state_before.total_cards_reviewed
        
        # Switch theme
        current_theme = nintendanki.theme_manager.get_current_theme()
        new_theme = Theme.DKC if current_theme != Theme.DKC else Theme.MARIO
        nintendanki.theme_manager.set_theme(new_theme)
        
        # Verify progression is preserved
        state_after = nintendanki.progression_system.get_state()
        assert state_after.total_points == points_before
        assert state_after.total_cards_reviewed == cards_before


class TestEventFlowDashboardUpdates:
    """Tests for Dashboard update event flow."""
    
    def test_dashboard_receives_updates(
        self, nintendanki, mock_reviewer, mock_card
    ):
        """Test that Dashboard receives updates on card review.
        
        Requirement 10.7: Dashboard updates in real-time.
        """
        if nintendanki.dashboard is None:
            pytest.skip("Dashboard not available (PyQt not installed)")
        
        # Mock the refresh method to track calls
        refresh_calls = []
        original_refresh = nintendanki.dashboard.refresh
        
        def mock_refresh():
            refresh_calls.append(True)
            return original_refresh()
        
        nintendanki.dashboard.refresh = mock_refresh
        
        # Simulate a card review
        nintendanki.hook_handler.on_card_reviewed(mock_reviewer, mock_card, ease=3)
        
        # Verify refresh was called
        assert len(refresh_calls) > 0


class TestEventFlowAchievementsAndUnlocks:
    """Tests for achievement and unlock event flow."""
    
    def test_achievements_checked_on_review(
        self, nintendanki, mock_reviewer, mock_card
    ):
        """Test that achievements are checked after each review."""
        # Mock check_achievements to track calls
        check_calls = []
        original_check = nintendanki.achievement_system.check_achievements
        
        def mock_check(state):
            check_calls.append(state)
            return original_check(state)
        
        nintendanki.achievement_system.check_achievements = mock_check
        
        # Simulate a card review
        nintendanki.hook_handler.on_card_reviewed(mock_reviewer, mock_card, ease=3)
        
        # Verify check_achievements was called (may be called multiple times)
        # At minimum once from the game window callback
        assert len(check_calls) >= 1
    
    def test_level_unlock_checked_on_review(
        self, nintendanki, mock_reviewer, mock_card
    ):
        """Test that level unlocks are checked after each review."""
        # Mock check_level_unlock to track calls
        check_calls = []
        original_check = nintendanki.progression_system.check_level_unlock
        
        def mock_check():
            check_calls.append(True)
            return original_check()
        
        nintendanki.progression_system.check_level_unlock = mock_check
        
        # Simulate a card review
        nintendanki.hook_handler.on_card_reviewed(mock_reviewer, mock_card, ease=3)
        
        # Verify check_level_unlock was called
        assert len(check_calls) >= 1
    
    def test_powerup_grant_checked_on_review(
        self, nintendanki, mock_reviewer, mock_card
    ):
        """Test that power-up grants are checked after each review."""
        # Mock check_powerup_grant to track calls
        check_calls = []
        original_check = nintendanki.progression_system.check_powerup_grant
        
        def mock_check():
            check_calls.append(True)
            return original_check()
        
        nintendanki.progression_system.check_powerup_grant = mock_check
        
        # Simulate a card review
        nintendanki.hook_handler.on_card_reviewed(mock_reviewer, mock_card, ease=3)
        
        # Verify check_powerup_grant was called
        assert len(check_calls) >= 1


class TestEventFlowErrorHandling:
    """Tests for error handling in event flow."""
    
    def test_game_window_error_doesnt_break_flow(
        self, nintendanki, mock_reviewer, mock_card
    ):
        """Test that errors in GameWindow don't break the event flow."""
        if nintendanki.game_window is None:
            pytest.skip("GameWindow not available (PyQt not installed)")
        
        # Make update_display raise an error
        nintendanki.game_window.update_display = MagicMock(
            side_effect=Exception("Test error")
        )
        
        initial_total = nintendanki.progression_system.get_state().total_cards_reviewed
        
        # Should not raise - errors are caught
        nintendanki.hook_handler.on_card_reviewed(mock_reviewer, mock_card, ease=3)
        
        # Progression should still be updated
        assert nintendanki.progression_system.get_state().total_cards_reviewed == initial_total + 1
    
    def test_dashboard_error_doesnt_break_flow(
        self, nintendanki, mock_reviewer, mock_card
    ):
        """Test that errors in Dashboard don't break the event flow."""
        if nintendanki.dashboard is None:
            pytest.skip("Dashboard not available (PyQt not installed)")
        
        # Make refresh raise an error
        nintendanki.dashboard.refresh = MagicMock(
            side_effect=Exception("Test error")
        )
        
        initial_total = nintendanki.progression_system.get_state().total_cards_reviewed
        
        # Should not raise - errors are caught
        nintendanki.hook_handler.on_card_reviewed(mock_reviewer, mock_card, ease=3)
        
        # Progression should still be updated
        assert nintendanki.progression_system.get_state().total_cards_reviewed == initial_total + 1


class TestCompleteEventFlow:
    """End-to-end tests for the complete event flow."""
    
    def test_complete_review_cycle(
        self, nintendanki, mock_reviewer, mock_card
    ):
        """Test a complete review cycle through all components.
        
        This test verifies the complete event flow:
        1. HookHandler receives review event
        2. ProgressionSystem updates state
        3. ScoringEngine calculates score
        4. ThemeManager provides animation
        5. GameWindow displays animation (if available)
        6. Dashboard refreshes (if available)
        7. Achievements/unlocks are checked
        
        Requirements: 7.2, 7.4
        """
        # Track all component interactions
        interactions = {
            'progression_updated': False,
            'theme_engine_called': False,
            'game_window_updated': False,
            'dashboard_refreshed': False,
            'achievements_checked': False,
        }
        
        # Mock ProgressionSystem.process_review
        original_process = nintendanki.progression_system.process_review
        def mock_process(result):
            interactions['progression_updated'] = True
            return original_process(result)
        nintendanki.progression_system.process_review = mock_process
        
        # Mock ThemeManager.get_theme_engine
        original_get_engine = nintendanki.theme_manager.get_theme_engine
        def mock_get_engine():
            interactions['theme_engine_called'] = True
            return original_get_engine()
        nintendanki.theme_manager.get_theme_engine = mock_get_engine
        
        # Mock GameWindow.update_display if available
        if nintendanki.game_window is not None:
            original_update = nintendanki.game_window.update_display
            def mock_update(state):
                interactions['game_window_updated'] = True
                return original_update(state)
            nintendanki.game_window.update_display = mock_update
        
        # Mock Dashboard.refresh if available
        if nintendanki.dashboard is not None:
            original_refresh = nintendanki.dashboard.refresh
            def mock_refresh():
                interactions['dashboard_refreshed'] = True
                return original_refresh()
            nintendanki.dashboard.refresh = mock_refresh
        
        # Mock AchievementSystem.check_achievements
        original_check = nintendanki.achievement_system.check_achievements
        def mock_check(state):
            interactions['achievements_checked'] = True
            return original_check(state)
        nintendanki.achievement_system.check_achievements = mock_check
        
        # Simulate a card review
        nintendanki.hook_handler.on_card_reviewed(mock_reviewer, mock_card, ease=3)
        
        # Verify all components were involved
        assert interactions['progression_updated'], "ProgressionSystem should be updated"
        
        # Theme engine and game window are only called if game_window exists
        if nintendanki.game_window is not None:
            assert interactions['theme_engine_called'], "ThemeManager should provide animation"
            assert interactions['game_window_updated'], "GameWindow should be updated"
            assert interactions['achievements_checked'], "Achievements should be checked"
        
        if nintendanki.dashboard is not None:
            assert interactions['dashboard_refreshed'], "Dashboard should be refreshed"
    
    def test_multiple_reviews_accumulate(
        self, nintendanki, mock_reviewer, mock_card
    ):
        """Test that multiple reviews accumulate correctly."""
        initial_state = nintendanki.progression_system.get_state()
        initial_total = initial_state.total_cards_reviewed
        initial_correct = initial_state.correct_answers
        initial_points = initial_state.total_points
        
        # Simulate 10 reviews (7 correct, 3 wrong)
        for i in range(10):
            ease = 3 if i < 7 else 1  # First 7 correct, last 3 wrong
            nintendanki.hook_handler.on_card_reviewed(mock_reviewer, mock_card, ease=ease)
        
        final_state = nintendanki.progression_system.get_state()
        
        assert final_state.total_cards_reviewed == initial_total + 10
        assert final_state.correct_answers == initial_correct + 7
        assert final_state.total_points > initial_points
