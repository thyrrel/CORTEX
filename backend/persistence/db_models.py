from typing import Dict, Any
from dataclasses import dataclass, field
import json

# --- Modelos de Persistência ---

@dataclass
class TraceDBModel:
    """Modelo de Persistência para o Histórico de Rastreamento."""
    timestamp: float
    agent_name: str
    action_description: str
    result_data_json: str  # Armazena dados complexos como JSON
    success: bool
    
    @classmethod
    def from_core(cls, trace_core):
        """Converte de core.dataclasses.ExecutionTrace para DBModel."""
        return cls(
            timestamp=trace_core.timestamp,
            agent_name=trace_core.agent_name,
            action_description=trace_core.action_description,
            result_data_json=json.dumps(trace_core.result_data),
            success=trace_core.success
        )

@dataclass
class TaskDBModel:
    """Modelo de Persistência para a Unidade de Trabalho (Task)."""
    task_id: str
    description: str
    context_json: str         # GlobalContext e variáveis de ambiente serializadas
    status: str
    priority: int
    required_agent: str
    delegated_to: Optional[str]
    creation_time: float
    last_update_time: float
    final_result_json: Optional[str]
    trace_history_json: str # Lista de TraceDBModel serializada como JSON
    
    @classmethod
    def from_core(cls, task_core):
        """Converte de core.dataclasses.Task para DBModel."""
        
        # Serializa o Contexto Global (que é imutável e complexo)
        context_data = {
            "session_id": task_core.context.session_id,
            "cortex_mode": task_core.context.cortex_mode,
            "initial_prompt": task_core.context.initial_prompt,
            "environment_vars": task_core.context.environment_vars,
        }
        
        # Serializa o Histórico de Rastreamento
        trace_db_models = [TraceDBModel.from_core(t) for t in task_core.trace_history]
        
        return cls(
            task_id=task_core.task_id,
            description=task_core.description,
            context_json=json.dumps(context_data),
            status=task_core.status.value,
            priority=task_core.priority.value,
            required_agent=task_core.required_agent or "None",
            delegated_to=task_core.delegated_to,
            creation_time=task_core.creation_time,
            last_update_time=task_core.last_update_time,
            final_result_json=json.dumps(task_core.final_result),
            trace_history_json=json.dumps([t.__dict__ for t in trace_db_models])
        )
