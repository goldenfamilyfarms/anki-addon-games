"""
Tests for the MenuIntegration module.

This module contains unit tests for the MenuIntegration class, including tests for:
- Menu item setup and teardown
- Toolbar button setup and teardown
- Callback functionality
- Mock menu provider functionality

Requirements tested: 7.6, 7.7
"""

import pytest
from unittest.mock import MagicMock, call

from integration.menu_integration import (
    MenuIntegration,
    MockAnkiMenuProvider,
    MockAction,
)


# ============================================================================
# Fixtures
# ============================================================================

@pytest.fixture
def mock_menu_provider():
    """Create a MockAnkiMenuProvider for testing."""
    return MockAnkiMenuProvider()


@pytest.fixture
def mock_dashboard():
    """Create a mock dashboard with show() method."""
    dashboard = MagicMock()
    dashboard.show = MagicMock()
    return dashboard


@pytest.fixture
def mock_game_window():
    """Create a mock game window with show() method."""
    game_window = MagicMock()
    game_window.show = MagicMock()
    return game_window


@pytest.fixture
def mock_settings_panel():
    """Create a mock settings panel with show() method."""
    settings_panel = MagicMock()
    settings_panel.show = MagicMock()
    return settings_panel


@pytest.fixture
def menu_integration(
    mock_dashboard,
    mock_game_window,
    mock_settings_panel,
    mock_menu_provider
):
    """Create a MenuIntegration with mock dependencies."""
    return MenuIntegration(
        dashboard=mock_dashboard,
        game_window=mock_game_window,
        settings_panel=mock_settings_panel,
        menu_provider=mock_menu_provider
    )


@pytest.fixture
def menu_integration_no_deps(mock_menu_provider):
    """Create a MenuIntegration with no UI dependencies."""
    return MenuIntegration(
        dashboard=None,
        game_window=None,
        settings_panel=None,
        menu_provider=mock_menu_provider
    )


# ============================================================================
# MockAnkiMenuProvider Tests
# ============================================================================

class TestMockAnkiMenuProvider:
    """Tests for the MockAnkiMenuProvider class."""
    
    def test_add_menu_item_creates_action(self, mock_menu_provider):
        """Test that add_menu_item creates and returns an action."""
        callback = MagicMock()
        action = mock_menu_provider.add_menu_item(
            menu_name="Tools",
            item_text="Test Item",
            callback=callback,
            shortcut="Ctrl+T"
        )
        
        assert action is not None
        assert isinstance(action, MockAction)
        assert action.text == "Test Item"
        assert action.shortcut == "Ctrl+T"
    
    def test_add_menu_item_tracks_items(self, mock_menu_provider):
        """Test that menu items are tracked in the provider."""
        callback = MagicMock()
        mock_menu_provider.add_menu_item(
            menu_name="Tools",
            item_text="Test Item",
            callback=callback
        )
        
        assert mock_menu_provider.has_menu_item("Tools", "Test Item")
        items = mock_menu_provider.get_menu_items("Tools")
        assert len(items) == 1
        assert items[0]["text"] == "Test Item"

    def test_remove_menu_item(self, mock_menu_provider):
        """Test that menu items can be removed."""
        callback = MagicMock()
        action = mock_menu_provider.add_menu_item(
            menu_name="Tools",
            item_text="Test Item",
            callback=callback
        )
        
        assert mock_menu_provider.has_menu_item("Tools", "Test Item")
        
        mock_menu_provider.remove_menu_item("Tools", action)
        
        assert not mock_menu_provider.has_menu_item("Tools", "Test Item")
    
    def test_add_toolbar_button_creates_action(self, mock_menu_provider):
        """Test that add_toolbar_button creates and returns an action."""
        callback = MagicMock()
        action = mock_menu_provider.add_toolbar_button(
            toolbar_name="main",
            button_text="Test Button",
            callback=callback,
            tooltip="Test tooltip"
        )
        
        assert action is not None
        assert isinstance(action, MockAction)
        assert action.text == "Test Button"
        assert action.tooltip == "Test tooltip"
    
    def test_add_toolbar_button_tracks_buttons(self, mock_menu_provider):
        """Test that toolbar buttons are tracked in the provider."""
        callback = MagicMock()
        mock_menu_provider.add_toolbar_button(
            toolbar_name="main",
            button_text="Test Button",
            callback=callback
        )
        
        assert mock_menu_provider.has_toolbar_button("main", "Test Button")
        buttons = mock_menu_provider.get_toolbar_buttons("main")
        assert len(buttons) == 1
        assert buttons[0]["text"] == "Test Button"
    
    def test_remove_toolbar_button(self, mock_menu_provider):
        """Test that toolbar buttons can be removed."""
        callback = MagicMock()
        action = mock_menu_provider.add_toolbar_button(
            toolbar_name="main",
            button_text="Test Button",
            callback=callback
        )
        
        assert mock_menu_provider.has_toolbar_button("main", "Test Button")
        
        mock_menu_provider.remove_toolbar_button("main", action)
        
        assert not mock_menu_provider.has_toolbar_button("main", "Test Button")
    
    def test_trigger_menu_item_calls_callback(self, mock_menu_provider):
        """Test that triggering a menu item calls its callback."""
        callback = MagicMock()
        mock_menu_provider.add_menu_item(
            menu_name="Tools",
            item_text="Test Item",
            callback=callback
        )
        
        result = mock_menu_provider.trigger_menu_item("Tools", "Test Item")
        
        assert result is True
        callback.assert_called_once()
    
    def test_trigger_toolbar_button_calls_callback(self, mock_menu_provider):
        """Test that triggering a toolbar button calls its callback."""
        callback = MagicMock()
        mock_menu_provider.add_toolbar_button(
            toolbar_name="main",
            button_text="Test Button",
            callback=callback
        )
        
        result = mock_menu_provider.trigger_toolbar_button("main", "Test Button")
        
        assert result is True
        callback.assert_called_once()
    
    def test_clear_all_removes_everything(self, mock_menu_provider):
        """Test that clear_all removes all items and buttons."""
        callback = MagicMock()
        mock_menu_provider.add_menu_item("Tools", "Item 1", callback)
        mock_menu_provider.add_menu_item("Tools", "Item 2", callback)
        mock_menu_provider.add_toolbar_button("main", "Button 1", callback)
        
        mock_menu_provider.clear_all()
        
        assert len(mock_menu_provider.get_menu_items("Tools")) == 0
        assert len(mock_menu_provider.get_toolbar_buttons("main")) == 0


# ============================================================================
# MockAction Tests
# ============================================================================

class TestMockAction:
    """Tests for the MockAction class."""
    
    def test_action_trigger_calls_callback(self):
        """Test that triggering an action calls its callback."""
        callback = MagicMock()
        action = MockAction(
            id=1,
            text="Test",
            callback=callback
        )
        
        action.trigger()
        
        callback.assert_called_once()
    
    def test_disabled_action_does_not_trigger(self):
        """Test that a disabled action does not call its callback."""
        callback = MagicMock()
        action = MockAction(
            id=1,
            text="Test",
            callback=callback
        )
        
        action.setEnabled(False)
        action.trigger()
        
        callback.assert_not_called()
    
    def test_action_enabled_state(self):
        """Test action enabled/disabled state."""
        action = MockAction(id=1, text="Test", callback=lambda: None)
        
        assert action.isEnabled() is True
        
        action.setEnabled(False)
        assert action.isEnabled() is False
        
        action.setEnabled(True)
        assert action.isEnabled() is True
    
    def test_action_visible_state(self):
        """Test action visible/hidden state."""
        action = MockAction(id=1, text="Test", callback=lambda: None)
        
        assert action.isVisible() is True
        
        action.setVisible(False)
        assert action.isVisible() is False
        
        action.setVisible(True)
        assert action.isVisible() is True
    
    def test_action_equality(self):
        """Test action equality based on id."""
        callback = lambda: None
        action1 = MockAction(id=1, text="Test", callback=callback)
        action2 = MockAction(id=1, text="Different", callback=callback)
        action3 = MockAction(id=2, text="Test", callback=callback)
        
        assert action1 == action2  # Same id
        assert action1 != action3  # Different id


# ============================================================================
# MenuIntegration Tests - Setup Menu (Requirement 7.6)
# ============================================================================

class TestMenuIntegrationSetupMenu:
    """Tests for MenuIntegration.setup_menu() - Requirement 7.6."""
    
    def test_setup_menu_adds_dashboard_item(
        self,
        menu_integration,
        mock_menu_provider
    ):
        """Test that setup_menu adds Dashboard menu item to Tools menu.
        
        Validates: Requirement 7.6 - Add menu item to Tools menu for Dashboard
        """
        menu_integration.setup_menu()
        
        assert mock_menu_provider.has_menu_item(
            "Tools",
            MenuIntegration.MENU_DASHBOARD
        )
    
    def test_setup_menu_adds_game_window_item(
        self,
        menu_integration,
        mock_menu_provider
    ):
        """Test that setup_menu adds Game Window menu item to Tools menu."""
        menu_integration.setup_menu()
        
        assert mock_menu_provider.has_menu_item(
            "Tools",
            MenuIntegration.MENU_GAME_WINDOW
        )
    
    def test_setup_menu_adds_settings_item(
        self,
        menu_integration,
        mock_menu_provider
    ):
        """Test that setup_menu adds Settings menu item to Tools menu."""
        menu_integration.setup_menu()
        
        assert mock_menu_provider.has_menu_item(
            "Tools",
            MenuIntegration.MENU_SETTINGS
        )
    
    def test_setup_menu_creates_three_actions(
        self,
        menu_integration,
        mock_menu_provider
    ):
        """Test that setup_menu creates three menu actions."""
        menu_integration.setup_menu()
        
        items = mock_menu_provider.get_menu_items("Tools")
        assert len(items) == 3
    
    def test_setup_menu_without_dashboard_skips_dashboard_item(
        self,
        mock_game_window,
        mock_settings_panel,
        mock_menu_provider
    ):
        """Test that setup_menu skips Dashboard item if no dashboard provided."""
        integration = MenuIntegration(
            dashboard=None,
            game_window=mock_game_window,
            settings_panel=mock_settings_panel,
            menu_provider=mock_menu_provider
        )
        
        integration.setup_menu()
        
        assert not mock_menu_provider.has_menu_item(
            "Tools",
            MenuIntegration.MENU_DASHBOARD
        )
        # But should still have game window and settings
        assert mock_menu_provider.has_menu_item(
            "Tools",
            MenuIntegration.MENU_GAME_WINDOW
        )
        assert mock_menu_provider.has_menu_item(
            "Tools",
            MenuIntegration.MENU_SETTINGS
        )
    
    def test_setup_menu_no_deps_adds_nothing(
        self,
        menu_integration_no_deps,
        mock_menu_provider
    ):
        """Test that setup_menu adds nothing if no UI components provided."""
        menu_integration_no_deps.setup_menu()
        
        items = mock_menu_provider.get_menu_items("Tools")
        assert len(items) == 0
    
    def test_dashboard_menu_item_opens_dashboard(
        self,
        menu_integration,
        mock_menu_provider,
        mock_dashboard
    ):
        """Test that clicking Dashboard menu item opens the dashboard.
        
        Validates: Requirement 7.6 - Menu item accesses Dashboard
        """
        menu_integration.setup_menu()
        
        # Trigger the menu item
        mock_menu_provider.trigger_menu_item(
            "Tools",
            MenuIntegration.MENU_DASHBOARD
        )
        
        mock_dashboard.show.assert_called_once()
    
    def test_game_window_menu_item_opens_game_window(
        self,
        menu_integration,
        mock_menu_provider,
        mock_game_window
    ):
        """Test that clicking Game Window menu item opens the game window."""
        menu_integration.setup_menu()
        
        mock_menu_provider.trigger_menu_item(
            "Tools",
            MenuIntegration.MENU_GAME_WINDOW
        )
        
        mock_game_window.show.assert_called_once()
    
    def test_settings_menu_item_opens_settings(
        self,
        menu_integration,
        mock_menu_provider,
        mock_settings_panel
    ):
        """Test that clicking Settings menu item opens the settings panel."""
        menu_integration.setup_menu()
        
        mock_menu_provider.trigger_menu_item(
            "Tools",
            MenuIntegration.MENU_SETTINGS
        )
        
        mock_settings_panel.show.assert_called_once()


# ============================================================================
# MenuIntegration Tests - Setup Toolbar (Requirement 7.7)
# ============================================================================

class TestMenuIntegrationSetupToolbar:
    """Tests for MenuIntegration.setup_toolbar() - Requirement 7.7."""
    
    def test_setup_toolbar_adds_game_window_button(
        self,
        menu_integration,
        mock_menu_provider
    ):
        """Test that setup_toolbar adds Game Window button to toolbar.
        
        Validates: Requirement 7.7 - Add toolbar button for Game Window
        """
        menu_integration.setup_toolbar()
        
        assert mock_menu_provider.has_toolbar_button(
            "main",
            MenuIntegration.TOOLBAR_GAME_WINDOW
        )
    
    def test_setup_toolbar_creates_one_action(
        self,
        menu_integration,
        mock_menu_provider
    ):
        """Test that setup_toolbar creates one toolbar action."""
        menu_integration.setup_toolbar()
        
        buttons = mock_menu_provider.get_toolbar_buttons("main")
        assert len(buttons) == 1
    
    def test_setup_toolbar_without_game_window_adds_nothing(
        self,
        mock_dashboard,
        mock_settings_panel,
        mock_menu_provider
    ):
        """Test that setup_toolbar adds nothing if no game window provided."""
        integration = MenuIntegration(
            dashboard=mock_dashboard,
            game_window=None,
            settings_panel=mock_settings_panel,
            menu_provider=mock_menu_provider
        )
        
        integration.setup_toolbar()
        
        buttons = mock_menu_provider.get_toolbar_buttons("main")
        assert len(buttons) == 0
    
    def test_toolbar_button_opens_game_window(
        self,
        menu_integration,
        mock_menu_provider,
        mock_game_window
    ):
        """Test that clicking toolbar button opens the game window.
        
        Validates: Requirement 7.7 - Toolbar button provides quick access to Game Window
        """
        menu_integration.setup_toolbar()
        
        mock_menu_provider.trigger_toolbar_button(
            "main",
            MenuIntegration.TOOLBAR_GAME_WINDOW
        )
        
        mock_game_window.show.assert_called_once()
    
    def test_toolbar_button_has_tooltip(
        self,
        menu_integration,
        mock_menu_provider
    ):
        """Test that toolbar button has a tooltip."""
        menu_integration.setup_toolbar()
        
        buttons = mock_menu_provider.get_toolbar_buttons("main")
        assert len(buttons) == 1
        assert buttons[0]["tooltip"] == MenuIntegration.TOOLBAR_GAME_WINDOW_TOOLTIP


# ============================================================================
# MenuIntegration Tests - Setup and Teardown
# ============================================================================

class TestMenuIntegrationSetupTeardown:
    """Tests for MenuIntegration setup and teardown functionality."""
    
    def test_setup_calls_both_setup_methods(
        self,
        menu_integration,
        mock_menu_provider
    ):
        """Test that setup() calls both setup_menu() and setup_toolbar()."""
        menu_integration.setup()
        
        # Should have menu items
        items = mock_menu_provider.get_menu_items("Tools")
        assert len(items) == 3
        
        # Should have toolbar button
        buttons = mock_menu_provider.get_toolbar_buttons("main")
        assert len(buttons) == 1
    
    def test_is_setup_property(self, menu_integration):
        """Test the is_setup property."""
        assert menu_integration.is_setup is False
        
        menu_integration.setup()
        
        assert menu_integration.is_setup is True
    
    def test_teardown_removes_menu_items(
        self,
        menu_integration,
        mock_menu_provider
    ):
        """Test that teardown removes all menu items."""
        menu_integration.setup()
        
        # Verify items exist
        assert len(mock_menu_provider.get_menu_items("Tools")) == 3
        
        menu_integration.teardown()
        
        # Verify items removed
        assert len(mock_menu_provider.get_menu_items("Tools")) == 0
    
    def test_teardown_removes_toolbar_buttons(
        self,
        menu_integration,
        mock_menu_provider
    ):
        """Test that teardown removes all toolbar buttons."""
        menu_integration.setup()
        
        # Verify button exists
        assert len(mock_menu_provider.get_toolbar_buttons("main")) == 1
        
        menu_integration.teardown()
        
        # Verify button removed
        assert len(mock_menu_provider.get_toolbar_buttons("main")) == 0
    
    def test_teardown_resets_setup_flag(self, menu_integration):
        """Test that teardown resets the is_setup flag."""
        menu_integration.setup()
        assert menu_integration.is_setup is True
        
        menu_integration.teardown()
        assert menu_integration.is_setup is False
    
    def test_menu_action_count_property(self, menu_integration):
        """Test the menu_action_count property."""
        assert menu_integration.menu_action_count == 0
        
        menu_integration.setup_menu()
        
        assert menu_integration.menu_action_count == 3
    
    def test_toolbar_action_count_property(self, menu_integration):
        """Test the toolbar_action_count property."""
        assert menu_integration.toolbar_action_count == 0
        
        menu_integration.setup_toolbar()
        
        assert menu_integration.toolbar_action_count == 1
    
    def test_double_setup_menu_is_idempotent(
        self,
        menu_integration,
        mock_menu_provider
    ):
        """Test that calling setup_menu twice does not duplicate items."""
        menu_integration.setup_menu()
        menu_integration.setup_toolbar()  # This sets _setup_complete
        
        # Try to setup menu again
        menu_integration.setup_menu()
        
        # Should still only have 3 items
        items = mock_menu_provider.get_menu_items("Tools")
        assert len(items) == 3


# ============================================================================
# MenuIntegration Tests - Callable Support
# ============================================================================

class TestMenuIntegrationCallableSupport:
    """Tests for MenuIntegration with callable UI components."""
    
    def test_callable_dashboard_is_called(self, mock_menu_provider):
        """Test that a callable dashboard is called when menu item triggered."""
        # Use a simple function instead of MagicMock to avoid hasattr('show') returning True
        call_count = [0]
        def dashboard_callback():
            call_count[0] += 1
        
        integration = MenuIntegration(
            dashboard=dashboard_callback,
            game_window=None,
            settings_panel=None,
            menu_provider=mock_menu_provider
        )
        
        integration.setup_menu()
        mock_menu_provider.trigger_menu_item(
            "Tools",
            MenuIntegration.MENU_DASHBOARD
        )
        
        assert call_count[0] == 1
    
    def test_callable_game_window_is_called(self, mock_menu_provider):
        """Test that a callable game window is called when triggered."""
        # Use a simple function instead of MagicMock to avoid hasattr('show') returning True
        call_count = [0]
        def game_window_callback():
            call_count[0] += 1
        
        integration = MenuIntegration(
            dashboard=None,
            game_window=game_window_callback,
            settings_panel=None,
            menu_provider=mock_menu_provider
        )
        
        integration.setup_toolbar()
        mock_menu_provider.trigger_toolbar_button(
            "main",
            MenuIntegration.TOOLBAR_GAME_WINDOW
        )
        
        assert call_count[0] == 1
    
    def test_callable_settings_is_called(self, mock_menu_provider):
        """Test that a callable settings panel is called when triggered."""
        # Use a simple function instead of MagicMock to avoid hasattr('show') returning True
        call_count = [0]
        def settings_callback():
            call_count[0] += 1
        
        integration = MenuIntegration(
            dashboard=None,
            game_window=None,
            settings_panel=settings_callback,
            menu_provider=mock_menu_provider
        )
        
        integration.setup_menu()
        mock_menu_provider.trigger_menu_item(
            "Tools",
            MenuIntegration.MENU_SETTINGS
        )
        
        assert call_count[0] == 1


# ============================================================================
# MenuIntegration Tests - Error Handling
# ============================================================================

class TestMenuIntegrationErrorHandling:
    """Tests for MenuIntegration error handling."""
    
    def test_dashboard_error_is_caught(self, mock_menu_provider):
        """Test that errors in dashboard.show() are caught."""
        dashboard = MagicMock()
        dashboard.show.side_effect = Exception("Dashboard error")
        
        integration = MenuIntegration(
            dashboard=dashboard,
            game_window=None,
            settings_panel=None,
            menu_provider=mock_menu_provider
        )
        
        integration.setup_menu()
        
        # Should not raise
        mock_menu_provider.trigger_menu_item(
            "Tools",
            MenuIntegration.MENU_DASHBOARD
        )
    
    def test_game_window_error_is_caught(self, mock_menu_provider):
        """Test that errors in game_window.show() are caught."""
        game_window = MagicMock()
        game_window.show.side_effect = Exception("Game window error")
        
        integration = MenuIntegration(
            dashboard=None,
            game_window=game_window,
            settings_panel=None,
            menu_provider=mock_menu_provider
        )
        
        integration.setup_toolbar()
        
        # Should not raise
        mock_menu_provider.trigger_toolbar_button(
            "main",
            MenuIntegration.TOOLBAR_GAME_WINDOW
        )
    
    def test_settings_error_is_caught(self, mock_menu_provider):
        """Test that errors in settings_panel.show() are caught."""
        settings = MagicMock()
        settings.show.side_effect = Exception("Settings error")
        
        integration = MenuIntegration(
            dashboard=None,
            game_window=None,
            settings_panel=settings,
            menu_provider=mock_menu_provider
        )
        
        integration.setup_menu()
        
        # Should not raise
        mock_menu_provider.trigger_menu_item(
            "Tools",
            MenuIntegration.MENU_SETTINGS
        )


# ============================================================================
# Integration Tests
# ============================================================================

class TestMenuIntegrationIntegration:
    """Integration tests for MenuIntegration."""
    
    def test_full_workflow(
        self,
        mock_dashboard,
        mock_game_window,
        mock_settings_panel,
        mock_menu_provider
    ):
        """Test the full workflow: setup, use, teardown."""
        # Create integration
        integration = MenuIntegration(
            dashboard=mock_dashboard,
            game_window=mock_game_window,
            settings_panel=mock_settings_panel,
            menu_provider=mock_menu_provider
        )
        
        # Setup
        integration.setup()
        assert integration.is_setup is True
        assert integration.menu_action_count == 3
        assert integration.toolbar_action_count == 1
        
        # Use menu items
        mock_menu_provider.trigger_menu_item("Tools", MenuIntegration.MENU_DASHBOARD)
        mock_dashboard.show.assert_called_once()
        
        mock_menu_provider.trigger_menu_item("Tools", MenuIntegration.MENU_GAME_WINDOW)
        mock_game_window.show.assert_called_once()
        
        mock_menu_provider.trigger_menu_item("Tools", MenuIntegration.MENU_SETTINGS)
        mock_settings_panel.show.assert_called_once()
        
        # Use toolbar button
        mock_menu_provider.trigger_toolbar_button("main", MenuIntegration.TOOLBAR_GAME_WINDOW)
        assert mock_game_window.show.call_count == 2  # Called twice now
        
        # Teardown
        integration.teardown()
        assert integration.is_setup is False
        assert integration.menu_action_count == 0
        assert integration.toolbar_action_count == 0
        assert len(mock_menu_provider.get_menu_items("Tools")) == 0
        assert len(mock_menu_provider.get_toolbar_buttons("main")) == 0
