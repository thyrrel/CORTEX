# backend/persistence/task_repository.py (Versão Corrigida)

import os
import mysql.connector

# CORREÇÃO: Usando Importação Absoluta para resolver o ModuleNotFoundError.
from backend.core.dataclasses import Task, TaskStatus, TaskPriority, GlobalContext, ExecutionTrace 

class TaskRepository:
    """
    Gerencia a persistência de Tasks e ExecutionTraces no banco de dados MySQL.
    """
    def __init__(self):
        # CORREÇÃO: Acessando os novos nomes de variáveis de ambiente.
        self.host = os.environ.get("DB_HOST") 
        self.user = os.environ.get("DB_USER")
        self.password = os.environ.get("DB_PASS")
        self.database = os.environ.get("DB_NAME")
        
        # Validação para garantir que as variáveis foram lidas.
        if not all([self.host, self.user, self.password, self.database]):
            raise ValueError("As credenciais do banco de dados (DB_HOST, DB_USER, etc.) não foram fornecidas/lidas corretamente.")
            
        # Tentativa de conexão
        try:
            self.conn = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database
            )
            print("Conexão MySQL estabelecida com sucesso.")
            self.cursor = self.conn.cursor()
        except mysql.connector.Error as err:
            print(f"Erro ao conectar ao MySQL: {err}")
            # Re-lança o erro para falhar a execução do CORTEX
            raise err

    # Placeholder para métodos de persistência
    def save_task(self, task: Task):
        pass # Implementação futura

    def get_task(self, task_id: str) -> Task:
        pass # Implementação futura

# Garanta que o __main__.py use TaskRepository, causando a tentativa de conexão.
