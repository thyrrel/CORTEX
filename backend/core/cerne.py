from typing import Any, Dict, Optional
import uuid
import time
from .agente_manager import AgenteManager, WorkerBase, WorkerSimples, WorkerCompleto # Importa a base e workers para Auto-Modulação
from .dataclasses import Task, TaskStatus, TaskPriority, GlobalContext, ExecutionTrace

class CERNE: 
    """
    O Kernel Lógico do C.O.R.T.E.X. (O Núcleo).
    Implementa o Loop de Raciocínio de 4 Fases e a Orquestração de Workers.
    """
    
    def __init__(self, agente_manager: AgenteManager):
        self._manager = agente_manager
        print("CERNE (Kernel Lógico) ativado. Loop de Raciocínio 4-Fases pronto.")

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

        # Cria uma nova classe temporária que herda do Worker selecionado
        # Isso simula a criação de um novo módulo/classe de agente em tempo de execução
        AdHocAgent = type(agent_name, (AgentClass,), {})
        
        # Registra o novo agente no AgenteManager
        self._manager.register_agent(AdHocAgent)
        
        print(f"Auto-Modulação: Novo agente ad-hoc '{agent_name}' ({complexity}) criado e registrado.")
        return agent_name

    # --- O Loop de Raciocínio (4 Fases) ---

    def processar_tarefa(self, raw_description: str, context: GlobalContext, initial_agent: Optional[str] = None) -> Task:
        """Inicia e executa o Loop de Raciocínio do CERNE para uma nova Tarefa."""
        
        task_id = f"TASK-{uuid.uuid4().hex[:8]}"
        task = Task(
            task_id=task_id,
            description=raw_description,
            context=context,
            required_agent=initial_agent or "ANALYSIS_CORE" # Define o agente inicial
        )

        print(f"\n--- CERNE: Iniciando Tarefa {task_id} ---")
        
        # 1. FASE DE ANÁLISE
        # Determina o agente ou a ação primária necessária
        task.update_status(
            TaskStatus.ANALYSIS, 
            "CERNE", 
            f"Analisando: '{raw_description[:30]}...'"
        )
        
        required_agent_name = initial_agent # Assume-se que o usuário deu uma pista inicial
        
        # Simulação da Lógica de Análise: Se a tarefa for complexa e não houver agente, considere a criação
        if "estudo avançado" in raw_description.lower() and required_agent_name is None:
            required_agent_name = "Pesquisador_Agente"
        
        # 2. FASE DE DELEGAÇÃO
        task.update_status(
            TaskStatus.DELEGATED, 
            "CERNE", 
            f"Tentando delegar para: {required_agent_name or 'Auto-Modulação'}"
        )
        
        worker = None
        if required_agent_name:
            try:
                worker = self._manager.get_agent(required_agent_name)
            except ValueError:
                worker = None # Worker não encontrado, segue para Revisão

        # 3. FASE DE REVISÃO (e Criação Dinâmica)
        if worker is None:
            # Se a delegação falhou ou o agente inicial não foi fornecido/encontrado,
            # o CERNE revisa a necessidade e pode usar Auto-Modulação.
            
            task.update_status(
                TaskStatus.ANALYSIS, # Volta ao status de análise interna
                "CERNE", 
                "Agente não encontrado. Revisando e usando Auto-Modulação."
            )
            
            # Lógica de Auto-Modulação: Cria um agente específico para o problema
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
            f"Executando via {required_agent_name}"
        )
        
        # Chama o worker
        try:
            result_data = worker.execute_task(task_data=raw_description)
            task.final_result = result_data
            task.update_status(TaskStatus.COMPLETED, required_agent_name, "Execução concluída.", result=result_data, success=True)
            print(f"Execução SUCESSO: {task.final_result}")
            
        except Exception as e:
            error_message = f"ERRO na execução do agente {required_agent_name}: {e}"
            task.update_status(TaskStatus.FAILED, required_agent_name, error_message, result=error_message, success=False)
            task.final_result = error_message
            print(f"Execução FALHA: {error_message}")
            
        return task
