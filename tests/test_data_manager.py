"""
Unit tests for DataManager.

Tests the SQLite persistence functionality including database initialization,
state saving/loading, progression persistence, integrity checking, and backups.

Requirements: 8.1, 8.2, 8.3, 8.4, 8.5, 8.6, 8.7
"""

import json
import sqlite3
import tempfile
from datetime import datetime
from pathlib import Path

import pytest

from data import (
    Achievement,
    Collectible,
    CollectibleType,
    DataManager,
    GameState,
    Level,
    PowerUp,
    PowerUpType,
    ProgressionState,
    Theme,
    ThemeState,
)


@pytest.fixture
def temp_db_path():
    """Create a temporary database path for testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir) / "test_nintendanki.db"


@pytest.fixture
def data_manager(temp_db_path):
    """Create a DataManager instance with a temporary database."""
    dm = DataManager(temp_db_path)
    dm.initialize_database()
    yield dm
    dm.close()


class TestDatabaseInitialization:
    """Tests for database initialization."""
    
    def test_initialize_creates_database_file(self, temp_db_path):
        """Test that initialize_database creates the database file."""
        dm = DataManager(temp_db_path)
        assert not temp_db_path.exists()
        
        dm.initialize_database()
        
        assert temp_db_path.exists()
        dm.close()
    
    def test_initialize_creates_all_tables(self, data_manager, temp_db_path):
        """Test that all required tables are created."""
        conn = sqlite3.connect(str(temp_db_path))
        cursor = conn.cursor()
        
        # Get list of tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = {row[0] for row in cursor.fetchall()}
        
        expected_tables = {
            "progression",
            "achievements",
            "powerups",
            "active_powerups",
            "levels",
            "collectibles",
            "theme_state",
            "sessions",
            "reviews",
        }
        
        assert expected_tables.issubset(tables)
        conn.close()
    
    def test_initialize_creates_default_progression(self, data_manager, temp_db_path):
        """Test that default progression row is created."""
        conn = sqlite3.connect(str(temp_db_path))
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM progression WHERE id = 1")
        row = cursor.fetchone()
        
        assert row is not None
        conn.close()
    
    def test_initialize_creates_theme_state_for_all_themes(self, data_manager, temp_db_path):
        """Test that theme state is initialized for all themes."""
        conn = sqlite3.connect(str(temp_db_path))
        cursor = conn.cursor()
        
        cursor.execute("SELECT theme FROM theme_state")
        themes = {row[0] for row in cursor.fetchall()}
        
        expected_themes = {"mario", "zelda", "dkc"}
        assert themes == expected_themes
        conn.close()
    
    def test_initialize_is_idempotent(self, temp_db_path):
        """Test that calling initialize_database multiple times is safe."""
        dm = DataManager(temp_db_path)
        
        dm.initialize_database()
        dm.initialize_database()
        dm.initialize_database()
        
        # Should not raise any errors
        state = dm.load_state()
        assert state.progression.total_points == 0
        dm.close()
    
    def test_initialize_creates_parent_directories(self):
        """Test that parent directories are created if they don't exist."""
        with tempfile.TemporaryDirectory() as tmpdir:
            nested_path = Path(tmpdir) / "nested" / "dirs" / "test.db"
            dm = DataManager(nested_path)
            
            dm.initialize_database()
            
            assert nested_path.exists()
            dm.close()


class TestSaveAndLoadState:
    """Tests for saving and loading complete game state."""
    
    def test_save_and_load_empty_state(self, data_manager):
        """Test saving and loading an empty game state."""
        state = GameState(progression=ProgressionState())
        
        data_manager.save_state(state)
        loaded = data_manager.load_state()
        
        assert loaded.progression.total_points == 0
        assert loaded.currency == 0
        assert loaded.theme == Theme.MARIO
    
    def test_save_and_load_progression(self, data_manager):
        """Test saving and loading progression data."""
        progression = ProgressionState(
            total_points=1500,
            total_cards_reviewed=200,
            correct_answers=180,
            current_streak=15,
            best_streak=25,
            levels_unlocked=3,
            levels_completed=2,
        )
        state = GameState(progression=progression, currency=500)
        
        data_manager.save_state(state)
        loaded = data_manager.load_state()
        
        assert loaded.progression.total_points == 1500
        assert loaded.progression.total_cards_reviewed == 200
        assert loaded.progression.correct_answers == 180
        assert loaded.progression.current_streak == 15
        assert loaded.progression.best_streak == 25
        assert loaded.progression.levels_unlocked == 3
        assert loaded.progression.levels_completed == 2
        assert loaded.currency == 500
    
    def test_save_and_load_achievements(self, data_manager):
        """Test saving and loading achievements."""
        now = datetime.now()
        achievements = [
            Achievement(
                id="first_100",
                name="Century",
                description="Review 100 cards",
                icon="trophy.png",
                reward_currency=50,
                unlocked=True,
                unlock_date=now,
                progress=100,
                target=100,
            ),
            Achievement(
                id="streak_10",
                name="On Fire",
                description="Get a 10 streak",
                icon="fire.png",
                reward_currency=25,
                unlocked=False,
                progress=5,
                target=10,
            ),
        ]
        state = GameState(progression=ProgressionState(), achievements=achievements)
        
        data_manager.save_state(state)
        loaded = data_manager.load_state()
        
        assert len(loaded.achievements) == 2
        
        first_100 = next(a for a in loaded.achievements if a.id == "first_100")
        assert first_100.name == "Century"
        assert first_100.unlocked is True
        assert first_100.progress == 100
        
        streak_10 = next(a for a in loaded.achievements if a.id == "streak_10")
        assert streak_10.unlocked is False
        assert streak_10.progress == 5
    
    def test_save_and_load_powerups(self, data_manager):
        """Test saving and loading power-ups."""
        now = datetime.now()
        powerups = [
            PowerUp(
                id="mushroom_1",
                type=PowerUpType.MUSHROOM,
                theme=Theme.MARIO,
                name="Super Mushroom",
                description="Grow bigger!",
                icon="mushroom.png",
                quantity=3,
                duration_seconds=0,
                acquired_at=now,
            ),
            PowerUp(
                id="double_points_1",
                type=PowerUpType.DOUBLE_POINTS,
                theme=None,
                name="Double Points",
                description="Double your points!",
                icon="2x.png",
                quantity=1,
                duration_seconds=60,
            ),
        ]
        state = GameState(progression=ProgressionState(), powerups=powerups)
        
        data_manager.save_state(state)
        loaded = data_manager.load_state()
        
        assert len(loaded.powerups) == 2
        
        mushroom = next(p for p in loaded.powerups if p.id == "mushroom_1")
        assert mushroom.type == PowerUpType.MUSHROOM
        assert mushroom.theme == Theme.MARIO
        assert mushroom.quantity == 3
        
        double_points = next(p for p in loaded.powerups if p.id == "double_points_1")
        assert double_points.theme is None
        assert double_points.duration_seconds == 60
    
    def test_save_and_load_levels(self, data_manager):
        """Test saving and loading levels."""
        now = datetime.now()
        levels = [
            Level(
                id="mario_1_1",
                theme=Theme.MARIO,
                level_number=1,
                name="World 1-1",
                description="The beginning",
                unlocked=True,
                completed=True,
                best_accuracy=0.95,
                completion_date=now,
                rewards_claimed=True,
            ),
            Level(
                id="mario_1_2",
                theme=Theme.MARIO,
                level_number=2,
                name="World 1-2",
                unlocked=True,
                completed=False,
            ),
        ]
        state = GameState(progression=ProgressionState(), levels=levels)
        
        data_manager.save_state(state)
        loaded = data_manager.load_state()
        
        assert len(loaded.levels) == 2
        
        level_1 = next(lvl for lvl in loaded.levels if lvl.id == "mario_1_1")
        assert level_1.unlocked is True
        assert level_1.completed is True
        assert level_1.best_accuracy == 0.95
        
        level_2 = next(lvl for lvl in loaded.levels if lvl.id == "mario_1_2")
        assert level_2.unlocked is True
        assert level_2.completed is False
    
    def test_save_and_load_cosmetics(self, data_manager):
        """Test saving and loading cosmetics/collectibles."""
        now = datetime.now()
        cosmetics = [
            Collectible(
                id="mario_hat",
                type=CollectibleType.COSMETIC,
                theme=Theme.MARIO,
                name="Mario's Hat",
                description="The iconic red cap",
                icon="hat.png",
                owned=True,
                equipped=True,
                acquired_at=now,
                price=100,
            ),
        ]
        state = GameState(progression=ProgressionState(), cosmetics=cosmetics)
        
        data_manager.save_state(state)
        loaded = data_manager.load_state()
        
        assert len(loaded.cosmetics) == 1
        hat = loaded.cosmetics[0]
        assert hat.id == "mario_hat"
        assert hat.owned is True
        assert hat.equipped is True
    
    def test_save_and_load_theme(self, data_manager):
        """Test saving and loading current theme."""
        state = GameState(progression=ProgressionState(), theme=Theme.ZELDA)
        
        data_manager.save_state(state)
        loaded = data_manager.load_state()
        
        assert loaded.theme == Theme.ZELDA
    
    def test_save_and_load_theme_specific_state(self, data_manager):
        """Test saving and loading theme-specific state."""
        theme_specific = {
            Theme.MARIO: ThemeState(theme=Theme.MARIO, coins=500),
            Theme.ZELDA: ThemeState(theme=Theme.ZELDA, hearts=5),
            Theme.DKC: ThemeState(
                theme=Theme.DKC,
                bananas=1000,
                map_progress={"world_1": True, "world_2": False},
                extra_data={"bonus_collected": 5},
            ),
        }
        state = GameState(
            progression=ProgressionState(),
            theme_specific=theme_specific,
        )
        
        data_manager.save_state(state)
        loaded = data_manager.load_state()
        
        assert loaded.theme_specific[Theme.MARIO].coins == 500
        assert loaded.theme_specific[Theme.ZELDA].hearts == 5
        assert loaded.theme_specific[Theme.DKC].bananas == 1000
        assert loaded.theme_specific[Theme.DKC].map_progress == {"world_1": True, "world_2": False}
        assert loaded.theme_specific[Theme.DKC].extra_data == {"bonus_collected": 5}


class TestSaveProgression:
    """Tests for per-review progression persistence."""
    
    def test_save_progression_updates_database(self, data_manager):
        """Test that save_progression updates the database."""
        progression = ProgressionState(
            total_points=100,
            total_cards_reviewed=10,
            correct_answers=9,
            current_streak=5,
            best_streak=5,
            levels_unlocked=0,
            levels_completed=0,
        )
        
        data_manager.save_progression(progression)
        loaded = data_manager.load_state()
        
        assert loaded.progression.total_points == 100
        assert loaded.progression.total_cards_reviewed == 10
        assert loaded.progression.correct_answers == 9
        assert loaded.progression.current_streak == 5
    
    def test_save_progression_preserves_other_data(self, data_manager):
        """Test that save_progression doesn't affect other data."""
        # First save complete state
        achievement = Achievement(
            id="test",
            name="Test",
            description="Test",
            icon="test.png",
            reward_currency=10,
            target=10,
        )
        state = GameState(
            progression=ProgressionState(total_points=50),
            achievements=[achievement],
            currency=200,
            theme=Theme.ZELDA,
        )
        data_manager.save_state(state)
        
        # Now update just progression
        new_progression = ProgressionState(total_points=100)
        data_manager.save_progression(new_progression)
        
        # Load and verify other data is preserved
        loaded = data_manager.load_state()
        assert loaded.progression.total_points == 100
        assert len(loaded.achievements) == 1
        assert loaded.theme == Theme.ZELDA
    
    def test_save_progression_multiple_times(self, data_manager):
        """Test saving progression multiple times."""
        for i in range(1, 11):
            progression = ProgressionState(
                total_points=i * 10,
                total_cards_reviewed=i,
                correct_answers=i,
            )
            data_manager.save_progression(progression)
        
        loaded = data_manager.load_state()
        assert loaded.progression.total_points == 100
        assert loaded.progression.total_cards_reviewed == 10


class TestCheckIntegrity:
    """Tests for database integrity checking."""
    
    def test_check_integrity_valid_database(self, data_manager):
        """Test that check_integrity returns True for valid database."""
        assert data_manager.check_integrity() is True
    
    def test_check_integrity_after_operations(self, data_manager):
        """Test integrity after various operations."""
        state = GameState(
            progression=ProgressionState(total_points=1000),
            currency=500,
        )
        data_manager.save_state(state)
        
        assert data_manager.check_integrity() is True
    
    def test_check_integrity_corrupted_database(self, temp_db_path):
        """Test that check_integrity returns False for corrupted database."""
        # Create a corrupted database file
        temp_db_path.parent.mkdir(parents=True, exist_ok=True)
        with open(temp_db_path, 'wb') as f:
            f.write(b"This is not a valid SQLite database")
        
        dm = DataManager(temp_db_path)
        result = dm.check_integrity()
        dm.close()  # Ensure connection is closed before cleanup
        assert result is False


class TestCreateBackup:
    """Tests for database backup creation."""
    
    def test_create_backup_creates_file(self, data_manager, temp_db_path):
        """Test that create_backup creates a backup file."""
        # Save some data first
        state = GameState(
            progression=ProgressionState(total_points=1000),
            currency=500,
        )
        data_manager.save_state(state)
        
        backup_path = data_manager.create_backup()
        
        assert backup_path.exists()
        assert "backup" in backup_path.name
    
    def test_create_backup_contains_same_data(self, data_manager, temp_db_path):
        """Test that backup contains the same data as original."""
        state = GameState(
            progression=ProgressionState(total_points=1000),
            currency=500,
        )
        data_manager.save_state(state)
        
        backup_path = data_manager.create_backup()
        
        # Load from backup
        backup_dm = DataManager(backup_path)
        backup_dm.initialize_database()
        backup_state = backup_dm.load_state()
        
        assert backup_state.progression.total_points == 1000
        assert backup_state.currency == 500
        backup_dm.close()
    
    def test_create_multiple_backups(self, data_manager, temp_db_path):
        """Test creating multiple backups."""
        import time
        
        backup1 = data_manager.create_backup()
        time.sleep(1.1)  # Ensure different timestamps (need > 1 second for timestamp format)
        backup2 = data_manager.create_backup()
        
        assert backup1.exists()
        assert backup2.exists()
        assert backup1 != backup2


class TestJsonExportImport:
    """Tests for JSON export and import functionality."""
    
    def test_export_to_json(self, data_manager):
        """Test exporting game state to JSON."""
        state = GameState(
            progression=ProgressionState(total_points=1000),
            currency=500,
            theme=Theme.ZELDA,
        )
        data_manager.save_state(state)
        
        with tempfile.TemporaryDirectory() as tmpdir:
            json_path = Path(tmpdir) / "backup.json"
            data_manager.export_to_json(json_path)
            
            assert json_path.exists()
            
            with open(json_path, 'r') as f:
                data = json.load(f)
            
            assert data["progression"]["total_points"] == 1000
            assert data["currency"] == 500
            assert data["theme"] == "zelda"
    
    def test_import_from_json(self, data_manager):
        """Test importing game state from JSON."""
        json_data = {
            "progression": {
                "total_points": 2000,
                "total_cards_reviewed": 200,
                "correct_answers": 180,
                "current_streak": 10,
                "best_streak": 20,
                "levels_unlocked": 4,
                "levels_completed": 3,
            },
            "achievements": [],
            "powerups": [],
            "levels": [],
            "currency": 750,
            "cosmetics": [],
            "theme": "dkc",
            "theme_specific": {},
        }
        
        with tempfile.TemporaryDirectory() as tmpdir:
            json_path = Path(tmpdir) / "import.json"
            with open(json_path, 'w') as f:
                json.dump(json_data, f)
            
            imported = data_manager.import_from_json(json_path)
            
            assert imported.progression.total_points == 2000
            assert imported.currency == 750
            assert imported.theme == Theme.DKC
    
    def test_export_import_roundtrip(self, data_manager):
        """Test that export and import produce equivalent state."""
        now = datetime.now()
        original_state = GameState(
            progression=ProgressionState(
                total_points=1500,
                total_cards_reviewed=150,
                correct_answers=140,
                current_streak=8,
                best_streak=15,
                levels_unlocked=3,
                levels_completed=2,
            ),
            achievements=[
                Achievement(
                    id="test_achievement",
                    name="Test",
                    description="Test achievement",
                    icon="test.png",
                    reward_currency=50,
                    unlocked=True,
                    unlock_date=now,
                    progress=100,
                    target=100,
                ),
            ],
            powerups=[
                PowerUp(
                    id="test_powerup",
                    type=PowerUpType.MUSHROOM,
                    theme=Theme.MARIO,
                    name="Test Powerup",
                    description="Test",
                    icon="test.png",
                    quantity=2,
                ),
            ],
            levels=[
                Level(
                    id="test_level",
                    theme=Theme.MARIO,
                    level_number=1,
                    name="Test Level",
                    unlocked=True,
                    completed=True,
                    best_accuracy=0.95,
                ),
            ],
            currency=1000,
            theme=Theme.ZELDA,
        )
        
        data_manager.save_state(original_state)
        
        with tempfile.TemporaryDirectory() as tmpdir:
            json_path = Path(tmpdir) / "roundtrip.json"
            data_manager.export_to_json(json_path)
            
            # Create new data manager and import
            new_db_path = Path(tmpdir) / "new.db"
            new_dm = DataManager(new_db_path)
            new_dm.initialize_database()
            
            imported = new_dm.import_from_json(json_path)
            
            assert imported.progression.total_points == 1500
            assert imported.currency == 1000
            assert imported.theme == Theme.ZELDA
            assert len(imported.achievements) == 1
            assert len(imported.powerups) == 1
            assert len(imported.levels) == 1
            
            new_dm.close()


class TestEdgeCases:
    """Tests for edge cases and error handling."""
    
    def test_load_state_empty_database(self, data_manager):
        """Test loading state from empty database returns defaults."""
        state = data_manager.load_state()
        
        assert state.progression.total_points == 0
        assert state.currency == 0
        assert state.theme == Theme.MARIO
    
    def test_save_state_with_none_values(self, data_manager):
        """Test saving state with None optional values."""
        state = GameState(
            progression=ProgressionState(),
            achievements=[
                Achievement(
                    id="test",
                    name="Test",
                    description="Test",
                    icon="test.png",
                    reward_currency=0,
                    unlock_date=None,
                    target=10,
                ),
            ],
            powerups=[
                PowerUp(
                    id="test",
                    type=PowerUpType.DOUBLE_POINTS,
                    theme=None,
                    name="Test",
                    description="Test",
                    icon="test.png",
                    acquired_at=None,
                ),
            ],
        )
        
        data_manager.save_state(state)
        loaded = data_manager.load_state()
        
        assert loaded.achievements[0].unlock_date is None
        assert loaded.powerups[0].theme is None
    
    def test_update_existing_records(self, data_manager):
        """Test that saving updates existing records instead of duplicating."""
        # Save initial state
        state1 = GameState(
            progression=ProgressionState(total_points=100),
            achievements=[
                Achievement(
                    id="test",
                    name="Test",
                    description="Test",
                    icon="test.png",
                    reward_currency=10,
                    progress=50,
                    target=100,
                ),
            ],
        )
        data_manager.save_state(state1)
        
        # Save updated state
        state2 = GameState(
            progression=ProgressionState(total_points=200),
            achievements=[
                Achievement(
                    id="test",
                    name="Test Updated",
                    description="Test",
                    icon="test.png",
                    reward_currency=10,
                    progress=100,
                    target=100,
                    unlocked=True,
                ),
            ],
        )
        data_manager.save_state(state2)
        
        loaded = data_manager.load_state()
        
        assert loaded.progression.total_points == 200
        assert len(loaded.achievements) == 1
        assert loaded.achievements[0].name == "Test Updated"
        assert loaded.achievements[0].progress == 100
        assert loaded.achievements[0].unlocked is True
    
    def test_close_and_reopen(self, temp_db_path):
        """Test closing and reopening the database."""
        dm1 = DataManager(temp_db_path)
        dm1.initialize_database()
        
        state = GameState(
            progression=ProgressionState(total_points=500),
            currency=100,
        )
        dm1.save_state(state)
        dm1.close()
        
        # Reopen
        dm2 = DataManager(temp_db_path)
        loaded = dm2.load_state()
        
        assert loaded.progression.total_points == 500
        assert loaded.currency == 100
        dm2.close()
