"""
Tests for the HookHandler module.

This module contains unit tests for the HookHandler class, including tests for:
- Hook registration and unregistration
- Card review event processing
- Integration with ProgressionSystem and ScoringEngine
- Mock hook provider functionality

Requirements tested: 7.1, 7.2, 7.3
"""

import pytest
from unittest.mock import MagicMock
from pathlib import Path
import tempfile

from integration.hook_handler import (
    HookHandler,
    MockAnkiHookProvider,
    RealAnkiHookProvider,
)
from core.progression_system import ProgressionSystem
from core.scoring_engine import ScoringEngine
from data.data_manager import DataManager
from data.models import GameConfig, ReviewResult


# ============================================================================
# Fixtures
# ============================================================================

@pytest.fixture
def temp_db_path():
    """Create a temporary database path for testing."""
    with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as tmpdir:
        yield Path(tmpdir) / "test_game.db"


@pytest.fixture
def data_manager(temp_db_path):
    """Create a DataManager with a temporary database."""
    dm = DataManager(temp_db_path)
    dm.initialize_database()
    yield dm
    # Close the database connection to release the file lock
    dm.close()


@pytest.fixture
def game_config():
    """Create a default GameConfig for testing."""
    return GameConfig()


@pytest.fixture
def scoring_engine(game_config):
    """Create a ScoringEngine for testing."""
    return ScoringEngine(game_config)


@pytest.fixture
def progression_system(data_manager, scoring_engine, game_config):
    """Create a ProgressionSystem for testing."""
    return ProgressionSystem(data_manager, scoring_engine, game_config)


@pytest.fixture
def mock_hook_provider():
    """Create a MockAnkiHookProvider for testing."""
    return MockAnkiHookProvider()


@pytest.fixture
def hook_handler(progression_system, scoring_engine, mock_hook_provider):
    """Create a HookHandler with mock dependencies."""
    return HookHandler(progression_system, scoring_engine, mock_hook_provider)


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
# MockAnkiHookProvider Tests
# ============================================================================

class TestMockAnkiHookProvider:
    """Tests for the MockAnkiHookProvider class."""
    
    def test_add_hook_registers_callback(self, mock_hook_provider):
        """Test that add_hook registers a callback."""
        callback = MagicMock()
        mock_hook_provider.add_hook("test_hook", callback)
        
        assert mock_hook_provider.is_hook_registered("test_hook")
        assert callback in mock_hook_provider.get_registered_hooks()["test_hook"]
    
    def test_remove_hook_unregisters_callback(self, mock_hook_provider):
        """Test that remove_hook unregisters a callback."""
        callback = MagicMock()
        mock_hook_provider.add_hook("test_hook", callback)
        mock_hook_provider.remove_hook("test_hook", callback)
        
        assert not mock_hook_provider.is_hook_registered("test_hook")
    
    def test_fire_hook_calls_callbacks(self, mock_hook_provider):
        """Test that fire_hook calls all registered callbacks."""
        callback1 = MagicMock()
        callback2 = MagicMock()
        
        mock_hook_provider.add_hook("test_hook", callback1)
        mock_hook_provider.add_hook("test_hook", callback2)
        
        mock_hook_provider.fire_hook("test_hook", "arg1", kwarg1="value1")
        
        callback1.assert_called_once_with("arg1", kwarg1="value1")
        callback2.assert_called_once_with("arg1", kwarg1="value1")
    
    def test_fire_hook_handles_callback_errors(self, mock_hook_provider):
        """Test that fire_hook continues even if a callback raises an error."""
        callback1 = MagicMock(side_effect=Exception("Test error"))
        callback2 = MagicMock()
        
        mock_hook_provider.add_hook("test_hook", callback1)
        mock_hook_provider.add_hook("test_hook", callback2)
        
        # Should not raise
        mock_hook_provider.fire_hook("test_hook")
        
        # Second callback should still be called
        callback2.assert_called_once()
    
    def test_clear_all_hooks(self, mock_hook_provider):
        """Test that clear_all_hooks removes all registered hooks."""
        mock_hook_provider.add_hook("hook1", MagicMock())
        mock_hook_provider.add_hook("hook2", MagicMock())
        
        mock_hook_provider.clear_all_hooks()
        
        assert not mock_hook_provider.is_hook_registered("hook1")
        assert not mock_hook_provider.is_hook_registered("hook2")
    
    def test_remove_nonexistent_callback(self, mock_hook_provider):
        """Test that removing a nonexistent callback doesn't raise."""
        callback = MagicMock()
        # Should not raise
        mock_hook_provider.remove_hook("nonexistent_hook", callback)


# ============================================================================
# HookHandler Registration Tests (Requirement 7.1)
# ============================================================================

class TestHookHandlerRegistration:
    """Tests for hook registration functionality (Requirement 7.1)."""
    
    def test_register_hooks_registers_reviewer_hook(
        self, hook_handler, mock_hook_provider
    ):
        """Test that register_hooks registers the reviewer_did_answer_card hook.
        
        Requirement 7.1: Register hooks for card review events when Anki starts.
        """
        hook_handler.register_hooks()
        
        assert mock_hook_provider.is_hook_registered(
            HookHandler.HOOK_REVIEWER_DID_ANSWER_CARD
        )
    
    def test_register_hooks_sets_registered_flag(self, hook_handler):
        """Test that register_hooks sets the is_registered flag."""
        assert not hook_handler.is_registered
        
        hook_handler.register_hooks()
        
        assert hook_handler.is_registered
    
    def test_register_hooks_idempotent(self, hook_handler, mock_hook_provider):
        """Test that calling register_hooks twice doesn't duplicate registrations."""
        hook_handler.register_hooks()
        hook_handler.register_hooks()  # Second call should be ignored
        
        hooks = mock_hook_provider.get_registered_hooks()
        assert len(hooks[HookHandler.HOOK_REVIEWER_DID_ANSWER_CARD]) == 1
    
    def test_unregister_hooks_removes_reviewer_hook(
        self, hook_handler, mock_hook_provider
    ):
        """Test that unregister_hooks removes the reviewer_did_answer_card hook.
        
        Requirement 7.3: Clean shutdown without interference.
        """
        hook_handler.register_hooks()
        hook_handler.unregister_hooks()
        
        assert not mock_hook_provider.is_hook_registered(
            HookHandler.HOOK_REVIEWER_DID_ANSWER_CARD
        )
    
    def test_unregister_hooks_clears_registered_flag(self, hook_handler):
        """Test that unregister_hooks clears the is_registered flag."""
        hook_handler.register_hooks()
        hook_handler.unregister_hooks()
        
        assert not hook_handler.is_registered
    
    def test_unregister_hooks_when_not_registered(self, hook_handler):
        """Test that unregister_hooks handles not being registered gracefully."""
        # Should not raise
        hook_handler.unregister_hooks()
        assert not hook_handler.is_registered


# ============================================================================
# HookHandler Card Review Processing Tests (Requirement 7.2)
# ============================================================================

class TestHookHandlerCardReview:
    """Tests for card review processing (Requirement 7.2)."""
    
    def test_on_card_reviewed_correct_answer_updates_progression(
        self, hook_handler, progression_system, mock_reviewer, mock_card
    ):
        """Test that correct answers update the progression system.
        
        Requirement 7.2: Notify ProgressionSystem with review result.
        """
        initial_state = progression_system.get_state()
        initial_correct = initial_state.correct_answers
        initial_total = initial_state.total_cards_reviewed
        
        # Ease 3 = Good (correct)
        hook_handler.on_card_reviewed(mock_reviewer, mock_card, ease=3)
        
        updated_state = progression_system.get_state()
        assert updated_state.correct_answers == initial_correct + 1
        assert updated_state.total_cards_reviewed == initial_total + 1
    
    def test_on_card_reviewed_wrong_answer_updates_progression(
        self, hook_handler, progression_system, mock_reviewer, mock_card
    ):
        """Test that wrong answers update the progression system.
        
        Requirement 7.2: Notify ProgressionSystem with review result.
        """
        initial_state = progression_system.get_state()
        initial_correct = initial_state.correct_answers
        initial_total = initial_state.total_cards_reviewed
        
        # Ease 1 = Again (wrong)
        hook_handler.on_card_reviewed(mock_reviewer, mock_card, ease=1)
        
        updated_state = progression_system.get_state()
        assert updated_state.correct_answers == initial_correct  # No change
        assert updated_state.total_cards_reviewed == initial_total + 1
    
    def test_on_card_reviewed_ease_3_is_correct(
        self, hook_handler, progression_system, mock_reviewer, mock_card
    ):
        """Test that ease=3 (Good) is treated as correct."""
        initial_correct = progression_system.get_state().correct_answers
        
        hook_handler.on_card_reviewed(mock_reviewer, mock_card, ease=3)
        
        assert progression_system.get_state().correct_answers == initial_correct + 1
    
    def test_on_card_reviewed_ease_4_is_correct(
        self, hook_handler, progression_system, mock_reviewer, mock_card
    ):
        """Test that ease=4 (Easy) is treated as correct."""
        initial_correct = progression_system.get_state().correct_answers
        
        hook_handler.on_card_reviewed(mock_reviewer, mock_card, ease=4)
        
        assert progression_system.get_state().correct_answers == initial_correct + 1
    
    def test_on_card_reviewed_ease_1_is_wrong(
        self, hook_handler, progression_system, mock_reviewer, mock_card
    ):
        """Test that ease=1 (Again) is treated as wrong."""
        initial_correct = progression_system.get_state().correct_answers
        
        hook_handler.on_card_reviewed(mock_reviewer, mock_card, ease=1)
        
        assert progression_system.get_state().correct_answers == initial_correct
    
    def test_on_card_reviewed_ease_2_is_wrong(
        self, hook_handler, progression_system, mock_reviewer, mock_card
    ):
        """Test that ease=2 (Hard) is treated as wrong."""
        initial_correct = progression_system.get_state().correct_answers
        
        hook_handler.on_card_reviewed(mock_reviewer, mock_card, ease=2)
        
        assert progression_system.get_state().correct_answers == initial_correct
    
    def test_on_card_reviewed_updates_points(
        self, hook_handler, progression_system, mock_reviewer, mock_card
    ):
        """Test that correct answers add points."""
        initial_points = progression_system.get_state().total_points
        
        hook_handler.on_card_reviewed(mock_reviewer, mock_card, ease=3)
        
        assert progression_system.get_state().total_points > initial_points
    
    def test_on_card_reviewed_updates_streak(
        self, hook_handler, progression_system, mock_reviewer, mock_card
    ):
        """Test that correct answers update the streak."""
        initial_streak = progression_system.get_state().current_streak
        
        hook_handler.on_card_reviewed(mock_reviewer, mock_card, ease=3)
        
        assert progression_system.get_state().current_streak == initial_streak + 1
    
    def test_on_card_reviewed_wrong_answer_resets_streak(
        self, hook_handler, progression_system, mock_reviewer, mock_card
    ):
        """Test that wrong answers reset the streak."""
        # Build up a streak
        hook_handler.on_card_reviewed(mock_reviewer, mock_card, ease=3)
        hook_handler.on_card_reviewed(mock_reviewer, mock_card, ease=3)
        assert progression_system.get_state().current_streak == 2
        
        # Wrong answer resets streak
        hook_handler.on_card_reviewed(mock_reviewer, mock_card, ease=1)
        assert progression_system.get_state().current_streak == 0


# ============================================================================
# HookHandler Non-Interference Tests (Requirement 7.3)
# ============================================================================

class TestHookHandlerNonInterference:
    """Tests for non-interference with Anki (Requirement 7.3)."""
    
    def test_on_card_reviewed_handles_errors_gracefully(
        self, hook_handler, mock_reviewer, mock_card
    ):
        """Test that errors in processing don't propagate.
        
        Requirement 7.3: Not interfere with Anki's native functionality.
        """
        # Make progression_system.process_review raise an error
        hook_handler.progression_system.process_review = MagicMock(
            side_effect=Exception("Test error")
        )
        
        # Should not raise - errors are caught and logged
        hook_handler.on_card_reviewed(mock_reviewer, mock_card, ease=3)
    
    def test_on_card_reviewed_handles_missing_card_attributes(
        self, hook_handler, mock_reviewer
    ):
        """Test that missing card attributes are handled gracefully.
        
        Requirement 7.3: Not interfere with Anki's native functionality.
        """
        # Card with no attributes
        empty_card = object()
        
        # Should not raise
        hook_handler.on_card_reviewed(mock_reviewer, empty_card, ease=3)
    
    def test_on_card_reviewed_handles_dict_card(
        self, hook_handler, progression_system, mock_reviewer
    ):
        """Test that dict-style cards are handled correctly."""
        dict_card = {
            'id': 99999,
            'did': 2,
            'ivl': 7,
            'reps': 10,
            'lapses': 1
        }
        
        initial_total = progression_system.get_state().total_cards_reviewed
        
        hook_handler.on_card_reviewed(mock_reviewer, dict_card, ease=3)
        
        assert progression_system.get_state().total_cards_reviewed == initial_total + 1


# ============================================================================
# HookHandler Callback Tests
# ============================================================================

class TestHookHandlerCallbacks:
    """Tests for review callback functionality."""
    
    def test_add_review_callback(self, hook_handler, mock_reviewer, mock_card):
        """Test that review callbacks are called on card review."""
        callback = MagicMock()
        hook_handler.add_review_callback(callback)
        
        hook_handler.on_card_reviewed(mock_reviewer, mock_card, ease=3)
        
        callback.assert_called_once()
        # Verify the callback received a ReviewResult
        call_args = callback.call_args[0]
        assert isinstance(call_args[0], ReviewResult)
    
    def test_remove_review_callback(self, hook_handler, mock_reviewer, mock_card):
        """Test that removed callbacks are not called."""
        callback = MagicMock()
        hook_handler.add_review_callback(callback)
        hook_handler.remove_review_callback(callback)
        
        hook_handler.on_card_reviewed(mock_reviewer, mock_card, ease=3)
        
        callback.assert_not_called()
    
    def test_multiple_review_callbacks(self, hook_handler, mock_reviewer, mock_card):
        """Test that multiple callbacks are all called."""
        callback1 = MagicMock()
        callback2 = MagicMock()
        
        hook_handler.add_review_callback(callback1)
        hook_handler.add_review_callback(callback2)
        
        hook_handler.on_card_reviewed(mock_reviewer, mock_card, ease=3)
        
        callback1.assert_called_once()
        callback2.assert_called_once()
    
    def test_callback_error_doesnt_stop_other_callbacks(
        self, hook_handler, mock_reviewer, mock_card
    ):
        """Test that callback errors don't prevent other callbacks from running."""
        callback1 = MagicMock(side_effect=Exception("Test error"))
        callback2 = MagicMock()
        
        hook_handler.add_review_callback(callback1)
        hook_handler.add_review_callback(callback2)
        
        hook_handler.on_card_reviewed(mock_reviewer, mock_card, ease=3)
        
        # Second callback should still be called
        callback2.assert_called_once()
    
    def test_add_same_callback_twice(self, hook_handler, mock_reviewer, mock_card):
        """Test that adding the same callback twice doesn't duplicate it."""
        callback = MagicMock()
        hook_handler.add_review_callback(callback)
        hook_handler.add_review_callback(callback)  # Should be ignored
        
        hook_handler.on_card_reviewed(mock_reviewer, mock_card, ease=3)
        
        # Should only be called once
        callback.assert_called_once()
    
    def test_remove_nonexistent_callback(self, hook_handler):
        """Test that removing a nonexistent callback doesn't raise."""
        callback = MagicMock()
        # Should not raise
        hook_handler.remove_review_callback(callback)


# ============================================================================
# HookHandler Integration Tests
# ============================================================================

class TestHookHandlerIntegration:
    """Integration tests for HookHandler with mock hook provider."""
    
    def test_hook_fires_on_card_reviewed(
        self, hook_handler, mock_hook_provider, mock_reviewer, mock_card
    ):
        """Test that firing the hook triggers on_card_reviewed."""
        hook_handler.register_hooks()
        
        initial_total = hook_handler.progression_system.get_state().total_cards_reviewed
        
        # Simulate Anki firing the hook
        mock_hook_provider.fire_hook(
            HookHandler.HOOK_REVIEWER_DID_ANSWER_CARD,
            mock_reviewer,
            mock_card,
            3  # ease
        )
        
        assert hook_handler.progression_system.get_state().total_cards_reviewed == initial_total + 1
    
    def test_full_review_cycle(
        self, hook_handler, mock_hook_provider, mock_reviewer, mock_card
    ):
        """Test a full cycle of registering, reviewing, and unregistering."""
        # Register hooks
        hook_handler.register_hooks()
        assert hook_handler.is_registered
        
        # Simulate multiple reviews
        for ease in [3, 4, 3, 1, 3]:  # Mix of correct and wrong
            mock_hook_provider.fire_hook(
                HookHandler.HOOK_REVIEWER_DID_ANSWER_CARD,
                mock_reviewer,
                mock_card,
                ease
            )
        
        state = hook_handler.progression_system.get_state()
        assert state.total_cards_reviewed == 5
        assert state.correct_answers == 4  # 3 correct (ease 3, 4, 3, 3)
        
        # Unregister hooks
        hook_handler.unregister_hooks()
        assert not hook_handler.is_registered
        
        # Firing hook after unregister should not process
        initial_total = state.total_cards_reviewed
        mock_hook_provider.fire_hook(
            HookHandler.HOOK_REVIEWER_DID_ANSWER_CARD,
            mock_reviewer,
            mock_card,
            3
        )
        # Total should not change since hook was unregistered
        assert hook_handler.progression_system.get_state().total_cards_reviewed == initial_total


# ============================================================================
# RealAnkiHookProvider Tests
# ============================================================================

class TestRealAnkiHookProvider:
    """Tests for RealAnkiHookProvider (limited without Anki)."""
    
    def test_real_provider_raises_without_anki(self):
        """Test that RealAnkiHookProvider raises when Anki is not available."""
        with pytest.raises(RuntimeError, match="Cannot create RealAnkiHookProvider"):
            RealAnkiHookProvider()


# ============================================================================
# HookHandler Default Provider Tests
# ============================================================================

class TestHookHandlerDefaultProvider:
    """Tests for HookHandler with default provider."""
    
    def test_default_provider_is_mock(self, progression_system, scoring_engine):
        """Test that HookHandler uses MockAnkiHookProvider by default."""
        handler = HookHandler(progression_system, scoring_engine)
        
        assert isinstance(handler.hook_provider, MockAnkiHookProvider)
