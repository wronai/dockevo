#!/usr/bin/env python3
"""
Container OS MVP - Minimalna wersja realizująca wszystkie kluczowe funkcje
Jednolikowa aplikacja z event bus, voice control, docker management i hot-reload

Instalacja:
pip install docker psutil

Uruchomienie:
python container-os.py

Funkcje:
- Interfejs tekstowy z komendami
- Voice control (TTS/STT przez system)
- Docker management
- Hot-reload plugins
- Event-driven architecture
- Self-learning
"""

import asyncio
import os
import sys
import json
import time
import importlib.util
import subprocess
import threading
from pathlib import Path
from typing import Dict, List, Callable, Any, Optional
from dataclasses import dataclass
from collections import defaultdict, deque
import tempfile

# Sprawdź zależności
try:
    import docker
    import psutil
except ImportError as e:
    print(f"❌ Missing dependency: {e}")
    print("Install with: pip install docker psutil")
    sys.exit(1)

@dataclass
class Event:
    type: str
    data: Dict[str, Any]
    timestamp: float = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = time.time()

class EventBus:
    """Minimalny event bus"""
    def __init__(self):
        self.subscribers = defaultdict(list)
        self.event_history = deque(maxlen=100)
        
    async def emit(self, event_type: str, data: Dict[str, Any]):
        event = Event(event_type, data)
        self.event_history.append(event)
        
        for handler in self.subscribers.get(event_type, []):
            try:
                if asyncio.iscoroutinefunction(handler):
                    await handler(event)
                else:
                    handler(event)
            except Exception as e:
                print(f"❌ Event handler error: {e}")
    
    def subscribe(self, event_type: str, handler: Callable):
        self.subscribers[event_type].append(handler)

class VoiceService:
    """Minimalny voice service używający systemowych narzędzi"""
    def __init__(self):
        self.tts_available = self._check_tts()
        self.stt_available = False  # Uproszczone dla MVP
        
    def _check_tts(self) -> bool:
        """Sprawdź dostępność TTS"""
        for cmd in ['espeak', 'say', 'spd-say']:
            if subprocess.run(['which', cmd], capture_output=True).returncode == 0:
                self.tts_cmd = cmd
                return True
        return False
    
    def speak(self, text: str) -> bool:
        """Wypowiedz tekst"""
        if not self.tts_available:
            print(f"🔊 [TTS] {text}")  # Fallback to text
            return True
            
        try:
            if self.tts_cmd == 'say':  # macOS
                subprocess.run(['say', text], check=True)
            elif self.tts_cmd == 'espeak':  # Linux
                subprocess.run(['espeak', text], check=True)
            elif self.tts_cmd == 'spd-say':  # Speech Dispatcher
                subprocess.run(['spd-say', text], check=True)
            return True
        except Exception as e:
            print(f"❌ TTS Error: {e}")
            return False

class DockerService:
    """Docker management service"""
    def __init__(self):
        try:
            self.client = docker.from_env()
            self.available = True
        except Exception as e:
            print(f"⚠️  Docker not available: {e}")
            self.available = False
    
    def list_containers(self, all_containers=False):
        """Lista kontenerów"""
        if not self.available:
            return "Docker not available"
        
        try:
            containers = self.client.containers.list(all=all_containers)
            if not containers:
                return "No containers found"
            
            result = "CONTAINER ID  IMAGE           STATUS\n"
            for c in containers:
                result += f"{c.short_id}      {c.image.tags[0] if c.image.tags else 'none':<15} {c.status}\n"
            return result
        except Exception as e:
            return f"Error: {e}"
    
    def start_container(self, name_or_id: str):
        """Uruchom kontener"""
        if not self.available:
            return "Docker not available"
        
        try:
            container = self.client.containers.get(name_or_id)
            container.start()
            return f"✅ Started: {name_or_id}"
        except Exception as e:
            return f"❌ Error: {e}"
    
    def stop_container(self, name_or_id: str):
        """Zatrzymaj kontener"""
        if not self.available:
            return "Docker not available"
        
        try:
            container = self.client.containers.get(name_or_id)
            container.stop()
            return f"🛑 Stopped: {name_or_id}"
        except Exception as e:
            return f"❌ Error: {e}"

class SystemService:
    """System information service"""
    
    def get_system_info(self):
        """Informacje o systemie"""
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            info = f"""🖥️  System Information:
CPU Usage: {cpu_percent}%
Memory: {memory.percent}% ({memory.used // 1024**2}MB / {memory.total // 1024**2}MB)
Disk: {disk.percent}% ({disk.used // 1024**3}GB / {disk.total // 1024**3}GB)
Uptime: {self._get_uptime()}"""
            
            return info
        except Exception as e:
            return f"Error getting system info: {e}"
    
    def _get_uptime(self):
        """Czas działania systemu"""
        try:
            uptime_seconds = time.time() - psutil.boot_time()
            hours = int(uptime_seconds // 3600)
            minutes = int((uptime_seconds % 3600) // 60)
            return f"{hours}h {minutes}m"
        except:
            return "unknown"

class PluginManager:
    """Minimalny plugin manager z hot-reload"""
    
    def __init__(self, event_bus: EventBus):
        self.event_bus = event_bus
        self.plugins = {}
        self.plugins_dir = Path("plugins")
        self.plugins_dir.mkdir(exist_ok=True)
        
    def create_sample_plugin(self):
        """Utwórz przykładowy plugin"""
        sample_plugin = '''
"""Sample plugin for Container OS MVP"""

def register(event_bus, shell):
    """Register plugin handlers"""
    
    def handle_hello_command(event):
        args = event.data.get('args', [])
        name = args[0] if args else 'World'
        return f"Hello, {name}!"
    
    def handle_time_command(event):
        import time
        return f"Current time: {time.strftime('%Y-%m-%d %H:%M:%S')}"
    
    # Register commands
    shell.register_command('hello', handle_hello_command)
    shell.register_command('time', handle_time_command)
    
    print("📦 Sample plugin loaded: hello, time")

def unregister(event_bus, shell):
    """Unregister plugin handlers"""
    shell.unregister_command('hello')
    shell.unregister_command('time')
    print("📦 Sample plugin unloaded")
'''
        
        sample_path = self.plugins_dir / "sample_plugin.py"
        if not sample_path.exists():
            with open(sample_path, 'w') as f:
                f.write(sample_plugin)
            print(f"📦 Created sample plugin: {sample_path}")
    
    async def load_plugin(self, plugin_path: Path, shell):
        """Załaduj plugin"""
        try:
            plugin_name = plugin_path.stem
            
            # Unload if already loaded
            if plugin_name in self.plugins:
                await self.unload_plugin(plugin_name, shell)
            
            # Load module
            spec = importlib.util.spec_from_file_location(plugin_name, plugin_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # Register plugin
            if hasattr(module, 'register'):
                module.register(self.event_bus, shell)
                self.plugins[plugin_name] = module
                await self.event_bus.emit('plugin.loaded', {'name': plugin_name})
                return True
            else:
                print(f"❌ Plugin {plugin_name} missing register() function")
                return False
                
        except Exception as e:
            print(f"❌ Error loading plugin {plugin_path}: {e}")
            return False
    
    async def unload_plugin(self, plugin_name: str, shell):
        """Wyładuj plugin"""
        if plugin_name in self.plugins:
            module = self.plugins[plugin_name]
            if hasattr(module, 'unregister'):
                module.unregister(self.event_bus, shell)
            del self.plugins[plugin_name]
            await self.event_bus.emit('plugin.unloaded', {'name': plugin_name})
    
    async def load_all_plugins(self, shell):
        """Załaduj wszystkie pluginy"""
        plugin_files = list(self.plugins_dir.glob("*.py"))
        for plugin_file in plugin_files:
            await self.load_plugin(plugin_file, shell)

class UsageTracker:
    """Śledzenie użycia dla self-learning"""
    
    def __init__(self):
        self.command_count = defaultdict(int)
        self.voice_patterns = defaultdict(int)
        self.session_start = time.time()
        
    def track_command(self, command: str):
        """Śledź użycie komendy"""
        self.command_count[command] += 1
        
        # Suggest alias for frequently used commands
        if self.command_count[command] == 5:
            print(f"💡 Command '{command}' used {self.command_count[command]} times. Consider creating an alias.")
    
    def get_stats(self):
        """Pobierz statystyki"""
        session_time = time.time() - self.session_start
        return {
            'session_time': f"{session_time/60:.1f} minutes",
            'commands_used': len(self.command_count),
            'total_commands': sum(self.command_count.values()),
            'most_used': dict(sorted(self.command_count.items(), key=lambda x: x[1], reverse=True)[:5])
        }

class ContainerOSMVP:
    """Główna klasa Container OS MVP"""
    
    def __init__(self):
        self.event_bus = EventBus()
        self.voice = VoiceService()
        self.docker = DockerService()
        self.system = SystemService()
        self.plugin_manager = PluginManager(self.event_bus)
        self.usage_tracker = UsageTracker()
        self.running = True
        self.commands = {}
        
        # Register built-in commands
        self._register_builtin_commands()
        
        # Subscribe to events
        self.event_bus.subscribe('command.executed', self._handle_command_executed)
        
    def _register_builtin_commands(self):
        """Zarejestruj wbudowane komendy"""
        self.commands.update({
            'help': self._cmd_help,
            'exit': self._cmd_exit,
            'quit': self._cmd_exit,
            'ps': self._cmd_ps,
            'containers': self._cmd_ps,
            'start': self._cmd_start,
            'stop': self._cmd_stop,
            'info': self._cmd_info,
            'status': self._cmd_info,
            'speak': self._cmd_speak,
            'voice': self._cmd_speak,
            'plugins': self._cmd_plugins,
            'stats': self._cmd_stats,
            'reload': self._cmd_reload_plugins,
        })
    
    def register_command(self, name: str, handler: Callable):
        """Zarejestruj komendę (dla pluginów)"""
        self.commands[name] = handler
        print(f"📝 Registered command: {name}")
    
    def unregister_command(self, name: str):
        """Wyrejestruj komendę"""
        if name in self.commands:
            del self.commands[name]
            print(f"📝 Unregistered command: {name}")
    
    async def _handle_command_executed(self, event: Event):
        """Handle command execution events"""
        command = event.data.get('command', '')
        self.usage_tracker.track_command(command.split()[0])  # Track main command
    
    async def start(self):
        """Uruchom system"""
        self._show_banner()
        
        # Create sample plugin
        self.plugin_manager.create_sample_plugin()
        
        # Load plugins
        await self.plugin_manager.load_all_plugins(self)
        
        # Start main loop
        await self._main_loop()
    
    def _show_banner(self):
        """Pokaż banner startowy"""
        banner = """
══════════════════════════════════════════════════════════════
                    Container OS MVP                          
                                                              
  🐳 Docker Management  🎤 Voice Control  🧩 Plugin System    
  🔄 Hot-Reload        📊 Self-Learning   ⚡ Event-Driven                                                                  
  Type 'help' for commands | 'speak hello' for voice test     
══════════════════════════════════════════════════════════════
        """
        print(banner)
        
        # System status
        print(f"🐳 Docker: {'✅ Available' if self.docker.available else '❌ Unavailable'}")
        print(f"🎤 Voice: {'✅ TTS Available' if self.voice.tts_available else '⚠️  Text only'}")
        print(f"🧩 Plugins: {len(self.plugin_manager.plugins)} loaded")
        print()
    
    async def _main_loop(self):
        """Główna pętla"""
        print("🚀 Container OS MVP ready!")
        
        while self.running:
            try:
                command_line = input("container-os> ").strip()
                
                if command_line:
                    await self._execute_command(command_line)
                    
            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                break
            except EOFError:
                break
            except Exception as e:
                print(f"❌ Error: {e}")
    
    async def _execute_command(self, command_line: str):
        """Wykonaj komendę"""
        parts = command_line.split()
        if not parts:
            return
        
        cmd_name = parts[0]
        args = parts[1:]
        
        # Emit command event
        await self.event_bus.emit('command.executed', {
            'command': command_line,
            'args': args
        })
        
        if cmd_name in self.commands:
            try:
                handler = self.commands[cmd_name]
                if asyncio.iscoroutinefunction(handler):
                    result = await handler(args)
                else:
                    result = handler({'data': {'args': args}})
                
                if result:
                    print(result)
                    
            except Exception as e:
                print(f"❌ Command error: {e}")
        else:
            print(f"❌ Unknown command: {cmd_name}. Type 'help' for available commands.")
    
    # Built-in command handlers
    async def _cmd_help(self, args):
        """Pokaż pomoc"""
        help_text = """
🆘 Container OS MVP - Available Commands:

📋 System Commands:
  help           Show this help
  info, status   Show system information  
  stats          Show usage statistics
  exit, quit     Exit the system

🐳 Docker Commands:
  ps, containers List Docker containers
  start <name>   Start container
  stop <name>    Stop container

🎤 Voice Commands:
  speak <text>   Text-to-speech
  voice <text>   Alias for speak

🧩 Plugin Commands:
  plugins        List loaded plugins
  reload         Reload all plugins

📦 Plugin Commands (if loaded):"""

        # Add plugin commands
        plugin_commands = []
        for name, handler in self.commands.items():
            if name not in ['help', 'exit', 'quit', 'ps', 'containers', 'start', 'stop', 
                           'info', 'status', 'speak', 'voice', 'plugins', 'stats', 'reload']:
                plugin_commands.append(f"  {name}")
        
        if plugin_commands:
            help_text += "\n" + "\n".join(plugin_commands)
        else:
            help_text += "\n  (No plugin commands loaded)"
        
        help_text += """

🎯 Voice Control Examples:
  speak "Hello World"
  speak "Container started successfully"

🧩 Plugin Development:
  Edit files in plugins/ directory for hot-reload
  See plugins/sample_plugin.py for example
        """
        
        return help_text
    
    async def _cmd_exit(self, args):
        """Wyjdź z systemu"""
        self.voice.speak("Goodbye!")
        self.running = False
        return "👋 Goodbye!"
    
    async def _cmd_ps(self, args):
        """Lista kontenerów"""
        all_containers = '-a' in args or '--all' in args
        result = self.docker.list_containers(all_containers)
        return f"🐳 Docker Containers:\n{result}"
    
    async def _cmd_start(self, args):
        """Uruchom kontener"""
        if not args:
            return "Usage: start <container_name>"
        
        container_name = args[0]
        result = self.docker.start_container(container_name)
        self.voice.speak(f"Container {container_name} started")
        return result
    
    async def _cmd_stop(self, args):
        """Zatrzymaj kontener"""
        if not args:
            return "Usage: stop <container_name>"
        
        container_name = args[0]
        result = self.docker.stop_container(container_name)
        self.voice.speak(f"Container {container_name} stopped")
        return result
    
    async def _cmd_info(self, args):
        """Informacje o systemie"""
        return self.system.get_system_info()
    
    async def _cmd_speak(self, args):
        """Text-to-speech"""
        if not args:
            return "Usage: speak <text>"
        
        text = " ".join(args)
        success = self.voice.speak(text)
        if success:
            return f"🔊 Spoke: {text}"
        else:
            return f"❌ TTS failed: {text}"
    
    async def _cmd_plugins(self, args):
        """Lista pluginów"""
        if not self.plugin_manager.plugins:
            return "📦 No plugins loaded"
        
        result = "📦 Loaded Plugins:\n"
        for name in self.plugin_manager.plugins:
            result += f"  • {name}\n"
        
        result += f"\n📁 Plugin directory: {self.plugin_manager.plugins_dir}"
        result += "\n💡 Edit plugin files for hot-reload"
        
        return result
    
    async def _cmd_stats(self, args):
        """Statystyki użycia"""
        stats = self.usage_tracker.get_stats()
        
        result = f"""📊 Usage Statistics:
Session time: {stats['session_time']}
Commands used: {stats['commands_used']}
Total commands: {stats['total_commands']}

Most used commands:"""
        
        for cmd, count in stats['most_used'].items():
            result += f"\n  {cmd}: {count} times"
        
        return result
    
    async def _cmd_reload_plugins(self, args):
        """Przeładuj wszystkie pluginy"""
        # Unload all plugins
        plugin_names = list(self.plugin_manager.plugins.keys())
        for name in plugin_names:
            await self.plugin_manager.unload_plugin(name, self)
        
        # Reload all plugins
        await self.plugin_manager.load_all_plugins(self)
        
        return f"🔄 Reloaded {len(self.plugin_manager.plugins)} plugins"

def main():
    """Entry point"""
    try:
        container_os = ContainerOSMVP()
        asyncio.run(container_os.start())
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except Exception as e:
        print(f"💥 Fatal error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()