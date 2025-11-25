import os
from typing import Dict, Type, Any
from abc import ABC, abstractmethod

# --- 1. Classes de Simulação (Para funcionalidade imediata) ---

class WorkerBase(ABC):
    """Classe base abstrata para todos os Workers (EDGE/SERVER)."""
    
    def __init__(self, name: str):
        self.name = name
        
    @abstractmethod
    def execute_task(self, task_data: Any) -> Any:
        """Executa uma tarefa recebida."""
        pass

class WorkerSimples(WorkerBase):
    """Simula um worker de baixa capacidade (modo EDGE)."""
    def execute_task(self, task_data: str) -> str:
        return f"Worker Simples [{self.name}] processou: '{task_data[:15]}...' (EDGE)"

class WorkerCompleto(WorkerBase):
    """Simula um worker de alta capacidade (modo SERVER)."""
    def execute_task(self, task_data: str) -> str:
        return f"Worker Completo [{self.name}] processou: '{task_data}' (SERVER)"

class AgenteManager:
    """Simulação do Módulo AgenteManager: Carrega e instancia workers."""
    
    def __init__(self, mode: str):
        self._worker_map: Dict[str, Type[WorkerBase]] = {}
        if mode == "SERVER":
            # Nomenclatura de Agentes (coerente com o CERNE)
            self._worker_map["Pesquisador_Agente"] = WorkerCompleto
            self._worker_map["Engenheiro_Agente"] = WorkerCompleto
        else: # EDGE
            self._worker_map["Sensor_Agente"] = WorkerSimples
            self._worker_map["Reporter_Agente"] = WorkerSimples
        print(f"AgenteManager inicializado em modo '{mode}'. Agentes disponíveis: {list(self._worker_map.keys())}")

    def get_agent(self, agent_name: str) -> WorkerBase:
        """Instancia e retorna um agente pelo nome."""
        worker_class = self._worker_map.get(agent_name)
        if not worker_class:
            raise ValueError(f"Agente '{agent_name}' não encontrado neste modo de operação.")
        return worker_class(name=agent_name)

# --- 2. Classes do Núcleo C.O.R.T.E.X. ---

class CERNE: # <--- CLASSE RENOMEADA DE CoordenadorV2
    """
    O Kernel Lógico do C.O.R.T.E.X. (O Núcleo).
    Implementa o Loop de Raciocínio (Análise -> Delegação -> Execução) e a Orquestração de Workers.
    """
    
    def __init__(self, agente_manager: AgenteManager):
        self._manager = agente_manager
        print("CERNE (Kernel Lógico) ativado. Loop de Raciocínio pronto.")

    def auto_modulacao(self, purpose: str = "Teste Simples") -> WorkerBase:
        """
        Função de Auto-Modulação: Cria agentes ad-hoc para testes ou simulações.
        Garante nomenclatura coerente com Agente_*.
        """
        # Nomenclatura ajustada para Agente_Simulacao
        agent_name = f"Agente_{purpose.replace(' ', '_')}" 
        print(f"Auto-Modulação: Criando agente de simulação '{agent_name}'.")
        # Cria um worker simples independentemente do modo principal.
        return WorkerSimples(name=agent_name)

    def processar_tarefa(self, task_desc: str, required_agent: str) -> str:
        """Executa o Loop de Raciocínio simplificado: Análise -> Delegação -> Execução."""
        print(f"\n--- Processando Tarefa em CERNE: '{task_desc}' ---")
        
        # 1. Análise (Simplificada)
        if "simulação" in task_desc.lower():
             worker = self.auto_modulacao(purpose="Simulacao_Teste")
        else:
            # 2. Delegação
            try:
                worker = self._manager.get_agent(required_agent)
            except ValueError as e:
                return f"Erro de Delegação: {e}"
        
        # 3. Execução
        resultado = worker.execute_task(task_data=task_desc)
        return resultado

class CORTEX:
    """
    A Fachada Singleton e o Ponto de Entrada (main) do Sistema de Orquestração.
    Define o ambiente operacional (EDGE/SERVER).
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
        
        # O CORTEX inicializa o CERNE com o Manager
        self.coordenador = CERNE(agente_manager=self.agente_manager) # <--- USO DA NOVA CLASSE
        
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
        
# --- 3. Execução de Teste ---
if __name__ == "__main__":
    # Teste em modo SERVER (padrão)
    os.environ["CORTEX_MODE"] = "SERVER" 
    cortex_server = CORTEX()
    cortex_server.start_system()
    
    print("\n==========================================")
    
    # Teste em modo EDGE
    os.environ["CORTEX_MODE"] = "EDGE" 
    # Força uma nova instância para teste de ambiente
    CORTEX._instance = None 
    cortex_edge = CORTEX()
    cortex_edge.start_system()
