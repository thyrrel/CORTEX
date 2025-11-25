# backend/core/__init__.py

# Importa as classes essenciais para facilitar o acesso de módulos externos ao 'core'.
# A importação interna (e.g., de main.py) deve usar imports relativos (e.g., from .cerne import CERNE).

from .main import CORTEX
from .cerne import CERNE
from .agente_manager import AgenteManager, WorkerBase
from .dataclasses import Task, TaskStatus, TaskPriority, GlobalContext
from .scheduler import CERNEScheduler, TaskPersister

# Lista de módulos a serem expostos publicamente pelo pacote
__all__ = [
    "CORTEX",
    "CERNE",
    "AgenteManager",
    "WorkerBase",
    "Task",
    "TaskStatus",
    "TaskPriority",
    "GlobalContext",
    "CERNEScheduler",
    "TaskPersister",
]

print("Módulo 'backend.core' inicializado e interfaces principais expostas.")
