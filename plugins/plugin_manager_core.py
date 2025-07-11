"""Core implementation of dockevOS Plugin Manager.

This module was split out of the package-level directory plugin to avoid the
"relative import with no known parent package" issue that arose when the
package tried to load its own single-file implementation dynamically.  All
other code should continue to import ``plugins.plugin_manager``.  The package
re-exports every public symbol from this module.
"""

from __future__ import annotations

import asyncio
import importlib
import inspect
from pathlib import Path
from typing import Any, Callable, Dict, List

from plugins.error_handler import get_error_handler, ErrorHandler  # absolute
from plugins.hardware_analyzer import (
    get_hardware_analyzer,
    HardwareAnalyzer,
)
from plugins.docker_manager import get_docker_manager, DockerManager

__all__ = [
    "PluginManager",
    "plugin_manager",
    "get_plugin_manager",
]


class PluginManager:
    """Load, manage and introspect dockevOS plugins."""

    def __init__(self) -> None:
        self.plugins_dir = Path(__file__).parent  # plugins/ directory
        self.plugins: Dict[str, Any] = {}
        self.command_handlers: Dict[str, Callable] = {}
        self.event_handlers: Dict[str, List[Callable]] = {}

        # Core services
        self.error_handler: ErrorHandler = get_error_handler()
        self.hardware_analyzer: HardwareAnalyzer = get_hardware_analyzer()
        self.docker_manager: DockerManager = get_docker_manager()

        self._register_core_commands()

    # ---------------------------------------------------------------------
    # Command registration helpers
    # ---------------------------------------------------------------------

    def _register_core_commands(self) -> None:
        self.register_command("help", self.show_help)
        self.register_command("plugins", self.list_plugins)
        self.register_command("reload", self.reload_plugins)

    def register_command(self, name: str, handler: Callable) -> None:
        self.command_handlers[name.lower()] = handler

    def register_event_handler(self, event: str, handler: Callable) -> None:
        self.event_handlers.setdefault(event, []).append(handler)

    # ---------------------------------------------------------------------
    # Plugin loading / reloading
    # ---------------------------------------------------------------------

    async def load_plugins(self) -> None:
        print("\n🔌 Loading plugins…")

        core_plugins: list[str] = [
            "error_handler",
            "hardware_analyzer",
            "docker_manager",
        ]
        for plugin_name in core_plugins:
            self._load_plugin(f"plugins.{plugin_name}")

        # Other plugins live in sub-directories that contain __init__.py
        for entry in self.plugins_dir.iterdir():
            if not entry.is_dir():
                continue
            name = entry.name
            if name in core_plugins or name.startswith("_") or name == "__pycache__":
                continue
            if not (entry / "__init__.py").exists():
                continue
            self._load_plugin(f"plugins.{name}")

        print(f"✅ Loaded {len(self.plugins)} plugins")

    def _load_plugin(self, module_name: str) -> None:
        try:
            # Skip if already loaded
            if module_name in self.plugins:
                return

            module = importlib.import_module(module_name)

            # If a plugin defines setup() use its return value; else module
            plugin_obj = None
            if hasattr(module, "setup"):
                plugin_obj = module.setup()
                if asyncio.iscoroutine(plugin_obj):
                    plugin_obj = asyncio.run(plugin_obj)
            if plugin_obj is None:
                plugin_obj = module

            self.plugins[module_name] = plugin_obj
            print(f"  ✅ {module_name.split('.')[-1]}")

            # Register commands / events
            if hasattr(plugin_obj, "commands"):
                for cmd, hnd in plugin_obj.commands.items():
                    self.register_command(cmd, hnd)
            if hasattr(plugin_obj, "event_handlers"):
                for evt, hnd in plugin_obj.event_handlers.items():
                    self.register_event_handler(evt, hnd)
        except Exception as exc:  # pragma: no cover – displayed to user
            self.error_handler.log_error(exc, {"plugin": module_name, "action": "load"})
            print(f"  ❌ {module_name.split('.')[-1]} – {exc}")

    async def reload_plugins(self, *_: Any) -> bool:  # command handler
        print("\n🔄 Reloading plugins…")
        self.plugins.clear()
        self.command_handlers.clear()
        self.event_handlers.clear()

        # Refresh core services (they might have hot-reloaded)
        self.error_handler = get_error_handler()
        self.hardware_analyzer = get_hardware_analyzer()
        self.docker_manager = get_docker_manager()
        self._register_core_commands()

        await self.load_plugins()
        return True

    # ------------------------------------------------------------------
    # Shell helpers
    # ------------------------------------------------------------------

    async def execute_command(self, cmd: str, args: list[str] | None = None) -> bool:
        args = args or []
        cmd = cmd.lower()

        if cmd in self.command_handlers:
            return await self._safe_call(self.command_handlers[cmd], args)

        matches = [c for c in self.command_handlers if c.startswith(cmd)]
        if len(matches) == 1:
            return await self._safe_call(self.command_handlers[matches[0]], args)
        if len(matches) > 1:
            print("❓ Did you mean one of: " + ", ".join(matches))
            return False
        return False

    async def _safe_call(self, handler: Callable, args: list[str]) -> bool:
        try:
            if inspect.iscoroutinefunction(handler):
                return await handler(*args)
            return handler(*args)  # type: ignore[call-arg]
        except Exception as exc:
            self.error_handler.log_error(exc, {"command": handler.__name__, "args": args})
            print(f"❌ Error executing command: {exc}")
            return False

    # ------------------------------------------------------------------
    # Built-in command implementations
    # ------------------------------------------------------------------

    async def show_help(self, *args: Any) -> bool:  # noqa: D401
        print("\n📚 Available commands:")
        for cmd in sorted(self.command_handlers):
            if cmd in {"help", "plugins", "reload"}:
                continue
            print("  •", cmd)
        return True

    async def list_plugins(self, *_: Any) -> bool:
        if not self.plugins:
            print("No plugins loaded")
            return True
        print("\n🔌 Loaded Plugins:")
        for name in sorted(self.plugins):
            print("  •", name)
        return True


# Singleton + public helper
plugin_manager = PluginManager()

def register(event_bus, shell):
    """Register the plugin manager core plugin
    
    Args:
        event_bus: The event bus instance
        shell: The shell instance
    """
    # The plugin manager is a core service that doesn't need to register commands
    # as it's already available through the shell
    print("📦 Plugin Manager Core loaded")
    return plugin_manager

def get_plugin_manager() -> PluginManager:  # noqa: D401 – simple accessor
    return plugin_manager
