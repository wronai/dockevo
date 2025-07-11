"""
Plugin Manager for dockevOS
Handles loading, unloading, and managing plugins
"""

import importlib
import asyncio
import inspect
import pkgutil
from pathlib import Path
from typing import Dict, List, Optional, Type, Any, Callable

from .error_handler import get_error_handler, ErrorHandler
from .hardware_analyzer import get_hardware_analyzer, HardwareAnalyzer
from .docker_manager import get_docker_manager, DockerManager

class PluginManager:
    def __init__(self):
        self.plugins_dir = Path(__file__).parent
        self.plugins: Dict[str, Any] = {}
        self.command_handlers: Dict[str, Callable] = {}
        self.event_handlers: Dict[str, List[Callable]] = {}
        
        # Initialize core services
        self.error_handler = get_error_handler()
        self.hardware_analyzer = get_hardware_analyzer()
        self.docker_manager = get_docker_manager()
        
        # Register core commands
        self._register_core_commands()
    
    def _register_core_commands(self):
        """Register core commands"""
        self.register_command('help', self.show_help)
        self.register_command('plugins', self.list_plugins)
        self.register_command('reload', self.reload_plugins)
    
    async def load_plugins(self):
        """Load all plugins from the plugins directory"""
        print("\n🔌 Loading plugins...")
        
        # Load core plugins first
        core_plugins = ['error_handler', 'hardware_analyzer', 'docker_manager']
        for plugin_name in core_plugins:
            self._load_plugin(f'plugins.{plugin_name}')
        
        # Load other plugins (only subdirectories with __init__.py)
        for entry in self.plugins_dir.iterdir():
            if not entry.is_dir():
                continue  # Only consider directories as plugins
            name = entry.name
            if name in core_plugins or name in {'__pycache__'} or name.startswith('_'):
                continue
            if not (entry / '__init__.py').exists():
                continue  # Not a Python package
            self._load_plugin(f'plugins.{name}')
        
        print(f"✅ Loaded {len(self.plugins)} plugins")
    
    def _load_plugin(self, module_name: str):
        """Load a single plugin by module name"""
        try:
            module = importlib.import_module(module_name)
            
            # Skip if already loaded
            if module_name in self.plugins:
                return
            
            # Initialize plugin if it has a setup function
            if hasattr(module, 'setup'):
                plugin_obj = module.setup()
                # If the setup function returns a coroutine, run it synchronously
                if asyncio.iscoroutine(plugin_obj):
                    plugin_obj = asyncio.run(plugin_obj)
                plugin = plugin_obj
                self.plugins[module_name] = plugin
                print(f"  ✅ {module_name.split('.')[-1]}")
                
                # Register commands if available
                if hasattr(plugin, 'commands'):
                    for cmd, handler in plugin.commands.items():
                        self.register_command(cmd, handler)
                
                # Register event handlers if available
                if hasattr(plugin, 'event_handlers'):
                    for event, handler in plugin.event_handlers.items():
                        self.register_event_handler(event, handler)
            
        except Exception as e:
            self.error_handler.log_error(e, {'plugin': module_name, 'action': 'load'})
            print(f"  ❌ {module_name.split('.')[-1]} - {str(e)}")
    
    async def reload_plugins(self, *args):
        """Reload all plugins"""
        print("\n🔄 Reloading plugins...")
        
        # Clear existing plugins and commands
        self.plugins.clear()
        self.command_handlers.clear()
        self.event_handlers.clear()
        
        # Reload core services
        self.error_handler = get_error_handler()
        self.hardware_analyzer = get_hardware_analyzer()
        self.docker_manager = get_docker_manager()
        
        # Re-register core commands
        self._register_core_commands()
        
        # Reload all plugins
        await self.load_plugins()
        
        print("✅ Plugins reloaded")
        return True
    
    def register_command(self, name: str, handler: Callable):
        """Register a command handler"""
        self.command_handlers[name.lower()] = handler
    
    def register_event_handler(self, event: str, handler: Callable):
        """Register an event handler"""
        if event not in self.event_handlers:
            self.event_handlers[event] = []
        self.event_handlers[event].append(handler)
    
    async def execute_command(self, command: str, args: List[str] = None) -> bool:
        """Execute a command with arguments"""
        args = args or []
        cmd = command.lower()
        
        # Check for exact match first
        if cmd in self.command_handlers:
            try:
                return await self._call_handler(self.command_handlers[cmd], args)
            except Exception as e:
                self.error_handler.log_error(e, {'command': cmd, 'args': args})
                print(f"❌ Error executing command: {e}")
                return False
        
        # Check for partial matches
        matches = [c for c in self.command_handlers if c.startswith(cmd)]
        
        if len(matches) == 1:
            try:
                return await self._call_handler(self.command_handlers[matches[0]], args)
            except Exception as e:
                self.error_handler.log_error(e, {'command': matches[0], 'args': args})
                print(f"❌ Error executing command: {e}")
                return False
        elif len(matches) > 1:
            print(f"❓ Did you mean one of these?\n  " + "\n  ".join(matches))
            return False
        
        # No handler found
        return False
    
    async def _call_handler(self, handler: Callable, args: List[str]) -> bool:
        """Call a command handler with proper argument handling"""
        if inspect.iscoroutinefunction(handler):
            return await handler(*args)
        else:
            return handler(*args)
    
    async def emit_event(self, event: str, *args, **kwargs):
        """Emit an event to all registered handlers"""
        if event not in self.event_handlers:
            return
            
        for handler in self.event_handlers[event]:
            try:
                if inspect.iscoroutinefunction(handler):
                    await handler(*args, **kwargs)
                else:
                    handler(*args, **kwargs)
            except Exception as e:
                self.error_handler.log_error(e, {'event': event, 'handler': handler.__name__})
    
    async def show_help(self, *args):
        """Show help for all commands"""
        print("\n📚 Available Commands:")
        print("-" * 80)
        
        # Group commands by plugin
        commands_by_plugin: Dict[str, List[str]] = {}
        
        for cmd in sorted(self.command_handlers.keys()):
            # Skip internal commands
            if cmd in ['help', 'plugins', 'reload']:
                continue
                
            # Get the plugin that registered this command
            plugin_name = 'System'
            for plugin in self.plugins.values():
                if hasattr(plugin, 'commands') and cmd in plugin.commands:
                    plugin_name = plugin.__class__.__name__.replace('Plugin', '')
                    break
            
            if plugin_name not in commands_by_plugin:
                commands_by_plugin[plugin_name] = []
            commands_by_plugin[plugin_name].append(cmd)
        
        # Print system commands first
        if 'System' in commands_by_plugin:
            print("\n🔧 System Commands:")
            print("  " + ", ".join(sorted(commands_by_plugin.pop('System'))))
        
        # Print plugin commands
        for plugin, cmds in sorted(commands_by_plugin.items()):
            print(f"\n🔌 {plugin} Commands:")
            print("  " + ", ".join(sorted(cmds)))
        
        print("\nType 'help <command>' for more information about a command")
        return True
    
    async def list_plugins(self, *args):
        """List all loaded plugins"""
        if not self.plugins:
            print("No plugins loaded")
            return True
            
        print("\n🔌 Loaded Plugins:")
        print("-" * 80)
        
        for name, plugin in self.plugins.items():
            plugin_name = name.split('.')[-1]
            version = getattr(plugin, 'VERSION', '1.0.0')
            description = getattr(plugin, 'DESCRIPTION', 'No description')
            
            print(f"📦 {plugin_name} (v{version})")
            print(f"   {description}")
            
            # List commands provided by this plugin
            if hasattr(plugin, 'commands'):
                cmds = ", ".join(sorted(plugin.commands.keys()))
                print(f"   Commands: {cmds}")
            
            print()
        
        return True

# Create a singleton instance
plugin_manager = PluginManager()

def get_plugin_manager() -> PluginManager:
    """Get the global plugin manager instance"""
    return plugin_manager
