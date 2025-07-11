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
