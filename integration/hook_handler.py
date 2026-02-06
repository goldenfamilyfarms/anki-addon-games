"""
HookHandler for NintendAnki.

This module implements the HookHandler class that handles Anki hook events
and dispatches them to the game systems (ProgressionSystem and ScoringEngine).

The HookHandler provides a mock-friendly interface that can be tested without
Anki running by using dependency injection for the hook registration system.

Requirements: 7.1, 7.2, 7.3
"""

from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional, Protocol
import logging

from core.progression_system import ProgressionSystem
from core.scoring_engine import ScoringEngine
from data.models import ReviewResult


# Set up logging
logger = logging.getLogger(__name__)


class AnkiHookProvider(Protocol):
    """Protocol for Anki hook registration.
    
    This protocol defines the interface for registering and unregistering
    hooks with Anki. It allows for dependency injection of the actual
    Anki hook system or a mock for testing.
    """
    
    def add_hook(self, hook_name: str, callback: Callable) -> None:
        """Register a callback for a hook.
        
        Args:
            hook_name: Name of the Anki hook to register for
            callback: Function to call when the hook fires
        """
        ...
    
    def remove_hook(self, hook_name: str, callback: Callable) -> None:
        """Unregister a callback from a hook.
        
        Args:
            hook_name: Name of the Anki hook to unregister from
            callback: Function to remove from the hook
        """
        ...


class RealAnkiHookProvider:
    """Real Anki hook provider that uses aqt.gui_hooks.
    
    This class wraps the actual Anki hook system for production use.
    It should only be instantiated when running inside Anki.
    """
    
    def __init__(self):
        """Initialize the real Anki hook provider."""
        try:
            from aqt import gui_hooks
            self._gui_hooks = gui_hooks
        except ImportError:
            raise RuntimeError(
                "Cannot create RealAnkiHookProvider outside of Anki. "
                "Use MockAnkiHookProvider for testing."
            )
    
    def add_hook(self, hook_name: str, callback: Callable) -> None:
        """Register a callback for an Anki hook.
        
        Args:
            hook_name: Name of the Anki hook (e.g., 'reviewer_did_answer_card')
            callback: Function to call when the hook fires
        """
        hook = getattr(self._gui_hooks, hook_name, None)
        if hook is not None:
            hook.append(callback)
            logger.info(f"Registered hook: {hook_name}")
        else:
            logger.warning(f"Hook not found: {hook_name}")
    
    def remove_hook(self, hook_name: str, callback: Callable) -> None:
        """Unregister a callback from an Anki hook.
        
        Args:
            hook_name: Name of the Anki hook
            callback: Function to remove from the hook
        """
        hook = getattr(self._gui_hooks, hook_name, None)
        if hook is not None:
            try:
                hook.remove(callback)
                logger.info(f"Unregistered hook: {hook_name}")
            except ValueError:
                logger.warning(f"Callback not found in hook: {hook_name}")
        else:
            logger.warning(f"Hook not found: {hook_name}")


class MockAnkiHookProvider:
    """Mock Anki hook provider for testing.
    
    This class provides a mock implementation of the Anki hook system
    that can be used for testing without Anki running.
    """
    
    def __init__(self):
        """Initialize the mock hook provider."""
        self._hooks: Dict[str, List[Callable]] = {}
    
    def add_hook(self, hook_name: str, callback: Callable) -> None:
        """Register a callback for a mock hook.
        
        Args:
            hook_name: Name of the hook
            callback: Function to register
        """
        if hook_name not in self._hooks:
            self._hooks[hook_name] = []
        self._hooks[hook_name].append(callback)
        logger.debug(f"Mock: Registered hook: {hook_name}")
    
    def remove_hook(self, hook_name: str, callback: Callable) -> None:
        """Unregister a callback from a mock hook.
        
        Args:
            hook_name: Name of the hook
            callback: Function to unregister
        """
        if hook_name in self._hooks:
            try:
                self._hooks[hook_name].remove(callback)
                logger.debug(f"Mock: Unregistered hook: {hook_name}")
            except ValueError:
                logger.debug(f"Mock: Callback not found in hook: {hook_name}")
    
    def fire_hook(self, hook_name: str, *args, **kwargs) -> None:
        """Fire a mock hook with the given arguments.
        
        This method is used in tests to simulate Anki hook events.
        
        Args:
            hook_name: Name of the hook to fire
            *args: Positional arguments to pass to callbacks
            **kwargs: Keyword arguments to pass to callbacks
        """
        if hook_name in self._hooks:
            for callback in self._hooks[hook_name]:
                try:
                    callback(*args, **kwargs)
                except Exception as e:
                    logger.error(f"Error in hook callback: {e}")
    
    def get_registered_hooks(self) -> Dict[str, List[Callable]]:
        """Get all registered hooks and their callbacks.
        
        Returns:
            Dictionary mapping hook names to lists of callbacks
        """
        return self._hooks.copy()
    
    def is_hook_registered(self, hook_name: str) -> bool:
        """Check if a hook has any registered callbacks.
        
        Args:
            hook_name: Name of the hook to check
            
        Returns:
            True if the hook has registered callbacks
        """
        return hook_name in self._hooks and len(self._hooks[hook_name]) > 0
    
    def clear_all_hooks(self) -> None:
        """Clear all registered hooks."""
        self._hooks.clear()


class HookHandler:
    """Handles Anki hook events and dispatches to game systems.
    
    The HookHandler is responsible for:
    - Registering hooks for Anki's card review events (Requirement 7.1)
    - Processing card review results and dispatching to ProgressionSystem (Requirement 7.2)
    - Unregistering hooks cleanly when the add-on unloads
    - Not interfering with Anki's native review functionality (Requirement 7.3)
    
    The handler uses dependency injection for the hook provider, allowing
    for easy testing with a mock provider.
    
    Attributes:
        progression_system: ProgressionSystem for updating game progression
        scoring_engine: ScoringEngine for calculating scores
        hook_provider: Provider for hook registration (real or mock)
        _hooks_registered: Whether hooks are currently registered
        _review_callbacks: List of additional callbacks to notify on review
    """
    
    # Anki hook names used by this handler
    HOOK_REVIEWER_DID_ANSWER_CARD = "reviewer_did_answer_card"
    
    def __init__(
        self,
        progression_system: ProgressionSystem,
        scoring_engine: ScoringEngine,
        hook_provider: Optional[AnkiHookProvider] = None
    ):
        """Initialize the HookHandler.
        
        Args:
            progression_system: ProgressionSystem for updating game progression
            scoring_engine: ScoringEngine for calculating scores
            hook_provider: Optional hook provider (uses MockAnkiHookProvider if None)
        """
        self.progression_system = progression_system
        self.scoring_engine = scoring_engine
        self.hook_provider = hook_provider or MockAnkiHookProvider()
        self._hooks_registered = False
        self._review_callbacks: List[Callable[[ReviewResult], None]] = []
        
        logger.info("HookHandler initialized")
    
    def register_hooks(self) -> None:
        """Register all Anki hooks for card review events.
        
        This method registers the handler's callbacks with Anki's hook system.
        It should be called when the add-on loads.
        
        The handler registers for the 'reviewer_did_answer_card' hook which
        fires after each card review is completed.
        
        Requirements: 7.1
        """
        if self._hooks_registered:
            logger.warning("Hooks already registered, skipping")
            return
        
        # Register for card review completion
        self.hook_provider.add_hook(
            self.HOOK_REVIEWER_DID_ANSWER_CARD,
            self._on_reviewer_did_answer_card
        )
        
        self._hooks_registered = True
        logger.info("Hooks registered successfully")
    
    def unregister_hooks(self) -> None:
        """Unregister all hooks on add-on unload.
        
        This method removes all registered callbacks from Anki's hook system.
        It should be called when the add-on unloads to ensure clean shutdown.
        
        Requirements: 7.3 (clean shutdown without interference)
        """
        if not self._hooks_registered:
            logger.warning("Hooks not registered, nothing to unregister")
            return
        
        # Unregister from card review completion
        self.hook_provider.remove_hook(
            self.HOOK_REVIEWER_DID_ANSWER_CARD,
            self._on_reviewer_did_answer_card
        )
        
        self._hooks_registered = False
        logger.info("Hooks unregistered successfully")
    
    def on_card_reviewed(self, reviewer: Any, card: Any, ease: int) -> None:
        """Called when a card review is completed.
        
        This is the public interface for processing card reviews. It can be
        called directly for testing or by the internal hook callback.
        
        The method:
        1. Converts the Anki card/reviewer data to a ReviewResult
        2. Dispatches to the ProgressionSystem for state updates
        3. Notifies any registered callbacks
        
        This method does NOT interfere with Anki's native functionality -
        it only observes and processes the review result after Anki has
        completed its own processing.
        
        Args:
            reviewer: Anki's reviewer instance (or mock)
            card: The card that was reviewed (or mock)
            ease: The ease button pressed (1=Again, 2=Hard, 3=Good, 4=Easy)
            
        Requirements: 7.2, 7.3
        """
        # Convert ease to is_correct (Good=3 or Easy=4 are correct)
        is_correct = ease >= 3
        
        # Extract card and deck IDs
        card_id = self._get_card_id(card)
        deck_id = self._get_deck_id(card)
        
        # Create ReviewResult
        review_result = ReviewResult(
            card_id=card_id,
            deck_id=deck_id,
            is_correct=is_correct,
            ease=ease,
            timestamp=datetime.now(),
            interval=self._get_card_interval(card),
            next_review=datetime.now(),  # Simplified - actual would come from card
            repetitions=self._get_card_repetitions(card),
            lapses=self._get_card_lapses(card),
            quality=ease
        )
        
        # Process the review through the progression system
        # This updates points, streaks, levels, etc.
        try:
            updated_state = self.progression_system.process_review(review_result)
            logger.debug(
                f"Review processed: correct={is_correct}, "
                f"total_points={updated_state.total_points}, "
                f"streak={updated_state.current_streak}"
            )
        except Exception as e:
            # Log error but don't raise - we must not interfere with Anki
            logger.error(f"Error processing review: {e}")
        
        # Notify any registered callbacks
        for callback in self._review_callbacks:
            try:
                callback(review_result)
            except Exception as e:
                logger.error(f"Error in review callback: {e}")
    
    def add_review_callback(self, callback: Callable[[ReviewResult], None]) -> None:
        """Add a callback to be notified when a card is reviewed.
        
        This allows other components (like the GameWindow) to be notified
        of review events without coupling them directly to the hook system.
        
        Args:
            callback: Function to call with the ReviewResult
        """
        if callback not in self._review_callbacks:
            self._review_callbacks.append(callback)
            logger.debug("Review callback added")
    
    def remove_review_callback(self, callback: Callable[[ReviewResult], None]) -> None:
        """Remove a previously registered review callback.
        
        Args:
            callback: Function to remove
        """
        try:
            self._review_callbacks.remove(callback)
            logger.debug("Review callback removed")
        except ValueError:
            logger.warning("Callback not found in review callbacks")
    
    @property
    def is_registered(self) -> bool:
        """Check if hooks are currently registered.
        
        Returns:
            True if hooks are registered
        """
        return self._hooks_registered
    
    def _on_reviewer_did_answer_card(self, reviewer: Any, card: Any, ease: int) -> None:
        """Internal callback for the reviewer_did_answer_card hook.
        
        This is the actual callback registered with Anki's hook system.
        It delegates to on_card_reviewed for the actual processing.
        
        Args:
            reviewer: Anki's reviewer instance
            card: The card that was reviewed
            ease: The ease button pressed
        """
        self.on_card_reviewed(reviewer, card, ease)
    
    def _get_card_id(self, card: Any) -> str:
        """Extract the card ID from an Anki card object.
        
        Args:
            card: Anki card object or mock
            
        Returns:
            String representation of the card ID
        """
        if hasattr(card, 'id'):
            return str(card.id)
        elif isinstance(card, dict) and 'id' in card:
            return str(card['id'])
        return "unknown"
    
    def _get_deck_id(self, card: Any) -> str:
        """Extract the deck ID from an Anki card object.
        
        Args:
            card: Anki card object or mock
            
        Returns:
            String representation of the deck ID
        """
        if hasattr(card, 'did'):
            return str(card.did)
        elif hasattr(card, 'deck_id'):
            return str(card.deck_id)
        elif isinstance(card, dict) and 'did' in card:
            return str(card['did'])
        elif isinstance(card, dict) and 'deck_id' in card:
            return str(card['deck_id'])
        return "unknown"
    
    def _get_card_interval(self, card: Any) -> int:
        """Extract the interval from an Anki card object.
        
        Args:
            card: Anki card object or mock
            
        Returns:
            Card interval in days
        """
        if hasattr(card, 'ivl'):
            return card.ivl
        elif isinstance(card, dict) and 'ivl' in card:
            return card['ivl']
        return 0
    
    def _get_card_repetitions(self, card: Any) -> int:
        """Extract the repetition count from an Anki card object.
        
        Args:
            card: Anki card object or mock
            
        Returns:
            Number of repetitions
        """
        if hasattr(card, 'reps'):
            return card.reps
        elif isinstance(card, dict) and 'reps' in card:
            return card['reps']
        return 0
    
    def _get_card_lapses(self, card: Any) -> int:
        """Extract the lapse count from an Anki card object.
        
        Args:
            card: Anki card object or mock
            
        Returns:
            Number of lapses
        """
        if hasattr(card, 'lapses'):
            return card.lapses
        elif isinstance(card, dict) and 'lapses' in card:
            return card['lapses']
        return 0
