"""
Docker Manager Plugin for dockevOS
Manages Docker containers, images, and services
"""

import docker
import json
from typing import Dict, List, Optional, Any
from pathlib import Path

from ..error_handler import get_error_handler

class DockerManager:
    def __init__(self):
        self.error_handler = get_error_handler()
        self.client = self._init_docker_client()
        self._register_commands()
    
    def _init_docker_client(self):
        """Initialize Docker client with error handling"""
        try:
            return docker.from_env()
        except Exception as e:
            self.error_handler.log_error(e, {'context': 'Docker client initialization'})
            print("❌ Docker is not running or not installed")
            return None
    
    def _register_commands(self):
        """Register Docker management commands"""
        self.commands = {
            'ps': self.list_containers,
            'images': self.list_images,
            'start': self.start_container,
            'stop': self.stop_container,
            'restart': self.restart_container,
            'logs': self.get_logs,
            'stats': self.get_stats,
            'compose': self.docker_compose,
            'install': self.install_service
        }
    
    async def handle_command(self, command: str, args: List[str]) -> bool:
        """Handle Docker commands"""
        if not self.client:
            print("❌ Docker is not available")
            return False
            
        cmd = command.lower()
        if cmd not in self.commands:
            return False
            
        try:
            return await self.commands[cmd](*args)
        except Exception as e:
            self.error_handler.log_error(e, {'command': command, 'args': args})
            print(f"❌ Error executing {command}: {str(e)}")
            return False
    
    # Docker command implementations
    async def list_containers(self, all_containers: bool = False) -> bool:
        """List all containers"""
        try:
            containers = self.client.containers.list(all=all_containers)
            if not containers:
                print("No running containers")
                return True
                
            print("\n🐳 Running Containers:")
            print("-" * 80)
            for container in containers:
                print(f"📦 {container.name} ({container.short_id})")
                print(f"   Status: {container.status}")
                print(f"   Image: {container.image.tags[0] if container.image.tags else 'N/A'}")
                print(f"   Ports: {container.ports or 'None'}")
                print("-" * 80)
            return True
        except Exception as e:
            self.error_handler.log_error(e, {'action': 'list_containers'})
            return False
    
    async def start_container(self, container_name: str) -> bool:
        """Start a container"""
        try:
            container = self.client.containers.get(container_name)
            container.start()
            print(f"✅ Started container: {container_name}")
            return True
        except Exception as e:
            self.error_handler.log_error(e, {'action': 'start_container', 'container': container_name})
            return False
    
    async def stop_container(self, container_name: str) -> bool:
        """Stop a container"""
        try:
            container = self.client.containers.get(container_name)
            container.stop()
            print(f"⏹️  Stopped container: {container_name}")
            return True
        except Exception as e:
            self.error_handler.log_error(e, {'action': 'stop_container', 'container': container_name})
            return False
    
    async def restart_container(self, container_name: str) -> bool:
        """Restart a container"""
        try:
            container = self.client.containers.get(container_name)
            container.restart()
            print(f"🔄 Restarted container: {container_name}")
            return True
        except Exception as e:
            self.error_handler.log_error(e, {'action': 'restart_container', 'container': container_name})
            return False
    
    async def get_logs(self, container_name: str, tail: int = 100) -> bool:
        """Get container logs"""
        try:
            container = self.client.containers.get(container_name)
            logs = container.logs(tail=tail).decode('utf-8')
            print(f"\n📜 Logs for {container_name}:")
            print("-" * 80)
            print(logs)
            print("-" * 80)
            return True
        except Exception as e:
            self.error_handler.log_error(e, {'action': 'get_logs', 'container': container_name})
            return False
    
    async def get_stats(self, container_name: str) -> bool:
        """Get container statistics"""
        try:
            container = self.client.containers.get(container_name)
            stats = container.stats(stream=False)
            
            # Parse and format stats
            cpu_percent = self._calculate_cpu_percent(stats)
            memory_usage = int(stats['memory_stats']['usage']) / (1024 * 1024)  # MB
            memory_limit = int(stats['memory_stats']['limit']) / (1024 * 1024)  # MB
            
            print(f"\n📊 Stats for {container_name}:")
            print("-" * 80)
            print(f"CPU: {cpu_percent:.2f}%")
            print(f"Memory: {memory_usage:.2f}MB / {memory_limit:.2f}MB ({(memory_usage/memory_limit)*100:.1f}%)")
            print("-" * 80)
            return True
        except Exception as e:
            self.error_handler.log_error(e, {'action': 'get_stats', 'container': container_name})
            return False
    
    async def docker_compose(self, action: str, file_path: str = 'docker-compose.yml') -> bool:
        """Run docker-compose commands"""
        try:
            if action == 'up':
                print(f"🚀 Starting services from {file_path}...")
                self.client.containers.run(
                    'docker/compose:latest',
                    f'up -d',
                    volumes={
                        '/var/run/docker.sock': {'bind': '/var/run/docker.sock', 'mode': 'rw'},
                        str(Path(file_path).parent.absolute()): {'bind': '/app', 'mode': 'rw'}
                    },
                    working_dir='/app',
                    remove=True,
                    detach=True
                )
                print("✅ Services started successfully")
                return True
            
            elif action == 'down':
                print(f"🛑 Stopping services from {file_path}...")
                self.client.containers.run(
                    'docker/compose:latest',
                    'down',
                    volumes={
                        '/var/run/docker.sock': {'bind': '/var/run/docker.sock', 'mode': 'rw'},
                        str(Path(file_path).parent.absolute()): {'bind': '/app', 'mode': 'rw'}
                    },
                    working_dir='/app',
                    remove=True
                )
                print("✅ Services stopped successfully")
                return True
            
            else:
                print("❌ Unknown compose action. Use 'up' or 'down'")
                return False
                
        except Exception as e:
            self.error_handler.log_error(e, {'action': 'docker_compose', 'subaction': action, 'file': file_path})
            return False
    
    async def install_service(self, service_name: str, config: Optional[Dict] = None) -> bool:
        """Install a predefined service"""
        services = {
            'nginx': {
                'image': 'nginx:alpine',
                'ports': {'80/tcp': 8080},
                'volumes': {'./nginx.conf': {'bind': '/etc/nginx/nginx.conf', 'mode': 'ro'}},
                'detach': True
            },
            'postgres': {
                'image': 'postgres:13',
                'environment': {'POSTGRES_PASSWORD': 'example'},
                'ports': {'5432/tcp': 5432},
                'volumes': {'pgdata': {'bind': '/var/lib/postgresql/data', 'mode': 'rw'}},
                'detach': True
            },
            'redis': {
                'image': 'redis:alpine',
                'ports': {'6379/tcp': 6379},
                'detach': True
            }
        }
        
        if service_name not in services:
            print(f"❌ Unknown service: {service_name}")
            print("Available services:" + "\n- " + "\n- ".join(services.keys()))
            return False
            
        try:
            print(f"🚀 Installing {service_name}...")
            config = config or services[service_name]
            self.client.containers.run(**config)
            print(f"✅ Successfully installed {service_name}")
            return True
        except Exception as e:
            self.error_handler.log_error(e, {'action': 'install_service', 'service': service_name})
            return False
    
    def _calculate_cpu_percent(self, stats: Dict) -> float:
        """Calculate CPU percentage from Docker stats"""
        cpu_delta = stats['cpu_stats']['cpu_usage']['total_usage'] - stats['precpu_stats']['cpu_usage']['total_usage']
        system_delta = stats['cpu_stats']['system_cpu_usage'] - stats['precpu_stats']['system_cpu_usage']
        
        if system_delta > 0.0 and cpu_delta > 0.0:
            return (cpu_delta / system_delta) * len(stats['cpu_stats']['cpu_usage']['percpu_usage']) * 100.0
        return 0.0

# Create a singleton instance
docker_manager = DockerManager()

def get_docker_manager() -> DockerManager:
    """Get the global Docker manager instance"""
    return docker_manager
