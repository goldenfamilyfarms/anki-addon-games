"""
Tests for the AnimationEngine class.

This module contains unit tests for the AnimationEngine, testing:
- Animation creation from sprites
- Animation playback (play, pause, stop)
- Animation speed customization
- FPS targeting (30+ FPS requirement)
- Animation callbacks and events

Requirements: 9.2, 9.3
"""

import time
from unittest.mock import MagicMock

import pytest

from data.models import Animation, AnimationType, Theme
from ui.animation_engine import (
    AnimationEngine,
    AnimationEventType,
    AnimationSequence,
    AnimationState,
)
from ui.asset_manager import AssetManager, Sprite, SpriteSheet


# Fixtures

@pytest.fixture
def asset_manager():
    """Create an AssetManager instance for testing."""
    return AssetManager(assets_root="test_assets")


@pytest.fixture
def animation_engine(asset_manager):
    """Create an AnimationEngine instance for testing."""
    return AnimationEngine(asset_manager)


@pytest.fixture
def sample_sprites():
    """Create sample sprites for testing."""
    sprites = []
    for i in range(4):
        sprite = Sprite(
            image=f"frame_{i}",
            width=64,
            height=64,
            source_sheet="test_sheet.png",
            frame_index=i,
            is_placeholder=False
        )
        sprites.append(sprite)
    return sprites


@pytest.fixture
def sample_sprite_sheet():
    """Create a sample sprite sheet for testing."""
    return SpriteSheet(
        path="test_sheet.png",
        image="test_image_data",
        width=256,
        height=64,
        frame_width=64,
        frame_height=64,
        columns=4,
        rows=1,
        frame_count=4,
        is_placeholder=False
    )


# Test AnimationSequence

class TestAnimationSequence:
    """Tests for the AnimationSequence dataclass."""
    
    def test_create_animation_sequence(self, sample_sprites):
        """Test creating an animation sequence."""
        animation = AnimationSequence(
            id="test_animation",
            sprites=sample_sprites,
            fps=30,
            loop=False
        )
        
        assert animation.id == "test_animation"
        assert animation.frame_count == 4
        assert animation.fps == 30
        assert animation.loop is False
        assert animation.state == AnimationState.IDLE
        assert animation.current_frame == 0
    
    def test_frame_duration_calculation(self, sample_sprites):
        """Test that frame duration is calculated correctly."""
        animation = AnimationSequence(
            id="test",
            sprites=sample_sprites,
            fps=30
        )
        
        # At 30 FPS, each frame should be ~33.33ms
        assert animation.frame_duration_ms == pytest.approx(1000.0 / 30, rel=0.01)
    
    def test_total_duration_calculation(self, sample_sprites):
        """Test that total duration is calculated correctly."""
        animation = AnimationSequence(
            id="test",
            sprites=sample_sprites,
            fps=30
        )
        
        # 4 frames at 30 FPS = ~133.33ms
        expected_duration = (1000.0 / 30) * 4
        assert animation.total_duration_ms == pytest.approx(expected_duration, rel=0.01)
    
    def test_minimum_fps_enforcement(self, sample_sprites):
        """Test that FPS below 30 is adjusted to 30."""
        animation = AnimationSequence(
            id="test",
            sprites=sample_sprites,
            fps=15  # Below minimum
        )
        
        # Should be adjusted to 30
        assert animation.fps == 30
    
    def test_get_current_sprite(self, sample_sprites):
        """Test getting the current sprite."""
        animation = AnimationSequence(
            id="test",
            sprites=sample_sprites,
            fps=30
        )
        
        sprite = animation.get_current_sprite()
        assert sprite == sample_sprites[0]
        
        animation.current_frame = 2
        sprite = animation.get_current_sprite()
        assert sprite == sample_sprites[2]
    
    def test_get_current_sprite_empty(self):
        """Test getting current sprite with no sprites."""
        animation = AnimationSequence(
            id="test",
            sprites=[],
            fps=30
        )
        
        assert animation.get_current_sprite() is None
    
    def test_add_callback(self, sample_sprites):
        """Test adding a callback."""
        animation = AnimationSequence(
            id="test",
            sprites=sample_sprites,
            fps=30
        )
        
        callback = MagicMock()
        animation.add_callback(AnimationEventType.START, callback)
        
        assert AnimationEventType.START in animation.callbacks
        assert callback in animation.callbacks[AnimationEventType.START]
    
    def test_remove_callback(self, sample_sprites):
        """Test removing a callback."""
        animation = AnimationSequence(
            id="test",
            sprites=sample_sprites,
            fps=30
        )
        
        callback = MagicMock()
        animation.add_callback(AnimationEventType.START, callback)
        
        result = animation.remove_callback(AnimationEventType.START, callback)
        assert result is True
        assert callback not in animation.callbacks.get(AnimationEventType.START, [])
    
    def test_trigger_event(self, sample_sprites):
        """Test triggering an event."""
        animation = AnimationSequence(
            id="test",
            sprites=sample_sprites,
            fps=30
        )
        
        callback = MagicMock()
        animation.add_callback(AnimationEventType.START, callback)
        
        animation.trigger_event(AnimationEventType.START)
        
        callback.assert_called_once()


# Test AnimationEngine

class TestAnimationEngine:
    """Tests for the AnimationEngine class."""
    
    def test_create_engine(self, animation_engine):
        """Test creating an animation engine."""
        assert animation_engine is not None
        assert animation_engine._speed_multiplier == 1.0
        assert animation_engine._current_animation is None
    
    def test_create_animation(self, animation_engine, sample_sprites):
        """Test creating an animation from sprites."""
        animation = animation_engine.create_animation(
            sprites=sample_sprites,
            fps=30,
            loop=False
        )
        
        assert animation is not None
        assert animation.frame_count == 4
        assert animation.fps == 30
        assert animation.loop is False
    
    def test_create_animation_with_custom_id(self, animation_engine, sample_sprites):
        """Test creating an animation with a custom ID."""
        animation = animation_engine.create_animation(
            sprites=sample_sprites,
            fps=30,
            animation_id="custom_id"
        )
        
        assert animation.id == "custom_id"
    
    def test_create_animation_minimum_fps(self, animation_engine, sample_sprites):
        """Test that animations enforce minimum 30 FPS (Requirement 9.2)."""
        animation = animation_engine.create_animation(
            sprites=sample_sprites,
            fps=15  # Below minimum
        )
        
        # Should be adjusted to 30
        assert animation.fps == 30
    
    def test_play_animation(self, animation_engine, sample_sprites):
        """Test playing an animation."""
        animation = animation_engine.create_animation(
            sprites=sample_sprites,
            fps=30
        )
        
        # Mock the timer to avoid PyQt dependency
        animation_engine._start_timer = MagicMock()
        
        animation_engine.play_animation(animation)
        
        assert animation_engine._current_animation == animation
        assert animation.state == AnimationState.PLAYING
        assert animation.current_frame == 0
    
    def test_play_animation_response_time(self, animation_engine, sample_sprites):
        """Test that animation starts within 100ms (Requirement 9.3)."""
        animation = animation_engine.create_animation(
            sprites=sample_sprites,
            fps=30
        )
        
        # Mock the timer
        animation_engine._start_timer = MagicMock()
        
        start_time = time.perf_counter()
        animation_engine.play_animation(animation)
        elapsed_ms = (time.perf_counter() - start_time) * 1000
        
        # Should complete within 100ms
        assert elapsed_ms < 100
    
    def test_stop_animation(self, animation_engine, sample_sprites):
        """Test stopping an animation."""
        animation = animation_engine.create_animation(
            sprites=sample_sprites,
            fps=30
        )
        
        animation_engine._start_timer = MagicMock()
        animation_engine._stop_timer = MagicMock()
        
        animation_engine.play_animation(animation)
        animation_engine.stop_animation()
        
        assert animation_engine._current_animation is None
        assert animation.state == AnimationState.STOPPED
    
    def test_pause_animation(self, animation_engine, sample_sprites):
        """Test pausing an animation."""
        animation = animation_engine.create_animation(
            sprites=sample_sprites,
            fps=30
        )
        
        animation_engine._start_timer = MagicMock()
        animation_engine._stop_timer = MagicMock()
        
        animation_engine.play_animation(animation)
        animation_engine.pause_animation()
        
        assert animation.state == AnimationState.PAUSED
    
    def test_resume_animation(self, animation_engine, sample_sprites):
        """Test resuming a paused animation."""
        animation = animation_engine.create_animation(
            sprites=sample_sprites,
            fps=30
        )
        
        animation_engine._start_timer = MagicMock()
        animation_engine._stop_timer = MagicMock()
        
        animation_engine.play_animation(animation)
        animation_engine.pause_animation()
        animation_engine.resume_animation()
        
        assert animation.state == AnimationState.PLAYING
    
    def test_set_animation_speed(self, animation_engine):
        """Test setting animation speed."""
        animation_engine.set_animation_speed(2.0)
        assert animation_engine.get_animation_speed() == 2.0
        
        animation_engine.set_animation_speed(0.5)
        assert animation_engine.get_animation_speed() == 0.5
    
    def test_set_animation_speed_invalid(self, animation_engine):
        """Test that invalid speed raises error."""
        with pytest.raises(ValueError):
            animation_engine.set_animation_speed(0)
        
        with pytest.raises(ValueError):
            animation_engine.set_animation_speed(-1)
    
    def test_update_advances_frame(self, animation_engine, sample_sprites):
        """Test that update advances the animation frame."""
        animation = animation_engine.create_animation(
            sprites=sample_sprites,
            fps=30
        )
        
        animation_engine._start_timer = MagicMock()
        animation_engine.play_animation(animation)
        
        # Simulate time passing (one frame duration)
        frame_duration = animation.frame_duration_ms
        animation_engine.update(delta_time_ms=frame_duration)
        
        assert animation.current_frame == 1
    
    def test_update_completes_animation(self, animation_engine, sample_sprites):
        """Test that animation completes after all frames."""
        animation = animation_engine.create_animation(
            sprites=sample_sprites,
            fps=30,
            loop=False
        )
        
        animation_engine._start_timer = MagicMock()
        animation_engine._stop_timer = MagicMock()
        animation_engine.play_animation(animation)
        
        # Simulate time passing for all frames
        total_duration = animation.total_duration_ms
        animation_engine.update(delta_time_ms=total_duration + 100)
        
        assert animation.state == AnimationState.COMPLETED
        assert animation.current_frame == animation.frame_count - 1
    
    def test_update_loops_animation(self, animation_engine, sample_sprites):
        """Test that looping animation loops correctly."""
        animation = animation_engine.create_animation(
            sprites=sample_sprites,
            fps=30,
            loop=True
        )
        
        animation_engine._start_timer = MagicMock()
        animation_engine.play_animation(animation)
        
        # Simulate time passing for more than one cycle
        total_duration = animation.total_duration_ms
        animation_engine.update(delta_time_ms=total_duration + animation.frame_duration_ms)
        
        # Should have looped back
        assert animation.state == AnimationState.PLAYING
        assert animation.current_frame < animation.frame_count
    
    def test_animation_callbacks(self, animation_engine, sample_sprites):
        """Test that animation callbacks are triggered."""
        animation = animation_engine.create_animation(
            sprites=sample_sprites,
            fps=30
        )
        
        animation_engine._start_timer = MagicMock()
        animation_engine._stop_timer = MagicMock()
        
        on_complete = MagicMock()
        on_frame_change = MagicMock()
        
        animation_engine.play_animation(
            animation,
            on_complete=on_complete,
            on_frame_change=on_frame_change
        )
        
        # Advance one frame
        animation_engine.update(delta_time_ms=animation.frame_duration_ms)
        on_frame_change.assert_called()
        
        # Complete the animation
        animation_engine.update(delta_time_ms=animation.total_duration_ms)
        on_complete.assert_called()
    
    def test_speed_multiplier_affects_playback(self, animation_engine, sample_sprites):
        """Test that speed multiplier affects animation playback."""
        animation = animation_engine.create_animation(
            sprites=sample_sprites,
            fps=30
        )
        
        animation_engine._start_timer = MagicMock()
        animation_engine.set_animation_speed(2.0)  # Double speed
        animation_engine.play_animation(animation)
        
        # At 2x speed, half the time should advance one frame
        half_frame_duration = animation.frame_duration_ms / 2
        animation_engine.update(delta_time_ms=half_frame_duration)
        
        assert animation.current_frame == 1
    
    def test_is_playing(self, animation_engine, sample_sprites):
        """Test is_playing method."""
        animation = animation_engine.create_animation(
            sprites=sample_sprites,
            fps=30
        )
        
        animation_engine._start_timer = MagicMock()
        animation_engine._stop_timer = MagicMock()
        
        assert animation_engine.is_playing() is False
        
        animation_engine.play_animation(animation)
        assert animation_engine.is_playing() is True
        
        animation_engine.pause_animation()
        assert animation_engine.is_playing() is False
    
    def test_is_paused(self, animation_engine, sample_sprites):
        """Test is_paused method."""
        animation = animation_engine.create_animation(
            sprites=sample_sprites,
            fps=30
        )
        
        animation_engine._start_timer = MagicMock()
        animation_engine._stop_timer = MagicMock()
        
        assert animation_engine.is_paused() is False
        
        animation_engine.play_animation(animation)
        assert animation_engine.is_paused() is False
        
        animation_engine.pause_animation()
        assert animation_engine.is_paused() is True
    
    def test_get_animation(self, animation_engine, sample_sprites):
        """Test retrieving a registered animation."""
        animation = animation_engine.create_animation(
            sprites=sample_sprites,
            fps=30,
            animation_id="test_anim"
        )
        
        retrieved = animation_engine.get_animation("test_anim")
        assert retrieved == animation
        
        assert animation_engine.get_animation("nonexistent") is None
    
    def test_remove_animation(self, animation_engine, sample_sprites):
        """Test removing a registered animation."""
        animation = animation_engine.create_animation(
            sprites=sample_sprites,
            fps=30,
            animation_id="test_anim"
        )
        
        result = animation_engine.remove_animation("test_anim")
        assert result is True
        assert animation_engine.get_animation("test_anim") is None
        
        result = animation_engine.remove_animation("nonexistent")
        assert result is False
    
    def test_clear_animations(self, animation_engine, sample_sprites):
        """Test clearing all animations."""
        animation_engine.create_animation(
            sprites=sample_sprites,
            fps=30,
            animation_id="anim1"
        )
        animation_engine.create_animation(
            sprites=sample_sprites,
            fps=30,
            animation_id="anim2"
        )
        
        animation_engine.clear_animations()
        
        assert animation_engine.get_animation("anim1") is None
        assert animation_engine.get_animation("anim2") is None
    
    def test_get_current_frame(self, animation_engine, sample_sprites):
        """Test getting current frame index."""
        animation = animation_engine.create_animation(
            sprites=sample_sprites,
            fps=30
        )
        
        assert animation_engine.get_current_frame() == -1
        
        animation_engine._start_timer = MagicMock()
        animation_engine.play_animation(animation)
        
        assert animation_engine.get_current_frame() == 0
    
    def test_get_frame_count(self, animation_engine, sample_sprites):
        """Test getting frame count."""
        animation = animation_engine.create_animation(
            sprites=sample_sprites,
            fps=30
        )
        
        assert animation_engine.get_frame_count() == 0
        
        animation_engine._start_timer = MagicMock()
        animation_engine.play_animation(animation)
        
        assert animation_engine.get_frame_count() == 4
    
    def test_get_animation_state(self, animation_engine, sample_sprites):
        """Test getting animation state."""
        animation = animation_engine.create_animation(
            sprites=sample_sprites,
            fps=30
        )
        
        assert animation_engine.get_animation_state() is None
        
        animation_engine._start_timer = MagicMock()
        animation_engine.play_animation(animation)
        
        assert animation_engine.get_animation_state() == AnimationState.PLAYING
    
    def test_performance_stats(self, animation_engine, sample_sprites):
        """Test getting performance statistics."""
        animation = animation_engine.create_animation(
            sprites=sample_sprites,
            fps=30
        )
        
        animation_engine._start_timer = MagicMock()
        animation_engine.play_animation(animation)
        
        # Simulate some updates
        for _ in range(10):
            animation_engine.update(delta_time_ms=33.33)
        
        stats = animation_engine.get_performance_stats()
        
        assert "current_fps" in stats
        assert "target_fps" in stats
        assert "speed_multiplier" in stats
        assert stats["target_fps"] == 30


class TestAnimationEngineWithAnimationModel:
    """Tests for AnimationEngine with Animation model integration."""
    
    def test_create_animation_from_model(self, animation_engine):
        """Test creating animation from Animation model."""
        # Create an Animation model
        animation_model = Animation(
            type=AnimationType.COLLECT,
            theme=Theme.MARIO,
            sprite_sheet="mario/characters/mario_run.png",
            frames=[0, 1, 2, 3],
            fps=30,
            loop=True
        )
        
        # The asset manager will return a placeholder since the file doesn't exist
        animation_seq = animation_engine.create_animation_from_model(animation_model)
        
        assert animation_seq is not None
        assert animation_seq.fps == 30
        assert animation_seq.loop is True
    
    def test_play_animation_model_directly(self, animation_engine):
        """Test playing an Animation model directly."""
        animation_model = Animation(
            type=AnimationType.DAMAGE,
            theme=Theme.ZELDA,
            sprite_sheet="zelda/characters/link_damage.png",
            frames=[0, 1],
            fps=30,
            loop=False
        )
        
        animation_engine._start_timer = MagicMock()
        
        # Should convert model to sequence and play
        animation_engine.play_animation(animation_model)
        
        assert animation_engine.is_playing()


class TestAnimationEngineEdgeCases:
    """Tests for edge cases and error handling."""
    
    def test_stop_when_not_playing(self, animation_engine):
        """Test stopping when no animation is playing."""
        # Should not raise an error
        animation_engine.stop_animation()
        assert animation_engine._current_animation is None
    
    def test_pause_when_not_playing(self, animation_engine, sample_sprites):
        """Test pausing when no animation is playing."""
        animation_engine.pause_animation()
        # Should not raise an error
    
    def test_resume_when_not_paused(self, animation_engine, sample_sprites):
        """Test resuming when not paused."""
        anim = animation_engine.create_animation(
            sprites=sample_sprites,
            fps=30
        )
        
        animation_engine._start_timer = MagicMock()
        animation_engine.play_animation(anim)
        
        # Resume when playing (not paused) should do nothing
        animation_engine.resume_animation()
        assert anim.state == AnimationState.PLAYING
    
    def test_update_when_not_playing(self, animation_engine):
        """Test update when no animation is playing."""
        result = animation_engine.update(delta_time_ms=33.33)
        assert result is None
    
    def test_empty_sprites_animation(self, animation_engine):
        """Test creating animation with empty sprites list."""
        animation = animation_engine.create_animation(
            sprites=[],
            fps=30
        )
        
        assert animation.frame_count == 0
        assert animation.get_current_sprite() is None
    
    def test_single_sprite_animation(self, animation_engine):
        """Test animation with single sprite."""
        sprite = Sprite(
            image="single_frame",
            width=64,
            height=64
        )
        
        animation = animation_engine.create_animation(
            sprites=[sprite],
            fps=30
        )
        
        assert animation.frame_count == 1
        assert animation.get_current_sprite() == sprite
    
    def test_play_replaces_current_animation(self, animation_engine, sample_sprites):
        """Test that playing a new animation stops the current one."""
        animation1 = animation_engine.create_animation(
            sprites=sample_sprites,
            fps=30,
            animation_id="anim1"
        )
        animation2 = animation_engine.create_animation(
            sprites=sample_sprites,
            fps=30,
            animation_id="anim2"
        )
        
        animation_engine._start_timer = MagicMock()
        animation_engine._stop_timer = MagicMock()
        
        animation_engine.play_animation(animation1)
        animation_engine.play_animation(animation2)
        
        assert animation_engine._current_animation == animation2
        assert animation1.state == AnimationState.STOPPED
