# backend/core/__main__.py (Versão Corrigida para Lógica de Inicialização e Erro)

import os
import sys
# Importa a exceção específica do MySQL para tratamento de erros.
from mysql.connector import Error as MySQLError 

# Importa as classes de dependência necessárias
from ..persistence.task_repository import TaskRepository
# Assumindo que você também tem uma classe principal para o CORTEX
# from ..core.main_controller import CORTEXController # Exemplo

# ----------------------------------------------------
# CORREÇÃO 1: Adicionando Inicialização de Atributos
# ----------------------------------------------------
class CORTEX:
    def __init__(self):
        # 1. CORREÇÃO: Inicializa o atributo _initialized antes de usá-lo.
        # Se você tem lógica de inicialização complexa, use False/True.
        # Caso contrário, defina todos os atributos aqui.
        self._initialized = False 
        
        # O restante do seu código de inicialização do __init__ viria aqui.
        print("CORTEX: Inicializando componentes...")
        
        # Tenta inicializar o repositório, o que causa a tentativa de conexão MySQL
        self.task_repo = TaskRepository()
        
        # Marca como inicializado
        self._initialized = True
        
    def run(self):
        """ Lógica principal de execução do loop do CORTEX. """
        print("CORTEX: Loop de raciocínio ativado.")
        # Lógica principal de loop de raciocínio, delegação, etc.

# ----------------------------------------------------
# CORREÇÃO 2: Tratamento de Exceções
# ----------------------------------------------------
if __name__ == "__main__":
    print("Iniciando CORTEX...")
    try:
        # Instanciação que desencadeia o TaskRepository.__init__ (e a conexão DB)
        cortex_server = CORTEX() # Linha 52 (ou similar)

        # Lógica principal (se a conexão for bem-sucedida)
        # cortex_server.run() 
        
    # Linha 57: Captura a exceção de MySQL ou uma exceção genérica se houver outros erros
    # CORREÇÃO: Usando a exceção importada (MySQLError) ou a genérica (Exception)
    except MySQLError as e: 
        print(f"ERRO CRÍTICO (MySQL): Falha na conexão ou credenciais: {e}")
        sys.exit(1)
    except ValueError as e:
        # Captura o erro de credenciais vazias do TaskRepository
        print(f"ERRO DE CONFIGURAÇÃO: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"ERRO DESCONHECIDO: {e}")
        sys.exit(1)
