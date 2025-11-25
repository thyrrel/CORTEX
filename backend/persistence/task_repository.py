# backend/persistence/task_repository.py (Versão Final: SSL, Mocking e CRUD)

import os
import uuid
import mysql.connector

# Importações de dependência (garantir que estas classes estão definidas no dataclasses.py)
from ..core.dataclasses import Task, TaskStatus, TaskPriority, GlobalContext, ExecutionTrace 

class TaskRepository:
    """
    Gerencia a persistência de Tasks e ExecutionTraces no banco de dados MySQL.
    """
    def __init__(self):
        # ----------------------------------------------------
        # MOCKING CONDICIONAL PARA CI/CD (Mantido para compatibilidade)
        # ----------------------------------------------------
        if os.environ.get("CORTEX_MODE") == "CI_TEST":
            print("CORTEX: Conexão MySQL em modo MOCKING (CI/CD). Conexão real ignorada.")
            self.conn = None
            self.cursor = None 
            return
        
        # ----------------------------------------------------
        # LÓGICA DE CONEXÃO REAL (PythonAnywhere/Produção)
        # ----------------------------------------------------
        self.host = os.environ.get("DB_HOST") 
        self.user = os.environ.get("DB_USER")
        self.password = os.environ.get("DB_PASS")
        self.database = os.environ.get("DB_NAME")
        self.port = os.environ.get("DB_PORT")
        
        # Tentativa de conexão
        try:
            self.conn = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database,
                port=int(self.port),
                # CORREÇÃO CRÍTICA: Adicionar SSL_MODE=REQUIRED para Aiven
                ssl_mode="REQUIRED" 
            )
            print("Conexão MySQL REAL estabelecida com sucesso.")
            self.cursor = self.conn.cursor()
        except mysql.connector.Error as err:
            print(f"ERRO DE CONEXÃO MySQL: {err}")
            raise err

    def save_task(self, task: Task):
        if self.conn is None:
            # Erro de execução se não estiver em CI_TEST e a conexão falhar.
            raise Exception("Conexão MySQL não estabelecida. Não é possível salvar a tarefa em modo real.")

        if not task.task_id:
            task.task_id = str(uuid.uuid4()) # Gera um UUID se for nova

        # Query usa ON DUPLICATE KEY UPDATE para suportar criação e atualização
        sql = """
        INSERT INTO Tasks (task_id, content, status, priority)
        VALUES (%s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE
            content = VALUES(content),
            status = VALUES(status),
            priority = VALUES(priority),
            updated_at = CURRENT_TIMESTAMP
        """
        
        values = (
            task.task_id,
            task.content,
            task.status,
            task.priority
        )

        try:
            self.cursor.execute(sql, values)
            self.conn.commit()
            print(f"Tarefa {task.task_id} salva/atualizada com sucesso.")
            return task.task_id
        except mysql.connector.Error as err:
            self.conn.rollback()
            print(f"ERRO ao salvar tarefa: {err}")
            raise

    def get_task(self, task_id: str) -> Task:
        # Implementação em breve
        pass
