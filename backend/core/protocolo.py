from dataclasses import dataclass, field
from typing import Dict, Any, Optional
import uuid
from ..core.dataclasses import TaskStatus, ExecutionTrace # Reutiliza tipos do Core

# --- 1. Pacote de Requisição do CERNE para o Agente ---

@dataclass(frozen=True) # A mensagem de requisição é imutável
class AgentMessage:
    """
    Pacote de dados de requisição enviado pelo CERNE para um Worker.
    Define o que o Agente deve executar.
    """
    
    # Identificadores de Rastreamento
    message_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    task_id: str
    
    # Payload da Ação
    action_type: str # Ex: "ANALYZE_PROMPT", "RETRIEVE_DATA", "GENERATE_CODE"
    raw_prompt: str
    
    # Parâmetros Específicos do Agente
    parameters: Dict[str, Any] = field(default_factory=dict)
    
    # Contexto de Segurança/Recursos
    resource_limits: Dict[str, Any] = field(default_factory=dict)
    
# --- 2. Pacote de Resposta do Agente para o CERNE ---

@dataclass
class AgentResponse:
    """
    Pacote de dados de resposta retornado de um Worker para o CERNE.
    Define o resultado da execução e a próxima etapa sugerida.
    """
    
    # Identificadores de Rastreamento
    message_id: str # Deve corresponder ao message_id da AgentMessage
    task_id: str
    
    # Status e Resultado
    success: bool
    status_code: int # Ex: 200 (OK), 400 (Input Inválido), 500 (Erro Interno)
    output_data: Any # O resultado principal da execução (pode ser JSON, string, etc.)
    
    # Rastreamento/Telemetria da Execução
    execution_time_ms: float
    
    # Sugestão de Próxima Ação (Para o Loop de Raciocínio)
    suggested_next_action: Optional[str] = None # Ex: "NEED_REVIEW", "DELEGATE_TO_ENGINEER", "TASK_COMPLETED"
    
    # Mensagens e Erros
    log_message: str = "Execução concluída."
    error_details: Optional[str] = None

