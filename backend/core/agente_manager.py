import os
from typing import Dict, Type, Any
from abc import ABC, abstractmethod
from ..utilities.logger import CORTEX_LOGGER
from .protocol import AgentMessage, AgentResponse 
# Importa a lista de plugins do novo diretório
from ...agents import AGENT_PLUGINS 

# --- 1. Classes de Abstração (Manutenção da Interface de Domínio) ---

class WorkerBase(ABC):
    """
    Classe base abstrata (Agente/Worker) para todos os componentes executáveis.
    Garante a interface de comunicação (AgentMessage -> AgentResponse).
    """
    
    def __init__(self, name: str, config: Dict[str, Any] = None):
        self.name = name
        self.config = config or {}
        
    @abstractmethod
    def execute_task(self, message: AgentMessage) -> AgentResponse: 
        """Método principal para execução de tarefas delegadas pelo CERNE."""
        pass
        
    def __repr__(self):
        return f"<Worker:{self.name} (Status: Ready)>"
        
# --- 2. O Manager Principal (Lógica de Plugin) ---

class AgenteManager:
    """
    Gerenciador de Agentes (Workers) do C.O.R.T.E.X.
    Carrega agentes dinamicamente através da lista AGENT_PLUGINS.
    """
    
    def __init__(self, mode: str):
        self._mode = mode
        self._agent_map: Dict[str, Type[WorkerBase]] = {}
        self._load_plugins()
        
    def _load_plugins(self):
        """Carrega a lista de classes de agentes disponíveis com base no modo CORTEX."""
        
        # Iterar sobre a lista de plugins importada
        for AgentClass in AGENT_PLUGINS:
            # Assumimos uma convenção simples para o filtro (nome da classe)
            agent_name = AgentClass.__name__
            is_server_agent = "Engenheiro" in agent_name or "Pesquisador" in agent_name
            is_edge_agent = "Sensor" in agent_name or "Simples" in agent_name
            
            if self._mode == "SERVER" and is_server_agent:
                self._register_agent_class(AgentClass)
            elif self._mode == "EDGE" and is_edge_agent:
                self._register_agent_class(AgentClass)
            # Nota: Um sistema real usaria decorators ou metadados na AgentClass para filtro.

        CORTEX_LOGGER.info(
            f"AgenteManager: Carregados {len(self._agent_map)} plugins para o modo '{self._mode}'.",
            extra_data={'mode': self._mode, 'agents': list(self._agent_map.keys())}
        )

    def _register_agent_class(self, AgentClass: Type[WorkerBase]):
         agent_name = AgentClass.__name__
         self._agent_map[agent_name] = AgentClass
         CORTEX_LOGGER.info(f"Plugin carregado: {agent_name}")


    def register_agent(self, agent_class: Type[WorkerBase]):
        """Registra um novo agente dinamicamente (usado pelo CERNE na Auto-Modulação)."""
        agent_name = agent_class.__name__
        if agent_name in self._agent_map:
            CORTEX_LOGGER.warning(f"Tentativa de registrar agente duplicado: '{agent_name}'.")
            return
            
        self._agent_map[agent_name] = agent_class
        CORTEX_LOGGER.info(
            f"Agente '{agent_name}' registrado dinamicamente via Auto-Modulação.",
            extra_data={'agent_name': agent_name}
        )

    def get_agent(self, agent_name: str, config: Dict[str, Any] = None) -> WorkerBase:
        """Instancia e retorna um agente pelo nome."""
        
        AgentClass = self._agent_map.get(agent_name)
        if not AgentClass:
            CORTEX_LOGGER.error(
                f"Agente '{agent_name}' não encontrado no mapeamento atual.",
                extra_data={'requested_agent': agent_name}
            )
            raise ValueError(f"Agente '{agent_name}' não encontrado.")
