# backend/core/dataclasses.py (Arquivo NOVO)

from dataclasses import dataclass
from typing import Literal

# Definições de Tipos (Módulos/Strings)
TaskStatus = Literal["PENDING", "PROCESSING", "COMPLETED", "FAILED"]
TaskPriority = Literal["HIGH", "MEDIUM", "LOW"]

@dataclass
class Task:
    """ Representa uma tarefa a ser processada pelo CORTEX. """
    task_id: str
    content: str
    status: TaskStatus = "PENDING"
    priority: TaskPriority = "MEDIUM"
    created_at: str = ""

@dataclass
class ExecutionTrace:
    """ Rastreia logs e eventos durante a execução de uma Task. """
    trace_id: str
    task_id: str
    log_message: str
    timestamp: str

@dataclass
class GlobalContext:
    """ Mantém configurações de estado global. """
    db_connection_status: str = "DISCONNECTED"
    api_key_valid: bool = False
    # Adicione outros campos conforme a necessidade
