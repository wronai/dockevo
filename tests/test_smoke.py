"""Basic smoke tests for dockevOS package.

Currently the goal is simply to ensure that the core package imports without
errors and the plugin manager can instantiate. These tests act as a guard for
CI so that the `make test` target does not fail when no user tests exist yet.
"""

import importlib
import sys
from pathlib import Path
# Ensure project root on path for editable import without install
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def test_import_package():
    """dockevos package should import successfully."""
    module = importlib.import_module("dockevos.__main__")
    assert module is not None


def test_plugin_manager_singleton():
    """Global plugin_manager should be creatable and expose expected attrs."""
    plugins_mod = importlib.import_module("plugins.plugin_manager")
    assert hasattr(plugins_mod, "plugin_manager"), "plugin_manager singleton missing"
