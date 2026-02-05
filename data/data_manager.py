"""
DataManager for NintendAnki.

This module provides SQLite database operations for persisting game state,
including progression, achievements, power-ups, levels, and theme-specific data.

Requirements: 8.1, 8.2, 8.3, 8.4, 8.5
"""

import json
import shutil
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional

from data.models import (
    Achievement,
    Collectible,
    CollectibleType,
    GameState,
    Level,
    PowerUp,
    PowerUpType,
    ProgressionState,
    Theme,
    ThemeState,
)


def _adapt_datetime(dt: datetime) -> str:
    """Adapt datetime to ISO format string for SQLite storage."""
    return dt.isoformat()


def _convert_datetime(s: bytes) -> datetime:
    """Convert ISO format string from SQLite to datetime."""
    return datetime.fromisoformat(s.decode())


# Register adapters and converters for datetime
sqlite3.register_adapter(datetime, _adapt_datetime)
sqlite3.register_converter("TIMESTAMP", _convert_datetime)


class DataManager:
    """Manages SQLite database operations for game state persistence.
    
    This class handles all database operations including:
    - Creating and initializing the database schema
    - Saving and loading complete game state
    - Per-review progression persistence
    - Database integrity checking and backup creation
    
    Attributes:
        db_path: Path to the SQLite database file
    """
    
    # SQL schema for all tables
    SCHEMA = """
    -- Core progression table
    CREATE TABLE IF NOT EXISTS progression (
        id INTEGER PRIMARY KEY,
        total_points INTEGER NOT NULL DEFAULT 0,
        total_cards_reviewed INTEGER NOT NULL DEFAULT 0,
        correct_answers INTEGER NOT NULL DEFAULT 0,
        current_streak INTEGER NOT NULL DEFAULT 0,
        best_streak INTEGER NOT NULL DEFAULT 0,
        levels_unlocked INTEGER NOT NULL DEFAULT 0,
        levels_completed INTEGER NOT NULL DEFAULT 0,
        currency INTEGER NOT NULL DEFAULT 0,
        current_theme TEXT NOT NULL DEFAULT 'mario',
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    -- Achievements table
    CREATE TABLE IF NOT EXISTS achievements (
        id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        description TEXT NOT NULL,
        icon TEXT NOT NULL,
        reward_currency INTEGER NOT NULL DEFAULT 0,
        unlocked INTEGER NOT NULL DEFAULT 0,
        unlock_date TIMESTAMP,
        progress INTEGER NOT NULL DEFAULT 0,
        target INTEGER NOT NULL
    );

    -- Power-ups inventory
    CREATE TABLE IF NOT EXISTS powerups (
        id TEXT PRIMARY KEY,
        type TEXT NOT NULL,
        theme TEXT,
        name TEXT NOT NULL,
        description TEXT NOT NULL,
        icon TEXT NOT NULL,
        quantity INTEGER NOT NULL DEFAULT 1,
        duration_seconds INTEGER NOT NULL DEFAULT 0,
        acquired_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    -- Active power-ups (with duration)
    CREATE TABLE IF NOT EXISTS active_powerups (
        id TEXT PRIMARY KEY,
        powerup_id TEXT NOT NULL,
        activated_at TIMESTAMP NOT NULL,
        duration_seconds INTEGER NOT NULL,
        remaining_seconds REAL NOT NULL,
        FOREIGN KEY (powerup_id) REFERENCES powerups(id)
    );

    -- Levels table
    CREATE TABLE IF NOT EXISTS levels (
        id TEXT PRIMARY KEY,
        theme TEXT NOT NULL,
        level_number INTEGER NOT NULL,
        name TEXT NOT NULL,
        description TEXT NOT NULL DEFAULT '',
        unlocked INTEGER NOT NULL DEFAULT 0,
        completed INTEGER NOT NULL DEFAULT 0,
        best_accuracy REAL,
        completion_date TIMESTAMP,
        rewards_claimed INTEGER NOT NULL DEFAULT 0
    );

    -- Collectibles/cosmetics
    CREATE TABLE IF NOT EXISTS collectibles (
        id TEXT PRIMARY KEY,
        type TEXT NOT NULL,
        theme TEXT,
        name TEXT NOT NULL,
        description TEXT NOT NULL,
        icon TEXT NOT NULL,
        owned INTEGER NOT NULL DEFAULT 0,
        equipped INTEGER NOT NULL DEFAULT 0,
        acquired_at TIMESTAMP,
        price INTEGER NOT NULL DEFAULT 0
    );

    -- Theme-specific state
    CREATE TABLE IF NOT EXISTS theme_state (
        theme TEXT PRIMARY KEY,
        coins INTEGER NOT NULL DEFAULT 0,
        bananas INTEGER NOT NULL DEFAULT 0,
        hearts INTEGER NOT NULL DEFAULT 3,
        map_progress TEXT,
        extra_data TEXT
    );

    -- Session history
    CREATE TABLE IF NOT EXISTS sessions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        started_at TIMESTAMP NOT NULL,
        ended_at TIMESTAMP,
        cards_reviewed INTEGER NOT NULL DEFAULT 0,
        correct_answers INTEGER NOT NULL DEFAULT 0,
        points_earned INTEGER NOT NULL DEFAULT 0,
        theme TEXT NOT NULL
    );

    -- Review history
    CREATE TABLE IF NOT EXISTS reviews (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        session_id INTEGER NOT NULL,
        card_id INTEGER NOT NULL,
        deck_id INTEGER NOT NULL,
        is_correct INTEGER NOT NULL,
        ease INTEGER NOT NULL,
        points_earned INTEGER NOT NULL,
        streak_at_time INTEGER NOT NULL,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (session_id) REFERENCES sessions(id)
    );
    """
    
    def __init__(self, db_path: Path):
        """Initialize the DataManager.
        
        Args:
            db_path: Path to the SQLite database file
        """
        self.db_path = Path(db_path)
        self._connection: Optional[sqlite3.Connection] = None
    
    def _get_connection(self) -> sqlite3.Connection:
        """Get or create a database connection.
        
        Returns:
            SQLite connection object
        """
        if self._connection is None:
            self._connection = sqlite3.connect(
                str(self.db_path),
                detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES
            )
            self._connection.row_factory = sqlite3.Row
        return self._connection
    
    def _close_connection(self) -> None:
        """Close the database connection if open."""
        if self._connection is not None:
            self._connection.close()
            self._connection = None
    
    def initialize_database(self) -> None:
        """Create database tables if they don't exist.
        
        This method creates all required tables for storing game state.
        If the database file doesn't exist, it will be created.
        
        Requirements: 8.1
        """
        # Ensure parent directory exists
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # Execute schema creation
        cursor.executescript(self.SCHEMA)
        
        # Initialize default progression row if not exists
        cursor.execute("""
            INSERT OR IGNORE INTO progression (id, total_points, total_cards_reviewed,
                correct_answers, current_streak, best_streak, levels_unlocked,
                levels_completed, currency, current_theme)
            VALUES (1, 0, 0, 0, 0, 0, 0, 0, 0, 'mario')
        """)
        
        # Initialize theme state for all themes
        for theme in Theme:
            cursor.execute("""
                INSERT OR IGNORE INTO theme_state (theme, coins, bananas, hearts)
                VALUES (?, 0, 0, 3)
            """, (theme.value,))
        
        conn.commit()
    
    def save_state(self, state: GameState) -> None:
        """Save complete game state to database.
        
        This method persists all game state including progression,
        achievements, power-ups, levels, cosmetics, and theme-specific data.
        
        Args:
            state: Complete game state to save
            
        Requirements: 8.3
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            # Save progression
            cursor.execute("""
                UPDATE progression SET
                    total_points = ?,
                    total_cards_reviewed = ?,
                    correct_answers = ?,
                    current_streak = ?,
                    best_streak = ?,
                    levels_unlocked = ?,
                    levels_completed = ?,
                    currency = ?,
                    current_theme = ?,
                    updated_at = ?
                WHERE id = 1
            """, (
                state.progression.total_points,
                state.progression.total_cards_reviewed,
                state.progression.correct_answers,
                state.progression.current_streak,
                state.progression.best_streak,
                state.progression.levels_unlocked,
                state.progression.levels_completed,
                state.currency,
                state.theme.value,
                datetime.now()
            ))
            
            # Save achievements
            for achievement in state.achievements:
                cursor.execute("""
                    INSERT OR REPLACE INTO achievements
                    (id, name, description, icon, reward_currency, unlocked, unlock_date, progress, target)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    achievement.id,
                    achievement.name,
                    achievement.description,
                    achievement.icon,
                    achievement.reward_currency,
                    1 if achievement.unlocked else 0,
                    achievement.unlock_date,
                    achievement.progress,
                    achievement.target
                ))
            
            # Save power-ups
            for powerup in state.powerups:
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
                    powerup.acquired_at
                ))
            
            # Save levels
            for level in state.levels:
                cursor.execute("""
                    INSERT OR REPLACE INTO levels
                    (id, theme, level_number, name, description, unlocked, completed,
                     best_accuracy, completion_date, rewards_claimed)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    level.id,
                    level.theme.value,
                    level.level_number,
                    level.name,
                    level.description,
                    1 if level.unlocked else 0,
                    1 if level.completed else 0,
                    level.best_accuracy,
                    level.completion_date,
                    1 if level.rewards_claimed else 0
                ))
            
            # Save cosmetics/collectibles
            for cosmetic in state.cosmetics:
                cursor.execute("""
                    INSERT OR REPLACE INTO collectibles
                    (id, type, theme, name, description, icon, owned, equipped, acquired_at, price)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    cosmetic.id,
                    cosmetic.type.value,
                    cosmetic.theme.value if cosmetic.theme else None,
                    cosmetic.name,
                    cosmetic.description,
                    cosmetic.icon,
                    1 if cosmetic.owned else 0,
                    1 if cosmetic.equipped else 0,
                    cosmetic.acquired_at,
                    cosmetic.price
                ))
            
            # Save theme-specific state
            for theme, theme_state in state.theme_specific.items():
                cursor.execute("""
                    INSERT OR REPLACE INTO theme_state
                    (theme, coins, bananas, hearts, map_progress, extra_data)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    theme.value,
                    theme_state.coins,
                    theme_state.bananas,
                    theme_state.hearts,
                    json.dumps(theme_state.map_progress) if theme_state.map_progress else None,
                    json.dumps(theme_state.extra_data) if theme_state.extra_data else None
                ))
            
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
    
    def load_state(self) -> GameState:
        """Load complete game state from database.
        
        This method loads all persisted game state including progression,
        achievements, power-ups, levels, cosmetics, and theme-specific data.
        
        Returns:
            Complete game state loaded from database
            
        Requirements: 8.4
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # Load progression
        cursor.execute("SELECT * FROM progression WHERE id = 1")
        row = cursor.fetchone()
        
        if row is None:
            # Return default state if no data exists
            return GameState(progression=ProgressionState())
        
        progression = ProgressionState(
            total_points=row["total_points"],
            total_cards_reviewed=row["total_cards_reviewed"],
            correct_answers=row["correct_answers"],
            current_streak=row["current_streak"],
            best_streak=row["best_streak"],
            levels_unlocked=row["levels_unlocked"],
            levels_completed=row["levels_completed"],
            session_accuracy=1.0,  # Session values reset on load
            session_health=100  # Full health on load (0-100 scale)
        )
        
        currency = row["currency"]
        current_theme = Theme(row["current_theme"])
        
        # Load achievements
        cursor.execute("SELECT * FROM achievements")
        achievements = []
        for row in cursor.fetchall():
            achievements.append(Achievement(
                id=row["id"],
                name=row["name"],
                description=row["description"],
                icon=row["icon"],
                reward_currency=row["reward_currency"],
                unlocked=bool(row["unlocked"]),
                unlock_date=row["unlock_date"],
                progress=row["progress"],
                target=row["target"]
            ))
        
        # Load power-ups
        cursor.execute("SELECT * FROM powerups")
        powerups = []
        for row in cursor.fetchall():
            theme = Theme(row["theme"]) if row["theme"] else None
            powerups.append(PowerUp(
                id=row["id"],
                type=PowerUpType(row["type"]),
                theme=theme,
                name=row["name"],
                description=row["description"],
                icon=row["icon"],
                quantity=row["quantity"],
                duration_seconds=row["duration_seconds"],
                acquired_at=row["acquired_at"]
            ))
        
        # Load levels
        cursor.execute("SELECT * FROM levels")
        levels = []
        for row in cursor.fetchall():
            levels.append(Level(
                id=row["id"],
                theme=Theme(row["theme"]),
                level_number=row["level_number"],
                name=row["name"],
                description=row["description"],
                unlocked=bool(row["unlocked"]),
                completed=bool(row["completed"]),
                best_accuracy=row["best_accuracy"],
                completion_date=row["completion_date"],
                rewards_claimed=bool(row["rewards_claimed"])
            ))
        
        # Load cosmetics/collectibles
        cursor.execute("SELECT * FROM collectibles")
        cosmetics = []
        for row in cursor.fetchall():
            theme = Theme(row["theme"]) if row["theme"] else None
            cosmetics.append(Collectible(
                id=row["id"],
                type=CollectibleType(row["type"]),
                theme=theme,
                name=row["name"],
                description=row["description"],
                icon=row["icon"],
                owned=bool(row["owned"]),
                equipped=bool(row["equipped"]),
                acquired_at=row["acquired_at"],
                price=row["price"]
            ))
        
        # Load theme-specific state
        cursor.execute("SELECT * FROM theme_state")
        theme_specific: Dict[Theme, ThemeState] = {}
        for row in cursor.fetchall():
            theme = Theme(row["theme"])
            map_progress = json.loads(row["map_progress"]) if row["map_progress"] else None
            extra_data = json.loads(row["extra_data"]) if row["extra_data"] else None
            theme_specific[theme] = ThemeState(
                theme=theme,
                coins=row["coins"],
                bananas=row["bananas"],
                hearts=row["hearts"],
                map_progress=map_progress,
                extra_data=extra_data
            )
        
        return GameState(
            progression=progression,
            achievements=achievements,
            powerups=powerups,
            levels=levels,
            currency=currency,
            cosmetics=cosmetics,
            theme=current_theme,
            theme_specific=theme_specific
        )
    
    def save_progression(self, progression: ProgressionState) -> None:
        """Save progression state (called after each review).
        
        This method provides fast persistence of progression data,
        designed to be called after each card review for immediate
        state persistence.
        
        Args:
            progression: Current progression state to save
            
        Requirements: 8.2
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE progression SET
                total_points = ?,
                total_cards_reviewed = ?,
                correct_answers = ?,
                current_streak = ?,
                best_streak = ?,
                levels_unlocked = ?,
                levels_completed = ?,
                updated_at = ?
            WHERE id = 1
        """, (
            progression.total_points,
            progression.total_cards_reviewed,
            progression.correct_answers,
            progression.current_streak,
            progression.best_streak,
            progression.levels_unlocked,
            progression.levels_completed,
            datetime.now()
        ))
        
        conn.commit()
    
    def check_integrity(self) -> bool:
        """Check database integrity.
        
        Performs SQLite integrity check to verify the database is not corrupted.
        
        Returns:
            True if database is valid, False if corrupted
            
        Requirements: 8.5
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute("PRAGMA integrity_check")
            result = cursor.fetchone()
            return result[0] == "ok"
        except sqlite3.DatabaseError:
            return False
        except Exception:
            return False
    
    def create_backup(self) -> Path:
        """Create a backup of the database file.
        
        Creates a timestamped backup copy of the database file in the same
        directory as the original database.
        
        Returns:
            Path to the created backup file
            
        Requirements: 8.5
        """
        # Close connection to ensure all data is flushed
        self._close_connection()
        
        # Generate backup filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"{self.db_path.stem}_backup_{timestamp}{self.db_path.suffix}"
        backup_path = self.db_path.parent / backup_name
        
        # Copy the database file
        shutil.copy2(self.db_path, backup_path)
        
        return backup_path
    
    def export_to_json(self, path: Path) -> None:
        """Export game state to JSON file for backup.
        
        Args:
            path: Path to the JSON file to create
            
        Requirements: 8.6
        """
        state = self.load_state()
        
        # Convert state to JSON-serializable dict
        data = self._state_to_dict(state)
        
        # Write to file
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, default=str)
    
    def import_from_json(self, path: Path) -> GameState:
        """Import game state from JSON backup file.
        
        Args:
            path: Path to the JSON file to import
            
        Returns:
            Imported game state
            
        Requirements: 8.7
        """
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        state = self._dict_to_state(data)
        self.save_state(state)
        return state
    
    def _state_to_dict(self, state: GameState) -> dict:
        """Convert GameState to a JSON-serializable dictionary."""
        return {
            "progression": {
                "total_points": state.progression.total_points,
                "total_cards_reviewed": state.progression.total_cards_reviewed,
                "correct_answers": state.progression.correct_answers,
                "current_streak": state.progression.current_streak,
                "best_streak": state.progression.best_streak,
                "levels_unlocked": state.progression.levels_unlocked,
                "levels_completed": state.progression.levels_completed,
                "session_accuracy": state.progression.session_accuracy,
                "session_health": state.progression.session_health,
            },
            "achievements": [
                {
                    "id": a.id,
                    "name": a.name,
                    "description": a.description,
                    "icon": a.icon,
                    "reward_currency": a.reward_currency,
                    "unlocked": a.unlocked,
                    "unlock_date": a.unlock_date.isoformat() if a.unlock_date else None,
                    "progress": a.progress,
                    "target": a.target,
                }
                for a in state.achievements
            ],
            "powerups": [
                {
                    "id": p.id,
                    "type": p.type.value,
                    "theme": p.theme.value if p.theme else None,
                    "name": p.name,
                    "description": p.description,
                    "icon": p.icon,
                    "quantity": p.quantity,
                    "duration_seconds": p.duration_seconds,
                    "acquired_at": p.acquired_at.isoformat() if p.acquired_at else None,
                }
                for p in state.powerups
            ],
            "levels": [
                {
                    "id": level.id,
                    "theme": level.theme.value,
                    "level_number": level.level_number,
                    "name": level.name,
                    "description": level.description,
                    "unlocked": level.unlocked,
                    "completed": level.completed,
                    "best_accuracy": level.best_accuracy,
                    "completion_date": level.completion_date.isoformat() if level.completion_date else None,
                    "rewards_claimed": level.rewards_claimed,
                }
                for level in state.levels
            ],
            "currency": state.currency,
            "cosmetics": [
                {
                    "id": c.id,
                    "type": c.type.value,
                    "theme": c.theme.value if c.theme else None,
                    "name": c.name,
                    "description": c.description,
                    "icon": c.icon,
                    "owned": c.owned,
                    "equipped": c.equipped,
                    "acquired_at": c.acquired_at.isoformat() if c.acquired_at else None,
                    "price": c.price,
                }
                for c in state.cosmetics
            ],
            "theme": state.theme.value,
            "theme_specific": {
                theme.value: {
                    "coins": ts.coins,
                    "bananas": ts.bananas,
                    "hearts": ts.hearts,
                    "map_progress": ts.map_progress,
                    "extra_data": ts.extra_data,
                }
                for theme, ts in state.theme_specific.items()
            },
        }
    
    def _dict_to_state(self, data: dict) -> GameState:
        """Convert a dictionary to GameState."""
        progression = ProgressionState(
            total_points=data["progression"]["total_points"],
            total_cards_reviewed=data["progression"]["total_cards_reviewed"],
            correct_answers=data["progression"]["correct_answers"],
            current_streak=data["progression"]["current_streak"],
            best_streak=data["progression"]["best_streak"],
            levels_unlocked=data["progression"]["levels_unlocked"],
            levels_completed=data["progression"]["levels_completed"],
            session_accuracy=data["progression"].get("session_accuracy", 1.0),
            session_health=data["progression"].get("session_health", 100),
        )
        
        achievements = [
            Achievement(
                id=a["id"],
                name=a["name"],
                description=a["description"],
                icon=a["icon"],
                reward_currency=a["reward_currency"],
                unlocked=a["unlocked"],
                unlock_date=datetime.fromisoformat(a["unlock_date"]) if a["unlock_date"] else None,
                progress=a["progress"],
                target=a["target"],
            )
            for a in data.get("achievements", [])
        ]
        
        powerups = [
            PowerUp(
                id=p["id"],
                type=PowerUpType(p["type"]),
                theme=Theme(p["theme"]) if p["theme"] else None,
                name=p["name"],
                description=p["description"],
                icon=p["icon"],
                quantity=p["quantity"],
                duration_seconds=p["duration_seconds"],
                acquired_at=datetime.fromisoformat(p["acquired_at"]) if p["acquired_at"] else None,
            )
            for p in data.get("powerups", [])
        ]
        
        levels = [
            Level(
                id=lvl["id"],
                theme=Theme(lvl["theme"]),
                level_number=lvl["level_number"],
                name=lvl["name"],
                description=lvl.get("description", ""),
                unlocked=lvl["unlocked"],
                completed=lvl["completed"],
                best_accuracy=lvl["best_accuracy"],
                completion_date=datetime.fromisoformat(lvl["completion_date"]) if lvl["completion_date"] else None,
                rewards_claimed=lvl["rewards_claimed"],
            )
            for lvl in data.get("levels", [])
        ]
        
        cosmetics = [
            Collectible(
                id=c["id"],
                type=CollectibleType(c["type"]),
                theme=Theme(c["theme"]) if c["theme"] else None,
                name=c["name"],
                description=c["description"],
                icon=c["icon"],
                owned=c["owned"],
                equipped=c["equipped"],
                acquired_at=datetime.fromisoformat(c["acquired_at"]) if c["acquired_at"] else None,
                price=c["price"],
            )
            for c in data.get("cosmetics", [])
        ]
        
        theme_specific = {}
        for theme_str, ts_data in data.get("theme_specific", {}).items():
            theme = Theme(theme_str)
            theme_specific[theme] = ThemeState(
                theme=theme,
                coins=ts_data["coins"],
                bananas=ts_data["bananas"],
                hearts=ts_data["hearts"],
                map_progress=ts_data.get("map_progress"),
                extra_data=ts_data.get("extra_data"),
            )
        
        return GameState(
            progression=progression,
            achievements=achievements,
            powerups=powerups,
            levels=levels,
            currency=data.get("currency", 0),
            cosmetics=cosmetics,
            theme=Theme(data.get("theme", "mario")),
            theme_specific=theme_specific,
        )
    
    def close(self) -> None:
        """Close the database connection."""
        self._close_connection()
