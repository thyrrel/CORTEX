import logging
import os
from typing import Optional, Dict, Any

class CortexLogger:
    """
    Sistema de Log e Telemetria estruturada do C.O.R.T.E.X.
    Adiciona contexto operacional (MODE, TASK_ID) a todas as entradas de log.
    """
    
    def __init__(self, name: str = 'CORTEX_SYSTEM', log_level: str = 'INFO'):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(log_level.upper())
        self.context: Dict[str, str] = {
            'cortex_mode': os.environ.get("CORTEX_MODE", "UNDEFINED"),
            'pid': str(os.getpid()),
        }
        self._setup_handler()
        
    def _setup_handler(self):
        """Configura o handler e o formatter para saídas em console (JSON estruturado opcionalmente)."""
        if not self.logger.handlers:
            
            # Formato de Log: Adiciona campos chave para rastreamento.
            # Em produção, este formato seria JSON para fácil ingestão em sistemas APM/ELK.
            formatter = logging.Formatter(
                fmt=f"[%(asctime)s] | %(levelname)-8s | CORE: {self.context['cortex_mode']} | PID: {self.context['pid']} | %(name)s | MSG: %(message)s",
                datefmt='%Y-%m-%d %H:%M:%S'
            )
            
            # Handler para saída padrão (console)
            handler = logging.StreamHandler()
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            
    def set_task_context(self, task_id: Optional[str]):
        """Define o ID da Task atual para logs específicos da execução."""
        self.context['task_id'] = task_id or "NONE"

    def info(self, message: str, extra_data: Optional[Dict[str, Any]] = None):
        """Registra uma mensagem informativa."""
        self._log(logging.INFO, message, extra_data)

    def warning(self, message: str, extra_data: Optional[Dict[str, Any]] = None):
        """Registra um alerta."""
        self._log(logging.WARNING, message, extra_data)
        
    def error(self, message: str, extra_data: Optional[Dict[str, Any]] = None):
        """Registra um erro crítico."""
        self._log(logging.ERROR, message, extra_data)

    def critical(self, message: str, extra_data: Optional[Dict[str, Any]] = None):
        """Registra uma falha irrecuperável."""
        self._log(logging.CRITICAL, message, extra_data)

    def _log(self, level: int, message: str, extra_data: Optional[Dict[str, Any]]):
        """Função interna para formatação e envio do log."""
        
        # Cria um dicionário com o contexto base e dados extras
        log_context = {
            'task_id': self.context.get('task_id', 'NONE'),
            'cortex_mode': self.context['cortex_mode'],
            'pid': self.context['pid'],
            **(extra_data or {})
        }
        
        # Formata a mensagem com o contexto relevante
        formatted_message = f"[{log_context['task_id']}] {message} | Data: {log_context}"
        
        self.logger.log(level, formatted_message)

# Instância Singleton do Logger para uso em todo o Core
CORTEX_LOGGER = CortexLogger()

