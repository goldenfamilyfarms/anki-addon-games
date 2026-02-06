"""
Integration layer for NintendAnki.

This module provides the integration between Anki and the NintendAnki game systems.
It includes hook handlers for Anki events and menu integration for the UI.
"""

from integration.hook_handler import (
    HookHandler,
    AnkiHookProvider,
    RealAnkiHookProvider,
    MockAnkiHookProvider,
)

__all__ = [
    "HookHandler",
    "AnkiHookProvider",
    "RealAnkiHookProvider",
    "MockAnkiHookProvider",
]
