# System Log Plugin

## Overview
The System Log Plugin provides comprehensive logging capabilities for dockevOS, capturing system events, command history, and performance metrics. It serves as a central logging service that other plugins can utilize for monitoring and debugging purposes.

## Features

- **Command Logging**: Tracks all executed commands with arguments, timestamps, and success/failure status
- **System Monitoring**: Collects hardware and OS information including CPU, memory, and disk usage
- **Persistent Storage**: Maintains logs in a structured format for long-term analysis
- **Query Interface**: Allows other plugins to retrieve and analyze log data
- **Performance Metrics**: Tracks system resource usage over time

## Usage

### Available Commands

- `logs [limit]` - Show recent system logs (default: 20 entries)
- `history [limit]` - Show command history (default: 10 entries)
- `system_info` - Display current system information

### Integration with Other Plugins

Other plugins can access the system log through the plugin manager:

```python
from plugins import get_plugin_manager

# Get the system log plugin
system_log = get_plugin_manager().plugins.get('system_log')

# Log a custom event
system_log.logger.info("Custom event from my plugin")

# Get recent command history
history = system_log.get_command_history(10)
```

## Configuration

Logs are stored in the `logs/` directory by default. You can customize the log directory by modifying the plugin initialization.

## Dependencies

- Python 3.8+
- `psutil` for system monitoring

## Permissions

This plugin requires read/write access to the log directory and read access to system information.
