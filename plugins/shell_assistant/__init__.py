"""
Shell Assistant Plugin for dockevOS
Uses Ollama/Mistral AI to analyze logs, fix issues, and install packages
"""

import os
import sys
import json
import subprocess
import asyncio
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple, Union

from ..error_handler import get_error_handler
from ..system_log import SystemLog

class ShellAssistant:
    VERSION = "1.0.0"
    DESCRIPTION = "AI-powered shell assistant with Ollama/Mistral integration"
    
    # Required permissions with descriptions
    REQUIRED_PERMISSIONS = {
        'install_packages': 'Install system and Python packages',
        'read_logs': 'Read system and application logs',
        'execute_commands': 'Execute shell commands',
        'access_network': 'Download models and packages',
        'modify_files': 'Create and modify configuration files'
    }
    
    # Alternative plugins that provide similar functionality
    ALTERNATIVES = [
        'manual_installer',
        'package_manager',
        'system_monitor'
    ]
    
    def __init__(self):
        self.error_handler = get_error_handler()
        self.system_log: Optional[SystemLog] = None
        self.permissions = {perm: False for perm in self.REQUIRED_PERMISSIONS}
        self.ollama_installed = False
        self.model_loaded = False
        self._register_commands()
    
    async def initialize(self):
        """Initialize the plugin and request permissions"""
        # Get system log plugin
        plugin_manager = get_plugin_manager()
        self.system_log = plugin_manager.plugins.get('system_log')
        
        # Request permissions
        await self._request_permissions()
        
        # Check for Ollama installation
        self.ollama_installed = await self._check_ollama_installed()
        
        if not self.ollama_installed and self.permissions['install_packages']:
            await self._install_ollama()
        
        # Load Mistral model if available
        if self.ollama_installed and self.permissions['access_network']:
            self.model_loaded = await self._load_mistral_model()
    
    async def _request_permissions(self) -> bool:
        """Request required permissions from the user"""
        print("\n🔐 Shell Assistant requires the following permissions:")
        
        for perm, description in self.REQUIRED_PERMISSIONS.items():
            while True:
                response = input(f"Allow {description}? (Y/n): ").strip().lower()
                if response in ['y', '']:
                    self.permissions[perm] = True
                    break
                elif response == 'n':
                    print(f"⚠️  {description} will be disabled")
                    break
                else:
                    print("Please enter 'y' or 'n'")
        
        # Check if we have minimum required permissions
        min_required = {'read_logs', 'execute_commands'}
        if not all(self.permissions[p] for p in min_required):
            print("\n❌ Insufficient permissions. The following permissions are required:")
            for p in min_required:
                print(f"- {self.REQUIRED_PERMISSIONS[p]}")
            print("\nPlease restart and grant the required permissions.")
            return False
            
        return True
    
    async def _check_ollama_installed(self) -> bool:
        """Check if Ollama is installed and running"""
        try:
            result = subprocess.run(['ollama', '--version'], 
                                 capture_output=True, 
                                 text=True)
            return result.returncode == 0
        except (FileNotFoundError, subprocess.SubprocessError):
            return False
    
    async def _install_ollama(self) -> bool:
        """Install Ollama if not present"""
        if not self.permissions['install_packages']:
            print("❌ Cannot install Ollama: Missing install_packages permission")
            return False
            
        print("\n🛠️  Installing Ollama...")
        
        try:
            # Determine system type
            if sys.platform == 'linux':
                install_cmd = "curl -fsSL https://ollama.com/install.sh | sh"
                result = subprocess.run(install_cmd, 
                                     shell=True, 
                                     capture_output=True, 
                                     text=True)
            elif sys.platform == 'darwin':
                result = subprocess.run(['brew', 'install', 'ollama'],
                                     capture_output=True,
                                     text=True)
            else:
                print("❌ Automatic Ollama installation is not supported on this platform")
                print("Please install Ollama manually from https://ollama.com")
                return False
            
            if result.returncode != 0:
                print(f"❌ Failed to install Ollama: {result.stderr}")
                return False
                
            print("✅ Ollama installed successfully")
            self.ollama_installed = True
            return True
            
        except Exception as e:
            self.error_handler.log_error(e, {'action': 'install_ollama'})
            print(f"❌ Error installing Ollama: {e}")
            return False
    
    async def _load_mistral_model(self) -> bool:
        """Load the Mistral model in Ollama"""
        print("\n🧠 Loading Mistral model (this may take a few minutes)...")
        
        try:
            # Check if model is already downloaded
            check_cmd = ['ollama', 'list']
            result = subprocess.run(check_cmd, 
                                 capture_output=True, 
                                 text=True)
            
            if 'mistral' not in result.stdout.lower():
                # Pull the model
                pull_cmd = ['ollama', 'pull', 'mistral:7b']
                process = await asyncio.create_subprocess_exec(
                    *pull_cmd,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
                
                # Stream the output
                while True:
                    output = await process.stdout.readline()
                    if not output:
                        break
                    print(output.decode().strip())
                
                # Wait for completion
                return_code = await process.wait()
                if return_code != 0:
                    print("❌ Failed to load Mistral model")
                    return False
            
            print("✅ Mistral model loaded successfully")
            return True
            
        except Exception as e:
            self.error_handler.log_error(e, {'action': 'load_mistral'})
            print(f"❌ Error loading Mistral model: {e}")
            return False
    
    async def analyze_issue(self, error_message: str) -> Dict[str, Any]:
        """Analyze an error message and suggest fixes"""
        if not self.model_loaded:
            return {
                'success': False,
                'error': 'Mistral model not loaded',
                'suggestion': 'Make sure Ollama is installed and the model is loaded'
            }
        
        try:
            # Get recent logs for context
            logs = "\n".join(self.system_log.get_recent_logs(20) if self.system_log else [])
            
            # Prepare the prompt
            prompt = f"""
            Analyze the following error and suggest a fix:
            
            Error: {error_message}
            
            Recent logs:
            {logs}
            
            Please provide:
            1. A brief description of the issue
            2. Step-by-step instructions to fix it
            3. Commands to run (if any)
            4. Any additional context or warnings
            """
            
            # Call Ollama API
            result = await self._query_mistral(prompt)
            
            # Parse the response
            return {
                'success': True,
                'analysis': result,
                'suggested_commands': self._extract_commands(result)
            }
            
        except Exception as e:
            self.error_handler.log_error(e, {'action': 'analyze_issue'})
            return {
                'success': False,
                'error': str(e)
            }
    
    async def _query_mistral(self, prompt: str) -> str:
        """Send a query to the Mistral model"""
        try:
            # Prepare the query
            query = {
                'model': 'mistral:7b',
                'prompt': prompt,
                'stream': False
            }
            
            # Call Ollama API
            cmd = ['ollama', 'generate']
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            # Send the query
            stdout, stderr = await process.communicate(
                input=json.dumps(query).encode()
            )
            
            if process.returncode != 0:
                raise Exception(f"Ollama error: {stderr.decode()}")
            
            # Parse the response
            response = json.loads(stdout.decode())
            return response.get('response', '').strip()
            
        except Exception as e:
            self.error_handler.log_error(e, {'action': 'query_mistral'})
            raise
    
    def _extract_commands(self, text: str) -> List[str]:
        """Extract shell commands from the model's response"""
        # Simple regex to find commands in code blocks
        import re
        commands = re.findall(r'```(?:bash|sh)?\n(.*?)\n```', text, re.DOTALL)
        return [cmd.strip() for cmd in commands if cmd.strip()]
    
    def _register_commands(self):
        """Register command handlers"""
        self.commands = {
            'analyze': self.cmd_analyze,
            'fix': self.cmd_fix,
            'install': self.cmd_install
        }
    
    async def cmd_analyze(self, *args):
        """Analyze an error message or recent logs"""
        error = ' '.join(args) if args else None
        
        if not error and self.system_log:
            # Get recent error logs if no error provided
            logs = self.system_log.get_recent_logs(10)
            error = "\n".join(logs)
        
        if not error:
            print("❌ No error message or logs to analyze")
            return False
        
        print("\n🔍 Analyzing issue...")
        result = await self.analyze_issue(error)
        
        if not result.get('success'):
            print(f"❌ Analysis failed: {result.get('error')}")
            return False
        
        print("\n📝 Analysis:")
        print("-" * 80)
        print(result['analysis'])
        print("-" * 80)
        
        if result.get('suggested_commands'):
            print("\n💡 Suggested commands:")
            for i, cmd in enumerate(result['suggested_commands'], 1):
                print(f"{i}. {cmd}")
        
        return True
    
    async def cmd_fix(self, *args):
        """Attempt to automatically fix an issue"""
        if not self.permissions['execute_commands']:
            print("❌ Missing permission to execute commands")
            return False
        
        error = ' '.join(args) if args else None
        if not error and self.system_log:
            logs = self.system_log.get_recent_logs(10)
            error = "\n".join(logs)
        
        if not error:
            print("❌ No error message or logs to analyze")
            return False
        
        print("\n🔍 Analyzing and attempting to fix issue...")
        result = await self.analyze_issue(error)
        
        if not result.get('success'):
            print(f"❌ Analysis failed: {result.get('error')}")
            return False
        
        print("\n📝 Analysis:")
        print("-" * 80)
        print(result['analysis'])
        print("-" * 80)
        
        if not result.get('suggested_commands'):
            print("\nℹ️ No automated fix available")
            return True
        
        # Execute suggested commands with confirmation
        print("\n💡 Suggested fix commands:")
        for i, cmd in enumerate(result['suggested_commands'], 1):
            print(f"{i}. {cmd}")
            
            while True:
                response = input(f"Run command {i}? (Y/n/skip): ").strip().lower()
                if response in ['y', '']:
                    await self._execute_command(cmd)
                    break
                elif response == 'n':
                    print(f"Skipping command: {cmd}")
                    break
                elif response == 'skip':
                    print("Skipping all remaining commands")
                    return True
                else:
                    print("Please enter 'y', 'n', or 'skip'")
        
        return True
    
    async def cmd_install(self, *args):
        """Install a package or dependency"""
        if not self.permissions['install_packages']:
            print("❌ Missing permission to install packages")
            return False
        
        if not args:
            print("Usage: install <package> [version]")
            return False
        
        package = args[0]
        version = args[1] if len(args) > 1 else None
        
        print(f"\n📦 Installing {package}{' ' + version if version else ''}...")
        
        try:
            # Try system package manager first
            if sys.platform == 'linux':
                cmd = ['sudo', 'apt-get', 'install', '-y', package]
            elif sys.platform == 'darwin':
                cmd = ['brew', 'install', package]
            else:
                cmd = ['pip', 'install', package]
            
            await self._execute_command(' '.join(cmd))
            return True
            
        except Exception as e:
            self.error_handler.log_error(e, {'action': 'install_package', 'package': package})
            print(f"❌ Failed to install {package}: {e}")
            return False
    
    async def _execute_command(self, command: str) -> Tuple[bool, str]:
        """Execute a shell command"""
        if not self.permissions['execute_commands']:
            print("❌ Missing permission to execute commands")
            return False, "Permission denied"
        
        try:
            print(f"$ {command}")
            process = await asyncio.create_subprocess_shell(
                command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            # Stream the output
            while True:
                output = await process.stdout.readline()
                if not output:
                    break
                print(output.decode().strip())
            
            # Get any remaining output
            stdout, stderr = await process.communicate()
            
            if process.returncode != 0:
                error = stderr.decode().strip()
                print(f"❌ Command failed: {error}")
                return False, error
            
            return True, stdout.decode().strip()
            

async def cmd_install(self, *args):
    """Install a package or dependency"""
    if not self.permissions['install_packages']:
        print("❌ Missing permission to install packages")
        return False
    
    if not args:
        print("Usage: install <package> [version]")
        return False
    
    package = args[0]
    version = args[1] if len(args) > 1 else None
    
    print(f"\n📦 Installing {package}{' ' + version if version else ''}...")
    
    try:
        # Try system package manager first
        if sys.platform == 'linux':
            cmd = ['sudo', 'apt-get', 'install', '-y', package]
        elif sys.platform == 'darwin':
            cmd = ['brew', 'install', package]
        else:
            cmd = ['pip', 'install', package]
        
        await self._execute_command(' '.join(cmd))
        return True
        
    except Exception as e:
        self.error_handler.log_error(e, {'action': 'install_package', 'package': package})
        print(f"❌ Failed to install {package}: {e}")
        return False

async def _execute_command(self, command: str) -> Tuple[bool, str]:
    """Execute a shell command"""
    if not self.permissions['execute_commands']:
        print("❌ Missing permission to execute commands")
        return False, "Permission denied"
    
    try:
        print(f"$ {command}")
        process = await asyncio.create_subprocess_shell(
            command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        # Stream the output
        while True:
            output = await process.stdout.readline()
            if not output:
                break
            print(output.decode().strip())
        
        # Get any remaining output
        stdout, stderr = await process.communicate()
        
        if process.returncode != 0:
            error = stderr.decode().strip()
            print(f"❌ Command failed: {error}")
            return False, error
        
        return True, stdout.decode().strip()
        
    except Exception as e:
        self.error_handler.log_error(e, {'command': command})
        print(f"❌ Error executing command: {e}")
        return False, str(e)

def register(event_bus, shell):
    """Register the shell assistant plugin
    
    Args:
        event_bus: The event bus instance
        shell: The shell instance
    """
    assistant = ShellAssistant()
    asyncio.create_task(assistant.initialize())
    print("📦 Shell Assistant plugin loaded")
    return assistant

# Plugin setup function (legacy support)
def setup():
    """Initialize and return the ShellAssistant plugin"""
    return ShellAssistant()
