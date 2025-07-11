"""dockevOS Plugin Manager (Core)
================================

This package is a thin wrapper that exposes the core `plugin_manager` singleton
and related classes while satisfying the rule that **every plugin (even the
manager itself) lives in its own directory with an `__init__.py`.**

It simply re-exports the contents of the legacy module
`plugins.plugin_manager` so other modules can continue to import
`plugins.plugin_manager` as before.
"""

import importlib.util
import importlib.machinery
from pathlib import Path

# ---------------------------------------------------------------------------
# Dynamically load the original single-file implementation that lives one
# directory up (plugins/plugin_manager.py).  We register it under a private
# module name to avoid circular-import issues, then re-export its public API.
# ---------------------------------------------------------------------------
_core_path = Path(__file__).parent.parent / "plugin_manager.py"

# Construct a new module spec + module object
_spec = importlib.util.spec_from_file_location("plugins._plugin_manager_core", _core_path)
_core_mod = importlib.util.module_from_spec(_spec)
loader = _spec.loader  # type: ignore[attr-defined]
assert loader is not None
loader.exec_module(_core_mod)  # type: ignore[arg-type]

# Inject into sys.modules so `import plugins._plugin_manager_core` works
import sys as _sys
_sys.modules[_spec.name] = _core_mod

# Re-export everything except dunder names so
# `import plugins.plugin_manager` gives the same symbols.
globals().update({k: v for k, v in _core_mod.__dict__.items() if not k.startswith("__")})

__all__ = [k for k in globals() if not k.startswith("__")]
