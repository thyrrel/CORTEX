import os
import time
from typing import Dict, Type, Any, Optional
from abc import ABC, abstractmethod
from ..utilities.logger import CORTEX_LOGGER
# Importa as classes do novo módulo de Protocolo
from .protocol import AgentMessage, AgentResponse 
from ..core.dataclasses import ExecutionTrace # Mantido para referência

# --- 1. Classes de Abstração de Workers (Base e Simulação) ---

class WorkerBase(ABC):
    """Classe base abstrata (Agente/Worker)."""
    
    def __init__(self, name: str, config: Dict[str, Any] = None):
        self.name = name
        self.config = config or {}
        
    @abstractmethod
    # NOVO ASSINATURA: Aceita AgentMessage e retorna AgentResponse
    def execute_task(self, message: AgentMessage) -> AgentResponse: 
        """Método principal para execução de tarefas delegadas pelo CERNE."""
        pass
        
    def __repr__(self):
        return f"<Worker:{self.name} (Status: Ready)>"

# --- Implementações Simuladas Refatoradas para usar o Protocolo ---

class WorkerSimples(WorkerBase):
    """Implementação simples para uso em modo EDGE e Auto-Modulação."""
    def execute_task(self, message: AgentMessage) -> AgentResponse:
        start_time = time.time()
        
        # Simula processamento simples
        output = f"Worker Simples [{self.name}] processou: '{message.raw_prompt[:15]}...' (EDGE)"
        
        return AgentResponse(
            message_id=message.message_id,
            task_id=message.task_id,
            success=True,
            status_code=200,
            output_data=output,
            execution_time_ms=(time.time() - start_time) * 1000,
            suggested_next_action="TASK_COMPLETED_SIMPLE",
            log_message="Processamento básico concluído com sucesso."
        )

class Pesquisador_Agente(WorkerBase):
    """Worker de alta capacidade para tarefas complexas (SERVER)."""
    def execute_task(self, message: AgentMessage) -> AgentResponse:
        start_time = time.time()
        
        # Simula uma análise longa
        time.sleep(0.1) 
        output = f"Pesquisador_Agente [{self.name}] analisou profundamente: '{message.raw_prompt}'"

        return AgentResponse(
            message_id=message.message_id,
            task_id=message.task_id,
            success=True,
            status_code=200,
            output_data=output,
            execution_time_ms=(time.time() - start_time) * 1000,
            suggested_next_action="DELEGATE_TO_REDATOR", # Sugere o próximo Agente
            log_message="Pesquisa de campo concluída. Próxima etapa sugerida: Redação."
        )

class Engenheiro_Agente(WorkerBase):
    """Worker de alta capacidade para manipulação de código e sistemas (SERVER)."""
    def execute_task(self, message: AgentMessage) -> AgentResponse:
        start_time = time.time()
        
        if "falha de segurança" in message.raw_prompt.lower():
            output = {"fix_applied": True, "details": "Patch de emergência implementado."}
            log_msg = "Mitigação de falha CRÍTICA concluída."
        else:
            output = f"Engenheiro_Agente [{self.name}] projetou: '{message.raw_prompt}'"
            log_msg = "Desenvolvimento de projeto finalizado."
            
        return AgentResponse(
            message_id=message.message_id,
            task_id=message.task_id,
            success=True,
            status_code=200,
            output_data=output,
            execution_time_ms=(time.time() - start_time) * 1000,
            suggested_next_action="TASK_COMPLETED",
            log_message=log_msg
        )

class Sensor_Agente(WorkerBase):
    """Worker de baixa capacidade para coleta de dados (EDGE)."""
    def execute_task(self, message: AgentMessage) -> AgentResponse:
        start_time = time.time()

        output = f"Sensor_Agente [{self.name}] reportou dados de telemetria: '{message.raw_prompt[:20]}...' (EDGE/Simples)"
        
        return AgentResponse(
            message_id=message.message_id,
            task_id=message.task_id,
            success=True,
            status_code=200,
            output_data=output,
            execution_time_ms=(time.time() - start_time) * 1000,
            suggested_next_action="SEND_TO_SERVER_FOR_ANALYSIS",
            log_message="Coleta de dados concluída."
        )
        
# --- 2. O Manager Principal (Inalterado, pois só gerencia o mapeamento de classes) ---

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
            "EDGE": [Sensor_Agente, WorkerSimples] 
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
            extra_data={'agent_name': agent_name}
        )

    def get_agent(self, agent_name: str, config: Dict[str, Any] = None) -> WorkerBase:
        """Instancia e retorna um agente pelo nome."""
        
        AgentClass = self._agent_map.get(agent_name)
        if not AgentClass:
            CORTEX_LOGGER.error(
                f"Falha na recuperação. Agente '{agent_name}' não encontrado neste modo.",
                extra_data={'requested_agent': agent_name, 'available': list(self._agent_map.keys())}
            )
            raise ValueError(
                f"Agente '{agent_name}' não encontrado. Verifique a nomenclatura *_Agente."
            )
            
        CORTEX_LOGGER.info(f"Agente '{agent_name}' instanciado com sucesso.")
        return AgentClass(name=agent_name, config=config)

    def list_agents(self) -> Dict[str, Type[WorkerBase]]:
        """Retorna o dicionário de agentes mapeados."""
        return self._agent_map
