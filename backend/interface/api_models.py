from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any
import uuid
# Importamos enumerações do core para manter o alinhamento de tipos
from ..core.dataclasses import TaskStatus, TaskPriority, ExecutionTrace 

@dataclass(frozen=True)
class TaskRequest:
    """Modelo de entrada para submeter uma nova tarefa ao sistema."""
    description: str
    priority: TaskPriority = TaskPriority.MEDIUM
    initial_agent: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
@dataclass
class TaskResponse:
    """Modelo de saída para retornar o estado de uma Task."""
    task_id: str
    status: TaskStatus
    delegated_to: Optional[str]
    final_result_summary: Optional[str]
    trace_history: List[ExecutionTrace]
    
@dataclass
class HealthResponse:
    """Modelo de saída para a verificação de saúde do sistema."""
    status: str
    cortex_mode: str
    scheduler_status: str
    agents_count: int

