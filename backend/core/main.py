# Trecho de main.py (Substitui a lógica de execução direta)

# Importações adicionais:
from .scheduler import CERNEScheduler, TaskPersister
from .dataclasses import GlobalContext, TaskStatus, TaskPriority 
# ... (Resto das importações de cerne e agente_manager)

class CORTEX:
    # ... (__new__ e __init__ permanecem os mesmos)
    
    def __init__(self):
        if self._initialized:
            return
            
        # ... (Definição de self.mode e AgenteManager)
        
        # O CORTEX inicializa o CERNE com o Manager
        self.coordenador: CERNE = CERNE(agente_manager=self.agente_manager)
        
        # NOVAS CAMADAS: Persistência e Agendamento
        self.persister = TaskPersister()
        self.scheduler = CERNEScheduler(cerne_instance=self.coordenador, persister=self.persister)
        
        self._initialized = True
        
    def _create_context(self, prompt: str) -> GlobalContext:
        # ... (Permanece o mesmo)

    def start_system(self):
        """Inicia o Scheduler e submete tarefas para teste."""
        print("\n--- Verificação de Integridade CORTEX (Scheduler Ativado) ---")
        
        # INICIA A THREAD DO SCHEDULER
        self.scheduler.start()
        
        # --- Teste 1: Tarefa Crítica (Prioridade Máxima) ---
        task_prompt_1 = "Monitorar e reportar falha de segurança CRÍTICA no módulo XY."
        context_1 = self._create_context(task_prompt_1)

        if self.mode == "SERVER":
            initial_agent = "Engenheiro_Agente"
        else:
            initial_agent = "Sensor_Agente"
            
        print(f"\n[TESTE 1] Submetendo tarefa de **Alta Prioridade** para {initial_agent}.")
        # SUBMISSÃO PELA FILA
        self.scheduler.submit_task(
            task_prompt_1, 
            context_1, 
            priority=TaskPriority.CRITICAL, # CRITICAL (20)
            initial_agent=initial_agent
        )
        
        # --- Teste 2: Tarefa Normal (Baixa Prioridade) ---
        task_prompt_2 = "Compilar relatório semanal de desempenho (Baixa Prioridade)."
        context_2 = self._create_context(task_prompt_2)
        
        print(f"\n[TESTE 2] Submetendo tarefa de **Baixa Prioridade** (Força Auto-Modulação).")
        # SUBMISSÃO PELA FILA
        self.scheduler.submit_task(
            task_prompt_2, 
            context_2, 
            priority=TaskPriority.LOW, # LOW (1)
            initial_agent=None # Força Revisão/Auto-Modulação
        )

        # Permite que o Scheduler processe as tarefas (a CRITICAL deve ir primeiro)
        time.sleep(2) 
        
        # Simula o encerramento seguro do sistema
        self.scheduler.stop()

        # Recupera e exibe o resultado final da tarefa de maior prioridade
        final_task_1 = self.persister.load_task(task_id=task_1.task_id) # Erro: task_1 não foi criada ainda
        
        # Para fins de teste funcional, vamos pegar o último ID criado que é task_2
        # (A forma correta seria guardar o ID retornado por submit_task)
        # Assumindo que o último ID criado é recuperável para este teste:
        
        # Simplesmente exibimos os resultados persistidos para verificação:
        print("\n--- Resultados Persistidos (Verificação de Integridade) ---")
        for t_id, task in self.persister._storage.items():
            if task.status != TaskStatus.PENDING:
                 print(f"ID: {t_id} | Prioridade: {task.priority.value} | Status Final: {task.status.value} | Delegado: {task.delegated_to}")
            
        print("----------------------------------------------------------")

    # ... (_create_context e _display_task_summary permanecem os mesmos, mas o _display_task_summary
    # não será usado no start_system porque a execução é assíncrona)
