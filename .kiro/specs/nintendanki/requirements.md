# Requirements Document

## Introduction

NintendAnki is an Anki desktop add-on that gamifies the study experience with three selectable Nintendo-inspired game themes: Mario-style (side-scrolling/coins), Zelda-style (exploration/bosses), and DKC (Donkey Kong Country)-style (collectibles/time trials). The add-on provides a unified progression system across all Anki decks, allowing users to switch themes at any time without losing progress. The goal is to increase study motivation through engaging game mechanics, visual feedback, and meaningful rewards.

## Glossary

- **Add-on**: A Python plugin that extends Anki's functionality
- **Anki_Hook**: An event callback system provided by Anki for add-ons to respond to user actions
- **Card_Review**: A single instance of a user answering a flashcard in Anki
- **Correct_Answer**: A card review where the user selects "Good" or "Easy"
- **Wrong_Answer**: A card review where the user selects "Again" or "Hard"
- **Theme**: A visual and mechanical game style (Mario, Zelda, or DKC)
- **Progression_System**: The unified tracking of points, levels, and achievements across all themes
- **Session**: A continuous period of card reviews from opening Anki to closing it
- **Streak**: Consecutive correct answers without interruption
- **Combo_Multiplier**: A bonus multiplier applied to points based on streak length
- **Power_Up**: A temporary or permanent bonus earned through gameplay
- **Collectible**: An in-game item that can be collected and stored
- **Level**: A playable game segment unlocked through card reviews
- **Dashboard**: The main UI panel showing player stats and game progress
- **Game_Window**: A separate PyQt window displaying real-time game animations
- **Sprite**: A 2D image used for character and item animations
- **Health_Bar**: A visual indicator of session health that decreases on wrong answers
- **Currency**: In-game coins/points used for unlocks and upgrades
- **Cosmetic**: A visual customization item with no gameplay effect
- **Boss_Battle**: A special challenge triggered at deck completion (Zelda theme)
- **Time_Trial**: A timed challenge mode for bonus rewards (DKC theme)
- **SQLite_Database**: Local file-based database for persisting game state
- **JSON_Config**: Configuration file for user preferences and settings

## Requirements

### Requirement 1: Theme Selection and Switching

**User Story:** As a user, I want to select and switch between game themes at any time, so that I can enjoy different gameplay styles without losing my progress.

#### Acceptance Criteria

1. WHEN the add-on is first installed, THE Theme_Selector SHALL present the user with three theme options: Mario, Zelda, and DKC
2. WHEN a user selects a theme, THE Theme_Manager SHALL apply the selected theme's visual assets and game mechanics immediately
3. WHEN a user switches themes mid-session, THE Progression_System SHALL preserve all accumulated points, levels, and achievements
4. WHEN a user switches themes, THE Game_Window SHALL transition to the new theme's visual style within 2 seconds
5. THE Theme_Manager SHALL persist the user's current theme selection to the SQLite_Database
6. WHEN the add-on loads, THE Theme_Manager SHALL restore the user's previously selected theme

### Requirement 2: Unified Progression System

**User Story:** As a user, I want my progress to be tracked across all Anki decks and themes, so that all my study efforts contribute to a single game experience.

#### Acceptance Criteria

1. THE Progression_System SHALL track total points earned across all decks and themes
2. WHEN a user completes a Card_Review in any deck, THE Progression_System SHALL update the unified point total
3. THE Progression_System SHALL track the total number of cards reviewed across all decks
4. WHEN a user earns 50 correct answers, THE Progression_System SHALL unlock one playable level
5. WHEN a user earns 100 correct answers, THE Progression_System SHALL grant one power-up
6. THE Progression_System SHALL persist all progression data to the SQLite_Database after each Card_Review
7. WHEN the add-on loads, THE Progression_System SHALL restore all progression data from the SQLite_Database

### Requirement 3: Points and Scoring

**User Story:** As a user, I want to earn points for correct answers and see penalties for wrong answers, so that I have meaningful feedback on my study performance.

#### Acceptance Criteria

1. WHEN a user provides a Correct_Answer, THE Scoring_Engine SHALL award base points (configurable, default 10)
2. WHEN a user provides a Wrong_Answer, THE Scoring_Engine SHALL apply a penalty (lose 1 coin or reduce health bar by 10%)
3. WHEN a user maintains a streak of 5+ correct answers, THE Scoring_Engine SHALL apply a combo multiplier (1.5x at 5, 2x at 10, 3x at 20)
4. WHEN a user achieves 90%+ accuracy in a session, THE Scoring_Engine SHALL award an accuracy bonus (25% extra points)
5. WHEN a session ends, THE Health_Bar SHALL reset to full for the next session
6. THE Scoring_Engine SHALL calculate and display the current score in real-time

### Requirement 4: Mario Theme Mechanics

**User Story:** As a user, I want to experience Mario-style gameplay with side-scrolling levels and coin collection, so that I feel like I'm playing a classic platformer while studying.

#### Acceptance Criteria

1. WHEN the Mario theme is active, THE Game_Window SHALL display a side-scrolling level view
2. WHEN a user provides a Correct_Answer, THE Mario_Engine SHALL animate the character moving forward and collecting a coin
3. WHEN a user provides a Wrong_Answer, THE Mario_Engine SHALL animate the character taking damage
4. WHEN a user achieves 95%+ accuracy in a level, THE Mario_Engine SHALL award a mushroom power-up
5. WHEN a user achieves 98%+ accuracy in a level, THE Mario_Engine SHALL award a fire flower power-up
6. WHEN a user completes a level with 100% accuracy, THE Mario_Engine SHALL award a star power-up
7. THE Mario_Engine SHALL display real-time sprite animations of the character running, jumping, and collecting items
8. WHEN a user unlocks a new level, THE Mario_Engine SHALL display the level selection screen with the new level available

### Requirement 5: Zelda Theme Mechanics

**User Story:** As a user, I want to experience Zelda-style gameplay with exploration and boss battles, so that I feel like I'm on an adventure while studying.

#### Acceptance Criteria

1. WHEN the Zelda theme is active, THE Game_Window SHALL display an adventure map view
2. WHEN a user provides a Correct_Answer, THE Zelda_Engine SHALL animate the character exploring and collecting items
3. WHEN a user provides a Wrong_Answer, THE Zelda_Engine SHALL animate the character taking damage from an enemy
4. WHEN a user completes all cards in a deck, THE Zelda_Engine SHALL trigger a boss battle sequence
5. WHEN a user wins a boss battle, THE Zelda_Engine SHALL award a special item (heart container, new weapon, or key item)
6. THE Zelda_Engine SHALL track both functional items (usable during reviews) and cosmetic items separately
7. WHEN a user has a functional item equipped, THE Item_System SHALL provide a review bonus (hint, extra time, or second chance)
8. THE Zelda_Engine SHALL display the adventure map with explored and unexplored regions based on deck progress

### Requirement 6: DKC Theme Mechanics

**User Story:** As a user, I want to experience DKC-style gameplay with collectible hoarding and time trials, so that I feel the excitement of racing against the clock while studying.

#### Acceptance Criteria

1. WHEN the DKC theme is active, THE Game_Window SHALL display a jungle world view with collectible counters
2. WHEN a user provides a Correct_Answer, THE DKC_Engine SHALL animate the character collecting bananas
3. WHEN a user provides a Wrong_Answer, THE DKC_Engine SHALL animate the character losing bananas
4. WHEN a user activates time trial mode, THE DKC_Engine SHALL start a countdown timer
5. WHEN a user completes cards within the time trial limit, THE DKC_Engine SHALL award bonus bananas based on remaining time
6. IF the time trial timer expires, THEN THE DKC_Engine SHALL end the time trial and calculate final rewards
7. THE DKC_Engine SHALL track world completion percentage based on total cards reviewed
8. WHEN a user reaches 100% world completion, THE DKC_Engine SHALL unlock a bonus world

### Requirement 7: Anki Integration

**User Story:** As a user, I want the add-on to seamlessly integrate with Anki's review system, so that my study flow is enhanced rather than interrupted.

#### Acceptance Criteria

1. WHEN Anki starts, THE Add-on SHALL register hooks for card review events
2. WHEN a Card_Review is completed, THE Anki_Hook SHALL notify the Progression_System with the review result
3. THE Add-on SHALL not interfere with Anki's native review functionality
4. WHEN the user is in review mode, THE Game_Window SHALL update in real-time based on review results
5. IF the Game_Window is closed, THEN THE Add-on SHALL continue tracking progress in the background
6. THE Add-on SHALL add a menu item to Anki's Tools menu for accessing the Dashboard
7. THE Add-on SHALL add a toolbar button for quick access to the Game_Window

### Requirement 8: Data Persistence

**User Story:** As a user, I want my game progress to be saved automatically, so that I never lose my achievements or collectibles.

#### Acceptance Criteria

1. THE Data_Manager SHALL store all game state in a SQLite database file within the add-on folder
2. WHEN a Card_Review is completed, THE Data_Manager SHALL persist the updated state within 1 second
3. THE Data_Manager SHALL store: character stats, collectibles, levels unlocked, achievements, currency, cosmetics, and map progress
4. WHEN the add-on loads, THE Data_Manager SHALL restore all persisted state
5. IF the database file is corrupted, THEN THE Data_Manager SHALL create a backup and initialize a new database
6. THE Data_Manager SHALL support exporting game state to a JSON file for backup purposes
7. THE Data_Manager SHALL support importing game state from a JSON backup file

### Requirement 9: Game Window and Animations

**User Story:** As a user, I want to see real-time animations in a separate game window, so that I can enjoy the visual feedback without cluttering my study interface.

#### Acceptance Criteria

1. THE Game_Window SHALL open as a separate PyQt window (not an overlay on Anki)
2. THE Game_Window SHALL display sprite animations at a minimum of 30 frames per second
3. WHEN a Card_Review result is received, THE Animation_Engine SHALL play the appropriate animation within 100ms
4. THE Game_Window SHALL support resizing while maintaining sprite aspect ratios
5. THE Game_Window SHALL remember its position and size between sessions
6. WHEN the user closes the Game_Window, THE Add-on SHALL continue functioning without the visual display
7. THE Game_Window SHALL provide a minimize-to-tray option

### Requirement 10: Dashboard

**User Story:** As a user, I want to view my overall progress and statistics in a dashboard, so that I can track my study achievements and game progress.

#### Acceptance Criteria

1. THE Dashboard SHALL be accessible from Anki's main window via menu or toolbar
2. THE Dashboard SHALL display: total points, cards reviewed, current streak, accuracy percentage, and levels unlocked
3. THE Dashboard SHALL display theme-specific progress (coins for Mario, items for Zelda, bananas for DKC)
4. THE Dashboard SHALL display a list of earned achievements with unlock dates
5. THE Dashboard SHALL display current power-ups and their effects
6. THE Dashboard SHALL provide quick access to theme switching
7. THE Dashboard SHALL update in real-time when the user completes reviews

### Requirement 11: Rewards and Unlocks

**User Story:** As a user, I want to earn meaningful rewards for my study efforts, so that I feel motivated to continue studying.

#### Acceptance Criteria

1. WHEN a user earns currency, THE Reward_System SHALL add it to the user's balance
2. THE Reward_System SHALL provide character unlocks purchasable with currency
3. THE Reward_System SHALL provide cosmetic items purchasable with currency
4. WHEN a user completes an achievement, THE Reward_System SHALL display a notification and award bonus currency
5. THE Reward_System SHALL track and display progress toward the next unlock
6. WHEN a user unlocks a new character, THE Character_System SHALL make it available for selection

### Requirement 12: Customization and Accessibility

**User Story:** As a user, I want to customize the game experience and accessibility options, so that the add-on works well for my preferences and needs.

#### Acceptance Criteria

1. THE Settings_Panel SHALL allow users to adjust difficulty (point values, penalty severity)
2. THE Settings_Panel SHALL allow users to adjust reward rates (multipliers, unlock thresholds)
3. THE Settings_Panel SHALL allow users to adjust game speed (animation speed, transition duration)
4. THE Settings_Panel SHALL provide a "stats only" mode that disables all animations
5. THE Settings_Panel SHALL provide colorblind mode options (deuteranopia, protanopia, tritanopia)
6. THE Settings_Panel SHALL allow users to enable/disable sound effects
7. THE Settings_Panel SHALL allow users to adjust sound volume
8. WHEN settings are changed, THE Settings_Manager SHALL persist them immediately
9. WHEN the add-on loads, THE Settings_Manager SHALL restore all user settings

### Requirement 13: Power-Up System

**User Story:** As a user, I want to earn and use power-ups that enhance my study experience, so that I have additional tools to help me succeed.

#### Acceptance Criteria

1. WHEN a user earns 100 correct answers, THE Power_Up_System SHALL grant one power-up appropriate to the current theme
2. WHEN a user is playing a level, THE Power_Up_System SHALL allow power-up collection during gameplay
3. THE Power_Up_System SHALL store earned power-ups in the user's inventory
4. WHEN a user activates a power-up, THE Power_Up_System SHALL apply its effect for the specified duration
5. THE Power_Up_System SHALL display available power-ups in the Dashboard
6. IF a power-up has a limited duration, THEN THE Power_Up_System SHALL display a countdown timer

### Requirement 14: Achievement System

**User Story:** As a user, I want to earn achievements for reaching milestones, so that I have long-term goals to work toward.

#### Acceptance Criteria

1. THE Achievement_System SHALL track progress toward predefined milestones
2. WHEN a user reaches a milestone, THE Achievement_System SHALL unlock the corresponding achievement
3. THE Achievement_System SHALL display a notification when an achievement is unlocked
4. THE Achievement_System SHALL persist all achievement data to the database
5. THE Dashboard SHALL display all achievements with their unlock status and dates
6. THE Achievement_System SHALL include achievements for: cards reviewed (100, 500, 1000, 5000), streaks (10, 25, 50, 100), accuracy (90%, 95%, 100% in a session), levels completed, and theme-specific milestones

### Requirement 15: Level System

**User Story:** As a user, I want to unlock and play levels as I study, so that I have tangible progress markers for my efforts.

#### Acceptance Criteria

1. WHEN a user earns 50 correct answers, THE Level_System SHALL unlock one new level
2. THE Level_System SHALL track which levels have been unlocked and completed
3. WHEN a user selects a level, THE Level_System SHALL load the level in the Game_Window
4. THE Level_System SHALL provide different level designs for each theme
5. WHEN a user completes a level, THE Level_System SHALL award completion rewards
6. THE Level_System SHALL persist level progress to the database
7. THE Dashboard SHALL display total levels unlocked and completed
