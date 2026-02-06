"""
Shared pytest fixtures for NintendAnki tests.

This module provides common fixtures used across test modules,
including Qt application setup for UI tests.
"""

import pytest
import sys


# Qt application fixture for UI tests
@pytest.fixture(scope="session")
def qapp():
    """Create a QApplication instance for the test session.
    
    This fixture is required for any tests that use PyQt widgets.
    It creates a single QApplication instance that is shared across
    all tests in the session.
    """
    try:
        from PyQt6.QtWidgets import QApplication
        from PyQt6.QtCore import Qt
        
        # Check if an application already exists
        app = QApplication.instance()
        if app is None:
            # Create new application with offscreen platform for headless testing
            app = QApplication(sys.argv)
        
        yield app
        
    except ImportError:
        try:
            from PyQt5.QtWidgets import QApplication
            from PyQt5.QtCore import Qt
            
            app = QApplication.instance()
            if app is None:
                app = QApplication(sys.argv)
            
            yield app
            
        except ImportError:
            # No PyQt available, yield None
            yield None


@pytest.fixture(autouse=True)
def setup_qt_for_tests(qapp):
    """Automatically set up Qt for tests that need it.
    
    This fixture runs before each test and ensures the Qt
    application is available.
    """
    yield qapp
