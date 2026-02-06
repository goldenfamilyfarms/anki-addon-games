"""
Unit tests for the RewardSystem.

Tests cover currency management, shop items, and item unlocking functionality.

Requirements: 11.1, 11.2, 11.3, 11.5, 11.6
"""

import pytest

from data.data_manager import DataManager
from core.reward_system import RewardSystem


@pytest.fixture
def temp_db(tmp_path):
    """Create a temporary database for testing."""
    db_path = tmp_path / "test_game.db"
    data_manager = DataManager(db_path)
    data_manager.initialize_database()
    return data_manager


@pytest.fixture
def reward_system(temp_db):
    """Create a RewardSystem instance with a temporary database."""
    return RewardSystem(temp_db)


class TestAddCurrency:
    """Tests for add_currency method - Requirement 11.1"""
    
    def test_add_currency_increases_balance(self, reward_system):
        """Adding currency should increase the balance by the exact amount."""
        initial_balance = reward_system.get_balance()
        new_balance = reward_system.add_currency(100, "test_source")
        
        assert new_balance == initial_balance + 100
    
    def test_add_currency_returns_new_balance(self, reward_system):
        """add_currency should return the new balance after addition."""
        reward_system.add_currency(50, "first_add")
        new_balance = reward_system.add_currency(30, "second_add")
        
        assert new_balance == 80
    
    def test_add_currency_zero_amount(self, reward_system):
        """Adding zero currency should not change the balance."""
        initial_balance = reward_system.get_balance()
        new_balance = reward_system.add_currency(0, "zero_add")
        
        assert new_balance == initial_balance
    
    def test_add_currency_negative_raises_error(self, reward_system):
        """Adding negative currency should raise ValueError."""
        with pytest.raises(ValueError, match="Amount must be non-negative"):
            reward_system.add_currency(-10, "negative_add")
    
    def test_add_currency_persists_to_database(self, temp_db):
        """Currency additions should persist to the database."""
        reward_system = RewardSystem(temp_db)
        reward_system.add_currency(200, "persistence_test")
        
        # Create new instance to verify persistence
        new_reward_system = RewardSystem(temp_db)
        assert new_reward_system.get_balance() == 200
    
    def test_add_currency_multiple_times(self, reward_system):
        """Multiple currency additions should accumulate correctly."""
        reward_system.add_currency(10, "add1")
        reward_system.add_currency(20, "add2")
        reward_system.add_currency(30, "add3")
        
        assert reward_system.get_balance() == 60
    
    def test_add_currency_large_amount(self, reward_system):
        """Adding large amounts of currency should work correctly."""
        large_amount = 1_000_000
        new_balance = reward_system.add_currency(large_amount, "large_add")
        
        assert new_balance == large_amount


class TestSpendCurrency:
    """Tests for spend_currency method - Requirements 11.2, 11.3"""
    
    def test_spend_currency_decreases_balance(self, reward_system):
        """Spending currency should decrease the balance."""
        reward_system.add_currency(100, "setup")
        result = reward_system.spend_currency(30, "test_item")
        
        assert result is True
        assert reward_system.get_balance() == 70
    
    def test_spend_currency_insufficient_funds(self, reward_system):
        """Spending more than available should fail and not change balance."""
        reward_system.add_currency(50, "setup")
        result = reward_system.spend_currency(100, "expensive_item")
        
        assert result is False
        assert reward_system.get_balance() == 50
    
    def test_spend_currency_exact_balance(self, reward_system):
        """Spending exactly the available balance should succeed."""
        reward_system.add_currency(100, "setup")
        result = reward_system.spend_currency(100, "exact_item")
        
        assert result is True
        assert reward_system.get_balance() == 0
    
    def test_spend_currency_zero_amount(self, reward_system):
        """Spending zero currency should succeed without changing balance."""
        reward_system.add_currency(50, "setup")
        result = reward_system.spend_currency(0, "free_item")
        
        assert result is True
        assert reward_system.get_balance() == 50
    
    def test_spend_currency_negative_amount(self, reward_system):
        """Spending negative currency should fail."""
        reward_system.add_currency(50, "setup")
        result = reward_system.spend_currency(-10, "negative_item")
        
        assert result is False
        assert reward_system.get_balance() == 50


class TestGetBalance:
    """Tests for get_balance method"""
    
    def test_get_balance_initial_zero(self, reward_system):
        """Initial balance should be zero."""
        assert reward_system.get_balance() == 0
    
    def test_get_balance_after_add(self, reward_system):
        """Balance should reflect added currency."""
        reward_system.add_currency(150, "test")
        assert reward_system.get_balance() == 150
    
    def test_get_balance_after_spend(self, reward_system):
        """Balance should reflect spent currency."""
        reward_system.add_currency(100, "setup")
        reward_system.spend_currency(40, "item")
        assert reward_system.get_balance() == 60


class TestGetShopItems:
    """Tests for get_shop_items method - Requirements 11.2, 11.3"""
    
    def test_get_shop_items_returns_list(self, reward_system):
        """get_shop_items should return a list of ShopItems."""
        items = reward_system.get_shop_items()
        
        assert isinstance(items, list)
        assert len(items) > 0
    
    def test_shop_items_have_characters(self, reward_system):
        """Shop should contain character items."""
        items = reward_system.get_shop_items()
        characters = [item for item in items if item.item_type == "character"]
        
        assert len(characters) > 0
    
    def test_shop_items_have_cosmetics(self, reward_system):
        """Shop should contain cosmetic items."""
        items = reward_system.get_shop_items()
        cosmetics = [item for item in items if item.item_type == "cosmetic"]
        
        assert len(cosmetics) > 0
    
    def test_shop_items_have_required_fields(self, reward_system):
        """Each shop item should have all required fields."""
        items = reward_system.get_shop_items()
        
        for item in items:
            assert item.id is not None
            assert item.name is not None
            assert item.description is not None
            assert item.icon is not None
            assert item.price >= 0
            assert item.item_type in ["character", "cosmetic"]
    
    def test_default_characters_are_owned(self, reward_system):
        """Default characters (Mario, Link, DK) should be owned by default."""
        items = reward_system.get_shop_items()
        
        default_chars = ["char_mario", "char_link", "char_dk"]
        for char_id in default_chars:
            char = next((item for item in items if item.id == char_id), None)
            assert char is not None, f"Default character {char_id} not found"
            assert char.owned is True, f"Default character {char_id} should be owned"
    
    def test_shop_items_reflect_ownership_status(self, temp_db):
        """Shop items should reflect current ownership status from database."""
        # First, unlock an item
        reward_system = RewardSystem(temp_db)
        reward_system.add_currency(100, "setup")
        reward_system.unlock_item("char_luigi")
        
        # Create new instance and check ownership
        new_reward_system = RewardSystem(temp_db)
        items = new_reward_system.get_shop_items()
        luigi = next((item for item in items if item.id == "char_luigi"), None)
        
        assert luigi is not None
        assert luigi.owned is True


class TestUnlockItem:
    """Tests for unlock_item method - Requirements 11.2, 11.3, 11.6"""
    
    def test_unlock_item_success(self, reward_system):
        """Unlocking an item with sufficient funds should succeed."""
        reward_system.add_currency(100, "setup")
        result = reward_system.unlock_item("char_luigi")
        
        assert result is True
    
    def test_unlock_item_deducts_currency(self, reward_system):
        """Unlocking an item should deduct its price from balance."""
        reward_system.add_currency(200, "setup")
        
        # Get Luigi's price
        items = reward_system.get_shop_items()
        luigi = next(item for item in items if item.id == "char_luigi")
        
        reward_system.unlock_item("char_luigi")
        
        assert reward_system.get_balance() == 200 - luigi.price
    
    def test_unlock_item_insufficient_funds(self, reward_system):
        """Unlocking an item without sufficient funds should fail."""
        reward_system.add_currency(10, "setup")  # Not enough for any character
        result = reward_system.unlock_item("char_luigi")
        
        assert result is False
        assert reward_system.get_balance() == 10  # Balance unchanged
    
    def test_unlock_item_already_owned(self, reward_system):
        """Unlocking an already owned item should fail."""
        reward_system.add_currency(200, "setup")
        
        # Mario is owned by default
        result = reward_system.unlock_item("char_mario")
        
        assert result is False
        assert reward_system.get_balance() == 200  # Balance unchanged
    
    def test_unlock_item_not_found(self, reward_system):
        """Unlocking a non-existent item should fail."""
        reward_system.add_currency(1000, "setup")
        result = reward_system.unlock_item("nonexistent_item")
        
        assert result is False
    
    def test_unlock_item_marks_as_owned(self, reward_system):
        """Unlocking an item should mark it as owned in shop."""
        reward_system.add_currency(100, "setup")
        reward_system.unlock_item("char_luigi")
        
        items = reward_system.get_shop_items()
        luigi = next(item for item in items if item.id == "char_luigi")
        
        assert luigi.owned is True
    
    def test_unlock_item_persists_to_database(self, temp_db):
        """Unlocked items should persist to the database."""
        reward_system = RewardSystem(temp_db)
        reward_system.add_currency(100, "setup")
        reward_system.unlock_item("char_luigi")
        
        # Create new instance to verify persistence
        new_reward_system = RewardSystem(temp_db)
        assert new_reward_system.is_item_owned("char_luigi") is True
    
    def test_unlock_cosmetic_item(self, reward_system):
        """Unlocking a cosmetic item should work correctly."""
        reward_system.add_currency(100, "setup")
        result = reward_system.unlock_item("cosmetic_golden_frame")
        
        assert result is True
        assert reward_system.is_item_owned("cosmetic_golden_frame") is True
    
    def test_unlock_character_makes_available_for_selection(self, reward_system):
        """Unlocked characters should appear in owned characters list."""
        reward_system.add_currency(100, "setup")
        reward_system.unlock_item("char_luigi")
        
        owned_chars = reward_system.get_owned_characters()
        char_ids = [c.id for c in owned_chars]
        
        assert "char_luigi" in char_ids


class TestGetUnlockProgress:
    """Tests for get_unlock_progress method - Requirement 11.5"""
    
    def test_unlock_progress_shows_next_item(self, reward_system):
        """Progress should show the next cheapest unowned item."""
        progress = reward_system.get_unlock_progress()
        
        assert progress.next_item is not None
        assert progress.next_item.owned is False
    
    def test_unlock_progress_shows_currency_needed(self, reward_system):
        """Progress should show currency needed for next unlock."""
        progress = reward_system.get_unlock_progress()
        
        assert progress.currency_needed >= 0
        assert progress.currency_needed == progress.next_item.price
    
    def test_unlock_progress_shows_current_balance(self, reward_system):
        """Progress should show current balance."""
        reward_system.add_currency(75, "setup")
        progress = reward_system.get_unlock_progress()
        
        assert progress.current_balance == 75
    
    def test_unlock_progress_percentage_calculation(self, reward_system):
        """Progress percentage should be calculated correctly."""
        # Add half the price of the cheapest item
        items = reward_system.get_shop_items()
        unowned = [i for i in items if not i.owned]
        unowned.sort(key=lambda x: x.price)
        cheapest = unowned[0]
        
        reward_system.add_currency(cheapest.price // 2, "setup")
        progress = reward_system.get_unlock_progress()
        
        expected_percentage = (cheapest.price // 2) / cheapest.price
        assert abs(progress.percentage - expected_percentage) < 0.01
    
    def test_unlock_progress_percentage_capped_at_one(self, reward_system):
        """Progress percentage should not exceed 1.0."""
        reward_system.add_currency(10000, "setup")
        progress = reward_system.get_unlock_progress()
        
        assert progress.percentage <= 1.0
    
    def test_unlock_progress_all_items_owned(self, temp_db):
        """When all items are owned, progress should indicate completion."""
        reward_system = RewardSystem(temp_db)
        
        # Add lots of currency and unlock all items
        reward_system.add_currency(100000, "setup")
        items = reward_system.get_shop_items()
        for item in items:
            if not item.owned:
                reward_system.unlock_item(item.id)
        
        progress = reward_system.get_unlock_progress()
        
        assert progress.next_item is None
        assert progress.percentage == 1.0


class TestGetOwnedCharacters:
    """Tests for get_owned_characters method - Requirement 11.6"""
    
    def test_default_characters_in_owned_list(self, reward_system):
        """Default characters should be in the owned list."""
        owned = reward_system.get_owned_characters()
        owned_ids = [c.id for c in owned]
        
        assert "char_mario" in owned_ids
        assert "char_link" in owned_ids
        assert "char_dk" in owned_ids
    
    def test_unlocked_character_in_owned_list(self, reward_system):
        """Newly unlocked characters should appear in owned list."""
        reward_system.add_currency(100, "setup")
        reward_system.unlock_item("char_luigi")
        
        owned = reward_system.get_owned_characters()
        owned_ids = [c.id for c in owned]
        
        assert "char_luigi" in owned_ids
    
    def test_owned_characters_only_returns_characters(self, reward_system):
        """get_owned_characters should only return character items."""
        owned = reward_system.get_owned_characters()
        
        for item in owned:
            assert item.item_type == "character"


class TestGetOwnedCosmetics:
    """Tests for get_owned_cosmetics method"""
    
    def test_no_cosmetics_owned_initially(self, reward_system):
        """No cosmetics should be owned initially."""
        owned = reward_system.get_owned_cosmetics()
        
        assert len(owned) == 0
    
    def test_unlocked_cosmetic_in_owned_list(self, reward_system):
        """Newly unlocked cosmetics should appear in owned list."""
        reward_system.add_currency(100, "setup")
        reward_system.unlock_item("cosmetic_golden_frame")
        
        owned = reward_system.get_owned_cosmetics()
        owned_ids = [c.id for c in owned]
        
        assert "cosmetic_golden_frame" in owned_ids
    
    def test_owned_cosmetics_only_returns_cosmetics(self, reward_system):
        """get_owned_cosmetics should only return cosmetic items."""
        reward_system.add_currency(200, "setup")
        reward_system.unlock_item("cosmetic_golden_frame")
        reward_system.unlock_item("cosmetic_rainbow_trail")
        
        owned = reward_system.get_owned_cosmetics()
        
        for item in owned:
            assert item.item_type == "cosmetic"


class TestIsItemOwned:
    """Tests for is_item_owned method"""
    
    def test_default_character_is_owned(self, reward_system):
        """Default characters should be reported as owned."""
        assert reward_system.is_item_owned("char_mario") is True
        assert reward_system.is_item_owned("char_link") is True
        assert reward_system.is_item_owned("char_dk") is True
    
    def test_unowned_item_not_owned(self, reward_system):
        """Unowned items should be reported as not owned."""
        assert reward_system.is_item_owned("char_luigi") is False
    
    def test_unlocked_item_is_owned(self, reward_system):
        """Unlocked items should be reported as owned."""
        reward_system.add_currency(100, "setup")
        reward_system.unlock_item("char_luigi")
        
        assert reward_system.is_item_owned("char_luigi") is True
    
    def test_nonexistent_item_not_owned(self, reward_system):
        """Non-existent items should be reported as not owned."""
        assert reward_system.is_item_owned("nonexistent_item") is False
