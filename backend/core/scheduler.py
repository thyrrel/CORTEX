import threading
import queue
import time
import uuid
from typing import Optional, Dict, List
from .cerne import CERNE
from .dataclasses import Task, TaskStatus, TaskPriority, GlobalContext

# --- 1. Camada de Persistência (Placeholder) ---

class TaskPersister:
    """
    Simulação de um mecanismo de persistência (Ex: Banco de Dados/Cache).
    Responsável por salvar e carregar o estado completo da Task.
    """
    def __init__(self):
        # Em um sistema real, aqui se conectaria ao DB (SQLite, Redis, etc.)
        self._storage: Dict[str, Task] = {} 
        print("TaskPersister inicializado (Memória Volátil).")

    def save_task(self, task: Task):
        """Salva ou atualiza uma Task na persistência."""
        # Note: Dataclasses são serializáveis, mas aqui salvamos o objeto diretamente.
        self._storage[task.task_id] = task
        # print(f"Persisted: {task.task_id} | Status: {task.status.value}")

    def load_task(self, task_id: str) -> Optional[Task]:
        """Carrega uma Task pelo ID."""
        return self._storage.get(task_id)

    def load_pending_tasks(self) -> List[Task]:
        """Carrega todas as tarefas que não foram concluídas/falhadas/canceladas."""
        return [
            t for t in self._storage.values() 
            if t.status in [TaskStatus.PENDING, TaskStatus.DELEGATED, TaskStatus.IN_PROGRESS]
        ]
        
# --- 2. Fila de Prioridade ---

class TaskQueue:
    """
    Fila de Prioridade que armazena Tasks. 
    Usa a prioridade da Task para determinar a ordem de processamento.
    """
    def __init__(self):
        # A fila armazena (prioridade, tempo de criação, Task). 
        # O tempo de criação serve como desempate (FIFO para mesma prioridade).
        self._queue = queue.PriorityQueue()

    def enqueue(self, task: Task):
        """Adiciona uma Task à fila com base em sua prioridade."""
        # Prioridade é invertida: valor mais alto (CRITICAL) deve ter prioridade mais baixa na tupla.
        priority_tuple = (-task.priority.value, task.creation_time, task)
        self._queue.put(priority_tuple)
        print(f"Task {task.task_id} enfileirada. Prioridade: {task.priority.value}.")

    def dequeue(self) -> Optional[Task]:
        """Remove e retorna a Task de maior prioridade."""
        try:
            # Retorna apenas o objeto Task (último elemento da tupla)
            _, _, task = self._queue.get_nowait()
            return task
        except queue.Empty:
            return None

    def is_empty(self):
        return self._queue.empty()

# --- 3. O Scheduler Principal ---

class CERNEScheduler(threading.Thread):
    """
    Executa o CERNE em uma thread separada, processando tarefas da fila de forma assíncrona.
    """
    def __init__(self, cerne_instance: CERNE, persister: TaskPersister):
        super().__init__(name="CERNEScheduler-Thread")
        self._cerne = cerne_instance
        self._persister = persister
        self._task_queue = TaskQueue()
        self._running = False
        print("CERNEScheduler criado. Pronto para gerenciar a execução assíncrona.")

    def run(self):
        """O Loop principal da Thread do Scheduler."""
        self._running = True
        print(f"Scheduler Thread '{self.name}' iniciada.")
        
        # 1. Recuperar tarefas pendentes da última sessão (Simulação de "Hot Reload")
        pending_tasks = self._persister.load_pending_tasks()
        for task in pending_tasks:
            self._task_queue.enqueue(task)
            
        while self._running:
            task = self._task_queue.dequeue()
            
            if task:
                # Processamento da Task: O CERNE assume o controle
                print(f"\n[Scheduler] Processando Task {task.task_id}...")
                
                # O CERNE recebe a Task, processa e a retorna atualizada
                # O processar_tarefa deve ser adaptado para receber uma Task existente
                
                # Adaptação temporária: Forçamos o CERNE a re-processar o prompt original
                # Em um sistema real, haveria um método 'resume_task'
                updated_task = self._cerne.processar_tarefa(
                    task.description, 
                    task.context, 
                    task.required_agent
                )
                
                # Persistir o resultado final
                self._persister.save_task(updated_task)
                
            else:
                # Aguarda um momento antes de verificar a fila novamente
                time.sleep(0.5)

    def stop(self):
        """Sinaliza à thread para parar a execução."""
        self._running = False
        self.join() # Espera a thread terminar
        print(f"Scheduler Thread '{self.name}' encerrada.")

    def submit_task(self, raw_description: str, context: GlobalContext, priority: TaskPriority, initial_agent: Optional[str] = None):
        """Recebe uma nova tarefa do CORTEX, cria o objeto Task e a submete à fila."""
        task_id = f"TASK-{uuid.uuid4().hex[:8]}"
        new_task = Task(
            task_id=task_id,
            description=raw_description,
            context=context,
            priority=priority,
            required_agent=initial_agent
        )
        self._persister.save_task(new_task) # Persiste o estado inicial
        self._task_queue.enqueue(new_task)
        return new_task

