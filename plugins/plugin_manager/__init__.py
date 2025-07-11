"""dockevOS Plugin Manager (Core)
================================

This package is a thin wrapper that exposes the core `plugin_manager` singleton
and related classes while satisfying the rule that **every plugin (even the
manager itself) lives in its own directory with an `__init__.py`.**

It simply re-exports the contents of the legacy module
`plugins.plugin_manager` so other modules can continue to import
`plugins.plugin_manager` as before.
"""

from importlib import import_module

# Import the original, single-file implementation and re-export everything so
# that users of `plugins.plugin_manager` see the same public API.
_core_mod = import_module("plugins.plugin_manager")

# Re-export its attributes at package level (except dunder internals)
globals().update({k: v for k, v in _core_mod.__dict__.items() if not k.startswith("__")})

__all__ = [k for k in globals() if not k.startswith("__")]
