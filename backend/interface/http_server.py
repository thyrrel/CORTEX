import os
import uvicorn # Simulação de framework assíncrono
from typing import Dict, Any
from ..core.main import CORTEX 
from .api_models import TaskRequest, TaskResponse, HealthResponse
from ..core.dataclasses import TaskStatus, TaskPriority, GlobalContext
import uuid

# Global CORTEX instance (Simula a inicialização do app)
CORTEX_INSTANCE: Optional[CORTEX] = None

def init_cortex():
    """Inicializa o Singleton CORTEX e o Scheduler."""
    global CORTEX_INSTANCE
    if CORTEX_INSTANCE is None:
        CORTEX_INSTANCE = CORTEX()
        # Inicia o Scheduler Thread
        CORTEX_INSTANCE.scheduler.start()
        print("CORTEX inicializado e Scheduler em execução.")

# --- Simulação de Endpoints HTTP ---

def get_health() -> HealthResponse:
    """Endpoint: /health"""
    if CORTEX_INSTANCE is None:
        return HealthResponse(status="UNINITIALIZED", cortex_mode="N/A", scheduler_status="STOPPED", agents_count=0)

    # Nota: A contagem de agentes é simulada, mas acessada via AgenteManager
    agent_count = len(CORTEX_INSTANCE.agente_manager.list_agents())

    return HealthResponse(
        status="RUNNING",
        cortex_mode=CORTEX_INSTANCE.mode,
        scheduler_status="ACTIVE", # Em um sistema real, verificaríamos a thread.is_alive()
        agents_count=agent_count
    )

def submit_task_endpoint(request: TaskRequest) -> TaskResponse:
    """Endpoint: POST /task/submit"""
    if CORTEX_INSTANCE is None:
        raise Exception("CORTEX não está ativo.")

    # 1. Cria o GlobalContext a partir da requisição
    context = GlobalContext(
        session_id=str(uuid.uuid4()),
        cortex_mode=CORTEX_INSTANCE.mode,
        initial_prompt=request.description,
        environment_vars=request.metadata # Metadados como variáveis ambientais
    )

    # 2. Submete a tarefa ao Scheduler
    new_task = CORTEX_INSTANCE.scheduler.submit_task(
        request.description,
        context,
        priority=request.priority,
        initial_agent=request.initial_agent
    )

    # 3. Retorna o status inicial
    return TaskResponse(
        task_id=new_task.task_id,
        status=new_task.status,
        delegated_to=new_task.delegated_to,
        final_result_summary=None,
        trace_history=[]
    )

def get_task_status_endpoint(task_id: str) -> TaskResponse:
    """Endpoint: GET /task/{task_id}"""
    if CORTEX_INSTANCE is None:
        raise Exception("CORTEX não está ativo.")
        
    task = CORTEX_INSTANCE.persister.load_task(task_id)
    
    if not task:
        raise FileNotFoundError(f"Task ID {task_id} não encontrado.")
    
    # Cria o resumo do resultado final para a API
    final_summary = str(task.final_result)[:200] if task.final_result else None

    return TaskResponse(
        task_id=task.task_id,
        status=task.status,
        delegated_to=task.delegated_to,
        final_result_summary=final_summary,
        trace_history=task.trace_history
    )

# --- Função de Execução Principal (Simulação) ---
def run_http_server(mode="SERVER", port=8000):
    os.environ["CORTEX_MODE"] = mode
    init_cortex()
    
    # Simulação de inicialização do servidor (usando uvicorn/framework)
    print(f"\nServidor HTTP (Interface) iniciado na porta {port} em modo {mode}.")
    print("Endpoints disponíveis: /health, /task/submit, /task/{id}")
    
    # Exemplo de como um cliente usaria:
    # 1. health = get_health()
    # 2. submissao = submit_task_endpoint(TaskRequest(...))
    # 3. status = get_task_status_endpoint(submissao.task_id)

if __name__ == "__main__":
    # Teste de inicialização da interface
    run_http_server(mode="SERVER")

