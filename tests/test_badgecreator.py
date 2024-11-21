"""
Unit tests for the `badgecreator.py` module.

This file contains tests to validate the functionality of the `create_badge` function,
ensuring it works correctly for valid inputs and handles errors gracefully.
"""

import os

import pytest

from badgecreator import create_badge

LOGO_PATH = os.path.join("resources", "heroku_logo.png")

@pytest.fixture(scope="module")
def setup_environment():
    """
    Fixture to verify the testing environment is set up correctly.

    Ensures that required resources like the logo file are available.
    """
    assert os.path.exists(LOGO_PATH), f"{LOGO_PATH} does not exist."

def test_create_badge_success(setup_environment):
    """
    Test successful badge creation with valid input.

    Verifies that the `create_badge` function returns a valid Base64-encoded PNG image.
    """
    line1 = "Test line 1"
    line2 = "Test line 2"
    badge = create_badge(line1, line2)

    assert isinstance(badge, str), "Badge should be a Base64-encoded string"
    assert badge.startswith("iVBORw0KGgo"), "Badge should be a Base64-encoded string"

def test_create_badge_invalid_logo_path(monkeypatch):
    """
    Test error handling for a missing logo file.

    Simulates an invalid logo file path to ensure the `create_badge` function raises a
    `FileNotFoundError`.
    """
    def mock_join(*args):
        return "invalid/path/to/heroku_logo.png"

    monkeypatch.setattr(os.path, "join", mock_join)

    with pytest.raises(FileNotFoundError):
        create_badge("Test line 1", "Test line 2")