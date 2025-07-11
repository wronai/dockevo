
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
