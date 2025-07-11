"""
System Information Plugin
Extended system monitoring capabilities
"""

def register(event_bus, shell):
    """Register system info plugin"""
    
    def handle_disk_command(event):
        """Show disk usage"""
        try:
            import psutil
            partitions = psutil.disk_partitions()
            
            result = "💿 Disk Usage:\n"
            for partition in partitions:
                try:
                    usage = psutil.disk_usage(partition.mountpoint)
                    result += f"  {partition.device} ({partition.mountpoint}): "
                    result += f"{usage.percent:.1f}% used "
                    result += f"({usage.used // 1024**3}GB / {usage.total // 1024**3}GB)\n"
                except PermissionError:
                    result += f"  {partition.device}: Permission denied\n"
            
            return result
        except Exception as e:
            return f"❌ Error getting disk info: {e}"
    
    def handle_network_command(event):
        """Show network information"""
        try:
            import psutil
            
            # Network interfaces
            interfaces = psutil.net_if_addrs()
            stats = psutil.net_io_counters(pernic=True)
            
            result = "🌐 Network Interfaces:\n"
            for interface, addresses in interfaces.items():
                if interface.startswith('lo'):  # Skip loopback
                    continue
                
                result += f"  {interface}:\n"
                for addr in addresses:
                    if addr.family.name == 'AF_INET':
                        result += f"    IP: {addr.address}\n"
                
                if interface in stats:
                    stat = stats[interface]
                    result += f"    RX: {stat.bytes_recv // 1024**2}MB, TX: {stat.bytes_sent // 1024**2}MB\n"
            
            return result
        except Exception as e:
            return f"❌ Error getting network info: {e}"
    
    def handle_processes_command(event):
        """Show top processes"""
        try:
            import psutil
            
            # Get top 10 processes by CPU usage
            processes = []
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
                try:
                    proc_info = proc.info
                    if proc_info['cpu_percent'] > 0:
                        processes.append(proc_info)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
            
            # Sort by CPU usage
            processes.sort(key=lambda x: x['cpu_percent'], reverse=True)
            
            result = "🔄 Top Processes (by CPU):\n"
            result += "PID     NAME                CPU%    MEM%\n"
            for proc in processes[:10]:
                result += f"{proc['pid']:<8} {proc['name']:<15} {proc['cpu_percent']:<8.1f} {proc['memory_percent']:<8.1f}\n"
            
            return result
        except Exception as e:
            return f"❌ Error getting process info: {e}"
    
    # Register commands
    shell.register_command('disk', handle_disk_command)
    shell.register_command('network', handle_network_command)
    shell.register_command('processes', handle_processes_command)
    shell.register_command('top', handle_processes_command)  # Alias
    
    print("📦 System info plugin loaded: disk, network, processes, top")

def unregister(event_bus, shell):
    """Unregister plugin"""
    shell.unregister_command('disk')
    shell.unregister_command('network')
    shell.unregister_command('processes')
    shell.unregister_command('top')
    print("📦 System info plugin unloaded")
