# backend/core/__main__.py (Versão Final com Teste de Persistência)

import sys
import mysql.connector

# Importações de módulos do projeto
from ..persistence.task_repository import TaskRepository
from ..core.dataclasses import Task, TaskStatus, TaskPriority # Importar apenas o necessário

# Define o erro para captura no bloco principal
MySQLError = mysql.connector.Error

class CORTEX:
    def __init__(self):
        self._initialized = False 
        print("CORTEX: Inicializando componentes...")
        # A inicialização do TaskRepository tentará a conexão ou entrará em mocking.
        self.task_repo = TaskRepository()
        self._initialized = True

    def run(self):
        """ Lógica principal de execução do loop do CORTEX. """
        print("CORTEX: Loop de raciocínio ativado.")
        
        # 🧪 TESTE DE CONEXÃO E PERSISTÊNCIA 🧪
        if self.task_repo.conn is not None:
            print("CORTEX: Rodando teste de persistência...")
            nova_tarefa = Task(
                task_id="", 
                content="Analisar e estruturar o plano de desenvolvimento do Módulo 1 (Scheduler) e do Agente Core.",
                priority=TaskPriority.HIGH
            )
            # Força o salvamento da primeira tarefa real
            self.task_repo.save_task(nova_tarefa)
            print("Teste de persistência concluído.")
        else:
            print("CORTEX: Teste de persistência ignorado (Modo MOCKING/CI_TEST).")

        # Futura lógica do CORTEX virá aqui...


if __name__ == "__main__":
    try:
        cortex_server = CORTEX() 
        cortex_server.run() 
        
    except MySQLError as e: 
        # Captura erros de conexão/autenticação MySQL
        print(f"ERRO CRÍTICO (MySQL): Falha na conexão ou credenciais: {e}")
        sys.exit(1)
    except ValueError as e:
        # Captura erros de configuração (e.g., variável faltando)
        print(f"ERRO DE CONFIGURAÇÃO: {e}")
        sys.exit(1)
    except Exception as e:
        # Captura erros inesperados
        print(f"ERRO DESCONHECIDO: {e}")
        sys.exit(1)
