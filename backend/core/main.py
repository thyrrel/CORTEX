import os
import uuid
import time
from typing import Any, Optional
# Importações do Core
from .cerne import CERNE 
from .agente_manager import AgenteManager 
from .dataclasses import GlobalContext, TaskStatus, TaskPriority
from .scheduler import CERNEScheduler 
# Importação da Política de Retry para o teste inicial
from .retry_policy import RetryPolicy 
# Importações de Camadas Externas
from ..persistence.task_repository import TaskRepository 
from ..utilities.logger import CORTEX_LOGGER 

class CORTEX:
    """
    A Fachada Singleton e o Ponto de Entrada do Sistema C.O.R.T.E.X.
    Orquestra a inicialização de todas as camadas e gerencia o ciclo de vida.
    """
    _instance = None
    
    def __new__(cls, *args, **kwargs):
        """Implementa o padrão Singleton."""
        if cls._instance is None:
            cls._instance = super(CORTEX, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
            
        # --- Configuração Inicial ---
        self.mode = os.environ.get("CORTEX_MODE", "SERVER").upper()
        if self.mode not in ["EDGE", "SERVER"]:
             CORTEX_LOGGER.critical(f"Modo CORTEX_MODE inválido: {self.mode}. Encerrando.")
             raise ValueError("Variável de ambiente CORTEX_MODE deve ser 'EDGE' ou 'SERVER'.")
        
        CORTEX_LOGGER.info(f"CORTEX Inicializando em modo: **{self.mode}**", extra_data={'mode': self.mode})
        
        # --- Inicialização das Camadas ---
        
        # 1. Agente Manager (Gerencia Workers)
        self.agente_manager = AgenteManager(mode=self.mode)
        
        # 2. CERNE (Lógica de Domínio)
        self.coordenador: CERNE = CERNE(agente_manager=self.agente_manager)
        
        # 3. Task Repository (Persistência)
        self.task_repository = TaskRepository() 
        
        # 4. CERNEScheduler (Execução Assíncrona, Injeção de CERNE e Repositório)
        # O GlobalContext é criado no start_system, mas aqui a instância é criada.
        self.scheduler: CERNEScheduler = CERNEScheduler(
            cerne_instance=self.coordenador, 
            task_repository=self.task_repository
        ) 
        
        self._initialized = True
        CORTEX_LOGGER.info("CORTEX Inicialização concluída. Sistema pronto.")
        
    def _create_context(self, prompt: str) -> GlobalContext:
        """Cria um GlobalContext para a tarefa atual."""
        return GlobalContext(
            session_id=str(uuid.uuid4()),
            cortex_mode=self.mode,
            initial_prompt=prompt,
            environment_vars=dict(os.environ)
        )

    def start_system(self):
        """Inicia o Scheduler e submete tarefas para teste."""
        CORTEX_LOGGER.info("Iniciando Thread do Scheduler para processamento assíncrono.")
        
        # INICIA A THREAD DO SCHEDULER
        self.scheduler.start()
        
        # --- Teste 1: Tarefa Crítica (Simula a necessidade de RETRY) ---
        task_prompt_1 = "Monitorar e reportar falha de segurança CRÍTICA no módulo XY (Teste de Backoff)."
        context_1 = self._create_context(task_prompt_1)

        # O Engenheiro_Agente está propenso a falhas de rede simuladas
        initial_agent_1 = "Engenheiro_Agente" if self.mode == "SERVER" else "Sensor_Agente"
            
        CORTEX_LOGGER.info(f"[TESTE 1] Submetendo tarefa de **Prioridade Crítica** ({initial_agent_1}).")
        task_1 = self.scheduler.submit_task(
            task_prompt_1, 
            context_1, 
            priority=TaskPriority.CRITICAL, 
            initial_agent=initial_agent_1
        )
        
        # --- Teste 2: Tarefa Normal (Simula Auto-Modulação) ---
        task_prompt_2 = "Compilar relatório semanal de desempenho (Baixa Prioridade)."
        context_2 = self._create_context(task_prompt_2)
        
        CORTEX_LOGGER.info("[TESTE 2] Submetendo tarefa de **Baixa Prioridade** (Força Auto-Modulação).")
        task_2 = self.scheduler.submit_task(
            task_prompt_2, 
            context_2, 
            priority=TaskPriority.LOW, 
            initial_agent=None
        )

        # Permite que o Scheduler processe as tarefas
        # (O teste 1 deve entrar em WAITING_BACKOFF)
        time.sleep(RetryPolicy.get_wait_time(1) + 2) # Espera o primeiro backoff + margem
        
        # Simula o enc
