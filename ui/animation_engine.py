"""
AnimationEngine for NintendAnki.

This module implements the AnimationEngine class that handles sprite animations
and rendering for the game window. It supports creating animations from sprite
sequences, playing animations with configurable FPS (targeting 30+ FPS), and
managing animation lifecycle (play, pause, stop).

Requirements: 9.2, 9.3
"""

import logging
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Callable, Dict, List, Optional, Union

from data.models import Animation
from ui.asset_manager import AssetManager, Sprite, SpriteSheet


# Configure logging
logger = logging.getLogger(__name__)


class AnimationState(str, Enum):
    """State of an animation."""
    IDLE = "idle"
    PLAYING = "playing"
    PAUSED = "paused"
    STOPPED = "stopped"
    COMPLETED = "completed"


class AnimationEventType(str, Enum):
    """Types of animation events for callbacks."""
    START = "start"
    FRAME_CHANGE = "frame_change"
    LOOP = "loop"
    PAUSE = "pause"
    RESUME = "resume"
    STOP = "stop"
    COMPLETE = "complete"


@dataclass
class AnimationSequence:
    """Represents an animation sequence created from sprites.
    
    This is the internal representation of an animation that can be played
    by the AnimationEngine. It contains all the sprites and timing information
    needed to render the animation.
    
    Attributes:
        id: Unique identifier for this animation sequence
        sprites: List of sprites that make up the animation frames
        fps: Target frames per second (minimum 30 for smooth animation)
        frame_duration_ms: Duration of each frame in milliseconds
        loop: Whether the animation should loop
        current_frame: Current frame index
        state: Current state of the animation
        elapsed_time_ms: Time elapsed since animation started
        total_duration_ms: Total duration of one animation cycle
        callbacks: Dictionary of event callbacks
    """
    id: str
    sprites: List[Sprite]
    fps: int = 30
    frame_duration_ms: float = field(init=False)
    loop: bool = False
    current_frame: int = 0
    state: AnimationState = AnimationState.IDLE
    elapsed_time_ms: float = 0.0
    total_duration_ms: float = field(init=False)
    callbacks: Dict[AnimationEventType, List[Callable]] = field(default_factory=dict)
    
    def __post_init__(self):
        """Calculate frame duration and total duration."""
        # Ensure minimum 30 FPS for smooth animation (Requirement 9.2)
        if self.fps < 30:
            logger.warning(f"FPS {self.fps} is below minimum 30, adjusting to 30")
            self.fps = 30
        
        self.frame_duration_ms = 1000.0 / self.fps
        self.total_duration_ms = self.frame_duration_ms * len(self.sprites) if self.sprites else 0
    
    @property
    def frame_count(self) -> int:
        """Get the total number of frames in the animation."""
        return len(self.sprites)
    
    def get_current_sprite(self) -> Optional[Sprite]:
        """Get the sprite for the current frame."""
        if not self.sprites or self.current_frame >= len(self.sprites):
            return None
        return self.sprites[self.current_frame]
    
    def add_callback(self, event_type: AnimationEventType, callback: Callable) -> None:
        """Add a callback for an animation event.
        
        Args:
            event_type: Type of event to listen for
            callback: Function to call when event occurs
        """
        if event_type not in self.callbacks:
            self.callbacks[event_type] = []
        self.callbacks[event_type].append(callback)
    
    def remove_callback(self, event_type: AnimationEventType, callback: Callable) -> bool:
        """Remove a callback for an animation event.
        
        Args:
            event_type: Type of event
            callback: Function to remove
            
        Returns:
            True if callback was found and removed
        """
        if event_type in self.callbacks and callback in self.callbacks[event_type]:
            self.callbacks[event_type].remove(callback)
            return True
        return False
    
    def trigger_event(self, event_type: AnimationEventType, **kwargs) -> None:
        """Trigger callbacks for an event.
        
        Args:
            event_type: Type of event to trigger
            **kwargs: Additional arguments to pass to callbacks
        """
        if event_type in self.callbacks:
            for callback in self.callbacks[event_type]:
                try:
                    callback(self, event_type, **kwargs)
                except Exception as e:
                    logger.error(f"Animation callback error: {e}")


class AnimationEngine:
    """Handles sprite animations and rendering.
    
    The AnimationEngine provides a centralized interface for creating and
    playing sprite animations. It supports:
    - Loading sprite sheets and creating animations from sprite sequences
    - Playing animations with configurable FPS (targeting 30+ FPS)
    - Animation speed multipliers for customization
    - Animation lifecycle management (play, pause, stop)
    - Callbacks for animation events (start, frame change, complete)
    
    Requirements: 9.2, 9.3
    
    Attributes:
        asset_manager: AssetManager for loading sprite sheets
        _current_animation: Currently playing animation
        _speed_multiplier: Animation speed multiplier (1.0 = normal)
        _animations: Dictionary of created animations by ID
        _timer: Timer for animation updates
        _last_update_time: Time of last animation update
        _target_widget: Widget to render animation on
    
    Example:
        >>> engine = AnimationEngine(asset_manager)
        >>> sheet = engine.load_sprite_sheet("mario/characters/mario_run.png")
        >>> sprites = asset_manager.get_sprites(sheet)
        >>> animation = engine.create_animation(sprites, fps=30)
        >>> engine.play_animation(animation, target_widget)
    """
    
    # Minimum FPS for smooth animation (Requirement 9.2)
    MIN_FPS = 30
    
    # Maximum response time for animation start (Requirement 9.3)
    MAX_RESPONSE_TIME_MS = 100
    
    # Default animation settings
    DEFAULT_FPS = 30
    DEFAULT_SPEED = 1.0
    
    def __init__(self, asset_manager: AssetManager):
        """Initialize the AnimationEngine.
        
        Args:
            asset_manager: AssetManager instance for loading sprite sheets
        """
        self.asset_manager = asset_manager
        
        # Current animation state
        self._current_animation: Optional[AnimationSequence] = None
        self._speed_multiplier: float = self.DEFAULT_SPEED
        
        # Animation registry
        self._animations: Dict[str, AnimationSequence] = {}
        self._animation_counter: int = 0
        
        # Timing
        self._last_update_time: float = 0.0
        self._timer = None  # Will be set when using PyQt timer
        self._target_widget = None
        
        # Performance tracking
        self._frame_times: List[float] = []
        self._max_frame_samples = 60
        
        logger.debug("AnimationEngine initialized")
    
    def load_sprite_sheet(self, path: str, **kwargs) -> SpriteSheet:
        """Load a sprite sheet from file.
        
        Delegates to the AssetManager to load and cache sprite sheets.
        
        Args:
            path: Path to the sprite sheet file
            **kwargs: Additional arguments passed to AssetManager.load_sprite_sheet
        
        Returns:
            SpriteSheet object containing the loaded image and metadata
        
        Requirements: 9.2
        """
        return self.asset_manager.load_sprite_sheet(path, **kwargs)
    
    def create_animation(
        self,
        sprites: List[Sprite],
        fps: int = DEFAULT_FPS,
        loop: bool = False,
        animation_id: Optional[str] = None
    ) -> AnimationSequence:
        """Create an animation from sprites.
        
        Creates an AnimationSequence from a list of sprites with the specified
        frame rate. The animation can be configured to loop or play once.
        
        Args:
            sprites: List of Sprite objects that make up the animation frames
            fps: Target frames per second (minimum 30 for smooth animation)
            loop: Whether the animation should loop
            animation_id: Optional custom ID for the animation
        
        Returns:
            AnimationSequence object ready to be played
        
        Requirements: 9.2
        """
        # Ensure minimum FPS (Requirement 9.2)
        if fps < self.MIN_FPS:
            logger.warning(f"Requested FPS {fps} is below minimum {self.MIN_FPS}, using {self.MIN_FPS}")
            fps = self.MIN_FPS
        
        # Generate animation ID if not provided
        if animation_id is None:
            self._animation_counter += 1
            animation_id = f"animation_{self._animation_counter}"
        
        # Create the animation sequence
        animation = AnimationSequence(
            id=animation_id,
            sprites=sprites,
            fps=fps,
            loop=loop
        )
        
        # Register the animation
        self._animations[animation_id] = animation
        
        logger.debug(f"Created animation '{animation_id}' with {len(sprites)} frames at {fps} FPS")
        
        return animation
    
    def create_animation_from_sheet(
        self,
        sprite_sheet: SpriteSheet,
        frame_indices: Optional[List[int]] = None,
        fps: int = DEFAULT_FPS,
        loop: bool = False,
        animation_id: Optional[str] = None
    ) -> AnimationSequence:
        """Create an animation directly from a sprite sheet.
        
        Convenience method that extracts sprites from a sheet and creates
        an animation in one step.
        
        Args:
            sprite_sheet: SpriteSheet to extract frames from
            frame_indices: List of frame indices to use (None = all frames)
            fps: Target frames per second
            loop: Whether the animation should loop
            animation_id: Optional custom ID for the animation
        
        Returns:
            AnimationSequence object ready to be played
        """
        sprites = self.asset_manager.get_sprites(sprite_sheet, frame_indices)
        return self.create_animation(sprites, fps, loop, animation_id)
    
    def create_animation_from_model(
        self,
        animation_model: Animation,
        animation_id: Optional[str] = None
    ) -> AnimationSequence:
        """Create an animation from an Animation model.
        
        Creates an AnimationSequence from the Animation dataclass used
        throughout the application.
        
        Args:
            animation_model: Animation dataclass with sprite sheet and frame info
            animation_id: Optional custom ID for the animation
        
        Returns:
            AnimationSequence object ready to be played
        """
        # Load the sprite sheet
        sprite_sheet = self.load_sprite_sheet(animation_model.sprite_sheet)
        
        # Get frame indices from the model, or use all frames
        frame_indices = animation_model.frames if animation_model.frames else None
        
        return self.create_animation_from_sheet(
            sprite_sheet=sprite_sheet,
            frame_indices=frame_indices,
            fps=animation_model.fps,
            loop=animation_model.loop,
            animation_id=animation_id
        )
    
    def play_animation(
        self,
        animation: Union[AnimationSequence, Animation],
        target=None,
        on_complete: Optional[Callable] = None,
        on_frame_change: Optional[Callable] = None
    ) -> None:
        """Play an animation on a target widget.
        
        Starts playing the specified animation. If another animation is
        currently playing, it will be stopped first. The animation must
        start within 100ms of being called (Requirement 9.3).
        
        Args:
            animation: AnimationSequence or Animation model to play
            target: QWidget to render the animation on (optional)
            on_complete: Callback when animation completes
            on_frame_change: Callback when frame changes
        
        Requirements: 9.3
        """
        start_time = time.perf_counter()
        
        # Convert Animation model to AnimationSequence if needed
        if isinstance(animation, Animation):
            animation = self.create_animation_from_model(animation)
        
        # Stop any currently playing animation
        if self._current_animation and self._current_animation.state == AnimationState.PLAYING:
            self.stop_animation()
        
        # Set up the animation
        self._current_animation = animation
        self._target_widget = target
        
        # Reset animation state
        animation.current_frame = 0
        animation.elapsed_time_ms = 0.0
        animation.state = AnimationState.PLAYING
        
        # Add callbacks if provided
        if on_complete:
            animation.add_callback(AnimationEventType.COMPLETE, 
                                   lambda anim, evt, **kw: on_complete())
        if on_frame_change:
            animation.add_callback(AnimationEventType.FRAME_CHANGE,
                                   lambda anim, evt, **kw: on_frame_change(anim.current_frame))
        
        # Record start time
        self._last_update_time = time.perf_counter() * 1000
        
        # Start the timer for animation updates
        self._start_timer()
        
        # Trigger start event
        animation.trigger_event(AnimationEventType.START)
        
        # Verify response time (Requirement 9.3)
        elapsed_ms = (time.perf_counter() - start_time) * 1000
        if elapsed_ms > self.MAX_RESPONSE_TIME_MS:
            logger.warning(f"Animation start took {elapsed_ms:.1f}ms, exceeds {self.MAX_RESPONSE_TIME_MS}ms target")
        else:
            logger.debug(f"Animation started in {elapsed_ms:.1f}ms")
    
    def stop_animation(self) -> None:
        """Stop the current animation.
        
        Stops the currently playing animation and resets its state.
        """
        if self._current_animation is None:
            return
        
        # Stop the timer
        self._stop_timer()
        
        # Update state
        self._current_animation.state = AnimationState.STOPPED
        
        # Trigger stop event
        self._current_animation.trigger_event(AnimationEventType.STOP)
        
        logger.debug(f"Animation '{self._current_animation.id}' stopped")
        
        self._current_animation = None
        self._target_widget = None
    
    def pause_animation(self) -> None:
        """Pause the current animation.
        
        Pauses the animation at the current frame. Can be resumed with
        resume_animation().
        """
        if self._current_animation is None:
            return
        
        if self._current_animation.state != AnimationState.PLAYING:
            return
        
        # Stop the timer but keep state
        self._stop_timer()
        
        self._current_animation.state = AnimationState.PAUSED
        self._current_animation.trigger_event(AnimationEventType.PAUSE)
        
        logger.debug(f"Animation '{self._current_animation.id}' paused at frame {self._current_animation.current_frame}")
    
    def resume_animation(self) -> None:
        """Resume a paused animation.
        
        Resumes playing from the current frame.
        """
        if self._current_animation is None:
            return
        
        if self._current_animation.state != AnimationState.PAUSED:
            return
        
        self._current_animation.state = AnimationState.PLAYING
        self._last_update_time = time.perf_counter() * 1000
        
        # Restart the timer
        self._start_timer()
        
        self._current_animation.trigger_event(AnimationEventType.RESUME)
        
        logger.debug(f"Animation '{self._current_animation.id}' resumed")
    
    def set_animation_speed(self, speed: float) -> None:
        """Set animation speed multiplier.
        
        Adjusts the playback speed of animations. A speed of 1.0 is normal,
        2.0 is double speed, 0.5 is half speed.
        
        Args:
            speed: Speed multiplier (must be > 0)
        
        Raises:
            ValueError: If speed is not positive
        """
        if speed <= 0:
            raise ValueError(f"Animation speed must be positive, got {speed}")
        
        self._speed_multiplier = speed
        logger.debug(f"Animation speed set to {speed}x")
    
    def get_animation_speed(self) -> float:
        """Get the current animation speed multiplier.
        
        Returns:
            Current speed multiplier
        """
        return self._speed_multiplier
    
    def update(self, delta_time_ms: Optional[float] = None) -> Optional[Sprite]:
        """Update the animation state.
        
        Advances the animation based on elapsed time and returns the
        current sprite to render. This method should be called regularly
        (e.g., from a timer) to update the animation.
        
        Args:
            delta_time_ms: Time elapsed since last update in milliseconds.
                          If None, calculates from system time.
        
        Returns:
            Current Sprite to render, or None if no animation is playing
        """
        if self._current_animation is None:
            return None
        
        if self._current_animation.state != AnimationState.PLAYING:
            return self._current_animation.get_current_sprite()
        
        # Calculate delta time if not provided
        current_time = time.perf_counter() * 1000
        if delta_time_ms is None:
            delta_time_ms = current_time - self._last_update_time
        self._last_update_time = current_time
        
        # Apply speed multiplier
        adjusted_delta = delta_time_ms * self._speed_multiplier
        
        # Track frame time for performance monitoring
        self._track_frame_time(delta_time_ms)
        
        # Update elapsed time
        animation = self._current_animation
        animation.elapsed_time_ms += adjusted_delta
        
        # Calculate new frame
        old_frame = animation.current_frame
        new_frame = int(animation.elapsed_time_ms / animation.frame_duration_ms)
        
        # Handle animation completion
        if new_frame >= animation.frame_count:
            if animation.loop:
                # Loop the animation
                animation.elapsed_time_ms %= animation.total_duration_ms
                new_frame = int(animation.elapsed_time_ms / animation.frame_duration_ms)
                animation.trigger_event(AnimationEventType.LOOP)
            else:
                # Animation complete
                new_frame = animation.frame_count - 1
                animation.state = AnimationState.COMPLETED
                animation.trigger_event(AnimationEventType.COMPLETE)
                self._stop_timer()
        
        # Update frame and trigger event if changed
        if new_frame != old_frame:
            animation.current_frame = new_frame
            animation.trigger_event(AnimationEventType.FRAME_CHANGE, frame=new_frame)
            
            # Update target widget if available
            self._render_frame()
        
        return animation.get_current_sprite()
    
    def _render_frame(self) -> None:
        """Render the current frame to the target widget."""
        if self._target_widget is None or self._current_animation is None:
            return
        
        sprite = self._current_animation.get_current_sprite()
        if sprite is None:
            return
        
        # Try to render using PyQt
        try:
            self._render_pyqt(sprite)
        except Exception as e:
            logger.debug(f"PyQt render failed: {e}")
    
    def _render_pyqt(self, sprite: Sprite) -> None:
        """Render a sprite using PyQt.
        
        Args:
            sprite: Sprite to render
        """
        if self._target_widget is None:
            return
        
        # Try PyQt6 first
        try:
            from PyQt6.QtGui import QPixmap
            from PyQt6.QtWidgets import QLabel
            
            if isinstance(sprite.image, QPixmap) and isinstance(self._target_widget, QLabel):
                self._target_widget.setPixmap(sprite.image)
                return
        except ImportError:
            pass
        
        # Try PyQt5
        try:
            from PyQt5.QtGui import QPixmap
            from PyQt5.QtWidgets import QLabel
            
            if isinstance(sprite.image, QPixmap) and isinstance(self._target_widget, QLabel):
                self._target_widget.setPixmap(sprite.image)
                return
        except ImportError:
            pass
    
    def _start_timer(self) -> None:
        """Start the animation timer."""
        # Calculate timer interval for target FPS
        if self._current_animation is None:
            return
        
        interval_ms = int(self._current_animation.frame_duration_ms / self._speed_multiplier)
        
        # Try to use PyQt timer
        try:
            self._start_pyqt_timer(interval_ms)
            return
        except Exception as e:
            logger.debug(f"PyQt timer not available: {e}")
        
        # Fallback: no automatic timer, manual update() calls required
        logger.debug("No timer available, manual update() calls required")
    
    def _start_pyqt_timer(self, interval_ms: int) -> None:
        """Start a PyQt timer for animation updates.
        
        Args:
            interval_ms: Timer interval in milliseconds
        """
        # Try PyQt6
        try:
            from PyQt6.QtCore import QTimer
            
            if self._timer is None:
                self._timer = QTimer()
                self._timer.timeout.connect(self.update)
            
            self._timer.start(interval_ms)
            logger.debug(f"Started PyQt6 timer with {interval_ms}ms interval")
            return
        except ImportError:
            pass
        
        # Try PyQt5
        try:
            from PyQt5.QtCore import QTimer
            
            if self._timer is None:
                self._timer = QTimer()
                self._timer.timeout.connect(self.update)
            
            self._timer.start(interval_ms)
            logger.debug(f"Started PyQt5 timer with {interval_ms}ms interval")
            return
        except ImportError:
            pass
        
        raise RuntimeError("No PyQt timer available")
    
    def _stop_timer(self) -> None:
        """Stop the animation timer."""
        if self._timer is not None:
            try:
                self._timer.stop()
            except Exception as e:
                logger.debug(f"Error stopping timer: {e}")
    
    def _track_frame_time(self, delta_time_ms: float) -> None:
        """Track frame time for performance monitoring.
        
        Args:
            delta_time_ms: Time since last frame in milliseconds
        """
        self._frame_times.append(delta_time_ms)
        if len(self._frame_times) > self._max_frame_samples:
            self._frame_times.pop(0)
    
    def get_current_fps(self) -> float:
        """Get the current actual FPS based on frame times.
        
        Returns:
            Current FPS, or 0 if no data available
        """
        if not self._frame_times:
            return 0.0
        
        avg_frame_time = sum(self._frame_times) / len(self._frame_times)
        if avg_frame_time <= 0:
            return 0.0
        
        return 1000.0 / avg_frame_time
    
    def get_animation_state(self) -> Optional[AnimationState]:
        """Get the state of the current animation.
        
        Returns:
            Current animation state, or None if no animation
        """
        if self._current_animation is None:
            return None
        return self._current_animation.state
    
    def get_current_frame(self) -> int:
        """Get the current frame index.
        
        Returns:
            Current frame index, or -1 if no animation
        """
        if self._current_animation is None:
            return -1
        return self._current_animation.current_frame
    
    def get_frame_count(self) -> int:
        """Get the total frame count of the current animation.
        
        Returns:
            Total frame count, or 0 if no animation
        """
        if self._current_animation is None:
            return 0
        return self._current_animation.frame_count
    
    def get_animation(self, animation_id: str) -> Optional[AnimationSequence]:
        """Get a registered animation by ID.
        
        Args:
            animation_id: ID of the animation to retrieve
        
        Returns:
            AnimationSequence if found, None otherwise
        """
        return self._animations.get(animation_id)
    
    def remove_animation(self, animation_id: str) -> bool:
        """Remove a registered animation.
        
        Args:
            animation_id: ID of the animation to remove
        
        Returns:
            True if animation was found and removed
        """
        if animation_id in self._animations:
            # Stop if it's the current animation
            if (self._current_animation and 
                self._current_animation.id == animation_id):
                self.stop_animation()
            
            del self._animations[animation_id]
            return True
        return False
    
    def clear_animations(self) -> None:
        """Clear all registered animations."""
        self.stop_animation()
        self._animations.clear()
        self._animation_counter = 0
        logger.debug("All animations cleared")
    
    def is_playing(self) -> bool:
        """Check if an animation is currently playing.
        
        Returns:
            True if an animation is playing
        """
        return (self._current_animation is not None and 
                self._current_animation.state == AnimationState.PLAYING)
    
    def is_paused(self) -> bool:
        """Check if an animation is currently paused.
        
        Returns:
            True if an animation is paused
        """
        return (self._current_animation is not None and 
                self._current_animation.state == AnimationState.PAUSED)
    
    def get_performance_stats(self) -> Dict[str, float]:
        """Get animation performance statistics.
        
        Returns:
            Dictionary with performance metrics
        """
        current_fps = self.get_current_fps()
        target_fps = self._current_animation.fps if self._current_animation else self.DEFAULT_FPS
        
        return {
            "current_fps": current_fps,
            "target_fps": target_fps,
            "speed_multiplier": self._speed_multiplier,
            "frame_count": len(self._frame_times),
            "avg_frame_time_ms": sum(self._frame_times) / len(self._frame_times) if self._frame_times else 0,
            "meets_target": current_fps >= self.MIN_FPS
        }
