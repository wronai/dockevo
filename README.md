# dockevOS – DockEvo Operating Shell

Minimalna wersja Container OS - jeden plik Python realizujący pełną funkcjonalność.

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

## 🧩 Plugin Architecture

Plugins now live in dedicated sub-directories under `plugins/`, each with an `__init__.py`, optional README, and assets. This allows clean packaging, dependencies, and hot-reloading.

```
plugins/
├── system_log/            # Core logging service
│   ├── __init__.py
│   └── README.md
├── shell_assistant/       # AI repair assistant (Ollama / Mistral-7B)
│   ├── __init__.py
│   └── README.md
├── alternative_plugin/    # Fallback manager
│   ├── __init__.py
│   └── README.md
└── <your_plugin>/         # Create your own!
    ├── __init__.py
    └── README.md
```

### Auto-Repair Startup Flow

```
┌── dockevos boot ───────────────────────────────┐
│ 1. System Log collects env + dependency info   │
│ 2. Hardware Analyzer checks missing libs       │
│ 3. Shell Assistant (if permitted) auto-fixes   │
│ 4. Alternative Plugin offers fallbacks         │
└────────────────────────────────────────────────┘
```

If a package such as `pyaudio` is missing, the chain above will attempt automatic installation or guide you through manual fixes.

---

## 🧩 Plugin Development

1. Create file in `plugins/` directory:

Create a folder called `plugins/my_plugin/` with an `__init__.py`:

```python
# plugins/my_plugin/__init__.py
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

---

## ⚙️ Plugin Generator

A helper script lives in `plugins/plugin_generator.py` (run outside dockevOS) to scaffold new plugins.

```bash
python plugins/plugin_generator.py basic awesome
```

Inside dockevOS you can invoke (once the generator is registered):

```bash
dockevos> generate plugin basic awesome
```

This will create `plugins/awesome/` pre-populated with templates and register commands automatically.

---

## 📦 Built-In Example Plugins

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
dockevos> speak "Hello Container OS"

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

## 🛠️ Requirements & Auto-Repair

The first run performs a **dependency audit**. Missing libraries trigger the AI Shell Assistant which will ask for permission to install system or Python packages. Refuse, and the Alternative Plugin suggests manual work-arounds.

Key runtimes:
- Python 3.8+
- Docker (optional for container management)
- PortAudio + PyAudio (for voice)
- Ollama (for AI Shell Assistant)

- Python 3.7+
- Docker (optional, for container management)
- espeak/say (optional, for voice features)

## 📁 Updated File Structure

```
dockevos/
├── dockevos/              # Core package
│   └── __main__.py
├── plugins/               # All modular plugins (see tree above)
├── PLUGIN_SYSTEM.md       # ASCII architecture diagrams
├── Makefile               # Common dev commands
└── README.md

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

This MVP can evolve into full Container OS:
1. Start with single file
2. Add more plugins
3. Extend event system
4. Add web interface (optional)
5. Container deployment
6. Multi-node clustering

**Perfect for learning, development, and quick deployments!** 🚀
