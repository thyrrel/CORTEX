import os
import uuid
import json
from typing import Any
from .cerne import CERNE 
from .agente_manager import AgenteManager 
from .dataclasses import GlobalContext, TaskStatus, ExecutionTrace # Importa o contexto e o trace

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
        
    def _create_context(self, prompt: str) -> GlobalContext:
        """Cria um GlobalContext para a tarefa atual."""
        return GlobalContext(
            session_id=str(uuid.uuid4()),
            cortex_mode=self.mode,
            initial_prompt=prompt,
            environment_vars=dict(os.environ)
        )

    def start_system(self):
        """Função de teste e verificação de integridade."""
        print("\n--- Verificação de Integridade CORTEX (Testes de Tarefas) ---")
        
        # --- Teste 1: Tarefa Normal (Delegação Direta) ---
        task_prompt_1 = "Análise de mercado IA Generativa com foco em hardware de Edge."
        context_1 = self._create_context(task_prompt_1)

        if self.mode == "SERVER":
            initial_agent = "Pesquisador_Agente"
        else:
            initial_agent = "Sensor_Agente"
            
        print(f"\n[TESTE 1] Enviando para agente conhecido: {initial_agent}")
        task_1 = self.coordenador.processar_tarefa(task_prompt_1, context_1, initial_agent=initial_agent)
            
        self._display_task_summary(task_1)
        
        print("\n==========================================")
        
        # --- Teste 2: Tarefa de Simulação (Dispara Auto-Modulação / Revisão) ---
        task_prompt_2 = "O sistema exige uma nova solução para um problema de comunicação I/O, necessitando de um agente não existente."
        context_2 = self._create_context(task_prompt_2)
        
        print("\n[TESTE 2] Enviando para agente Nulo (Força Revisão/Auto-Modulação)")
        # A Revisão será acionada porque initial_agent é None
        task_2 = self.coordenador.processar_tarefa(task_prompt_2, context_2, initial_agent=None)
        
        self._display_task_summary(task_2)
        
        print("\n--- FIM da Verificação de Integridade CORTEX ---")

    def _display_task_summary(self, task: Task):
        """Exibe o resumo detalhado de uma Task, incluindo o Trace."""
        print(f"\n### Resumo da Tarefa {task.task_id} ###")
        print(f"  Status Final: **{task.status.value}**")
        print(f"  Delegado Final: {task.delegated_to}")
        print(f"  Resultado Final: {str(task.final_result)[:60]}...")
        
        print("\n  Historico de Rastreamento (Trace):")
        for i, trace in enumerate(task.trace_history):
            status = trace.success and "SUCESSO" or "FALHA"
            print(f"    [{i+1}] {trace.agent_name} ({status}): {trace.action_description[:50]}...")
        
# --- 4. Execução de Teste ---
if __name__ == "__main__":
    # Teste em modo SERVER (padrão)
    os.environ["CORTEX_MODE"] = "SERVER" 
    cortex_server = CORTEX()
    cortex_server.start_system()
    
    print("\n\n=======================================================")
    
    # Teste em modo EDGE
    os.environ["CORTEX_MODE"] = "EDGE" 
    # Reseta o Singleton (Simula reinicialização do processo)
    CORTEX._instance = None 
    cortex_edge = CORTEX()
    cortex_edge.start_system()
