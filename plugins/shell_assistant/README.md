# Shell Assistant Plugin

## Overview
The Shell Assistant Plugin integrates Ollama's Mistral 7B model to provide AI-powered assistance for system administration tasks, including error analysis, package installation, and issue resolution.

## Features

- **AI-Powered Analysis**: Uses Mistral 7B to analyze errors and suggest fixes
- **Automated Package Installation**: Installs system and Python packages with permission
- **Interactive Fixes**: Guides through the resolution process with step-by-step commands
- **Permission Management**: Requests and manages required permissions
- **Log Analysis**: Integrates with System Log plugin for context-aware assistance

## Prerequisites

- Ollama installed and running
- Mistral 7B model downloaded (will be handled automatically)
- Internet access for model downloads

## Installation

The plugin will automatically install Ollama and download the Mistral model if needed. You'll be prompted to grant necessary permissions during initialization.

## Usage

### Commands

- `analyze [error]` - Analyze an error message or recent logs
- `fix [error]` - Attempt to automatically fix an issue
- `install <package> [version]` - Install a system or Python package

### Examples

1. **Analyze an error**:
   ```
   dockevos> analyze "ModuleNotFoundError: No module named 'pyaudio'"
   ```

2. **Fix an issue**:
   ```
   dockevos> fix "Error: Port 8080 is already in use"
   ```

3. **Install a package**:
   ```
   dockevos> install pyaudio
   ```

## Permissions

The plugin requests the following permissions:

- `install_packages`: Install system and Python packages
- `read_logs`: Read system and application logs
- `execute_commands`: Execute shell commands
- `access_network`: Download models and packages
- `modify_files`: Create and modify configuration files

## Integration

The Shell Assistant integrates with:

- **System Log Plugin**: For log analysis and context
- **Error Handler**: For error tracking and reporting
- **Plugin Manager**: For inter-plugin communication

## Troubleshooting

1. **Model Loading Issues**:
   - Ensure Ollama is installed and running
   - Check internet connection for model downloads
   - Verify sufficient disk space for the model (~4GB)

2. **Permission Denied Errors**:
   - Grant the required permissions during initialization
   - Run dockevOS with appropriate privileges

3. **Command Execution Failures**:
   - Check system requirements
   - Verify package repositories are up to date

## Alternatives

If the Shell Assistant cannot be used, consider these alternatives:

1. Manual package installation
2. Using system package managers directly
3. Consulting system documentation

## License

MIT License - See main project license.
