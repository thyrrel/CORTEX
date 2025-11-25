# backend/persistence/task_repository.py (Versão Corrigida para Porta)

import os
import mysql.connector
from ..core.dataclasses import Task, TaskStatus, TaskPriority, GlobalContext, ExecutionTrace 

class TaskRepository:
    def __init__(self):
        # ----------------------------------------------------
        # MOCKING CONDICIONAL PARA CI/CD
        # ----------------------------------------------------
        if os.environ.get("CORTEX_MODE") == "CI_TEST":
            print("CORTEX: Conexão MySQL em modo MOCKING (CI/CD). Conexão real ignorada.")
            self.conn = None
            self.cursor = None 
            return
        
        # ----------------------------------------------------
        # LÓGICA DE CONEXÃO REAL (Leitura dos 5 Secrets)
        # ----------------------------------------------------
        self.host = os.environ.get("DB_HOST") 
        self.user = os.environ.get("DB_USER")
        self.password = os.environ.get("DB_PASS")
        self.database = os.environ.get("DB_NAME")
        
        # LER A PORTA
        self.port = os.environ.get("DB_PORT") # Lendo o novo Secret DB_PORT
        
        # Validação de credenciais (Verificando a nova variável self.port)
        if not all([self.host, self.user, self.password, self.database, self.port]):
            raise ValueError("As credenciais do banco de dados (DB_HOST, DB_USER, DB_PORT, etc.) não foram fornecidas/lidas corretamente.")
            
        # Tentativa de conexão
        try:
            self.conn = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database,
                # PASSANDO A PORTA: Convertendo o valor do Secret (string) para int
                port=int(self.port) 
            )
            print("Conexão MySQL REAL estabelecida com sucesso.")
            self.cursor = self.conn.cursor()
        except mysql.connector.Error as err:
            print(f"ERRO DE CONEXÃO MySQL: {err}")
            raise err
    
    def save_task(self, task: Task):
        if self.conn is None:
            print(f"MOCK: Salvando tarefa {task.task_id} em memória.")
            return
        pass 

    def get_task(self, task_id: str) -> Task:
        pass
