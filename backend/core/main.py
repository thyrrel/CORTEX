import os
import uuid
import time
from typing import Any, Optional
from .cerne import CERNE 
from .agente_manager import AgenteManager 
from .dataclasses import GlobalContext, TaskStatus, TaskPriority
from ..persistence.task_repository import TaskRepository 
from .scheduler import CERNEScheduler 
from ..utilities.logger import CORTEX_LOGGER # Importa o Logger

class CORTEX:
    """
    A Fachada Singleton e o Ponto de Entrada (main) do Sistema de Orquestração C.O.R.T.E.X.
    Inicializa todas as camadas arquiteturais.
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
        self.mode = os.environ.get("CORTEX_MODE", "SERVER").upper()
        if self.mode not in ["EDGE", "SERVER"]:
             CORTEX_LOGGER.critical(f"Modo CORTEX_MODE inválido: {self.mode}. Encerrando.")
             raise ValueError("Variável de ambiente CORTEX_MODE deve ser 'EDGE' ou 'SERVER'.")
        
        CORTEX_LOGGER.info(f"CORTEX Inicializando em modo: **{self.mode}**", extra_data={'mode': self.mode})
        
        # 2. Implementação da Lógica de Carregamento
        self.agente_manager = AgenteManager(mode=self.mode)
        
        # 3. Inicializa o CERNE
        self.coordenador: CERNE = CERNE(agente_manager=self.agente_manager)
        
        # 4. Camada de Persistência
        self.task_repository = TaskRepository() 
        
        # 5. Agendamento
        self.scheduler = CERNEScheduler(
            cerne_instance=self.coordenador, 
            task_repository=self.task_repository
        ) 
        
        self._initialized = True
        CORTEX_LOGGER.info("CORTEX Inicialização concluída. Sistema pronto.")
        
    def _create_context(self, prompt: str) -> GlobalContext:
        """Cria um GlobalContext para a tarefa atual."""
        return GlobalContext(
            session_id=str(uuid.uuid4()),
            cortex_mode=self.mode,
            initial_prompt=prompt,
            environment_vars=dict(os.environ)
        )

    def start_system(self):
        """Inicia o Scheduler e submete tarefas para teste."""
        CORTEX_LOGGER.info("Iniciando Thread do Scheduler para processamento assíncrono.")
        
        # INICIA A THREAD DO SCHEDULER
        self.scheduler.start()
        
        # --- Teste 1: Tarefa Crítica (Prioridade Máxima) ---
        task_prompt_1 = "Monitorar e reportar falha de segurança CRÍTICA no módulo XY."
        context_1 = self._create_context(task_prompt_1)

        initial_agent_1 = "Engenheiro_Agente" if self.mode == "SERVER" else "Sensor_Agente"
            
        CORTEX_LOGGER.info(f"[TESTE 1] Submetendo tarefa de **Prioridade Crítica** para {initial_agent_1}.")
        task_1 = self.scheduler.submit_task(
            task_prompt_1, 
            context_1, 
            priority=TaskPriority.CRITICAL, 
            initial_agent=initial_agent_1
        )
        
        # --- Teste 2: Tarefa Normal (Baixa Prioridade) ---
        task_prompt_2 = "Compilar relatório semanal de desempenho (Baixa Prioridade)."
        context_2 = self._create_context(task_prompt_2)
        
        CORTEX_LOGGER.info("[TESTE 2] Submetendo tarefa de **Baixa Prioridade** (Força Auto-Modulação).")
        task_2 = self.scheduler.submit_task(
            task_prompt_2, 
            context_2, 
            priority=TaskPriority.LOW, 
            initial_agent=None
        )

        # Permite que o Scheduler processe as tarefas
        time.sleep(2) 
        
        # Simula o encerramento seguro do sistema
        self.scheduler.stop()
        CORTEX_LOGGER.info("Scheduler Thread encerrada. Recuperando resultados para verificação.")

        # Recupera e exibe o resultado final das tarefas persistidas
        print("\n--- Resultados Persistidos (Verificação de Integridade) ---")
        
        final_task_1 = self.task_repository.find_by_id(task_1.task_id)
        final_task_2 = self.task_repository.find_by_id(task_2.task_id)

        self._display_task_summary(final_task_1)
        self._display_task_summary(final_task_2)
            
        print("----------------------------------------------------------")

    def _display_task_summary(self, task: Optional[Any]):
        """Exibe o resumo detalhado de uma Task, recuperada do Repositório."""
        if not task:
             print("Task não encontrada no Repositório.")
             return
             
        # Saída formatada no console para facilitar a leitura humana do teste
        print(f"\n### Resumo da Tarefa {task.task_id} (P:{task.priority.value}) ###")
        print(f"  Status Final: **{task.status.value}**")
        print(f"  Delegado Final: {task.delegated_to}")
        print(f"  Resultado Final: {str(task.final_result)[:60]}...")
        
        print("\n  Historico de Rastreamento (Trace):")
        for i, trace in enumerate(task.trace_history):
            status = trace.success and "SUCESSO" or "FALHA"
            print(f"    [{i+1}] {trace.agent_name} ({status}): {trace.action_description[:50]}...")
        
        
# --- 6. Execução de Teste ---
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
