# Alternative Plugin

## Overview
The Alternative Plugin provides fallback implementations and alternative solutions when the primary plugins are unavailable or when permissions are denied. It ensures system functionality by offering substitute implementations and guiding users through manual alternatives.

## Features

- **Plugin Alternatives**: Provides fallback implementations for core plugins
- **Graceful Degradation**: Maintains functionality when primary plugins fail
- **User Guidance**: Offers step-by-step instructions for manual alternatives
- **Dynamic Loading**: Can load alternative implementations at runtime
- **Permission-Aware**: Respects user permissions and access levels

## Usage

### Commands

- `alternatives [plugin]` - List available alternatives for all plugins or a specific one
- `use <plugin> <alternative>` - Switch to an alternative implementation

### Examples

1. **List all alternatives**:
   ```
   dockevos> alternatives
   ```

2. **List alternatives for a specific plugin**:
   ```
   dockevos> alternatives shell_assistant
   ```

3. **Switch to an alternative implementation**:
   ```
   dockevos> use shell_assistant manual_installer
   ```

## Available Alternatives

### Shell Assistant Alternatives

1. **Manual Installer**
   - Description: Provides step-by-step instructions for manual package installation
   - Use when: Automated installation fails or is not permitted
   - Command: `use shell_assistant manual_installer`

2. **Package Manager**
   - Description: Basic package management interface
   - Use when: Full shell assistant is not available
   - Command: `use shell_assistant package_manager`

### Voice Service Alternatives

1. **Text Input**
   - Description: Fallback text input when voice is unavailable
   - Use when: Microphone access is denied or not available
   - Command: `use voice_service text_input`

## Integration

The Alternative Plugin integrates with:

- **Plugin Manager**: For dynamic loading of alternatives
- **Error Handler**: To detect when alternatives are needed
- **Permission System**: To respect user preferences

## Adding New Alternatives

To add a new alternative implementation:

1. Create a new plugin module in the `plugins/` directory
2. Implement the required interface for the plugin being replaced
3. Add an entry to the `_load_alternatives` method in `__init__.py`

Example:
```python
self.alternatives['target_plugin'] = [
    {
        'name': 'my_alternative',
        'description': 'My alternative implementation',
        'module': 'plugins.my_alternative',
        'class': 'MyAlternativeClass'
    }
]
```

## Best Practices

1. **Keep it Simple**: Alternatives should be lightweight and have minimal dependencies
2. **Graceful Degradation**: Provide the most functionality possible with available resources
3. **Clear Instructions**: Include detailed guidance for manual alternatives
4. **Permission Awareness**: Respect user permissions and access levels
5. **Error Handling**: Provide clear error messages and recovery options

## Troubleshooting

If an alternative fails to load:
1. Check that the module and class names are correct
2. Verify the alternative implements the required interface
3. Check for dependency issues
4. Review the error logs for specific issues

## License

MIT License - See main project license.
