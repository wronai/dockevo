"""
Error Handler Plugin for dockevOS
Handles error logging, spell checking, and plugin communication
"""

import difflib
import logging
from typing import Dict, List, Optional, Any, Callable
import importlib
import sys
from pathlib import Path

class ErrorHandler:
    def __init__(self):
        self.logger = self._setup_logging()
        self.known_commands: List[str] = []
        self.plugin_handlers: Dict[str, Callable] = {}
        self._load_plugin_handlers()

    def _setup_logging(self) -> logging.Logger:
        """Configure logging for the error handler"""
        logger = logging.getLogger('dockevos_error')
        logger.setLevel(logging.DEBUG)
        
        # Create logs directory if it doesn't exist
        log_dir = Path('logs')
        log_dir.mkdir(exist_ok=True)
        
        # File handler
        file_handler = logging.FileHandler(log_dir / 'dockevos_errors.log')
        file_handler.setLevel(logging.DEBUG)
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        # Formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
        
        return logger

    def _load_plugin_handlers(self):
        """Dynamically load error handlers from plugins"""
        plugins_dir = Path('plugins')
        for plugin_file in plugins_dir.glob('**/*_handler.py'):
            try:
                module_name = f"{plugin_file.parent.name}.{plugin_file.stem}"
                module = importlib.import_module(f"plugins.{module_name}")
                if hasattr(module, 'register_handler'):
                    module.register_handler(self)
                    self.logger.info(f"Loaded error handler from {module_name}")
            except Exception as e:
                self.logger.error(f"Error loading handler {plugin_file}: {e}")

    def register_commands(self, commands: List[str]):
        """Register known commands for spell checking"""
        self.known_commands.extend(commands)
        self.known_commands = list(set(self.known_commands))  # Remove duplicates

    def suggest_correction(self, word: str) -> Optional[str]:
        """Suggest correction for a mistyped command"""
        if not self.known_commands:
            return None
            
        matches = difflib.get_close_matches(
            word.lower(),
            [cmd.lower() for cmd in self.known_commands],
            n=1,
            cutoff=0.6
        )
        return matches[0] if matches else None

    def log_error(self, error: Exception, context: Optional[Dict] = None):
        """Log an error with context"""
        error_info = {
            'type': type(error).__name__,
            'message': str(error),
            'context': context or {}
        }
        self.logger.error(f"Error occurred: {error_info}")
        self._notify_handlers('error_occurred', error_info)

    def _notify_handlers(self, event_type: str, data: Any):
        """Notify all registered handlers about an event"""
        for handler in self.plugin_handlers.get(event_type, []):
            try:
                handler(data)
            except Exception as e:
                self.logger.error(f"Error in handler for {event_type}: {e}")

    def register_handler(self, event_type: str, handler: Callable):
        """Register a new event handler"""
        if event_type not in self.plugin_handlers:
            self.plugin_handlers[event_type] = []
        self.plugin_handlers[event_type].append(handler)
        self.logger.debug(f"Registered handler for {event_type}")

# Singleton instance
error_handler = ErrorHandler()

def register(event_bus, shell):
    """Register the error handler plugin
    
    Args:
        event_bus: The event bus instance
        shell: The shell instance
    """
    # The error handler is a core service that doesn't need to register commands
    # as it's already available through the shell
    print(" Error Handler loaded")
    return error_handler

def get_error_handler() -> ErrorHandler:
    """Get the global error handler instance"""
    return error_handler
