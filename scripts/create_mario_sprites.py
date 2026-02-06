"""
Script to create placeholder sprites for the Mario theme.

This script generates simple colored shapes as placeholder sprites for:
- Character sprites (idle, run, jump, damage)
- Item sprites (coin, mushroom, fire flower, star)
- Background tiles
- UI elements

Requirements: 4.7
"""

from pathlib import Path
from PIL import Image, ImageDraw


def create_directory_structure(base_path: Path) -> None:
    """Create the directory structure for Mario assets."""
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


def create_character_sprite(
    width: int,
    height: int,
    color: tuple,
    state: str
) -> Image.Image:
    """Create a character sprite placeholder.
    
    Args:
        width: Width of the sprite
        height: Height of the sprite
        color: RGB color tuple for the character
        state: Animation state (idle, run, jump, damage)
    
    Returns:
        PIL Image with the character sprite
    """
    img = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Draw body (rectangle)
    body_top = height // 4
    body_bottom = height - height // 6
    body_left = width // 4
    body_right = width - width // 4
    draw.rectangle([body_left, body_top, body_right, body_bottom], fill=color)
    
    # Draw head (circle)
    head_radius = width // 5
    head_center = (width // 2, body_top - head_radius // 2)
    draw.ellipse([
        head_center[0] - head_radius,
        head_center[1] - head_radius,
        head_center[0] + head_radius,
        head_center[1] + head_radius
    ], fill=(255, 200, 150, 255))  # Skin color
    
    # Add state-specific details
    if state == "run":
        # Add motion lines
        draw.line([(body_left - 5, body_top + 5), (body_left - 15, body_top + 5)], fill=(200, 200, 200, 200), width=2)
        draw.line([(body_left - 5, body_top + 15), (body_left - 12, body_top + 15)], fill=(200, 200, 200, 200), width=2)
    elif state == "jump":
        # Draw arms up
        draw.line([(body_left, body_top + 5), (body_left - 10, body_top - 10)], fill=color, width=3)
        draw.line([(body_right, body_top + 5), (body_right + 10, body_top - 10)], fill=color, width=3)
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
    
    return img


def create_coin_sprite(size: int) -> Image.Image:
    """Create a coin sprite placeholder.
    
    Args:
        size: Size of the sprite (width and height)
    
    Returns:
        PIL Image with the coin sprite
    """
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Draw golden coin (ellipse for 3D effect)
    margin = size // 8
    draw.ellipse([margin, margin // 2, size - margin, size - margin // 2], fill=(255, 215, 0, 255))
    
    # Add shine
    shine_x = size // 3
    shine_y = size // 3
    draw.ellipse([shine_x - 3, shine_y - 3, shine_x + 3, shine_y + 3], fill=(255, 255, 200, 255))
    
    # Add dollar sign or C
    center_x = size // 2
    center_y = size // 2
    draw.text((center_x - 4, center_y - 6), "C", fill=(200, 150, 0, 255))
    
    return img


def create_mushroom_sprite(size: int) -> Image.Image:
    """Create a mushroom power-up sprite placeholder.
    
    Args:
        size: Size of the sprite (width and height)
    
    Returns:
        PIL Image with the mushroom sprite
    """
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Draw stem (white rectangle)
    stem_width = size // 3
    stem_height = size // 3
    stem_left = (size - stem_width) // 2
    stem_top = size - stem_height - size // 8
    draw.rectangle([stem_left, stem_top, stem_left + stem_width, stem_top + stem_height], fill=(255, 255, 240, 255))
    
    # Draw cap (red dome)
    cap_margin = size // 8
    draw.ellipse([cap_margin, cap_margin, size - cap_margin, stem_top + size // 8], fill=(255, 0, 0, 255))
    
    # Add white spots
    spot_size = size // 10
    draw.ellipse([size // 4, size // 4, size // 4 + spot_size, size // 4 + spot_size], fill=(255, 255, 255, 255))
    draw.ellipse([size // 2, size // 5, size // 2 + spot_size, size // 5 + spot_size], fill=(255, 255, 255, 255))
    draw.ellipse([size * 2 // 3, size // 4, size * 2 // 3 + spot_size, size // 4 + spot_size], fill=(255, 255, 255, 255))
    
    return img


def create_fire_flower_sprite(size: int) -> Image.Image:
    """Create a fire flower power-up sprite placeholder.
    
    Args:
        size: Size of the sprite (width and height)
    
    Returns:
        PIL Image with the fire flower sprite
    """
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Draw stem (green)
    stem_width = size // 6
    stem_left = (size - stem_width) // 2
    stem_top = size // 2
    draw.rectangle([stem_left, stem_top, stem_left + stem_width, size - size // 8], fill=(0, 180, 0, 255))
    
    # Draw flower center (orange)
    center_x = size // 2
    center_y = size // 3
    center_radius = size // 6
    draw.ellipse([
        center_x - center_radius,
        center_y - center_radius,
        center_x + center_radius,
        center_y + center_radius
    ], fill=(255, 165, 0, 255))
    
    # Draw petals (red/orange)
    petal_radius = size // 5
    petal_positions = [
        (center_x, center_y - petal_radius),  # top
        (center_x + petal_radius, center_y),  # right
        (center_x, center_y + petal_radius),  # bottom
        (center_x - petal_radius, center_y),  # left
    ]
    for px, py in petal_positions:
        draw.ellipse([
            px - petal_radius // 2,
            py - petal_radius // 2,
            px + petal_radius // 2,
            py + petal_radius // 2
        ], fill=(255, 69, 0, 255))
    
    return img


def create_star_sprite(size: int) -> Image.Image:
    """Create a star power-up sprite placeholder.
    
    Args:
        size: Size of the sprite (width and height)
    
    Returns:
        PIL Image with the star sprite
    """
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Calculate star points
    import math
    center_x = size // 2
    center_y = size // 2
    outer_radius = size // 2 - size // 8
    inner_radius = outer_radius // 2
    
    points = []
    for i in range(10):
        angle = math.pi / 2 + i * math.pi / 5  # Start from top
        radius = outer_radius if i % 2 == 0 else inner_radius
        x = center_x + radius * math.cos(angle)
        y = center_y - radius * math.sin(angle)
        points.append((x, y))
    
    # Draw star (yellow)
    draw.polygon(points, fill=(255, 255, 0, 255), outline=(255, 200, 0, 255))
    
    # Add eyes
    eye_y = center_y - size // 10
    draw.ellipse([center_x - size // 6, eye_y - 2, center_x - size // 10, eye_y + 2], fill=(0, 0, 0, 255))
    draw.ellipse([center_x + size // 10, eye_y - 2, center_x + size // 6, eye_y + 2], fill=(0, 0, 0, 255))
    
    return img


def create_background_tile(size: int, tile_type: str) -> Image.Image:
    """Create a background tile placeholder.
    
    Args:
        size: Size of the tile (width and height)
        tile_type: Type of tile (sky, ground, brick, question_block)
    
    Returns:
        PIL Image with the background tile
    """
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    if tile_type == "sky":
        # Light blue sky
        draw.rectangle([0, 0, size, size], fill=(135, 206, 235, 255))
    elif tile_type == "ground":
        # Brown ground with texture
        draw.rectangle([0, 0, size, size], fill=(139, 69, 19, 255))
        # Add some texture lines
        for i in range(0, size, size // 4):
            draw.line([(0, i), (size, i)], fill=(100, 50, 10, 255), width=1)
    elif tile_type == "brick":
        # Red brick pattern
        draw.rectangle([0, 0, size, size], fill=(178, 34, 34, 255))
        # Draw brick lines
        draw.line([(0, size // 2), (size, size // 2)], fill=(100, 20, 20, 255), width=2)
        draw.line([(size // 2, 0), (size // 2, size // 2)], fill=(100, 20, 20, 255), width=2)
        draw.line([(0, size // 2), (0, size)], fill=(100, 20, 20, 255), width=2)
        draw.line([(size, size // 2), (size, size)], fill=(100, 20, 20, 255), width=2)
    elif tile_type == "question_block":
        # Yellow question block
        draw.rectangle([0, 0, size, size], fill=(255, 200, 0, 255))
        draw.rectangle([2, 2, size - 2, size - 2], fill=(255, 220, 50, 255))
        # Draw question mark
        center_x = size // 2
        draw.text((center_x - 4, size // 4), "?", fill=(255, 255, 255, 255))
    elif tile_type == "pipe":
        # Green pipe
        draw.rectangle([0, 0, size, size], fill=(0, 128, 0, 255))
        draw.rectangle([size // 8, 0, size - size // 8, size], fill=(0, 180, 0, 255))
        # Highlight
        draw.rectangle([size // 4, 0, size // 3, size], fill=(100, 220, 100, 255))
    
    return img


def create_ui_element(width: int, height: int, element_type: str) -> Image.Image:
    """Create a UI element placeholder.
    
    Args:
        width: Width of the element
        height: Height of the element
        element_type: Type of UI element (health_bar, coin_counter, level_indicator)
    
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
        # Add gradient effect
        draw.rectangle([0, 0, width, height // 3], fill=(255, 80, 80, 255))
    elif element_type == "coin_icon":
        # Small coin icon for counter
        return create_coin_sprite(min(width, height))
    elif element_type == "panel_bg":
        # Semi-transparent panel background
        draw.rectangle([0, 0, width, height], fill=(0, 0, 0, 180))
        draw.rectangle([2, 2, width - 2, height - 2], outline=(255, 255, 255, 100), width=2)
    
    return img


def main():
    """Generate all placeholder sprites for the Mario theme."""
    # Base path for Mario assets
    base_path = Path("assets/mario")
    
    # Create directory structure
    create_directory_structure(base_path)
    
    # Character sprite settings
    char_width = 32
    char_height = 48
    mario_color = (255, 0, 0, 255)  # Red for Mario
    
    # Create character sprites
    print("Creating character sprites...")
    states = ["idle", "run", "jump", "damage"]
    for state in states:
        sprite = create_character_sprite(char_width, char_height, mario_color, state)
        sprite.save(base_path / "characters" / f"mario_{state}.png")
        print(f"  Created mario_{state}.png")
    
    # Create item sprites (32x32)
    print("Creating item sprites...")
    item_size = 32
    
    coin = create_coin_sprite(item_size)
    coin.save(base_path / "items" / "coin.png")
    print("  Created coin.png")
    
    mushroom = create_mushroom_sprite(item_size)
    mushroom.save(base_path / "items" / "mushroom.png")
    print("  Created mushroom.png")
    
    fire_flower = create_fire_flower_sprite(item_size)
    fire_flower.save(base_path / "items" / "fire_flower.png")
    print("  Created fire_flower.png")
    
    star = create_star_sprite(item_size)
    star.save(base_path / "items" / "star.png")
    print("  Created star.png")
    
    # Create background tiles (32x32)
    print("Creating background tiles...")
    tile_size = 32
    tile_types = ["sky", "ground", "brick", "question_block", "pipe"]
    for tile_type in tile_types:
        tile = create_background_tile(tile_size, tile_type)
        tile.save(base_path / "backgrounds" / f"{tile_type}.png")
        print(f"  Created {tile_type}.png")
    
    # Create UI elements
    print("Creating UI elements...")
    
    health_bar_bg = create_ui_element(100, 20, "health_bar_bg")
    health_bar_bg.save(base_path / "ui" / "health_bar_bg.png")
    print("  Created health_bar_bg.png")
    
    health_bar_fill = create_ui_element(96, 16, "health_bar_fill")
    health_bar_fill.save(base_path / "ui" / "health_bar_fill.png")
    print("  Created health_bar_fill.png")
    
    coin_icon = create_ui_element(24, 24, "coin_icon")
    coin_icon.save(base_path / "ui" / "coin_icon.png")
    print("  Created coin_icon.png")
    
    panel_bg = create_ui_element(200, 100, "panel_bg")
    panel_bg.save(base_path / "ui" / "panel_bg.png")
    print("  Created panel_bg.png")
    
    print("\nAll Mario theme placeholder sprites created successfully!")
    print(f"Assets saved to: {base_path.absolute()}")


if __name__ == "__main__":
    main()
