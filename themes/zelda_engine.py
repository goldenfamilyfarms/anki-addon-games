"""
ZeldaEngine for NintendAnki.

This module implements the ZeldaEngine class that provides Zelda-themed
game mechanics including adventure exploration, boss battles, and
item equipment system.

Requirements: 5.1, 5.2, 5.3, 5.4, 5.5, 5.6, 5.7, 5.8
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, TYPE_CHECKING

from core.theme_manager import ThemeEngine
from data.models import (
    Animation,
    AnimationType,
    Collectible,
    CollectibleType,
    Level,
    LevelView,
    Theme,
    ThemeStats,
)

if TYPE_CHECKING:
    from data.data_manager import DataManager


class ZeldaItemCategory(str, Enum):
    """Categories for Zelda items.
    
    Requirements: 5.6
    """
    FUNCTIONAL = "functional"  # Usable during reviews, provides bonuses
    COSMETIC = "cosmetic"      # Visual only, no gameplay effect


class ZeldaItemEffect(str, Enum):
    """Effects that functional Zelda items can provide.
    
    Requirements: 5.7
    """
    HINT = "hint"              # Provides a hint for the current card
    EXTRA_TIME = "extra_time"  # Gives extra time to answer
    SECOND_CHANCE = "second_chance"  # Allows a retry on wrong answer


@dataclass
class ZeldaItem:
    """A Zelda-themed item that can be equipped.
    
    Items are categorized as either functional (providing review bonuses)
    or cosmetic (visual only).
    
    Requirements: 5.6, 5.7
    
    Attributes:
        id: Unique identifier for the item
        name: Display name of the item
        description: Description of the item
        icon: Path to the item icon
        category: Whether the item is functional or cosmetic
        effect: The effect provided if functional (None for cosmetic)
        effect_value: Numeric value for the effect (e.g., extra seconds)
        owned: Whether the player owns this item
        equipped: Whether the item is currently equipped
        acquired_at: When the item was acquired
    """
    id: str
    name: str
    description: str
    icon: str
    category: ZeldaItemCategory
    effect: Optional[ZeldaItemEffect] = None
    effect_value: int = 0
    owned: bool = False
    equipped: bool = False
    acquired_at: Optional[datetime] = None


@dataclass
class BossBattle:
    """Represents a boss battle sequence.
    
    Boss battles are triggered when a user completes all cards in a deck.
    
    Requirements: 5.4
    
    Attributes:
        id: Unique identifier for the battle
        deck_id: ID of the deck that triggered the battle
        boss_name: Name of the boss
        boss_icon: Path to boss sprite
        difficulty: Difficulty level (1-5)
        started_at: When the battle started
        completed: Whether the battle is complete
        won: Whether the player won
    """
    id: str
    deck_id: int
    boss_name: str
    boss_icon: str
    difficulty: int = 1
    started_at: Optional[datetime] = None
    completed: bool = False
    won: bool = False


@dataclass
class BossReward:
    """Rewards earned from completing a boss battle.
    
    Requirements: 5.5
    
    Attributes:
        battle_id: ID of the completed battle
        item_awarded: The special item awarded (heart container, weapon, or key item)
        currency_earned: Currency awarded
        experience_earned: Experience points awarded
    """
    battle_id: str
    item_awarded: Optional[ZeldaItem] = None
    currency_earned: int = 0
    experience_earned: int = 0


@dataclass
class MapRegion:
    """A region on the adventure map.
    
    Requirements: 5.8
    
    Attributes:
        id: Unique identifier for the region
        name: Display name of the region
        explored: Whether the region has been explored
        deck_id: Associated deck ID (if any)
        position: Position on the map (x, y)
        connected_regions: IDs of connected regions
    """
    id: str
    name: str
    explored: bool = False
    deck_id: Optional[int] = None
    position: tuple = (0, 0)
    connected_regions: List[str] = field(default_factory=list)


@dataclass
class AdventureMap:
    """The adventure map showing explored and unexplored regions.
    
    Requirements: 5.1, 5.8
    
    Attributes:
        regions: List of map regions
        current_region: Currently active region
        total_explored: Number of explored regions
        total_regions: Total number of regions
        background: Path to map background image
    """
    regions: List[MapRegion]
    current_region: Optional[MapRegion] = None
    total_explored: int = 0
    total_regions: int = 0
    background: str = "assets/zelda/adventure_map.png"


# Predefined boss names for variety
BOSS_NAMES = [
    "Phantom Ganon",
    "King Dodongo",
    "Barinade",
    "Volvagia",
    "Morpha",
    "Bongo Bongo",
    "Twinrova",
    "Dark Link",
    "Gleeok",
    "Moldorm",
]

# Predefined special items that can be awarded from boss battles
SPECIAL_ITEMS = {
    "heart_container": ZeldaItem(
        id="zelda_heart_container",
        name="Heart Container",
        description="Increases your maximum health",
        icon="assets/zelda/heart_container.png",
        category=ZeldaItemCategory.FUNCTIONAL,
        effect=ZeldaItemEffect.SECOND_CHANCE,
        effect_value=1,
    ),
    "master_sword": ZeldaItem(
        id="zelda_master_sword",
        name="Master Sword",
        description="The legendary blade that seals darkness",
        icon="assets/zelda/master_sword.png",
        category=ZeldaItemCategory.FUNCTIONAL,
        effect=ZeldaItemEffect.HINT,
        effect_value=1,
    ),
    "hylian_shield": ZeldaItem(
        id="zelda_hylian_shield",
        name="Hylian Shield",
        description="A sturdy shield bearing the royal crest",
        icon="assets/zelda/hylian_shield.png",
        category=ZeldaItemCategory.FUNCTIONAL,
        effect=ZeldaItemEffect.SECOND_CHANCE,
        effect_value=1,
    ),
    "fairy_bow": ZeldaItem(
        id="zelda_fairy_bow",
        name="Fairy Bow",
        description="A bow blessed by the Great Fairies",
        icon="assets/zelda/fairy_bow.png",
        category=ZeldaItemCategory.FUNCTIONAL,
        effect=ZeldaItemEffect.EXTRA_TIME,
        effect_value=30,
    ),
    "hookshot": ZeldaItem(
        id="zelda_hookshot",
        name="Hookshot",
        description="Extends to grab distant objects",
        icon="assets/zelda/hookshot.png",
        category=ZeldaItemCategory.FUNCTIONAL,
        effect=ZeldaItemEffect.HINT,
        effect_value=1,
    ),
}


# Cosmetic items
COSMETIC_ITEMS = {
    "green_tunic": ZeldaItem(
        id="zelda_green_tunic",
        name="Green Tunic",
        description="The classic hero's garb",
        icon="assets/zelda/green_tunic.png",
        category=ZeldaItemCategory.COSMETIC,
    ),
    "blue_tunic": ZeldaItem(
        id="zelda_blue_tunic",
        name="Blue Tunic",
        description="Allows breathing underwater",
        icon="assets/zelda/blue_tunic.png",
        category=ZeldaItemCategory.COSMETIC,
    ),
    "red_tunic": ZeldaItem(
        id="zelda_red_tunic",
        name="Red Tunic",
        description="Protects against extreme heat",
        icon="assets/zelda/red_tunic.png",
        category=ZeldaItemCategory.COSMETIC,
    ),
    "triforce_piece": ZeldaItem(
        id="zelda_triforce_piece",
        name="Triforce Piece",
        description="A fragment of the sacred golden power",
        icon="assets/zelda/triforce.png",
        category=ZeldaItemCategory.COSMETIC,
    ),
}


class ZeldaEngine(ThemeEngine):
    """Zelda theme engine with exploration mechanics.
    
    Implements the ThemeEngine interface with Zelda-specific behavior:
    - Correct answers: Character explores and finds items
    - Wrong answers: Character takes damage from enemies
    - Boss battles: Triggered on deck completion
    - Adventure map: Shows explored/unexplored regions
    - Item system: Functional and cosmetic items
    
    Requirements: 5.1, 5.2, 5.3, 5.4, 5.5, 5.6, 5.7, 5.8
    
    Attributes:
        data_manager: DataManager for accessing game state
        _hearts: Current heart count
        _equipped_item: Currently equipped functional item
        _owned_items: List of owned items
        _active_boss_battle: Current boss battle (if any)
    """
    
    # Animation configuration
    DEFAULT_FPS = 30
    EXPLORE_FRAMES = [0, 1, 2, 3, 4, 5]  # Exploration animation frames
    DAMAGE_FRAMES = [0, 1, 2, 3]  # Damage animation frames
    ATTACK_FRAMES = [0, 1, 2, 3, 4]  # Attack animation frames
    IDLE_FRAMES = [0, 1]  # Idle animation frames

    
    def __init__(self, data_manager: 'DataManager'):
        """Initialize the ZeldaEngine.
        
        Args:
            data_manager: DataManager for accessing game state and theme data
        """
        self.data_manager = data_manager
        self._hearts = 3
        self._equipped_item: Optional[ZeldaItem] = None
        self._owned_items: List[ZeldaItem] = []
        self._active_boss_battle: Optional[BossBattle] = None
        self._load_theme_state()
    
    def _load_theme_state(self) -> None:
        """Load Zelda-specific state from the database."""
        game_state = self.data_manager.load_state()
        theme_state = game_state.theme_specific.get(Theme.ZELDA)
        if theme_state:
            self._hearts = theme_state.hearts
            # Load items from extra_data if available
            if theme_state.extra_data:
                self._load_items_from_extra_data(theme_state.extra_data)
    
    def _load_items_from_extra_data(self, extra_data: Dict) -> None:
        """Load owned items from extra_data dictionary.
        
        Args:
            extra_data: Dictionary containing item data
        """
        owned_item_ids = extra_data.get("owned_items", [])
        equipped_item_id = extra_data.get("equipped_item")
        
        # Reconstruct owned items
        all_items = {**SPECIAL_ITEMS, **COSMETIC_ITEMS}
        for item_id in owned_item_ids:
            if item_id in all_items:
                item = ZeldaItem(
                    id=all_items[item_id].id,
                    name=all_items[item_id].name,
                    description=all_items[item_id].description,
                    icon=all_items[item_id].icon,
                    category=all_items[item_id].category,
                    effect=all_items[item_id].effect,
                    effect_value=all_items[item_id].effect_value,
                    owned=True,
                )
                self._owned_items.append(item)
                if item_id == equipped_item_id:
                    item.equipped = True
                    self._equipped_item = item

    
    def _save_theme_state(self) -> None:
        """Save Zelda-specific state to the database."""
        game_state = self.data_manager.load_state()
        theme_state = game_state.theme_specific.get(Theme.ZELDA)
        if theme_state:
            theme_state.hearts = self._hearts
            # Save items to extra_data
            theme_state.extra_data = {
                "owned_items": [item.id for item in self._owned_items],
                "equipped_item": self._equipped_item.id if self._equipped_item else None,
            }
            self.data_manager.save_state(game_state)
    
    def get_animation_for_correct(self) -> Animation:
        """Get animation to play for correct answer.
        
        Returns an animation showing Link exploring and collecting items.
        The animation includes the character movement and item discovery
        visual effect.
        
        Requirements: 5.2
        
        Returns:
            Animation for exploration/item collection
        """
        return Animation(
            type=AnimationType.COLLECT,
            theme=Theme.ZELDA,
            sprite_sheet="assets/zelda/link_explore.png",
            frames=self.EXPLORE_FRAMES,
            fps=self.DEFAULT_FPS,
            loop=False
        )
    
    def get_animation_for_wrong(self) -> Animation:
        """Get animation to play for wrong answer.
        
        Returns an animation showing Link taking damage from an enemy.
        The animation includes the character flinching and damage effect.
        
        Requirements: 5.3
        
        Returns:
            Animation for taking enemy damage
        """
        return Animation(
            type=AnimationType.DAMAGE,
            theme=Theme.ZELDA,
            sprite_sheet="assets/zelda/link_damage.png",
            frames=self.DAMAGE_FRAMES,
            fps=self.DEFAULT_FPS,
            loop=False
        )

    
    def get_collectible_for_correct(self) -> Collectible:
        """Get collectible earned for correct answer.
        
        Returns a rupee collectible that is added to the player's
        collection when they answer correctly.
        
        Returns:
            Rupee collectible
        """
        return Collectible(
            id="zelda_rupee",
            type=CollectibleType.RUPEE,
            theme=Theme.ZELDA,
            name="Green Rupee",
            description="A green rupee found while exploring",
            icon="assets/zelda/rupee_green.png",
            owned=True
        )
    
    def get_level_view(self, level: Level) -> LevelView:
        """Get the visual representation of a level.
        
        Returns a LevelView configured for Zelda-style adventure
        gameplay with appropriate dungeon/overworld background.
        
        Requirements: 5.1
        
        Args:
            level: The level to get the view for
            
        Returns:
            LevelView with Zelda-style visual representation
        """
        # Generate collectible positions based on level
        collectibles = self._generate_level_collectibles(level)
        
        return LevelView(
            level=level,
            background=f"assets/zelda/dungeon_{level.level_number}_bg.png",
            character_position=(100, 200),  # Starting position
            collectibles_visible=collectibles
        )
    
    def _generate_level_collectibles(self, level: Level) -> List[Collectible]:
        """Generate collectibles for a level.
        
        Creates a list of rupee and heart collectibles for the level.
        
        Args:
            level: The level to generate collectibles for
            
        Returns:
            List of collectibles for the level
        """
        collectibles = []
        # Generate rupees based on level number
        num_rupees = 3 + level.level_number
        
        for i in range(num_rupees):
            collectibles.append(Collectible(
                id=f"level_{level.level_number}_rupee_{i}",
                type=CollectibleType.RUPEE,
                theme=Theme.ZELDA,
                name="Rupee",
                description="A collectible rupee",
                icon="assets/zelda/rupee_green.png",
                owned=False
            ))
        
        # Add a heart every 3 levels
        if level.level_number % 3 == 0:
            collectibles.append(Collectible(
                id=f"level_{level.level_number}_heart",
                type=CollectibleType.HEART,
                theme=Theme.ZELDA,
                name="Heart",
                description="Restores health",
                icon="assets/zelda/heart.png",
                owned=False
            ))
        
        return collectibles

    
    def get_dashboard_stats(self) -> ThemeStats:
        """Get theme-specific stats for dashboard.
        
        Returns Zelda-specific statistics including rupee count,
        heart count, and map completion for display in the dashboard.
        
        Returns:
            ThemeStats with Zelda-specific statistics
        """
        game_state = self.data_manager.load_state()
        theme_state = game_state.theme_specific.get(Theme.ZELDA)
        
        hearts = theme_state.hearts if theme_state else 3
        
        # Calculate map completion
        completion = self._calculate_map_completion()
        
        # Count rupees (from currency or theme-specific tracking)
        rupees = game_state.currency  # Using main currency as rupees
        
        return ThemeStats(
            theme=Theme.ZELDA,
            primary_collectible_name="Rupees",
            primary_collectible_count=rupees,
            secondary_stat_name="Hearts",
            secondary_stat_value=hearts,
            completion_percentage=completion
        )
    
    def _calculate_map_completion(self) -> float:
        """Calculate the adventure map completion percentage.
        
        Based on explored regions vs total regions.
        
        Returns:
            Completion percentage (0.0 to 1.0)
        """
        adventure_map = self.get_adventure_map()
        if adventure_map.total_regions == 0:
            return 0.0
        return adventure_map.total_explored / adventure_map.total_regions
    
    def trigger_boss_battle(self, deck_id: int) -> BossBattle:
        """Trigger a boss battle for deck completion.
        
        Creates a new boss battle when a user completes all cards in a deck.
        The boss is selected based on the deck_id for variety.
        
        Requirements: 5.4
        
        Args:
            deck_id: ID of the completed deck
            
        Returns:
            BossBattle instance representing the battle
        """
        import hashlib
        
        # Select boss based on deck_id for consistent but varied selection
        boss_index = deck_id % len(BOSS_NAMES)
        boss_name = BOSS_NAMES[boss_index]
        
        # Calculate difficulty based on deck_id (1-5)
        difficulty = min(5, max(1, (deck_id % 5) + 1))
        
        # Generate unique battle ID
        battle_id = hashlib.md5(f"boss_{deck_id}_{datetime.now().isoformat()}".encode()).hexdigest()[:12]
        
        battle = BossBattle(
            id=battle_id,
            deck_id=deck_id,
            boss_name=boss_name,
            boss_icon=f"assets/zelda/boss_{boss_name.lower().replace(' ', '_')}.png",
            difficulty=difficulty,
            started_at=datetime.now(),
            completed=False,
            won=False
        )
        
        self._active_boss_battle = battle
        return battle

    
    def complete_boss_battle(self, battle: BossBattle, won: bool) -> BossReward:
        """Complete a boss battle and calculate rewards.
        
        Awards a special item if the player wins the battle.
        Special items include heart containers, new weapons, or key items.
        
        Requirements: 5.5
        
        Args:
            battle: The boss battle to complete
            won: Whether the player won the battle
            
        Returns:
            BossReward with items and currency earned
        """
        battle.completed = True
        battle.won = won
        
        if self._active_boss_battle and self._active_boss_battle.id == battle.id:
            self._active_boss_battle = None
        
        if not won:
            return BossReward(
                battle_id=battle.id,
                item_awarded=None,
                currency_earned=10,  # Consolation prize
                experience_earned=50
            )
        
        # Award a special item based on difficulty
        item = self._select_boss_reward(battle.difficulty)
        
        # Add item to owned items if not already owned
        if item and not any(i.id == item.id for i in self._owned_items):
            item.owned = True
            item.acquired_at = datetime.now()
            self._owned_items.append(item)
            self._save_theme_state()
        
        # Calculate currency and experience based on difficulty
        currency = 50 * battle.difficulty
        experience = 100 * battle.difficulty
        
        return BossReward(
            battle_id=battle.id,
            item_awarded=item,
            currency_earned=currency,
            experience_earned=experience
        )
    
    def _select_boss_reward(self, difficulty: int) -> ZeldaItem:
        """Select a reward item based on boss difficulty.
        
        Higher difficulty bosses award better items.
        
        Args:
            difficulty: Boss difficulty (1-5)
            
        Returns:
            ZeldaItem to award
        """
        # Map difficulty to item rewards
        reward_map = {
            1: "heart_container",
            2: "hylian_shield",
            3: "fairy_bow",
            4: "hookshot",
            5: "master_sword",
        }
        
        item_key = reward_map.get(difficulty, "heart_container")
        template = SPECIAL_ITEMS[item_key]
        
        return ZeldaItem(
            id=template.id,
            name=template.name,
            description=template.description,
            icon=template.icon,
            category=template.category,
            effect=template.effect,
            effect_value=template.effect_value,
            owned=True,
            acquired_at=datetime.now()
        )

    
    def get_adventure_map(self) -> AdventureMap:
        """Get the adventure map with explored regions.
        
        Returns the adventure map showing which regions have been
        explored based on deck progress.
        
        Requirements: 5.1, 5.8
        
        Returns:
            AdventureMap with region exploration status
        """
        game_state = self.data_manager.load_state()
        theme_state = game_state.theme_specific.get(Theme.ZELDA)
        
        # Get map progress from theme state
        map_data = {}
        if theme_state and theme_state.map_progress:
            map_data = theme_state.map_progress
        
        # Generate regions based on levels/decks
        regions = self._generate_map_regions(game_state, map_data)
        
        # Find current region (first unexplored or last explored)
        current_region = None
        for region in regions:
            if not region.explored:
                current_region = region
                break
        if current_region is None and regions:
            current_region = regions[-1]
        
        total_explored = sum(1 for r in regions if r.explored)
        
        return AdventureMap(
            regions=regions,
            current_region=current_region,
            total_explored=total_explored,
            total_regions=len(regions),
            background="assets/zelda/adventure_map.png"
        )
    
    def _generate_map_regions(self, game_state, map_data: Dict) -> List[MapRegion]:
        """Generate map regions based on game progress.
        
        Args:
            game_state: Current game state
            map_data: Saved map progress data
            
        Returns:
            List of MapRegion instances
        """
        # Define base regions
        region_templates = [
            ("hyrule_field", "Hyrule Field", (200, 300)),
            ("kokiri_forest", "Kokiri Forest", (100, 400)),
            ("death_mountain", "Death Mountain", (350, 150)),
            ("zoras_domain", "Zora's Domain", (450, 250)),
            ("lake_hylia", "Lake Hylia", (300, 450)),
            ("gerudo_valley", "Gerudo Valley", (50, 200)),
            ("kakariko_village", "Kakariko Village", (250, 200)),
            ("lost_woods", "Lost Woods", (150, 350)),
            ("temple_of_time", "Temple of Time", (300, 250)),
            ("hyrule_castle", "Hyrule Castle", (300, 100)),
        ]
        
        regions = []
        explored_ids = map_data.get("explored_regions", [])
        
        # Determine how many regions should be unlocked based on progress
        correct_answers = game_state.progression.correct_answers
        unlocked_count = min(len(region_templates), max(1, correct_answers // 25 + 1))
        
        for i, (region_id, name, position) in enumerate(region_templates[:unlocked_count]):
            explored = region_id in explored_ids or i == 0  # First region always explored
            
            # Connect to adjacent regions
            connected = []
            if i > 0:
                connected.append(region_templates[i-1][0])
            if i < len(region_templates) - 1 and i < unlocked_count - 1:
                connected.append(region_templates[i+1][0])
            
            regions.append(MapRegion(
                id=region_id,
                name=name,
                explored=explored,
                position=position,
                connected_regions=connected
            ))
        
        return regions

    
    def get_equipped_item(self) -> Optional[ZeldaItem]:
        """Get currently equipped functional item.
        
        Returns the item that is currently equipped and providing
        review bonuses, or None if no item is equipped.
        
        Requirements: 5.7
        
        Returns:
            Currently equipped ZeldaItem or None
        """
        return self._equipped_item
    
    def equip_item(self, item_id: str) -> bool:
        """Equip a functional item.
        
        Equips the specified item if it is owned and is a functional item.
        Only one functional item can be equipped at a time.
        
        Requirements: 5.7
        
        Args:
            item_id: ID of the item to equip
            
        Returns:
            True if item was successfully equipped, False otherwise
        """
        # Find the item in owned items
        item_to_equip = None
        for item in self._owned_items:
            if item.id == item_id:
                item_to_equip = item
                break
        
        # Check if item exists and is owned
        if item_to_equip is None:
            return False
        
        # Check if item is functional (only functional items can be equipped)
        if item_to_equip.category != ZeldaItemCategory.FUNCTIONAL:
            return False
        
        # Unequip current item
        if self._equipped_item:
            self._equipped_item.equipped = False
        
        # Equip new item
        item_to_equip.equipped = True
        self._equipped_item = item_to_equip
        
        # Save state
        self._save_theme_state()
        
        return True
    
    def unequip_item(self) -> bool:
        """Unequip the currently equipped item.
        
        Returns:
            True if an item was unequipped, False if nothing was equipped
        """
        if self._equipped_item is None:
            return False
        
        self._equipped_item.equipped = False
        self._equipped_item = None
        self._save_theme_state()
        
        return True

    
    def get_owned_items(self) -> List[ZeldaItem]:
        """Get all owned items.
        
        Returns:
            List of all owned ZeldaItems
        """
        return list(self._owned_items)
    
    def get_functional_items(self) -> List[ZeldaItem]:
        """Get all owned functional items.
        
        Requirements: 5.6
        
        Returns:
            List of owned functional items
        """
        return [item for item in self._owned_items 
                if item.category == ZeldaItemCategory.FUNCTIONAL]
    
    def get_cosmetic_items(self) -> List[ZeldaItem]:
        """Get all owned cosmetic items.
        
        Requirements: 5.6
        
        Returns:
            List of owned cosmetic items
        """
        return [item for item in self._owned_items 
                if item.category == ZeldaItemCategory.COSMETIC]
    
    def get_item_effect(self) -> Optional[tuple]:
        """Get the effect of the currently equipped item.
        
        Returns the effect type and value if an item is equipped.
        
        Requirements: 5.7
        
        Returns:
            Tuple of (ZeldaItemEffect, effect_value) or None
        """
        if self._equipped_item is None:
            return None
        
        if self._equipped_item.effect is None:
            return None
        
        return (self._equipped_item.effect, self._equipped_item.effect_value)
    
    def add_item(self, item: ZeldaItem) -> bool:
        """Add an item to the player's inventory.
        
        Args:
            item: The item to add
            
        Returns:
            True if item was added, False if already owned
        """
        if any(i.id == item.id for i in self._owned_items):
            return False
        
        item.owned = True
        if item.acquired_at is None:
            item.acquired_at = datetime.now()
        self._owned_items.append(item)
        self._save_theme_state()
        
        return True

    
    def get_hearts(self) -> int:
        """Get current heart count.
        
        Returns:
            Current number of hearts
        """
        return self._hearts
    
    def set_hearts(self, hearts: int) -> None:
        """Set the heart count.
        
        Args:
            hearts: New heart count (minimum 0)
        """
        self._hearts = max(0, hearts)
        self._save_theme_state()
    
    def get_attack_animation(self) -> Animation:
        """Get the attack animation for Link.
        
        Returns:
            Animation for Link attacking
        """
        return Animation(
            type=AnimationType.ATTACK,
            theme=Theme.ZELDA,
            sprite_sheet="assets/zelda/link_attack.png",
            frames=self.ATTACK_FRAMES,
            fps=self.DEFAULT_FPS,
            loop=False
        )
    
    def get_idle_animation(self) -> Animation:
        """Get the idle animation for Link.
        
        Returns:
            Animation for Link idle state
        """
        return Animation(
            type=AnimationType.IDLE,
            theme=Theme.ZELDA,
            sprite_sheet="assets/zelda/link_idle.png",
            frames=self.IDLE_FRAMES,
            fps=15,  # Slower for idle
            loop=True
        )
    
    def get_victory_animation(self) -> Animation:
        """Get the victory animation for Link.
        
        Returns:
            Animation for Link victory pose
        """
        return Animation(
            type=AnimationType.VICTORY,
            theme=Theme.ZELDA,
            sprite_sheet="assets/zelda/link_victory.png",
            frames=[0, 1, 2, 3],
            fps=self.DEFAULT_FPS,
            loop=False
        )
    
    def get_active_boss_battle(self) -> Optional[BossBattle]:
        """Get the currently active boss battle.
        
        Returns:
            Active BossBattle or None
        """
        return self._active_boss_battle
    
    def explore_region(self, region_id: str) -> bool:
        """Mark a region as explored.
        
        Args:
            region_id: ID of the region to explore
            
        Returns:
            True if region was newly explored, False otherwise
        """
        game_state = self.data_manager.load_state()
        theme_state = game_state.theme_specific.get(Theme.ZELDA)
        
        if theme_state is None:
            return False
        
        if theme_state.map_progress is None:
            theme_state.map_progress = {"explored_regions": []}
        
        explored = theme_state.map_progress.get("explored_regions", [])
        
        if region_id in explored:
            return False
        
        explored.append(region_id)
        theme_state.map_progress["explored_regions"] = explored
        self.data_manager.save_state(game_state)
        
        return True
