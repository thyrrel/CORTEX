# backend/core/agente_manager.py - Trecho modificado para carregamento dinâmico

# IMPORTAÇÃO CHAVE: Importa a lista de plugins
from ...agents import AGENT_PLUGINS 

class AgenteManager:
    # ... (métodos e atributos)

    def _load_agents_by_mode(self):
        """Carrega agentes do AGENT_PLUGINS, filtrando por uma flag de modo (simulada)."""
        
        for AgentClass in AGENT_PLUGINS:
            # Simulação de filtro: agentes que não são "simples" rodam em SERVER
            is_simple_worker = "Simples" in AgentClass.__name__ 
            
            if self._mode == "SERVER" and not is_simple_worker:
                self._register_agent_class(AgentClass)
            elif self._mode == "EDGE" and is_simple_worker: # Exemplo de filtro para EDGE
                self._register_agent_class(AgentClass)
            # Nota: A lógica real de filtro seria baseada em metadados da classe AgentClass.

    def _register_agent_class(self, AgentClass):
         agent_name = AgentClass.__name__
         self._agent_map[agent_name] = AgentClass
         CORTEX_LOGGER.info(f"Plugin carregado: {agent_name} no modo {self._mode}")
