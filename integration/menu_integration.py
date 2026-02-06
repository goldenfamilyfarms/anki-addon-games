"""
MenuIntegration for NintendAnki.

This module implements the MenuIntegration class that integrates add-on UI elements
into Anki's interface, including menu items and toolbar buttons.

The MenuIntegration provides a mock-friendly interface that can be tested without
Anki running by using dependency injection for the menu/toolbar system.

Requirements: 7.6, 7.7
"""

from typing import Any, Callable, Dict, List, Optional, Protocol
import logging


# Set up logging
logger = logging.getLogger(__name__)


class AnkiMenuProvider(Protocol):
    """Protocol for Anki menu integration.
    
    This protocol defines the interface for adding menu items and toolbar buttons
    to Anki's interface. It allows for dependency injection of the actual
    Anki menu system or a mock for testing.
    """
    
    def add_menu_item(
        self,
        menu_name: str,
        item_text: str,
        callback: Callable[[], None],
        shortcut: Optional[str] = None
    ) -> Any:
        """Add a menu item to a menu.
        
        Args:
            menu_name: Name of the menu to add to (e.g., "Tools")
            item_text: Text to display for the menu item
            callback: Function to call when the menu item is clicked
            shortcut: Optional keyboard shortcut (e.g., "Ctrl+Shift+D")
            
        Returns:
            The created menu action (QAction or mock)
        """
        ...
    
    def remove_menu_item(self, menu_name: str, action: Any) -> None:
        """Remove a menu item from a menu.
        
        Args:
            menu_name: Name of the menu to remove from
            action: The action to remove (returned from add_menu_item)
        """
        ...
    
    def add_toolbar_button(
        self,
        toolbar_name: str,
        button_text: str,
        callback: Callable[[], None],
        icon_path: Optional[str] = None,
        tooltip: Optional[str] = None
    ) -> Any:
        """Add a button to a toolbar.
        
        Args:
            toolbar_name: Name of the toolbar to add to (e.g., "main")
            button_text: Text to display on the button
            callback: Function to call when the button is clicked
            icon_path: Optional path to an icon file
            tooltip: Optional tooltip text
            
        Returns:
            The created toolbar action (QAction or mock)
        """
        ...
    
    def remove_toolbar_button(self, toolbar_name: str, action: Any) -> None:
        """Remove a button from a toolbar.
        
        Args:
            toolbar_name: Name of the toolbar to remove from
            action: The action to remove (returned from add_toolbar_button)
        """
        ...


class RealAnkiMenuProvider:
    """Real Anki menu provider that uses aqt.mw.
    
    This class wraps the actual Anki menu/toolbar system for production use.
    It should only be instantiated when running inside Anki.
    """
    
    def __init__(self, main_window: Any = None):
        """Initialize the real Anki menu provider.
        
        Args:
            main_window: Anki's main window (mw). If None, will try to import from aqt.
        """
        try:
            if main_window is None:
                from aqt import mw
                self._mw = mw
            else:
                self._mw = main_window
            from aqt.qt import QAction, QIcon
            self._QAction = QAction
            self._QIcon = QIcon
        except ImportError:
            raise RuntimeError(
                "Cannot create RealAnkiMenuProvider outside of Anki. "
                "Use MockAnkiMenuProvider for testing."
            )
        
        self._menu_actions: Dict[str, List[Any]] = {}
        self._toolbar_actions: Dict[str, List[Any]] = {}
    
    def add_menu_item(
        self,
        menu_name: str,
        item_text: str,
        callback: Callable[[], None],
        shortcut: Optional[str] = None
    ) -> Any:
        """Add a menu item to an Anki menu.
        
        Args:
            menu_name: Name of the menu (e.g., "Tools")
            item_text: Text to display for the menu item
            callback: Function to call when clicked
            shortcut: Optional keyboard shortcut
            
        Returns:
            The created QAction
        """
        # Find the menu
        menu = self._find_menu(menu_name)
        if menu is None:
            logger.warning(f"Menu not found: {menu_name}")
            return None
        
        # Create the action
        action = self._QAction(item_text, self._mw)
        action.triggered.connect(callback)
        
        if shortcut:
            action.setShortcut(shortcut)
        
        # Add to menu
        menu.addAction(action)
        
        # Track for cleanup
        if menu_name not in self._menu_actions:
            self._menu_actions[menu_name] = []
        self._menu_actions[menu_name].append(action)
        
        logger.info(f"Added menu item '{item_text}' to {menu_name} menu")
        return action
    
    def remove_menu_item(self, menu_name: str, action: Any) -> None:
        """Remove a menu item from an Anki menu.
        
        Args:
            menu_name: Name of the menu
            action: The QAction to remove
        """
        if action is None:
            return
        
        menu = self._find_menu(menu_name)
        if menu is not None:
            menu.removeAction(action)
            logger.info(f"Removed menu item from {menu_name} menu")
        
        # Remove from tracking
        if menu_name in self._menu_actions:
            try:
                self._menu_actions[menu_name].remove(action)
            except ValueError:
                pass
    
    def add_toolbar_button(
        self,
        toolbar_name: str,
        button_text: str,
        callback: Callable[[], None],
        icon_path: Optional[str] = None,
        tooltip: Optional[str] = None
    ) -> Any:
        """Add a button to an Anki toolbar.
        
        Args:
            toolbar_name: Name of the toolbar (e.g., "main")
            button_text: Text to display on the button
            callback: Function to call when clicked
            icon_path: Optional path to an icon file
            tooltip: Optional tooltip text
            
        Returns:
            The created QAction
        """
        # Create the action
        if icon_path:
            icon = self._QIcon(icon_path)
            action = self._QAction(icon, button_text, self._mw)
        else:
            action = self._QAction(button_text, self._mw)
        
        action.triggered.connect(callback)
        
        if tooltip:
            action.setToolTip(tooltip)
        
        # Add to main window's toolbar
        # Anki's main toolbar is accessed via mw.form.toolbar
        try:
            if hasattr(self._mw, 'form') and hasattr(self._mw.form, 'toolbar'):
                self._mw.form.toolbar.addAction(action)
            else:
                # Fallback: add to main window's toolbar directly
                self._mw.addToolBar(action)
        except Exception as e:
            logger.warning(f"Could not add toolbar button: {e}")
            return None
        
        # Track for cleanup
        if toolbar_name not in self._toolbar_actions:
            self._toolbar_actions[toolbar_name] = []
        self._toolbar_actions[toolbar_name].append(action)
        
        logger.info(f"Added toolbar button '{button_text}'")
        return action
    
    def remove_toolbar_button(self, toolbar_name: str, action: Any) -> None:
        """Remove a button from an Anki toolbar.
        
        Args:
            toolbar_name: Name of the toolbar
            action: The QAction to remove
        """
        if action is None:
            return
        
        try:
            if hasattr(self._mw, 'form') and hasattr(self._mw.form, 'toolbar'):
                self._mw.form.toolbar.removeAction(action)
            logger.info(f"Removed toolbar button")
        except Exception as e:
            logger.warning(f"Could not remove toolbar button: {e}")
        
        # Remove from tracking
        if toolbar_name in self._toolbar_actions:
            try:
                self._toolbar_actions[toolbar_name].remove(action)
            except ValueError:
                pass
    
    def _find_menu(self, menu_name: str) -> Any:
        """Find a menu by name in Anki's menu bar.
        
        Args:
            menu_name: Name of the menu to find
            
        Returns:
            The QMenu if found, None otherwise
        """
        if not hasattr(self._mw, 'form') or not hasattr(self._mw.form, 'menubar'):
            return None
        
        menubar = self._mw.form.menubar
        for action in menubar.actions():
            menu = action.menu()
            if menu and action.text().replace('&', '') == menu_name:
                return menu
        
        return None


class MockAnkiMenuProvider:
    """Mock Anki menu provider for testing.
    
    This class provides a mock implementation of the Anki menu/toolbar system
    that can be used for testing without Anki running.
    """
    
    def __init__(self):
        """Initialize the mock menu provider."""
        self._menu_items: Dict[str, List[Dict[str, Any]]] = {}
        self._toolbar_buttons: Dict[str, List[Dict[str, Any]]] = {}
        self._action_counter = 0
    
    def add_menu_item(
        self,
        menu_name: str,
        item_text: str,
        callback: Callable[[], None],
        shortcut: Optional[str] = None
    ) -> Any:
        """Add a mock menu item.
        
        Args:
            menu_name: Name of the menu
            item_text: Text to display
            callback: Function to call when clicked
            shortcut: Optional keyboard shortcut
            
        Returns:
            A mock action object
        """
        self._action_counter += 1
        action = MockAction(
            id=self._action_counter,
            text=item_text,
            callback=callback,
            shortcut=shortcut
        )
        
        if menu_name not in self._menu_items:
            self._menu_items[menu_name] = []
        
        self._menu_items[menu_name].append({
            'action': action,
            'text': item_text,
            'callback': callback,
            'shortcut': shortcut
        })
        
        logger.debug(f"Mock: Added menu item '{item_text}' to {menu_name}")
        return action
    
    def remove_menu_item(self, menu_name: str, action: Any) -> None:
        """Remove a mock menu item.
        
        Args:
            menu_name: Name of the menu
            action: The mock action to remove
        """
        if menu_name in self._menu_items:
            self._menu_items[menu_name] = [
                item for item in self._menu_items[menu_name]
                if item['action'] != action
            ]
            logger.debug(f"Mock: Removed menu item from {menu_name}")
    
    def add_toolbar_button(
        self,
        toolbar_name: str,
        button_text: str,
        callback: Callable[[], None],
        icon_path: Optional[str] = None,
        tooltip: Optional[str] = None
    ) -> Any:
        """Add a mock toolbar button.
        
        Args:
            toolbar_name: Name of the toolbar
            button_text: Text to display
            callback: Function to call when clicked
            icon_path: Optional icon path
            tooltip: Optional tooltip
            
        Returns:
            A mock action object
        """
        self._action_counter += 1
        action = MockAction(
            id=self._action_counter,
            text=button_text,
            callback=callback,
            icon_path=icon_path,
            tooltip=tooltip
        )
        
        if toolbar_name not in self._toolbar_buttons:
            self._toolbar_buttons[toolbar_name] = []
        
        self._toolbar_buttons[toolbar_name].append({
            'action': action,
            'text': button_text,
            'callback': callback,
            'icon_path': icon_path,
            'tooltip': tooltip
        })
        
        logger.debug(f"Mock: Added toolbar button '{button_text}'")
        return action
    
    def remove_toolbar_button(self, toolbar_name: str, action: Any) -> None:
        """Remove a mock toolbar button.
        
        Args:
            toolbar_name: Name of the toolbar
            action: The mock action to remove
        """
        if toolbar_name in self._toolbar_buttons:
            self._toolbar_buttons[toolbar_name] = [
                item for item in self._toolbar_buttons[toolbar_name]
                if item['action'] != action
            ]
            logger.debug(f"Mock: Removed toolbar button from {toolbar_name}")
    
    # Test helper methods
    
    def get_menu_items(self, menu_name: str) -> List[Dict[str, Any]]:
        """Get all menu items for a menu.
        
        Args:
            menu_name: Name of the menu
            
        Returns:
            List of menu item dictionaries
        """
        return self._menu_items.get(menu_name, [])
    
    def get_toolbar_buttons(self, toolbar_name: str) -> List[Dict[str, Any]]:
        """Get all toolbar buttons for a toolbar.
        
        Args:
            toolbar_name: Name of the toolbar
            
        Returns:
            List of toolbar button dictionaries
        """
        return self._toolbar_buttons.get(toolbar_name, [])
    
    def has_menu_item(self, menu_name: str, item_text: str) -> bool:
        """Check if a menu item exists.
        
        Args:
            menu_name: Name of the menu
            item_text: Text of the menu item
            
        Returns:
            True if the menu item exists
        """
        items = self._menu_items.get(menu_name, [])
        return any(item['text'] == item_text for item in items)
    
    def has_toolbar_button(self, toolbar_name: str, button_text: str) -> bool:
        """Check if a toolbar button exists.
        
        Args:
            toolbar_name: Name of the toolbar
            button_text: Text of the button
            
        Returns:
            True if the toolbar button exists
        """
        buttons = self._toolbar_buttons.get(toolbar_name, [])
        return any(button['text'] == button_text for button in buttons)
    
    def trigger_menu_item(self, menu_name: str, item_text: str) -> bool:
        """Trigger a menu item's callback.
        
        Args:
            menu_name: Name of the menu
            item_text: Text of the menu item
            
        Returns:
            True if the item was found and triggered
        """
        items = self._menu_items.get(menu_name, [])
        for item in items:
            if item['text'] == item_text:
                item['callback']()
                return True
        return False
    
    def trigger_toolbar_button(self, toolbar_name: str, button_text: str) -> bool:
        """Trigger a toolbar button's callback.
        
        Args:
            toolbar_name: Name of the toolbar
            button_text: Text of the button
            
        Returns:
            True if the button was found and triggered
        """
        buttons = self._toolbar_buttons.get(toolbar_name, [])
        for button in buttons:
            if button['text'] == button_text:
                button['callback']()
                return True
        return False
    
    def clear_all(self) -> None:
        """Clear all menu items and toolbar buttons."""
        self._menu_items.clear()
        self._toolbar_buttons.clear()


class MockAction:
    """Mock QAction for testing.
    
    This class simulates a Qt QAction for testing purposes.
    """
    
    def __init__(
        self,
        id: int,
        text: str,
        callback: Callable[[], None],
        shortcut: Optional[str] = None,
        icon_path: Optional[str] = None,
        tooltip: Optional[str] = None
    ):
        """Initialize the mock action.
        
        Args:
            id: Unique identifier for this action
            text: Display text
            callback: Function to call when triggered
            shortcut: Optional keyboard shortcut
            icon_path: Optional icon path
            tooltip: Optional tooltip
        """
        self.id = id
        self.text = text
        self.callback = callback
        self.shortcut = shortcut
        self.icon_path = icon_path
        self.tooltip = tooltip
        self._enabled = True
        self._visible = True
    
    def trigger(self) -> None:
        """Trigger the action's callback."""
        if self._enabled:
            self.callback()
    
    def setEnabled(self, enabled: bool) -> None:
        """Set whether the action is enabled."""
        self._enabled = enabled
    
    def isEnabled(self) -> bool:
        """Check if the action is enabled."""
        return self._enabled
    
    def setVisible(self, visible: bool) -> None:
        """Set whether the action is visible."""
        self._visible = visible
    
    def isVisible(self) -> bool:
        """Check if the action is visible."""
        return self._visible
    
    def __eq__(self, other: Any) -> bool:
        """Check equality based on id."""
        if isinstance(other, MockAction):
            return self.id == other.id
        return False
    
    def __hash__(self) -> int:
        """Hash based on id."""
        return hash(self.id)


class DashboardOpener(Protocol):
    """Protocol for opening the Dashboard.
    
    This allows dependency injection of the dashboard opening mechanism.
    """
    
    def show(self) -> None:
        """Show the dashboard."""
        ...


class GameWindowOpener(Protocol):
    """Protocol for opening the Game Window.
    
    This allows dependency injection of the game window opening mechanism.
    """
    
    def show(self) -> None:
        """Show the game window."""
        ...


class SettingsPanelOpener(Protocol):
    """Protocol for opening the Settings Panel.
    
    This allows dependency injection of the settings panel opening mechanism.
    """
    
    def show(self) -> None:
        """Show the settings panel."""
        ...


class MenuIntegration:
    """Integrates add-on UI elements into Anki's interface.
    
    The MenuIntegration is responsible for:
    - Adding menu items to Anki's Tools menu for accessing the Dashboard (Requirement 7.6)
    - Adding a toolbar button for quick access to the Game Window (Requirement 7.7)
    - Providing clean setup and teardown of UI elements
    
    The class uses dependency injection for the menu provider, allowing
    for easy testing with a mock provider.
    
    Attributes:
        dashboard: Dashboard opener (or callable)
        game_window: Game window opener (or callable)
        settings_panel: Settings panel opener (or callable)
        menu_provider: Provider for menu/toolbar integration (real or mock)
        _menu_actions: List of created menu actions for cleanup
        _toolbar_actions: List of created toolbar actions for cleanup
        _setup_complete: Whether setup has been completed
    """
    
    # Menu and toolbar names
    TOOLS_MENU = "Tools"
    MAIN_TOOLBAR = "main"
    
    # Menu item texts
    MENU_DASHBOARD = "NintendAnki Dashboard"
    MENU_GAME_WINDOW = "NintendAnki Game Window"
    MENU_SETTINGS = "NintendAnki Settings"
    
    # Toolbar button text
    TOOLBAR_GAME_WINDOW = "🎮"
    TOOLBAR_GAME_WINDOW_TOOLTIP = "Open NintendAnki Game Window"
    
    def __init__(
        self,
        dashboard: Optional[DashboardOpener] = None,
        game_window: Optional[GameWindowOpener] = None,
        settings_panel: Optional[SettingsPanelOpener] = None,
        menu_provider: Optional[AnkiMenuProvider] = None
    ):
        """Initialize the MenuIntegration.
        
        Args:
            dashboard: Dashboard opener (must have show() method or be callable)
            game_window: Game window opener (must have show() method or be callable)
            settings_panel: Settings panel opener (must have show() method or be callable)
            menu_provider: Optional menu provider (uses MockAnkiMenuProvider if None)
        """
        self.dashboard = dashboard
        self.game_window = game_window
        self.settings_panel = settings_panel
        self.menu_provider = menu_provider or MockAnkiMenuProvider()
        
        self._menu_actions: List[Any] = []
        self._toolbar_actions: List[Any] = []
        self._setup_complete = False
        
        logger.info("MenuIntegration initialized")
    
    def setup_menu(self, main_window: Any = None) -> None:
        """Add menu items to Anki's Tools menu.
        
        This method adds the following menu items to the Tools menu:
        - NintendAnki Dashboard: Opens the main dashboard
        - NintendAnki Game Window: Opens the game window
        - NintendAnki Settings: Opens the settings panel
        
        Args:
            main_window: Anki's main window (optional, for compatibility)
            
        Requirements: 7.6
        """
        if self._setup_complete:
            logger.warning("Menu already set up, skipping")
            return
        
        # Add Dashboard menu item
        if self.dashboard is not None:
            action = self.menu_provider.add_menu_item(
                menu_name=self.TOOLS_MENU,
                item_text=self.MENU_DASHBOARD,
                callback=self._open_dashboard,
                shortcut="Ctrl+Shift+D"
            )
            if action is not None:
                self._menu_actions.append(action)
                logger.info(f"Added menu item: {self.MENU_DASHBOARD}")
        
        # Add Game Window menu item
        if self.game_window is not None:
            action = self.menu_provider.add_menu_item(
                menu_name=self.TOOLS_MENU,
                item_text=self.MENU_GAME_WINDOW,
                callback=self._open_game_window,
                shortcut="Ctrl+Shift+G"
            )
            if action is not None:
                self._menu_actions.append(action)
                logger.info(f"Added menu item: {self.MENU_GAME_WINDOW}")
        
        # Add Settings menu item
        if self.settings_panel is not None:
            action = self.menu_provider.add_menu_item(
                menu_name=self.TOOLS_MENU,
                item_text=self.MENU_SETTINGS,
                callback=self._open_settings,
                shortcut="Ctrl+Shift+S"
            )
            if action is not None:
                self._menu_actions.append(action)
                logger.info(f"Added menu item: {self.MENU_SETTINGS}")
        
        logger.info("Menu setup complete")
    
    def setup_toolbar(self, main_window: Any = None) -> None:
        """Add toolbar button for quick game window access.
        
        This method adds a toolbar button that opens the Game Window
        with a single click.
        
        Args:
            main_window: Anki's main window (optional, for compatibility)
            
        Requirements: 7.7
        """
        if self.game_window is None:
            logger.warning("No game window provided, skipping toolbar setup")
            return
        
        action = self.menu_provider.add_toolbar_button(
            toolbar_name=self.MAIN_TOOLBAR,
            button_text=self.TOOLBAR_GAME_WINDOW,
            callback=self._open_game_window,
            tooltip=self.TOOLBAR_GAME_WINDOW_TOOLTIP
        )
        
        if action is not None:
            self._toolbar_actions.append(action)
            logger.info("Added toolbar button for Game Window")
        
        self._setup_complete = True
        logger.info("Toolbar setup complete")
    
    def setup(self, main_window: Any = None) -> None:
        """Set up both menu items and toolbar button.
        
        This is a convenience method that calls both setup_menu() and
        setup_toolbar().
        
        Args:
            main_window: Anki's main window (optional, for compatibility)
        """
        self.setup_menu(main_window)
        self.setup_toolbar(main_window)
    
    def teardown(self) -> None:
        """Remove all menu items and toolbar buttons.
        
        This method should be called when the add-on unloads to ensure
        clean removal of all UI elements.
        """
        # Remove menu items
        for action in self._menu_actions:
            self.menu_provider.remove_menu_item(self.TOOLS_MENU, action)
        self._menu_actions.clear()
        
        # Remove toolbar buttons
        for action in self._toolbar_actions:
            self.menu_provider.remove_toolbar_button(self.MAIN_TOOLBAR, action)
        self._toolbar_actions.clear()
        
        self._setup_complete = False
        logger.info("Menu integration teardown complete")
    
    @property
    def is_setup(self) -> bool:
        """Check if the menu integration has been set up.
        
        Returns:
            True if setup has been completed
        """
        return self._setup_complete
    
    @property
    def menu_action_count(self) -> int:
        """Get the number of menu actions created.
        
        Returns:
            Number of menu actions
        """
        return len(self._menu_actions)
    
    @property
    def toolbar_action_count(self) -> int:
        """Get the number of toolbar actions created.
        
        Returns:
            Number of toolbar actions
        """
        return len(self._toolbar_actions)
    
    def _open_dashboard(self) -> None:
        """Open the dashboard.
        
        This is the callback for the Dashboard menu item.
        """
        if self.dashboard is not None:
            try:
                if hasattr(self.dashboard, 'show'):
                    self.dashboard.show()
                elif callable(self.dashboard):
                    self.dashboard()
                logger.debug("Dashboard opened")
            except Exception as e:
                logger.error(f"Error opening dashboard: {e}")
    
    def _open_game_window(self) -> None:
        """Open the game window.
        
        This is the callback for the Game Window menu item and toolbar button.
        """
        if self.game_window is not None:
            try:
                if hasattr(self.game_window, 'show'):
                    self.game_window.show()
                elif callable(self.game_window):
                    self.game_window()
                logger.debug("Game window opened")
            except Exception as e:
                logger.error(f"Error opening game window: {e}")
    
    def _open_settings(self) -> None:
        """Open the settings panel.
        
        This is the callback for the Settings menu item.
        """
        if self.settings_panel is not None:
            try:
                if hasattr(self.settings_panel, 'show'):
                    self.settings_panel.show()
                elif callable(self.settings_panel):
                    self.settings_panel()
                logger.debug("Settings panel opened")
            except Exception as e:
                logger.error(f"Error opening settings panel: {e}")
