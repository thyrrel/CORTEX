import os
# Importa o CERNE do seu novo módulo dedicado
from .cerne import CERNE 
# Importa o AgenteManager do seu módulo dedicado
from .agente_manager import AgenteManager 
from typing import Any

class CORTEX:
    """
    A Fachada Singleton e o Ponto de Entrada (main) do Sistema de Orquestração C.O.R.T.E.X.
    Define o ambiente operacional (EDGE/SERVER) e inicializa o AgenteManager e o CERNE.
    """
    _instance = None
    
    def __new__(cls, *args, **kwargs):
        """Implementa o padrão Singleton."""
        if cls._instance is None:
            cls._instance = super(CORTEX, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
            
        # 1. Definição do Modo de Operação
        self.mode = os.environ.get("CORTEX_MODE", "SERVER").upper() # Padrão: SERVER
        if self.mode not in ["EDGE", "SERVER"]:
             raise ValueError("Variável de ambiente CORTEX_MODE deve ser 'EDGE' ou 'SERVER'.")
        
        print(f"CORTEX Inicializando em modo: **{self.mode}**")
        
        # 2. Implementação da Lógica de Carregamento
        self.agente_manager = AgenteManager(mode=self.mode)
        
        # 3. O CORTEX inicializa o CERNE com o Manager
        self.coordenador: CERNE = CERNE(agente_manager=self.agente_manager)
        
        self._initialized = True
        
    def start_system(self):
        """Função de teste e verificação de integridade."""
        print("\n--- Verificação de Integridade CORTEX ---")
        
        # Teste 1: Tarefa Normal (Delegação)
        if self.mode == "SERVER":
            r1 = self.coordenador.processar_tarefa("Análise de mercado IA Generativa", "Pesquisador_Agente")
        else:
            r1 = self.coordenador.processar_tarefa("Leitura do Sensor 0xAB12", "Sensor_Agente")
            
        print(f"Resultado (Delegação): {r1}")
        
        # Teste 2: Tarefa de Simulação (Auto-Modulação)
        r2 = self.coordenador.processar_tarefa("Executar simulação de falha de I/O", "N/A")
        print(f"Resultado (Auto-Modulação): {r2}")
        
        print("------------------------------------------")
        
# --- 4. Execução de Teste ---
if __name__ == "__main__":
    # Teste em modo SERVER (padrão)
    os.environ["CORTEX_MODE"] = "SERVER" 
    cortex_server = CORTEX()
    cortex_server.start_system()
    
    print("\n==========================================")
    
    # Teste em modo EDGE
    os.environ["CORTEX_MODE"] = "EDGE" 
    CORTEX._instance = None 
    cortex_edge = CORTEX()
    cortex_edge.start_system()
