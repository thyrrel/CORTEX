import threading
import queue
import time
import uuid
from typing import Optional, Dict, List
from .cerne import CERNE
from .dataclasses import Task, TaskStatus, TaskPriority, GlobalContext
from ..persistence.task_repository import TaskRepository # Importa o repositório formalizado
from ..utilities.logger import CORTEX_LOGGER # Importa o Logger Singleton

# --- Fila de Prioridade ---

class TaskQueue:
    """
    Fila de Prioridade que armazena Tasks. 
    Usa a prioridade da Task para determinar a ordem de processamento.
    """
    def __init__(self):
        # A fila armazena (prioridade invertida, tempo de criação, Task).
        self._queue = queue.PriorityQueue()
        CORTEX_LOGGER.info("TaskQueue inicializada.")

    def enqueue(self, task: Task):
        """Adiciona uma Task à fila com base em sua prioridade."""
        # Prioridade é invertida: valor mais alto (CRITICAL) tem a menor tupla para ser processado primeiro.
        priority_tuple = (-task.priority.value, task.creation_time, task)
        self._queue.put(priority_tuple)
        CORTEX_LOGGER.info(
            f"Task enfileirada. Prioridade: {task.priority.value}.",
            extra_data={'task_id': task.task_id, 'priority': task.priority.value}
        )

    def dequeue(self) -> Optional[Task]:
        """Remove e retorna a Task de maior prioridade."""
        try:
            _, _, task = self._queue.get_nowait()
            return task
        except queue.Empty:
            return None

    def is_empty(self):
        return self._queue.empty()

# --- O Scheduler Principal ---

class CERNEScheduler(threading.Thread):
    """
    Executa o CERNE em uma thread separada, processando tarefas da fila de forma assíncrona.
    Utiliza o TaskRepository para carregar e persistir o estado das Tasks.
    """
    # ATENÇÃO: O construtor foi ajustado para receber TaskRepository
    def __init__(self, cerne_instance: CERNE, task_repository: TaskRepository):
        super().__init__(name="CERNEScheduler-Thread")
        self._cerne = cerne_instance
        self._repository = task_repository
        self._task_queue = TaskQueue()
        self._running = False
        CORTEX_LOGGER.info("CERNEScheduler criado. Pronto para gerenciar execução assíncrona.")

    def run(self):
        """O Loop principal da Thread do Scheduler."""
        self._running = True
        CORTEX_LOGGER.info(f"Scheduler Thread '{self.name}' iniciada.")
        
        # 1. Recuperar tarefas pendentes da última sessão (Recuperação de estado)
        pending_tasks = self._repository.find_pending_tasks()
        for task in pending_tasks:
            self._task_queue.enqueue(task)
            CORTEX_LOGGER.warning(
                f"Tarefa pendente recuperada e re-enfileirada.",
                extra_data={'task_id': task.task_id, 'status': task.status.value}
            )
            
        while self._running:
            task = self._task_queue.dequeue()
            
            if task:
                CORTEX_LOGGER.info(f"Iniciando processamento da Task.", extra_data={'task_id': task.task_id})
                
                # O CERNE recebe a Task, processa e a retorna atualizada
                # Nota: Futuramente, este método deve ser 'resume_task' para continuar o trace.
                updated_task = self._cerne.processar_tarefa(
                    task.description, 
                    task.context, 
                    task.required_agent
                )
                
                # Persistir o resultado final usando o Repositório
                self._repository.save(updated_task)
                CORTEX_LOGGER.info(f"Task finalizada e estado persistido. Status: {updated_task.status.value}", extra_data={'task_id': task.task_id})
                
            else:
                # Aguarda um momento para evitar loop ativo
                time.sleep(0.5)

    def stop(self):
        """Sinaliza à thread para parar a execução e aguarda seu encerramento seguro."""
        CORTEX_LOGGER.warning(f"Sinal de parada recebido. Encerrando Scheduler Thread.")
        self._running = False
        self.join() 
        CORTEX_LOGGER.info(f"Scheduler Thread '{self.name}' encerrada.")

    def submit_task(self, raw_description: str, context: GlobalContext, priority: TaskPriority, initial_agent: Optional[str] = None) -> Task:
        """Recebe uma nova tarefa do CORTEX, cria o objeto Task e a submete à fila."""
        task_id = f"TASK-{uuid.uuid4().hex[:8]}"
        new_task = Task(
            task_id=task_id,
            description=raw_description,
            context=context,
            priority=priority,
            required_agent=initial_agent
        )
        # Persiste o estado inicial antes de enfileirar
        self._repository.save(new_task) 
        self._task_queue.enqueue(new_task)
        
        CORTEX_LOGGER.info(
            f"Tarefa submetida com sucesso. Aguardando processamento.",
            extra_data={'task_id': task_id, 'priority': priority.value}
        )
        return new_task
