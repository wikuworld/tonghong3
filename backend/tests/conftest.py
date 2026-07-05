"""Pytest fixtures for Tonghong ERP backend tests."""

import pytest
from unittest.mock import MagicMock


@pytest.fixture
def db_session():
    return MagicMock()
