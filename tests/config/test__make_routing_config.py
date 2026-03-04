"""Tests for $MKLMKL/config.py"""

import re
import yaml
from pathlib import Path
import pytest
from mklists.config.resolve import _make_routing_config


