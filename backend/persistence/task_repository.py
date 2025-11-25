# backend/persistence/task_repository.py (Exemplo Corrigido)

# Importações internas do Python
import os
import mysql.connector

# Importação corrigida: usando caminho absoluto a partir do pacote 'backend'
# ANTES: from ..core.dataclasses import Task, TaskStatus, TaskPriority, GlobalContext, ExecutionTrace 
from backend.core.dataclasses import Task, TaskStatus, TaskPriority, GlobalContext, ExecutionTrace # LINHA 9 CORRIGIDA

class TaskRepository:
    def __init__(self):
        # Configuração da conexão usando variáveis de ambiente
        self.host = os.environ.get("CORTEX_DB_HOST")
        self.user = os.environ.get("CORTEX_DB_USER")
        self.password = os.environ.get("CORTEX_DB_PASS")
        self.database = os.environ.get("CORTEX_DB_NAME")
        
        # Teste de conexão (esta linha deve ser o próximo ponto de falha)
        if not all([self.host, self.user, self.password, self.database]):
            raise ValueError("As credenciais do banco de dados não foram fornecidas via Secrets.")
            
        self.conn = mysql.connector.connect(
            host=self.host,
            user=self.user,
            password=self.password,
            database=self.database
        )
        # ... (restante da classe)
