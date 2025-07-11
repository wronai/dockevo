"""dockevOS Plugin Manager Package
================================

This directory plugin allows `plugins.plugin_manager` to behave as normal while
keeping the actual implementation in `plugins.plugin_manager_core`.  All public
symbols are re-exported so existing imports continue to work.
`plugins.plugin_manager` as before.
"""

from importlib import import_module as _import

_core_mod = _import("plugins.plugin_manager_core")

globals().update({k: v for k, v in _core_mod.__dict__.items() if not k.startswith("__")})

def register(event_bus, shell):
    """Register the plugin manager plugin
    
    Args:
        event_bus: The event bus instance
        shell: The shell instance
    """
    # The plugin manager is a special case that doesn't need to register commands
    # as it's already available through the shell
    print("📦 Plugin Manager loaded")
    return plugin_manager

__all__ = [k for k in globals() if not k.startswith("__")] + ['register']
