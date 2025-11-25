from typing import Any, Dict, Optional
import uuid
import time
from .agente_manager import AgenteManager, WorkerBase, WorkerSimples, WorkerCompleto
from .dataclasses import Task, TaskStatus, TaskPriority, GlobalContext, ExecutionTrace
# Importa o Logger Singleton para uso
from ..utilities.logger import CORTEX_LOGGER 

class CERNE: 
    """
    O Kernel Lógico do C.O.R.T.E.X. (O Núcleo).
    Implementa o Loop de Raciocínio de 4 Fases e a Orquestração de Workers.
    """
    
    def __init__(self, agente_manager: AgenteManager):
        self._manager = agente_manager
        CORTEX_LOGGER.info("CERNE (Kernel Lógico) ativado. Loop de Raciocínio 4-Fases pronto.")

    # --- Funções de Auto-Modulação (Criação Dinâmica) ---
    
    def _create_new_adhoc_agent(self, purpose: str, complexity: str = "Simples") -> str:
        """Cria, registra e retorna o nome de um novo agente ad-hoc."""
        base_name = purpose.replace(' ', '_')
        agent_name = f"Agente_{base_name}_{uuid.uuid4().hex[:4]}" 
        
        # Seleciona a classe base do Worker com base na complexidade
        if complexity.upper() == "COMPLETO":
            AgentClass = WorkerCompleto
        else: # Simples (padrão)
            AgentClass = WorkerSimples

        # Cria uma nova classe temporária
        AdHocAgent = type(agent_name, (AgentClass,), {})
        
        # Registra o novo agente no AgenteManager
        self._manager.register_agent(AdHocAgent)
        
        CORTEX_LOGGER.info(
            f"Novo agente ad-hoc '{agent_name}' ({complexity}) criado e registrado.",
            extra_data={'new_agent': agent_name, 'complexity': complexity}
        )
        return agent_name

    # --- O Loop de Raciocínio (4 Fases) ---

    def processar_tarefa(self, raw_description: str, context: GlobalContext, initial_agent: Optional[str] = None) -> Task:
        """Inicia e executa o Loop de Raciocínio do CERNE para uma nova Tarefa."""
        
        task_id = f"TASK-{uuid.uuid4().hex[:8]}"
        
        # 1. Configura o contexto do Logger para esta Task
        CORTEX_LOGGER.set_task_context(task_id)
        
        task = Task(
            task_id=task_id,
            description=raw_description,
            context=context,
            required_agent=initial_agent or "ANALYSIS_CORE"
        )

        CORTEX_LOGGER.info(f"Iniciando Tarefa: '{raw_description[:30]}...'", extra_data={'task_id': task_id})
        
        # 1. FASE DE ANÁLISE
        task.update_status(
            TaskStatus.ANALYSIS, 
            "CERNE", 
            f"Analisando: '{raw_description[:30]}...'"
        )
        CORTEX_LOGGER.info("Fase de Análise concluída.", extra_data={'status': task.status.value})
        
        required_agent_name = initial_agent
        
        if "estudo avançado" in raw_description.lower() and required_agent_name is None and context.cortex_mode == "SERVER":
            required_agent_name = "Pesquisador_Agente"
        
        # 2. FASE DE DELEGAÇÃO
        task.update_status(
            TaskStatus.DELEGATED, 
            "CERNE", 
            f"Tentando delegar para: {required_agent_name or 'Auto-Modulação'}"
        )
        CORTEX_LOGGER
