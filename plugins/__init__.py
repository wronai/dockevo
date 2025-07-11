""
dockevOS Plugin System
======================

This package contains the core plugin system for dockevOS, including:
- Plugin Manager: Handles loading and managing plugins
- Error Handler: Centralized error handling and logging
- Hardware Analyzer: System compatibility checking
- Docker Manager: Container and service management

To create a new plugin, add a Python module in this directory with a `setup()` function
that returns an instance of your plugin class.
"""

# Import core components for easier access
from .plugin_manager import get_plugin_manager, PluginManager
from .error_handler import get_error_handler, ErrorHandler
from .hardware_analyzer import get_hardware_analyzer, HardwareAnalyzer
from .docker_manager import get_docker_manager, DockerManager

# Export public API
__all__ = [
    'get_plugin_manager', 'PluginManager',
    'get_error_handler', 'ErrorHandler',
    'get_hardware_analyzer', 'HardwareAnalyzer',
    'get_docker_manager', 'DockerManager'
]
