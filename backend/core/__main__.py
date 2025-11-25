# backend/core/main.py (Trecho Relevante: Inicialização)

import os
import uuid
import time
from typing import Any
# ... (Outras importações de CERNE, AgenteManager, dataclasses, scheduler)
from ..persistence.task_repository import TaskRepository 
# ... (Importação do logger, assumindo que existe)

class CORTEX:
    # ... (Singleton Pattern e o método __new__)
    
    def __init__(self):
        if self._initialized:
            return
            
        # 1. Definição do Modo de Operação (EDGE/SERVER)
        self.mode = os.environ.get("CORTEX_MODE", "SERVER").upper() 
        print(f"CORTEX Inicializando em modo: **{self.mode}**")
        
        # 2. Carregar Configuração do DB a partir do Ambiente/Secrets
        db_config = {
            # Lê as variáveis definidas no GitHub Secrets (ou localmente)
            "host": os.environ.get("CORTEX_DB_HOST"), 
            "user": os.environ.get("CORTEX_DB_USER"),
            "password": os.environ.get("CORTEX_DB_PASS"), 
            "database": os.environ.get("CORTEX_DB_NAME", "cortex_db"), # Nome: ezyro_40493351_CORTEX
        }
        
        # Validação Crítica
        if not all(db_config.values()):
            # Esta verificação garante que a Action falhará se os Secrets não forem injetados
            print("ERRO CRÍTICO: Credenciais de Banco de Dados Incompletas. Verifique GitHub Secrets.")
            raise ValueError("Configuração DB Incompleta.")
            
        # 3. Task Repository (Injeção da Configuração)
        self.task_repository = TaskRepository(db_config=db_config)
        
        # 4. Implementação da Lógica (AgenteManager, CERNE, Scheduler)
        # ... (Inicialização dos outros componentes que usam o self.task_repository)

        self._initialized = True
        
    # ... (Resto da classe, incluindo _create_context e start_system)
    
# --- Execução de Teste ---
if __name__ == "__main__":
    # Garante que o teste de persistência rode:
    os.environ["CORTEX_MODE"] = "SERVER" 
    try:
        cortex_server = CORTEX()
        cortex_server.start_system() # start_system contém o teste de save/load
    except ValueError as e:
        print(f"Falha de Inicialização: {e}")
        exit(1) # Força a falha do script se houver erro crítico
    except Error as e:
        print(f"Falha de Persistência MySQL: {e}")
        exit(1) # Força a falha do script se houver erro no TaskRepository
