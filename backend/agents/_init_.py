# backend/agents/__init__.py
from .agent_impls import Pesquisador_Agente, Engenheiro_Agente # Importa os agentes concretos

# Lista dos Agentes disponíveis para o AgenteManager
AGENT_PLUGINS = [
    Pesquisador_Agente,
    Engenheiro_Agente,
    # ... (adicionar outros agentes aqui)
]
