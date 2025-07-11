"""Plugin templates for the dockevOS plugin-generator.

Separate file so that new templates can be added without touching the main
code.  Each template entry contains a short description, optional install
dependencies and a list of advertised features.
"""
from __future__ import annotations

from pathlib import Path
import textwrap
import time
from typing import Dict

TEMPLATES: Dict[str, Dict] = {
    "basic": {
        "description": "Basic plugin template with stub hello command",
        "dependencies": [],
        "features": ["commands"],
    },
}


def create_basic_plugin(plugin_name: str) -> str:  # noqa: D401
    """Return Python source code for a minimal plugin.

    This helper keeps the code-generation logic separate from CLI/shell logic.
    """
    ts = time.strftime("%Y-%m-%d %H:%M:%S")
    return textwrap.dedent(
        f'''"""{plugin_name.title()} Plugin (generated {ts})"""

VERSION = "0.1.0"
DESCRIPTION = "Auto-generated basic plugin"
commands = {{}}


def register(event_bus, shell):
    """Register plugin commands with the shell."""
    def cmd_hello(event):
        name = (event.data.get("args") or ["World"])[0]
        return f"Hello, {{name}} from {plugin_name}!"

    shell.register_command("{plugin_name}-hello", cmd_hello)
    commands["{plugin_name}-hello"] = cmd_hello
    print("📦 {plugin_name} plugin loaded → {plugin_name}-hello")


def unregister(event_bus, shell):
    shell.unregister_command("{plugin_name}-hello")
    print("📦 {plugin_name} plugin unloaded")
'''
    )
