# Plugin Manager (Core)

This directory wraps the **core plugin system** for dockevOS.

* `__init__.py` – thin wrapper that re-exports the legacy single-file implementation found at `plugins/plugin_manager.py` so that the loader can treat the manager itself as a folder-style plugin.
* _Not a real plugin_: the manager is required before any other plugin can load and therefore is marked as **core** in discovery.
