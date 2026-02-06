"""LevelSystem for NintendAnki - manages level unlocking and completion."""

import uuid
from datetime import datetime
from typing import Dict, List, Optional

from data.data_manager import DataManager
from data.models import Level, LevelProgress, LevelReward, PowerUp, PowerUpType, Theme

MARIO_LEVELS = [
    {"name": "World 1-1", "description": "The classic starting level."},
    {"name": "World 1-2", "description": "Underground caverns."},
    {"name": "World 1-3", "description": "Athletic sky level."},
    {"name": "World 1-4", "description": "First castle."},
    {"name": "World 2-1", "description": "Desert land."},
    {"name": "World 2-2", "description": "Quicksand cavern."},
    {"name": "World 2-3", "description": "Pyramid secrets."},
    {"name": "World 2-4", "description": "Desert castle."},
    {"name": "World 3-1", "description": "Water world."},
    {"name": "World 3-2", "description": "Coral reef."},
    {"name": "World 3-3", "description": "Sunken ship."},
    {"name": "World 3-4", "description": "Water castle."},
    {"name": "World 4-1", "description": "Giant land."},
    {"name": "World 4-2", "description": "Giant underground."},
    {"name": "World 4-3", "description": "Giant sky."},
    {"name": "World 4-4", "description": "Giant castle."},
]

ZELDA_LEVELS = [
    {"name": "Kokiri Forest", "description": "Peaceful forest village."},
    {"name": "Deku Tree", "description": "First dungeon."},
    {"name": "Hyrule Field", "description": "Open plains."},
    {"name": "Kakariko Village", "description": "Mountain village."},
    {"name": "Death Mountain", "description": "Treacherous path."},
    {"name": "Dodongo Cavern", "description": "Dinosaur cavern."},
    {"name": "Zora River", "description": "River path."},
    {"name": "Zora Domain", "description": "Underwater kingdom."},
    {"name": "Jabu Jabu", "description": "Giant fish."},
    {"name": "Temple of Time", "description": "Sacred temple."},
    {"name": "Lost Woods", "description": "Forest maze."},
    {"name": "Forest Temple", "description": "Haunted temple."},
    {"name": "Lon Lon Ranch", "description": "Ranch visit."},
    {"name": "Fire Temple", "description": "Volcanic temple."},
    {"name": "Ice Cavern", "description": "Frozen passage."},
    {"name": "Water Temple", "description": "Water dungeon."},
]

DKC_LEVELS = [
    {"name": "Jungle Hijinxs", "description": "Lush jungle."},
    {"name": "Ropey Rampage", "description": "Vines and ropes."},
    {"name": "Reptile Rumble", "description": "Reptilian enemies."},
    {"name": "Coral Capers", "description": "Underwater caves."},
    {"name": "Barrel Canyon", "description": "Barrel cannons."},
    {"name": "Gnawty Lair", "description": "Beaver boss."},
    {"name": "Winky Walkway", "description": "Frog friend."},
    {"name": "Mine Cart", "description": "Dangerous mine."},
    {"name": "Bouncy Bonanza", "description": "Factory tires."},
    {"name": "Stop Go Station", "description": "Signal timing."},
    {"name": "Millstone Mayhem", "description": "Rolling stones."},
    {"name": "Necky Nuts", "description": "Vulture boss."},
    {"name": "Vulture Culture", "description": "Cliff vultures."},
    {"name": "Tree Top Town", "description": "Treetop village."},
    {"name": "Forest Frenzy", "description": "Forest canopy."},
    {"name": "Temple Tempest", "description": "Temple ruins."},
]

THEME_LEVELS = {Theme.MARIO: MARIO_LEVELS, Theme.ZELDA: ZELDA_LEVELS, Theme.DKC: DKC_LEVELS}
BASE_LEVEL_REWARD = 50
ACCURACY_BONUS_THRESHOLDS = [(1.0, 100), (0.98, 75), (0.95, 50), (0.90, 25)]


class LevelSystem:
    """Manages level unlocking and completion."""
    
    def __init__(self, data_manager: DataManager):
        self.data_manager = data_manager
        self._levels: Dict[str, Level] = {}
        self._levels_by_theme: Dict[Theme, List[Level]] = {
            Theme.MARIO: [], Theme.ZELDA: [], Theme.DKC: [],
        }
        self._initialize_levels()
        self._load_levels()
    
    def _initialize_levels(self) -> None:
        conn = self.data_manager._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM levels")
        count = cursor.fetchone()[0]
        if count == 0:
            for theme, level_defs in THEME_LEVELS.items():
                for i, level_def in enumerate(level_defs):
                    level_id = f"{theme.value}_level_{i + 1}"
                    cursor.execute("""
                        INSERT INTO levels
                        (id, theme, level_number, name, description, unlocked, completed,
                         best_accuracy, completion_date, rewards_claimed)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (level_id, theme.value, i + 1, level_def["name"],
                          level_def["description"], 1 if i == 0 else 0, 0, None, None, 0))
            conn.commit()
    
    def _load_levels(self) -> None:
        conn = self.data_manager._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM levels ORDER BY theme, level_number")
        for row in cursor.fetchall():
            level = Level(
                id=row["id"], theme=Theme(row["theme"]), level_number=row["level_number"],
                name=row["name"], description=row["description"],
                unlocked=bool(row["unlocked"]), completed=bool(row["completed"]),
                best_accuracy=row["best_accuracy"], completion_date=row["completion_date"],
                rewards_claimed=bool(row["rewards_claimed"]),
            )
            self._levels[level.id] = level
            self._levels_by_theme[level.theme].append(level)
    
    def _save_level(self, level: Level) -> None:
        conn = self.data_manager._get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE levels SET unlocked = ?, completed = ?, best_accuracy = ?,
                completion_date = ?, rewards_claimed = ? WHERE id = ?
        """, (1 if level.unlocked else 0, 1 if level.completed else 0,
              level.best_accuracy, level.completion_date,
              1 if level.rewards_claimed else 0, level.id))
        conn.commit()
    
    def unlock_level(self, theme: Theme) -> Optional[Level]:
        theme_levels = self._levels_by_theme.get(theme, [])
        for level in theme_levels:
            if not level.unlocked:
                level.unlocked = True
                self._save_level(level)
                return level
        return None
    
    def complete_level(self, level_id: str, accuracy: float) -> Optional[LevelReward]:
        if level_id not in self._levels:
            return None
        level = self._levels[level_id]
        if not level.unlocked:
            return None
        accuracy = max(0.0, min(1.0, accuracy))
        is_first_completion = not level.completed
        level.completed = True
        if level.best_accuracy is None or accuracy > level.best_accuracy:
            level.best_accuracy = accuracy
        if is_first_completion:
            level.completion_date = datetime.now()
        currency_earned = BASE_LEVEL_REWARD
        for threshold, bonus in ACCURACY_BONUS_THRESHOLDS:
            if accuracy >= threshold:
                currency_earned += bonus
                break
        if not is_first_completion:
            currency_earned = currency_earned // 2
        powerup_earned = None
        if is_first_completion and level.theme == Theme.MARIO:
            if accuracy >= 1.0:
                powerup_earned = self._create_powerup(PowerUpType.STAR, level.theme)
            elif accuracy >= 0.98:
                powerup_earned = self._create_powerup(PowerUpType.FIRE_FLOWER, level.theme)
            elif accuracy >= 0.95:
                powerup_earned = self._create_powerup(PowerUpType.MUSHROOM, level.theme)
        elif is_first_completion and level.theme == Theme.ZELDA:
            if accuracy >= 0.95:
                powerup_earned = self._create_powerup(PowerUpType.HEART_CONTAINER, level.theme)
        elif is_first_completion and level.theme == Theme.DKC:
            if accuracy >= 0.95:
                powerup_earned = self._create_powerup(PowerUpType.GOLDEN_BANANA, level.theme)
        level.rewards_claimed = True
        self._save_level(level)
        return LevelReward(level_id=level_id, currency_earned=currency_earned,
                          powerup_earned=powerup_earned, achievement_unlocked=None)
    
    def _create_powerup(self, powerup_type: PowerUpType, theme: Theme) -> PowerUp:
        POWERUP_INFO = {
            PowerUpType.MUSHROOM: ("Super Mushroom", "Extra health protection.", "mushroom.png"),
            PowerUpType.FIRE_FLOWER: ("Fire Flower", "Doubles points.", "fire_flower.png"),
            PowerUpType.STAR: ("Super Star", "Invincibility.", "star.png"),
            PowerUpType.HEART_CONTAINER: ("Heart Container", "Max health increase.", "heart_container.png"),
            PowerUpType.GOLDEN_BANANA: ("Golden Banana", "Triples points.", "golden_banana.png"),
        }
        info = POWERUP_INFO.get(powerup_type, (powerup_type.value, "A power-up.", f"{powerup_type.value}.png"))
        return PowerUp(id=str(uuid.uuid4()), type=powerup_type, theme=theme,
                      name=info[0], description=info[1], icon=info[2],
                      quantity=1, duration_seconds=0, acquired_at=datetime.now())
    
    def get_available_levels(self, theme: Theme) -> List[Level]:
        return [level for level in self._levels_by_theme.get(theme, []) if level.unlocked]
    
    def get_all_levels(self, theme: Theme) -> List[Level]:
        return self._levels_by_theme.get(theme, [])
    
    def get_level(self, level_id: str) -> Optional[Level]:
        return self._levels.get(level_id)
    
    def get_level_progress(self) -> LevelProgress:
        total_levels = len(self._levels)
        levels_unlocked = sum(1 for level in self._levels.values() if level.unlocked)
        levels_completed = sum(1 for level in self._levels.values() if level.completed)
        completion_percentage = (levels_completed / total_levels * 100.0) if total_levels > 0 else 0.0
        return LevelProgress(total_levels=total_levels, levels_unlocked=levels_unlocked,
                            levels_completed=levels_completed, completion_percentage=completion_percentage)
    
    def get_theme_level_progress(self, theme: Theme) -> LevelProgress:
        theme_levels = self._levels_by_theme.get(theme, [])
        total_levels = len(theme_levels)
        levels_unlocked = sum(1 for level in theme_levels if level.unlocked)
        levels_completed = sum(1 for level in theme_levels if level.completed)
        completion_percentage = (levels_completed / total_levels * 100.0) if total_levels > 0 else 0.0
        return LevelProgress(total_levels=total_levels, levels_unlocked=levels_unlocked,
                            levels_completed=levels_completed, completion_percentage=completion_percentage)
    
    def get_next_locked_level(self, theme: Theme) -> Optional[Level]:
        for level in self._levels_by_theme.get(theme, []):
            if not level.unlocked:
                return level
        return None
    
    def is_level_unlocked(self, level_id: str) -> bool:
        level = self._levels.get(level_id)
        return level.unlocked if level else False
    
    def is_level_completed(self, level_id: str) -> bool:
        level = self._levels.get(level_id)
        return level.completed if level else False
    
    def get_total_levels_for_theme(self, theme: Theme) -> int:
        return len(self._levels_by_theme.get(theme, []))
    
    def reset_level_progress(self, level_id: str) -> bool:
        if level_id not in self._levels:
            return False
        level = self._levels[level_id]
        level.completed = False
        level.best_accuracy = None
        level.completion_date = None
        level.rewards_claimed = False
        self._save_level(level)
        return True
    
    def unlock_all_levels(self, theme: Optional[Theme] = None) -> int:
        count = 0
        levels_to_unlock = self._levels.values() if theme is None else self._levels_by_theme.get(theme, [])
        for level in levels_to_unlock:
            if not level.unlocked:
                level.unlocked = True
                self._save_level(level)
                count += 1
        return count
