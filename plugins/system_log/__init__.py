"""
System Log Plugin for dockevOS
Captures and manages system logs for analysis by other plugins
"""

import logging
import os
import sys
import json
import time
from pathlib import Path
from typing import Dict, List, Optional, Any, Union
from datetime import datetime

from ..error_handler import get_error_handler

class SystemLog:
    VERSION = "1.0.0"
    DESCRIPTION = "System log collection and management"
    
    def __init__(self, log_dir: str = "logs"):
        self.error_handler = get_error_handler()
        self.log_dir = Path(log_dir)
        self.log_file = self.log_dir / "system.log"
        self._setup_logging()
        self.command_history: List[Dict] = []
        self._register_commands()
    
    def _setup_logging(self):
        """Configure logging for system events"""
        try:
            self.log_dir.mkdir(parents=True, exist_ok=True)
            
            self.logger = logging.getLogger('dockevos_system')
            self.logger.setLevel(logging.DEBUG)
            
            # File handler for persistent logs
            file_handler = logging.FileHandler(self.log_file)
            file_handler.setLevel(logging.DEBUG)
            
            # Console handler for immediate feedback
            console_handler = logging.StreamHandler()
            console_handler.setLevel(logging.INFO)
            
            # Formatter
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
            
            file_handler.setFormatter(formatter)
            console_handler.setFormatter(formatter)
            
            # Add handlers
            self.logger.addHandler(file_handler)
            self.logger.addHandler(console_handler)
            
            # Log system info
            self.log_system_info()
            
        except Exception as e:
            print(f"❌ Failed to initialize system log: {e}")
            self.error_handler.log_error(e, {'context': 'system_log setup'})
    
    def log_system_info(self):
        """Log basic system information"""
        try:
            import platform
            import psutil
            
            system_info = {
                'timestamp': datetime.now().isoformat(),
                'system': {
                    'os': platform.system(),
                    'os_version': platform.version(),
                    'os_release': platform.release(),
                    'machine': platform.machine(),
                    'processor': platform.processor(),
                    'python_version': platform.python_version(),
                },
                'hardware': {
                    'cpu_cores': psutil.cpu_count(),
                    'cpu_percent': psutil.cpu_percent(),
                    'memory_total': psutil.virtual_memory().total,
                    'memory_available': psutil.virtual_memory().available,
                    'disk_usage': dict(psutil.disk_usage('/')._asdict()),
                }
            }
            
            self.logger.info("System information collected")
            return system_info
            
        except Exception as e:
            self.error_handler.log_error(e, {'context': 'collecting system info'})
            return {}
    
    def log_command(self, command: str, args: List[str], success: bool, 
                   output: Optional[str] = None, error: Optional[str] = None):
        """Log a command execution"""
        try:
            entry = {
                'timestamp': datetime.now().isoformat(),
                'command': command,
                'args': args,
                'success': success,
                'output': output,
                'error': error
            }
            
            self.command_history.append(entry)
            self.logger.debug(f"Command executed: {command} {args}")
            
            # Keep command history manageable
            if len(self.command_history) > 1000:
                self.command_history = self.command_history[-1000:]
                
            return entry
            
        except Exception as e:
            self.error_handler.log_error(e, {'context': 'logging command'})
    
    def get_recent_logs(self, limit: int = 50) -> List[Dict]:
        """Get recent log entries"""
        try:
            # Read from log file if needed
            if self.log_file.exists():
                with open(self.log_file, 'r') as f:
                    lines = f.readlines()[-limit:]
                return [line.strip() for line in lines]
            return []
        except Exception as e:
            self.error_handler.log_error(e, {'context': 'getting recent logs'})
            return []
    
    def get_command_history(self, limit: int = 20) -> List[Dict]:
        """Get command history"""
        return self.command_history[-limit:]
    
    def _register_commands(self):
        """Register command handlers"""
        self.commands = {
            'logs': self.cmd_show_logs,
            'history': self.cmd_show_history,
            'system_info': self.cmd_system_info
        }
    
    async def cmd_show_logs(self, *args):
        """Show recent system logs"""
        try:
            limit = int(args[0]) if args else 20
            logs = self.get_recent_logs(limit)
            print(f"\n📜 Last {len(logs)} log entries:")
            print("-" * 80)
            for log in logs:
                print(log)
            print("-" * 80)
            return True
        except Exception as e:
            self.error_handler.log_error(e, {'action': 'show_logs', 'args': args})
            return False
    
    async def cmd_show_history(self, *args):
        """Show command history"""
        try:
            limit = int(args[0]) if args else 10
            history = self.get_command_history(limit)
            print(f"\n📜 Command History (last {len(history)}):")
            print("-" * 80)
            for i, entry in enumerate(history, 1):
                status = "✅" if entry.get('success') else "❌"
                cmd = f"{entry.get('command', '')} {' '.join(entry.get('args', []))}"
                print(f"{i:3d}. {status} {cmd}")
                if entry.get('error'):
                    print(f"    Error: {entry.get('error')}")
            print("-" * 80)
            return True
        except Exception as e:
            self.error_handler.log_error(e, {'action': 'show_history', 'args': args})
            return False
    
    async def cmd_system_info(self, *args):
        """Show system information"""
        try:
            info = self.log_system_info()
            print("\n🖥️  System Information:")
            print("-" * 80)
            print(f"OS: {info.get('system', {}).get('os')} {info.get('system', {}).get('os_release')}")
            print(f"CPU: {info.get('hardware', {}).get('cpu_cores')} cores")
            print(f"Memory: {info.get('hardware', {}).get('memory_available')/1024/1024:.1f} MB available")
            print(f"Disk: {info.get('hardware', {}).get('disk_usage', {}).get('percent')}% used")
            print("-" * 80)
            return True
        except Exception as e:
            self.error_handler.log_error(e, {'action': 'system_info'})
            return False

def setup():
    """Plugin setup function"""
    return SystemLog()
