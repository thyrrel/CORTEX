"""
CLIInterface - Interface de linha de comando interativa para C.O.R.T.E.X.
"""

import asyncio
import cmd
import logging
import json
from typing import Dict, Any
from pathlib import Path
import sys
import threading

logger = logging.getLogger(__name__)

class CLIInterface(cmd.Cmd):
    """Interface de linha de comando interativa."""
    
    prompt = "CORTEX> "
    intro = """
    ╔═══════════════════════════════════════════════════════╗
    ║         C.O.R.T.E.X. Command Interface                ║
    ║  Digite 'help' para ver comandos disponíveis         ║
    ╚═══════════════════════════════════════════════════════╝
    """
    
    def __init__(self):
        super().__init__()
        self.running = False
        self.brain = None
        
    async def run(self):
        """Inicia a interface CLI."""
        self.running = True
        
        # Inicia thread para input não-bloqueante
        loop = asyncio.get_event_loop()
        
        await loop.run_in_executor(None, self.cmdloop)
        
    def do_scan(self, arg):
        """Escaneia a rede: scan [network|devices|ports]"""
        asyncio.create_task(self._handle_scan(arg))
        
    def do_status(self, arg):
        """Mostra status do sistema: status [all|network|security|devices]"""
        asyncio.create_task(self._handle_status(arg))
        
    def do_token(self, arg):
        """Gerencia tokens: token [list|set|get|remove] service key [value]"""
        asyncio.create_task(self._handle_token(arg))
        
    def do_device(self, arg):
        """Controla dispositivos: device [list|control|info] device_id [action]"""
        asyncio.create_task(self._handle_device(arg))
        
    def do_config(self, arg):
        """Gerencia configurações: config [get|set|reload] key [value]"""
        asyncio.create_task(self._handle_config(arg))
        
    def do_backup(self, arg):
        """Faz backup do sistema: backup [config|vault|all]"""
        asyncio.create_task(self._handle_backup(arg))
        
    def do_restore(self, arg):
        """Restaura backup: restore [config|vault|all] path"""
        asyncio.create_task(self._handle_restore(arg))
        
    def do_exit(self, arg):
        """Sai do sistema"""
        print("Encerrando C.O.R.T.E.X...")
        asyncio.create_task(self._shutdown())
        return True
        
    def do_quit(self, arg):
        """Alias para exit"""
        return self.do_exit(arg)
        
    def do_EOF(self, arg):
        """Handle Ctrl+D"""
        print()
        return self.do_exit(arg)
        
    async def _handle_scan(self, arg):
        """Processa comando scan."""
        from modules.network.monitor import NetworkMonitor
        monitor = NetworkMonitor()
        
        if not arg or arg == "network":
            devices = await monitor.discover_network()
            
            print("\n📡 Dispositivos encontrados:")
            print("-" * 80)
            for ip, device in devices.items():
                print(f"IP: {ip:15} MAC: {device['mac']} "
                      f"Vendor: {device['vendor']}")
                if device.get('hostname') != ip:
                    print(f"    Hostname: {device['hostname']}")
                print(f"    Ports: {', '.join(map(str, device['open_ports']))}")
                if device.get('iot'):
                    print(f"    IoT Services: {list(device['iot'].keys())}")
                print()
                
    async def _handle_status(self, arg):
        """Processa comando status."""
        from modules.core.brain import Brain
        brain = Brain()
        
        status = await brain._get_status({}, {})
        
        print("\n📊 Status do Sistema:")
        print("-" * 40)
        for key, value in status['data'].items():
            print(f"{key}: {value}")
            
    async def _handle_token(self, arg):
        """Processa comando token."""
        args = arg.split()
        if len(args) < 2:
            print("Uso: token [list|set|get|remove] service [key] [value]")
            return
            
        action = args[0]
        
        from modules.security.vault import VaultManager
        vault = VaultManager()
        await vault.initialize()
        
        if action == "list":
            services = vault.list_services()
            print("\n🔑 Serviços configurados:")
            for service in services:
                tokens = vault.list_tokens(service)
                print(f"  {service}: {', '.join(tokens)}")
                
        elif action == "get" and len(args) >= 3:
            service, key = args[1], args[2]
            token = vault.get_token(service, key)
            if token:
                print(f"{service}.{key}: {token}")
            else:
                print("Token não encontrado")
                
        elif action == "set" and len(args) >= 4:
            service, key, value = args[1], args[2], args[3]
            vault.set_token(service, key, value)
            await vault.save()
            print("✅ Token configurado")
            
        elif action == "remove" and len(args) >= 3:
            service, key = args[1], args[2]
            vault.remove_token(service, key)
            await vault.save()
            print("✅ Token removido")
            
    async def _handle_device(self, arg):
        """Processa comando device."""
        args = arg.split()
        if len(args) < 1:
            print("Uso: device [list|info|control] device_id [action]")
            return
            
        action = args[0]
        
        if action == "list":
            from modules.network.monitor import NetworkMonitor
            monitor = NetworkMonitor()
            
            devices = await monitor.discover_network()
            
            print("\n📱 Dispositivos disponíveis:")
            for ip, device in devices.items():
                print(f"{ip}: {device.get('hostname', 'Unknown')}")
                
    async def _shutdown(self):
        """Encerra o sistema."""
        import sys
        sys.exit(0)
      
