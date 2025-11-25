# backend/agents/__init__.py
from .agent_impls import Pesquisador_Agente, Engenheiro_Agente, Sensor_Agente, WorkerSimples 

# LISTA OFICIAL DE PLUGINS (Entry Point do sistema de agentes)
AGENT_PLUGINS = [
    Pesquisador_Agente,
    Engenheiro_Agente,
    Sensor_Agente, 
    WorkerSimples,
]
