"""
Unit tests for ConfigManager.

Tests the JSON configuration file management including loading, saving,
resetting to defaults, and handling of missing/corrupted config files.

Requirements: 12.8, 12.9
"""

import json
import tempfile
from pathlib import Path

import pytest

from data import ConfigManager, GameConfig


@pytest.fixture
def temp_config_path():
    """Create a temporary config file path for testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir) / "test_config.json"


@pytest.fixture
def config_manager(temp_config_path):
    """Create a ConfigManager instance with a temporary config path."""
    return ConfigManager(temp_config_path)


class TestLoadConfig:
    """Tests for loading configuration."""
    
    def test_load_config_missing_file_returns_defaults(self, config_manager, temp_config_path):
        """Test that loading from missing file returns default config."""
        assert not temp_config_path.exists()
        
        config = config_manager.load_config()
        
        assert config.base_points == 10
        assert config.penalty_health_reduction == 0.1
        assert config.penalty_currency_loss == 1
        assert config.streak_multiplier_5 == 1.5
        assert config.streak_multiplier_10 == 2.0
        assert config.streak_multiplier_20 == 3.0
        assert config.accuracy_bonus_threshold == 0.9
        assert config.accuracy_bonus_multiplier == 1.25
        assert config.cards_per_level == 50
        assert config.cards_per_powerup == 100
        assert config.animation_speed == 1.0
        assert config.animations_enabled is True
        assert config.colorblind_mode is None
        assert config.sound_enabled is True
        assert config.sound_volume == 0.7
    
    def test_load_config_valid_file(self, config_manager, temp_config_path):
        """Test loading configuration from a valid JSON file."""
        config_data = {
            "difficulty": {
                "base_points": 20,
                "penalty_health_reduction": 0.2,
                "penalty_currency_loss": 2,
            },
            "rewards": {
                "streak_multiplier_5": 2.0,
                "streak_multiplier_10": 3.0,
                "streak_multiplier_20": 4.0,
                "accuracy_bonus_threshold": 0.85,
                "accuracy_bonus_multiplier": 1.5,
            },
            "unlocks": {
                "cards_per_level": 25,
                "cards_per_powerup": 50,
            },
            "animation": {
                "animation_speed": 1.5,
                "animations_enabled": False,
            },
            "accessibility": {
                "colorblind_mode": "deuteranopia",
                "sound_enabled": False,
                "sound_volume": 0.5,
            },
        }
        
        temp_config_path.parent.mkdir(parents=True, exist_ok=True)
        with open(temp_config_path, 'w') as f:
            json.dump(config_data, f)
        
        config = config_manager.load_config()
        
        assert config.base_points == 20
        assert config.penalty_health_reduction == 0.2
        assert config.penalty_currency_loss == 2
        assert config.streak_multiplier_5 == 2.0
        assert config.streak_multiplier_10 == 3.0
        assert config.streak_multiplier_20 == 4.0
        assert config.accuracy_bonus_threshold == 0.85
        assert config.accuracy_bonus_multiplier == 1.5
        assert config.cards_per_level == 25
        assert config.cards_per_powerup == 50
        assert config.animation_speed == 1.5
        assert config.animations_enabled is False
        assert config.colorblind_mode == "deuteranopia"
        assert config.sound_enabled is False
        assert config.sound_volume == 0.5
    
    def test_load_config_partial_file_uses_defaults_for_missing(self, config_manager, temp_config_path):
        """Test that missing keys use default values."""
        config_data = {
            "difficulty": {
                "base_points": 15,
            },
            "animation": {
                "animations_enabled": False,
            },
        }
        
        temp_config_path.parent.mkdir(parents=True, exist_ok=True)
        with open(temp_config_path, 'w') as f:
            json.dump(config_data, f)
        
        config = config_manager.load_config()
        
        # Specified values
        assert config.base_points == 15
        assert config.animations_enabled is False
        
        # Default values for missing keys
        assert config.penalty_health_reduction == 0.1
        assert config.streak_multiplier_5 == 1.5
        assert config.cards_per_level == 50
        assert config.sound_volume == 0.7
    
    def test_load_config_corrupted_json_returns_defaults(self, config_manager, temp_config_path):
        """Test that corrupted JSON file returns default config."""
        temp_config_path.parent.mkdir(parents=True, exist_ok=True)
        with open(temp_config_path, 'w') as f:
            f.write("{ invalid json content }")
        
        config = config_manager.load_config()
        
        # Should return defaults
        assert config.base_points == 10
        assert config.animations_enabled is True
    
    def test_load_config_corrupted_creates_backup(self, config_manager, temp_config_path):
        """Test that corrupted config file is backed up."""
        temp_config_path.parent.mkdir(parents=True, exist_ok=True)
        with open(temp_config_path, 'w') as f:
            f.write("{ invalid json }")
        
        config_manager.load_config()
        
        # Check that a backup was created
        backup_files = list(temp_config_path.parent.glob("*_corrupted_*"))
        assert len(backup_files) == 1
    
    def test_load_config_empty_file_returns_defaults(self, config_manager, temp_config_path):
        """Test that empty file returns default config."""
        temp_config_path.parent.mkdir(parents=True, exist_ok=True)
        temp_config_path.touch()
        
        config = config_manager.load_config()
        
        assert config.base_points == 10


class TestSaveConfig:
    """Tests for saving configuration."""
    
    def test_save_config_creates_file(self, config_manager, temp_config_path):
        """Test that save_config creates the config file."""
        assert not temp_config_path.exists()
        
        config = GameConfig(base_points=25)
        config_manager.save_config(config)
        
        assert temp_config_path.exists()
    
    def test_save_config_creates_parent_directories(self):
        """Test that save_config creates parent directories."""
        with tempfile.TemporaryDirectory() as tmpdir:
            nested_path = Path(tmpdir) / "nested" / "dirs" / "config.json"
            cm = ConfigManager(nested_path)
            
            config = GameConfig()
            cm.save_config(config)
            
            assert nested_path.exists()
    
    def test_save_config_writes_correct_data(self, config_manager, temp_config_path):
        """Test that save_config writes correct JSON data."""
        config = GameConfig(
            base_points=30,
            penalty_health_reduction=0.15,
            streak_multiplier_5=1.75,
            animations_enabled=False,
            colorblind_mode="protanopia",
            sound_volume=0.3,
        )
        
        config_manager.save_config(config)
        
        with open(temp_config_path, 'r') as f:
            data = json.load(f)
        
        assert data["difficulty"]["base_points"] == 30
        assert data["difficulty"]["penalty_health_reduction"] == 0.15
        assert data["rewards"]["streak_multiplier_5"] == 1.75
        assert data["animation"]["animations_enabled"] is False
        assert data["accessibility"]["colorblind_mode"] == "protanopia"
        assert data["accessibility"]["sound_volume"] == 0.3
    
    def test_save_config_overwrites_existing(self, config_manager, temp_config_path):
        """Test that save_config overwrites existing file."""
        # Save initial config
        config1 = GameConfig(base_points=10)
        config_manager.save_config(config1)
        
        # Save updated config
        config2 = GameConfig(base_points=50)
        config_manager.save_config(config2)
        
        # Load and verify
        loaded = config_manager.load_config()
        assert loaded.base_points == 50


class TestResetToDefaults:
    """Tests for resetting configuration to defaults."""
    
    def test_reset_to_defaults_returns_default_config(self, config_manager):
        """Test that reset_to_defaults returns default config."""
        config = config_manager.reset_to_defaults()
        
        assert config.base_points == 10
        assert config.penalty_health_reduction == 0.1
        assert config.animations_enabled is True
        assert config.colorblind_mode is None
    
    def test_reset_to_defaults_saves_to_file(self, config_manager, temp_config_path):
        """Test that reset_to_defaults saves defaults to file."""
        # First save custom config
        custom = GameConfig(base_points=100, animations_enabled=False)
        config_manager.save_config(custom)
        
        # Reset to defaults
        config_manager.reset_to_defaults()
        
        # Load and verify defaults were saved
        loaded = config_manager.load_config()
        assert loaded.base_points == 10
        assert loaded.animations_enabled is True
    
    def test_reset_to_defaults_creates_file_if_missing(self, config_manager, temp_config_path):
        """Test that reset_to_defaults creates file if it doesn't exist."""
        assert not temp_config_path.exists()
        
        config_manager.reset_to_defaults()
        
        assert temp_config_path.exists()


class TestRoundTrip:
    """Tests for save and load round-trip."""
    
    def test_save_load_roundtrip_preserves_all_values(self, config_manager):
        """Test that saving and loading preserves all configuration values."""
        original = GameConfig(
            base_points=25,
            penalty_health_reduction=0.15,
            penalty_currency_loss=3,
            streak_multiplier_5=1.75,
            streak_multiplier_10=2.5,
            streak_multiplier_20=4.0,
            accuracy_bonus_threshold=0.95,
            accuracy_bonus_multiplier=1.5,
            cards_per_level=30,
            cards_per_powerup=75,
            animation_speed=2.0,
            animations_enabled=False,
            colorblind_mode="tritanopia",
            sound_enabled=False,
            sound_volume=0.25,
        )
        
        config_manager.save_config(original)
        loaded = config_manager.load_config()
        
        assert loaded.base_points == original.base_points
        assert loaded.penalty_health_reduction == original.penalty_health_reduction
        assert loaded.penalty_currency_loss == original.penalty_currency_loss
        assert loaded.streak_multiplier_5 == original.streak_multiplier_5
        assert loaded.streak_multiplier_10 == original.streak_multiplier_10
        assert loaded.streak_multiplier_20 == original.streak_multiplier_20
        assert loaded.accuracy_bonus_threshold == original.accuracy_bonus_threshold
        assert loaded.accuracy_bonus_multiplier == original.accuracy_bonus_multiplier
        assert loaded.cards_per_level == original.cards_per_level
        assert loaded.cards_per_powerup == original.cards_per_powerup
        assert loaded.animation_speed == original.animation_speed
        assert loaded.animations_enabled == original.animations_enabled
        assert loaded.colorblind_mode == original.colorblind_mode
        assert loaded.sound_enabled == original.sound_enabled
        assert loaded.sound_volume == original.sound_volume
    
    def test_save_load_roundtrip_with_none_colorblind_mode(self, config_manager):
        """Test round-trip with None colorblind mode."""
        original = GameConfig(colorblind_mode=None)
        
        config_manager.save_config(original)
        loaded = config_manager.load_config()
        
        assert loaded.colorblind_mode is None


class TestValidation:
    """Tests for value validation."""
    
    def test_invalid_base_points_uses_default(self, config_manager, temp_config_path):
        """Test that invalid base_points uses default value."""
        config_data = {
            "difficulty": {
                "base_points": -5,  # Invalid: must be positive
            },
        }
        
        temp_config_path.parent.mkdir(parents=True, exist_ok=True)
        with open(temp_config_path, 'w') as f:
            json.dump(config_data, f)
        
        config = config_manager.load_config()
        assert config.base_points == 10  # Default
    
    def test_invalid_penalty_health_reduction_uses_default(self, config_manager, temp_config_path):
        """Test that out-of-range penalty_health_reduction uses default."""
        config_data = {
            "difficulty": {
                "penalty_health_reduction": 1.5,  # Invalid: must be 0.0-1.0
            },
        }
        
        temp_config_path.parent.mkdir(parents=True, exist_ok=True)
        with open(temp_config_path, 'w') as f:
            json.dump(config_data, f)
        
        config = config_manager.load_config()
        assert config.penalty_health_reduction == 0.1  # Default
    
    def test_invalid_sound_volume_uses_default(self, config_manager, temp_config_path):
        """Test that out-of-range sound_volume uses default."""
        config_data = {
            "accessibility": {
                "sound_volume": 2.0,  # Invalid: must be 0.0-1.0
            },
        }
        
        temp_config_path.parent.mkdir(parents=True, exist_ok=True)
        with open(temp_config_path, 'w') as f:
            json.dump(config_data, f)
        
        config = config_manager.load_config()
        assert config.sound_volume == 0.7  # Default
    
    def test_invalid_colorblind_mode_uses_default(self, config_manager, temp_config_path):
        """Test that invalid colorblind_mode uses default (None)."""
        config_data = {
            "accessibility": {
                "colorblind_mode": "invalid_mode",
            },
        }
        
        temp_config_path.parent.mkdir(parents=True, exist_ok=True)
        with open(temp_config_path, 'w') as f:
            json.dump(config_data, f)
        
        config = config_manager.load_config()
        assert config.colorblind_mode is None  # Default
    
    def test_invalid_animations_enabled_uses_default(self, config_manager, temp_config_path):
        """Test that non-boolean animations_enabled uses default."""
        config_data = {
            "animation": {
                "animations_enabled": "yes",  # Invalid: must be boolean
            },
        }
        
        temp_config_path.parent.mkdir(parents=True, exist_ok=True)
        with open(temp_config_path, 'w') as f:
            json.dump(config_data, f)
        
        config = config_manager.load_config()
        assert config.animations_enabled is True  # Default
    
    def test_string_number_values_are_converted(self, config_manager, temp_config_path):
        """Test that string numbers are converted to proper types."""
        config_data = {
            "difficulty": {
                "base_points": "15",  # String that can be converted
            },
            "rewards": {
                "streak_multiplier_5": "2.0",
            },
        }
        
        temp_config_path.parent.mkdir(parents=True, exist_ok=True)
        with open(temp_config_path, 'w') as f:
            json.dump(config_data, f)
        
        config = config_manager.load_config()
        assert config.base_points == 15
        assert config.streak_multiplier_5 == 2.0
    
    def test_zero_base_points_uses_default(self, config_manager, temp_config_path):
        """Test that zero base_points uses default (must be positive)."""
        config_data = {
            "difficulty": {
                "base_points": 0,
            },
        }
        
        temp_config_path.parent.mkdir(parents=True, exist_ok=True)
        with open(temp_config_path, 'w') as f:
            json.dump(config_data, f)
        
        config = config_manager.load_config()
        assert config.base_points == 10  # Default
    
    def test_negative_penalty_currency_loss_uses_default(self, config_manager, temp_config_path):
        """Test that negative penalty_currency_loss uses default."""
        config_data = {
            "difficulty": {
                "penalty_currency_loss": -1,
            },
        }
        
        temp_config_path.parent.mkdir(parents=True, exist_ok=True)
        with open(temp_config_path, 'w') as f:
            json.dump(config_data, f)
        
        config = config_manager.load_config()
        assert config.penalty_currency_loss == 1  # Default


class TestColorblindModes:
    """Tests for colorblind mode options."""
    
    def test_deuteranopia_mode(self, config_manager, temp_config_path):
        """Test deuteranopia colorblind mode."""
        config = GameConfig(colorblind_mode="deuteranopia")
        config_manager.save_config(config)
        
        loaded = config_manager.load_config()
        assert loaded.colorblind_mode == "deuteranopia"
    
    def test_protanopia_mode(self, config_manager, temp_config_path):
        """Test protanopia colorblind mode."""
        config = GameConfig(colorblind_mode="protanopia")
        config_manager.save_config(config)
        
        loaded = config_manager.load_config()
        assert loaded.colorblind_mode == "protanopia"
    
    def test_tritanopia_mode(self, config_manager, temp_config_path):
        """Test tritanopia colorblind mode."""
        config = GameConfig(colorblind_mode="tritanopia")
        config_manager.save_config(config)
        
        loaded = config_manager.load_config()
        assert loaded.colorblind_mode == "tritanopia"
