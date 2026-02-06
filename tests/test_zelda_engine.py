"""
Unit tests for ZeldaEngine.

Tests the ZeldaEngine class functionality including:
- Animation generation for correct/wrong answers
- Collectible generation
- Boss battle mechanics
- Adventure map functionality
- Item equipment system

Requirements: 5.1, 5.2, 5.3, 5.4, 5.5, 5.6, 5.7, 5.8
"""

import pytest
from datetime import datetime

from themes.zelda_engine import (
    ZeldaEngine,
    ZeldaItem,
    ZeldaItemCategory,
    ZeldaItemEffect,
    BossBattle,
    BossReward,
    MapRegion,
    AdventureMap,
    SPECIAL_ITEMS,
    COSMETIC_ITEMS,
    BOSS_NAMES,
)
from core.theme_manager import ThemeEngine
from data.data_manager import DataManager
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


@pytest.fixture
def temp_db_path(tmp_path):
    """Create a temporary database path for testing."""
    return tmp_path / "test_nintendanki.db"


@pytest.fixture
def data_manager(temp_db_path):
    """Create a DataManager with a temporary database."""
    dm = DataManager(temp_db_path)
    dm.initialize_database()
    return dm


@pytest.fixture
def zelda_engine(data_manager):
    """Create a ZeldaEngine for testing."""
    return ZeldaEngine(data_manager)


class TestZeldaEngineInitialization:
    """Tests for ZeldaEngine initialization."""
    
    def test_zelda_engine_is_theme_engine(self, zelda_engine):
        """Test that ZeldaEngine is a ThemeEngine subclass."""
        assert isinstance(zelda_engine, ThemeEngine)
    
    def test_zelda_engine_initializes_with_data_manager(self, data_manager):
        """Test that ZeldaEngine initializes with a DataManager."""
        engine = ZeldaEngine(data_manager)
        assert engine.data_manager is data_manager
    
    def test_zelda_engine_initializes_with_default_hearts(self, zelda_engine):
        """Test that ZeldaEngine initializes with 3 hearts."""
        assert zelda_engine.get_hearts() == 3
    
    def test_zelda_engine_initializes_with_no_equipped_item(self, zelda_engine):
        """Test that ZeldaEngine initializes with no equipped item."""
        assert zelda_engine.get_equipped_item() is None
    
    def test_zelda_engine_initializes_with_empty_inventory(self, zelda_engine):
        """Test that ZeldaEngine initializes with empty inventory."""
        assert len(zelda_engine.get_owned_items()) == 0


class TestGetAnimationForCorrect:
    """Tests for get_animation_for_correct method.
    
    Requirements: 5.2
    """
    
    def test_returns_animation(self, zelda_engine):
        """Test that get_animation_for_correct returns an Animation."""
        animation = zelda_engine.get_animation_for_correct()
        assert isinstance(animation, Animation)
    
    def test_animation_type_is_collect(self, zelda_engine):
        """Test that animation type is COLLECT for exploration."""
        animation = zelda_engine.get_animation_for_correct()
        assert animation.type == AnimationType.COLLECT
    
    def test_animation_theme_is_zelda(self, zelda_engine):
        """Test that animation theme is ZELDA."""
        animation = zelda_engine.get_animation_for_correct()
        assert animation.theme == Theme.ZELDA
    
    def test_animation_has_sprite_sheet(self, zelda_engine):
        """Test that animation has a sprite sheet path."""
        animation = zelda_engine.get_animation_for_correct()
        assert animation.sprite_sheet is not None
        assert "zelda" in animation.sprite_sheet.lower()
    
    def test_animation_has_frames(self, zelda_engine):
        """Test that animation has frame data."""
        animation = zelda_engine.get_animation_for_correct()
        assert len(animation.frames) > 0
    
    def test_animation_fps_is_valid(self, zelda_engine):
        """Test that animation FPS is at least 30 (Requirement 9.2)."""
        animation = zelda_engine.get_animation_for_correct()
        assert animation.fps >= 30


class TestGetAnimationForWrong:
    """Tests for get_animation_for_wrong method.
    
    Requirements: 5.3
    """
    
    def test_returns_animation(self, zelda_engine):
        """Test that get_animation_for_wrong returns an Animation."""
        animation = zelda_engine.get_animation_for_wrong()
        assert isinstance(animation, Animation)
    
    def test_animation_type_is_damage(self, zelda_engine):
        """Test that animation type is DAMAGE for enemy attack."""
        animation = zelda_engine.get_animation_for_wrong()
        assert animation.type == AnimationType.DAMAGE
    
    def test_animation_theme_is_zelda(self, zelda_engine):
        """Test that animation theme is ZELDA."""
        animation = zelda_engine.get_animation_for_wrong()
        assert animation.theme == Theme.ZELDA
    
    def test_animation_has_sprite_sheet(self, zelda_engine):
        """Test that animation has a sprite sheet path."""
        animation = zelda_engine.get_animation_for_wrong()
        assert animation.sprite_sheet is not None
        assert "zelda" in animation.sprite_sheet.lower()
    
    def test_animation_has_frames(self, zelda_engine):
        """Test that animation has frame data."""
        animation = zelda_engine.get_animation_for_wrong()
        assert len(animation.frames) > 0


class TestGetCollectibleForCorrect:
    """Tests for get_collectible_for_correct method."""
    
    def test_returns_collectible(self, zelda_engine):
        """Test that get_collectible_for_correct returns a Collectible."""
        collectible = zelda_engine.get_collectible_for_correct()
        assert isinstance(collectible, Collectible)
    
    def test_collectible_is_rupee(self, zelda_engine):
        """Test that collectible is a rupee."""
        collectible = zelda_engine.get_collectible_for_correct()
        assert collectible.type == CollectibleType.RUPEE
    
    def test_collectible_theme_is_zelda(self, zelda_engine):
        """Test that collectible theme is ZELDA."""
        collectible = zelda_engine.get_collectible_for_correct()
        assert collectible.theme == Theme.ZELDA
    
    def test_collectible_is_owned(self, zelda_engine):
        """Test that collectible is marked as owned."""
        collectible = zelda_engine.get_collectible_for_correct()
        assert collectible.owned is True


class TestTriggerBossBattle:
    """Tests for trigger_boss_battle method.
    
    Requirements: 5.4
    """
    
    def test_returns_boss_battle(self, zelda_engine):
        """Test that trigger_boss_battle returns a BossBattle."""
        battle = zelda_engine.trigger_boss_battle(deck_id=1)
        assert isinstance(battle, BossBattle)
    
    def test_boss_battle_has_deck_id(self, zelda_engine):
        """Test that boss battle has the correct deck_id."""
        battle = zelda_engine.trigger_boss_battle(deck_id=42)
        assert battle.deck_id == 42
    
    def test_boss_battle_has_boss_name(self, zelda_engine):
        """Test that boss battle has a boss name from the predefined list."""
        battle = zelda_engine.trigger_boss_battle(deck_id=1)
        assert battle.boss_name in BOSS_NAMES
    
    def test_boss_battle_has_difficulty(self, zelda_engine):
        """Test that boss battle has difficulty between 1 and 5."""
        for deck_id in range(10):
            battle = zelda_engine.trigger_boss_battle(deck_id=deck_id)
            assert 1 <= battle.difficulty <= 5
    
    def test_boss_battle_has_unique_id(self, zelda_engine):
        """Test that each boss battle has a unique ID."""
        battle1 = zelda_engine.trigger_boss_battle(deck_id=1)
        battle2 = zelda_engine.trigger_boss_battle(deck_id=1)
        assert battle1.id != battle2.id
    
    def test_boss_battle_is_not_completed(self, zelda_engine):
        """Test that new boss battle is not completed."""
        battle = zelda_engine.trigger_boss_battle(deck_id=1)
        assert battle.completed is False
        assert battle.won is False
    
    def test_boss_battle_has_started_at(self, zelda_engine):
        """Test that boss battle has a start time."""
        battle = zelda_engine.trigger_boss_battle(deck_id=1)
        assert battle.started_at is not None
        assert isinstance(battle.started_at, datetime)
    
    def test_boss_battle_sets_active_battle(self, zelda_engine):
        """Test that triggering a battle sets it as active."""
        battle = zelda_engine.trigger_boss_battle(deck_id=1)
        assert zelda_engine.get_active_boss_battle() == battle
    
    def test_different_decks_get_different_bosses(self, zelda_engine):
        """Test that different deck IDs can get different bosses."""
        bosses = set()
        for deck_id in range(len(BOSS_NAMES)):
            battle = zelda_engine.trigger_boss_battle(deck_id=deck_id)
            bosses.add(battle.boss_name)
        # Should have multiple different bosses
        assert len(bosses) > 1


class TestCompleteBossBattle:
    """Tests for complete_boss_battle method.
    
    Requirements: 5.5
    """
    
    def test_returns_boss_reward(self, zelda_engine):
        """Test that complete_boss_battle returns a BossReward."""
        battle = zelda_engine.trigger_boss_battle(deck_id=1)
        reward = zelda_engine.complete_boss_battle(battle, won=True)
        assert isinstance(reward, BossReward)
    
    def test_winning_awards_special_item(self, zelda_engine):
        """Test that winning a boss battle awards a special item."""
        battle = zelda_engine.trigger_boss_battle(deck_id=1)
        reward = zelda_engine.complete_boss_battle(battle, won=True)
        assert reward.item_awarded is not None
        assert isinstance(reward.item_awarded, ZeldaItem)
    
    def test_losing_does_not_award_item(self, zelda_engine):
        """Test that losing a boss battle does not award a special item."""
        battle = zelda_engine.trigger_boss_battle(deck_id=1)
        reward = zelda_engine.complete_boss_battle(battle, won=False)
        assert reward.item_awarded is None
    
    def test_winning_awards_currency(self, zelda_engine):
        """Test that winning awards currency based on difficulty."""
        battle = zelda_engine.trigger_boss_battle(deck_id=1)
        reward = zelda_engine.complete_boss_battle(battle, won=True)
        assert reward.currency_earned > 0
        assert reward.currency_earned == 50 * battle.difficulty
    
    def test_losing_awards_consolation_currency(self, zelda_engine):
        """Test that losing awards a small consolation prize."""
        battle = zelda_engine.trigger_boss_battle(deck_id=1)
        reward = zelda_engine.complete_boss_battle(battle, won=False)
        assert reward.currency_earned == 10
    
    def test_winning_awards_experience(self, zelda_engine):
        """Test that winning awards experience based on difficulty."""
        battle = zelda_engine.trigger_boss_battle(deck_id=1)
        reward = zelda_engine.complete_boss_battle(battle, won=True)
        assert reward.experience_earned > 0
        assert reward.experience_earned == 100 * battle.difficulty
    
    def test_battle_marked_completed(self, zelda_engine):
        """Test that battle is marked as completed."""
        battle = zelda_engine.trigger_boss_battle(deck_id=1)
        zelda_engine.complete_boss_battle(battle, won=True)
        assert battle.completed is True
    
    def test_battle_marked_won_or_lost(self, zelda_engine):
        """Test that battle won status is set correctly."""
        battle1 = zelda_engine.trigger_boss_battle(deck_id=1)
        zelda_engine.complete_boss_battle(battle1, won=True)
        assert battle1.won is True
        
        battle2 = zelda_engine.trigger_boss_battle(deck_id=2)
        zelda_engine.complete_boss_battle(battle2, won=False)
        assert battle2.won is False
    
    def test_clears_active_battle(self, zelda_engine):
        """Test that completing a battle clears the active battle."""
        battle = zelda_engine.trigger_boss_battle(deck_id=1)
        assert zelda_engine.get_active_boss_battle() is not None
        zelda_engine.complete_boss_battle(battle, won=True)
        assert zelda_engine.get_active_boss_battle() is None
    
    def test_item_added_to_inventory(self, zelda_engine):
        """Test that won item is added to inventory."""
        battle = zelda_engine.trigger_boss_battle(deck_id=1)
        reward = zelda_engine.complete_boss_battle(battle, won=True)
        
        owned_items = zelda_engine.get_owned_items()
        assert any(item.id == reward.item_awarded.id for item in owned_items)
    
    def test_higher_difficulty_better_rewards(self, zelda_engine):
        """Test that higher difficulty bosses give better rewards."""
        # Difficulty 1 boss
        battle1 = zelda_engine.trigger_boss_battle(deck_id=0)  # difficulty 1
        reward1 = zelda_engine.complete_boss_battle(battle1, won=True)
        
        # Difficulty 5 boss
        battle5 = zelda_engine.trigger_boss_battle(deck_id=4)  # difficulty 5
        reward5 = zelda_engine.complete_boss_battle(battle5, won=True)
        
        assert reward5.currency_earned > reward1.currency_earned
        assert reward5.experience_earned > reward1.experience_earned


class TestGetAdventureMap:
    """Tests for get_adventure_map method.
    
    Requirements: 5.1, 5.8
    """
    
    def test_returns_adventure_map(self, zelda_engine):
        """Test that get_adventure_map returns an AdventureMap."""
        adventure_map = zelda_engine.get_adventure_map()
        assert isinstance(adventure_map, AdventureMap)
    
    def test_map_has_regions(self, zelda_engine):
        """Test that map has regions."""
        adventure_map = zelda_engine.get_adventure_map()
        assert isinstance(adventure_map.regions, list)
        assert len(adventure_map.regions) >= 1
    
    def test_map_has_background(self, zelda_engine):
        """Test that map has a background image."""
        adventure_map = zelda_engine.get_adventure_map()
        assert adventure_map.background is not None
        assert "zelda" in adventure_map.background.lower()
    
    def test_map_tracks_explored_count(self, zelda_engine):
        """Test that map tracks explored region count."""
        adventure_map = zelda_engine.get_adventure_map()
        assert adventure_map.total_explored >= 0
        assert adventure_map.total_regions >= adventure_map.total_explored
    
    def test_first_region_always_explored(self, zelda_engine):
        """Test that the first region is always explored."""
        adventure_map = zelda_engine.get_adventure_map()
        if adventure_map.regions:
            assert adventure_map.regions[0].explored is True
    
    def test_regions_have_names(self, zelda_engine):
        """Test that all regions have names."""
        adventure_map = zelda_engine.get_adventure_map()
        for region in adventure_map.regions:
            assert region.name is not None
            assert len(region.name) > 0
    
    def test_regions_have_positions(self, zelda_engine):
        """Test that all regions have positions."""
        adventure_map = zelda_engine.get_adventure_map()
        for region in adventure_map.regions:
            assert region.position is not None
            assert len(region.position) == 2
    
    def test_more_progress_unlocks_more_regions(self, data_manager):
        """Test that more correct answers unlock more regions."""
        # Initial state - few regions
        engine1 = ZeldaEngine(data_manager)
        map1 = engine1.get_adventure_map()
        initial_regions = len(map1.regions)
        
        # Add progress
        state = data_manager.load_state()
        state.progression.correct_answers = 100
        data_manager.save_state(state)
        
        engine2 = ZeldaEngine(data_manager)
        map2 = engine2.get_adventure_map()
        
        assert len(map2.regions) >= initial_regions
    
    def test_current_region_is_set(self, zelda_engine):
        """Test that current region is set."""
        adventure_map = zelda_engine.get_adventure_map()
        if adventure_map.regions:
            assert adventure_map.current_region is not None


class TestItemEquipment:
    """Tests for item equipment methods.
    
    Requirements: 5.6, 5.7
    """
    
    def test_get_equipped_item_returns_none_initially(self, zelda_engine):
        """Test that no item is equipped initially."""
        assert zelda_engine.get_equipped_item() is None
    
    def test_equip_item_returns_false_for_unowned_item(self, zelda_engine):
        """Test that equipping an unowned item returns False."""
        result = zelda_engine.equip_item("zelda_master_sword")
        assert result is False
    
    def test_equip_owned_functional_item(self, zelda_engine):
        """Test that owned functional items can be equipped."""
        # Add a functional item
        item = ZeldaItem(
            id="zelda_master_sword",
            name="Master Sword",
            description="Test sword",
            icon="test.png",
            category=ZeldaItemCategory.FUNCTIONAL,
            effect=ZeldaItemEffect.HINT,
            effect_value=1,
        )
        zelda_engine.add_item(item)
        
        result = zelda_engine.equip_item("zelda_master_sword")
        assert result is True
        assert zelda_engine.get_equipped_item() is not None
        assert zelda_engine.get_equipped_item().id == "zelda_master_sword"
    
    def test_cannot_equip_cosmetic_item(self, zelda_engine):
        """Test that cosmetic items cannot be equipped."""
        # Add a cosmetic item
        item = ZeldaItem(
            id="zelda_green_tunic",
            name="Green Tunic",
            description="Test tunic",
            icon="test.png",
            category=ZeldaItemCategory.COSMETIC,
        )
        zelda_engine.add_item(item)
        
        result = zelda_engine.equip_item("zelda_green_tunic")
        assert result is False
        assert zelda_engine.get_equipped_item() is None
    
    def test_equipping_new_item_unequips_old(self, zelda_engine):
        """Test that equipping a new item unequips the old one."""
        # Add two functional items
        item1 = ZeldaItem(
            id="item1",
            name="Item 1",
            description="Test",
            icon="test.png",
            category=ZeldaItemCategory.FUNCTIONAL,
            effect=ZeldaItemEffect.HINT,
        )
        item2 = ZeldaItem(
            id="item2",
            name="Item 2",
            description="Test",
            icon="test.png",
            category=ZeldaItemCategory.FUNCTIONAL,
            effect=ZeldaItemEffect.EXTRA_TIME,
        )
        zelda_engine.add_item(item1)
        zelda_engine.add_item(item2)
        
        zelda_engine.equip_item("item1")
        assert zelda_engine.get_equipped_item().id == "item1"
        
        zelda_engine.equip_item("item2")
        assert zelda_engine.get_equipped_item().id == "item2"
    
    def test_unequip_item(self, zelda_engine):
        """Test that items can be unequipped."""
        item = ZeldaItem(
            id="test_item",
            name="Test",
            description="Test",
            icon="test.png",
            category=ZeldaItemCategory.FUNCTIONAL,
            effect=ZeldaItemEffect.HINT,
        )
        zelda_engine.add_item(item)
        zelda_engine.equip_item("test_item")
        
        result = zelda_engine.unequip_item()
        assert result is True
        assert zelda_engine.get_equipped_item() is None
    
    def test_unequip_when_nothing_equipped(self, zelda_engine):
        """Test that unequipping when nothing is equipped returns False."""
        result = zelda_engine.unequip_item()
        assert result is False


class TestItemCategorization:
    """Tests for item categorization.
    
    Requirements: 5.6
    """
    
    def test_get_functional_items(self, zelda_engine):
        """Test that get_functional_items returns only functional items."""
        # Add both types of items
        functional = ZeldaItem(
            id="func_item",
            name="Functional",
            description="Test",
            icon="test.png",
            category=ZeldaItemCategory.FUNCTIONAL,
            effect=ZeldaItemEffect.HINT,
        )
        cosmetic = ZeldaItem(
            id="cosm_item",
            name="Cosmetic",
            description="Test",
            icon="test.png",
            category=ZeldaItemCategory.COSMETIC,
        )
        zelda_engine.add_item(functional)
        zelda_engine.add_item(cosmetic)
        
        functional_items = zelda_engine.get_functional_items()
        assert len(functional_items) == 1
        assert all(i.category == ZeldaItemCategory.FUNCTIONAL for i in functional_items)
    
    def test_get_cosmetic_items(self, zelda_engine):
        """Test that get_cosmetic_items returns only cosmetic items."""
        # Add both types of items
        functional = ZeldaItem(
            id="func_item",
            name="Functional",
            description="Test",
            icon="test.png",
            category=ZeldaItemCategory.FUNCTIONAL,
            effect=ZeldaItemEffect.HINT,
        )
        cosmetic = ZeldaItem(
            id="cosm_item",
            name="Cosmetic",
            description="Test",
            icon="test.png",
            category=ZeldaItemCategory.COSMETIC,
        )
        zelda_engine.add_item(functional)
        zelda_engine.add_item(cosmetic)
        
        cosmetic_items = zelda_engine.get_cosmetic_items()
        assert len(cosmetic_items) == 1
        assert all(i.category == ZeldaItemCategory.COSMETIC for i in cosmetic_items)
    
    def test_special_items_are_functional(self):
        """Test that all predefined special items are functional."""
        for item in SPECIAL_ITEMS.values():
            assert item.category == ZeldaItemCategory.FUNCTIONAL
    
    def test_cosmetic_items_are_cosmetic(self):
        """Test that all predefined cosmetic items are cosmetic."""
        for item in COSMETIC_ITEMS.values():
            assert item.category == ZeldaItemCategory.COSMETIC
    
    def test_functional_items_have_effects(self):
        """Test that all functional items have effects."""
        for item in SPECIAL_ITEMS.values():
            assert item.effect is not None
    
    def test_cosmetic_items_have_no_effects(self):
        """Test that cosmetic items have no effects."""
        for item in COSMETIC_ITEMS.values():
            assert item.effect is None


class TestItemEffects:
    """Tests for item effects.
    
    Requirements: 5.7
    """
    
    def test_get_item_effect_returns_none_when_nothing_equipped(self, zelda_engine):
        """Test that get_item_effect returns None when nothing is equipped."""
        assert zelda_engine.get_item_effect() is None
    
    def test_get_item_effect_returns_effect_when_equipped(self, zelda_engine):
        """Test that get_item_effect returns effect when item is equipped."""
        item = ZeldaItem(
            id="test_item",
            name="Test",
            description="Test",
            icon="test.png",
            category=ZeldaItemCategory.FUNCTIONAL,
            effect=ZeldaItemEffect.HINT,
            effect_value=1,
        )
        zelda_engine.add_item(item)
        zelda_engine.equip_item("test_item")
        
        effect = zelda_engine.get_item_effect()
        assert effect is not None
        assert effect[0] == ZeldaItemEffect.HINT
        assert effect[1] == 1
    
    def test_hint_effect(self, zelda_engine):
        """Test that HINT effect is properly returned."""
        item = ZeldaItem(
            id="hint_item",
            name="Hint Item",
            description="Test",
            icon="test.png",
            category=ZeldaItemCategory.FUNCTIONAL,
            effect=ZeldaItemEffect.HINT,
            effect_value=1,
        )
        zelda_engine.add_item(item)
        zelda_engine.equip_item("hint_item")
        
        effect = zelda_engine.get_item_effect()
        assert effect[0] == ZeldaItemEffect.HINT
    
    def test_extra_time_effect(self, zelda_engine):
        """Test that EXTRA_TIME effect is properly returned."""
        item = ZeldaItem(
            id="time_item",
            name="Time Item",
            description="Test",
            icon="test.png",
            category=ZeldaItemCategory.FUNCTIONAL,
            effect=ZeldaItemEffect.EXTRA_TIME,
            effect_value=30,
        )
        zelda_engine.add_item(item)
        zelda_engine.equip_item("time_item")
        
        effect = zelda_engine.get_item_effect()
        assert effect[0] == ZeldaItemEffect.EXTRA_TIME
        assert effect[1] == 30
    
    def test_second_chance_effect(self, zelda_engine):
        """Test that SECOND_CHANCE effect is properly returned."""
        item = ZeldaItem(
            id="chance_item",
            name="Chance Item",
            description="Test",
            icon="test.png",
            category=ZeldaItemCategory.FUNCTIONAL,
            effect=ZeldaItemEffect.SECOND_CHANCE,
            effect_value=1,
        )
        zelda_engine.add_item(item)
        zelda_engine.equip_item("chance_item")
        
        effect = zelda_engine.get_item_effect()
        assert effect[0] == ZeldaItemEffect.SECOND_CHANCE


class TestGetLevelView:
    """Tests for get_level_view method.
    
    Requirements: 5.1
    """
    
    def test_returns_level_view(self, zelda_engine):
        """Test that get_level_view returns a LevelView."""
        level = Level(id="test_level", theme=Theme.ZELDA, level_number=1, name="Test Level")
        view = zelda_engine.get_level_view(level)
        assert isinstance(view, LevelView)
    
    def test_level_view_has_background(self, zelda_engine):
        """Test that level view has a background image."""
        level = Level(id="test_level", theme=Theme.ZELDA, level_number=1, name="Test Level")
        view = zelda_engine.get_level_view(level)
        assert view.background is not None
        assert "zelda" in view.background.lower()
    
    def test_level_view_has_character_position(self, zelda_engine):
        """Test that level view has a character starting position."""
        level = Level(id="test_level", theme=Theme.ZELDA, level_number=1, name="Test Level")
        view = zelda_engine.get_level_view(level)
        assert view.character_position is not None
        assert len(view.character_position) == 2
    
    def test_level_view_has_collectibles(self, zelda_engine):
        """Test that level view has collectibles."""
        level = Level(id="test_level", theme=Theme.ZELDA, level_number=1, name="Test Level")
        view = zelda_engine.get_level_view(level)
        assert isinstance(view.collectibles_visible, list)
        assert len(view.collectibles_visible) > 0
    
    def test_higher_levels_have_more_collectibles(self, zelda_engine):
        """Test that higher level numbers have more collectibles."""
        level1 = Level(id="level_1", theme=Theme.ZELDA, level_number=1, name="Level 1")
        level5 = Level(id="level_5", theme=Theme.ZELDA, level_number=5, name="Level 5")
        
        view1 = zelda_engine.get_level_view(level1)
        view5 = zelda_engine.get_level_view(level5)
        
        assert len(view5.collectibles_visible) > len(view1.collectibles_visible)
    
    def test_every_third_level_has_heart(self, zelda_engine):
        """Test that every third level has a heart collectible."""
        level3 = Level(id="level_3", theme=Theme.ZELDA, level_number=3, name="Level 3")
        view3 = zelda_engine.get_level_view(level3)
        
        hearts = [c for c in view3.collectibles_visible if c.type == CollectibleType.HEART]
        assert len(hearts) >= 1


class TestGetDashboardStats:
    """Tests for get_dashboard_stats method."""
    
    def test_returns_theme_stats(self, zelda_engine):
        """Test that get_dashboard_stats returns ThemeStats."""
        stats = zelda_engine.get_dashboard_stats()
        assert isinstance(stats, ThemeStats)
    
    def test_stats_theme_is_zelda(self, zelda_engine):
        """Test that stats theme is ZELDA."""
        stats = zelda_engine.get_dashboard_stats()
        assert stats.theme == Theme.ZELDA
    
    def test_stats_primary_collectible_is_rupees(self, zelda_engine):
        """Test that primary collectible is rupees."""
        stats = zelda_engine.get_dashboard_stats()
        assert stats.primary_collectible_name == "Rupees"
    
    def test_stats_secondary_stat_is_hearts(self, zelda_engine):
        """Test that secondary stat is hearts."""
        stats = zelda_engine.get_dashboard_stats()
        assert stats.secondary_stat_name == "Hearts"
    
    def test_stats_reflects_heart_count(self, data_manager):
        """Test that stats reflects actual heart count."""
        state = data_manager.load_state()
        state.theme_specific[Theme.ZELDA].hearts = 5
        data_manager.save_state(state)
        
        engine = ZeldaEngine(data_manager)
        stats = engine.get_dashboard_stats()
        
        assert stats.secondary_stat_value == 5


class TestHeartManagement:
    """Tests for heart management methods."""
    
    def test_get_hearts_returns_initial_value(self, zelda_engine):
        """Test that get_hearts returns initial value of 3."""
        assert zelda_engine.get_hearts() == 3
    
    def test_set_hearts_updates_value(self, zelda_engine):
        """Test that set_hearts updates the heart count."""
        zelda_engine.set_hearts(5)
        assert zelda_engine.get_hearts() == 5
    
    def test_set_hearts_minimum_zero(self, zelda_engine):
        """Test that hearts cannot go below zero."""
        zelda_engine.set_hearts(-5)
        assert zelda_engine.get_hearts() == 0
    
    def test_hearts_persist_to_database(self, data_manager):
        """Test that hearts are persisted to database."""
        engine = ZeldaEngine(data_manager)
        engine.set_hearts(7)
        
        # Create new engine to verify persistence
        engine2 = ZeldaEngine(data_manager)
        assert engine2.get_hearts() == 7


class TestSpriteAnimations:
    """Tests for sprite animation methods."""
    
    def test_get_attack_animation(self, zelda_engine):
        """Test get_attack_animation returns valid animation."""
        animation = zelda_engine.get_attack_animation()
        
        assert isinstance(animation, Animation)
        assert animation.type == AnimationType.ATTACK
        assert animation.theme == Theme.ZELDA
        assert animation.loop is False
    
    def test_get_idle_animation(self, zelda_engine):
        """Test get_idle_animation returns valid animation."""
        animation = zelda_engine.get_idle_animation()
        
        assert isinstance(animation, Animation)
        assert animation.type == AnimationType.IDLE
        assert animation.theme == Theme.ZELDA
        assert animation.loop is True
    
    def test_get_victory_animation(self, zelda_engine):
        """Test get_victory_animation returns valid animation."""
        animation = zelda_engine.get_victory_animation()
        
        assert isinstance(animation, Animation)
        assert animation.type == AnimationType.VICTORY
        assert animation.theme == Theme.ZELDA
        assert animation.loop is False


class TestExploreRegion:
    """Tests for explore_region method."""
    
    def test_explore_region_returns_true_for_new_region(self, zelda_engine):
        """Test that exploring a new region returns True."""
        result = zelda_engine.explore_region("kokiri_forest")
        assert result is True
    
    def test_explore_region_returns_false_for_already_explored(self, zelda_engine):
        """Test that exploring an already explored region returns False."""
        zelda_engine.explore_region("kokiri_forest")
        result = zelda_engine.explore_region("kokiri_forest")
        assert result is False
    
    def test_explored_region_persists(self, data_manager):
        """Test that explored regions persist to database."""
        engine = ZeldaEngine(data_manager)
        engine.explore_region("death_mountain")
        
        # Create new engine to verify persistence
        engine2 = ZeldaEngine(data_manager)
        _ = engine2.get_adventure_map()  # Trigger state load
        
        # Check if death_mountain is in explored regions
        state = data_manager.load_state()
        theme_state = state.theme_specific.get(Theme.ZELDA)
        explored = theme_state.map_progress.get("explored_regions", [])
        assert "death_mountain" in explored


class TestAddItem:
    """Tests for add_item method."""
    
    def test_add_item_returns_true_for_new_item(self, zelda_engine):
        """Test that adding a new item returns True."""
        item = ZeldaItem(
            id="new_item",
            name="New Item",
            description="Test",
            icon="test.png",
            category=ZeldaItemCategory.FUNCTIONAL,
        )
        result = zelda_engine.add_item(item)
        assert result is True
    
    def test_add_item_returns_false_for_duplicate(self, zelda_engine):
        """Test that adding a duplicate item returns False."""
        item = ZeldaItem(
            id="dup_item",
            name="Duplicate",
            description="Test",
            icon="test.png",
            category=ZeldaItemCategory.FUNCTIONAL,
        )
        zelda_engine.add_item(item)
        result = zelda_engine.add_item(item)
        assert result is False
    
    def test_added_item_appears_in_inventory(self, zelda_engine):
        """Test that added items appear in inventory."""
        item = ZeldaItem(
            id="inv_item",
            name="Inventory Item",
            description="Test",
            icon="test.png",
            category=ZeldaItemCategory.FUNCTIONAL,
        )
        zelda_engine.add_item(item)
        
        owned = zelda_engine.get_owned_items()
        assert any(i.id == "inv_item" for i in owned)
    
    def test_added_item_marked_as_owned(self, zelda_engine):
        """Test that added items are marked as owned."""
        item = ZeldaItem(
            id="owned_item",
            name="Owned Item",
            description="Test",
            icon="test.png",
            category=ZeldaItemCategory.FUNCTIONAL,
            owned=False,  # Initially not owned
        )
        zelda_engine.add_item(item)
        
        owned = zelda_engine.get_owned_items()
        added_item = next(i for i in owned if i.id == "owned_item")
        assert added_item.owned is True
    
    def test_added_item_has_acquired_at(self, zelda_engine):
        """Test that added items have acquired_at timestamp."""
        item = ZeldaItem(
            id="timed_item",
            name="Timed Item",
            description="Test",
            icon="test.png",
            category=ZeldaItemCategory.FUNCTIONAL,
        )
        zelda_engine.add_item(item)
        
        owned = zelda_engine.get_owned_items()
        added_item = next(i for i in owned if i.id == "timed_item")
        assert added_item.acquired_at is not None


class TestDataclasses:
    """Tests for ZeldaEngine dataclasses."""
    
    def test_zelda_item_defaults(self):
        """Test ZeldaItem default values."""
        item = ZeldaItem(
            id="test",
            name="Test",
            description="Test",
            icon="test.png",
            category=ZeldaItemCategory.FUNCTIONAL,
        )
        assert item.effect is None
        assert item.effect_value == 0
        assert item.owned is False
        assert item.equipped is False
        assert item.acquired_at is None
    
    def test_boss_battle_defaults(self):
        """Test BossBattle default values."""
        battle = BossBattle(
            id="test",
            deck_id=1,
            boss_name="Test Boss",
            boss_icon="test.png",
        )
        assert battle.difficulty == 1
        assert battle.started_at is None
        assert battle.completed is False
        assert battle.won is False
    
    def test_boss_reward_defaults(self):
        """Test BossReward default values."""
        reward = BossReward(battle_id="test")
        assert reward.item_awarded is None
        assert reward.currency_earned == 0
        assert reward.experience_earned == 0
    
    def test_map_region_defaults(self):
        """Test MapRegion default values."""
        region = MapRegion(id="test", name="Test")
        assert region.explored is False
        assert region.deck_id is None
        assert region.position == (0, 0)
        assert region.connected_regions == []
    
    def test_adventure_map_defaults(self):
        """Test AdventureMap default values."""
        adventure_map = AdventureMap(regions=[])
        assert adventure_map.current_region is None
        assert adventure_map.total_explored == 0
        assert adventure_map.total_regions == 0
        assert "adventure_map" in adventure_map.background


class TestZeldaItemCategory:
    """Tests for ZeldaItemCategory enum."""
    
    def test_functional_category_value(self):
        """Test FUNCTIONAL category value."""
        assert ZeldaItemCategory.FUNCTIONAL.value == "functional"
    
    def test_cosmetic_category_value(self):
        """Test COSMETIC category value."""
        assert ZeldaItemCategory.COSMETIC.value == "cosmetic"


class TestZeldaItemEffect:
    """Tests for ZeldaItemEffect enum."""
    
    def test_hint_effect_value(self):
        """Test HINT effect value."""
        assert ZeldaItemEffect.HINT.value == "hint"
    
    def test_extra_time_effect_value(self):
        """Test EXTRA_TIME effect value."""
        assert ZeldaItemEffect.EXTRA_TIME.value == "extra_time"
    
    def test_second_chance_effect_value(self):
        """Test SECOND_CHANCE effect value."""
        assert ZeldaItemEffect.SECOND_CHANCE.value == "second_chance"
