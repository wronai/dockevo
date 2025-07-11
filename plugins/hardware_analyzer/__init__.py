"""
Hardware Analyzer Plugin for dockevOS
Detects and fixes hardware compatibility issues
"""

import platform
import subprocess
import sys
import shutil
from typing import Dict, List, Optional, Tuple
from pathlib import Path

from ..error_handler import get_error_handler

class HardwareAnalyzer:
    def __init__(self):
        self.error_handler = get_error_handler()
        self.system_info = self._get_system_info()
        self.required_packages = self._get_required_packages()
        self._register_error_handlers()
        
    def _get_system_info(self) -> Dict[str, str]:
        """Gather system information"""
        return {
            'system': platform.system(),
            'release': platform.release(),
            'version': platform.version(),
            'machine': platform.machine(),
            'processor': platform.processor(),
            'python_version': platform.python_version()
        }
    
    def _get_required_packages(self) -> Dict[str, Dict]:
        """Define required packages per system"""
        return {
            'Linux': {
                'pyaudio': {'pip': 'pyaudio', 'system': 'python3-pyaudio'},
                'portaudio': {'system': 'portaudio19-dev'},
                'docker': {'system': 'docker.io'},
            },
            'Darwin': {
                'pyaudio': {'pip': 'pyaudio'},
                'portaudio': {'brew': 'portaudio'},
                'docker': {'brew': 'docker'},
            },
            'Windows': {
                'pyaudio': {'pip': 'pyaudio'},
                'docker': {'choco': 'docker-desktop'},
            }
        }
    
    def _register_error_handlers(self):
        """Register error handlers"""
        self.error_handler.register_handler('missing_dependency', self.handle_missing_dependency)
        self.error_handler.register_handler('hardware_error', self.handle_hardware_error)
    
    def handle_missing_dependency(self, data: Dict):
        """Handle missing dependency errors"""
        dependency = data.get('dependency')
        if not dependency:
            return
            
        print(f"🔍 Detected missing dependency: {dependency}")
        self.install_dependency(dependency)
    
    def handle_hardware_error(self, data: Dict):
        """Handle hardware-related errors"""
        error_msg = data.get('message', 'Unknown hardware error')
        print(f"⚠️  Hardware issue detected: {error_msg}")
        self.analyze_issue(error_msg)
    
    def check_dependency(self, name: str) -> bool:
        """Check if a dependency is installed"""
        if name == 'pyaudio':
            try:
                import pyaudio
                return True
            except ImportError:
                return False
        return shutil.which(name) is not None
    
    def install_dependency(self, name: str) -> bool:
        """Install a system or Python dependency"""
        print(f"🔧 Attempting to install {name}...")
        
        # Get package info for current system
        pkg_info = self.required_packages.get(self.system_info['system'], {}).get(name, {})
        
        # Try different installation methods
        if 'pip' in pkg_info and self._install_pip_package(pkg_info['pip']):
            return True
            
        if 'system' in pkg_info and self._install_system_package(pkg_info['system']):
            return True
            
        if 'brew' in pkg_info and self._install_brew_package(pkg_info['brew']):
            return True
            
        if 'choco' in pkg_info and self._install_choco_package(pkg_info['choco']):
            return True
            
        print(f"❌ Failed to install {name}")
        return False
    
    def _install_pip_package(self, package: str) -> bool:
        """Install a Python package using pip"""
        try:
            print(f"📦 Installing {package} via pip...")
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', package])
            return True
        except subprocess.CalledProcessError:
            return False
    
    def _install_system_package(self, package: str) -> bool:
        """Install a system package using the system package manager"""
        if self.system_info['system'] != 'Linux':
            return False
            
        try:
            print(f"📦 Installing {package} via apt...")
            subprocess.check_call(['sudo', 'apt-get', 'update'])
            subprocess.check_call(['sudo', 'apt-get', 'install', '-y', package])
            return True
        except subprocess.CalledProcessError:
            return False
    
    def _install_brew_package(self, package: str) -> bool:
        """Install a package using Homebrew (macOS)"""
        if self.system_info['system'] != 'Darwin':
            return False
            
        try:
            print(f"🍺 Installing {package} via Homebrew...")
            subprocess.check_call(['brew', 'install', package])
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False
    
    def _install_choco_package(self, package: str) -> bool:
        """Install a package using Chocolatey (Windows)"""
        if self.system_info['system'] != 'Windows':
            return False
            
        try:
            print(f"🍫 Installing {package} via Chocolatey...")
            subprocess.check_call(['choco', 'install', '-y', package])
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False
    
    def analyze_issue(self, error_message: str):
        """Analyze a hardware-related issue and suggest fixes"""
        print("\n🛠️  Analyzing system configuration...")
        
        # Common issues and their solutions
        common_issues = {
            'audio': ['pyaudio', 'portaudio'],
            'microphone': ['pyaudio', 'portaudio'],
            'docker': ['docker'],
            'port': ['docker'],
            'device': ['udev']
        }
        
        # Check for common issues
        for issue, deps in common_issues.items():
            if issue.lower() in error_message.lower():
                print(f"\n🔧 Detected potential {issue} issue. Checking dependencies...")
                for dep in deps:
                    if not self.check_dependency(dep):
                        self.install_dependency(dep)

# Create a singleton instance
hardware_analyzer = HardwareAnalyzer()

def register(event_bus, shell):
    """Register the hardware analyzer plugin
    
    Args:
        event_bus: The event bus instance
        shell: The shell instance
    """
    # The hardware analyzer is a core service that doesn't need to register commands
    # as it's already available through the shell
    print("📦 Hardware Analyzer loaded")
    return hardware_analyzer

def get_hardware_analyzer():
    """Get the global hardware analyzer instance"""
    return hardware_analyzer
