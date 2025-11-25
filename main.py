#!/usr/bin/env python3
"""
C.O.R.T.E.X. - Centralized Omniscient Real-time Tactical Executive System
Ponto de entrada principal que inicializa todos os módulos e mantém o loop principal.
"""

import asyncio
import logging
import signal
import sys
from pathlib import Path

# Adiciona o diretório raiz ao path
sys.path.insert(0, str(Path(__file__).parent))

from modules.core.brain import Brain
from modules.core.memory import MemoryManager
from modules.core.scheduler import TaskScheduler
from modules.security.vault import VaultManager
from modules.network.monitor import NetworkMonitor
from modules.interface.voice import VoiceInterface
from modules.interface.cli import CLIInterface
from config.settings import Config

# Configuração de logging estruturado
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/cortex.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class Cortex:
    """Classe principal do sistema C.O.R.T.E.X."""
    
    def __init__(self):
        self.config = Config()
        self.vault = VaultManager()
        self.memory = MemoryManager()
        self.scheduler = TaskScheduler()
        self.network_monitor = NetworkMonitor()
        self.brain = Brain()
        self.voice = VoiceInterface()
        self.cli = CLIInterface()
        
        # Flags de controle
        self.running = False
        
    async def initialize(self):
        """Inicializa todos os módulos do sistema."""
        logger.info("🚀 Inicializando C.O.R.T.E.X...")
        
        try:
            # Inicializa segurança primeiro
            await self.vault.initialize()
            
            # Carrega configurações e tokens
            await self.config.load_config()
            
            # Inicializa módulos principais
            await self.memory.initialize()
            await self.network_monitor.start()
            await self.brain.initialize()
            
            # Inicializa interfaces
            if self.config.get('voice_enabled', True):
                await self.voice.initialize()
                
            logger.info("✅ C.O.R.T.E.X. inicializado com sucesso")
            
        except Exception as e:
            logger.error(f"❌ Erro na inicialização: {e}")
            raise
            
    async def shutdown(self):
        """Encerra todos os módulos de forma segura."""
        logger.info("🛑 Encerrando C.O.R.T.E.X...")
        
        self.running = False
        
        # Salva estados
        await self.memory.save_state()
        await self.vault.save()
        
        # Encerra módulos
        await self.network_monitor.stop()
        await self.brain.shutdown()
        await self.voice.shutdown()
        
        logger.info("✅ C.O.R.T.E.X. encerrado com segurança")
        
    async def run(self):
        """Loop principal do sistema."""
        await self.initialize()
        self.running = True
        
        # Registra handlers de sinal
        def signal_handler(signum, frame):
            logger.info(f"Recebido sinal {signum}")
            asyncio.create_task(self.shutdown())
            
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
        # Inicia interfaces
        tasks = [
            self.brain.main_loop(),
            self.network_monitor.monitor_loop(),
            self.scheduler.run(),
        ]
        
        if self.config.get('voice_enabled', True):
            tasks.append(self.voice.listen_loop())
            
        # Interface CLI opcional
        if not self.config.get('headless', False):
            tasks.append(self.cli.run())
            
        # Executa todas as tarefas
        try:
            await asyncio.gather(*tasks)
        except Exception as e:
            logger.error(f"Erro no loop principal: {e}")
        finally:
            await self.shutdown()

if __name__ == "__main__":
    try:
        cortex = Cortex()
        asyncio.run(cortex.run())
    except KeyboardInterrupt:
        logger.info("Interrupção manual detectada")
    except Exception as e:
        logger.error(f"Erro fatal: {e}")
        sys.exit(1)
