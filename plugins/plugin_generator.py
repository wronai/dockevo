#!/usr/bin/env python3
"""
Plugin Generator for dockevOS MVP
Automatycznie generuje pluginy na podstawie template'ów

Usage:
- Jako plugin w dockevOS: `generate plugin voice-enhanced`
- Jako standalone: python plugin_generator.py voice-enhanced
"""

import os
import json
import time
from pathlib import Path
from typing import Dict, List, Optional

# Template definitions
PLUGIN_TEMPLATES = {
    "basic": {
        "description": "Basic plugin template with simple commands",
        "dependencies": [],
        "features": ["commands"]
    },
    "voice-enhanced": {
        "description": "Enhanced voice control with multiple TTS engines",
        "dependencies": ["pyttsx3", "gTTS", "pygame"],
        "features": ["voice", "tts", "speech_recognition"]
    },
    "docker-advanced": {
        "description": "Advanced Docker management with compose support",
        "dependencies": ["docker-compose", "pyyaml"],
        "features": ["docker", "compose", "networking"]
    },
    "system-monitor": {
        "description": "Advanced system monitoring and alerting",
        "dependencies": ["psutil", "plotly", "schedule"],
        "features": ["monitoring", "alerts", "visualization"]
    },
    "api-client": {
        "description": "REST API client template",
        "dependencies": ["requests", "aiohttp"],
        "features": ["http", "api", "async"]
    },
    "database": {
        "description": "Database management plugin",
        "dependencies": ["sqlalchemy", "alembic"],
        "features": ["database", "orm", "migrations"]
    },
    "scheduler": {
        "description": "Task scheduling and automation",
        "dependencies": ["schedule", "crontab"],
        "features": ["scheduling", "automation", "tasks"]
    },
    "notification": {
        "description": "Multi-channel notification system",
        "dependencies": ["plyer", "requests"],
        "features": ["notifications", "alerts", "integrations"]
    }
}

def generate_basic_plugin(plugin_name: str, description: str) -> str:
    """Generate basic plugin template"""
    return f'''"""
{plugin_name.title()} Plugin for dockevOS MVP
{description}

Generated on: {time.strftime('%Y-%m-%d %H:%M:%S')}
"""

import time
import json
from pathlib import Path

def register(event_bus, shell):
    """Register {plugin_name} plugin handlers"""
    
    def handle_example_command(event):
        """Example command - replace with your functionality"""
        args = event.data.get('args', [])
        
        if not args:
            return "Usage: example <message>"
        
        message = ' '.join(args)
        return f"✨ {plugin_name.title()}: {{message}}"
    
    def handle_status_command(event):
        """Show plugin status"""
        return f"📊 {plugin_name.title()} plugin is active"
    
    def handle_config_command(event):
        """Configure plugin settings"""
        args = event.data.get('args', [])
        
        if not args:
            return "Usage: {plugin_name}-config <key> [value]"
        
        # Simple config management
        config_file = Path(f'{plugin_name}_config.json')
        config = {{}
        
        if config_file.exists():
            try:
                with open(config_file, 'r') as f:
                    config = json.load(f)
            except:
                config = {{}
        
        key = args[0]
        
        if len(args) == 1:
            # Get value
            value = config.get(key, 'Not set')
            return f"🔧 {plugin_name}.{{key}} = {{value}}"
        else:
            # Set value
            value = ' '.join(args[1:])
            config[key] = value
            
            with open(config_file, 'w') as f:
                json.dump(config, f, indent=2)
            
            return f"✅ Set {plugin_name}.{{key}} = {{value}}"
    
    # Register commands
    shell.register_command('{plugin_name}-example', handle_example_command)
    shell.register_command('{plugin_name}-status', handle_status_command)
    shell.register_command('{plugin_name}-config', handle_config_command)
    
    # Subscribe to events
    event_bus.subscribe('system.startup', lambda e: print(f"🚀 {plugin_name.title()} plugin initialized"))
    
    print(f"📦 {plugin_name.title()} plugin loaded: {{plugin_name}}-example, {{plugin_name}}-status, {{plugin_name}}-config")

def unregister(event_bus, shell):
    """Unregister plugin handlers"""
    shell.unregister_command('{plugin_name}-example')
    shell.unregister_command('{plugin_name}-status') 
    shell.unregister_command('{plugin_name}-config')
    print(f"📦 {plugin_name.title()} plugin unloaded")

# Plugin metadata
PLUGIN_INFO = {
    "name": "{plugin_name}",
    "version": "1.0.0",
    "description": "{description}",
    "author": "Plugin Generator",
    "generated": "{time.strftime('%Y-%m-%d %H:%M:%S')}"
}
'''

def generate_voice_enhanced_plugin(plugin_name: str, description: str) -> str:
    """Generate enhanced voice plugin with multiple TTS engines"""
    return f'''"""
{plugin_name.title()} Plugin for dockevOS MVP
{description}

Features:
- Multiple TTS engines (pyttsx3, gTTS, espeak)
- Voice quality selection
- Speech rate/pitch control
- Voice profiles
- Audio caching

Dependencies: pip install pyttsx3 gtts pygame

Generated on: {time.strftime('%Y-%m-%d %H:%M:%S')}
"""

import os
import sys
import json
import tempfile
import asyncio
from pathlib import Path
from typing import Dict, Optional

# Voice engine availability
VOICE_ENGINES = {{}

try:
    import pyttsx3
    VOICE_ENGINES['pyttsx3'] = True
except ImportError:
    VOICE_ENGINES['pyttsx3'] = False

try:
    from gtts import gTTS
    import pygame
    VOICE_ENGINES['gtts'] = True
except ImportError:
    VOICE_ENGINES['gtts'] = False

try:
    import subprocess
    # Check for espeak
    result = subprocess.run(['which', 'espeak'], capture_output=True)
    VOICE_ENGINES['espeak'] = result.returncode == 0
except:
    VOICE_ENGINES['espeak'] = False

class VoiceEnhanced:
    def __init__(self):
        self.config_file = Path('voice_enhanced_config.json')
        self.cache_dir = Path('voice_cache')
        self.cache_dir.mkdir(exist_ok=True)
        
        # Default configuration
        self.config = {{
            'engine': 'auto',
            'rate': 150,
            'pitch': 50,
            'volume': 0.8,
            'voice_id': 0,
            'language': 'en',
            'cache_enabled': True
        }
        
        self.load_config()
        self.init_engines()
    
    def load_config(self):
        """Load configuration from file"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    saved_config = json.load(f)
                    self.config.update(saved_config)
            except Exception as e:
                print(f"⚠️  Error loading voice config: {{e}}")
    
    def save_config(self):
        """Save configuration to file"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=2)
        except Exception as e:
            print(f"⚠️  Error saving voice config: {{e}}")
    
    def init_engines(self):
        """Initialize available TTS engines"""
        self.engines = {{}
        
        # Initialize pyttsx3
        if VOICE_ENGINES['pyttsx3']:
            try:
                engine = pyttsx3.init()
                engine.setProperty('rate', self.config['rate'])
                engine.setProperty('volume', self.config['volume'])
                
                voices = engine.getProperty('voices')
                if voices and len(voices) > self.config['voice_id']:
                    engine.setProperty('voice', voices[self.config['voice_id']].id)
                
                self.engines['pyttsx3'] = engine
            except Exception as e:
                print(f"⚠️  Error initializing pyttsx3: {{e}}")
        
        # Initialize pygame for gTTS playback
        if VOICE_ENGINES['gtts']:
            try:
                pygame.mixer.init()
                self.engines['gtts'] = True
            except Exception as e:
                print(f"⚠️  Error initializing pygame: {{e}}")
                VOICE_ENGINES['gtts'] = False
    
    def get_cache_path(self, text: str, engine: str) -> Path:
        """Get cache file path for text"""
        import hashlib
        text_hash = hashlib.md5(f"{{engine}}_{{text}}_{{self.config['language']}}".encode()).hexdigest()
        return self.cache_dir / f"{{text_hash}}.mp3"
    
    def speak_pyttsx3(self, text: str) -> bool:
        """Speak using pyttsx3 (offline)"""
        try:
            engine = self.engines.get('pyttsx3')
            if not engine:
                return False
            
            engine.say(text)
            engine.runAndWait()
            return True
        except Exception as e:
            print(f"❌ pyttsx3 error: {{e}}")
            return False
    
    def speak_gtts(self, text: str) -> bool:
        """Speak using Google TTS (online)"""
        try:
            if not VOICE_ENGINES['gtts']:
                return False
            
            # Check cache first
            cache_path = self.get_cache_path(text, 'gtts')
            
            if not cache_path.exists() or not self.config['cache_enabled']:
                # Generate speech
                tts = gTTS(text=text, lang=self.config['language'], slow=False)
                tts.save(str(cache_path))
            
            # Play audio
            pygame.mixer.music.load(str(cache_path))
            pygame.mixer.music.play()
            
            # Wait for playback to finish
            while pygame.mixer.music.get_busy():
                pygame.time.wait(100)
            
            return True
        except Exception as e:
            print(f"❌ gTTS error: {{e}}")
            return False
    
    def speak_espeak(self, text: str) -> bool:
        """Speak using espeak (system)"""
        try:
            if not VOICE_ENGINES['espeak']:
                return False
            
            cmd = [
                'espeak',
                '-s', str(self.config['rate']),
                '-p', str(self.config['pitch']),
                '-a', str(int(self.config['volume'] * 100)),
                text
            ]
            
            subprocess.run(cmd, check=True, capture_output=True)
            return True
        except Exception as e:
            print(f"❌ espeak error: {{e}}")
            return False
    
    def speak(self, text: str, engine: Optional[str] = None) -> bool:
        """Speak text using specified or auto-selected engine"""
        if not text.strip():
            return False
        
        # Determine engine to use
        target_engine = engine or self.config['engine']
        
        if target_engine == 'auto':
            # Auto-select best available engine
            if VOICE_ENGINES['gtts']:
                target_engine = 'gtts'
            elif VOICE_ENGINES['pyttsx3']:
                target_engine = 'pyttsx3'
            elif VOICE_ENGINES['espeak']:
                target_engine = 'espeak'
            else:
                print(f"🔊 [TTS] {{text}}")  # Fallback to text
                return True
        
        # Try selected engine
        if target_engine == 'pyttsx3':
            return self.speak_pyttsx3(text)
        elif target_engine == 'gtts':
            return self.speak_gtts(text)
        elif target_engine == 'espeak':
            return self.speak_espeak(text)
        else:
            print(f"🔊 [TTS] {{text}}")  # Fallback
            return True
    
    def get_available_engines(self) -> List[str]:
        """Get list of available engines"""
        available = []
        for engine, available_flag in VOICE_ENGINES.items():
            if available_flag:
                available.append(engine)
        return available
    
    def get_voice_info(self) -> Dict:
        """Get voice system information"""
        info = {{
            'engines_available': self.get_available_engines(),
            'current_engine': self.config['engine'],
            'config': self.config.copy()
        }
        
        if VOICE_ENGINES['pyttsx3'] and 'pyttsx3' in self.engines:
            try:
                voices = self.engines['pyttsx3'].getProperty('voices')
                info['pyttsx3_voices'] = [
                    {{'id': i, 'name': v.name, 'lang': getattr(v, 'languages', ['unknown'])[0]}
                    for i, v in enumerate(voices or [])
                ]
            except:
                info['pyttsx3_voices'] = []
        
        return info

# Global voice instance
voice_enhanced = None

def register(event_bus, shell):
    """Register voice enhanced plugin"""
    global voice_enhanced
    
    voice_enhanced = VoiceEnhanced()
    
    def handle_speak_command(event):
        """Enhanced speak command"""
        args = event.data.get('args', [])
        
        if not args:
            return "Usage: speak <text> [engine]"
        
        # Extract engine if specified
        engine = None
        if len(args) > 1 and args[-1] in voice_enhanced.get_available_engines():
            engine = args[-1]
            text = ' '.join(args[:-1])
        else:
            text = ' '.join(args)
        
        success = voice_enhanced.speak(text, engine)
        if success:
            return f"🔊 Spoke: {{text}}" + (f" ({{engine}})" if engine else "")
        else:
            return f"❌ Failed to speak: {{text}}"
    
    def handle_voice_engines_command(event):
        """List available voice engines"""
        engines = voice_enhanced.get_available_engines()
        
        if not engines:
            return "❌ No voice engines available"
        
        result = "🎤 Available Voice Engines:\\n"
        for engine in engines:
            current = " (current)" if engine == voice_enhanced.config['engine'] else ""
            result += f"  • {{engine}}{{current}}\\n"
        
        return result
    
    def handle_voice_config_command(event):
        """Configure voice settings"""
        args = event.data.get('args', [])
        
        if not args:
            info = voice_enhanced.get_voice_info()
            result = "🔧 Voice Configuration:\\n"
            result += f"  Engine: {{info['current_engine']}}\\n"
            result += f"  Rate: {{info['config']['rate']}}\\n"
            result += f"  Volume: {{info['config']['volume']}}\\n"
            result += f"  Language: {{info['config']['language']}}\\n"
            result += f"  Cache: {{info['config']['cache_enabled']}}\\n"
            result += f"\\nAvailable engines: {{', '.join(info['engines_available'])}}"
            return result
        
        if len(args) < 2:
            return "Usage: voice-config <key> <value>"
        
        key, value = args[0], args[1]
        
        try:
            if key == 'engine':
                if value in voice_enhanced.get_available_engines() or value == 'auto':
                    voice_enhanced.config['engine'] = value
                else:
                    return f"❌ Unknown engine: {{value}}"
            elif key == 'rate':
                voice_enhanced.config['rate'] = int(value)
            elif key == 'volume':
                voice_enhanced.config['volume'] = float(value)
            elif key == 'language':
                voice_enhanced.config['language'] = value
            elif key == 'cache':
                voice_enhanced.config['cache_enabled'] = value.lower() in ['true', '1', 'yes']
            else:
                return f"❌ Unknown config key: {{key}}"
            
            voice_enhanced.save_config()
            voice_enhanced.init_engines()  # Reinitialize with new config
            
            return f"✅ Set voice.{{key}} = {{value}}"
        except ValueError as e:
            return f"❌ Invalid value for {{key}}: {{e}}"
    
    def handle_voice_test_command(event):
        """Test all available voice engines"""
        engines = voice_enhanced.get_available_engines()
        
        if not engines:
            return "❌ No voice engines available for testing"
        
        test_text = "Hello, this is a voice test."
        results = []
        
        for engine in engines:
            print(f"🧪 Testing {{engine}}...")
            success = voice_enhanced.speak(test_text, engine)
            status = "✅ OK" if success else "❌ Failed"
            results.append(f"  {{engine}}: {{status}}")
        
        return "🧪 Voice Engine Test Results:\\n" + "\\n".join(results)
    
    def handle_voice_clear_cache_command(event):
        """Clear voice cache"""
        try:
            cache_files = list(voice_enhanced.cache_dir.glob("*.mp3"))
            for cache_file in cache_files:
                cache_file.unlink()
            
            return f"🧹 Cleared {{len(cache_files)}} cached voice files"
        except Exception as e:
            return f"❌ Error clearing cache: {{e}}"
    
    # Register commands
    shell.register_command('speak', handle_speak_command)
    shell.register_command('voice-engines', handle_voice_engines_command)
    shell.register_command('voice-config', handle_voice_config_command)
    shell.register_command('voice-test', handle_voice_test_command)
    shell.register_command('voice-clear-cache', handle_voice_clear_cache_command)
    
    # Override default speak command for better quality
    if 'speak' in shell.commands:
        shell.commands['speak'] = handle_speak_command
    
    print(f"📦 Voice Enhanced plugin loaded with {{len(voice_enhanced.get_available_engines())}} engines")
    print(f"🎤 Available engines: {{', '.join(voice_enhanced.get_available_engines())}}")

def unregister(event_bus, shell):
    """Unregister voice enhanced plugin"""
    shell.unregister_command('voice-engines')
    shell.unregister_command('voice-config')
    shell.unregister_command('voice-test')
    shell.unregister_command('voice-clear-cache')
    print("📦 Voice Enhanced plugin unloaded")

# Plugin metadata
PLUGIN_INFO = {
    "name": "voice_enhanced",
    "version": "1.0.0",
    "description": "Enhanced voice control with multiple TTS engines",
    "author": "Plugin Generator",
    "dependencies": ["pyttsx3", "gtts", "pygame"],
    "features": ["voice", "tts", "caching", "multi_engine"],
    "generated": "{time.strftime('%Y-%m-%d %H:%M:%S')}"
}
'''

def generate_docker_advanced_plugin(plugin_name: str, description: str) -> str:
    """Generate advanced Docker management plugin"""
    return f'''"""
{plugin_name.title()} Plugin for dockevOS MVP
{description}

Features:
- Docker Compose management
- Network management
- Volume management
- Image building
- Container logs streaming
- Health checks

Dependencies: pip install docker-compose pyyaml

Generated on: {time.strftime('%Y-%m-%d %H:%M:%S')}
"""

import os
import json
import yaml
import subprocess
from pathlib import Path
from typing import Dict, List, Optional

try:
    import docker
    DOCKER_AVAILABLE = True
except ImportError:
    DOCKER_AVAILABLE = False
    print("⚠️  Docker library not available. Install with: pip install docker")

class DockerAdvanced:
    def __init__(self):
        self.client = None
        if DOCKER_AVAILABLE:
            try:
                self.client = docker.from_env()
                self.available = True
            except Exception as e:
                print(f"⚠️  Docker not available: {{e}}")
                self.available = False
        else:
            self.available = False
    
    def list_containers_detailed(self, all_containers=False) -> str:
        """List containers with detailed information"""
        if not self.available:
            return "❌ Docker not available"
        
        try:
            containers = self.client.containers.list(all=all_containers)
            
            if not containers:
                return "📦 No containers found"
            
            result = "🐳 Docker Containers (Detailed):\\n"
            result += "NAME               IMAGE              STATUS      PORTS                   CPU/MEM\\n"
            result += "-" * 80 + "\\n"
            
            for container in containers:
                name = container.name[:18]
                image = (container.image.tags[0] if container.image.tags else 'none')[:18]
                status = container.status[:11]
                
                # Get port mappings
                ports = []
                if container.attrs.get('NetworkSettings', {{}}).get('Ports'):
                    for internal_port, external in container.attrs['NetworkSettings']['Ports'].items():
                        if external:
                            external_port = external[0]['HostPort']
                            ports.append(f"{{external_port}}:{{internal_port.split('/')[0]}}")
                
                ports_str = ', '.join(ports[:2]) if ports else 'none'
                if len(ports) > 2:
                    ports_str += f" (+{{len(ports)-2}})"
                
                # Get resource usage (simplified)
                try:
                    stats = container.stats(stream=False)
                    cpu_percent = 0.0
                    memory_usage = "0MB"
                    
                    if 'cpu_stats' in stats and 'precpu_stats' in stats:
                        cpu_delta = stats['cpu_stats']['cpu_usage']['total_usage'] - stats['precpu_stats']['cpu_usage']['total_usage']
                        system_delta = stats['cpu_stats']['system_cpu_usage'] - stats['precpu_stats']['system_cpu_usage']
                        if system_delta > 0:
                            cpu_percent = (cpu_delta / system_delta) * len(stats['cpu_stats']['cpu_usage']['percpu_usage']) * 100
                    
                    if 'memory_stats' in stats:
                        memory_usage = f"{{stats['memory_stats']['usage'] // 1024**2}}MB"
                    
                    resource_info = f"{{cpu_percent:.1f}}%/{{memory_usage}}"
                except:
                    resource_info = "N/A"
                
                result += f"{{name:<18}} {{image:<18}} {{status:<11}} {{ports_str:<23}} {{resource_info}}\\n"
            
            return result
        except Exception as e:
            return f"❌ Error listing containers: {{e}}"
    
    def inspect_container(self, name_or_id: str) -> str:
        """Get detailed container information"""
        if not self.available:
            return "❌ Docker not available"
        
        try:
            container = self.client.containers.get(name_or_id)
            attrs = container.attrs
            
            result = f"🔍 Container Inspection: {{container.name}}\\n"
            result += "=" * 50 + "\\n"
            result += f"ID: {{container.short_id}}\\n"
            result += f"Image: {{container.image.tags[0] if container.image.tags else 'none'}}\\n"
            result += f"Status: {{container.status}}\\n"
            result += f"Created: {{attrs['Created'][:19]}}\\n"
            
            # Network information
            networks = attrs.get('NetworkSettings', {{}}).get('Networks', {{}})
            if networks:
                result += "\\nNetworks:\\n"
                for net_name, net_info in networks.items():
                    ip = net_info.get('IPAddress', 'N/A')
                    result += f"  {{net_name}}: {{ip}}\\n"
            
            # Port mappings
            ports = attrs.get('NetworkSettings', {{}}).get('Ports', {{}})
            if ports:
                result += "\\nPort Mappings:\\n"
                for internal, external in ports.items():
                    if external:
                        ext_port = external[0]['HostPort']
                        result += f"  {{internal}} -> {{ext_port}}\\n"
            
            # Environment variables
            env_vars = attrs.get('Config', {{}}).get('Env', [])
            if env_vars:
                result += "\\nEnvironment Variables:\\n"
                for env in env_vars[:10]:  # Show first 10
                    if '=' in env:
                        key, value = env.split('=', 1)
                        # Hide sensitive values
                        if any(sensitive in key.lower() for sensitive in ['password', 'secret', 'key', 'token']):
                            value = '***'
                        result += f"  {{key}}={{value}}\\n"
                if len(env_vars) > 10:
                    result += f"  ... and {{len(env_vars)-10}} more\\n"
            
            return result
        except Exception as e:
            return f"❌ Error inspecting container: {{e}}"
    
    def manage_compose(self, action: str, path: str = ".") -> str:
        """Manage Docker Compose stacks"""
        compose_file = Path(path) / "docker-compose.yml"
        
        if not compose_file.exists():
            return f"❌ No docker-compose.yml found in {{path}}"
        
        try:
            if action == "up":
                result = subprocess.run(
                    ["docker-compose", "-f", str(compose_file), "up", "-d"],
                    capture_output=True, text=True, cwd=path
                )
            elif action == "down":
                result = subprocess.run(
                    ["docker-compose", "-f", str(compose_file), "down"],
                    capture_output=True, text=True, cwd=path
                )
            elif action == "ps":
                result = subprocess.run(
                    ["docker-compose", "-f", str(compose_file), "ps"],
                    capture_output=True, text=True, cwd=path
                )
            elif action == "logs":
                result = subprocess.run(
                    ["docker-compose", "-f", str(compose_file), "logs", "--tail=50"],
                    capture_output=True, text=True, cwd=path
                )
            else:
                return f"❌ Unknown compose action: {{action}}"
            
            if result.returncode == 0:
                return f"✅ Compose {{action}} successful:\\n{{result.stdout}}"
            else:
                return f"❌ Compose {{action}} failed:\\n{{result.stderr}}"
                
        except FileNotFoundError:
            return "❌ docker-compose command not found. Please install docker-compose."
        except Exception as e:
            return f"❌ Error running compose {{action}}: {{e}}"
    
    def list_networks(self) -> str:
        """List Docker networks"""
        if not self.available:
            return "❌ Docker not available"
        
        try:
            networks = self.client.networks.list()
            
            result = "🌐 Docker Networks:\\n"
            result += "NAME               DRIVER    SCOPE     SUBNET\\n"
            result += "-" * 60 + "\\n"
            
            for network in networks:
                name = network.name[:18]
                driver = network.attrs.get('Driver', 'unknown')[:9]
                scope = network.attrs.get('Scope', 'unknown')[:9]
                
                # Get subnet info
                subnet = "N/A"
                if network.attrs.get('IPAM', {{}}).get('Config'):
                    config = network.attrs['IPAM']['Config'][0]
                    subnet = config.get('Subnet', 'N/A')[:15]
                
                result += f"{{name:<18}} {{driver:<9}} {{scope:<9}} {{subnet}}\\n"
            
            return result
        except Exception as e:
            return f"❌ Error listing networks: {{e}}"
    
    def list_volumes(self) -> str:
        """List Docker volumes"""
        if not self.available:
            return "❌ Docker not available"
        
        try:
            volumes = self.client.volumes.list()
            
            result = "💾 Docker Volumes:\\n"
            result += "NAME                           DRIVER    MOUNTPOINT\\n"
            result += "-" * 70 + "\\n"
            
            for volume in volumes:
                name = volume.name[:30]
                driver = volume.attrs.get('Driver', 'unknown')[:9]
                mountpoint = volume.attrs.get('Mountpoint', 'N/A')
                
                # Truncate long mountpoints
                if len(mountpoint) > 25:
                    mountpoint = "..." + mountpoint[-22:]
                
                result += f"{{name:<30}} {{driver:<9}} {{mountpoint}}\\n"
            
            return result
        except Exception as e:
            return f"❌ Error listing volumes: {{e}}"
    
    def container_logs(self, name_or_id: str, lines: int = 50) -> str:
        """Get container logs"""
        if not self.available:
            return "❌ Docker not available"
        
        try:
            container = self.client.containers.get(name_or_id)
            logs = container.logs(tail=lines, timestamps=True).decode('utf-8')
            
            return f"📋 Logs for {{container.name}} (last {{lines}} lines):\\n" + "="*50 + "\\n" + logs
        except Exception as e:
            return f"❌ Error getting logs: {{e}}"

# Global docker instance
docker_advanced = None

def register(event_bus, shell):
    """Register docker advanced plugin"""
    global docker_advanced
    
    docker_advanced = DockerAdvanced()
    
    def handle_docker_ps_detailed_command(event):
        """List containers with detailed information"""
        args = event.data.get('args', [])
        all_containers = '-a' in args or '--all' in args
        return docker_advanced.list_containers_detailed(all_containers)
    
    def handle_docker_inspect_command(event):
        """Inspect container details"""
        args = event.data.get('args', [])
        if not args:
            return "Usage: docker-inspect <container_name_or_id>"
        
        return docker_advanced.inspect_container(args[0])
    
    def handle_docker_networks_command(event):
        """List Docker networks"""
        return docker_advanced.list_networks()
    
    def handle_docker_volumes_command(event):
        """List Docker volumes"""
        return docker_advanced.list_volumes()
    
    def handle_docker_logs_command(event):
        """Get container logs"""
        args = event.data.get('args', [])
        if not args:
            return "Usage: docker-logs <container_name> [lines]"
        
        container_name = args[0]
        lines = int(args[1]) if len(args) > 1 else 50
        
        return docker_advanced.container_logs(container_name, lines)
    
    def handle_compose_command(event):
        """Docker Compose management"""
        args = event.data.get('args', [])
        if not args:
            return "Usage: compose <up|down|ps|logs> [path]"
        
        action = args[0]
        path = args[1] if len(args) > 1 else "."
        
        return docker_advanced.manage_compose(action, path)
    
    # Register commands
    shell.register_command('docker-ps-detailed', handle_docker_ps_detailed_command)
    shell.register_command('docker-inspect', handle_docker_inspect_command)
    shell.register_command('docker-networks', handle_docker_networks_command)
    shell.register_command('docker-volumes', handle_docker_volumes_command)
    shell.register_command('docker-logs', handle_docker_logs_command)
    shell.register_command('compose', handle_compose_command)
    
    print(f"📦 Docker Advanced plugin loaded with {{6}} commands")

def unregister(event_bus, shell):
    """Unregister docker advanced plugin"""
    shell.unregister_command('docker-ps-detailed')
    shell.unregister_command('docker-inspect')
    shell.unregister_command('docker-networks')
    shell.unregister_command('docker-volumes')
    shell.unregister_command('docker-logs')
    shell.unregister_command('compose')
    print("📦 Docker Advanced plugin unloaded")

# Plugin metadata
PLUGIN_INFO = {
    "name": "docker_advanced",
    "version": "1.0.0",
    "description": "Advanced Docker management with compose support",
    "author": "Plugin Generator",
    "dependencies": ["docker", "docker-compose", "pyyaml"],
    "features": ["docker", "compose", "networking", "volumes"],
    "generated": "{time.strftime('%Y-%m-%d %H:%M:%S')}"
}
'''

def generate_system_monitor_plugin(plugin_name: str, description: str) -> str:
    """Generate advanced system monitoring plugin"""
    return f'''"""
{plugin_name.title()} Plugin for dockevOS MVP
{description}

Features:
- Real-time system monitoring
- CPU, Memory, Disk, Network tracking
- Process monitoring
- Alerts and thresholds
- Historical data
- Performance graphs (text-based)

Dependencies: pip install psutil

Generated on: {time.strftime('%Y-%m-%d %H:%M:%S')}
"""

import time
import json
import threading
from pathlib import Path
from typing import Dict, List, Optional
from collections import deque, defaultdict

try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False
    print("⚠️  psutil not available. Install with: pip install psutil")

class SystemMonitor:
    def __init__(self):
        self.monitoring = False
        self.monitor_thread = None
        self.data_history = defaultdict(lambda: deque(maxlen=100))
        self.alerts = {{
            'cpu_threshold': 80.0,
            'memory_threshold': 85.0,
            'disk_threshold': 90.0,
            'enabled': True
        }
        self.config_file = Path('system_monitor_config.json')
        self.load_config()
        
    def load_config(self):
        """Load monitor configuration"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                    self.alerts.update(config.get('alerts', {{}}))
            except Exception as e:
                print(f"⚠️  Error loading monitor config: {{e}}")
    
    def save_config(self):
        """Save monitor configuration"""
        try:
            config = {{'alerts': self.alerts}
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=2)
        except Exception as e:
            print(f"⚠️  Error saving monitor config: {{e}}")
    
    def collect_metrics(self) -> Dict:
        """Collect current system metrics"""
        if not PSUTIL_AVAILABLE:
            return {{}
        
        try:
            metrics = {{
                'timestamp': time.time(),
                'cpu_percent': psutil.cpu_percent(interval=1),
                'memory': psutil.virtual_memory()._asdict(),
                'disk': psutil.disk_usage('/')._asdict(),
                'network': psutil.net_io_counters()._asdict(),
                'processes': len(psutil.pids()),
                'load_avg': psutil.getloadavg() if hasattr(psutil, 'getloadavg') else (0, 0, 0)
            }
            
            # Store in history
            self.data_history['cpu'].append(metrics['cpu_percent'])
            self.data_history['memory'].append(metrics['memory']['percent'])
            self.data_history['disk'].append(metrics['disk']['percent'])
            
            return metrics
        except Exception as e:
            print(f"❌ Error collecting metrics: {{e}}")
            return {{}
    
    def check_alerts(self, metrics: Dict):
        """Check for alert conditions"""
        if not self.alerts['enabled'] or not metrics:
            return
        
        alerts_triggered = []
        
        if metrics['cpu_percent'] > self.alerts['cpu_threshold']:
            alerts_triggered.append(f"🚨 HIGH CPU: {{metrics['cpu_percent']:.1f}}% > {{self.alerts['cpu_threshold']}}%")
        
        if metrics['memory']['percent'] > self.alerts['memory_threshold']:
            alerts_triggered.append(f"🚨 HIGH MEMORY: {{metrics['memory']['percent']:.1f}}% > {{self.alerts['memory_threshold']}}%")
        
        if metrics['disk']['percent'] > self.alerts['disk_threshold']:
            alerts_triggered.append(f"🚨 HIGH DISK: {{metrics['disk']['percent']:.1f}}% > {{self.alerts['disk_threshold']}}%")
        
        for alert in alerts_triggered:
            print(alert)
    
    def start_monitoring(self):
        """Start background monitoring"""
        if self.monitoring:
            return "⚠️  Monitoring already running"
        
        self.monitoring = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
        return "🔄 System monitoring started"
    
    def stop_monitoring(self):
        """Stop background monitoring"""
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=2)
        return "⏹️  System monitoring stopped"
    
    def _monitor_loop(self):
        """Background monitoring loop"""
        while self.monitoring:
            try:
                metrics = self.collect_metrics()
                self.check_alerts(metrics)
                time.sleep(5)  # Monitor every 5 seconds
            except Exception as e:
                print(f"❌ Monitor loop error: {{e}}")
                time.sleep(5)
    
    def get_current_status(self) -> str:
        """Get current system status"""
        if not PSUTIL_AVAILABLE:
            return "❌ psutil not available"
        
        metrics = self.collect_metrics()
        if not metrics:
            return "❌ Unable to collect metrics"
        
        # Format uptime
        boot_time = psutil.boot_time()
        uptime_seconds = time.time() - boot_time
        uptime_hours = int(uptime_seconds // 3600)
        uptime_minutes = int((uptime_seconds % 3600) // 60)
        uptime_str = f"{{uptime_hours}}h {{uptime_minutes}}m"
        
        # Format memory
        mem = metrics['memory']
        mem_used_gb = mem['used'] / (1024**3)
        mem_total_gb = mem['total'] / (1024**3)
        
        # Format disk
        disk = metrics['disk']
        disk_used_gb = disk['used'] / (1024**3)
        disk_total_gb = disk['total'] / (1024**3)
        
        status = f"""📊 System Status:
─────────────────────────────────────────
 CPU Usage:    {{metrics['cpu_percent']:6.1f}}% │ {{self._get_bar(metrics['cpu_percent'])}
 Memory:       {{mem['percent']:6.1f}}% │ {{self._get_bar(mem['percent'])}
 Disk Usage:   {{disk['percent']:6.1f}}% │ {{self._get_bar(disk['percent'])}
─────────────────────────────────────────

💾 Memory: {{mem_used_gb:.1f}}GB / {{mem_total_gb:.1f}}GB
💿 Disk:   {{disk_used_gb:.1f}}GB / {{disk_total_gb:.1f}}GB
🔄 Processes: {{metrics['processes']}
⏰ Uptime: {{uptime_str}
📈 Load Avg: {{metrics['load_avg'][0]:.2f}}, {{metrics['load_avg'][1]:.2f}}, {{metrics['load_avg'][2]:.2f}
🔔 Monitoring: {{'ON' if self.monitoring else 'OFF'}}"""
        
        return status
    
    def _get_bar(self, percent: float, width: int = 10) -> str:
        """Generate text-based progress bar"""
        filled = int((percent / 100) * width)
        bar = "█" * filled + "░" * (width - filled)
        return f"[{{bar}}]"
    
    def get_history_graph(self, metric: str = 'cpu', points: int = 20) -> str:
        """Generate text-based graph of historical data"""
        if metric not in self.data_history or not self.data_history[metric]:
            return f"❌ No historical data for {{metric}}"
        
        data = list(self.data_history[metric])[-points:]
        if not data:
            return f"❌ No data points for {{metric}}"
        
        max_val = max(data)
        min_val = min(data)
        
        # Normalize data to 0-10 range for display
        height = 8
        normalized = []
        for val in data:
            if max_val > min_val:
                norm = ((val - min_val) / (max_val - min_val)) * height
            else:
                norm = height / 2
            normalized.append(int(norm))
        
        # Build graph
        graph = f"📈 {{metric.upper()}} History (last {{len(data)}} points):\\n"
        graph += f"Max: {{max_val:.1f}}% ┐\\n"
        
        for row in range(height, -1, -1):
            line = "         │"
            for val in normalized:
                if val >= row:
                    line += "█"
                else:
                    line += " "
            graph += line + "\\n"
        
        graph += f"Min: {{min_val:.1f}}% └" + "─" * len(data) + "\\n"
        graph += "         " + "".join([str(i%10) for i in range(len(data))])
        
        return graph
    
    def get_top_processes(self, count: int = 10) -> str:
        """Get top processes by CPU/Memory usage"""
        if not PSUTIL_AVAILABLE:
            return "❌ psutil not available"
        
        try:
            processes = []
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent', 'memory_info']):
                try:
                    proc_info = proc.info
                    if proc_info['cpu_percent'] is not None:
                        processes.append(proc_info)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
            
            # Sort by CPU usage
            processes.sort(key=lambda x: x['cpu_percent'] or 0, reverse=True)
            
            result = f"🔝 Top {{count}} Processes (by CPU):\\n"
            result += "PID      NAME                 CPU%    MEM%    RSS\\n"
            result += "-" * 60 + "\\n"
            
            for proc in processes[:count]:
                pid = proc['pid']
                name = (proc['name'] or 'unknown')[:20]
                cpu = proc['cpu_percent'] or 0
                mem_percent = proc['memory_percent'] or 0
                rss_mb = (proc['memory_info'].rss if proc['memory_info'] else 0) // 1024**2
                
                result += f"{{pid:<8}} {{name:<20}} {{cpu:<7.1f}} {{mem_percent:<7.1f}} {{rss_mb}}MB\\n"
            
            return result
        except Exception as e:
            return f"❌ Error getting processes: {{e}}"

# Global monitor instance
system_monitor = None

def register(event_bus, shell):
    """Register system monitor plugin"""
    global system_monitor
    
    system_monitor = SystemMonitor()
    
    def handle_monitor_status_command(event):
        """Show current system status"""
        return system_monitor.get_current_status()
    
    def handle_monitor_start_command(event):
        """Start system monitoring"""
        return system_monitor.start_monitoring()
    
    def handle_monitor_stop_command(event):
        """Stop system monitoring"""
        return system_monitor.stop_monitoring()
    
    def handle_monitor_history_command(event):
        """Show historical data graph"""
        args = event.data.get('args', [])
        metric = args[0] if args else 'cpu'
        points = int(args[1]) if len(args) > 1 else 20
        
        return system_monitor.get_history_graph(metric, points)
    
    def handle_monitor_processes_command(event):
        """Show top processes"""
        args = event.data.get('args', [])
        count = int(args[0]) if args else 10
        
        return system_monitor.get_top_processes(count)
    
    def handle_monitor_alerts_command(event):
        """Configure monitoring alerts"""
        args = event.data.get('args', [])
        
        if not args:
            alerts = system_monitor.alerts
            result = "🔔 Alert Configuration:\\n"
            result += f"  Enabled: {{alerts['enabled']}}\\n"
            result += f"  CPU Threshold: {{alerts['cpu_threshold']}}%\\n"
            result += f"  Memory Threshold: {{alerts['memory_threshold']}}%\\n"
            result += f"  Disk Threshold: {{alerts['disk_threshold']}}%\\n"
            result += "\\nUsage: monitor-alerts <cpu|memory|disk|enabled> <value>"
            return result
        
        if len(args) < 2:
            return "Usage: monitor-alerts <cpu|memory|disk|enabled> <value>"
        
        key, value = args[0], args[1]
        
        try:
            if key == 'enabled':
                system_monitor.alerts['enabled'] = value.lower() in ['true', '1', 'yes', 'on']
            elif key == 'cpu':
                system_monitor.alerts['cpu_threshold'] = float(value)
            elif key == 'memory':
                system_monitor.alerts['memory_threshold'] = float(value)
            elif key == 'disk':
                system_monitor.alerts['disk_threshold'] = float(value)
            else:
                return f"❌ Unknown alert setting: {{key}}"
            
            system_monitor.save_config()
            return f"✅ Set alert.{{key}} = {{value}}"
        except ValueError:
            return f"❌ Invalid value for {{key}}: {{value}}"
    
    # Register commands
    shell.register_command('monitor', handle_monitor_status_command)
    shell.register_command('monitor-start', handle_monitor_start_command)
    shell.register_command('monitor-stop', handle_monitor_stop_command)
    shell.register_command('monitor-history', handle_monitor_history_command)
    shell.register_command('monitor-processes', handle_monitor_processes_command)
    shell.register_command('monitor-alerts', handle_monitor_alerts_command)
    
    print(f"📦 System Monitor plugin loaded with {{6}} commands")

def unregister(event_bus, shell):
    """Unregister system monitor plugin"""
    global system_monitor
    if system_monitor:
        system_monitor.stop_monitoring()
    
    shell.unregister_command('monitor')
    shell.unregister_command('monitor-start')
    shell.unregister_command('monitor-stop')
    shell.unregister_command('monitor-history')
    shell.unregister_command('monitor-processes')
    shell.unregister_command('monitor-alerts')
    print("📦 System Monitor plugin unloaded")

# Plugin metadata
PLUGIN_INFO = {
    "name": "system_monitor",
    "version": "1.0.0",
    "description": "Advanced system monitoring and alerting",
    "author": "Plugin Generator",
    "dependencies": ["psutil"],
    "features": ["monitoring", "alerts", "visualization", "history"],
    "generated": "{time.strftime('%Y-%m-%d %H:%M:%S')}"
}


class PluginGenerator:
    """Main plugin generator class"""
    
    def __init__(self):
        self.templates = PLUGIN_TEMPLATES
        self.generators = {
            "basic": generate_basic_plugin,
            "voice-enhanced": generate_voice_enhanced_plugin,
            "docker-advanced": generate_docker_advanced_plugin,
            "system-monitor": generate_system_monitor_plugin,
        }
    
    def list_templates(self) -> str:
        """List available plugin templates"""
        result = "🧩 Available Plugin Templates:\\n\\n"
        
        for template_name, template_info in self.templates.items():
            result += f"📦 **{{template_name}}**\\n"
            result += f"   {{template_info['description']}}\\n"
            result += f"   Dependencies: {{', '.join(template_info['dependencies']) if template_info['dependencies'] else 'None'}}\\n"
            result += f"   Features: {{', '.join(template_info['features'])}}\\n\\n"
        
        return result
    
    def generate_plugin(self, template_name: str, plugin_name: str, description: str = None) -> str:
        """Generate plugin from template"""
        if template_name not in self.templates:
            return f"❌ Unknown template: {{template_name}}. Available: {{', '.join(self.templates.keys())}}"
        
        template_info = self.templates[template_name]
        
        if description is None:
            description = template_info['description']
        
        # Generate plugin code
        if template_name in self.generators:
            plugin_code = self.generators[template_name](plugin_name, description)
        else:
            plugin_code = generate_basic_plugin(plugin_name, description)
        
        # Save to file
        plugins_dir = Path("plugins")
        plugins_dir.mkdir(exist_ok=True)
        
        plugin_file = plugins_dir / f"{{plugin_name}}.py"
        
        try:
            with open(plugin_file, 'w') as f:
                f.write(plugin_code)
            
            # Generate installation instructions
            deps = template_info['dependencies']
            install_cmd = f"pip install {{' '.join(deps)}}" if deps else "No dependencies required"
            
            result = f"""✅ Plugin generated successfully!

📁 File: {{plugin_file}
📦 Template: {{template_name}
🔧 Features: {{', '.join(template_info['features'])}

{{f'📥 Install dependencies: {{install_cmd}}' if deps else '✨ No dependencies required'}

🚀 Usage:
  1. Install dependencies (if any)
  2. Reload plugins: reload
  3. Use new commands (check with: help)

🧩 Plugin will be auto-loaded on next restart or reload!"""
            
            return result
            
        except Exception as e:
            return f"❌ Error saving plugin: {{e}}"
    
    def create_custom_template(self, template_name: str, description: str, 
                             features: List[str], dependencies: List[str] = None) -> str:
        """Create custom plugin template"""
        if dependencies is None:
            dependencies = []
        
        self.templates[template_name] = {{
            "description": description,
            "dependencies": dependencies,
            "features": features
        }
        
        return f"✅ Custom template '{{template_name}}' created with features: {{', '.join(features)}}"

# Plugin generator instance
plugin_generator = None

def register(event_bus, shell):
    """Register plugin generator as a plugin itself"""
    global plugin_generator
    
    plugin_generator = PluginGenerator()
    
    def handle_generate_command(event):
        """Generate new plugin from template"""
        args = event.data.get('args', [])
        
        if not args:
            return """Usage: generate <subcommand> [args]

Subcommands:
  list                          List available templates
  plugin <template> <name>     Generate plugin from template
  template <name> <desc>       Create custom template

Examples:
  generate list
  generate plugin voice-enhanced my-voice
  generate plugin basic calculator "Simple calculator plugin"
"""
        
        subcommand = args[0]
        
        if subcommand == "list":
            return plugin_generator.list_templates()
        
        elif subcommand == "plugin":
            if len(args) < 3:
                return "Usage: generate plugin <template> <plugin_name> [description]"
            
            template_name = args[1]
            plugin_name = args[2]
            description = ' '.join(args[3:]) if len(args) > 3 else None
            
            return plugin_generator.generate_plugin(template_name, plugin_name, description)
        
        elif subcommand == "template":
            if len(args) < 3:
                return "Usage: generate template <name> <description>"
            
            template_name = args[1]
            description = ' '.join(args[2:])
            features = ["custom"]  # Default features
            
            return plugin_generator.create_custom_template(template_name, description, features)
        
        else:
            return f"❌ Unknown subcommand: {{subcommand}}"
    
    def handle_templates_command(event):
        """List available templates (shortcut)"""
        return plugin_generator.list_templates()
    
    # Register commands
    shell.register_command('generate', handle_generate_command)
    shell.register_command('templates', handle_templates_command)
    
    print(f"📦 Plugin Generator loaded with {{len(plugin_generator.templates)}} templates")

def unregister(event_bus, shell):
    """Unregister plugin generator"""
    shell.unregister_command('generate')
    shell.unregister_command('templates')
    print("📦 Plugin Generator unloaded")

# Plugin metadata
PLUGIN_INFO = {
    "name": "plugin_generator",
    "version": "1.0.0",
    "description": "Generate new plugins from templates",
    "author": "dockevOS",
    "dependencies": [],
    "features": ["generation", "templates", "automation"],
    "generated": time.strftime('%Y-%m-%d %H:%M:%S')
}

# CLI usage
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python plugin_generator.py <template_name> [plugin_name] [description]")
        print("\\nAvailable templates:")
        for name, info in PLUGIN_TEMPLATES.items():
            print(f"  {{name:<20}} - {{info['description']}}")
        sys.exit(1)
    
    template_name = sys.argv[1]
    plugin_name = sys.argv[2] if len(sys.argv) > 2 else f"generated_{{template_name}}"
    description = ' '.join(sys.argv[3:]) if len(sys.argv) > 3 else None
    
    generator = PluginGenerator()
    result = generator.generate_plugin(template_name, plugin_name, description)
    print(result)