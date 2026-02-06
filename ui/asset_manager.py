"""
AssetManager for NintendAnki.

This module implements the AssetManager class that handles loading,
caching, and managing sprite sheets and images for all game themes.

Requirements: 4.7, 9.2
"""

import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union

from data.models import Theme


# Configure logging
logger = logging.getLogger(__name__)


@dataclass
class SpriteSheet:
    """Represents a loaded sprite sheet.
    
    A sprite sheet is a single image containing multiple sprite frames
    arranged in a grid. This class stores the image data and metadata
    needed to extract individual frames.
    
    Attributes:
        path: Original path to the sprite sheet file
        image: The loaded image data (format depends on backend)
        width: Total width of the sprite sheet in pixels
        height: Total height of the sprite sheet in pixels
        frame_width: Width of each frame in pixels
        frame_height: Height of each frame in pixels
        columns: Number of columns in the sprite sheet
        rows: Number of rows in the sprite sheet
        frame_count: Total number of frames in the sprite sheet
        is_placeholder: True if this is a placeholder sprite sheet
    """
    path: str
    image: object  # Can be QPixmap, PIL.Image, or bytes depending on backend
    width: int
    height: int
    frame_width: int = 0
    frame_height: int = 0
    columns: int = 1
    rows: int = 1
    frame_count: int = 1
    is_placeholder: bool = False
    
    def __post_init__(self):
        """Calculate frame dimensions if not provided."""
        if self.frame_width == 0:
            self.frame_width = self.width // self.columns if self.columns > 0 else self.width
        if self.frame_height == 0:
            self.frame_height = self.height // self.rows if self.rows > 0 else self.height
        if self.frame_count == 1 and (self.columns > 1 or self.rows > 1):
            self.frame_count = self.columns * self.rows


@dataclass
class Sprite:
    """Represents a single sprite frame extracted from a sprite sheet.
    
    Attributes:
        image: The sprite image data
        width: Width of the sprite in pixels
        height: Height of the sprite in pixels
        source_sheet: Path to the source sprite sheet
        frame_index: Index of this frame in the source sheet
        is_placeholder: True if this is a placeholder sprite
    """
    image: object
    width: int
    height: int
    source_sheet: str = ""
    frame_index: int = 0
    is_placeholder: bool = False


class AssetManager:
    """Manages loading, caching, and retrieval of game assets.
    
    The AssetManager provides a centralized interface for loading and
    caching sprite sheets and images for all game themes. It handles:
    - Sprite sheet loading with automatic caching
    - Asset path resolution for each theme (mario, zelda, dkc)
    - Graceful handling of missing assets with placeholders
    - Support for common image formats (PNG, JPG, GIF, BMP)
    
    Requirements: 4.7, 9.2
    
    Attributes:
        assets_root: Root directory for all assets
        _cache: Dictionary mapping asset paths to loaded SpriteSheet objects
        _placeholder_cache: Cache for placeholder images by size
    
    Example:
        >>> asset_manager = AssetManager()
        >>> sheet = asset_manager.load_sprite_sheet("mario/characters/mario_run.png")
        >>> sprite = asset_manager.get_sprite(sheet, frame_index=0)
    """
    
    # Supported image formats
    SUPPORTED_FORMATS = {'.png', '.jpg', '.jpeg', '.gif', '.bmp'}
    
    # Default placeholder dimensions
    DEFAULT_PLACEHOLDER_SIZE = (64, 64)
    
    # Theme asset subdirectories
    THEME_DIRECTORIES = {
        Theme.MARIO: "mario",
        Theme.ZELDA: "zelda",
        Theme.DKC: "dkc",
    }
    
    # Common asset subdirectories within each theme
    ASSET_SUBDIRS = {
        "characters": "characters",
        "items": "items",
        "backgrounds": "backgrounds",
        "enemies": "enemies",
        "ui": "ui",
        "effects": "effects",
    }
    
    def __init__(self, assets_root: Optional[Union[str, Path]] = None):
        """Initialize the AssetManager.
        
        Args:
            assets_root: Root directory for assets. Defaults to 'assets' in
                        the current working directory.
        """
        if assets_root is None:
            self.assets_root = Path("assets")
        else:
            self.assets_root = Path(assets_root)
        
        # Cache for loaded sprite sheets (path -> SpriteSheet)
        self._cache: Dict[str, SpriteSheet] = {}
        
        # Cache for placeholder images ((width, height) -> image)
        self._placeholder_cache: Dict[Tuple[int, int], object] = {}
        
        # Statistics for debugging
        self._cache_hits = 0
        self._cache_misses = 0
        
        logger.debug(f"AssetManager initialized with root: {self.assets_root}")
    
    def load_sprite_sheet(
        self,
        path: str,
        frame_width: int = 0,
        frame_height: int = 0,
        columns: int = 1,
        rows: int = 1
    ) -> SpriteSheet:
        """Load a sprite sheet from file.
        
        Loads a sprite sheet image and caches it for future use. If the
        file doesn't exist or can't be loaded, returns a placeholder
        sprite sheet.
        
        Args:
            path: Path to the sprite sheet file (relative to assets_root
                  or absolute)
            frame_width: Width of each frame in pixels (0 = auto-calculate)
            frame_height: Height of each frame in pixels (0 = auto-calculate)
            columns: Number of columns in the sprite sheet
            rows: Number of rows in the sprite sheet
        
        Returns:
            SpriteSheet object containing the loaded image and metadata
        
        Requirements: 4.7, 9.2
        """
        # Normalize the path
        normalized_path = self._normalize_path(path)
        cache_key = f"{normalized_path}:{frame_width}:{frame_height}:{columns}:{rows}"
        
        # Check cache first
        if cache_key in self._cache:
            self._cache_hits += 1
            logger.debug(f"Cache hit for: {normalized_path}")
            return self._cache[cache_key]
        
        self._cache_misses += 1
        logger.debug(f"Cache miss for: {normalized_path}")
        
        # Resolve the full path
        full_path = self._resolve_asset_path(normalized_path)
        
        # Try to load the image
        sprite_sheet = self._load_image(
            full_path,
            normalized_path,
            frame_width,
            frame_height,
            columns,
            rows
        )
        
        # Cache the result
        self._cache[cache_key] = sprite_sheet
        
        return sprite_sheet
    
    def _load_image(
        self,
        full_path: Path,
        original_path: str,
        frame_width: int,
        frame_height: int,
        columns: int,
        rows: int
    ) -> SpriteSheet:
        """Load an image file and create a SpriteSheet.
        
        Args:
            full_path: Full path to the image file
            original_path: Original path string for reference
            frame_width: Width of each frame
            frame_height: Height of each frame
            columns: Number of columns
            rows: Number of rows
        
        Returns:
            SpriteSheet with loaded image or placeholder
        """
        # Check if file exists and has supported format
        if not full_path.exists():
            logger.warning(f"Asset not found: {full_path}")
            return self._create_placeholder_sprite_sheet(
                original_path, frame_width, frame_height, columns, rows
            )
        
        suffix = full_path.suffix.lower()
        if suffix not in self.SUPPORTED_FORMATS:
            logger.warning(f"Unsupported format: {suffix} for {full_path}")
            return self._create_placeholder_sprite_sheet(
                original_path, frame_width, frame_height, columns, rows
            )
        
        # Try to load with available backends
        image_data, width, height = self._load_with_backend(full_path)
        
        if image_data is None:
            logger.warning(f"Failed to load image: {full_path}")
            return self._create_placeholder_sprite_sheet(
                original_path, frame_width, frame_height, columns, rows
            )
        
        logger.debug(f"Loaded sprite sheet: {full_path} ({width}x{height})")
        
        return SpriteSheet(
            path=original_path,
            image=image_data,
            width=width,
            height=height,
            frame_width=frame_width,
            frame_height=frame_height,
            columns=columns,
            rows=rows,
            is_placeholder=False
        )
    
    def _load_with_backend(self, path: Path) -> Tuple[Optional[object], int, int]:
        """Load an image using available backends.
        
        Tries to load the image using PyQt first, then PIL, then raw bytes.
        
        Args:
            path: Path to the image file
        
        Returns:
            Tuple of (image_data, width, height) or (None, 0, 0) on failure
        """
        # Try PyQt backend first (preferred for Anki add-on)
        try:
            from PyQt6.QtGui import QPixmap
            pixmap = QPixmap(str(path))
            if not pixmap.isNull():
                return pixmap, pixmap.width(), pixmap.height()
        except ImportError:
            pass
        except Exception as e:
            logger.debug(f"PyQt6 load failed: {e}")
        
        # Try PyQt5 as fallback
        try:
            from PyQt5.QtGui import QPixmap
            pixmap = QPixmap(str(path))
            if not pixmap.isNull():
                return pixmap, pixmap.width(), pixmap.height()
        except ImportError:
            pass
        except Exception as e:
            logger.debug(f"PyQt5 load failed: {e}")
        
        # Try PIL/Pillow backend
        try:
            from PIL import Image
            img = Image.open(path)
            width, height = img.size
            return img, width, height
        except ImportError:
            pass
        except Exception as e:
            logger.debug(f"PIL load failed: {e}")
        
        # Fallback: load as raw bytes with basic PNG/JPEG header parsing
        try:
            with open(path, 'rb') as f:
                data = f.read()
            width, height = self._parse_image_dimensions(data, path.suffix.lower())
            if width > 0 and height > 0:
                return data, width, height
        except Exception as e:
            logger.debug(f"Raw bytes load failed: {e}")
        
        return None, 0, 0
    
    def _parse_image_dimensions(self, data: bytes, suffix: str) -> Tuple[int, int]:
        """Parse image dimensions from raw bytes.
        
        Args:
            data: Raw image bytes
            suffix: File extension (e.g., '.png')
        
        Returns:
            Tuple of (width, height) or (0, 0) if parsing fails
        """
        try:
            if suffix == '.png':
                # PNG header: width at bytes 16-19, height at bytes 20-23
                if data[:8] == b'\x89PNG\r\n\x1a\n':
                    width = int.from_bytes(data[16:20], 'big')
                    height = int.from_bytes(data[20:24], 'big')
                    return width, height
            
            elif suffix in ('.jpg', '.jpeg'):
                # JPEG: search for SOF0 marker (0xFF 0xC0)
                i = 0
                while i < len(data) - 9:
                    if data[i] == 0xFF:
                        marker = data[i + 1]
                        if marker == 0xC0 or marker == 0xC2:
                            height = int.from_bytes(data[i + 5:i + 7], 'big')
                            width = int.from_bytes(data[i + 7:i + 9], 'big')
                            return width, height
                        elif marker == 0xD8 or marker == 0xD9:
                            i += 2
                        elif marker == 0x00:
                            i += 1
                        else:
                            length = int.from_bytes(data[i + 2:i + 4], 'big')
                            i += 2 + length
                    else:
                        i += 1
            
            elif suffix == '.gif':
                # GIF header: width at bytes 6-7, height at bytes 8-9
                if data[:6] in (b'GIF87a', b'GIF89a'):
                    width = int.from_bytes(data[6:8], 'little')
                    height = int.from_bytes(data[8:10], 'little')
                    return width, height
            
            elif suffix == '.bmp':
                # BMP header: width at bytes 18-21, height at bytes 22-25
                if data[:2] == b'BM':
                    width = int.from_bytes(data[18:22], 'little')
                    height = abs(int.from_bytes(data[22:26], 'little', signed=True))
                    return width, height
        
        except Exception as e:
            logger.debug(f"Failed to parse image dimensions: {e}")
        
        return 0, 0
    
    def _create_placeholder_sprite_sheet(
        self,
        path: str,
        frame_width: int = 0,
        frame_height: int = 0,
        columns: int = 1,
        rows: int = 1
    ) -> SpriteSheet:
        """Create a placeholder sprite sheet for missing assets.
        
        Creates a simple colored rectangle as a placeholder when the
        requested asset cannot be loaded.
        
        Args:
            path: Original path (for reference)
            frame_width: Requested frame width
            frame_height: Requested frame height
            columns: Number of columns
            rows: Number of rows
        
        Returns:
            SpriteSheet with placeholder image
        """
        # Determine placeholder size
        if frame_width > 0 and frame_height > 0:
            width = frame_width * columns
            height = frame_height * rows
        else:
            width, height = self.DEFAULT_PLACEHOLDER_SIZE
            frame_width = width // columns if columns > 0 else width
            frame_height = height // rows if rows > 0 else height
        
        # Get or create placeholder image
        placeholder_image = self._get_placeholder_image(width, height)
        
        logger.info(f"Created placeholder for: {path} ({width}x{height})")
        
        return SpriteSheet(
            path=path,
            image=placeholder_image,
            width=width,
            height=height,
            frame_width=frame_width,
            frame_height=frame_height,
            columns=columns,
            rows=rows,
            is_placeholder=True
        )
    
    def _get_placeholder_image(self, width: int, height: int) -> object:
        """Get or create a placeholder image of the specified size.
        
        Args:
            width: Width in pixels
            height: Height in pixels
        
        Returns:
            Placeholder image object
        """
        cache_key = (width, height)
        
        if cache_key in self._placeholder_cache:
            return self._placeholder_cache[cache_key]
        
        # Try to create with PyQt
        placeholder = self._create_pyqt_placeholder(width, height)
        
        if placeholder is None:
            # Try PIL
            placeholder = self._create_pil_placeholder(width, height)
        
        if placeholder is None:
            # Fallback to raw bytes (simple magenta PNG)
            placeholder = self._create_raw_placeholder(width, height)
        
        self._placeholder_cache[cache_key] = placeholder
        return placeholder
    
    def _create_pyqt_placeholder(self, width: int, height: int) -> Optional[object]:
        """Create a placeholder using PyQt.
        
        Args:
            width: Width in pixels
            height: Height in pixels
        
        Returns:
            QPixmap placeholder or None
        """
        try:
            from PyQt6.QtGui import QPixmap, QPainter, QColor, QFont
            from PyQt6.QtCore import Qt
            
            pixmap = QPixmap(width, height)
            pixmap.fill(QColor(255, 0, 255, 128))  # Semi-transparent magenta
            
            painter = QPainter(pixmap)
            painter.setPen(QColor(0, 0, 0))
            painter.setFont(QFont("Arial", min(width, height) // 4))
            painter.drawText(pixmap.rect(), Qt.AlignmentFlag.AlignCenter, "?")
            painter.end()
            
            return pixmap
        except ImportError:
            pass
        except Exception as e:
            logger.debug(f"PyQt6 placeholder creation failed: {e}")
        
        try:
            from PyQt5.QtGui import QPixmap, QPainter, QColor, QFont
            from PyQt5.QtCore import Qt
            
            pixmap = QPixmap(width, height)
            pixmap.fill(QColor(255, 0, 255, 128))
            
            painter = QPainter(pixmap)
            painter.setPen(QColor(0, 0, 0))
            painter.setFont(QFont("Arial", min(width, height) // 4))
            painter.drawText(pixmap.rect(), Qt.AlignCenter, "?")
            painter.end()
            
            return pixmap
        except ImportError:
            pass
        except Exception as e:
            logger.debug(f"PyQt5 placeholder creation failed: {e}")
        
        return None
    
    def _create_pil_placeholder(self, width: int, height: int) -> Optional[object]:
        """Create a placeholder using PIL.
        
        Args:
            width: Width in pixels
            height: Height in pixels
        
        Returns:
            PIL Image placeholder or None
        """
        try:
            from PIL import Image, ImageDraw
            
            img = Image.new('RGBA', (width, height), (255, 0, 255, 128))
            draw = ImageDraw.Draw(img)
            
            # Draw a question mark or X pattern
            draw.line([(0, 0), (width, height)], fill=(0, 0, 0, 255), width=2)
            draw.line([(width, 0), (0, height)], fill=(0, 0, 0, 255), width=2)
            
            return img
        except ImportError:
            pass
        except Exception as e:
            logger.debug(f"PIL placeholder creation failed: {e}")
        
        return None
    
    def _create_raw_placeholder(self, width: int, height: int) -> bytes:
        """Create a simple raw bytes placeholder.
        
        Creates a minimal representation for when no image library is available.
        
        Args:
            width: Width in pixels
            height: Height in pixels
        
        Returns:
            Bytes representing placeholder data
        """
        # Return a simple data structure with dimensions
        return bytes([
            0x50, 0x4C, 0x41, 0x43,  # "PLAC" magic bytes
            (width >> 8) & 0xFF, width & 0xFF,
            (height >> 8) & 0xFF, height & 0xFF,
            0xFF, 0x00, 0xFF, 0x80  # RGBA magenta semi-transparent
        ])
    
    def get_sprite(
        self,
        sprite_sheet: SpriteSheet,
        frame_index: int = 0
    ) -> Sprite:
        """Extract a single sprite frame from a sprite sheet.
        
        Args:
            sprite_sheet: The sprite sheet to extract from
            frame_index: Index of the frame to extract (0-based)
        
        Returns:
            Sprite object containing the extracted frame
        """
        if frame_index < 0 or frame_index >= sprite_sheet.frame_count:
            logger.warning(
                f"Frame index {frame_index} out of range for {sprite_sheet.path} "
                f"(max: {sprite_sheet.frame_count - 1})"
            )
            frame_index = 0
        
        # Calculate frame position
        col = frame_index % sprite_sheet.columns
        row = frame_index // sprite_sheet.columns
        
        x = col * sprite_sheet.frame_width
        y = row * sprite_sheet.frame_height
        
        # Extract the frame based on image type
        frame_image = self._extract_frame(
            sprite_sheet.image,
            x, y,
            sprite_sheet.frame_width,
            sprite_sheet.frame_height
        )
        
        return Sprite(
            image=frame_image,
            width=sprite_sheet.frame_width,
            height=sprite_sheet.frame_height,
            source_sheet=sprite_sheet.path,
            frame_index=frame_index,
            is_placeholder=sprite_sheet.is_placeholder
        )
    
    def _extract_frame(
        self,
        image: object,
        x: int,
        y: int,
        width: int,
        height: int
    ) -> object:
        """Extract a rectangular region from an image.
        
        Args:
            image: Source image
            x: X coordinate of top-left corner
            y: Y coordinate of top-left corner
            width: Width of region
            height: Height of region
        
        Returns:
            Extracted image region
        """
        # Try PyQt extraction
        try:
            from PyQt6.QtGui import QPixmap
            if isinstance(image, QPixmap):
                return image.copy(x, y, width, height)
        except ImportError:
            pass
        
        try:
            from PyQt5.QtGui import QPixmap
            if isinstance(image, QPixmap):
                return image.copy(x, y, width, height)
        except ImportError:
            pass
        
        # Try PIL extraction
        try:
            from PIL import Image
            if isinstance(image, Image.Image):
                return image.crop((x, y, x + width, y + height))
        except ImportError:
            pass
        
        # For raw bytes or unknown types, return the whole image
        return image
    
    def get_sprites(
        self,
        sprite_sheet: SpriteSheet,
        frame_indices: Optional[List[int]] = None
    ) -> List[Sprite]:
        """Extract multiple sprite frames from a sprite sheet.
        
        Args:
            sprite_sheet: The sprite sheet to extract from
            frame_indices: List of frame indices to extract. If None,
                          extracts all frames.
        
        Returns:
            List of Sprite objects
        """
        if frame_indices is None:
            frame_indices = list(range(sprite_sheet.frame_count))
        
        return [self.get_sprite(sprite_sheet, idx) for idx in frame_indices]
    
    def resolve_theme_asset_path(
        self,
        theme: Theme,
        asset_type: str,
        asset_name: str
    ) -> str:
        """Resolve the path to a theme-specific asset.
        
        Constructs the full path to an asset based on theme and type.
        
        Args:
            theme: The game theme (MARIO, ZELDA, DKC)
            asset_type: Type of asset (characters, items, backgrounds, etc.)
            asset_name: Name of the asset file
        
        Returns:
            Resolved asset path relative to assets_root
        
        Example:
            >>> path = asset_manager.resolve_theme_asset_path(
            ...     Theme.MARIO, "characters", "mario_run.png"
            ... )
            >>> print(path)  # "mario/characters/mario_run.png"
        """
        theme_dir = self.THEME_DIRECTORIES.get(theme, theme.value)
        asset_subdir = self.ASSET_SUBDIRS.get(asset_type, asset_type)
        
        return f"{theme_dir}/{asset_subdir}/{asset_name}"
    
    def load_theme_asset(
        self,
        theme: Theme,
        asset_type: str,
        asset_name: str,
        **kwargs
    ) -> SpriteSheet:
        """Load a theme-specific asset.
        
        Convenience method that combines path resolution and loading.
        
        Args:
            theme: The game theme
            asset_type: Type of asset
            asset_name: Name of the asset file
            **kwargs: Additional arguments passed to load_sprite_sheet
        
        Returns:
            Loaded SpriteSheet
        """
        path = self.resolve_theme_asset_path(theme, asset_type, asset_name)
        return self.load_sprite_sheet(path, **kwargs)
    
    def _normalize_path(self, path: str) -> str:
        """Normalize an asset path.
        
        Converts backslashes to forward slashes and removes leading slashes.
        
        Args:
            path: Path to normalize
        
        Returns:
            Normalized path string
        """
        # Convert backslashes to forward slashes
        normalized = path.replace('\\', '/')
        
        # Remove leading slashes
        normalized = normalized.lstrip('/')
        
        # Remove 'assets/' prefix if present (will be added by resolve)
        if normalized.startswith('assets/'):
            normalized = normalized[7:]
        
        return normalized
    
    def _resolve_asset_path(self, path: str) -> Path:
        """Resolve a relative asset path to an absolute path.
        
        Args:
            path: Relative path within assets directory
        
        Returns:
            Absolute Path object
        """
        # Check if it's already an absolute path
        path_obj = Path(path)
        if path_obj.is_absolute():
            return path_obj
        
        # Resolve relative to assets_root
        return self.assets_root / path
    
    def preload_theme_assets(self, theme: Theme) -> int:
        """Preload all assets for a specific theme.
        
        Loads all assets for a theme into the cache for faster access
        during gameplay.
        
        Args:
            theme: The theme to preload assets for
        
        Returns:
            Number of assets loaded
        """
        theme_dir = self.THEME_DIRECTORIES.get(theme, theme.value)
        theme_path = self.assets_root / theme_dir
        
        if not theme_path.exists():
            logger.warning(f"Theme directory not found: {theme_path}")
            return 0
        
        count = 0
        for asset_file in theme_path.rglob('*'):
            if asset_file.is_file() and asset_file.suffix.lower() in self.SUPPORTED_FORMATS:
                relative_path = str(asset_file.relative_to(self.assets_root))
                self.load_sprite_sheet(relative_path)
                count += 1
        
        logger.info(f"Preloaded {count} assets for theme: {theme.value}")
        return count
    
    def clear_cache(self) -> None:
        """Clear all cached assets.
        
        Useful for freeing memory or forcing assets to be reloaded.
        """
        self._cache.clear()
        self._placeholder_cache.clear()
        self._cache_hits = 0
        self._cache_misses = 0
        logger.debug("Asset cache cleared")
    
    def get_cache_stats(self) -> Dict[str, int]:
        """Get cache statistics.
        
        Returns:
            Dictionary with cache statistics
        """
        return {
            "cached_assets": len(self._cache),
            "cached_placeholders": len(self._placeholder_cache),
            "cache_hits": self._cache_hits,
            "cache_misses": self._cache_misses,
            "hit_rate": (
                self._cache_hits / (self._cache_hits + self._cache_misses)
                if (self._cache_hits + self._cache_misses) > 0
                else 0.0
            )
        }
    
    def is_asset_loaded(self, path: str) -> bool:
        """Check if an asset is already loaded in the cache.
        
        Args:
            path: Path to the asset
        
        Returns:
            True if the asset is cached
        """
        normalized = self._normalize_path(path)
        # Check with default parameters
        cache_key = f"{normalized}:0:0:1:1"
        return cache_key in self._cache
    
    def get_loaded_asset(self, path: str) -> Optional[SpriteSheet]:
        """Get a loaded asset from cache without loading it.
        
        Args:
            path: Path to the asset
        
        Returns:
            Cached SpriteSheet or None if not loaded
        """
        normalized = self._normalize_path(path)
        cache_key = f"{normalized}:0:0:1:1"
        return self._cache.get(cache_key)
