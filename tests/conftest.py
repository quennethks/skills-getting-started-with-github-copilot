"""Shared pytest fixtures for FastAPI backend tests."""

import copy

import pytest
from fastapi.testclient import TestClient

from src import app as app_module


@pytest.fixture
def client() -> TestClient:
    """Provide a test client for the FastAPI app."""
    return TestClient(app_module.app)


@pytest.fixture(autouse=True)
def restore_activities_state():
    """Reset the in-memory activities store after every test."""
    original_activities = copy.deepcopy(app_module.activities)

    yield

    app_module.activities.clear()
    app_module.activities.update(original_activities)
