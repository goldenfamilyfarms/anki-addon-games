"""
NintendAnki - Anki Add-on Entry Point

This module serves as the entry point for the NintendAnki add-on when loaded by Anki.
It imports and initializes the NintendAnki add-on, registers hooks when Anki loads,
and handles clean shutdown when Anki closes.

Requirements: 7.1 - WHEN Anki starts, THE Add-on SHALL register hooks for card review events

The add-on provides three Nintendo-inspired game themes (Mario, Zelda, DKC) with a
unified progression system that tracks progress across all Anki decks.
"""

import logging
from pathlib import Path
from typing import Optional

# Configure logging for the add-on
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Global reference to the NintendAnki instance
_nintendanki = None


def _get_addon_dir() -> Path:
    """Get the add-on directory path.
    
    Returns:
        Path to the add-on directory.
    """
    return Path(__file__).parent


def _initialize_addon() -> None:
    """Initialize the NintendAnki add-on.
    
    This function is called when Anki loads the add-on. It:
    1. Imports the main NintendAnki module
    2. Initializes all managers and systems
    3. Registers hooks for card review events (Requirement 7.1)
    4. Sets up menu items and toolbar buttons
    
    Requirements: 7.1 - WHEN Anki starts, THE Add-on SHALL register hooks
                       for card review events
    """
    global _nintendanki
    
    try:
        # Import the main module
        from main import NintendAnki, initialize, shutdown
        
        # Get the add-on directory
        addon_dir = _get_addon_dir()
        
        # Initialize the add-on with real Anki integration
        # This registers hooks for card review events (Requirement 7.1)
        _nintendanki = initialize(addon_dir, use_real_anki=True)
        
        logger.info("NintendAnki add-on initialized successfully")
        
    except Exception as e:
        logger.error(f"Failed to initialize NintendAnki add-on: {e}")
        raise


def _shutdown_addon() -> None:
    """Shutdown the NintendAnki add-on.
    
    This function is called when Anki closes or the add-on is unloaded.
    It ensures proper cleanup of resources including:
    - Unregistering Anki hooks
    - Closing UI windows
    - Saving any pending state
    """
    global _nintendanki
    
    try:
        if _nintendanki is not None:
            from main import shutdown
            shutdown()
            _nintendanki = None
            logger.info("NintendAnki add-on shutdown complete")
    except Exception as e:
        logger.error(f"Error during NintendAnki shutdown: {e}")


def _register_shutdown_hook() -> None:
    """Register a hook to shutdown the add-on when Anki closes.
    
    This ensures proper cleanup when Anki exits.
    """
    try:
        from aqt import gui_hooks
        
        # Register shutdown callback for when Anki profile is closed
        gui_hooks.profile_will_close.append(_shutdown_addon)
        
        logger.debug("Registered shutdown hook for profile_will_close")
        
    except ImportError:
        logger.warning("Could not register shutdown hook - gui_hooks not available")
    except Exception as e:
        logger.error(f"Failed to register shutdown hook: {e}")


# Anki add-on initialization
# This code runs when Anki loads the add-on
try:
    # Check if we're running inside Anki
    from aqt import mw
    
    if mw is not None:
        # We're running inside Anki - initialize the add-on
        logger.info("NintendAnki add-on loading...")
        
        # Initialize the add-on (registers hooks - Requirement 7.1)
        _initialize_addon()
        
        # Register shutdown hook for clean exit
        _register_shutdown_hook()
        
        logger.info("NintendAnki add-on loaded successfully")
    else:
        logger.debug("Anki main window not available, deferring initialization")
        
except ImportError:
    # Not running inside Anki (e.g., running tests or standalone)
    logger.debug("Not running inside Anki - add-on not auto-initialized")
except Exception as e:
    logger.error(f"Failed to load NintendAnki add-on: {e}")


# Public API for external access
def get_nintendanki():
    """Get the NintendAnki instance.
    
    Returns:
        The NintendAnki instance, or None if not initialized.
    """
    return _nintendanki


def show_game_window() -> None:
    """Show the game window.
    
    This can be called from Anki's menu or toolbar.
    """
    if _nintendanki is not None:
        _nintendanki.show_game_window()


def show_dashboard() -> None:
    """Show the dashboard.
    
    This can be called from Anki's menu or toolbar.
    """
    if _nintendanki is not None:
        _nintendanki.show_dashboard()


def show_settings() -> None:
    """Show the settings panel.
    
    This can be called from Anki's menu or toolbar.
    """
    if _nintendanki is not None:
        _nintendanki.show_settings()
