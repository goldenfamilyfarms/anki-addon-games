"""
Unit tests for the PowerUpSystem.

Tests cover power-up granting, activation, inventory management,
and duration tracking functionality.

Requirements: 13.1, 13.2, 13.3, 13.4, 13.5, 13.6
"""

import pytest

from data.data_manager import DataManager
from data.models import PowerUpType, Theme
from core.powerup_system import PowerUpSystem, THEME_POWERUPS, POWERUP_METADATA


@pytest.fixture
def temp_db(tmp_path):
    """Create a temporary database for testing."""
    db_path = tmp_path / "test_game.db"
    data_manager = DataManager(db_path)
    data_manager.initialize_database()
    return data_manager


@pytest.fixture
def powerup_system(temp_db):
    """Create a PowerUpSystem instance with a temporary database."""
    return PowerUpSystem(temp_db)


class TestGrantPowerup:
    """Tests for grant_powerup method - Requirements 13.1, 13.2, 13.3"""
    
    def test_grant_powerup_returns_powerup(self, powerup_system):
        """Granting a power-up should return a PowerUp instance."""
        powerup = powerup_system.grant_powerup(PowerUpType.MUSHROOM, Theme.MARIO)
        
        assert powerup is not None
        assert powerup.type == PowerUpType.MUSHROOM
        assert powerup.theme == Theme.MARIO
    
    def test_grant_powerup_adds_to_inventory(self, powerup_system):
        """Granted power-up should appear in inventory."""
        powerup_system.grant_powerup(PowerUpType.MUSHROOM, Theme.MARIO)
        
        inventory = powerup_system.get_inventory()
        assert len(inventory) == 1
        assert inventory[0].type == PowerUpType.MUSHROOM

    def test_grant_powerup_with_correct_metadata(self, powerup_system):
        """Granted power-up should have correct metadata from POWERUP_METADATA."""
        powerup = powerup_system.grant_powerup(PowerUpType.FIRE_FLOWER, Theme.MARIO)
        
        expected_metadata = POWERUP_METADATA[PowerUpType.FIRE_FLOWER]
        assert powerup.name == expected_metadata["name"]
        assert powerup.description == expected_metadata["description"]
        assert powerup.icon == expected_metadata["icon"]
        assert powerup.duration_seconds == expected_metadata["duration_seconds"]
    
    def test_grant_same_powerup_increments_quantity(self, powerup_system):
        """Granting the same power-up type should increment quantity."""
        powerup_system.grant_powerup(PowerUpType.MUSHROOM, Theme.MARIO)
        powerup_system.grant_powerup(PowerUpType.MUSHROOM, Theme.MARIO)
        
        inventory = powerup_system.get_inventory()
        assert len(inventory) == 1
        assert inventory[0].quantity == 2
    
    def test_grant_different_powerups_creates_separate_entries(self, powerup_system):
        """Granting different power-up types should create separate inventory entries."""
        powerup_system.grant_powerup(PowerUpType.MUSHROOM, Theme.MARIO)
        powerup_system.grant_powerup(PowerUpType.FIRE_FLOWER, Theme.MARIO)
        
        inventory = powerup_system.get_inventory()
        assert len(inventory) == 2
    
    def test_grant_theme_appropriate_powerups(self, powerup_system):
        """Each theme should have appropriate power-ups defined."""
        # Test Mario theme power-ups
        assert PowerUpType.MUSHROOM in THEME_POWERUPS[Theme.MARIO]
        assert PowerUpType.FIRE_FLOWER in THEME_POWERUPS[Theme.MARIO]
        assert PowerUpType.STAR in THEME_POWERUPS[Theme.MARIO]
        
        # Test Zelda theme power-ups
        assert PowerUpType.HEART_CONTAINER in THEME_POWERUPS[Theme.ZELDA]
        assert PowerUpType.FAIRY in THEME_POWERUPS[Theme.ZELDA]
        
        # Test DKC theme power-ups
        assert PowerUpType.BANANA in THEME_POWERUPS[Theme.DKC]
        assert PowerUpType.BARREL in THEME_POWERUPS[Theme.DKC]
    
    def test_grant_powerup_persists_to_database(self, temp_db):
        """Granted power-ups should be persisted to the database."""
        system1 = PowerUpSystem(temp_db)
        system1.grant_powerup(PowerUpType.MUSHROOM, Theme.MARIO)
        
        # Create a new system instance to verify persistence
        system2 = PowerUpSystem(temp_db)
        inventory = system2.get_inventory()
        
        assert len(inventory) == 1
        assert inventory[0].type == PowerUpType.MUSHROOM


class TestActivatePowerup:
    """Tests for activate_powerup method - Requirements 13.4"""
    
    def test_activate_powerup_returns_true_on_success(self, powerup_system):
        """Activating a valid power-up should return True."""
        powerup = powerup_system.grant_powerup(PowerUpType.FIRE_FLOWER, Theme.MARIO)
        
        result = powerup_system.activate_powerup(powerup.id)
        assert result is True
    
    def test_activate_powerup_returns_false_for_invalid_id(self, powerup_system):
        """Activating a non-existent power-up should return False."""
        result = powerup_system.activate_powerup("invalid-id")
        assert result is False
    
    def test_activate_powerup_decrements_quantity(self, powerup_system):
        """Activating a power-up should decrement its quantity."""
        powerup = powerup_system.grant_powerup(PowerUpType.MUSHROOM, Theme.MARIO)
        powerup_system.grant_powerup(PowerUpType.MUSHROOM, Theme.MARIO)  # quantity = 2
        
        powerup_system.activate_powerup(powerup.id)
        
        inventory = powerup_system.get_inventory()
        assert len(inventory) == 1
        assert inventory[0].quantity == 1
    
    def test_activate_powerup_removes_from_inventory_when_quantity_zero(self, powerup_system):
        """Power-up should be removed from inventory when quantity reaches zero."""
        powerup = powerup_system.grant_powerup(PowerUpType.MUSHROOM, Theme.MARIO)
        
        powerup_system.activate_powerup(powerup.id)
        
        inventory = powerup_system.get_inventory()
        assert len(inventory) == 0
    
    def test_activate_timed_powerup_adds_to_active_list(self, powerup_system):
        """Activating a timed power-up should add it to active power-ups."""
        # Fire Flower has duration_seconds = 60
        powerup = powerup_system.grant_powerup(PowerUpType.FIRE_FLOWER, Theme.MARIO)
        
        powerup_system.activate_powerup(powerup.id)
        
        active = powerup_system.get_active_powerups()
        assert len(active) == 1
        assert active[0].powerup.type == PowerUpType.FIRE_FLOWER
        assert active[0].remaining_seconds == 60.0

    def test_activate_instant_powerup_not_added_to_active_list(self, powerup_system):
        """Activating an instant power-up should not add it to active power-ups."""
        # Mushroom has duration_seconds = 0 (instant)
        powerup = powerup_system.grant_powerup(PowerUpType.MUSHROOM, Theme.MARIO)
        
        powerup_system.activate_powerup(powerup.id)
        
        active = powerup_system.get_active_powerups()
        assert len(active) == 0
    
    def test_activate_powerup_returns_false_when_quantity_zero(self, powerup_system):
        """Cannot activate a power-up with zero quantity."""
        powerup = powerup_system.grant_powerup(PowerUpType.MUSHROOM, Theme.MARIO)
        powerup_system.activate_powerup(powerup.id)  # quantity now 0
        
        # Try to activate again
        result = powerup_system.activate_powerup(powerup.id)
        assert result is False


class TestGetActivePowerups:
    """Tests for get_active_powerups method - Requirements 13.5, 13.6"""
    
    def test_get_active_powerups_returns_empty_list_initially(self, powerup_system):
        """Should return empty list when no power-ups are active."""
        active = powerup_system.get_active_powerups()
        assert active == []
    
    def test_get_active_powerups_returns_activated_powerups(self, powerup_system):
        """Should return all activated timed power-ups."""
        powerup1 = powerup_system.grant_powerup(PowerUpType.FIRE_FLOWER, Theme.MARIO)
        powerup2 = powerup_system.grant_powerup(PowerUpType.STAR, Theme.MARIO)
        
        powerup_system.activate_powerup(powerup1.id)
        powerup_system.activate_powerup(powerup2.id)
        
        active = powerup_system.get_active_powerups()
        assert len(active) == 2
    
    def test_get_active_powerups_includes_remaining_duration(self, powerup_system):
        """Active power-ups should include remaining duration."""
        powerup = powerup_system.grant_powerup(PowerUpType.FIRE_FLOWER, Theme.MARIO)
        powerup_system.activate_powerup(powerup.id)
        
        active = powerup_system.get_active_powerups()
        assert active[0].remaining_seconds == 60.0
        assert active[0].duration_seconds == 60


class TestGetInventory:
    """Tests for get_inventory method - Requirements 13.3, 13.5"""
    
    def test_get_inventory_returns_empty_list_initially(self, powerup_system):
        """Should return empty list when no power-ups have been granted."""
        inventory = powerup_system.get_inventory()
        assert inventory == []
    
    def test_get_inventory_returns_all_powerups(self, powerup_system):
        """Should return all power-ups in inventory."""
        powerup_system.grant_powerup(PowerUpType.MUSHROOM, Theme.MARIO)
        powerup_system.grant_powerup(PowerUpType.FIRE_FLOWER, Theme.MARIO)
        powerup_system.grant_powerup(PowerUpType.HEART_CONTAINER, Theme.ZELDA)
        
        inventory = powerup_system.get_inventory()
        assert len(inventory) == 3
    
    def test_get_inventory_returns_correct_quantities(self, powerup_system):
        """Should return correct quantities for each power-up."""
        powerup_system.grant_powerup(PowerUpType.MUSHROOM, Theme.MARIO)
        powerup_system.grant_powerup(PowerUpType.MUSHROOM, Theme.MARIO)
        powerup_system.grant_powerup(PowerUpType.MUSHROOM, Theme.MARIO)
        
        inventory = powerup_system.get_inventory()
        assert len(inventory) == 1
        assert inventory[0].quantity == 3


class TestTick:
    """Tests for tick method - Requirements 13.6"""
    
    def test_tick_decrements_remaining_time(self, powerup_system):
        """Tick should decrement remaining time on active power-ups."""
        powerup = powerup_system.grant_powerup(PowerUpType.FIRE_FLOWER, Theme.MARIO)
        powerup_system.activate_powerup(powerup.id)
        
        powerup_system.tick(10.0)  # 10 seconds elapsed
        
        active = powerup_system.get_active_powerups()
        assert active[0].remaining_seconds == 50.0
    
    def test_tick_returns_expired_powerups(self, powerup_system):
        """Tick should return list of expired power-ups."""
        powerup = powerup_system.grant_powerup(PowerUpType.STAR, Theme.MARIO)  # 30 seconds
        powerup_system.activate_powerup(powerup.id)
        
        expired = powerup_system.tick(35.0)  # More than 30 seconds
        
        assert len(expired) == 1
        assert expired[0].type == PowerUpType.STAR
    
    def test_tick_removes_expired_powerups_from_active_list(self, powerup_system):
        """Expired power-ups should be removed from active list."""
        powerup = powerup_system.grant_powerup(PowerUpType.STAR, Theme.MARIO)  # 30 seconds
        powerup_system.activate_powerup(powerup.id)
        
        powerup_system.tick(35.0)  # Expire the power-up
        
        active = powerup_system.get_active_powerups()
        assert len(active) == 0
    
    def test_tick_handles_multiple_powerups(self, powerup_system):
        """Tick should handle multiple active power-ups correctly."""
        powerup1 = powerup_system.grant_powerup(PowerUpType.STAR, Theme.MARIO)  # 30 seconds
        powerup2 = powerup_system.grant_powerup(PowerUpType.FIRE_FLOWER, Theme.MARIO)  # 60 seconds
        
        powerup_system.activate_powerup(powerup1.id)
        powerup_system.activate_powerup(powerup2.id)
        
        # After 35 seconds, Star should expire but Fire Flower should remain
        expired = powerup_system.tick(35.0)
        
        assert len(expired) == 1
        assert expired[0].type == PowerUpType.STAR
        
        active = powerup_system.get_active_powerups()
        assert len(active) == 1
        assert active[0].powerup.type == PowerUpType.FIRE_FLOWER
        assert active[0].remaining_seconds == 25.0
    
    def test_tick_returns_empty_list_when_no_expiration(self, powerup_system):
        """Tick should return empty list when no power-ups expire."""
        powerup = powerup_system.grant_powerup(PowerUpType.FIRE_FLOWER, Theme.MARIO)
        powerup_system.activate_powerup(powerup.id)
        
        expired = powerup_system.tick(5.0)  # Only 5 seconds
        
        assert expired == []


class TestHelperMethods:
    """Tests for helper methods."""
    
    def test_get_theme_powerup_types(self, powerup_system):
        """Should return correct power-up types for each theme."""
        mario_types = powerup_system.get_theme_powerup_types(Theme.MARIO)
        assert PowerUpType.MUSHROOM in mario_types
        assert PowerUpType.FIRE_FLOWER in mario_types
        
        zelda_types = powerup_system.get_theme_powerup_types(Theme.ZELDA)
        assert PowerUpType.HEART_CONTAINER in zelda_types
        assert PowerUpType.FAIRY in zelda_types
        
        dkc_types = powerup_system.get_theme_powerup_types(Theme.DKC)
        assert PowerUpType.BANANA in dkc_types
        assert PowerUpType.BARREL in dkc_types
    
    def test_has_active_powerup_of_type(self, powerup_system):
        """Should correctly detect active power-ups by type."""
        powerup = powerup_system.grant_powerup(PowerUpType.FIRE_FLOWER, Theme.MARIO)
        
        assert powerup_system.has_active_powerup_of_type(PowerUpType.FIRE_FLOWER) is False
        
        powerup_system.activate_powerup(powerup.id)
        
        assert powerup_system.has_active_powerup_of_type(PowerUpType.FIRE_FLOWER) is True
        assert powerup_system.has_active_powerup_of_type(PowerUpType.STAR) is False
    
    def test_get_powerup_count(self, powerup_system):
        """Should return correct count of power-ups by type."""
        powerup_system.grant_powerup(PowerUpType.MUSHROOM, Theme.MARIO)
        powerup_system.grant_powerup(PowerUpType.MUSHROOM, Theme.MARIO)
        powerup_system.grant_powerup(PowerUpType.FIRE_FLOWER, Theme.MARIO)
        
        assert powerup_system.get_powerup_count(PowerUpType.MUSHROOM) == 2
        assert powerup_system.get_powerup_count(PowerUpType.FIRE_FLOWER) == 1
        assert powerup_system.get_powerup_count(PowerUpType.STAR) == 0
    
    def test_get_powerup_count_with_theme_filter(self, powerup_system):
        """Should filter power-up count by theme."""
        powerup_system.grant_powerup(PowerUpType.MUSHROOM, Theme.MARIO)
        powerup_system.grant_powerup(PowerUpType.HEART_CONTAINER, Theme.ZELDA)
        
        assert powerup_system.get_powerup_count(PowerUpType.MUSHROOM, Theme.MARIO) == 1
        assert powerup_system.get_powerup_count(PowerUpType.MUSHROOM, Theme.ZELDA) == 0
    
    def test_clear_all_active(self, powerup_system):
        """Should clear all active power-ups."""
        powerup1 = powerup_system.grant_powerup(PowerUpType.FIRE_FLOWER, Theme.MARIO)
        powerup2 = powerup_system.grant_powerup(PowerUpType.STAR, Theme.MARIO)
        
        powerup_system.activate_powerup(powerup1.id)
        powerup_system.activate_powerup(powerup2.id)
        
        assert len(powerup_system.get_active_powerups()) == 2
        
        powerup_system.clear_all_active()
        
        assert len(powerup_system.get_active_powerups()) == 0


class TestPersistence:
    """Tests for database persistence."""
    
    def test_inventory_persists_across_instances(self, temp_db):
        """Inventory should persist across PowerUpSystem instances."""
        system1 = PowerUpSystem(temp_db)
        system1.grant_powerup(PowerUpType.MUSHROOM, Theme.MARIO)
        system1.grant_powerup(PowerUpType.FIRE_FLOWER, Theme.MARIO)
        
        system2 = PowerUpSystem(temp_db)
        inventory = system2.get_inventory()
        
        assert len(inventory) == 2
        types = {p.type for p in inventory}
        assert PowerUpType.MUSHROOM in types
        assert PowerUpType.FIRE_FLOWER in types
    
    def test_active_powerups_persist_across_instances(self, temp_db):
        """Active power-ups should persist across PowerUpSystem instances."""
        system1 = PowerUpSystem(temp_db)
        powerup = system1.grant_powerup(PowerUpType.FIRE_FLOWER, Theme.MARIO)
        system1.activate_powerup(powerup.id)
        
        system2 = PowerUpSystem(temp_db)
        active = system2.get_active_powerups()
        
        assert len(active) == 1
        assert active[0].powerup.type == PowerUpType.FIRE_FLOWER
    
    def test_quantity_updates_persist(self, temp_db):
        """Quantity updates should persist to database."""
        system1 = PowerUpSystem(temp_db)
        powerup = system1.grant_powerup(PowerUpType.MUSHROOM, Theme.MARIO)
        system1.grant_powerup(PowerUpType.MUSHROOM, Theme.MARIO)  # quantity = 2
        system1.activate_powerup(powerup.id)  # quantity = 1
        
        system2 = PowerUpSystem(temp_db)
        inventory = system2.get_inventory()
        
        assert len(inventory) == 1
        assert inventory[0].quantity == 1


class TestEdgeCases:
    """Tests for edge cases and boundary conditions."""
    
    def test_tick_with_zero_delta_time(self, powerup_system):
        """Tick with zero delta time should not change remaining time."""
        powerup = powerup_system.grant_powerup(PowerUpType.FIRE_FLOWER, Theme.MARIO)
        powerup_system.activate_powerup(powerup.id)
        
        powerup_system.tick(0.0)
        
        active = powerup_system.get_active_powerups()
        assert active[0].remaining_seconds == 60.0
    
    def test_tick_with_exact_expiration_time(self, powerup_system):
        """Tick with exact remaining time should expire the power-up."""
        powerup = powerup_system.grant_powerup(PowerUpType.STAR, Theme.MARIO)  # 30 seconds
        powerup_system.activate_powerup(powerup.id)
        
        expired = powerup_system.tick(30.0)  # Exactly 30 seconds
        
        assert len(expired) == 1
        assert len(powerup_system.get_active_powerups()) == 0
    
    def test_grant_powerup_for_all_themes(self, powerup_system):
        """Should be able to grant power-ups for all themes."""
        # Grant one power-up for each theme
        mario_powerup = powerup_system.grant_powerup(PowerUpType.MUSHROOM, Theme.MARIO)
        zelda_powerup = powerup_system.grant_powerup(PowerUpType.HEART_CONTAINER, Theme.ZELDA)
        dkc_powerup = powerup_system.grant_powerup(PowerUpType.BANANA, Theme.DKC)
        
        inventory = powerup_system.get_inventory()
        assert len(inventory) == 3
        
        themes = {p.theme for p in inventory}
        assert Theme.MARIO in themes
        assert Theme.ZELDA in themes
        assert Theme.DKC in themes
    
    def test_multiple_activations_of_same_type(self, powerup_system):
        """Should be able to activate multiple power-ups of the same type."""
        # Grant 3 fire flowers
        powerup = powerup_system.grant_powerup(PowerUpType.FIRE_FLOWER, Theme.MARIO)
        powerup_system.grant_powerup(PowerUpType.FIRE_FLOWER, Theme.MARIO)
        powerup_system.grant_powerup(PowerUpType.FIRE_FLOWER, Theme.MARIO)
        
        # Activate all 3
        powerup_system.activate_powerup(powerup.id)
        powerup_system.activate_powerup(powerup.id)
        powerup_system.activate_powerup(powerup.id)
        
        # Should have 3 active power-ups
        active = powerup_system.get_active_powerups()
        assert len(active) == 3
        
        # Inventory should be empty
        inventory = powerup_system.get_inventory()
        assert len(inventory) == 0
    
    def test_tick_with_small_delta_time(self, powerup_system):
        """Tick with very small delta time should work correctly."""
        powerup = powerup_system.grant_powerup(PowerUpType.FIRE_FLOWER, Theme.MARIO)
        powerup_system.activate_powerup(powerup.id)
        
        # Simulate many small ticks
        for _ in range(100):
            powerup_system.tick(0.1)
        
        active = powerup_system.get_active_powerups()
        assert len(active) == 1
        # 60 - (100 * 0.1) = 50 seconds remaining
        assert abs(active[0].remaining_seconds - 50.0) < 0.01
    
    def test_powerup_with_unknown_type_uses_default_metadata(self, powerup_system):
        """Power-ups with unknown types should use default metadata."""
        # Use a power-up type that's not in POWERUP_METADATA
        powerup = powerup_system.grant_powerup(PowerUpType.CAPE_FEATHER, Theme.MARIO)
        
        assert powerup.name == "Cape Feather"
        assert "cape_feather" in powerup.description.lower()
        assert powerup.icon == "cape_feather.png"
    
    def test_active_powerup_remaining_time_persists(self, temp_db):
        """Remaining time on active power-ups should persist correctly."""
        system1 = PowerUpSystem(temp_db)
        powerup = system1.grant_powerup(PowerUpType.FIRE_FLOWER, Theme.MARIO)
        system1.activate_powerup(powerup.id)
        system1.tick(25.0)  # 35 seconds remaining
        
        system2 = PowerUpSystem(temp_db)
        active = system2.get_active_powerups()
        
        assert len(active) == 1
        assert abs(active[0].remaining_seconds - 35.0) < 0.01
