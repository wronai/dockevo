#!/bin/bash
set -e

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Logging functions
log() { echo -e "${GREEN}[SETUP]${NC} $1"; }
info() { echo -e "${BLUE}[INFO]${NC} $1"; }
warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
error() { echo -e "${RED}[ERROR]${NC} $1"; exit 1; }

show_banner() {
    echo -e "${BLUE}"
    cat << 'EOF'
╔══════════════════════════════════════════════════╗
║              dockevOS MVP Setup              ║
║                                                  ║
║  🚀 Quick setup for minimal viable system       ║
╚══════════════════════════════════════════════════╝
EOF
    echo -e "${NC}"
}

check_python() {
    log "Checking Python installation..."
    
    if ! command -v python3 &> /dev/null; then
        echo "❌ Python 3 not found. Please install Python 3.7+"
        exit 1
    fi
    
    python_version=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
    info "Python version: $python_version"
}

install_dependencies() {
    log "Installing Python dependencies..."
    
    # Check if pip is available
    if ! command -v pip3 &> /dev/null; then
        warn "pip3 not found, trying to install..."
        if command -v apt-get &> /dev/null; then
            sudo apt-get update && sudo apt-get install -y python3-pip
        elif command -v yum &> /dev/null; then
            sudo yum install -y python3-pip
        elif command -v brew &> /dev/null; then
            brew install python3
        else
            echo "❌ Cannot install pip. Please install manually."
            exit 1
        fi
    fi
    
    # Install required packages
    pip3 install --user docker psutil
    
    log "Dependencies installed successfully"
}

check_docker() {
    log "Checking Docker installation..."
    
    if ! command -v docker &> /dev/null; then
        warn "Docker not found. dockevOS will work with limited functionality."
        info "To install Docker: curl -fsSL https://get.docker.com | sh"
        return
    fi
    
    # Check if Docker daemon is running
    if ! docker info &> /dev/null; then
        warn "Docker daemon not running. Some features may not work."
        info "Start Docker: sudo systemctl start docker"
        return
    fi
    
    info "Docker is available and running"
}

setup_audio() {
    log "Setting up audio for voice features..."
    
    # Check for TTS tools
    tts_available=false
    
    if command -v espeak &> /dev/null; then
        info "Found espeak for text-to-speech"
        tts_available=true
    elif command -v say &> /dev/null; then
        info "Found say for text-to-speech (macOS)"
        tts_available=true
    elif command -v spd-say &> /dev/null; then
        info "Found spd-say for text-to-speech"
        tts_available=true
    fi
    
    if [ "$tts_available" = false ]; then
        warn "No TTS engine found. Installing espeak..."
        
        if command -v apt-get &> /dev/null; then
            sudo apt-get update && sudo apt-get install -y espeak
        elif command -v yum &> /dev/null; then
            sudo yum install -y espeak
        elif command -v brew &> /dev/null; then
            brew install espeak
        else
            warn "Cannot install TTS engine. Voice features will use text fallback."
        fi
    fi
}

create_project_structure() {
    log "Creating project structure..."
    
    # Create plugins directory
    mkdir -p plugins
    
    # Create advanced plugin example
    cat > plugins/advanced_plugin.py << 'EOF'
"""
Advanced Plugin Example for dockevOS MVP
Shows more complex plugin capabilities
"""

import time
import json
from pathlib import Path

def register(event_bus, shell):
    """Register advanced plugin handlers"""
    
    def handle_weather_command(event):
        """Mock weather command"""
        args = event.data.get('args', [])
        city = args[0] if args else 'Unknown'
        
        # Mock weather data
        weather_data = {
            'city': city,
            'temperature': '22°C',
            'condition': 'Sunny',
            'humidity': '65%'
        }
        
        return f"🌤️  Weather in {city}: {weather_data['temperature']}, {weather_data['condition']}"
    
    def handle_note_command(event):
        """Simple note-taking"""
        args = event.data.get('args', [])
        
        if not args:
            return "Usage: note <add|list|clear> [text]"
        
        action = args[0]
        notes_file = Path('notes.json')
        
        # Load existing notes
        notes = []
        if notes_file.exists():
            try:
                with open(notes_file, 'r') as f:
                    notes = json.load(f)
            except:
                notes = []
        
        if action == 'add' and len(args) > 1:
            note_text = ' '.join(args[1:])
            note = {
                'text': note_text,
                'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
            }
            notes.append(note)
            
            # Save notes
            with open(notes_file, 'w') as f:
                json.dump(notes, f, indent=2)
            
            return f"📝 Note added: {note_text}"
        
        elif action == 'list':
            if not notes:
                return "📝 No notes found"
            
            result = "📝 Your notes:\n"
            for i, note in enumerate(notes[-5:], 1):  # Show last 5 notes
                result += f"  {i}. {note['text']} ({note['timestamp']})\n"
            return result
        
        elif action == 'clear':
            if notes_file.exists():
                notes_file.unlink()
            return "📝 All notes cleared"
        
        else:
            return "Usage: note <add|list|clear> [text]"
    
    def handle_calc_command(event):
        """Simple calculator"""
        args = event.data.get('args', [])
        
        if not args:
            return "Usage: calc <expression> (e.g., calc 2 + 2)"
        
        try:
            expression = ' '.join(args)
            # Safe evaluation of basic math
            allowed_chars = set('0123456789+-*/.() ')
            if all(c in allowed_chars for c in expression):
                result = eval(expression)
                return f"🧮 {expression} = {result}"
            else:
                return "❌ Invalid characters in expression"
        except Exception as e:
            return f"❌ Calculation error: {e}"
    
    def handle_uptime_command(event):
        """Show system uptime and load"""
        try:
            import psutil
            import datetime
            
            boot_time = psutil.boot_time()
            uptime = datetime.datetime.now() - datetime.datetime.fromtimestamp(boot_time)
            
            load_avg = psutil.getloadavg() if hasattr(psutil, 'getloadavg') else (0, 0, 0)
            
            return f"⏰ Uptime: {uptime} | Load: {load_avg[0]:.2f}, {load_avg[1]:.2f}, {load_avg[2]:.2f}"
        except Exception as e:
            return f"❌ Error getting uptime: {e}"
    
    # Register all commands
    shell.register_command('weather', handle_weather_command)
    shell.register_command('note', handle_note_command)
    shell.register_command('calc', handle_calc_command)
    shell.register_command('uptime', handle_uptime_command)
    
    print("📦 Advanced plugin loaded: weather, note, calc, uptime")

def unregister(event_bus, shell):
    """Unregister plugin handlers"""
    shell.unregister_command('weather')
    shell.unregister_command('note')
    shell.unregister_command('calc')
    shell.unregister_command('uptime')
    print("📦 Advanced plugin unloaded")
EOF

    # Create system info plugin
    cat > plugins/system_info_plugin.py << 'EOF'
"""
System Information Plugin
Extended system monitoring capabilities
"""

def register(event_bus, shell):
    """Register system info plugin"""
    
    def handle_disk_command(event):
        """Show disk usage"""
        try:
            import psutil
            partitions = psutil.disk_partitions()
            
            result = "💿 Disk Usage:\n"
            for partition in partitions:
                try:
                    usage = psutil.disk_usage(partition.mountpoint)
                    result += f"  {partition.device} ({partition.mountpoint}): "
                    result += f"{usage.percent:.1f}% used "
                    result += f"({usage.used // 1024**3}GB / {usage.total // 1024**3}GB)\n"
                except PermissionError:
                    result += f"  {partition.device}: Permission denied\n"
            
            return result
        except Exception as e:
            return f"❌ Error getting disk info: {e}"
    
    def handle_network_command(event):
        """Show network information"""
        try:
            import psutil
            
            # Network interfaces
            interfaces = psutil.net_if_addrs()
            stats = psutil.net_io_counters(pernic=True)
            
            result = "🌐 Network Interfaces:\n"
            for interface, addresses in interfaces.items():
                if interface.startswith('lo'):  # Skip loopback
                    continue
                
                result += f"  {interface}:\n"
                for addr in addresses:
                    if addr.family.name == 'AF_INET':
                        result += f"    IP: {addr.address}\n"
                
                if interface in stats:
                    stat = stats[interface]
                    result += f"    RX: {stat.bytes_recv // 1024**2}MB, TX: {stat.bytes_sent // 1024**2}MB\n"
            
            return result
        except Exception as e:
            return f"❌ Error getting network info: {e}"
    
    def handle_processes_command(event):
        """Show top processes"""
        try:
            import psutil
            
            # Get top 10 processes by CPU usage
            processes = []
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
                try:
                    proc_info = proc.info
                    if proc_info['cpu_percent'] > 0:
                        processes.append(proc_info)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
            
            # Sort by CPU usage
            processes.sort(key=lambda x: x['cpu_percent'], reverse=True)
            
            result = "🔄 Top Processes (by CPU):\n"
            result += "PID     NAME                CPU%    MEM%\n"
            for proc in processes[:10]:
                result += f"{proc['pid']:<8} {proc['name']:<15} {proc['cpu_percent']:<8.1f} {proc['memory_percent']:<8.1f}\n"
            
            return result
        except Exception as e:
            return f"❌ Error getting process info: {e}"
    
    # Register commands
    shell.register_command('disk', handle_disk_command)
    shell.register_command('network', handle_network_command)
    shell.register_command('processes', handle_processes_command)
    shell.register_command('top', handle_processes_command)  # Alias
    
    print("📦 System info plugin loaded: disk, network, processes, top")

def unregister(event_bus, shell):
    """Unregister plugin"""
    shell.unregister_command('disk')
    shell.unregister_command('network')
    shell.unregister_command('processes')
    shell.unregister_command('top')
    print("📦 System info plugin unloaded")
EOF

    log "Project structure created with example plugins"
}

create_launcher() {
    log "Creating launcher script..."
    
    cat > run-dockevos.sh << 'EOF'
#!/bin/bash

# dockevOS MVP Launcher
echo "🚀 Starting dockevOS MVP..."

# Check if main file exists
if [ ! -f "dockevos.py" ]; then
    echo "❌ dockevos.py not found"
    echo "Please run this script from the dockevOS directory"
    exit 1
fi

# Check Python dependencies
python3 -c "import docker, psutil" 2>/dev/null || {
    echo "❌ Missing dependencies. Run setup.sh first"
    exit 1
}

# Start dockevOS
python3 dockevos.py
EOF

    chmod +x run-dockevos.sh
    
    log "Launcher script created: run-dockevos.sh"
}

create_readme() {
    log "Creating README..."
    
    cat > README.md << 'EOF'
# dockevOS MVP

Minimalna wersja dockevOS - jeden plik Python realizujący pełną funkcjonalność.

## 🚀 Quick Start

```bash
# Setup (one time)
./setup.sh

# Run
./run-dockevos.sh
# OR
python3 dockevos.py
```

## ✨ Features

- 🐳 **Docker Management** - ps, start, stop containers
- 🎤 **Voice Control** - Text-to-speech feedback
- 🧩 **Plugin System** - Hot-reload plugins
- 📊 **Self-Learning** - Usage statistics and suggestions
- ⚡ **Event-Driven** - Extensible architecture

## 🎯 Basic Commands

```bash
dockevos> help          # Show all commands
dockevos> ps            # List containers
dockevos> start nginx   # Start container
dockevos> stop nginx    # Stop container
dockevos> info          # System information
dockevos> speak hello   # Text-to-speech test
dockevos> plugins       # List loaded plugins
dockevos> stats         # Usage statistics
```

## 🧩 Plugin Development

1. Create file in `plugins/` directory:

```python
# plugins/my_plugin.py
def register(event_bus, shell):
    def my_command(event):
        return "Hello from my plugin!"
    
    shell.register_command('my-cmd', my_command)
    print("📦 My plugin loaded")

def unregister(event_bus, shell):
    shell.unregister_command('my-cmd')
```

2. Save file → automatic hot-reload
3. Use command: `my-cmd`

## 📦 Example Plugins

### Basic Commands
- `hello [name]` - Greeting
- `time` - Current time

### Advanced Commands  
- `weather [city]` - Mock weather info
- `note add|list|clear [text]` - Simple notes
- `calc 2 + 2` - Calculator
- `uptime` - System uptime

### System Info
- `disk` - Disk usage
- `network` - Network interfaces
- `processes` - Top processes

## 🎤 Voice Features

```bash
# Test TTS
dockevos> speak "Hello dockevOS"

# Voice feedback on actions
dockevos> start nginx
🔊 "Container nginx started"
```

## 🔄 Hot-Reload Demo

1. Edit `plugins/sample_plugin.py`
2. Add new command function
3. Save file
4. Command immediately available

## 📊 Self-Learning

System tracks usage and provides suggestions:
- Command frequency analysis
- Alias suggestions for frequent commands
- Usage statistics

## 🐳 Docker Integration

Works with local Docker daemon:
- List containers (all or running)
- Start/stop containers by name or ID
- Voice feedback for actions

## 🛠️ Requirements

- Python 3.7+
- Docker (optional, for container management)
- espeak/say (optional, for voice features)

## 📁 File Structure

```
dockevos/
├── dockevos.py     # Main application (single file!)
├── setup.sh           # Setup script
├── run-dockevos.sh    # Launcher
├── plugins/               # Plugin directory
│   ├── sample_plugin.py   # Basic examples
│   ├── advanced_plugin.py # Advanced features
│   └── system_info_plugin.py # System monitoring
└── README.md          # This file
```

## 🎯 Evolution Path

This MVP can evolve into full dockevOS:
1. Start with single file
2. Add more plugins
3. Extend event system
4. Add web interface (optional)
5. Container deployment
6. Multi-node clustering

**Perfect for learning, development, and quick deployments!** 🚀
EOF

    log "README created: README.md"
}

show_completion() {
    echo ""
    echo -e "${GREEN}🎉 dockevOS MVP Setup Complete!${NC}"
    echo ""
    echo "📁 Created files:"
    echo "  • dockevos.py     - Main application"
    echo "  • setup.sh           - This setup script"
    echo "  • run-dockevos.sh    - Launcher script"
    echo "  • plugins/               - Plugin directory with examples"
    echo "  • README.md          - Documentation"
    echo ""
    echo "🚀 Quick start:"
    echo "  ./run-dockevos.sh"
    echo ""
    echo "💡 Try these commands:"
    echo "  help              - Show all commands"
    echo "  ps                - List Docker containers"
    echo "  speak hello       - Test voice features"
    echo "  hello world       - Test plugin system"
    echo "  plugins           - List loaded plugins"
    echo ""
    echo "🧩 Plugin development:"
    echo "  Edit files in plugins/ for hot-reload"
    echo "  See plugins/sample_plugin.py for examples"
    echo ""
    echo "Happy containerizing! 🐳"
}

# Check if running in a virtual environment
in_venv() {
    python3 -c 'import sys; sys.exit(0) if hasattr(sys, "real_prefix") or (hasattr(sys, "base_prefix") and sys.base_prefix != sys.prefix) else sys.exit(1)'
}

# Create virtual environment if not exists
create_venv() {
    if [ ! -d "venv" ]; then
        log "Creating virtual environment..."
        python3 -m venv venv
        source venv/bin/activate
    elif ! in_venv; then
        log "Activating existing virtual environment..."
        source venv/bin/activate
    fi
}

# Install development dependencies
install_dev_dependencies() {
    log "Installing development dependencies..."
    pip install -e ".[dev]"
}

# Install STT dependencies
install_stt_dependencies() {
    log "Installing optional STT dependencies..."
    pip install -e ".[stt]"
}

# Main execution
main() {
    show_banner
    
    # Check Python version
    check_python
    
    # Create and activate virtual environment
    create_venv
    
    # Install core dependencies
    log "Installing core dependencies..."
    pip install -e .
    
    # Install development dependencies
    read -p "Install development dependencies? [y/N] " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        install_dev_dependencies
    fi
    
    # Install STT dependencies
    read -p "Install STT (Speech-to-Text) dependencies? [y/N] " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        install_stt_dependencies
    fi
    
    # Check Docker
    check_docker
    
    # Setup audio
    setup_audio
    
    # Show completion message
    show_completion
}

main "$@"