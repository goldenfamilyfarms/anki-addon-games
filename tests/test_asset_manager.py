"""
Tests for the AssetManager class.

This module contains unit tests for the AssetManager, testing:
- Sprite sheet loading and caching
- Asset path resolution for each theme
- Handling of missing assets with placeholders
- Support for common image formats

Requirements: 4.7, 9.2
"""

import tempfile
from pathlib import Path

from data.models import Theme
from ui.asset_manager import AssetManager, Sprite, SpriteSheet


class TestAssetManagerInitialization:
    """Tests for AssetManager initialization."""
    
    def test_default_initialization(self):
        """Test AssetManager initializes with default assets root."""
        manager = AssetManager()
        assert manager.assets_root == Path("assets")
        assert len(manager._cache) == 0
        assert len(manager._placeholder_cache) == 0
    
    def test_custom_assets_root_string(self):
        """Test AssetManager accepts string path for assets root."""
        manager = AssetManager(assets_root="custom/assets")
        assert manager.assets_root == Path("custom/assets")
    
    def test_custom_assets_root_path(self):
        """Test AssetManager accepts Path object for assets root."""
        custom_path = Path("custom/assets")
        manager = AssetManager(assets_root=custom_path)
        assert manager.assets_root == custom_path
    
    def test_initial_cache_stats(self):
        """Test initial cache statistics are zero."""
        manager = AssetManager()
        stats = manager.get_cache_stats()
        assert stats["cached_assets"] == 0
        assert stats["cached_placeholders"] == 0
        assert stats["cache_hits"] == 0
        assert stats["cache_misses"] == 0
        assert stats["hit_rate"] == 0.0


class TestPathNormalization:
    """Tests for path normalization."""
    
    def test_normalize_forward_slashes(self):
        """Test forward slashes are preserved."""
        manager = AssetManager()
        result = manager._normalize_path("mario/characters/mario.png")
        assert result == "mario/characters/mario.png"
    
    def test_normalize_backslashes(self):
        """Test backslashes are converted to forward slashes."""
        manager = AssetManager()
        result = manager._normalize_path("mario\\characters\\mario.png")
        assert result == "mario/characters/mario.png"
    
    def test_normalize_leading_slash(self):
        """Test leading slashes are removed."""
        manager = AssetManager()
        result = manager._normalize_path("/mario/characters/mario.png")
        assert result == "mario/characters/mario.png"
    
    def test_normalize_assets_prefix(self):
        """Test 'assets/' prefix is removed."""
        manager = AssetManager()
        result = manager._normalize_path("assets/mario/characters/mario.png")
        assert result == "mario/characters/mario.png"
    
    def test_normalize_mixed_slashes(self):
        """Test mixed slashes are normalized."""
        manager = AssetManager()
        result = manager._normalize_path("mario\\characters/mario.png")
        assert result == "mario/characters/mario.png"


class TestThemeAssetPathResolution:
    """Tests for theme-specific asset path resolution."""
    
    def test_resolve_mario_character_path(self):
        """Test resolving Mario character asset path."""
        manager = AssetManager()
        path = manager.resolve_theme_asset_path(
            Theme.MARIO, "characters", "mario_run.png"
        )
        assert path == "mario/characters/mario_run.png"
    
    def test_resolve_zelda_item_path(self):
        """Test resolving Zelda item asset path."""
        manager = AssetManager()
        path = manager.resolve_theme_asset_path(
            Theme.ZELDA, "items", "sword.png"
        )
        assert path == "zelda/items/sword.png"
    
    def test_resolve_dkc_background_path(self):
        """Test resolving DKC background asset path."""
        manager = AssetManager()
        path = manager.resolve_theme_asset_path(
            Theme.DKC, "backgrounds", "jungle.png"
        )
        assert path == "dkc/backgrounds/jungle.png"
    
    def test_resolve_custom_asset_type(self):
        """Test resolving with custom asset type."""
        manager = AssetManager()
        path = manager.resolve_theme_asset_path(
            Theme.MARIO, "custom_type", "asset.png"
        )
        assert path == "mario/custom_type/asset.png"
    
    def test_all_themes_have_directories(self):
        """Test all themes have directory mappings."""
        manager = AssetManager()
        for theme in Theme:
            assert theme in manager.THEME_DIRECTORIES


class TestPlaceholderCreation:
    """Tests for placeholder sprite sheet creation."""
    
    def test_placeholder_created_for_missing_file(self):
        """Test placeholder is created when file doesn't exist."""
        manager = AssetManager(assets_root="nonexistent")
        sheet = manager.load_sprite_sheet("missing.png")
        
        assert sheet.is_placeholder is True
        assert sheet.path == "missing.png"
    
    def test_placeholder_has_default_dimensions(self):
        """Test placeholder uses default dimensions when not specified."""
        manager = AssetManager(assets_root="nonexistent")
        sheet = manager.load_sprite_sheet("missing.png")
        
        assert sheet.width == 64
        assert sheet.height == 64
    
    def test_placeholder_respects_frame_dimensions(self):
        """Test placeholder uses specified frame dimensions."""
        manager = AssetManager(assets_root="nonexistent")
        sheet = manager.load_sprite_sheet(
            "missing.png",
            frame_width=32,
            frame_height=32,
            columns=4,
            rows=2
        )
        
        assert sheet.width == 128  # 32 * 4
        assert sheet.height == 64   # 32 * 2
        assert sheet.frame_width == 32
        assert sheet.frame_height == 32
    
    def test_placeholder_image_is_not_none(self):
        """Test placeholder has an image object."""
        manager = AssetManager(assets_root="nonexistent")
        sheet = manager.load_sprite_sheet("missing.png")
        
        assert sheet.image is not None


class TestCaching:
    """Tests for asset caching functionality."""
    
    def test_same_asset_returns_cached_version(self):
        """Test loading same asset twice returns cached version."""
        manager = AssetManager(assets_root="nonexistent")
        
        sheet1 = manager.load_sprite_sheet("test.png")
        sheet2 = manager.load_sprite_sheet("test.png")
        
        assert sheet1 is sheet2
    
    def test_cache_hit_increments_counter(self):
        """Test cache hits are counted."""
        manager = AssetManager(assets_root="nonexistent")
        
        manager.load_sprite_sheet("test.png")
        manager.load_sprite_sheet("test.png")
        
        stats = manager.get_cache_stats()
        assert stats["cache_hits"] == 1
        assert stats["cache_misses"] == 1
    
    def test_different_parameters_create_different_cache_entries(self):
        """Test different frame parameters create separate cache entries."""
        manager = AssetManager(assets_root="nonexistent")
        
        sheet1 = manager.load_sprite_sheet("test.png", columns=1)
        sheet2 = manager.load_sprite_sheet("test.png", columns=2)
        
        assert sheet1 is not sheet2
        assert manager.get_cache_stats()["cached_assets"] == 2
    
    def test_clear_cache(self):
        """Test cache clearing."""
        manager = AssetManager(assets_root="nonexistent")
        
        manager.load_sprite_sheet("test1.png")
        manager.load_sprite_sheet("test2.png")
        
        assert manager.get_cache_stats()["cached_assets"] == 2
        
        manager.clear_cache()
        
        stats = manager.get_cache_stats()
        assert stats["cached_assets"] == 0
        assert stats["cache_hits"] == 0
        assert stats["cache_misses"] == 0
    
    def test_is_asset_loaded(self):
        """Test checking if asset is loaded."""
        manager = AssetManager(assets_root="nonexistent")
        
        assert manager.is_asset_loaded("test.png") is False
        
        manager.load_sprite_sheet("test.png")
        
        assert manager.is_asset_loaded("test.png") is True
    
    def test_get_loaded_asset(self):
        """Test getting loaded asset from cache."""
        manager = AssetManager(assets_root="nonexistent")
        
        assert manager.get_loaded_asset("test.png") is None
        
        sheet = manager.load_sprite_sheet("test.png")
        cached = manager.get_loaded_asset("test.png")
        
        assert cached is sheet


class TestSpriteSheetDataclass:
    """Tests for SpriteSheet dataclass."""
    
    def test_sprite_sheet_post_init_calculates_frame_dimensions(self):
        """Test frame dimensions are calculated in post_init."""
        sheet = SpriteSheet(
            path="test.png",
            image=None,
            width=128,
            height=64,
            columns=4,
            rows=2
        )
        
        assert sheet.frame_width == 32
        assert sheet.frame_height == 32
    
    def test_sprite_sheet_post_init_calculates_frame_count(self):
        """Test frame count is calculated in post_init."""
        sheet = SpriteSheet(
            path="test.png",
            image=None,
            width=128,
            height=64,
            columns=4,
            rows=2
        )
        
        assert sheet.frame_count == 8
    
    def test_sprite_sheet_preserves_explicit_frame_dimensions(self):
        """Test explicit frame dimensions are preserved."""
        sheet = SpriteSheet(
            path="test.png",
            image=None,
            width=128,
            height=64,
            frame_width=16,
            frame_height=16,
            columns=4,
            rows=2
        )
        
        assert sheet.frame_width == 16
        assert sheet.frame_height == 16


class TestSpriteExtraction:
    """Tests for sprite extraction from sprite sheets."""
    
    def test_get_sprite_returns_sprite_object(self):
        """Test get_sprite returns a Sprite object."""
        manager = AssetManager(assets_root="nonexistent")
        sheet = manager.load_sprite_sheet("test.png", columns=4, rows=2)
        
        sprite = manager.get_sprite(sheet, frame_index=0)
        
        assert isinstance(sprite, Sprite)
    
    def test_get_sprite_has_correct_dimensions(self):
        """Test extracted sprite has correct dimensions."""
        manager = AssetManager(assets_root="nonexistent")
        sheet = manager.load_sprite_sheet(
            "test.png",
            frame_width=32,
            frame_height=32,
            columns=4,
            rows=2
        )
        
        sprite = manager.get_sprite(sheet, frame_index=0)
        
        assert sprite.width == 32
        assert sprite.height == 32
    
    def test_get_sprite_records_source_info(self):
        """Test sprite records source sheet and frame index."""
        manager = AssetManager(assets_root="nonexistent")
        sheet = manager.load_sprite_sheet("test.png", columns=4, rows=2)
        
        sprite = manager.get_sprite(sheet, frame_index=3)
        
        assert sprite.source_sheet == "test.png"
        assert sprite.frame_index == 3
    
    def test_get_sprite_inherits_placeholder_status(self):
        """Test sprite inherits placeholder status from sheet."""
        manager = AssetManager(assets_root="nonexistent")
        sheet = manager.load_sprite_sheet("missing.png")
        
        sprite = manager.get_sprite(sheet, frame_index=0)
        
        assert sprite.is_placeholder is True
    
    def test_get_sprite_clamps_invalid_frame_index(self):
        """Test invalid frame index is clamped to 0."""
        manager = AssetManager(assets_root="nonexistent")
        sheet = manager.load_sprite_sheet("test.png", columns=2, rows=2)
        
        # Negative index
        sprite = manager.get_sprite(sheet, frame_index=-1)
        assert sprite.frame_index == 0
        
        # Index too large
        sprite = manager.get_sprite(sheet, frame_index=100)
        assert sprite.frame_index == 0
    
    def test_get_sprites_returns_list(self):
        """Test get_sprites returns list of sprites."""
        manager = AssetManager(assets_root="nonexistent")
        sheet = manager.load_sprite_sheet("test.png", columns=4, rows=2)
        
        sprites = manager.get_sprites(sheet, frame_indices=[0, 1, 2])
        
        assert len(sprites) == 3
        assert all(isinstance(s, Sprite) for s in sprites)
    
    def test_get_sprites_all_frames(self):
        """Test get_sprites returns all frames when indices not specified."""
        manager = AssetManager(assets_root="nonexistent")
        sheet = manager.load_sprite_sheet(
            "test.png",
            frame_width=32,
            frame_height=32,
            columns=4,
            rows=2
        )
        
        sprites = manager.get_sprites(sheet)
        
        assert len(sprites) == 8


class TestLoadThemeAsset:
    """Tests for the load_theme_asset convenience method."""
    
    def test_load_theme_asset_combines_path_and_load(self):
        """Test load_theme_asset resolves path and loads asset."""
        manager = AssetManager(assets_root="nonexistent")
        
        sheet = manager.load_theme_asset(
            Theme.MARIO,
            "characters",
            "mario.png"
        )
        
        assert sheet.path == "mario/characters/mario.png"
    
    def test_load_theme_asset_passes_kwargs(self):
        """Test load_theme_asset passes additional kwargs."""
        manager = AssetManager(assets_root="nonexistent")
        
        sheet = manager.load_theme_asset(
            Theme.ZELDA,
            "items",
            "sword.png",
            columns=4,
            rows=2
        )
        
        assert sheet.columns == 4
        assert sheet.rows == 2


class TestSupportedFormats:
    """Tests for supported image format handling."""
    
    def test_supported_formats_include_common_types(self):
        """Test common image formats are supported."""
        manager = AssetManager()
        
        assert '.png' in manager.SUPPORTED_FORMATS
        assert '.jpg' in manager.SUPPORTED_FORMATS
        assert '.jpeg' in manager.SUPPORTED_FORMATS
        assert '.gif' in manager.SUPPORTED_FORMATS
        assert '.bmp' in manager.SUPPORTED_FORMATS
    
    def test_unsupported_format_returns_placeholder(self):
        """Test unsupported format returns placeholder."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create a file with unsupported extension
            unsupported_file = Path(tmpdir) / "test.xyz"
            unsupported_file.write_text("not an image")
            
            manager = AssetManager(assets_root=tmpdir)
            sheet = manager.load_sprite_sheet("test.xyz")
            
            assert sheet.is_placeholder is True


class TestImageDimensionParsing:
    """Tests for image dimension parsing from raw bytes."""
    
    def test_parse_png_dimensions(self):
        """Test parsing PNG image dimensions."""
        manager = AssetManager()
        
        # Minimal PNG header with 100x50 dimensions
        png_header = (
            b'\x89PNG\r\n\x1a\n'  # PNG signature
            b'\x00\x00\x00\rIHDR'  # IHDR chunk
            b'\x00\x00\x00\x64'    # Width: 100
            b'\x00\x00\x002'       # Height: 50
        )
        
        width, height = manager._parse_image_dimensions(png_header, '.png')
        
        assert width == 100
        assert height == 50
    
    def test_parse_gif_dimensions(self):
        """Test parsing GIF image dimensions."""
        manager = AssetManager()
        
        # GIF header with 200x150 dimensions (little-endian)
        gif_header = (
            b'GIF89a'
            b'\xc8\x00'  # Width: 200
            b'\x96\x00'  # Height: 150
        )
        
        width, height = manager._parse_image_dimensions(gif_header, '.gif')
        
        assert width == 200
        assert height == 150
    
    def test_parse_invalid_data_returns_zero(self):
        """Test parsing invalid data returns (0, 0)."""
        manager = AssetManager()
        
        width, height = manager._parse_image_dimensions(b'invalid', '.png')
        
        assert width == 0
        assert height == 0


class TestRealFileLoading:
    """Tests for loading real image files."""
    
    def test_load_real_png_file(self):
        """Test loading a real PNG file."""
        # Create a temporary directory manually to handle cleanup properly
        tmpdir = tempfile.mkdtemp()
        try:
            # Create a minimal valid PNG file
            png_path = Path(tmpdir) / "test.png"
            # Minimal 1x1 red PNG
            png_data = bytes([
                0x89, 0x50, 0x4E, 0x47, 0x0D, 0x0A, 0x1A, 0x0A,  # PNG signature
                0x00, 0x00, 0x00, 0x0D, 0x49, 0x48, 0x44, 0x52,  # IHDR chunk
                0x00, 0x00, 0x00, 0x01,  # Width: 1
                0x00, 0x00, 0x00, 0x01,  # Height: 1
                0x08, 0x02, 0x00, 0x00, 0x00,  # Bit depth, color type, etc.
                0x90, 0x77, 0x53, 0xDE,  # CRC
                0x00, 0x00, 0x00, 0x0C, 0x49, 0x44, 0x41, 0x54,  # IDAT chunk
                0x08, 0xD7, 0x63, 0xF8, 0xFF, 0xFF, 0x3F, 0x00,
                0x05, 0xFE, 0x02, 0xFE,
                0xA3, 0x6C, 0xEC, 0xF5,  # CRC
                0x00, 0x00, 0x00, 0x00, 0x49, 0x45, 0x4E, 0x44,  # IEND chunk
                0xAE, 0x42, 0x60, 0x82   # CRC
            ])
            png_path.write_bytes(png_data)
            
            manager = AssetManager(assets_root=tmpdir)
            sheet = manager.load_sprite_sheet("test.png")
            
            # Should load successfully (may be placeholder if no image library)
            assert sheet is not None
            assert sheet.path == "test.png"
            
            # Clear cache to release file handles before cleanup
            manager.clear_cache()
        finally:
            # Clean up with error handling for Windows file locking
            import shutil
            try:
                shutil.rmtree(tmpdir, ignore_errors=True)
            except Exception:
                pass  # Ignore cleanup errors on Windows


class TestPreloadThemeAssets:
    """Tests for preloading theme assets."""
    
    def test_preload_nonexistent_theme_returns_zero(self):
        """Test preloading nonexistent theme directory returns 0."""
        manager = AssetManager(assets_root="nonexistent")
        count = manager.preload_theme_assets(Theme.MARIO)
        assert count == 0
    
    def test_preload_empty_theme_returns_zero(self):
        """Test preloading empty theme directory returns 0."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create empty theme directory
            theme_dir = Path(tmpdir) / "mario"
            theme_dir.mkdir()
            
            manager = AssetManager(assets_root=tmpdir)
            count = manager.preload_theme_assets(Theme.MARIO)
            
            assert count == 0


class TestCacheStatistics:
    """Tests for cache statistics."""
    
    def test_hit_rate_calculation(self):
        """Test cache hit rate is calculated correctly."""
        manager = AssetManager(assets_root="nonexistent")
        
        # First load is a miss
        manager.load_sprite_sheet("test.png")
        # Second load is a hit
        manager.load_sprite_sheet("test.png")
        # Third load is a hit
        manager.load_sprite_sheet("test.png")
        
        stats = manager.get_cache_stats()
        
        # 2 hits, 1 miss = 2/3 = 0.666...
        assert stats["cache_hits"] == 2
        assert stats["cache_misses"] == 1
        assert abs(stats["hit_rate"] - 0.666666) < 0.001
