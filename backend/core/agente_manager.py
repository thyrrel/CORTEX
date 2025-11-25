import os
from typing import Dict, Type, Any, Optional
from abc import ABC, abstractmethod
from ..utilities.logger import CORTEX_LOGGER # Importa o Logger
from ..core.dataclasses import ExecutionTrace # Necessário para tipos de Workers

# --- 1. Classes de Abstração de Workers (Base e Simulação - Inalteradas) ---

class WorkerBase(ABC):
    """Classe base abstrata (Agente/Worker)."""
    
    def __init__(self, name: str, config: Dict[str, Any] = None):
        self.name = name
        self.config = config or {}
        
    @abstractmethod
    def execute_task(self, task_data: Any) -> Any:
        """Método principal para execução de tarefas."""
        pass
        
    def __repr__(self):
        return f"<Worker:{self.name} (Status: Ready)>"

class WorkerSimples(WorkerBase):
    """Implementação simples para uso em modo EDGE e Auto-Modulação."""
    def execute_task(self, task_data: str) -> str:
        # Nota: O Worker pode usar o logger, mas aqui ele retorna a string processada.
        return f"Worker Simples [{self.name}] processou: '{task_data[:15]}...' (EDGE)"

class Pesquisador_Agente(WorkerBase):
    """Worker de alta capacidade para tarefas complexas (SERVER)."""
    def execute_task(self, task_data: str) -> str:
        return f"Pesquisador_Agente [{self.name}] analisou: '{task_data}' (SERVER/Complexo)"

class Engenheiro_Agente(WorkerBase):
    """Worker de alta capacidade para manipulação de código e sistemas (SERVER)."""
    def execute_task(self, task_data: str) -> str:
        return f"Engenheiro_Agente [{self.name}] projetou: '{task_data}' (SERVER/Técnico)"

class Sensor_Agente(WorkerBase):
    """Worker de baixa capacidade para coleta de dados (EDGE)."""
    def execute_task(self, task_data: str) -> str:
        return f"Sensor_Agente [{self.name}] reportou: '{task_data[:20]}...' (EDGE/Simples)"
        
# --- 2. O Manager Principal ---

class AgenteManager:
    """
    Gerenciador de Agentes (Workers) do C.O.R.T.E.X.
    Responsável pelo mapeamento, carregamento condicional e instanciação de Workers.
    """
    
    def __init__(self, mode: str):
        self._mode = mode
        self._agent_map: Dict[str, Type[WorkerBase]] = {}
        self._load_agents_by_mode()
        
    def _load_agents_by_mode(self):
        """Carrega a lista de classes de agentes disponíveis com base no modo CORTEX."""
        
        agent_definitions = {
            "SERVER": [Pesquisador_Agente, Engenheiro_Agente],
            "EDGE": [Sensor_Agente, WorkerSimples] # WorkerSimples útil para EDGE
        }
        
        agents_to_load = agent_definitions.get(self._mode, [])
        
        for AgentClass in agents_to_load:
            agent_name = AgentClass.__name__
            self._agent_map[agent_name] = AgentClass
            
        CORTEX_LOGGER.info(
            f"AgenteManager: Mapeados {len(self._agent_map)} agentes para o modo '{self._mode}'.",
            extra_data={'mode': self._mode, 'agents': list(self._agent_map.keys())}
        )

    def register_agent(self, agent_class: Type[WorkerBase]):
        """Registra um novo agente dinamicamente (usado pelo CERNE na Auto-Modulação)."""
        agent_name = agent_class.__name__
        if agent_name in self._agent_map:
            CORTEX_LOGGER.warning(f"Tentativa de registrar agente duplicado: '{agent_name}'.")
            return
            
        self._agent_map[agent_name] = agent_class
        CORTEX_LOGGER.info(
            f"Agente '{agent_name}' registrado dinamicamente.",
