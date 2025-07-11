"""
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


"""Lazy access helpers to core plugin system components."""

def get_plugin_manager():
    from .plugin_manager import plugin_manager  # noqa: import inside
    return plugin_manager

def get_error_handler():
    from .error_handler import error_handler
    return error_handler

def get_hardware_analyzer():
    from .hardware_analyzer import hardware_analyzer
    return hardware_analyzer

def get_docker_manager():
    from .docker_manager import docker_manager
    return docker_manager

# Public API names
PluginManager = 'PluginManager'
ErrorHandler = 'ErrorHandler'
HardwareAnalyzer = 'HardwareAnalyzer'
DockerManager = 'DockerManager'

def register(event_bus, shell):
    """Register core plugins with the system
    
    Args:
        event_bus: The event bus instance
        shell: The shell instance
    """
    # Core plugins are already loaded and registered
    print("📦 Core plugins loaded")
    return {
        'plugin_manager': get_plugin_manager(),
        'error_handler': get_error_handler(),
        'hardware_analyzer': get_hardware_analyzer(),
        'docker_manager': get_docker_manager()
    }

# Export public API
__all__ = [
    'get_plugin_manager', 'get_error_handler',
    'get_hardware_analyzer', 'get_docker_manager',
    'register'
]
