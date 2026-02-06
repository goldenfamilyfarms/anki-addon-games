# Implementation Plan: NintendAnki

## Overview

This implementation plan breaks down the NintendAnki add-on into incremental coding tasks. Each task builds on previous work, ensuring no orphaned code. The plan prioritizes core functionality first, then theme-specific features, and finally polish and accessibility.

## Tasks

- [x] 1. Set up project foundation and data layer
  - [x] 1.1 Create data models and enums
    - Define Theme enum, ReviewResult, ProgressionState, ScoreResult, PenaltyResult dataclasses
    - Define Achievement, PowerUp, Level, Collectible, GameState dataclasses
    - Define GameConfig dataclass with all configurable settings
    - _Requirements: 2.1, 3.1, 8.3_
  
  - [x] 1.2 Implement DataManager with SQLite persistence
    - Create database schema (all tables from design)
    - Implement initialize_database(), save_state(), load_state()
    - Implement save_progression() for per-review persistence
    - Implement check_integrity() and create_backup()
    - _Requirements: 8.1, 8.2, 8.3, 8.4, 8.5_
  
  - [ ]* 1.3 Write property test for game state round-trip persistence
    - **Property 5: Game State Round-Trip Persistence**
    - **Validates: Requirements 2.6, 2.7, 8.3, 8.4**
  
  - [x] 1.4 Implement ConfigManager with JSON persistence
    - Implement load_config(), save_config(), reset_to_defaults()
    - Handle missing/corrupted config files gracefully
    - _Requirements: 12.8, 12.9_
  
  - [ ]* 1.5 Write property test for settings round-trip persistence
    - **Property 22: Settings Round-Trip Persistence**
    - **Validates: Requirements 12.8, 12.9**
  
  - [x] 1.6 Implement JSON export/import for backups
    - Implement export_to_json() and import_from_json()
    - _Requirements: 8.6, 8.7_
  
  - [ ]* 1.7 Write property test for JSON backup round-trip
    - **Property 15: JSON Backup Round-Trip**
    - **Validates: Requirements 8.6, 8.7**

- [x] 2. Checkpoint - Ensure data layer tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [x] 3. Implement core scoring and progression systems
  - [x] 3.1 Implement ScoringEngine
    - Implement calculate_score() with base points and multipliers
    - Implement get_combo_multiplier() with streak tiers (1.0/1.5/2.0/3.0)
    - Implement calculate_penalty() for wrong answers
    - _Requirements: 3.1, 3.2, 3.3, 3.4_
  
  - [ ]* 3.2 Write property test for combo multiplier calculation
    - **Property 6: Combo Multiplier Calculation**
    - **Validates: Requirements 3.3**
  
  - [ ]* 3.3 Write property test for scoring rules
    - **Property 7: Scoring Rules**
    - **Validates: Requirements 3.1, 3.2, 3.4**
  
  - [x] 3.4 Implement ProgressionSystem
    - Implement process_review() to update state on each review
    - Implement get_state() to retrieve current progression
    - Implement check_level_unlock() (every 50 correct answers)
    - Implement check_powerup_grant() (every 100 correct answers)
    - Implement reset_session() for health/session accuracy reset
    - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5, 3.5_
  
  - [ ]* 3.5 Write property test for progression invariants
    - **Property 3: Progression Invariants**
    - **Validates: Requirements 2.1, 2.2, 2.3**
  
  - [ ]* 3.6 Write property test for threshold-based unlocks
    - **Property 4: Threshold-Based Unlocks**
    - **Validates: Requirements 2.4, 2.5, 13.1**

- [x] 4. Implement reward and achievement systems
  - [x] 4.1 Implement RewardSystem
    - Implement add_currency(), spend_currency(), get_balance()
    - Implement get_shop_items() and unlock_item()
    - Define shop items (characters, cosmetics)
    - _Requirements: 11.1, 11.2, 11.3, 11.5, 11.6_
  
  - [ ]* 4.2 Write property test for currency balance updates
    - **Property 19: Currency Balance Updates**
    - **Validates: Requirements 11.1**
  
  - [ ]* 4.3 Write property test for reward unlocks
    - **Property 20: Reward Unlocks**
    - **Validates: Requirements 11.4, 11.5, 11.6**
  
  - [x] 4.4 Implement AchievementSystem
    - Define all achievements (cards reviewed, streaks, accuracy, levels, theme-specific)
    - Implement check_achievements() to detect newly unlocked achievements
    - Implement get_all_achievements() and get_progress()
    - _Requirements: 14.1, 14.2, 14.3, 14.4, 14.5, 14.6_
  
  - [ ]* 4.5 Write property test for achievement tracking and persistence
    - **Property 24: Achievement Tracking and Persistence**
    - **Validates: Requirements 14.1, 14.2, 14.4**

- [x] 5. Implement power-up and level systems
  - [x] 5.1 Implement PowerUpSystem
    - Implement grant_powerup() with theme-appropriate power-ups
    - Implement activate_powerup() and get_active_powerups()
    - Implement get_inventory() and tick() for duration tracking
    - _Requirements: 13.1, 13.2, 13.3, 13.4, 13.5, 13.6_
  
  - [ ]* 5.2 Write property test for power-up lifecycle
    - **Property 23: Power-Up Lifecycle**
    - **Validates: Requirements 13.3, 13.4, 13.6**
  
  - [x] 5.3 Implement LevelSystem
    - Implement unlock_level() and complete_level()
    - Implement get_available_levels() and get_level_progress()
    - Define level structures for each theme
    - _Requirements: 15.1, 15.2, 15.3, 15.4, 15.5, 15.6, 15.7_
  
  - [ ]* 5.4 Write property test for level tracking and rewards
    - **Property 25: Level Tracking and Rewards**
    - **Validates: Requirements 15.2, 15.5, 15.6**

- [x] 6. Checkpoint - Ensure core systems tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [x] 7. Implement theme management and base theme engine
  - [x] 7.1 Implement ThemeManager
    - Implement get_current_theme(), set_theme()
    - Implement get_theme_engine() to return appropriate engine
    - Persist theme selection to database
    - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5, 1.6_
  
  - [ ]* 7.2 Write property test for theme switching preserves progression
    - **Property 1: Theme Switching Preserves Progression**
    - **Validates: Requirements 1.3**
  
  - [ ]* 7.3 Write property test for theme selection round-trip persistence
    - **Property 2: Theme Selection Round-Trip Persistence**
    - **Validates: Requirements 1.5, 1.6**
  
  - [x] 7.4 Implement ThemeEngine abstract base class
    - Define abstract methods for animations, collectibles, level views, stats
    - Create Animation, Collectible, LevelView, ThemeStats dataclasses
    - _Requirements: 4.1, 5.1, 6.1_

- [x] 8. Implement Mario theme engine
  - [x] 8.1 Implement MarioEngine
    - Implement get_animation_for_correct() (coin collection)
    - Implement get_animation_for_wrong() (damage)
    - Implement get_powerup_for_accuracy() (mushroom/fire flower/star)
    - Implement get_level_selection_view()
    - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5, 4.6, 4.7, 4.8_
  
  - [ ]* 8.2 Write property test for Mario accuracy rewards
    - **Property 9: Mario Accuracy Rewards**
    - **Validates: Requirements 4.4, 4.5, 4.6**

- [x] 9. Implement Zelda theme engine
  - [x] 9.1 Implement ZeldaEngine
    - Implement get_animation_for_correct() (exploration)
    - Implement get_animation_for_wrong() (enemy damage)
    - Implement trigger_boss_battle() and complete_boss_battle()
    - Implement get_adventure_map(), get_equipped_item(), equip_item()
    - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5, 5.6, 5.7, 5.8_
  
  - [ ]* 9.2 Write property test for Zelda item categorization
    - **Property 10: Zelda Item Categorization**
    - **Validates: Requirements 5.6**
  
  - [ ]* 9.3 Write property test for Zelda item effects
    - **Property 11: Zelda Item Effects**
    - **Validates: Requirements 5.5, 5.7**

- [x] 10. Implement DKC theme engine
  - [x] 10.1 Implement DKCEngine
    - Implement get_animation_for_correct() (banana collection)
    - Implement get_animation_for_wrong() (banana loss)
    - Implement start_time_trial() and complete_time_trial()
    - Implement get_world_completion() and get_banana_count()
    - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5, 6.6, 6.7, 6.8_
  
  - [ ]* 10.2 Write property test for DKC time trial rewards
    - **Property 12: DKC Time Trial Rewards**
    - **Validates: Requirements 6.5**
  
  - [ ]* 10.3 Write property test for DKC world completion
    - **Property 13: DKC World Completion**
    - **Validates: Requirements 6.7**
  
  - [ ]* 10.4 Write property test for theme animation selection
    - **Property 8: Theme Animation Selection**
    - **Validates: Requirements 4.2, 4.3, 5.2, 5.3, 6.2, 6.3**

- [x] 11. Checkpoint - Ensure theme engine tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [x] 12. Implement Anki integration layer
  - [x] 12.1 Implement HookHandler
    - Implement register_hooks() to hook into Anki's reviewer
    - Implement on_card_reviewed() to process review events
    - Implement unregister_hooks() for clean shutdown
    - _Requirements: 7.1, 7.2, 7.3_
  
  - [ ]* 12.2 Write property test for background progress tracking
    - **Property 14: Background Progress Tracking**
    - **Validates: Requirements 7.5, 9.6**
  
  - [x] 12.3 Implement MenuIntegration
    - Implement setup_menu() to add Tools menu items
    - Implement setup_toolbar() to add toolbar button
    - _Requirements: 7.6, 7.7_

- [x] 13. Implement UI layer - Animation Engine
  - [x] 13.1 Implement AssetManager
    - Implement sprite sheet loading and caching
    - Implement asset path resolution for each theme
    - Handle missing assets gracefully with placeholders
    - _Requirements: 4.7, 9.2_
  
  - [x] 13.2 Implement AnimationEngine
    - Implement load_sprite_sheet() and create_animation()
    - Implement play_animation() and stop_animation()
    - Implement set_animation_speed() for customization
    - Target 30+ FPS rendering
    - _Requirements: 9.2, 9.3_

- [x] 14. Implement UI layer - Game Window
  - [x] 14.1 Implement GameWindow
    - Create PyQt QMainWindow with game display area
    - Implement show_animation() to play animations
    - Implement update_display() to show current state
    - Implement switch_theme() for theme transitions
    - _Requirements: 9.1, 9.3, 9.4_
  
  - [ ]* 14.2 Write property test for game window aspect ratio preservation
    - **Property 16: Game Window Aspect Ratio Preservation**
    - **Validates: Requirements 9.4**
  
  - [x] 14.3 Implement window position persistence
    - Implement save_position() and restore_position()
    - Implement minimize_to_tray()
    - _Requirements: 9.5, 9.6, 9.7_
  
  - [ ]* 14.4 Write property test for game window position persistence
    - **Property 17: Game Window Position Persistence**
    - **Validates: Requirements 9.5**

- [x] 15. Implement UI layer - Dashboard
  - [x] 15.1 Implement Dashboard
    - Create PyQt QDialog with tabbed interface
    - Implement stats tab (points, cards, streak, accuracy, levels)
    - Implement achievements tab with unlock status and dates
    - Implement power-ups tab with inventory display
    - Implement theme selector
    - _Requirements: 10.1, 10.2, 10.3, 10.4, 10.5, 10.6, 10.7_
  
  - [ ]* 15.2 Write property test for dashboard displays required information
    - **Property 18: Dashboard Displays Required Information**
    - **Validates: Requirements 10.2, 10.3, 10.4, 10.5**

- [x] 16. Implement UI layer - Settings Panel
  - [x] 16.1 Implement SettingsPanel
    - Create PyQt QDialog with settings categories
    - Implement difficulty settings (points, penalties)
    - Implement reward rate settings (multipliers, thresholds)
    - Implement animation settings (speed, enable/disable)
    - Implement accessibility settings (colorblind modes, sound)
    - _Requirements: 12.1, 12.2, 12.3, 12.4, 12.5, 12.6, 12.7_
  
  - [ ]* 16.2 Write property test for stats-only mode disables animations
    - **Property 21: Stats-Only Mode Disables Animations**
    - **Validates: Requirements 12.4**

- [x] 17. Checkpoint - Ensure UI tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [x] 18. Wire all components together
  - [x] 18.1 Create main add-on entry point
    - Initialize all managers and systems
    - Wire dependencies between components
    - Register Anki hooks on add-on load
    - _Requirements: 7.1, 7.2_
  
  - [x] 18.2 Implement event flow from review to UI
    - Connect HookHandler to ProgressionSystem and ScoringEngine
    - Connect ProgressionSystem to ThemeManager
    - Connect ThemeManager to GameWindow
    - _Requirements: 7.2, 7.4_
  
  - [x] 18.3 Implement real-time dashboard updates
    - Connect review events to Dashboard refresh
    - _Requirements: 10.7_

- [x] 19. Create placeholder assets
  - [x] 19.1 Create placeholder sprites for Mario theme
    - Character sprites (idle, run, jump, damage)
    - Item sprites (coin, mushroom, fire flower, star)
    - Background tiles
    - _Requirements: 4.7_
  
  - [x] 19.2 Create placeholder sprites for Zelda theme
    - Character sprites (idle, walk, attack, damage)
    - Item sprites (heart, sword, shield, key)
    - Map tiles
    - _Requirements: 5.8_
  
  - [x] 19.3 Create placeholder sprites for DKC theme
    - Character sprites (idle, run, collect, damage)
    - Collectible sprites (banana, barrel)
    - Jungle background tiles
    - _Requirements: 6.1_

- [x] 20. Final integration and polish
  - [x] 20.1 Write integration tests
    - Test full review cycle with all themes
    - Test theme switching during session
    - Test add-on load/unload cycle
    - _Requirements: 1.3, 7.3_
  
  - [x] 20.2 Create Anki add-on manifest
    - Create manifest.json with add-on metadata
    - Create __init__.py entry point
    - Package for Anki add-on distribution
    - _Requirements: 7.1_

- [x] 21. Final checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.

## Notes

- Tasks marked with `*` are optional and can be skipped for faster MVP
- Each task references specific requirements for traceability
- Checkpoints ensure incremental validation
- Property tests validate universal correctness properties using Hypothesis
- Unit tests validate specific examples and edge cases
- The implementation follows a bottom-up approach: data layer → core logic → themes → UI → integration
