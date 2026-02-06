"""
Script to create placeholder sprites for the DKC (Donkey Kong Country) theme.

This script generates simple colored shapes as placeholder sprites for:
- Character sprites (idle, run, collect, damage)
- Collectible sprites (banana, barrel, etc.)
- Jungle background tiles
- UI elements (banana counter, timer, etc.)
- Enemy sprites

Requirements: 6.1
"""

from pathlib import Path
from PIL import Image, ImageDraw
import math


def create_directory_structure(base_path: Path) -> None:
    """Create the directory structure for DKC assets."""
    directories = [
        base_path / "characters",
        base_path / "items",
        base_path / "backgrounds",
        base_path / "ui",
        base_path / "enemies",
    ]
    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)
    print(f"Created directory structure at {base_path}")


def create_dk_sprite(
    width: int,
    height: int,
    state: str
) -> Image.Image:
    """Create a Donkey Kong character sprite placeholder.
    
    Args:
        width: Width of the sprite
        height: Height of the sprite
        state: Animation state (idle, run, collect, damage)
    
    Returns:
        PIL Image with the character sprite
    """
    img = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # DK's colors
    fur_color = (139, 90, 43, 255)  # Brown fur
    belly_color = (210, 180, 140, 255)  # Tan belly
    face_color = (210, 180, 140, 255)  # Tan face
    
    # Draw body (large oval for gorilla body)
    body_top = height // 4
    body_bottom = height - height // 8
    body_left = width // 6
    body_right = width - width // 6
    draw.ellipse([body_left, body_top, body_right, body_bottom], fill=fur_color)
    
    # Draw belly (lighter oval)
    belly_margin = width // 8
    draw.ellipse([
        body_left + belly_margin,
        body_top + height // 8,
        body_right - belly_margin,
        body_bottom - height // 10
    ], fill=belly_color)
    
    # Draw head (circle)
    head_radius = width // 4
    head_center = (width // 2, body_top - head_radius // 3)
    draw.ellipse([
        head_center[0] - head_radius,
        head_center[1] - head_radius,
        head_center[0] + head_radius,
        head_center[1] + head_radius
    ], fill=fur_color)
    
    # Draw face (lighter area)
    face_radius = head_radius * 2 // 3
    draw.ellipse([
        head_center[0] - face_radius,
        head_center[1] - face_radius // 2,
        head_center[0] + face_radius,
        head_center[1] + face_radius
    ], fill=face_color)
    
    # Draw DK's signature red tie
    tie_top = body_top + height // 10
    tie_width = width // 6
    tie_center = width // 2
    draw.polygon([
        (tie_center, tie_top),
        (tie_center - tie_width // 2, tie_top + height // 8),
        (tie_center, tie_top + height // 3),
        (tie_center + tie_width // 2, tie_top + height // 8),
    ], fill=(255, 0, 0, 255))
    # DK letters on tie
    draw.text((tie_center - 6, tie_top + height // 12), "DK", fill=(255, 255, 0, 255))
    
    # Add state-specific details
    if state == "run":
        # Add motion lines
        draw.line([(body_left - 5, body_top + 10), (body_left - 15, body_top + 10)], fill=(200, 200, 200, 200), width=2)
        draw.line([(body_left - 5, body_top + 25), (body_left - 12, body_top + 25)], fill=(200, 200, 200, 200), width=2)
        draw.line([(body_left - 5, body_top + 40), (body_left - 10, body_top + 40)], fill=(200, 200, 200, 200), width=2)
        # Arms in running position
        draw.ellipse([body_left - 8, body_top + 5, body_left + 5, body_top + 20], fill=fur_color)
        draw.ellipse([body_right - 5, body_top + 15, body_right + 8, body_top + 30], fill=fur_color)
    elif state == "collect":
        # Arms reaching up (collecting bananas)
        draw.line([(body_left + 5, body_top + 5), (body_left - 10, body_top - 15)], fill=fur_color, width=6)
        draw.line([(body_right - 5, body_top + 5), (body_right + 10, body_top - 15)], fill=fur_color, width=6)
        # Happy expression - big smile
        smile_y = head_center[1] + face_radius // 2
        draw.arc([
            head_center[0] - face_radius // 2,
            smile_y - 5,
            head_center[0] + face_radius // 2,
            smile_y + 5
        ], 0, 180, fill=(0, 0, 0, 255), width=2)
    elif state == "damage":
        # Add red tint/flash effect
        overlay = Image.new('RGBA', (width, height), (255, 0, 0, 80))
        img = Image.alpha_composite(img, overlay)
        draw = ImageDraw.Draw(img)
        # Add X eyes
        eye_y = head_center[1] - 2
        draw.line([(head_center[0] - 10, eye_y - 3), (head_center[0] - 4, eye_y + 3)], fill=(0, 0, 0, 255), width=2)
        draw.line([(head_center[0] - 10, eye_y + 3), (head_center[0] - 4, eye_y - 3)], fill=(0, 0, 0, 255), width=2)
        draw.line([(head_center[0] + 4, eye_y - 3), (head_center[0] + 10, eye_y + 3)], fill=(0, 0, 0, 255), width=2)
        draw.line([(head_center[0] + 4, eye_y + 3), (head_center[0] + 10, eye_y - 3)], fill=(0, 0, 0, 255), width=2)
    else:  # idle
        # Draw simple eyes
        eye_y = head_center[1] - 2
        draw.ellipse([head_center[0] - 10, eye_y - 3, head_center[0] - 4, eye_y + 3], fill=(0, 0, 0, 255))
        draw.ellipse([head_center[0] + 4, eye_y - 3, head_center[0] + 10, eye_y + 3], fill=(0, 0, 0, 255))
        # Neutral mouth
        draw.line([
            (head_center[0] - face_radius // 3, head_center[1] + face_radius // 3),
            (head_center[0] + face_radius // 3, head_center[1] + face_radius // 3)
        ], fill=(0, 0, 0, 255), width=2)
    
    return img


def create_banana_sprite(size: int) -> Image.Image:
    """Create a banana collectible sprite placeholder.
    
    Args:
        size: Size of the sprite (width and height)
    
    Returns:
        PIL Image with the banana sprite
    """
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Banana yellow color
    banana_color = (255, 225, 53, 255)
    banana_dark = (200, 170, 30, 255)
    
    # Draw curved banana shape using arc and polygon
    center_x = size // 2
    center_y = size // 2
    
    # Create banana curve points
    banana_points = []
    for i in range(20):
        t = i / 19
        # Parametric curve for banana shape
        angle = math.pi * 0.3 + t * math.pi * 0.4
        radius = size // 3 + math.sin(t * math.pi) * size // 8
        x = center_x + radius * math.cos(angle)
        y = center_y - radius * math.sin(angle) + size // 6
        banana_points.append((x, y))
    
    # Add thickness to banana
    thick_points = []
    for i in range(20):
        t = i / 19
        angle = math.pi * 0.3 + t * math.pi * 0.4
        radius = size // 3 + math.sin(t * math.pi) * size // 8 - size // 10
        x = center_x + radius * math.cos(angle)
        y = center_y - radius * math.sin(angle) + size // 6
        thick_points.append((x, y))
    
    # Combine points for filled polygon
    all_points = banana_points + list(reversed(thick_points))
    draw.polygon(all_points, fill=banana_color, outline=banana_dark)
    
    # Add stem
    stem_x = banana_points[0][0]
    stem_y = banana_points[0][1]
    draw.rectangle([stem_x - 2, stem_y - 4, stem_x + 2, stem_y], fill=(101, 67, 33, 255))
    
    # Add shine
    shine_idx = len(banana_points) // 3
    shine_x = (banana_points[shine_idx][0] + thick_points[shine_idx][0]) // 2
    shine_y = (banana_points[shine_idx][1] + thick_points[shine_idx][1]) // 2
    draw.ellipse([shine_x - 2, shine_y - 2, shine_x + 2, shine_y + 2], fill=(255, 255, 200, 255))
    
    return img


def create_banana_bunch_sprite(size: int) -> Image.Image:
    """Create a banana bunch collectible sprite placeholder.
    
    Args:
        size: Size of the sprite (width and height)
    
    Returns:
        PIL Image with the banana bunch sprite
    """
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    banana_color = (255, 225, 53, 255)
    banana_dark = (200, 170, 30, 255)
    
    # Draw multiple bananas in a bunch
    offsets = [(-size // 6, 0), (0, -size // 8), (size // 6, 0)]
    
    for ox, oy in offsets:
        # Simple banana shape for bunch
        center_x = size // 2 + ox
        center_y = size // 2 + oy
        
        # Draw curved banana
        draw.arc([
            center_x - size // 4,
            center_y - size // 4,
            center_x + size // 4,
            center_y + size // 4
        ], 200, 340, fill=banana_color, width=size // 8)
    
    # Draw connecting stem
    draw.ellipse([
        size // 2 - size // 10,
        size // 4 - size // 10,
        size // 2 + size // 10,
        size // 4 + size // 10
    ], fill=(101, 67, 33, 255))
    
    return img


def create_barrel_sprite(size: int, barrel_type: str = "normal") -> Image.Image:
    """Create a barrel sprite placeholder.
    
    Args:
        size: Size of the sprite (width and height)
        barrel_type: Type of barrel (normal, dk_barrel, tnt)
    
    Returns:
        PIL Image with the barrel sprite
    """
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    center_x = size // 2
    center_y = size // 2
    
    if barrel_type == "tnt":
        # Red TNT barrel
        barrel_color = (200, 50, 50, 255)
        band_color = (150, 30, 30, 255)
    elif barrel_type == "dk_barrel":
        # DK barrel (blue with DK logo)
        barrel_color = (70, 130, 180, 255)
        band_color = (50, 100, 150, 255)
    else:
        # Normal brown barrel
        barrel_color = (139, 90, 43, 255)
        band_color = (100, 60, 30, 255)
    
    # Draw barrel body (oval)
    margin = size // 8
    draw.ellipse([margin, margin, size - margin, size - margin], fill=barrel_color)
    
    # Draw barrel bands (horizontal lines)
    band_positions = [size // 4, size // 2, size * 3 // 4]
    for band_y in band_positions:
        draw.line([(margin + 2, band_y), (size - margin - 2, band_y)], fill=band_color, width=3)
    
    # Draw vertical wood grain lines
    for i in range(3):
        x = margin + (size - 2 * margin) * (i + 1) // 4
        draw.line([(x, margin + 5), (x, size - margin - 5)], fill=band_color, width=1)
    
    # Add type-specific details
    if barrel_type == "tnt":
        # TNT text
        draw.text((center_x - 10, center_y - 5), "TNT", fill=(255, 255, 255, 255))
    elif barrel_type == "dk_barrel":
        # DK logo
        draw.text((center_x - 8, center_y - 5), "DK", fill=(255, 255, 0, 255))
    
    # Add highlight
    draw.arc([margin + 2, margin + 2, size // 2, size // 2], 120, 200, fill=(255, 255, 255, 100), width=2)
    
    return img


def create_kong_letter_sprite(size: int, letter: str) -> Image.Image:
    """Create a KONG letter collectible sprite placeholder.
    
    Args:
        size: Size of the sprite (width and height)
        letter: The letter (K, O, N, or G)
    
    Returns:
        PIL Image with the KONG letter sprite
    """
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Golden background circle
    margin = size // 8
    draw.ellipse([margin, margin, size - margin, size - margin], fill=(255, 215, 0, 255))
    draw.ellipse([margin + 2, margin + 2, size - margin - 2, size - margin - 2], fill=(255, 235, 100, 255))
    
    # Draw the letter
    center_x = size // 2
    center_y = size // 2
    
    # Red letter with black outline
    letter_color = (200, 0, 0, 255)
    draw.text((center_x - 6, center_y - 8), letter, fill=(0, 0, 0, 255))
    draw.text((center_x - 7, center_y - 9), letter, fill=letter_color)
    
    # Add shine
    draw.ellipse([margin + 5, margin + 5, margin + 10, margin + 10], fill=(255, 255, 200, 255))
    
    return img


def create_jungle_tile(size: int, tile_type: str) -> Image.Image:
    """Create a jungle background tile placeholder.
    
    Args:
        size: Size of the tile (width and height)
        tile_type: Type of tile (jungle_floor, jungle_canopy, vine, tree_trunk,
                   water, cave, mine_cart_track, bonus_barrel_bg)
    
    Returns:
        PIL Image with the background tile
    """
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    if tile_type == "jungle_floor":
        # Brown/green jungle floor
        draw.rectangle([0, 0, size, size], fill=(34, 100, 34, 255))
        # Add grass tufts
        for i in range(0, size, 6):
            grass_height = 3 + (i % 4)
            draw.line([(i, size), (i, size - grass_height)], fill=(50, 150, 50, 255), width=2)
            draw.line([(i + 2, size), (i + 1, size - grass_height - 2)], fill=(60, 160, 60, 255), width=1)
    
    elif tile_type == "jungle_canopy":
        # Dense green canopy
        draw.rectangle([0, 0, size, size], fill=(0, 80, 0, 255))
        # Add leaf clusters
        for i in range(0, size, 8):
            for j in range(0, size, 8):
                if (i + j) % 16 == 0:
                    draw.ellipse([i, j, i + 10, j + 8], fill=(0, 100, 0, 255))
                    draw.ellipse([i + 3, j + 2, i + 12, j + 10], fill=(0, 120, 0, 255))
    
    elif tile_type == "vine":
        # Vertical vine
        draw.rectangle([0, 0, size, size], fill=(135, 206, 235, 100))  # Sky background
        # Draw vine
        vine_x = size // 2
        draw.line([(vine_x, 0), (vine_x, size)], fill=(34, 139, 34, 255), width=4)
        # Add leaves
        for y in range(0, size, 10):
            leaf_dir = 1 if y % 20 == 0 else -1
            # Ensure x0 < x1 for ellipse
            if leaf_dir > 0:
                x0, x1 = vine_x + 3, vine_x + 12
            else:
                x0, x1 = vine_x - 12, vine_x - 3
            draw.ellipse([x0, y, x1, y + 6], fill=(50, 160, 50, 255))
    
    elif tile_type == "tree_trunk":
        # Brown tree trunk
        draw.rectangle([0, 0, size, size], fill=(101, 67, 33, 255))
        # Add bark texture
        for i in range(0, size, 8):
            draw.line([(0, i), (size, i + 2)], fill=(80, 50, 25, 255), width=1)
        # Add vertical grain
        for i in range(0, size, 12):
            draw.line([(i, 0), (i + 2, size)], fill=(120, 80, 40, 255), width=1)
    
    elif tile_type == "water":
        # Blue water with waves
        draw.rectangle([0, 0, size, size], fill=(30, 100, 180, 255))
        # Add wave pattern
        for i in range(0, size, 10):
            draw.arc([i - 5, size // 3, i + 10, size // 3 + 10], 0, 180, fill=(80, 150, 220, 255), width=2)
            draw.arc([i, size * 2 // 3, i + 15, size * 2 // 3 + 10], 0, 180, fill=(80, 150, 220, 255), width=2)
    
    elif tile_type == "cave":
        # Dark cave background
        draw.rectangle([0, 0, size, size], fill=(40, 40, 50, 255))
        # Add rock texture
        for i in range(0, size, 10):
            for j in range(0, size, 10):
                if (i * j) % 30 == 0:
                    draw.ellipse([i, j, i + 8, j + 6], fill=(50, 50, 60, 255))
    
    elif tile_type == "mine_cart_track":
        # Mine cart track
        draw.rectangle([0, 0, size, size], fill=(60, 50, 40, 255))  # Dark background
        # Draw rails
        rail_y1 = size // 3
        rail_y2 = size * 2 // 3
        draw.line([(0, rail_y1), (size, rail_y1)], fill=(100, 100, 100, 255), width=3)
        draw.line([(0, rail_y2), (size, rail_y2)], fill=(100, 100, 100, 255), width=3)
        # Draw ties
        for i in range(0, size, 8):
            draw.rectangle([i, rail_y1 - 2, i + 4, rail_y2 + 2], fill=(101, 67, 33, 255))
    
    elif tile_type == "bonus_barrel_bg":
        # Starry bonus area background
        draw.rectangle([0, 0, size, size], fill=(20, 20, 60, 255))
        # Add stars
        import random
        random.seed(42)  # Consistent pattern
        for _ in range(5):
            x = random.randint(2, size - 4)
            y = random.randint(2, size - 4)
            draw.ellipse([x, y, x + 3, y + 3], fill=(255, 255, 200, 255))
    
    elif tile_type == "sky":
        # Jungle sky
        draw.rectangle([0, 0, size, size], fill=(135, 200, 235, 255))
        # Add cloud wisps
        draw.ellipse([size // 4, size // 4, size * 3 // 4, size // 2], fill=(255, 255, 255, 150))
    
    return img


def create_enemy_sprite(size: int, enemy_type: str) -> Image.Image:
    """Create an enemy sprite placeholder.
    
    Args:
        size: Size of the sprite (width and height)
        enemy_type: Type of enemy (kremling, gnawty, zinger, klaptrap, boss)
    
    Returns:
        PIL Image with the enemy sprite
    """
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    center_x = size // 2
    center_y = size // 2
    
    if enemy_type == "kremling":
        # Green crocodile enemy (Kritter)
        body_color = (0, 150, 0, 255)
        belly_color = (150, 200, 100, 255)
        
        # Body
        draw.ellipse([size // 6, size // 4, size - size // 6, size - size // 6], fill=body_color)
        # Belly
        draw.ellipse([size // 4, size // 3, size - size // 4, size - size // 5], fill=belly_color)
        # Head
        draw.ellipse([size // 4, size // 8, size * 3 // 4, size // 2], fill=body_color)
        # Snout
        draw.ellipse([size // 3, size // 4, size * 2 // 3, size // 2 + 5], fill=body_color)
        # Eyes (angry)
        draw.ellipse([center_x - 8, size // 5, center_x - 2, size // 5 + 6], fill=(255, 255, 0, 255))
        draw.ellipse([center_x + 2, size // 5, center_x + 8, size // 5 + 6], fill=(255, 255, 0, 255))
        draw.ellipse([center_x - 6, size // 5 + 2, center_x - 4, size // 5 + 4], fill=(0, 0, 0, 255))
        draw.ellipse([center_x + 4, size // 5 + 2, center_x + 6, size // 5 + 4], fill=(0, 0, 0, 255))
    
    elif enemy_type == "gnawty":
        # Beaver enemy
        body_color = (139, 90, 43, 255)
        
        # Body
        draw.ellipse([size // 4, size // 3, size * 3 // 4, size - size // 6], fill=body_color)
        # Head
        draw.ellipse([size // 3, size // 6, size * 2 // 3, size // 2], fill=body_color)
        # Teeth
        draw.rectangle([center_x - 4, size // 2 - 2, center_x - 1, size // 2 + 5], fill=(255, 255, 255, 255))
        draw.rectangle([center_x + 1, size // 2 - 2, center_x + 4, size // 2 + 5], fill=(255, 255, 255, 255))
        # Eyes
        draw.ellipse([center_x - 8, size // 4, center_x - 3, size // 4 + 5], fill=(0, 0, 0, 255))
        draw.ellipse([center_x + 3, size // 4, center_x + 8, size // 4 + 5], fill=(0, 0, 0, 255))
        # Tail
        draw.ellipse([size * 3 // 4 - 5, size // 2, size - size // 8, size * 3 // 4], fill=(100, 60, 30, 255))
    
    elif enemy_type == "zinger":
        # Bee/wasp enemy
        body_color = (255, 200, 0, 255)
        stripe_color = (0, 0, 0, 255)
        
        # Body (oval)
        draw.ellipse([size // 4, size // 3, size * 3 // 4, size - size // 4], fill=body_color)
        # Stripes
        for i in range(3):
            y = size // 3 + 5 + i * 8
            draw.line([(size // 4 + 3, y), (size * 3 // 4 - 3, y)], fill=stripe_color, width=3)
        # Wings
        draw.ellipse([size // 8, size // 4, size // 3, size // 2], fill=(200, 200, 255, 180))
        draw.ellipse([size * 2 // 3, size // 4, size - size // 8, size // 2], fill=(200, 200, 255, 180))
        # Stinger
        draw.polygon([
            (center_x, size - size // 4),
            (center_x - 3, size - size // 8),
            (center_x + 3, size - size // 8),
        ], fill=(50, 50, 50, 255))
        # Eyes (angry)
        draw.ellipse([center_x - 8, size // 3, center_x - 2, size // 3 + 6], fill=(255, 0, 0, 255))
        draw.ellipse([center_x + 2, size // 3, center_x + 8, size // 3 + 6], fill=(255, 0, 0, 255))
    
    elif enemy_type == "klaptrap":
        # Small snapping enemy
        body_color = (0, 100, 200, 255)
        
        # Body
        draw.ellipse([size // 4, size // 3, size * 3 // 4, size - size // 6], fill=body_color)
        # Big mouth/jaw
        draw.arc([size // 6, size // 4, size - size // 6, size * 2 // 3], 0, 180, fill=(200, 50, 50, 255), width=size // 4)
        # Teeth
        for i in range(4):
            x = size // 4 + i * (size // 6)
            draw.polygon([
                (x, size // 2),
                (x + 4, size // 2 + 8),
                (x + 8, size // 2),
            ], fill=(255, 255, 255, 255))
        # Eyes
        draw.ellipse([center_x - 10, size // 5, center_x - 2, size // 5 + 8], fill=(255, 255, 255, 255))
        draw.ellipse([center_x + 2, size // 5, center_x + 10, size // 5 + 8], fill=(255, 255, 255, 255))
        draw.ellipse([center_x - 7, size // 5 + 2, center_x - 5, size // 5 + 6], fill=(0, 0, 0, 255))
        draw.ellipse([center_x + 5, size // 5 + 2, center_x + 7, size // 5 + 6], fill=(0, 0, 0, 255))
    
    elif enemy_type == "boss":
        # King K. Rool style boss
        body_color = (0, 120, 0, 255)
        belly_color = (200, 180, 100, 255)
        
        # Large body
        draw.ellipse([size // 8, size // 4, size - size // 8, size - size // 8], fill=body_color)
        # Belly
        draw.ellipse([size // 5, size // 3, size - size // 5, size - size // 6], fill=belly_color)
        # Head
        draw.ellipse([size // 5, 0, size - size // 5, size // 2], fill=body_color)
        # Crown
        crown_color = (255, 215, 0, 255)
        draw.polygon([
            (size // 4, size // 6),
            (size // 3, 0),
            (size // 2, size // 8),
            (size * 2 // 3, 0),
            (size * 3 // 4, size // 6),
        ], fill=crown_color)
        # Eyes (one big, one small - K. Rool style)
        draw.ellipse([center_x - 12, size // 5, center_x - 2, size // 5 + 12], fill=(255, 0, 0, 255))
        draw.ellipse([center_x + 4, size // 5 + 2, center_x + 10, size // 5 + 8], fill=(255, 255, 0, 255))
        draw.ellipse([center_x - 9, size // 5 + 4, center_x - 5, size // 5 + 8], fill=(0, 0, 0, 255))
        draw.ellipse([center_x + 6, size // 5 + 4, center_x + 8, size // 5 + 6], fill=(0, 0, 0, 255))
    
    return img


def create_ui_element(width: int, height: int, element_type: str) -> Image.Image:
    """Create a UI element placeholder.
    
    Args:
        width: Width of the element
        height: Height of the element
        element_type: Type of UI element
    
    Returns:
        PIL Image with the UI element
    """
    img = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    if element_type == "health_bar_bg":
        # Dark background for health bar
        draw.rectangle([0, 0, width, height], fill=(50, 50, 50, 200))
        draw.rectangle([2, 2, width - 2, height - 2], fill=(30, 30, 30, 255))
    
    elif element_type == "health_bar_fill":
        # Red health fill
        draw.rectangle([0, 0, width, height], fill=(220, 20, 20, 255))
        draw.rectangle([0, 0, width, height // 3], fill=(255, 80, 80, 255))
    
    elif element_type == "banana_icon":
        # Small banana icon for counter
        return create_banana_sprite(min(width, height))
    
    elif element_type == "banana_counter_bg":
        # Background for banana counter
        draw.rectangle([0, 0, width, height], fill=(60, 40, 20, 220))
        draw.rectangle([2, 2, width - 2, height - 2], outline=(139, 90, 43, 255), width=2)
    
    elif element_type == "timer_bg":
        # Timer background for time trials
        draw.rectangle([0, 0, width, height], fill=(20, 20, 40, 220))
        draw.rectangle([2, 2, width - 2, height - 2], outline=(100, 100, 150, 255), width=2)
        # Clock icon hint
        center_x = width // 6
        center_y = height // 2
        draw.ellipse([center_x - 8, center_y - 8, center_x + 8, center_y + 8], outline=(200, 200, 200, 255), width=2)
        draw.line([(center_x, center_y), (center_x, center_y - 5)], fill=(200, 200, 200, 255), width=1)
        draw.line([(center_x, center_y), (center_x + 4, center_y)], fill=(200, 200, 200, 255), width=1)
    
    elif element_type == "panel_bg":
        # Semi-transparent panel background (DKC style - wooden)
        draw.rectangle([0, 0, width, height], fill=(80, 50, 30, 220))
        draw.rectangle([2, 2, width - 2, height - 2], outline=(139, 90, 43, 200), width=3)
        # Wood grain effect
        for i in range(0, height, 10):
            draw.line([(4, i), (width - 4, i + 2)], fill=(100, 60, 35, 150), width=1)
    
    elif element_type == "kong_letters_bg":
        # Background for KONG letter display
        draw.rectangle([0, 0, width, height], fill=(40, 40, 60, 220))
        # Four slots for K-O-N-G
        slot_width = (width - 20) // 4
        for i in range(4):
            x = 5 + i * (slot_width + 3)
            draw.rectangle([x, 5, x + slot_width, height - 5], fill=(60, 60, 80, 255), outline=(100, 100, 120, 255))
    
    elif element_type == "world_progress_bg":
        # World completion progress bar background
        draw.rectangle([0, 0, width, height], fill=(40, 60, 40, 220))
        draw.rectangle([2, 2, width - 2, height - 2], outline=(80, 120, 80, 255), width=2)
    
    elif element_type == "world_progress_fill":
        # World completion progress fill (green)
        draw.rectangle([0, 0, width, height], fill=(50, 180, 50, 255))
        draw.rectangle([0, 0, width, height // 3], fill=(80, 220, 80, 255))
    
    elif element_type == "life_icon":
        # Extra life balloon icon
        balloon_color = (255, 50, 50, 255)
        center_x = width // 2
        center_y = height // 2
        # Balloon
        draw.ellipse([center_x - 8, center_y - 10, center_x + 8, center_y + 5], fill=balloon_color)
        # String
        draw.line([(center_x, center_y + 5), (center_x, center_y + 12)], fill=(200, 200, 200, 255), width=1)
        # Shine
        draw.ellipse([center_x - 4, center_y - 6, center_x - 1, center_y - 3], fill=(255, 200, 200, 255))
    
    return img


def main():
    """Generate all placeholder sprites for the DKC theme."""
    # Base path for DKC assets
    base_path = Path("assets/dkc")
    
    # Create directory structure
    create_directory_structure(base_path)
    
    # Character sprite settings (larger for DK)
    char_width = 48
    char_height = 64
    
    # Create character sprites (Donkey Kong)
    print("Creating character sprites...")
    states = ["idle", "run", "collect", "damage"]
    for state in states:
        sprite = create_dk_sprite(char_width, char_height, state)
        sprite.save(base_path / "characters" / f"dk_{state}.png")
        print(f"  Created dk_{state}.png")
    
    # Create collectible sprites (32x32)
    print("Creating collectible sprites...")
    item_size = 32
    
    # Banana (single)
    banana = create_banana_sprite(item_size)
    banana.save(base_path / "items" / "banana.png")
    print("  Created banana.png")
    
    # Banana bunch
    banana_bunch = create_banana_bunch_sprite(item_size)
    banana_bunch.save(base_path / "items" / "banana_bunch.png")
    print("  Created banana_bunch.png")
    
    # Barrels
    barrel_types = ["normal", "dk_barrel", "tnt"]
    for barrel_type in barrel_types:
        barrel = create_barrel_sprite(item_size, barrel_type)
        filename = f"barrel_{barrel_type}.png" if barrel_type != "normal" else "barrel.png"
        barrel.save(base_path / "items" / filename)
        print(f"  Created {filename}")
    
    # KONG letters
    for letter in ["K", "O", "N", "G"]:
        kong_letter = create_kong_letter_sprite(item_size, letter)
        kong_letter.save(base_path / "items" / f"kong_{letter.lower()}.png")
        print(f"  Created kong_{letter.lower()}.png")
    
    # Create jungle background tiles (32x32)
    print("Creating background tiles...")
    tile_size = 32
    tile_types = [
        "jungle_floor", "jungle_canopy", "vine", "tree_trunk",
        "water", "cave", "mine_cart_track", "bonus_barrel_bg", "sky"
    ]
    for tile_type in tile_types:
        tile = create_jungle_tile(tile_size, tile_type)
        tile.save(base_path / "backgrounds" / f"{tile_type}.png")
        print(f"  Created {tile_type}.png")
    
    # Create enemy sprites
    print("Creating enemy sprites...")
    enemy_size = 32
    enemy_types = ["kremling", "gnawty", "zinger", "klaptrap"]
    for enemy_type in enemy_types:
        enemy = create_enemy_sprite(enemy_size, enemy_type)
        enemy.save(base_path / "enemies" / f"{enemy_type}.png")
        print(f"  Created {enemy_type}.png")
    
    # Boss sprite (larger)
    boss_size = 64
    boss = create_enemy_sprite(boss_size, "boss")
    boss.save(base_path / "enemies" / "boss.png")
    print("  Created boss.png")
    
    # Create UI elements
    print("Creating UI elements...")
    
    health_bar_bg = create_ui_element(100, 20, "health_bar_bg")
    health_bar_bg.save(base_path / "ui" / "health_bar_bg.png")
    print("  Created health_bar_bg.png")
    
    health_bar_fill = create_ui_element(96, 16, "health_bar_fill")
    health_bar_fill.save(base_path / "ui" / "health_bar_fill.png")
    print("  Created health_bar_fill.png")
    
    banana_icon = create_ui_element(24, 24, "banana_icon")
    banana_icon.save(base_path / "ui" / "banana_icon.png")
    print("  Created banana_icon.png")
    
    banana_counter_bg = create_ui_element(80, 30, "banana_counter_bg")
    banana_counter_bg.save(base_path / "ui" / "banana_counter_bg.png")
    print("  Created banana_counter_bg.png")
    
    timer_bg = create_ui_element(120, 30, "timer_bg")
    timer_bg.save(base_path / "ui" / "timer_bg.png")
    print("  Created timer_bg.png")
    
    panel_bg = create_ui_element(200, 100, "panel_bg")
    panel_bg.save(base_path / "ui" / "panel_bg.png")
    print("  Created panel_bg.png")
    
    kong_letters_bg = create_ui_element(160, 40, "kong_letters_bg")
    kong_letters_bg.save(base_path / "ui" / "kong_letters_bg.png")
    print("  Created kong_letters_bg.png")
    
    world_progress_bg = create_ui_element(150, 20, "world_progress_bg")
    world_progress_bg.save(base_path / "ui" / "world_progress_bg.png")
    print("  Created world_progress_bg.png")
    
    world_progress_fill = create_ui_element(146, 16, "world_progress_fill")
    world_progress_fill.save(base_path / "ui" / "world_progress_fill.png")
    print("  Created world_progress_fill.png")
    
    life_icon = create_ui_element(24, 24, "life_icon")
    life_icon.save(base_path / "ui" / "life_icon.png")
    print("  Created life_icon.png")
    
    print("\nAll DKC theme placeholder sprites created successfully!")
    print(f"Assets saved to: {base_path.absolute()}")


if __name__ == "__main__":
    main()
