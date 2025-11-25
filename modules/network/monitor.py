"""
NetworkMonitor - Monitoramento contínuo de rede e dispositivos.
Descobre dispositivos, monitora tráfego e detecta anomalias.
"""

import asyncio
import socket
import struct
import subprocess
import threading
from typing import Dict, List, Optional, Tuple
import logging
import json
from datetime import datetime
import psutil
import netifaces
from scapy.all import ARP, Ether, srp, conf
from concurrent.futures import ThreadPoolExecutor

logger = logging.getLogger(__name__)

class NetworkMonitor:
    """Monitoramento de rede e descoberta de dispositivos."""
    
    def __init__(self):
        self.devices = {}
        self.monitoring = False
        self.executor = ThreadPoolExecutor(max_workers=10)
        self.last_scan = None
        
    async def start(self):
        """Inicia o monitoramento de rede."""
        logger.info("Iniciando monitoramento de rede...")
        self.monitoring = True
        
        # Descobre rede inicial
        await self.discover_network()
        
    async def stop(self):
        """Para o monitoramento de rede."""
        logger.info("Parando monitoramento de rede...")
        self.monitoring = False
        
    async def discover_network(self) -> Dict[str, dict]:
        """Descobre todos os dispositivos na rede local."""
        logger.info("Escaneando rede...")
        
        # Obtém informações da rede
        network_info = await self._get_network_info()
        
        # Escaneia hosts
        hosts = await self._scan_hosts(network_info['subnet'])
        
        # Analisa cada host
        for host in hosts:
            device_info = await self._analyze_host(host)
            self.devices[host['ip']] = device_info
            
        self.last_scan = datetime.utcnow()
        
        logger.info(f"Descobertos {len(self.devices)} dispositivos")
        return self.devices
        
    async def _get_network_info(self) -> dict:
        """Obtém informações sobre a rede local."""
        # Obtém gateway padrão
        gateways = netifaces.gateways()
        default_gateway = gateways['default'][netifaces.AF_INET]
        
        # Obtém interface ativa
        interface = default_gateway[1]
        addrs = netifaces.ifaddresses(interface)
        
        # Calcula subnet
        ip = addrs[netifaces.AF_INET][0]['addr']
        netmask = addrs[netifaces.AF_INET][0]['netmask']
        
        # Converte netmask para CIDR
        cidr = sum(bin(int(x)).count('1') for x in netmask.split('.'))
        subnet = f"{ip}/{cidr}"
        
        return {
            'gateway': default_gateway[0],
            'interface': interface,
            'ip': ip,
            'netmask': netmask,
            'subnet': subnet
        }
        
    async def _scan_hosts(self, subnet: str) -> List[dict]:
        """Escaneia hosts na subnet usando ARP."""
        # Usa scapy para ARP scan
        loop = asyncio.get_event_loop()
        
        def scan():
            conf.verb = 0  # Desabilita output verbose
            arp = ARP(pdst=subnet)
            ether = Ether(dst="ff:ff:ff:ff:ff:ff")
            packet = ether/arp
            
            result = srp(packet, timeout=3, verbose=0)[0]
            
            hosts = []
            for sent, received in result:
                hosts.append({
                    'ip': received.psrc,
                    'mac': received.hwsrc,
                    'vendor': self._get_mac_vendor(received.hwsrc)
                })
                
            return hosts
            
        hosts = await loop.run_in_executor(self.executor, scan)
        return hosts
        
    def _get_mac_vendor(self, mac: str) -> str:
        """Obtém o fabricante do MAC address."""
        try:
            # Busca vendor via API ou banco local
            # Implementação simplificada
            oui = mac.upper().replace(':', '')[:6]
            # Em produção, usar banco OUI completo
            return f"Vendor-{oui}"
        except:
            return "Unknown"
            
    async def _analyze_host(self, host: dict) -> dict:
        """Analisa um host específico."""
        analysis = {
            **host,
            "services": [],
            "last_seen": datetime.utcnow().isoformat(),
            "os": await self._detect_os(host['ip']),
            "open_ports": await self._scan_ports(host['ip']),
            "hostname": await self._resolve_hostname(host['ip'])
        }
        
        # Detecta serviços IoT
        iot_info = await self._detect_iot_services(host['ip'], analysis['open_ports'])
        analysis['iot'] = iot_info
        
        return analysis
        
    async def _detect_os(self, ip: str) -> str:
        """Detecta o sistema operacional do host."""
        try:
            # Usa nmap OS detection
            process = await asyncio.create_subprocess_exec(
                'nmap', '-O', '--osscan-limit', ip,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            # Parse simplificado da saída
            output = stdout.decode()
            if "Running: " in output:
                os_line = output.split("Running: ")[1].split("\n")[0]
                return os_line.strip()
                
        except Exception as e:
            logger.debug(f"Erro ao detectar OS para {ip}: {e}")
            
        return "Unknown"
        
    async def _scan_ports(self, ip: str, ports: List[int] = None) -> List[int]:
        """Escaneia portas abertas no host."""
        if ports is None:
            ports = [21, 22, 23, 53, 80, 135, 139, 443, 445, 993, 995, 1883, 5683, 8080]
            
        open_ports = []
        
        async def check_port(port):
            try:
                reader, writer = await asyncio.wait_for(
                    asyncio.open_connection(ip, port),
                    timeout=1
                )
                writer.close()
                await writer.wait_closed()
                open_ports.append(port)
            except:
                pass
                
        tasks = [check_port(port) for port in ports]
        await asyncio.gather(*tasks, return_exceptions=True)
        
        return open_ports
        
    async def _resolve_hostname(self, ip: str) -> str:
        """Resolve hostname para IP."""
        try:
            hostname, _, _ = socket.gethostbyaddr(ip)
            return hostname
        except:
            return ip
            
    async def _detect_iot_services(self, ip: str, open_ports: List[int]) -> dict:
        """Detecta serviços IoT específicos."""
        iot_services = {}
        
        # MQTT
        if 1883 in open_ports:
            iot_services['mqtt'] = {
                'port': 1883,
                'status': 'detected',
                'description': 'MQTT Broker'
            }
            
        # CoAP
        if 5683 in open_ports:
            iot_services['coap'] = {
                'port': 5683,
                'status': 'detected',
                'description': 'CoAP Server'
            }
            
        # Web interface
        if 80 in open_ports or 8080 in open_ports:
            # Tenta identificar dispositivo via web
            port = 80 if 80 in open_ports else 8080
            info = await self._probe_web_interface(ip, port)
            if info:
                iot_services['web'] = info
                
        return iot_services
        
    async def _probe_web_interface(self, ip: str, port: int) -> Optional[dict]:
        """Sonda interface web para identificar dispositivo."""
        try:
            # Implementação simplificada
            # Em produção, usar requests com timeout
            return {
                'port': port,
                'status': 'detected',
                'type': 'web_interface'
            }
        except:
            return None
            
    async def monitor_loop(self):
        """Loop principal de monitoramento."""
        while self.monitoring:
            try:
                # Atualiza descoberta a cada 5 minutos
                await asyncio.sleep(300)
                await self.discover_network()
                
                # Verifica mudanças
                await self._check_changes()
                
            except Exception as e:
                logger.error(f"Erro no loop de monitoramento: {e}")
                await asyncio.sleep(60)
                
    async def _check_changes(self):
        """Verifica mudanças na rede."""
        # Implementa detecção de mudanças
        # Notifica sobre novos dispositivos ou serviços
        pass
        
    def get_device(self, ip: str) -> Optional[dict]:
        """Obtém informações de um dispositivo específico."""
        return self.devices.get(ip)
        
    def get_devices_by_type(self, device_type: str) -> List[dict]:
        """Obtém dispositivos por tipo."""
        filtered = []
        for device in self.devices.values():
            if device.get('iot', {}).get('type') == device_type:
                filtered.append(device)
        return filtered
      
