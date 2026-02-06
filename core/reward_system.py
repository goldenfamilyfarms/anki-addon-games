"""
RewardSystem for NintendAnki.

This module manages currency and unlockable rewards including characters
and cosmetic items. It handles currency transactions, shop items, and
tracks progress toward unlocks.

Requirements: 11.1, 11.2, 11.3, 11.5, 11.6
"""

from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional

from data.data_manager import DataManager
from data.models import (
    Collectible,
    CollectibleType,
    ShopItem,
    Theme,
)


@dataclass
class UnlockProgress:
    """Progress toward the next unlock.
    
    Attributes:
        next_item: The next item that can be unlocked
        currency_needed: Currency needed to unlock the next item
        current_balance: Current currency balance
        percentage: Percentage progress toward the unlock (0.0 to 1.0)
    """
    next_item: Optional[ShopItem]
    currency_needed: int
    current_balance: int
    percentage: float


# Default shop items - characters and cosmetics available for purchase
DEFAULT_SHOP_ITEMS: List[ShopItem] = [
    # Mario theme characters
    ShopItem(
        id="char_mario",
        name="Mario",
        description="The classic hero! Jump and collect coins.",
        icon="mario.png",
        price=0,  # Default character, free
        item_type="character",
        owned=True,  # Owned by default
    ),
    ShopItem(
        id="char_luigi",
        name="Luigi",
        description="Mario's brother with higher jumps.",
        icon="luigi.png",
        price=100,
        item_type="character",
    ),
    ShopItem(
        id="char_toad",
        name="Toad",
        description="Fast and nimble mushroom friend.",
        icon="toad.png",
        price=150,
        item_type="character",
    ),
    ShopItem(
        id="char_peach",
        name="Princess Peach",
        description="Float gracefully through levels.",
        icon="peach.png",
        price=200,
        item_type="character",
    ),
    
    # Zelda theme characters
    ShopItem(
        id="char_link",
        name="Link",
        description="The Hero of Time! Explore dungeons.",
        icon="link.png",
        price=0,  # Default character, free
        item_type="character",
        owned=True,  # Owned by default
    ),
    ShopItem(
        id="char_zelda",
        name="Princess Zelda",
        description="Wield the power of wisdom.",
        icon="zelda.png",
        price=200,
        item_type="character",
    ),
    ShopItem(
        id="char_sheik",
        name="Sheik",
        description="Swift and mysterious warrior.",
        icon="sheik.png",
        price=250,
        item_type="character",
    ),
    
    # DKC theme characters
    ShopItem(
        id="char_dk",
        name="Donkey Kong",
        description="The king of the jungle! Collect bananas.",
        icon="dk.png",
        price=0,  # Default character, free
        item_type="character",
        owned=True,  # Owned by default
    ),
    ShopItem(
        id="char_diddy",
        name="Diddy Kong",
        description="DK's nimble sidekick.",
        icon="diddy.png",
        price=100,
        item_type="character",
    ),
    ShopItem(
        id="char_dixie",
        name="Dixie Kong",
        description="Helicopter spin through the air.",
        icon="dixie.png",
        price=150,
        item_type="character",
    ),
    ShopItem(
        id="char_cranky",
        name="Cranky Kong",
        description="The original DK with sage advice.",
        icon="cranky.png",
        price=300,
        item_type="character",
    ),
    
    # Cosmetic items - Universal
    ShopItem(
        id="cosmetic_golden_frame",
        name="Golden Frame",
        description="A shiny golden frame for your profile.",
        icon="golden_frame.png",
        price=50,
        item_type="cosmetic",
    ),
    ShopItem(
        id="cosmetic_rainbow_trail",
        name="Rainbow Trail",
        description="Leave a rainbow trail as you move.",
        icon="rainbow_trail.png",
        price=75,
        item_type="cosmetic",
    ),
    ShopItem(
        id="cosmetic_sparkle_effect",
        name="Sparkle Effect",
        description="Add sparkles to your character.",
        icon="sparkle.png",
        price=100,
        item_type="cosmetic",
    ),
    ShopItem(
        id="cosmetic_victory_dance",
        name="Victory Dance",
        description="Special dance animation on level complete.",
        icon="victory_dance.png",
        price=125,
        item_type="cosmetic",
    ),
    ShopItem(
        id="cosmetic_crown",
        name="Royal Crown",
        description="A majestic crown for your character.",
        icon="crown.png",
        price=200,
        item_type="cosmetic",
    ),
    ShopItem(
        id="cosmetic_cape",
        name="Hero's Cape",
        description="A flowing cape that billows in the wind.",
        icon="cape.png",
        price=150,
        item_type="cosmetic",
    ),
    
    # Theme-specific cosmetics
    ShopItem(
        id="cosmetic_mario_hat",
        name="Mario's Hat",
        description="The iconic red cap with M logo.",
        icon="mario_hat.png",
        price=80,
        item_type="cosmetic",
    ),
    ShopItem(
        id="cosmetic_master_sword_glow",
        name="Master Sword Glow",
        description="Your sword glows with sacred power.",
        icon="sword_glow.png",
        price=120,
        item_type="cosmetic",
    ),
    ShopItem(
        id="cosmetic_banana_bunch",
        name="Banana Bunch",
        description="Carry a decorative banana bunch.",
        icon="banana_bunch.png",
        price=60,
        item_type="cosmetic",
    ),
]


class RewardSystem:
    """Manages currency and unlockable rewards.
    
    This class handles all reward-related operations including:
    - Adding and spending currency
    - Managing shop items (characters and cosmetics)
    - Tracking progress toward unlocks
    - Unlocking items when purchased
    
    Requirements: 11.1, 11.2, 11.3, 11.5, 11.6
    
    Attributes:
        data_manager: DataManager instance for persistence
    """
    
    def __init__(self, data_manager: DataManager):
        """Initialize the RewardSystem.
        
        Args:
            data_manager: DataManager instance for persistence
        """
        self._data_manager = data_manager
        self._shop_items = self._initialize_shop_items()
    
    def _initialize_shop_items(self) -> List[ShopItem]:
        """Initialize shop items with ownership status from database.
        
        Returns:
            List of shop items with current ownership status
        """
        # Load current game state to get owned items
        state = self._data_manager.load_state()
        owned_ids = {c.id for c in state.cosmetics if c.owned}
        
        # Create shop items with current ownership status
        items = []
        for item in DEFAULT_SHOP_ITEMS:
            # Check if item is owned (either default owned or in database)
            is_owned = item.owned or item.id in owned_ids
            items.append(ShopItem(
                id=item.id,
                name=item.name,
                description=item.description,
                icon=item.icon,
                price=item.price,
                item_type=item.item_type,
                owned=is_owned,
            ))
        
        return items
    
    def add_currency(self, amount: int, source: str) -> int:
        """Add currency to user's balance.
        
        Args:
            amount: Amount of currency to add (must be non-negative)
            source: Description of where the currency came from
            
        Returns:
            New currency balance after addition
            
        Raises:
            ValueError: If amount is negative
            
        Requirements: 11.1
        """
        if amount < 0:
            raise ValueError("Amount must be non-negative")
        
        # Load current state
        state = self._data_manager.load_state()
        
        # Add currency
        state.currency += amount
        
        # Save updated state
        self._data_manager.save_state(state)
        
        return state.currency
    
    def spend_currency(self, amount: int, item_id: str) -> bool:
        """Spend currency on an item.
        
        Args:
            amount: Amount of currency to spend
            item_id: ID of the item being purchased
            
        Returns:
            True if the transaction was successful, False if insufficient funds
            
        Requirements: 11.2, 11.3
        """
        if amount < 0:
            return False
        
        # Load current state
        state = self._data_manager.load_state()
        
        # Check if user has enough currency
        if state.currency < amount:
            return False
        
        # Deduct currency
        state.currency -= amount
        
        # Save updated state
        self._data_manager.save_state(state)
        
        return True
    
    def get_balance(self) -> int:
        """Get current currency balance.
        
        Returns:
            Current currency balance
        """
        state = self._data_manager.load_state()
        return state.currency
    
    def get_shop_items(self) -> List[ShopItem]:
        """Get available items for purchase.
        
        Returns:
            List of all shop items with current ownership status
            
        Requirements: 11.2, 11.3
        """
        # Refresh ownership status from database
        self._shop_items = self._initialize_shop_items()
        return self._shop_items
    
    def unlock_item(self, item_id: str) -> bool:
        """Unlock an item (character, cosmetic).
        
        This method handles the full purchase flow:
        1. Validates the item exists and is not already owned
        2. Checks if user has sufficient currency
        3. Deducts the price from user's balance
        4. Marks the item as owned
        
        Args:
            item_id: ID of the item to unlock
            
        Returns:
            True if the item was successfully unlocked, False otherwise
            
        Requirements: 11.2, 11.3, 11.6
        """
        # Find the item in shop
        item = None
        for shop_item in self._shop_items:
            if shop_item.id == item_id:
                item = shop_item
                break
        
        if item is None:
            return False  # Item not found
        
        if item.owned:
            return False  # Already owned
        
        # Load current state
        state = self._data_manager.load_state()
        
        # Check if user has enough currency
        if state.currency < item.price:
            return False  # Insufficient funds
        
        # Deduct currency
        state.currency -= item.price
        
        # Determine collectible type based on item type
        if item.item_type == "character":
            collectible_type = CollectibleType.CHARACTER_SKIN
        else:
            collectible_type = CollectibleType.COSMETIC
        
        # Create or update the collectible in state
        existing_collectible = None
        for c in state.cosmetics:
            if c.id == item_id:
                existing_collectible = c
                break
        
        if existing_collectible:
            # Update existing collectible
            existing_collectible.owned = True
            existing_collectible.acquired_at = datetime.now()
        else:
            # Create new collectible
            new_collectible = Collectible(
                id=item.id,
                type=collectible_type,
                theme=None,  # Universal items
                name=item.name,
                description=item.description,
                icon=item.icon,
                owned=True,
                equipped=False,
                acquired_at=datetime.now(),
                price=item.price,
            )
            state.cosmetics.append(new_collectible)
        
        # Save updated state
        self._data_manager.save_state(state)
        
        # Update local shop items cache
        for i, shop_item in enumerate(self._shop_items):
            if shop_item.id == item_id:
                self._shop_items[i] = ShopItem(
                    id=shop_item.id,
                    name=shop_item.name,
                    description=shop_item.description,
                    icon=shop_item.icon,
                    price=shop_item.price,
                    item_type=shop_item.item_type,
                    owned=True,
                )
                break
        
        return True
    
    def get_unlock_progress(self) -> UnlockProgress:
        """Get progress toward the next unlock.
        
        Finds the cheapest unowned item and calculates progress toward it.
        
        Returns:
            UnlockProgress with details about the next available unlock
            
        Requirements: 11.5
        """
        # Refresh shop items
        self._shop_items = self._initialize_shop_items()
        
        # Get current balance
        balance = self.get_balance()
        
        # Find the cheapest unowned item
        unowned_items = [item for item in self._shop_items if not item.owned]
        
        if not unowned_items:
            # All items owned
            return UnlockProgress(
                next_item=None,
                currency_needed=0,
                current_balance=balance,
                percentage=1.0,
            )
        
        # Sort by price to find cheapest
        unowned_items.sort(key=lambda x: x.price)
        next_item = unowned_items[0]
        
        # Calculate progress percentage
        if next_item.price == 0:
            percentage = 1.0
        else:
            percentage = min(1.0, balance / next_item.price)
        
        return UnlockProgress(
            next_item=next_item,
            currency_needed=next_item.price,
            current_balance=balance,
            percentage=percentage,
        )
    
    def get_owned_characters(self) -> List[ShopItem]:
        """Get list of owned characters.
        
        Returns:
            List of character items that the user owns
            
        Requirements: 11.6
        """
        self._shop_items = self._initialize_shop_items()
        return [
            item for item in self._shop_items 
            if item.item_type == "character" and item.owned
        ]
    
    def get_owned_cosmetics(self) -> List[ShopItem]:
        """Get list of owned cosmetics.
        
        Returns:
            List of cosmetic items that the user owns
        """
        self._shop_items = self._initialize_shop_items()
        return [
            item for item in self._shop_items 
            if item.item_type == "cosmetic" and item.owned
        ]
    
    def is_item_owned(self, item_id: str) -> bool:
        """Check if an item is owned.
        
        Args:
            item_id: ID of the item to check
            
        Returns:
            True if the item is owned, False otherwise
        """
        self._shop_items = self._initialize_shop_items()
        for item in self._shop_items:
            if item.id == item_id:
                return item.owned
        return False
