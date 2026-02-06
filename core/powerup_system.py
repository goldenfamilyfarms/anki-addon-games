"""
PowerUpSystem for NintendAnki.

This module manages power-ups and their effects, including granting theme-appropriate
power-ups, activating them, tracking inventory, and managing duration timers.

Requirements: 13.1, 13.2, 13.3, 13.4, 13.5, 13.6
"""

import uuid
from datetime import datetime
from typing import Dict, List, Optional

from data.data_manager import DataManager
from data.models import (
    ActivePowerUp,
    PowerUp,
    PowerUpType,
    Theme,
)


# Theme-appropriate power-ups mapping
# Each theme has a list of power-up types that can be granted
THEME_POWERUPS: Dict[Theme, List[PowerUpType]] = {
    Theme.MARIO: [
        PowerUpType.MUSHROOM,
        PowerUpType.FIRE_FLOWER,
        PowerUpType.STAR,
        PowerUpType.LEAF,
        PowerUpType.ONE_UP_MUSHROOM,
    ],
    Theme.ZELDA: [
        PowerUpType.HEART_CONTAINER,
        PowerUpType.FAIRY,
        PowerUpType.POTION,
        PowerUpType.SHIELD,
        PowerUpType.BOMB,
    ],
    Theme.DKC: [
        PowerUpType.BANANA,
        PowerUpType.BARREL,
        PowerUpType.ANIMAL_BUDDY,
        PowerUpType.GOLDEN_BANANA,
        PowerUpType.DK_COIN,
    ],
}

# Power-up metadata (name, description, icon, duration)
POWERUP_METADATA: Dict[PowerUpType, Dict] = {
    # Mario power-ups
    PowerUpType.MUSHROOM: {
        "name": "Super Mushroom",
        "description": "Grants extra health protection for your next wrong answer.",
        "icon": "mushroom.png",
        "duration_seconds": 0,  # Instant/permanent effect
    },
    PowerUpType.FIRE_FLOWER: {
        "name": "Fire Flower",
        "description": "Doubles points earned for the next 60 seconds.",
        "icon": "fire_flower.png",
        "duration_seconds": 60,
    },
    PowerUpType.STAR: {
        "name": "Super Star",
        "description": "Invincibility! No penalties for wrong answers for 30 seconds.",
        "icon": "star.png",
        "duration_seconds": 30,
    },
    PowerUpType.LEAF: {
        "name": "Super Leaf",
        "description": "Grants a second chance on your next wrong answer.",
        "icon": "leaf.png",
        "duration_seconds": 0,
    },
    PowerUpType.ONE_UP_MUSHROOM: {
        "name": "1-Up Mushroom",
        "description": "Restores full session health.",
        "icon": "1up_mushroom.png",
        "duration_seconds": 0,
    },
    
    # Zelda power-ups
    PowerUpType.HEART_CONTAINER: {
        "name": "Heart Container",
        "description": "Permanently increases maximum health.",
        "icon": "heart_container.png",
        "duration_seconds": 0,
    },
    PowerUpType.FAIRY: {
        "name": "Fairy",
        "description": "Automatically revives you when health reaches zero.",
        "icon": "fairy.png",
        "duration_seconds": 0,
    },
    PowerUpType.POTION: {
        "name": "Red Potion",
        "description": "Restores half of your session health.",
        "icon": "potion.png",
        "duration_seconds": 0,
    },
    PowerUpType.SHIELD: {
        "name": "Hylian Shield",
        "description": "Blocks the next penalty from a wrong answer.",
        "icon": "shield.png",
        "duration_seconds": 0,
    },
    PowerUpType.BOMB: {
        "name": "Bomb",
        "description": "Reveals a hint for the next difficult card.",
        "icon": "bomb.png",
        "duration_seconds": 0,
    },
    
    # DKC power-ups
    PowerUpType.BANANA: {
        "name": "Banana Bunch",
        "description": "Grants bonus points immediately.",
        "icon": "banana.png",
        "duration_seconds": 0,
    },
    PowerUpType.BARREL: {
        "name": "DK Barrel",
        "description": "Protects your streak from the next wrong answer.",
        "icon": "barrel.png",
        "duration_seconds": 0,
    },
    PowerUpType.ANIMAL_BUDDY: {
        "name": "Animal Buddy",
        "description": "Increases combo multiplier by 0.5x for 45 seconds.",
        "icon": "animal_buddy.png",
        "duration_seconds": 45,
    },
    PowerUpType.GOLDEN_BANANA: {
        "name": "Golden Banana",
        "description": "Triples points earned for the next 30 seconds.",
        "icon": "golden_banana.png",
        "duration_seconds": 30,
    },
    PowerUpType.DK_COIN: {
        "name": "DK Coin",
        "description": "Grants a large currency bonus.",
        "icon": "dk_coin.png",
        "duration_seconds": 0,
    },
    
    # Universal power-ups
    PowerUpType.DOUBLE_POINTS: {
        "name": "Double Points",
        "description": "Doubles all points earned for 60 seconds.",
        "icon": "double_points.png",
        "duration_seconds": 60,
    },
    PowerUpType.INVINCIBILITY: {
        "name": "Invincibility",
        "description": "No penalties for wrong answers for 30 seconds.",
        "icon": "invincibility.png",
        "duration_seconds": 30,
    },
    PowerUpType.HEALTH_RECOVERY: {
        "name": "Health Recovery",
        "description": "Restores session health to full.",
        "icon": "health_recovery.png",
        "duration_seconds": 0,
    },
    PowerUpType.TIME_FREEZE: {
        "name": "Time Freeze",
        "description": "Pauses any active timers for 30 seconds.",
        "icon": "time_freeze.png",
        "duration_seconds": 30,
    },
    PowerUpType.MULTIPLIER: {
        "name": "Score Multiplier",
        "description": "Increases score multiplier by 1.5x for 45 seconds.",
        "icon": "multiplier.png",
        "duration_seconds": 45,
    },
}


class PowerUpSystem:
    """Manages power-ups and their effects.
    
    This class handles:
    - Granting theme-appropriate power-ups to users
    - Activating power-ups from inventory
    - Tracking active power-ups with duration timers
    - Managing the power-up inventory
    
    Attributes:
        data_manager: DataManager instance for persistence
        _inventory: In-memory cache of power-ups in inventory
        _active_powerups: Currently active power-ups with timers
    """
    
    def __init__(self, data_manager: DataManager):
        """Initialize the PowerUpSystem.
        
        Args:
            data_manager: DataManager instance for persistence
        """
        self.data_manager = data_manager
        self._inventory: Dict[str, PowerUp] = {}
        self._active_powerups: Dict[str, ActivePowerUp] = {}
        self._load_inventory()
        self._load_active_powerups()
    
    def _load_inventory(self) -> None:
        """Load power-up inventory from database."""
        state = self.data_manager.load_state()
        for powerup in state.powerups:
            self._inventory[powerup.id] = powerup
    
    def _load_active_powerups(self) -> None:
        """Load active power-ups from database."""
        conn = self.data_manager._get_connection()
        cursor = conn.cursor()
        
        # Query active_powerups joined with powerups to get full powerup data
        cursor.execute("""
            SELECT ap.id, ap.powerup_id, ap.activated_at, ap.duration_seconds, ap.remaining_seconds,
                   p.type, p.theme, p.name, p.description, p.icon, p.quantity, 
                   p.duration_seconds as powerup_duration, p.acquired_at
            FROM active_powerups ap
            JOIN powerups p ON ap.powerup_id = p.id
        """)
        
        for row in cursor.fetchall():
            powerup_id = row["powerup_id"]
            
            # Reconstruct the PowerUp from the database row
            theme = Theme(row["theme"]) if row["theme"] else None
            powerup = PowerUp(
                id=powerup_id,
                type=PowerUpType(row["type"]),
                theme=theme,
                name=row["name"],
                description=row["description"],
                icon=row["icon"],
                quantity=row["quantity"],
                duration_seconds=row["powerup_duration"],
                acquired_at=row["acquired_at"],
            )
            
            self._active_powerups[row["id"]] = ActivePowerUp(
                powerup_id=powerup_id,
                powerup=powerup,
                activated_at=row["activated_at"],
                duration_seconds=row["duration_seconds"],
                remaining_seconds=row["remaining_seconds"],
            )
    
    def _save_powerup(self, powerup: PowerUp) -> None:
        """Save a power-up to the database."""
        conn = self.data_manager._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT OR REPLACE INTO powerups
            (id, type, theme, name, description, icon, quantity, duration_seconds, acquired_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            powerup.id,
            powerup.type.value,
            powerup.theme.value if powerup.theme else None,
            powerup.name,
            powerup.description,
            powerup.icon,
            powerup.quantity,
            powerup.duration_seconds,
            powerup.acquired_at,
        ))
        conn.commit()
    
    def _save_active_powerup(self, active_id: str, active: ActivePowerUp) -> None:
        """Save an active power-up to the database."""
        conn = self.data_manager._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT OR REPLACE INTO active_powerups
            (id, powerup_id, activated_at, duration_seconds, remaining_seconds)
            VALUES (?, ?, ?, ?, ?)
        """, (
            active_id,
            active.powerup_id,
            active.activated_at,
            active.duration_seconds,
            active.remaining_seconds,
        ))
        conn.commit()
    
    def _remove_active_powerup(self, active_id: str) -> None:
        """Remove an active power-up from the database."""
        conn = self.data_manager._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM active_powerups WHERE id = ?", (active_id,))
        conn.commit()
    
    def _remove_powerup_from_db(self, powerup_id: str) -> None:
        """Remove a power-up from the database."""
        conn = self.data_manager._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM powerups WHERE id = ?", (powerup_id,))
        conn.commit()
    
    def grant_powerup(self, powerup_type: PowerUpType, theme: Theme) -> PowerUp:
        """Grant a power-up to the user.
        
        Creates a new power-up of the specified type and adds it to the
        user's inventory. The power-up is associated with the given theme.
        
        Args:
            powerup_type: The type of power-up to grant
            theme: The theme this power-up is associated with
            
        Returns:
            The newly created PowerUp instance
            
        Requirements: 13.1, 13.2, 13.3
        """
        # Get metadata for this power-up type
        metadata = POWERUP_METADATA.get(powerup_type, {
            "name": powerup_type.value.replace("_", " ").title(),
            "description": f"A {powerup_type.value} power-up.",
            "icon": f"{powerup_type.value}.png",
            "duration_seconds": 0,
        })
        
        # Check if we already have this type of power-up in inventory
        existing = self._find_powerup_by_type(powerup_type, theme)
        
        if existing:
            # Increment quantity of existing power-up
            existing.quantity += 1
            self._save_powerup(existing)
            return existing
        
        # Create new power-up
        powerup = PowerUp(
            id=str(uuid.uuid4()),
            type=powerup_type,
            theme=theme,
            name=metadata["name"],
            description=metadata["description"],
            icon=metadata["icon"],
            quantity=1,
            duration_seconds=metadata["duration_seconds"],
            acquired_at=datetime.now(),
        )
        
        # Add to inventory and persist
        self._inventory[powerup.id] = powerup
        self._save_powerup(powerup)
        
        return powerup
    
    def _find_powerup_by_type(self, powerup_type: PowerUpType, theme: Optional[Theme]) -> Optional[PowerUp]:
        """Find an existing power-up by type and theme."""
        for powerup in self._inventory.values():
            if powerup.type == powerup_type and powerup.theme == theme:
                return powerup
        return None
    
    def activate_powerup(self, powerup_id: str) -> bool:
        """Activate a power-up from inventory.
        
        Activates the specified power-up, applying its effect. For timed
        power-ups, starts the duration countdown. For instant power-ups,
        applies the effect immediately.
        
        Args:
            powerup_id: ID of the power-up to activate
            
        Returns:
            True if activation was successful, False otherwise
            
        Requirements: 13.4
        """
        # Check if power-up exists in inventory
        if powerup_id not in self._inventory:
            return False
        
        powerup = self._inventory[powerup_id]
        
        # Check if we have any quantity available
        if powerup.quantity <= 0:
            return False
        
        # Decrement quantity
        powerup.quantity -= 1
        
        # If this is a timed power-up, add to active list
        if powerup.duration_seconds > 0:
            active_id = str(uuid.uuid4())
            active = ActivePowerUp(
                powerup_id=powerup_id,
                powerup=powerup,
                activated_at=datetime.now(),
                duration_seconds=powerup.duration_seconds,
                remaining_seconds=float(powerup.duration_seconds),
            )
            self._active_powerups[active_id] = active
            self._save_active_powerup(active_id, active)
        
        # Update or remove from inventory
        if powerup.quantity <= 0:
            del self._inventory[powerup_id]
            # Only remove from DB if there are no active instances of this powerup
            # Keep the record for active powerup reference
            if powerup.duration_seconds > 0:
                # Keep in DB with quantity 0 for active powerup reference
                self._save_powerup(powerup)
            else:
                # Instant powerup, safe to remove
                self._remove_powerup_from_db(powerup_id)
        else:
            self._save_powerup(powerup)
        
        return True
    
    def get_active_powerups(self) -> List[ActivePowerUp]:
        """Get currently active power-ups with remaining duration.
        
        Returns a list of all power-ups that are currently active,
        including their remaining duration for timed effects.
        
        Returns:
            List of ActivePowerUp instances
            
        Requirements: 13.5, 13.6
        """
        return list(self._active_powerups.values())
    
    def get_inventory(self) -> List[PowerUp]:
        """Get all power-ups in inventory.
        
        Returns a list of all power-ups the user has collected but
        not yet used.
        
        Returns:
            List of PowerUp instances in inventory
            
        Requirements: 13.3, 13.5
        """
        return list(self._inventory.values())
    
    def tick(self, delta_time: float) -> List[PowerUp]:
        """Update active power-up timers.
        
        Decrements the remaining time on all active timed power-ups.
        Power-ups that expire are removed from the active list.
        
        Args:
            delta_time: Time elapsed since last tick in seconds
            
        Returns:
            List of power-ups that expired during this tick
            
        Requirements: 13.6
        """
        expired: List[PowerUp] = []
        expired_ids: List[str] = []
        
        for active_id, active in self._active_powerups.items():
            # Decrement remaining time
            active.remaining_seconds -= delta_time
            
            # Check if expired
            if active.remaining_seconds <= 0:
                expired.append(active.powerup)
                expired_ids.append(active_id)
            else:
                # Update in database
                self._save_active_powerup(active_id, active)
        
        # Remove expired power-ups
        for active_id in expired_ids:
            del self._active_powerups[active_id]
            self._remove_active_powerup(active_id)
        
        return expired
    
    def get_theme_powerup_types(self, theme: Theme) -> List[PowerUpType]:
        """Get the list of power-up types available for a theme.
        
        Args:
            theme: The theme to get power-up types for
            
        Returns:
            List of PowerUpType values appropriate for the theme
        """
        return THEME_POWERUPS.get(theme, [])
    
    def has_active_powerup_of_type(self, powerup_type: PowerUpType) -> bool:
        """Check if there's an active power-up of the specified type.
        
        Args:
            powerup_type: The type of power-up to check for
            
        Returns:
            True if an active power-up of this type exists
        """
        for active in self._active_powerups.values():
            if active.powerup.type == powerup_type:
                return True
        return False
    
    def get_powerup_count(self, powerup_type: PowerUpType, theme: Optional[Theme] = None) -> int:
        """Get the total count of a specific power-up type in inventory.
        
        Args:
            powerup_type: The type of power-up to count
            theme: Optional theme filter
            
        Returns:
            Total quantity of the specified power-up type
        """
        total = 0
        for powerup in self._inventory.values():
            if powerup.type == powerup_type:
                if theme is None or powerup.theme == theme:
                    total += powerup.quantity
        return total
    
    def clear_all_active(self) -> None:
        """Clear all active power-ups (for testing or session reset)."""
        for active_id in list(self._active_powerups.keys()):
            self._remove_active_powerup(active_id)
        self._active_powerups.clear()
