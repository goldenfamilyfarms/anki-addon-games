"""
ConfigManager for NintendAnki.

This module provides JSON configuration file management for persisting
user settings including difficulty, rewards, animations, and accessibility options.

Requirements: 12.8, 12.9
"""

import json
import logging
import shutil
from dataclasses import asdict, fields
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

from data.models import GameConfig


logger = logging.getLogger(__name__)


class ConfigManager:
    """Manages JSON configuration file for user settings.
    
    This class handles all configuration operations including:
    - Loading configuration from JSON file
    - Saving configuration to JSON file
    - Resetting configuration to defaults
    - Graceful handling of missing or corrupted config files
    
    Attributes:
        config_path: Path to the JSON configuration file
    
    Requirements: 12.8, 12.9
    """
    
    # Valid colorblind mode options
    VALID_COLORBLIND_MODES = {None, "deuteranopia", "protanopia", "tritanopia"}
    
    def __init__(self, config_path: Path):
        """Initialize the ConfigManager.
        
        Args:
            config_path: Path to the JSON configuration file
        """
        self.config_path = Path(config_path)
        self._cached_config: Optional[GameConfig] = None
    
    def load_config(self) -> GameConfig:
        """Load configuration from JSON file.
        
        Loads user settings from the JSON configuration file. If the file
        doesn't exist or is corrupted, returns default configuration.
        
        Returns:
            GameConfig with loaded or default settings
            
        Requirements: 12.9
        """
        if not self.config_path.exists():
            logger.info(f"Config file not found at {self.config_path}, using defaults")
            self._cached_config = GameConfig()
            return self._cached_config
        
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            config = self._dict_to_config(data)
            self._cached_config = config
            return config
            
        except json.JSONDecodeError as e:
            logger.warning(f"Config file corrupted (JSON error): {e}")
            self._handle_corrupted_config()
            self._cached_config = GameConfig()
            return self._cached_config
            
        except Exception as e:
            logger.warning(f"Error loading config: {e}")
            self._handle_corrupted_config()
            self._cached_config = GameConfig()
            return self._cached_config
    
    def save_config(self, config: GameConfig) -> None:
        """Save configuration to JSON file.
        
        Persists user settings to the JSON configuration file immediately.
        Creates parent directories if they don't exist.
        
        Args:
            config: GameConfig to save
            
        Requirements: 12.8
        """
        # Ensure parent directory exists
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Convert config to dictionary
        data = self._config_to_dict(config)
        
        # Write to file with pretty formatting
        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            # Update cache
            self._cached_config = config
            logger.debug(f"Config saved to {self.config_path}")
            
        except Exception as e:
            logger.error(f"Error saving config: {e}")
            raise
    
    def reset_to_defaults(self) -> GameConfig:
        """Reset configuration to defaults.
        
        Creates a new GameConfig with default values and saves it to the
        configuration file, replacing any existing settings.
        
        Returns:
            GameConfig with default settings
        """
        default_config = GameConfig()
        self.save_config(default_config)
        return default_config
    
    def _config_to_dict(self, config: GameConfig) -> Dict[str, Any]:
        """Convert GameConfig to a JSON-serializable dictionary.
        
        Args:
            config: GameConfig to convert
            
        Returns:
            Dictionary representation of the config
        """
        return {
            # Difficulty settings
            "difficulty": {
                "base_points": config.base_points,
                "penalty_health_reduction": config.penalty_health_reduction,
                "penalty_currency_loss": config.penalty_currency_loss,
            },
            # Reward settings
            "rewards": {
                "streak_multiplier_5": config.streak_multiplier_5,
                "streak_multiplier_10": config.streak_multiplier_10,
                "streak_multiplier_20": config.streak_multiplier_20,
                "accuracy_bonus_threshold": config.accuracy_bonus_threshold,
                "accuracy_bonus_multiplier": config.accuracy_bonus_multiplier,
            },
            # Unlock settings
            "unlocks": {
                "cards_per_level": config.cards_per_level,
                "cards_per_powerup": config.cards_per_powerup,
            },
            # Animation settings
            "animation": {
                "animation_speed": config.animation_speed,
                "animations_enabled": config.animations_enabled,
            },
            # Accessibility settings
            "accessibility": {
                "colorblind_mode": config.colorblind_mode,
                "sound_enabled": config.sound_enabled,
                "sound_volume": config.sound_volume,
            },
        }
    
    def _dict_to_config(self, data: Dict[str, Any]) -> GameConfig:
        """Convert a dictionary to GameConfig.
        
        Handles missing keys by using default values, and validates
        values to ensure they are within acceptable ranges.
        
        Args:
            data: Dictionary to convert
            
        Returns:
            GameConfig with values from dictionary
        """
        defaults = GameConfig()
        
        # Extract difficulty settings
        difficulty = data.get("difficulty", {})
        base_points = self._validate_positive_int(
            difficulty.get("base_points", defaults.base_points),
            defaults.base_points
        )
        penalty_health_reduction = self._validate_float_range(
            difficulty.get("penalty_health_reduction", defaults.penalty_health_reduction),
            0.0, 1.0, defaults.penalty_health_reduction
        )
        penalty_currency_loss = self._validate_non_negative_int(
            difficulty.get("penalty_currency_loss", defaults.penalty_currency_loss),
            defaults.penalty_currency_loss
        )
        
        # Extract reward settings
        rewards = data.get("rewards", {})
        streak_multiplier_5 = self._validate_positive_float(
            rewards.get("streak_multiplier_5", defaults.streak_multiplier_5),
            defaults.streak_multiplier_5
        )
        streak_multiplier_10 = self._validate_positive_float(
            rewards.get("streak_multiplier_10", defaults.streak_multiplier_10),
            defaults.streak_multiplier_10
        )
        streak_multiplier_20 = self._validate_positive_float(
            rewards.get("streak_multiplier_20", defaults.streak_multiplier_20),
            defaults.streak_multiplier_20
        )
        accuracy_bonus_threshold = self._validate_float_range(
            rewards.get("accuracy_bonus_threshold", defaults.accuracy_bonus_threshold),
            0.0, 1.0, defaults.accuracy_bonus_threshold
        )
        accuracy_bonus_multiplier = self._validate_positive_float(
            rewards.get("accuracy_bonus_multiplier", defaults.accuracy_bonus_multiplier),
            defaults.accuracy_bonus_multiplier
        )
        
        # Extract unlock settings
        unlocks = data.get("unlocks", {})
        cards_per_level = self._validate_positive_int(
            unlocks.get("cards_per_level", defaults.cards_per_level),
            defaults.cards_per_level
        )
        cards_per_powerup = self._validate_positive_int(
            unlocks.get("cards_per_powerup", defaults.cards_per_powerup),
            defaults.cards_per_powerup
        )
        
        # Extract animation settings
        animation = data.get("animation", {})
        animation_speed = self._validate_positive_float(
            animation.get("animation_speed", defaults.animation_speed),
            defaults.animation_speed
        )
        animations_enabled = self._validate_bool(
            animation.get("animations_enabled", defaults.animations_enabled),
            defaults.animations_enabled
        )
        
        # Extract accessibility settings
        accessibility = data.get("accessibility", {})
        colorblind_mode = self._validate_colorblind_mode(
            accessibility.get("colorblind_mode", defaults.colorblind_mode)
        )
        sound_enabled = self._validate_bool(
            accessibility.get("sound_enabled", defaults.sound_enabled),
            defaults.sound_enabled
        )
        sound_volume = self._validate_float_range(
            accessibility.get("sound_volume", defaults.sound_volume),
            0.0, 1.0, defaults.sound_volume
        )
        
        return GameConfig(
            base_points=base_points,
            penalty_health_reduction=penalty_health_reduction,
            penalty_currency_loss=penalty_currency_loss,
            streak_multiplier_5=streak_multiplier_5,
            streak_multiplier_10=streak_multiplier_10,
            streak_multiplier_20=streak_multiplier_20,
            accuracy_bonus_threshold=accuracy_bonus_threshold,
            accuracy_bonus_multiplier=accuracy_bonus_multiplier,
            cards_per_level=cards_per_level,
            cards_per_powerup=cards_per_powerup,
            animation_speed=animation_speed,
            animations_enabled=animations_enabled,
            colorblind_mode=colorblind_mode,
            sound_enabled=sound_enabled,
            sound_volume=sound_volume,
        )
    
    def _handle_corrupted_config(self) -> None:
        """Handle a corrupted configuration file.
        
        Creates a backup of the corrupted file before it gets overwritten
        with defaults.
        """
        if not self.config_path.exists():
            return
        
        try:
            # Generate backup filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_name = f"{self.config_path.stem}_corrupted_{timestamp}{self.config_path.suffix}"
            backup_path = self.config_path.parent / backup_name
            
            # Copy the corrupted file
            shutil.copy2(self.config_path, backup_path)
            logger.info(f"Corrupted config backed up to {backup_path}")
            
        except Exception as e:
            logger.warning(f"Failed to backup corrupted config: {e}")
    
    def _validate_positive_int(self, value: Any, default: int) -> int:
        """Validate that a value is a positive integer.
        
        Args:
            value: Value to validate
            default: Default value to use if validation fails
            
        Returns:
            Validated positive integer
        """
        try:
            int_value = int(value)
            if int_value > 0:
                return int_value
            logger.warning(f"Invalid positive int value: {value}, using default: {default}")
            return default
        except (TypeError, ValueError):
            logger.warning(f"Invalid positive int value: {value}, using default: {default}")
            return default
    
    def _validate_non_negative_int(self, value: Any, default: int) -> int:
        """Validate that a value is a non-negative integer.
        
        Args:
            value: Value to validate
            default: Default value to use if validation fails
            
        Returns:
            Validated non-negative integer
        """
        try:
            int_value = int(value)
            if int_value >= 0:
                return int_value
            logger.warning(f"Invalid non-negative int value: {value}, using default: {default}")
            return default
        except (TypeError, ValueError):
            logger.warning(f"Invalid non-negative int value: {value}, using default: {default}")
            return default
    
    def _validate_positive_float(self, value: Any, default: float) -> float:
        """Validate that a value is a positive float.
        
        Args:
            value: Value to validate
            default: Default value to use if validation fails
            
        Returns:
            Validated positive float
        """
        try:
            float_value = float(value)
            if float_value > 0:
                return float_value
            logger.warning(f"Invalid positive float value: {value}, using default: {default}")
            return default
        except (TypeError, ValueError):
            logger.warning(f"Invalid positive float value: {value}, using default: {default}")
            return default
    
    def _validate_float_range(self, value: Any, min_val: float, max_val: float, default: float) -> float:
        """Validate that a value is a float within a range.
        
        Args:
            value: Value to validate
            min_val: Minimum allowed value (inclusive)
            max_val: Maximum allowed value (inclusive)
            default: Default value to use if validation fails
            
        Returns:
            Validated float within range
        """
        try:
            float_value = float(value)
            if min_val <= float_value <= max_val:
                return float_value
            logger.warning(f"Float value {value} out of range [{min_val}, {max_val}], using default: {default}")
            return default
        except (TypeError, ValueError):
            logger.warning(f"Invalid float value: {value}, using default: {default}")
            return default
    
    def _validate_bool(self, value: Any, default: bool) -> bool:
        """Validate that a value is a boolean.
        
        Args:
            value: Value to validate
            default: Default value to use if validation fails
            
        Returns:
            Validated boolean
        """
        if isinstance(value, bool):
            return value
        logger.warning(f"Invalid bool value: {value}, using default: {default}")
        return default
    
    def _validate_colorblind_mode(self, value: Any) -> Optional[str]:
        """Validate colorblind mode setting.
        
        Args:
            value: Value to validate
            
        Returns:
            Valid colorblind mode or None
        """
        if value in self.VALID_COLORBLIND_MODES:
            return value
        logger.warning(f"Invalid colorblind mode: {value}, using default: None")
        return None
