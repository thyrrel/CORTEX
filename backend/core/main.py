# backend/core/main.py (Trecho modificado)

import os
# ... (outras importações)
from ..persistence.task_repository import TaskRepository 

class CORTEX:
    # ... (código do Singleton)
    
    def __init__(self):
        if self._initialized:
            return
            
        # ... (Configuração de Modo)
        
        # --- 3. Carregar Configuração do DB a partir do Ambiente/Secrets ---
        db_config = {
            # As variáveis de ambiente devem ser definidas no GitHub Secrets (ou localmente para teste)
            "host": os.environ.get("CORTEX_DB_HOST", "localhost"), # Default para localhost para dev local
            "user": os.environ.get("CORTEX_DB_USER", "root"),
            "password": os.environ.get("CORTEX_DB_PASS"), # Não deve ter default!
            "database": os.environ.get("CORTEX_DB_NAME", "cortex_db"),
        }
        
        if not db_config["password"]:
            CORTEX_LOGGER.critical("Variável de ambiente CORTEX_DB_PASS não definida. Persistência falhará.")
            # Não lançamos exceção aqui para permitir que o sistema inicie, mas o repository falhará.
            
        # 4. Task Repository (Injeção da Configuração)
        self.task_repository = TaskRepository(db_config=db_config)
        
        # ... (restante da inicialização)
