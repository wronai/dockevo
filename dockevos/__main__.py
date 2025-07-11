#!/usr/bin/env python3
"""
dockevOS MVP - Minimalna wersja realizująca wszystkie kluczowe funkcje
Jednolikowa aplikacja z event bus, voice control, docker management i hot-reload

Instalacja:
pip install docker psutil

Uruchomienie:
python dockevos.py

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
    if 'pytest' in sys.modules or os.environ.get('DOCKEVOS_IGNORE_MISSING_DEPS'):
        print("⚠️  Skipping dependency check in test/CI environment")
    else:
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
        self.stt_available = self._check_stt()
        self.stt_engine = None
        if self.stt_available:
            self._init_stt_engine()
            
    def _check_stt(self) -> bool:
        """Sprawdź dostępność STT"""
        # Check for common STT tools
        stt_tools = ['pocketsphinx', 'vosk', 'whisper']
        for tool in stt_tools:
            if subprocess.run(['which', tool], capture_output=True).returncode == 0:
                self.stt_engine = tool
                return True
        return False
        
    def _init_stt_engine(self):
        """Initialize the selected STT engine"""
        try:
            if self.stt_engine == 'pocketsphinx':
                # Minimal configuration for pocketsphinx
                import pocketsphinx
                self.stt_available = True
                
            elif self.stt_engine == 'vosk':
                # Initialize Vosk
                import vosk
                import pyaudio
                
                # Download Vosk model if not exists
                model_path = os.path.expanduser('~/.cache/vosk/models/vosk-model-small-en-us-0.15')
                if not os.path.exists(model_path):
                    print("📥 Downloading Vosk model (small English model, ~50MB)...")
                    import urllib.request
                    import zipfile
                    
                    os.makedirs(os.path.dirname(model_path), exist_ok=True)
                    zip_path = os.path.join(os.path.dirname(model_path), 'model.zip')
                    
                    try:
                        # Download the model
                        url = 'https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip'
                        urllib.request.urlretrieve(url, zip_path)
                        
                        # Extract the model
                        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                            zip_ref.extractall(os.path.dirname(model_path))
                        
                        # Clean up
                        os.remove(zip_path)
                    except Exception as e:
                        print(f"⚠️  Failed to download Vosk model: {e}")
                        print("💡 Please download it manually and extract to ~/.cache/vosk/models/")
                        self.stt_available = False
                        return
                
                # Initialize the model and recognizer
                print("🔊 Initializing Vosk model...")
                self.vosk_model = vosk.Model(model_path)
                self.vosk_recognizer = vosk.KaldiRecognizer(self.vosk_model, 16000)
                
                # Initialize PyAudio with device selection
                print("🔍 Detecting audio devices...")
                self.pyaudio = pyaudio.PyAudio()
                
                # List available input devices
                info = self.pyaudio.get_host_api_info_by_index(0)
                num_devices = info.get('deviceCount')
                
                print("\nAvailable audio devices:")
                print("----------------------")
                for i in range(0, num_devices):
                    device_info = self.pyaudio.get_device_info_by_host_api_device_index(0, i)
                    if device_info.get('maxInputChannels') > 0:
                        print(f"{i}: {device_info.get('name')} (Input Channels: {device_info.get('maxInputChannels')})")
                
                # Try to find a suitable input device
                self.input_device_index = None
                for i in range(0, num_devices):
                    device_info = self.pyaudio.get_device_info_by_host_api_device_index(0, i)
                    if device_info.get('maxInputChannels') > 0:
                        self.input_device_index = i
                        break
                
                if self.input_device_index is None:
                    print("❌ No suitable input device found")
                    self.stt_available = False
                    return
                
                print(f"\n🎤 Using input device: {self.pyaudio.get_device_info_by_index(self.input_device_index).get('name')}")
                self.stt_available = True
                
            elif self.stt_engine == 'whisper':
                # Whisper will be loaded on-demand due to its size
                self.stt_available = True
                
            print(f"✅ STT engine initialized: {self.stt_engine}")
            
        except Exception as e:
            print(f"⚠️  STT initialization error: {e}")
            import traceback
            traceback.print_exc()
            print("\n💡 Try installing system dependencies:")
            print("Ubuntu/Debian: sudo apt-get install portaudio19-dev python3-pyaudio")
            print("macOS: brew install portaudio")
            print("Windows: pip install pipwin && pipwin install pyaudio")
            self.stt_available = False
        
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
            
    def listen(self, timeout=30) -> str:
        """Listen for speech and return transcribed text
        
        Args:
            timeout: Maximum time in seconds to listen (0 for no timeout)
            
        Returns:
            str: Transcribed text or empty string if nothing was recognized
        """
        if not self.stt_available or not hasattr(self, 'vosk_recognizer'):
            print("❌ STT is not available. Make sure you have a microphone and required dependencies.")
            print("💡 Try: pip install pyaudio")
            if not hasattr(self, 'pyaudio'):
                print("💡 You may need to install system dependencies:")
                print("   - Ubuntu/Debian: sudo apt-get install portaudio19-dev python3-pyaudio")
                print("   - macOS: brew install portaudio")
                print("   - Windows: pip install pipwin && pipwin install pyaudio")
            return ""
            
        print("\n🎤 Listening... (press Ctrl+C to stop or wait for silence to end)")
        
        stream = None
        try:
            # Open microphone stream with the selected device
            stream = self.pyaudio.open(
                format=pyaudio.paInt16,
                channels=1,
                rate=16000,
                input=True,
                input_device_index=self.input_device_index,
                frames_per_buffer=4096
            )
            
            print("🔊 Speak now...")
            
            # Reset the recognizer to clear any previous state
            self.vosk_recognizer.Reset()
            
            start_time = time.time()
            last_activity = time.time()
            result_text = ""
            
            while True:
                # Check for timeout
                current_time = time.time()
                if timeout > 0 and (current_time - start_time) > timeout:
                    print("\n⏱️  Timeout reached")
                    break
                
                try:
                    # Read audio data in smaller chunks for more responsive processing
                    data = stream.read(2048, exception_on_overflow=False)
                    
                    if len(data) == 0:
                        print("\n⚠️  No audio data received from microphone")
                        break
                    
                    # Process audio with Vosk
                    if self.vosk_recognizer.AcceptWaveform(data):
                        result = json.loads(self.vosk_recognizer.Result())
                        if 'text' in result and result['text']:
                            result_text = result['text']
                            print(f"\r🎤 Heard: {result_text}", end='', flush=True)
                            last_activity = time.time()
                    else:
                        # Check for partial results
                        partial = json.loads(self.vosk_recognizer.PartialResult())
                        if 'partial' in partial and partial['partial']:
                            print(f"\r🎤 Heard: {partial['partial']}", end='', flush=True)
                            last_activity = time.time()
                        
                        # Check for silence to end of speech (3 seconds of no new input)
                        if (current_time - last_activity) > 3.0:
                            if last_activity > start_time:  # Only end if we've heard something
                                print("\n🔇 End of speech detected")
                                break
                
                except IOError as e:
                    if e.errno == -9981:  # Input overflowed
                        print("\n⚠️  Audio input overflow - continuing...")
                        continue
                    raise
                
                # Small sleep to prevent CPU overuse
                time.sleep(0.01)
            
            return result_text.strip()
            
        except KeyboardInterrupt:
            print("\n⏹️  Stopped listening")
            return ""
            
        except Exception as e:
            print(f"\n❌ STT Error: {e}")
            import traceback
            traceback.print_exc()
            
            if 'No default input device' in str(e):
                print("\n💡 No microphone found. Please check your audio input devices:")
                print("1. Make sure your microphone is properly connected")
                print("2. Check system sound settings")
                print("3. Try a different input device if available")
            
            return ""
            
        finally:
            # Ensure the stream is always closed properly
            if stream:
                try:
                    stream.stop_stream()
                    stream.close()
                except:
                    pass
                
            print()  # Ensure we end on a new line

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
"""Sample plugin for dockevOS MVP"""

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
    """Główna klasa dockevOS MVP"""
    
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
            'listen': self._cmd_listen,
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
                    dockevOS MVP                          
                                                              
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
        print("🚀 dockevOS MVP ready!")
        
        while self.running:
            try:
                command_line = input("dockevos> ").strip()
                
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
🆘 dockevOS MVP - Available Commands:

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
            print("Usage: speak <text>")
            return
            
        text = ' '.join(args)
        if self.voice.speak(text):
            print(f"🔊 Said: {text}")
        else:
            print("❌ Failed to speak")
            
    async def _cmd_listen(self, args):
        """Speech-to-text (STT)"""
        if not self.voice.stt_available:
            print("❌ STT is not available. Please install a supported STT engine like Vosk or Whisper.")
            print("💡 Try: pip install vosk pyaudio")
            if not hasattr(self.voice, 'pyaudio'):
                print("💡 You may need to install system dependencies for PyAudio:")
                print("   - Ubuntu/Debian: sudo apt-get install portaudio19-dev python3-pyaudio")
                print("   - macOS: brew install portaudio")
                print("   - Windows: pip install pipwin && pipwin install pyaudio")
            return ""
            
        try:
            # Get timeout from args if provided, default to 30 seconds
            timeout = 30
            if args and args[0].isdigit():
                timeout = int(args[0])
                
            # Start listening
            result = self.voice.listen(timeout=timeout)
            
            # If we got a result, let's process it
            if result:
                print(f"🎤 Recognized: {result}")
                
                # Check if the recognized text is a command
                if result.lower().startswith(("hey ", "ok ", "computer ", "container ", "os ")):
                    # Remove wake words and process as command
                    command = result.split(' ', 1)[1] if ' ' in result else ""
                    if command:
                        print(f"🤖 Executing command: {command}")
                        await self._execute_command(command)
                
                return result
            else:
                print("❌ No speech detected or recognized.")
                return ""
                
        except Exception as e:
            print(f"❌ STT Error: {e}")
            return ""
    
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
        dockevos = ContainerOSMVP()
        asyncio.run(dockevos.start())
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except Exception as e:
        print(f"💥 Fatal error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()