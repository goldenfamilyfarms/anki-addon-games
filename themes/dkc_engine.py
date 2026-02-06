"""DKCEngine for NintendAnki - DKC themed game mechanics."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional, TYPE_CHECKING

from core.theme_manager import ThemeEngine
from data.models import (
    Animation, AnimationType, Collectible, CollectibleType,
    Level, LevelView, Theme, ThemeStats,
)

if TYPE_CHECKING:
    from data.data_manager import DataManager

CARDS_FOR_FULL_COMPLETION = 500


@dataclass
class TimeTrial:
    """Represents a time trial challenge."""
    id: str
    duration_seconds: int
    started_at: Optional[datetime] = None
    remaining_seconds: float = 0.0
    cards_completed: int = 0
    active: bool = False
    completed: bool = False


@dataclass
class TimeTrialReward:
    """Rewards earned from completing a time trial."""
    trial_id: str
    base_bananas: int
    bonus_bananas: int
    total_bananas: int
    time_remaining: float
    cards_completed: int


@dataclass
class JungleWorld:
    """Represents a jungle world in the DKC theme."""
    id: str
    name: str
    completion_percentage: float = 0.0
    is_bonus_world: bool = False
    unlocked: bool = True
    levels: List[Level] = field(default_factory=list)


class DKCEngine(ThemeEngine):
    """DKC theme engine with collectible and time trial mechanics."""
    
    DEFAULT_FPS = 30
    COLLECT_FRAMES = [0, 1, 2, 3, 4, 5]
    DAMAGE_FRAMES = [0, 1, 2, 3]
    RUN_FRAMES = [0, 1, 2, 3, 4, 5, 6, 7]
    IDLE_FRAMES = [0, 1]
    DEFAULT_TIME_TRIAL_DURATION = 60
    BANANAS_PER_CARD = 5
    BONUS_BANANAS_PER_SECOND = 2
    BANANAS_LOST_ON_WRONG = 3
    
    def __init__(self, data_manager: "DataManager"):
        self.data_manager = data_manager
        self._banana_count = 0
        self._active_time_trial: Optional[TimeTrial] = None
        self._bonus_world_unlocked = False
        self._load_theme_state()
    
    def _load_theme_state(self) -> None:
        game_state = self.data_manager.load_state()
        theme_state = game_state.theme_specific.get(Theme.DKC)
        if theme_state:
            self._banana_count = theme_state.bananas
            if theme_state.extra_data:
                self._bonus_world_unlocked = theme_state.extra_data.get("bonus_world_unlocked", False)
    
    def _save_theme_state(self) -> None:
        game_state = self.data_manager.load_state()
        theme_state = game_state.theme_specific.get(Theme.DKC)
        if theme_state:
            theme_state.bananas = self._banana_count
            if theme_state.extra_data is None:
                theme_state.extra_data = {}
            theme_state.extra_data["bonus_world_unlocked"] = self._bonus_world_unlocked
            self.data_manager.save_state(game_state)
    
    def get_animation_for_correct(self) -> Animation:
        return Animation(
            type=AnimationType.COLLECT, theme=Theme.DKC,
            sprite_sheet="assets/dkc/dk_collect_banana.png",
            frames=self.COLLECT_FRAMES, fps=self.DEFAULT_FPS, loop=False
        )
    
    def get_animation_for_wrong(self) -> Animation:
        return Animation(
            type=AnimationType.DAMAGE, theme=Theme.DKC,
            sprite_sheet="assets/dkc/dk_lose_banana.png",
            frames=self.DAMAGE_FRAMES, fps=self.DEFAULT_FPS, loop=False
        )
    
    def get_collectible_for_correct(self) -> Collectible:
        return Collectible(
            id="dkc_banana", type=CollectibleType.BANANA, theme=Theme.DKC,
            name="Banana", description="A yellow banana collected for a correct answer",
            icon="assets/dkc/banana.png", owned=True
        )
    
    def get_level_view(self, level: Level) -> LevelView:
        collectibles = self._generate_level_collectibles(level)
        return LevelView(
            level=level, background=f"assets/dkc/jungle_{level.level_number}_bg.png",
            character_position=(50, 350), collectibles_visible=collectibles
        )
    
    def _generate_level_collectibles(self, level: Level) -> List[Collectible]:
        collectibles = []
        num_bananas = 10 + (level.level_number * 3)
        for i in range(num_bananas):
            collectibles.append(Collectible(
                id=f"level_{level.level_number}_banana_{i}",
                type=CollectibleType.BANANA, theme=Theme.DKC,
                name="Banana", description="A collectible banana",
                icon="assets/dkc/banana.png", owned=False
            ))
        if level.level_number % 5 == 0:
            collectibles.append(Collectible(
                id=f"level_{level.level_number}_dk_coin",
                type=CollectibleType.DK_COIN, theme=Theme.DKC,
                name="DK Coin", description="A rare DK Coin",
                icon="assets/dkc/dk_coin.png", owned=False
            ))
        return collectibles
    
    def get_dashboard_stats(self) -> ThemeStats:
        game_state = self.data_manager.load_state()
        theme_state = game_state.theme_specific.get(Theme.DKC)
        bananas = theme_state.bananas if theme_state else 0
        dk_coins = self._count_dk_coins()
        completion = self.get_world_completion()
        return ThemeStats(
            theme=Theme.DKC, primary_collectible_name="Bananas",
            primary_collectible_count=bananas, secondary_stat_name="DK Coins",
            secondary_stat_value=dk_coins, completion_percentage=completion
        )
    
    def _count_dk_coins(self) -> int:
        game_state = self.data_manager.load_state()
        return sum(1 for c in game_state.cosmetics 
                   if c.type == CollectibleType.DK_COIN and c.theme == Theme.DKC)
    
    def start_time_trial(self, duration_seconds: int = 0) -> TimeTrial:
        import hashlib
        if duration_seconds <= 0:
            duration_seconds = self.DEFAULT_TIME_TRIAL_DURATION
        trial_id = hashlib.md5(f"time_trial_{datetime.now().isoformat()}".encode()).hexdigest()[:12]
        trial = TimeTrial(
            id=trial_id, duration_seconds=duration_seconds,
            started_at=datetime.now(), remaining_seconds=float(duration_seconds),
            cards_completed=0, active=True, completed=False
        )
        self._active_time_trial = trial
        return trial
    
    def complete_time_trial(self, trial: TimeTrial, cards_completed: int) -> TimeTrialReward:
        trial.completed = True
        trial.active = False
        trial.cards_completed = cards_completed
        if self._active_time_trial and self._active_time_trial.id == trial.id:
            self._active_time_trial = None
        base_bananas = cards_completed * self.BANANAS_PER_CARD
        time_remaining = max(0.0, trial.remaining_seconds)
        bonus_bananas = int(time_remaining * self.BONUS_BANANAS_PER_SECOND)
        total_bananas = base_bananas + bonus_bananas
        self._banana_count += total_bananas
        self._save_theme_state()
        return TimeTrialReward(
            trial_id=trial.id, base_bananas=base_bananas,
            bonus_bananas=bonus_bananas, total_bananas=total_bananas,
            time_remaining=time_remaining, cards_completed=cards_completed
        )
    
    def update_time_trial(self, elapsed_seconds: float) -> Optional[TimeTrial]:
        if self._active_time_trial is None or not self._active_time_trial.active:
            return None
        self._active_time_trial.remaining_seconds -= elapsed_seconds
        if self._active_time_trial.remaining_seconds <= 0:
            self._active_time_trial.remaining_seconds = 0
            self._active_time_trial.active = False
        return self._active_time_trial
    
    def get_active_time_trial(self) -> Optional[TimeTrial]:
        return self._active_time_trial
    
    def is_time_trial_active(self) -> bool:
        return self._active_time_trial is not None and self._active_time_trial.active
    
    def get_world_completion(self) -> float:
        game_state = self.data_manager.load_state()
        total_cards = game_state.progression.total_cards_reviewed
        completion = min(1.0, total_cards / CARDS_FOR_FULL_COMPLETION)
        if completion >= 1.0 and not self._bonus_world_unlocked:
            self._bonus_world_unlocked = True
            self._save_theme_state()
        return completion
    
    def get_banana_count(self) -> int:
        return self._banana_count
    
    def add_bananas(self, count: int = 1) -> int:
        self._banana_count += count
        self._save_theme_state()
        return self._banana_count
    
    def remove_bananas(self, count: int = 0) -> int:
        if count <= 0:
            count = self.BANANAS_LOST_ON_WRONG
        self._banana_count = max(0, self._banana_count - count)
        self._save_theme_state()
        return self._banana_count
    
    def is_bonus_world_unlocked(self) -> bool:
        self.get_world_completion()
        return self._bonus_world_unlocked
    
    def get_jungle_worlds(self) -> List[JungleWorld]:
        worlds = [
            JungleWorld(id="jungle_1", name="Kongo Jungle",
                       completion_percentage=self._calculate_world_completion(1),
                       is_bonus_world=False, unlocked=True),
            JungleWorld(id="jungle_2", name="Monkey Mines",
                       completion_percentage=self._calculate_world_completion(2),
                       is_bonus_world=False, unlocked=self.get_world_completion() >= 0.2),
            JungleWorld(id="jungle_3", name="Vine Valley",
                       completion_percentage=self._calculate_world_completion(3),
                       is_bonus_world=False, unlocked=self.get_world_completion() >= 0.4),
            JungleWorld(id="jungle_4", name="Gorilla Glacier",
                       completion_percentage=self._calculate_world_completion(4),
                       is_bonus_world=False, unlocked=self.get_world_completion() >= 0.6),
            JungleWorld(id="jungle_5", name="Kremkroc Industries",
                       completion_percentage=self._calculate_world_completion(5),
                       is_bonus_world=False, unlocked=self.get_world_completion() >= 0.8),
        ]
        if self.is_bonus_world_unlocked():
            worlds.append(JungleWorld(id="bonus_world", name="Lost World",
                                     completion_percentage=0.0, is_bonus_world=True, unlocked=True))
        return worlds
    
    def _calculate_world_completion(self, world_number: int) -> float:
        overall_completion = self.get_world_completion()
        world_start = (world_number - 1) * 0.2
        world_end = world_number * 0.2
        if overall_completion >= world_end:
            return 1.0
        elif overall_completion <= world_start:
            return 0.0
        else:
            return (overall_completion - world_start) / 0.2
    
    def get_run_animation(self) -> Animation:
        return Animation(
            type=AnimationType.RUN, theme=Theme.DKC,
            sprite_sheet="assets/dkc/dk_run.png",
            frames=self.RUN_FRAMES, fps=self.DEFAULT_FPS, loop=True
        )
    
    def get_idle_animation(self) -> Animation:
        return Animation(
            type=AnimationType.IDLE, theme=Theme.DKC,
            sprite_sheet="assets/dkc/dk_idle.png",
            frames=self.IDLE_FRAMES, fps=15, loop=True
        )
    
    def get_victory_animation(self) -> Animation:
        return Animation(
            type=AnimationType.VICTORY, theme=Theme.DKC,
            sprite_sheet="assets/dkc/dk_victory.png",
            frames=[0, 1, 2, 3, 4, 5], fps=self.DEFAULT_FPS, loop=False
        )
