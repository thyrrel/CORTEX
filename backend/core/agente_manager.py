# Trecho de backend/core/agente_manager.py

class WorkerBase(ABC):
    # ... (métodos __init__ e __repr__ mantidos)
    
    @abstractmethod
    # NOVO ASSINATURA: Usa AgentMessage e retorna AgentResponse
    def execute_task(self, message: AgentMessage) -> AgentResponse: 
        """Método principal para execução de tarefas delegadas pelo CERNE."""
        pass
