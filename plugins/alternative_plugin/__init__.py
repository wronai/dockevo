"""
Alternative Plugin Manager for dockevOS
Handles fallback functionality when plugins are missing or permissions are denied
"""

import importlib
import inspect
from typing import Dict, List, Optional, Any, Type, Callable
from pathlib import Path

from ..error_handler import get_error_handler

class AlternativePlugin:
    VERSION = "1.0.0"
    DESCRIPTION = "Manages alternative implementations and fallbacks for plugins"
    
    def __init__(self):
        self.error_handler = get_error_handler()
        self.alternatives: Dict[str, List[Dict]] = {}
        self._load_alternatives()
        self._register_commands()
    
    def _load_alternatives(self):
        """Load alternative implementations for plugins"""
        self.alternatives = {
            'shell_assistant': [
                {
                    'name': 'manual_installer',
                    'description': 'Manual package installation guide',
                    'module': 'plugins.alternative.manual_installer',
                    'class': 'ManualInstaller'
                },
                {
                    'name': 'package_manager',
                    'description': 'Basic package manager interface',
                    'module': 'plugins.alternative.package_manager',
                    'class': 'PackageManager'
                }
            ],
            'voice_service': [
                {
                    'name': 'text_input',
                    'description': 'Fallback text input when voice is unavailable',
                    'module': 'plugins.alternative.text_input',
                    'class': 'TextInput'
                }
            ]
        }
    
    def get_alternatives(self, plugin_name: str) -> List[Dict]:
        """Get alternative implementations for a plugin"""
        return self.alternatives.get(plugin_name, [])
    
    async def suggest_alternative(self, plugin_name: str, reason: str = '') -> Optional[Dict]:
        """Suggest an alternative plugin"""
        alternatives = self.get_alternatives(plugin_name)
        if not alternatives:
            return None
            
        print(f"\n🔍 No suitable implementation found for {plugin_name}")
        if reason:
            print(f"   Reason: {reason}")
        
        print("\n🔄 Available alternatives:")
        for i, alt in enumerate(alternatives, 1):
            print(f"{i}. {alt['name']} - {alt['description']}")
        
        print(f"{len(alternatives) + 1}. Cancel")
        
        while True:
            try:
                choice = input("\nSelect an alternative (or press Enter to cancel): ").strip()
                if not choice:
                    return None
                    
                choice_idx = int(choice) - 1
                if 0 <= choice_idx < len(alternatives):
                    return alternatives[choice_idx]
                elif choice_idx == len(alternatives):
                    return None
                else:
                    print("❌ Invalid choice")
                    
            except ValueError:
                print("❌ Please enter a number")
    
    async def load_alternative(self, plugin_name: str, alternative: Dict) -> Any:
        """Load an alternative plugin implementation"""
        try:
            module = importlib.import_module(alternative['module'])
            plugin_class = getattr(module, alternative['class'])
            return plugin_class()
        except Exception as e:
            self.error_handler.log_error(e, {
                'action': 'load_alternative',
                'plugin': plugin_name,
                'alternative': alternative['name']
            })
            print(f"❌ Failed to load alternative {alternative['name']}: {e}")
            return None
    
    def _register_commands(self):
        """Register command handlers"""
        self.commands = {
            'alternatives': self.cmd_list_alternatives,
            'use': self.cmd_use_alternative
        }
    
    async def cmd_list_alternatives(self, *args):
        """List available alternatives for plugins"""
        if not args and not self.alternatives:
            print("No alternatives configured")
            return False
        
        if not args:
            print("\n🔄 Available plugin alternatives:")
            for plugin, alts in self.alternatives.items():
                print(f"\n{plugin}:")
                for alt in alts:
                    print(f"  - {alt['name']}: {alt['description']}")
            return True
        
        # Show alternatives for specific plugin
        plugin_name = args[0].lower()
        alternatives = self.get_alternatives(plugin_name)
        
        if not alternatives:
            print(f"No alternatives found for {plugin_name}")
            return False
        
        print(f"\n🔄 Alternatives for {plugin_name}:")
        for i, alt in enumerate(alternatives, 1):
            print(f"{i}. {alt['name']} - {alt['description']}")
        
        return True
    
    async def cmd_use_alternative(self, *args):
        """Switch to an alternative implementation"""
        if len(args) < 2:
            print("Usage: use <plugin> <alternative>")
            return False
        
        plugin_name = args[0].lower()
        alt_name = args[1].lower()
        
        alternatives = self.get_alternatives(plugin_name)
        if not alternatives:
            print(f"No alternatives found for {plugin_name}")
            return False
        
        # Find the requested alternative
        selected = next((a for a in alternatives if a['name'].lower() == alt_name), None)
        if not selected:
            print(f"Alternative '{alt_name}' not found for {plugin_name}")
            return False
        
        print(f"\n🔄 Loading {selected['name']} as alternative for {plugin_name}...")
        plugin = await self.load_alternative(plugin_name, selected)
        
        if plugin:
            # Register the plugin with the plugin manager
            plugin_manager = get_plugin_manager()
            plugin_manager.plugins[plugin_name] = plugin
            print(f"✅ Successfully loaded {selected['name']}")
            return True
        
        return False

def setup():
    """Plugin setup function"""
    return AlternativePlugin()
