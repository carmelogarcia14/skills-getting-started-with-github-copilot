"""Pytest configuration and fixtures for integration tests."""

import pytest
from fastapi.testclient import TestClient
from src.app import app, activities


@pytest.fixture
def client():
    """Provide a TestClient instance for testing FastAPI endpoints."""
    return TestClient(app)


@pytest.fixture
def reset_activities():
    """
    Reset activities to initial state before each test.
    This fixture clears all participants and ensures test isolation.
    """
    yield  # Test runs here
    
    # Reset participants after test
    for activity in activities.values():
        activity["participants"] = []


@pytest.fixture(autouse=True)
def clean_state(reset_activities):
    """
    Auto-use fixture that ensures clean state for every test.
    This clears all participants before and after each test.
    """
    # Clear before test
    for activity in activities.values():
        activity["participants"] = []
    
    yield  # Test runs here
    
    # Clean up is handled by reset_activities fixture
