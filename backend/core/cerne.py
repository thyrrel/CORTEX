from typing import Any, Dict, Optional
import uuid
import time
from .agente_manager import AgenteManager, WorkerBase
from .dataclasses import Task, TaskStatus, TaskPriority, GlobalContext, ExecutionTrace
from .protocol import AgentMessage, AgentResponse 
from ..utilities.logger import CORTEX_LOGGER 

class CERNE: 
    """
    O Kernel Lógico do C.O.R.T.E.X. (O Núcleo).
    Implementa o Loop de Raciocínio Multi-Pass com base no Protocolo Agente-CERNE.
    """
    
    # ... (Métodos __init__ e _create_new_adhoc_agent permanecem os mesmos)
    
    def __init__(self, agente_manager: AgenteManager):
        self._manager = agente_manager
        CORTEX_LOGGER.info("CERNE (Kernel Lógico) ativado. Loop de Raciocínio Multi-Pass pronto.")

    # ... (Método _create_new_adhoc_agent permanece o mesmo)
    
    # --- Novo: Método de Gerenciamento de Ciclo ---
    
    def processar_tarefa(self, task: Task) -> Task:
        """
        Ponto de entrada do Scheduler. Inicia ou retoma o ciclo de execução da Task.
        """
        # Aqui, o CERNE decide se a Task precisa de análise inicial ou se é uma retomada.
        if task.status in [TaskStatus.PENDING, TaskStatus.RETRY]:
            return self._execute_task_cycle(task, is_initial_run=True)
        
        # Para outros status (ex: WAITING_BACKOFF), a lógica de retomada será adicionada no Scheduler.
        CORTEX_LOGGER.warning(f"Task {task.task_id} está no status {task.status.value}. Ignorando processamento neste ciclo.", extra_data={'task_id': task.task_id})
        return task

    def _execute_task_cycle(self, task: Task, is_initial_run: bool = False) -> Task:
        """Executa um único passo (passo completo de 4 fases) do Loop de Raciocínio."""
        
        # Configura o contexto do Logger para esta Task
        CORTEX_LOGGER.set_task_context(task.task_id)
        CORTEX_LOGGER.info(f"Iniciando ciclo de execução.", extra_data={'task_id': task.task_id, 'initial_run': is_initial_run})

        # 1. FASE DE ANÁLISE (e Determinação do Próximo Agente)
        # O agente alvo é o 'required_agent' se for uma execução inicial, ou o sugerido pela última resposta.
        required_agent_name = task.required_agent
        
        # Simulação de Lógica de Encadeamento: Se a task já tem trace, o próximo agente pode ser determinado pela sugestão
        if not is_initial_run and task.trace_history:
            last_trace = task.trace_history[-1]
            # Assumimos que o campo 'result' do trace contém o AgentResponse desempacotado
            suggested_action = last_trace.result_data.get('next_action') 
            
            if suggested_action and suggested_action.startswith("DELEGATE_TO_"):
                required_agent_name = suggested_action.replace("DELEGATE_TO_", "")
                task.update_status(TaskStatus.ANALYSIS, "CERNE", f"Encadeamento: Alvo definido como {required_agent_name}")
            else:
                # Caso a sugestão não seja de encadeamento, usa o agente inicial ou o último delegado.
                required_agent_name = task.delegated_to or task.required_agent
        
        # 2. FASE DE DELEGAÇÃO e 3. FASE DE REVISÃO (Mapeamento de Agente)
        try:
            worker = self._manager.get_agent(required_agent_name)
        except ValueError:
            # Caso o agente não exista ou falhe na inicialização, tenta Auto-Modulação
            task.update_status(TaskStatus.ANALYSIS, "CERNE", "Agente indisponível. Acionando Auto-Modulação.")
            new_agent_name = self._create_new_adhoc_agent(
                purpose="Revisor_AdHoc", 
                complexity="Simples" if task.context.cortex_mode == "EDGE" else "COMPLETO"
            )
            worker = self._manager.get_agent(new_agent_name)
            required_agent_name = new_agent_name
            
        task.delegated_to = required_agent_name
        
        # 4. FASE DE EXECUÇÃO
        task.update_status(TaskStatus.IN_PROGRESS, "CERNE", f"Executando via {required_agent_name}")
        
        execution_message = AgentMessage(
            task_id=task.task_id,
            action_type="EXECUTE_TASK",
            raw_prompt=task.description,
            parameters={'mode': task.context.cortex_mode}
        )
        
        try:
            response: AgentResponse = worker.execute_task(message=execution_message)
            
            # Processamento da Resposta Estruturada
            
            # 5. NOVO: LÓGICA DE DECISÃO MULTI-PASS
            final_status = TaskStatus.COMPLETED
            next_action = response.suggested_next_action
            
            if not response.success:
                # Caso de Falha de Execução (inclui falha de rede tratada pelo Agente)
                
                if next_action == "RETRY_IN_BACKOFF":
                    final_status = TaskStatus.RETRY # Novo status de espera ativa
                    CORTEX_LOGGER.warning("Agente sugeriu RETRY_IN_BACKOFF. Task será re-enfileirada.")
                elif next_action == "EXTERNAL_MANUAL_REVIEW":
                    final_status = TaskStatus.FAILED # Estado terminal
                    CORTEX_LOGGER.critical("Agente sugeriu REVISÃO MANUAL. Task movida para FAILED.")
                else:
                    final_status = TaskStatus.FAILED
                    CORTEX_LOGGER.error(f"Falha de execução não tratada: {response.log_message}")

            elif next_action not in ["TASK_COMPLETED", "TASK_COMPLETED_SIMPLE"]:
                # Caso de Sucesso e Sugestão de Continuação (Encadeamento)
                final_status = TaskStatus.DELEGATED # Estado intermediário para indicar que requer novo ciclo
                task.required_agent = required_agent_name # Manter o agente atual para o trace
                CORTEX_LOGGER.info(f"Encadeamento sugerido: {next_action}. Task requer novo ciclo.")
            
            # Atualiza o trace com dados estruturados da resposta
            task.update_status(
                final_status, 
                required_agent_name, 
                response.log_message, 
                result={'output_data': response.output_data, 'next_action': next_action, 'exec_time': response.execution_time_ms}, 
                success=response.success
            )
            
        except Exception as e:
            # ERRO FATAL (não tratado pelo Agente, ex: falha de memória do CERNE)
            error_message = f"ERRO FATAL (CERNE) na execução do agente {required_agent_name}: {e}"
            task.update_status(TaskStatus.FAILED, required_agent_name, error_message, result=error_message, success=False)
            task.final_result = error_message
            CORTEX_LOGGER.critical(f"Execução FALHA IRRECUPERÁVEL. Status final: {TaskStatus.FAILED.value}", extra_data={'error': str(e)})
            
        CORTEX_LOGGER.set_task_context(None)
        return task
