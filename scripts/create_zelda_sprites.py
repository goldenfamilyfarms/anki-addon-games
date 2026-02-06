"""
Script to create placeholder sprites for the Zelda theme.

This script generates simple colored shapes as placeholder sprites for:
- Character sprites (idle, walk, attack, damage)
- Item sprites (heart, sword, shield, key, etc.)
- Map tiles (grass, water, mountain, dungeon, etc.)
- UI elements
- Enemy sprites

Requirements: 5.8
"""

from pathlib import Path
from PIL import Image, ImageDraw
import math


def create_directory_structure(base_path: Path) -> None:
    """Create the directory structure for Zelda assets."""
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


def create_link_sprite(
    width: int,
    height: int,
    state: str
) -> Image.Image:
    """Create a Link character sprite placeholder.
    
    Args:
        width: Width of the sprite
        height: Height of the sprite
        state: Animation state (idle, walk, attack, damage)
    
    Returns:
        PIL Image with the character sprite
    """
    img = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Link's colors
    tunic_color = (0, 128, 0, 255)  # Green tunic
    skin_color = (255, 200, 150, 255)
    hair_color = (200, 180, 100, 255)  # Blonde hair
    
    # Draw body (rectangle)
    body_top = height // 3
    body_bottom = height - height // 6
    body_left = width // 4
    body_right = width - width // 4
    draw.rectangle([body_left, body_top, body_right, body_bottom], fill=tunic_color)
    
    # Draw head (circle)
    head_radius = width // 5
    head_center = (width // 2, body_top - head_radius // 2)
    draw.ellipse([
        head_center[0] - head_radius,
        head_center[1] - head_radius,
        head_center[0] + head_radius,
        head_center[1] + head_radius
    ], fill=skin_color)
    
    # Draw hair (pointed cap style)
    draw.polygon([
        (head_center[0] - head_radius, head_center[1] - head_radius // 2),
        (head_center[0], head_center[1] - head_radius - 5),
        (head_center[0] + head_radius + 5, head_center[1] - head_radius // 2),
    ], fill=hair_color)
    
    # Add state-specific details
    if state == "walk":
        # Add motion lines
        draw.line([(body_left - 5, body_top + 5), (body_left - 12, body_top + 5)], fill=(200, 200, 200, 200), width=2)
        draw.line([(body_left - 5, body_top + 15), (body_left - 10, body_top + 15)], fill=(200, 200, 200, 200), width=2)
        # Legs in walking position
        draw.line([(body_left + 5, body_bottom), (body_left, body_bottom + 8)], fill=tunic_color, width=4)
        draw.line([(body_right - 5, body_bottom), (body_right, body_bottom + 8)], fill=tunic_color, width=4)
    elif state == "attack":
        # Draw sword arm extended
        sword_color = (192, 192, 192, 255)
        draw.line([(body_right, body_top + 10), (body_right + 15, body_top - 5)], fill=skin_color, width=3)
        # Draw sword
        draw.line([(body_right + 12, body_top - 5), (body_right + 25, body_top - 20)], fill=sword_color, width=3)
        draw.polygon([
            (body_right + 25, body_top - 20),
            (body_right + 28, body_top - 18),
            (body_right + 23, body_top - 15),
        ], fill=sword_color)
    elif state == "damage":
        # Add red tint/flash effect
        overlay = Image.new('RGBA', (width, height), (255, 0, 0, 80))
        img = Image.alpha_composite(img, overlay)
        draw = ImageDraw.Draw(img)
        # Add X eyes
        eye_y = head_center[1]
        draw.line([(head_center[0] - 8, eye_y - 3), (head_center[0] - 2, eye_y + 3)], fill=(0, 0, 0, 255), width=2)
        draw.line([(head_center[0] - 8, eye_y + 3), (head_center[0] - 2, eye_y - 3)], fill=(0, 0, 0, 255), width=2)
        draw.line([(head_center[0] + 2, eye_y - 3), (head_center[0] + 8, eye_y + 3)], fill=(0, 0, 0, 255), width=2)
        draw.line([(head_center[0] + 2, eye_y + 3), (head_center[0] + 8, eye_y - 3)], fill=(0, 0, 0, 255), width=2)
    else:  # idle
        # Draw simple eyes
        eye_y = head_center[1]
        draw.ellipse([head_center[0] - 6, eye_y - 2, head_center[0] - 2, eye_y + 2], fill=(0, 0, 0, 255))
        draw.ellipse([head_center[0] + 2, eye_y - 2, head_center[0] + 6, eye_y + 2], fill=(0, 0, 0, 255))
        # Standing legs
        draw.line([(body_left + 5, body_bottom), (body_left + 5, body_bottom + 8)], fill=tunic_color, width=4)
        draw.line([(body_right - 5, body_bottom), (body_right - 5, body_bottom + 8)], fill=tunic_color, width=4)
    
    return img


def create_heart_sprite(size: int, filled: bool = True) -> Image.Image:
    """Create a heart sprite placeholder.
    
    Args:
        size: Size of the sprite (width and height)
        filled: Whether the heart is filled (True) or empty (False)
    
    Returns:
        PIL Image with the heart sprite
    """
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Heart shape using bezier-like curves
    center_x = size // 2
    center_y = size // 2
    
    # Create heart shape points
    heart_points = []
    for i in range(100):
        t = i / 100 * 2 * math.pi
        x = 16 * (math.sin(t) ** 3)
        y = -(13 * math.cos(t) - 5 * math.cos(2*t) - 2 * math.cos(3*t) - math.cos(4*t))
        # Scale to fit
        scale = size / 40
        heart_points.append((center_x + x * scale, center_y + y * scale - size // 8))
    
    fill_color = (255, 0, 0, 255) if filled else (100, 100, 100, 100)
    outline_color = (180, 0, 0, 255) if filled else (80, 80, 80, 255)
    
    draw.polygon(heart_points, fill=fill_color, outline=outline_color)
    
    # Add shine if filled
    if filled:
        shine_x = center_x - size // 6
        shine_y = center_y - size // 6
        draw.ellipse([shine_x - 2, shine_y - 2, shine_x + 2, shine_y + 2], fill=(255, 200, 200, 255))
    
    return img


def create_sword_sprite(size: int) -> Image.Image:
    """Create a sword sprite placeholder.
    
    Args:
        size: Size of the sprite (width and height)
    
    Returns:
        PIL Image with the sword sprite
    """
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    center_x = size // 2
    blade_color = (192, 192, 192, 255)
    hilt_color = (139, 69, 19, 255)
    guard_color = (255, 215, 0, 255)
    
    # Draw blade (pointing up)
    blade_width = size // 6
    blade_top = size // 8
    blade_bottom = size * 2 // 3
    draw.polygon([
        (center_x, blade_top),  # Tip
        (center_x - blade_width, blade_bottom),
        (center_x + blade_width, blade_bottom),
    ], fill=blade_color, outline=(150, 150, 150, 255))
    
    # Add blade shine
    draw.line([(center_x - 2, blade_top + 10), (center_x - 2, blade_bottom - 5)], fill=(220, 220, 220, 255), width=2)
    
    # Draw guard (cross piece)
    guard_y = blade_bottom
    guard_width = size // 3
    draw.rectangle([
        center_x - guard_width,
        guard_y - 3,
        center_x + guard_width,
        guard_y + 3
    ], fill=guard_color)
    
    # Draw hilt
    hilt_top = guard_y + 3
    hilt_bottom = size - size // 8
    hilt_width = size // 8
    draw.rectangle([
        center_x - hilt_width,
        hilt_top,
        center_x + hilt_width,
        hilt_bottom
    ], fill=hilt_color)
    
    # Draw pommel
    pommel_radius = size // 10
    draw.ellipse([
        center_x - pommel_radius,
        hilt_bottom - pommel_radius // 2,
        center_x + pommel_radius,
        hilt_bottom + pommel_radius
    ], fill=guard_color)
    
    return img


def create_shield_sprite(size: int) -> Image.Image:
    """Create a shield sprite placeholder.
    
    Args:
        size: Size of the sprite (width and height)
    
    Returns:
        PIL Image with the shield sprite
    """
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    center_x = size // 2
    center_y = size // 2
    
    # Shield colors (Hylian shield style)
    shield_blue = (0, 0, 139, 255)
    shield_red = (139, 0, 0, 255)
    border_color = (192, 192, 192, 255)
    
    # Draw shield shape (pointed bottom)
    margin = size // 8
    shield_points = [
        (margin, margin),  # Top left
        (size - margin, margin),  # Top right
        (size - margin, center_y),  # Right middle
        (center_x, size - margin),  # Bottom point
        (margin, center_y),  # Left middle
    ]
    draw.polygon(shield_points, fill=shield_blue, outline=border_color)
    
    # Draw inner border
    inner_margin = size // 6
    inner_points = [
        (inner_margin, inner_margin),
        (size - inner_margin, inner_margin),
        (size - inner_margin, center_y - 2),
        (center_x, size - inner_margin - 4),
        (inner_margin, center_y - 2),
    ]
    draw.polygon(inner_points, outline=border_color)
    
    # Draw bird/triforce symbol (simplified)
    symbol_y = center_y - size // 8
    triangle_size = size // 6
    # Top triangle
    draw.polygon([
        (center_x, symbol_y - triangle_size),
        (center_x - triangle_size // 2, symbol_y),
        (center_x + triangle_size // 2, symbol_y),
    ], fill=shield_red)
    
    return img


def create_key_sprite(size: int) -> Image.Image:
    """Create a key sprite placeholder.
    
    Args:
        size: Size of the sprite (width and height)
    
    Returns:
        PIL Image with the key sprite
    """
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    key_color = (255, 215, 0, 255)  # Gold
    outline_color = (200, 160, 0, 255)
    
    center_x = size // 2
    
    # Draw key bow (circular top)
    bow_radius = size // 4
    bow_center_y = size // 4
    draw.ellipse([
        center_x - bow_radius,
        bow_center_y - bow_radius,
        center_x + bow_radius,
        bow_center_y + bow_radius
    ], fill=key_color, outline=outline_color)
    # Inner hole
    inner_radius = bow_radius // 2
    draw.ellipse([
        center_x - inner_radius,
        bow_center_y - inner_radius,
        center_x + inner_radius,
        bow_center_y + inner_radius
    ], fill=(0, 0, 0, 0))
    
    # Draw key shaft
    shaft_width = size // 8
    shaft_top = bow_center_y + bow_radius - 2
    shaft_bottom = size - size // 6
    draw.rectangle([
        center_x - shaft_width // 2,
        shaft_top,
        center_x + shaft_width // 2,
        shaft_bottom
    ], fill=key_color, outline=outline_color)
    
    # Draw key teeth
    teeth_y = shaft_bottom - size // 8
    draw.rectangle([
        center_x + shaft_width // 2,
        teeth_y,
        center_x + shaft_width,
        teeth_y + size // 12
    ], fill=key_color, outline=outline_color)
    draw.rectangle([
        center_x + shaft_width // 2,
        teeth_y + size // 8,
        center_x + shaft_width * 3 // 4,
        teeth_y + size // 8 + size // 16
    ], fill=key_color, outline=outline_color)
    
    return img


def create_rupee_sprite(size: int, color: str = "green") -> Image.Image:
    """Create a rupee (gem) sprite placeholder.
    
    Args:
        size: Size of the sprite (width and height)
        color: Color of the rupee (green, blue, red)
    
    Returns:
        PIL Image with the rupee sprite
    """
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    colors = {
        "green": ((0, 200, 0, 255), (0, 150, 0, 255)),
        "blue": ((0, 100, 255, 255), (0, 50, 200, 255)),
        "red": ((255, 50, 50, 255), (200, 0, 0, 255)),
    }
    fill_color, outline_color = colors.get(color, colors["green"])
    
    center_x = size // 2
    center_y = size // 2
    
    # Hexagonal gem shape
    margin = size // 6
    points = [
        (center_x, margin),  # Top
        (size - margin, center_y - size // 6),  # Upper right
        (size - margin, center_y + size // 6),  # Lower right
        (center_x, size - margin),  # Bottom
        (margin, center_y + size // 6),  # Lower left
        (margin, center_y - size // 6),  # Upper left
    ]
    draw.polygon(points, fill=fill_color, outline=outline_color)
    
    # Add shine
    draw.line([(center_x - 3, margin + 5), (center_x - 3, center_y)], fill=(255, 255, 255, 150), width=2)
    
    return img


def create_potion_sprite(size: int, color: str = "red") -> Image.Image:
    """Create a potion bottle sprite placeholder.
    
    Args:
        size: Size of the sprite (width and height)
        color: Color of the potion (red, green, blue)
    
    Returns:
        PIL Image with the potion sprite
    """
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    colors = {
        "red": (255, 50, 50, 255),
        "green": (50, 255, 50, 255),
        "blue": (50, 100, 255, 255),
    }
    potion_color = colors.get(color, colors["red"])
    bottle_color = (200, 200, 220, 200)
    cork_color = (139, 90, 43, 255)
    
    center_x = size // 2
    
    # Draw bottle body
    body_top = size // 3
    body_bottom = size - size // 8
    body_width = size // 3
    draw.ellipse([
        center_x - body_width,
        body_top,
        center_x + body_width,
        body_bottom
    ], fill=bottle_color, outline=(150, 150, 170, 255))
    
    # Draw potion liquid
    liquid_margin = 4
    draw.ellipse([
        center_x - body_width + liquid_margin,
        body_top + size // 6,
        center_x + body_width - liquid_margin,
        body_bottom - liquid_margin
    ], fill=potion_color)
    
    # Draw bottle neck
    neck_width = size // 8
    neck_top = size // 8
    draw.rectangle([
        center_x - neck_width,
        neck_top,
        center_x + neck_width,
        body_top + 5
    ], fill=bottle_color, outline=(150, 150, 170, 255))
    
    # Draw cork
    draw.rectangle([
        center_x - neck_width - 2,
        neck_top - 5,
        center_x + neck_width + 2,
        neck_top + 3
    ], fill=cork_color)
    
    return img


def create_map_tile(size: int, tile_type: str) -> Image.Image:
    """Create a map tile placeholder for the adventure map.
    
    Args:
        size: Size of the tile (width and height)
        tile_type: Type of tile (grass, water, mountain, dungeon, forest, 
                   desert, explored, unexplored, path, bridge)
    
    Returns:
        PIL Image with the map tile
    """
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    if tile_type == "grass":
        # Green grass tile
        draw.rectangle([0, 0, size, size], fill=(34, 139, 34, 255))
        # Add grass texture
        for i in range(0, size, 4):
            for j in range(0, size, 4):
                if (i + j) % 8 == 0:
                    draw.line([(i, j), (i, j + 3)], fill=(50, 160, 50, 255), width=1)
    
    elif tile_type == "water":
        # Blue water tile
        draw.rectangle([0, 0, size, size], fill=(30, 144, 255, 255))
        # Add wave pattern
        for i in range(0, size, 8):
            draw.arc([i - 4, size // 3, i + 8, size // 3 + 8], 0, 180, fill=(100, 180, 255, 255))
            draw.arc([i, size * 2 // 3, i + 12, size * 2 // 3 + 8], 0, 180, fill=(100, 180, 255, 255))
    
    elif tile_type == "mountain":
        # Gray mountain tile
        draw.rectangle([0, 0, size, size], fill=(128, 128, 128, 255))
        # Draw mountain peaks
        draw.polygon([
            (size // 4, size),
            (size // 2, size // 4),
            (size * 3 // 4, size),
        ], fill=(100, 100, 100, 255), outline=(80, 80, 80, 255))
        # Snow cap
        draw.polygon([
            (size // 2 - 4, size // 3),
            (size // 2, size // 4),
            (size // 2 + 4, size // 3),
        ], fill=(255, 255, 255, 255))
    
    elif tile_type == "dungeon":
        # Dark dungeon entrance tile
        draw.rectangle([0, 0, size, size], fill=(50, 50, 50, 255))
        # Draw entrance
        entrance_margin = size // 4
        draw.rectangle([
            entrance_margin,
            entrance_margin,
            size - entrance_margin,
            size - entrance_margin // 2
        ], fill=(20, 20, 20, 255), outline=(80, 80, 80, 255))
        # Add skull or danger symbol
        center_x = size // 2
        draw.ellipse([center_x - 4, size // 3, center_x + 4, size // 3 + 8], fill=(200, 200, 200, 255))
    
    elif tile_type == "forest":
        # Dark green forest tile
        draw.rectangle([0, 0, size, size], fill=(0, 100, 0, 255))
        # Draw trees
        tree_positions = [(size // 4, size // 2), (size * 3 // 4, size // 2), (size // 2, size // 4)]
        for tx, ty in tree_positions:
            # Tree trunk
            draw.rectangle([tx - 2, ty, tx + 2, ty + 10], fill=(101, 67, 33, 255))
            # Tree foliage
            draw.polygon([
                (tx, ty - 8),
                (tx - 6, ty + 2),
                (tx + 6, ty + 2),
            ], fill=(0, 80, 0, 255))
    
    elif tile_type == "desert":
        # Sandy desert tile
        draw.rectangle([0, 0, size, size], fill=(237, 201, 175, 255))
        # Add sand dune pattern
        draw.arc([0, size // 2, size, size], 180, 360, fill=(220, 180, 150, 255))
    
    elif tile_type == "explored":
        # Explored region (lighter, visible)
        draw.rectangle([0, 0, size, size], fill=(144, 238, 144, 255))
        # Add checkmark or visited indicator
        draw.line([(size // 4, size // 2), (size // 2 - 2, size * 3 // 4)], fill=(0, 100, 0, 255), width=2)
        draw.line([(size // 2 - 2, size * 3 // 4), (size * 3 // 4, size // 4)], fill=(0, 100, 0, 255), width=2)
    
    elif tile_type == "unexplored":
        # Unexplored region (darker, foggy)
        draw.rectangle([0, 0, size, size], fill=(80, 80, 80, 200))
        # Add question mark
        center_x = size // 2
        draw.text((center_x - 4, size // 3), "?", fill=(150, 150, 150, 255))
    
    elif tile_type == "path":
        # Dirt path tile
        draw.rectangle([0, 0, size, size], fill=(34, 139, 34, 255))  # Grass background
        # Draw path
        path_width = size // 3
        draw.rectangle([
            (size - path_width) // 2,
            0,
            (size + path_width) // 2,
            size
        ], fill=(139, 119, 101, 255))
    
    elif tile_type == "bridge":
        # Bridge over water
        draw.rectangle([0, 0, size, size], fill=(30, 144, 255, 255))  # Water background
        # Draw wooden bridge
        bridge_width = size // 2
        draw.rectangle([
            (size - bridge_width) // 2,
            0,
            (size + bridge_width) // 2,
            size
        ], fill=(139, 90, 43, 255))
        # Bridge planks
        for i in range(0, size, size // 4):
            draw.line([((size - bridge_width) // 2, i), ((size + bridge_width) // 2, i)], fill=(100, 60, 30, 255), width=1)
    
    elif tile_type == "castle":
        # Castle tile
        draw.rectangle([0, 0, size, size], fill=(169, 169, 169, 255))
        # Draw castle towers
        tower_width = size // 4
        draw.rectangle([0, size // 3, tower_width, size], fill=(128, 128, 128, 255))
        draw.rectangle([size - tower_width, size // 3, size, size], fill=(128, 128, 128, 255))
        # Battlements
        for i in range(0, tower_width, 4):
            draw.rectangle([i, size // 3 - 4, i + 2, size // 3], fill=(128, 128, 128, 255))
            draw.rectangle([size - tower_width + i, size // 3 - 4, size - tower_width + i + 2, size // 3], fill=(128, 128, 128, 255))
        # Gate
        draw.rectangle([size // 3, size // 2, size * 2 // 3, size], fill=(60, 40, 20, 255))
    
    return img


def create_enemy_sprite(size: int, enemy_type: str) -> Image.Image:
    """Create an enemy sprite placeholder.
    
    Args:
        size: Size of the sprite (width and height)
        enemy_type: Type of enemy (octorok, moblin, keese, stalfos, boss)
    
    Returns:
        PIL Image with the enemy sprite
    """
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    center_x = size // 2
    center_y = size // 2
    
    if enemy_type == "octorok":
        # Red octopus-like enemy
        body_color = (200, 50, 50, 255)
        draw.ellipse([size // 4, size // 4, size * 3 // 4, size * 3 // 4], fill=body_color)
        # Eyes
        draw.ellipse([center_x - 8, center_y - 5, center_x - 2, center_y + 1], fill=(255, 255, 255, 255))
        draw.ellipse([center_x + 2, center_y - 5, center_x + 8, center_y + 1], fill=(255, 255, 255, 255))
        draw.ellipse([center_x - 6, center_y - 3, center_x - 4, center_y - 1], fill=(0, 0, 0, 255))
        draw.ellipse([center_x + 4, center_y - 3, center_x + 6, center_y - 1], fill=(0, 0, 0, 255))
    
    elif enemy_type == "moblin":
        # Pig-like enemy
        body_color = (139, 90, 43, 255)
        # Body
        draw.rectangle([size // 4, size // 3, size * 3 // 4, size - size // 6], fill=body_color)
        # Head
        draw.ellipse([size // 3, size // 8, size * 2 // 3, size // 2], fill=body_color)
        # Snout
        draw.ellipse([center_x - 4, size // 3, center_x + 4, size // 3 + 8], fill=(200, 150, 150, 255))
        # Eyes (angry)
        draw.line([(center_x - 8, size // 4), (center_x - 3, size // 4 + 3)], fill=(0, 0, 0, 255), width=2)
        draw.line([(center_x + 3, size // 4 + 3), (center_x + 8, size // 4)], fill=(0, 0, 0, 255), width=2)
    
    elif enemy_type == "keese":
        # Bat-like enemy
        body_color = (50, 50, 80, 255)
        # Body
        draw.ellipse([center_x - 5, center_y - 3, center_x + 5, center_y + 5], fill=body_color)
        # Wings
        draw.polygon([
            (center_x - 5, center_y),
            (size // 8, center_y - 8),
            (size // 8, center_y + 5),
        ], fill=body_color)
        draw.polygon([
            (center_x + 5, center_y),
            (size - size // 8, center_y - 8),
            (size - size // 8, center_y + 5),
        ], fill=body_color)
        # Eyes (red)
        draw.ellipse([center_x - 4, center_y - 2, center_x - 1, center_y + 1], fill=(255, 0, 0, 255))
        draw.ellipse([center_x + 1, center_y - 2, center_x + 4, center_y + 1], fill=(255, 0, 0, 255))
    
    elif enemy_type == "stalfos":
        # Skeleton enemy
        bone_color = (240, 230, 210, 255)
        # Skull
        draw.ellipse([center_x - 8, size // 8, center_x + 8, size // 8 + 16], fill=bone_color)
        # Eye sockets
        draw.ellipse([center_x - 6, size // 8 + 4, center_x - 2, size // 8 + 8], fill=(0, 0, 0, 255))
        draw.ellipse([center_x + 2, size // 8 + 4, center_x + 6, size // 8 + 8], fill=(0, 0, 0, 255))
        # Ribcage
        for i in range(3):
            y = size // 3 + i * 6
            draw.line([(center_x - 6, y), (center_x + 6, y)], fill=bone_color, width=2)
        # Spine
        draw.line([(center_x, size // 8 + 16), (center_x, size - size // 4)], fill=bone_color, width=3)
    
    elif enemy_type == "boss":
        # Large boss enemy (Ganon-like)
        body_color = (100, 50, 150, 255)  # Purple
        # Large body
        draw.ellipse([size // 8, size // 4, size - size // 8, size - size // 8], fill=body_color)
        # Horns
        draw.polygon([
            (size // 4, size // 4),
            (size // 8, 0),
            (size // 3, size // 6),
        ], fill=(80, 40, 120, 255))
        draw.polygon([
            (size * 3 // 4, size // 4),
            (size - size // 8, 0),
            (size * 2 // 3, size // 6),
        ], fill=(80, 40, 120, 255))
        # Glowing eyes
        draw.ellipse([center_x - 10, center_y - 8, center_x - 2, center_y], fill=(255, 255, 0, 255))
        draw.ellipse([center_x + 2, center_y - 8, center_x + 10, center_y], fill=(255, 255, 0, 255))
    
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
    
    elif element_type == "heart_container":
        # Heart container UI
        return create_heart_sprite(min(width, height))
    
    elif element_type == "panel_bg":
        # Semi-transparent panel background (Zelda style - darker)
        draw.rectangle([0, 0, width, height], fill=(20, 40, 60, 220))
        draw.rectangle([2, 2, width - 2, height - 2], outline=(100, 150, 200, 150), width=2)
    
    elif element_type == "map_frame":
        # Frame for the adventure map
        draw.rectangle([0, 0, width, height], fill=(60, 40, 20, 255))
        draw.rectangle([4, 4, width - 4, height - 4], fill=(40, 25, 10, 255))
        draw.rectangle([8, 8, width - 8, height - 8], outline=(100, 70, 40, 255), width=2)
    
    elif element_type == "item_slot":
        # Item slot for inventory
        draw.rectangle([0, 0, width, height], fill=(40, 40, 60, 255))
        draw.rectangle([2, 2, width - 2, height - 2], outline=(80, 80, 120, 255), width=1)
    
    return img


def main():
    """Generate all placeholder sprites for the Zelda theme."""
    # Base path for Zelda assets
    base_path = Path("assets/zelda")
    
    # Create directory structure
    create_directory_structure(base_path)
    
    # Character sprite settings
    char_width = 32
    char_height = 48
    
    # Create character sprites (Link)
    print("Creating character sprites...")
    states = ["idle", "walk", "attack", "damage"]
    for state in states:
        sprite = create_link_sprite(char_width, char_height, state)
        sprite.save(base_path / "characters" / f"link_{state}.png")
        print(f"  Created link_{state}.png")
    
    # Create item sprites (32x32)
    print("Creating item sprites...")
    item_size = 32
    
    # Heart (filled and empty)
    heart_filled = create_heart_sprite(item_size, filled=True)
    heart_filled.save(base_path / "items" / "heart.png")
    print("  Created heart.png")
    
    heart_empty = create_heart_sprite(item_size, filled=False)
    heart_empty.save(base_path / "items" / "heart_empty.png")
    print("  Created heart_empty.png")
    
    # Sword
    sword = create_sword_sprite(item_size)
    sword.save(base_path / "items" / "sword.png")
    print("  Created sword.png")
    
    # Shield
    shield = create_shield_sprite(item_size)
    shield.save(base_path / "items" / "shield.png")
    print("  Created shield.png")
    
    # Key
    key = create_key_sprite(item_size)
    key.save(base_path / "items" / "key.png")
    print("  Created key.png")
    
    # Rupees (different colors)
    for color in ["green", "blue", "red"]:
        rupee = create_rupee_sprite(item_size, color)
        rupee.save(base_path / "items" / f"rupee_{color}.png")
        print(f"  Created rupee_{color}.png")
    
    # Potions
    for color in ["red", "green", "blue"]:
        potion = create_potion_sprite(item_size, color)
        potion.save(base_path / "items" / f"potion_{color}.png")
        print(f"  Created potion_{color}.png")
    
    # Create map tiles (32x32) for adventure map
    print("Creating map tiles...")
    tile_size = 32
    tile_types = [
        "grass", "water", "mountain", "dungeon", "forest",
        "desert", "explored", "unexplored", "path", "bridge", "castle"
    ]
    for tile_type in tile_types:
        tile = create_map_tile(tile_size, tile_type)
        tile.save(base_path / "backgrounds" / f"{tile_type}.png")
        print(f"  Created {tile_type}.png")
    
    # Create enemy sprites
    print("Creating enemy sprites...")
    enemy_size = 32
    enemy_types = ["octorok", "moblin", "keese", "stalfos"]
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
    
    heart_container = create_ui_element(24, 24, "heart_container")
    heart_container.save(base_path / "ui" / "heart_container.png")
    print("  Created heart_container.png")
    
    panel_bg = create_ui_element(200, 100, "panel_bg")
    panel_bg.save(base_path / "ui" / "panel_bg.png")
    print("  Created panel_bg.png")
    
    map_frame = create_ui_element(256, 256, "map_frame")
    map_frame.save(base_path / "ui" / "map_frame.png")
    print("  Created map_frame.png")
    
    item_slot = create_ui_element(40, 40, "item_slot")
    item_slot.save(base_path / "ui" / "item_slot.png")
    print("  Created item_slot.png")
    
    print("\nAll Zelda theme placeholder sprites created successfully!")
    print(f"Assets saved to: {base_path.absolute()}")


if __name__ == "__main__":
    main()
