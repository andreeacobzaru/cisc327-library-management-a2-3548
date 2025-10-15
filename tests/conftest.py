"""
Pytest configuration file for automatic test setup to clear database and add sample data.
"""

import pytest
from .util import setup_pretest_database

@pytest.fixture(scope="session", autouse=True)
def setup_database():
    """
    Automatic fixture that runs once per test session (when pytest is called).
    This ensures the entire test suite starts with a clean database state.
    """
    setup_pretest_database()
    yield 
