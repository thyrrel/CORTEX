# backend/persistence/task_repository.py (Versão Final para PythonAnywhere)

import os
import uuid
import mysql.connector
from ..core.dataclasses import Task, TaskStatus, TaskPriority, GlobalContext, ExecutionTrace 

class TaskRepository:
    def __init__(self):
        # ... (Mantém o código de MOCKING para CI/CD) ...
        if os.environ.get("CORTEX_MODE") == "CI_TEST":
            print("CORTEX: Conexão MySQL em modo MOCKING (CI/CD). Conexão real ignorada.")
            self.conn = None
            self.cursor = None 
            return
        
        # LÓGICA DE CONEXÃO REAL (PythonAnywhere)
        self.host = os.environ.get("DB_HOST") 
        self.user = os.environ.get("DB_USER")
        self.password = os.environ.get("DB_PASS")
        self.database = os.environ.get("DB_NAME")
        self.port = os.environ.get("DB_PORT") # Agora será 3306
        
        try:
            self.conn = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database,
                port=int(self.port) 
                # CRÍTICO: Removido ssl_mode="REQUIRED"
            )
            print("Conexão MySQL REAL estabelecida com sucesso.")
            self.cursor = self.conn.cursor()
        except mysql.connector.Error as err:
            print(f"ERRO DE CONEXÃO MySQL: {err}")
            raise err

    # ... (Os métodos save_task e get_task permanecem inalterados) ...
    
