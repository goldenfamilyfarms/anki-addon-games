"""
Core module for NintendAnki.

This module contains the core game logic including scoring, progression,
achievements, power-ups, levels, and rewards.
"""

from core.scoring_engine import ScoringEngine
from core.progression_system import ProgressionSystem
from core.achievement_system import AchievementSystem

__all__ = ['ScoringEngine', 'ProgressionSystem', 'AchievementSystem']
