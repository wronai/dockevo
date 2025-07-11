"""Plugin Generator for dockevOS

Generates new plugin skeletons from simple templates. This has been refactored
from the original single-file script into a proper folder-based plugin so that
it loads cleanly alongside the rest of the plugin ecosystem.
"""

from __future__ import annotations

import textwrap
import time
from pathlib import Path
from typing import Dict, List

# ---------------------------------------------------------------------------
# Template definitions (trimmed for brevity; add more as needed)
# ---------------------------------------------------------------------------
TEMPLATES: Dict[str, Dict] = {
    "basic": {
        "description": "Basic plugin template with stub commands",
        "dependencies": [],
        "features": ["commands"],
    }
}


# ---------------------------------------------------------------------------
# Helper for generating code
# ---------------------------------------------------------------------------

def _create_basic_plugin(plugin_name: str) -> str:
    """Return Python source for a minimal plugin."""

    ts = time.strftime("%Y-%m-%d %H:%M:%S")
    return textwrap.dedent(
        f'''
        """{plugin_name.title()} Plugin (generated {ts})"""

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


# ---------------------------------------------------------------------------
# Main plugin class
# ---------------------------------------------------------------------------

class PluginGenerator:
    VERSION = "1.0.0"
    DESCRIPTION = "Generate new plugins from templates"

    def __init__(self, event_bus, shell):
        self.event_bus = event_bus
        self.shell = shell
        self.commands: Dict[str, callable] = {}
        self.register_commands()

    # ---------------- Commands ----------------

    def register_commands(self):
        self._register("templates", self.cmd_list_templates)
        self._register("generate", self.cmd_generate)

    def _register(self, name: str, handler):
        self.shell.register_command(name, handler)
        self.commands[name] = handler

    # Command implementations

    def cmd_list_templates(self, event):
        lines = ["🧩 Available templates:\n"]
        for name, info in TEMPLATES.items():
            lines.append(f"  • {name:12} – {info['description']}")
        return "\n".join(lines)

    def cmd_generate(self, event):
        args: List[str] = event.data.get("args", [])
        if len(args) < 3 or args[0] != "plugin":
            return "Usage: generate plugin <template> <plugin_name>"

        template, plugin_name = args[1], args[2]
        if template not in TEMPLATES:
            return f"❌ Unknown template: {template}. Run 'templates' for a list."

        # For now we only support the basic template
        code = _create_basic_plugin(plugin_name)
        plugin_dir = Path("plugins") / plugin_name
        plugin_dir.mkdir(parents=True, exist_ok=True)
        with open(plugin_dir / "__init__.py", "w", encoding="utf-8") as fp:
            fp.write(code)

        return (
            f"✅ Plugin '{plugin_name}' created using '{template}' template.\n"
            "Reload plugins (command: reload) or restart dockevOS to activate it."
        )


# ---------------------------------------------------------------------------
# Plugin setup expected by Plugin Manager
# ---------------------------------------------------------------------------

def setup():  # noqa: D401 – simple factory
    from plugins.plugin_manager import get_plugin_manager  # lazy import

    pm = get_plugin_manager()
    return PluginGenerator(pm, pm)  # event_bus and shell are both pm for now
