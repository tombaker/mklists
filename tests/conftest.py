"""Reinitializes class variables in Rule class."""

import pytest
from mklists.rules import Rule


@pytest.fixture()
def reinitialize_ruleclass_variables():
    """Reinitializes class variables in Rule class."""
    Rule.sources_list = []
    Rule.sources_list_is_initialized = False
