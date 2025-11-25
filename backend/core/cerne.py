from typing import Any, Dict, Optional
import uuid
import time
from .agente_manager import AgenteManager, WorkerBase, WorkerSimples, WorkerCompleto
from .dataclasses import Task, TaskStatus, TaskPriority, GlobalContext, ExecutionTrace
# Importa as classes do protocolo
from .protocol import AgentMessage, AgentResponse 
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
        
        if complexity.upper() == "COMPLETO":
            AgentClass = WorkerCompleto
        else:
            AgentClass = WorkerSimples

        AdHocAgent = type(agent_name, (AgentClass,), {})
        self._manager.register_agent(AdHocAgent)
        
        CORTEX_LOGGER.info(
            f"Novo agente ad-hoc '{agent_name}' ({complexity}) criado e registrado.",
            extra_data={'new_agent': agent_name, 'complexity': complexity}
        )
        return agent_name

    # --- O Loop de Raciocínio (4 Fases) ---

    def processar_tarefa(self, raw_description: str, context: GlobalContext, initial_agent: Optional[str] = None) -> Task:
        """Inicia e executa o Loop de Raciocínio do CERNE para uma nova Tarefa."""
        
        # 1. Configura a Task e o Logger
        task_id = f"TASK-{uuid.uuid4().hex[:8]}"
        CORTEX_LOGGER.set_task_context(task_id)
        
        task = Task(
            task_id=task_id,
            description=raw_description,
            context=context,
            # Mantemos 'required_agent' no dataclass para o histórico
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
        CORTEX_LOGGER.info(f"Tentativa de Delegação para {required_agent_name}.", extra_data={'delegation': required_agent_name})
        
        worker = None
        if required_agent_name:
            try:
                worker = self._manager.get_agent(required_agent_name)
            except ValueError:
                CORTEX_LOGGER.warning(f"Agente '{required_agent_name}' não encontrado. Necessária Revisão.")
                worker = None 

        # 3. FASE DE REVISÃO (e Criação Dinâmica)
        if worker is None:
            task.update_status(
                TaskStatus.ANALYSIS, 
                "CERNE", 
                "Agente indisponível. Acionando Auto-Modulação."
            )
            
            # Lógica de Auto-Modulação
            new_agent_name = self._create_new_adhoc_agent(
                purpose="Revisor_AdHoc", 
                complexity="Simples" if context.cortex_mode == "EDGE" else "COMPLETO"
            )
            worker = self._manager.get_agent(new_agent_name)
            required_agent_name = new_agent_name
            
        task.delegated_to = required_agent_name
        
        # 4. FASE DE EXECUÇÃO
        task.update_status(
            TaskStatus.IN_PROGRESS, 
            "CERNE", 
            f"Preparando mensagem para {required_agent_name}"
        )
        
        # --- NOVO: CONSTRUÇÃO DO AgentMessage ---
        execution_message = AgentMessage(
            task_id=task.task_id,
            action_type="EXECUTE_TASK",
            raw_prompt=raw_description,
            parameters={'mode': context.cortex_mode} # Exemplo de parâmetro
        )
        # --- FIM DO NOVO ---
        
        CORTEX_LOGGER.info(f"Executando tarefa através do Agente: {required_agent_name}.")
        
        try:
            # NOVO: Chamada ao Worker com o pacote AgentMessage
            response: AgentResponse = worker.execute_task(message=execution_message)
            
            # --- NOVO: PROCESSAMENTO DO AgentResponse ---
            
            # Atualiza o resultado final
            task.final_result = response.output_data
            
            # Determina o status final com base na resposta do agente
            new_status = TaskStatus.COMPLETED if response.success else TaskStatus.FAILED
            
            # Atualiza o trace com dados estruturados da resposta
            task.update_status(
                new_status, 
                required_agent_name, 
                response.log_message, 
                result={'output_data': response.output_data, 'next_action': response.suggested_next_action}, 
                success=response.success
            )
            
            CORTEX_LOGGER.info(
                f"Execução SUCESSO. Status final: {new_status.value}. Próxima Ação: {response.suggested_next_action}",
                extra_data={'exec_time': response.execution_time_ms}
            )
            
        except Exception as e:
            error_message = f"ERRO FATAL na execução do agente {required_agent_name}: {e}"
            task.update_status(TaskStatus.FAILED, required_agent_name, error_message, result=error_message, success=False)
            task.final_result = error_message
            CORTEX_LOGGER.error(f"Execução FALHA. Status final: {TaskStatus.FAILED.value}", extra_data={'error': str(e)})
            
        # 5. Resetar o contexto do Logger
        CORTEX_LOGGER.set_task_context(None)
        
        return task
