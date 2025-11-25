from typing import Optional, List, Dict
from ..core.dataclasses import Task, TaskStatus, TaskPriority, GlobalContext, ExecutionTrace
from .db_models import TaskDBModel, TraceDBModel
import json

class TaskRepository:
    """
    Abstrai a comunicação com o Banco de Dados.
    Responsável por converter entre os objetos de domínio (core.Task) e os modelos de persistência (db_models).
    """
    
    def __init__(self):
        # Simulação de um banco de dados persistente
        self._db_session: Dict[str, TaskDBModel] = {}
        print("TaskRepository inicializado (Simulação de DB em memória).")

    def _to_core_task(self, db_model: TaskDBModel) -> Task:
        """Converte um DBModel de volta para um objeto de domínio Task completo."""
        
        # Desserializa o Contexto
        context_data = json.loads(db_model.context_json)
        context = GlobalContext(
            session_id=context_data['session_id'],
            cortex_mode=context_data['cortex_mode'],
            initial_prompt=context_data['initial_prompt'],
            environment_vars=context_data['environment_vars']
        )
        
        # Desserializa o Histórico de Rastreamento (Trace)
        trace_db_data = json.loads(db_model.trace_history_json)
        trace_history = []
        for t_data in trace_db_data:
            trace = ExecutionTrace(
                timestamp=t_data['timestamp'],
                agent_name=t_data['agent_name'],
                action_description=t_data['action_description'],
                success=t_data['success'],
                # Desserializa o dado complexo dentro do Trace
                result_data=json.loads(t_data['result_data_json'])
            )
            trace_history.append(trace)

        # Cria e popula o objeto Task
        task = Task(
            task_id=db_model.task_id,
            description=db_model.description,
            context=context,
            status=TaskStatus(db_model.status),
            priority=TaskPriority(db_model.priority),
            required_agent=db_model.required_agent,
            delegated_to=db_model.delegated_to,
            creation_time=db_model.creation_time,
            last_update_time=db_model.last_update_time,
            trace_history=trace_history,
            final_result=json.loads(db_model.final_result_json) if db_model.final_result_json else None
        )
        return task

    def save(self, task: Task):
        """Converte a Task para DBModel e salva."""
        db_model = TaskDBModel.from_core(task)
        self._db_session[task.task_id] = db_model
        # print(f"Repository: Task {task.task_id} persistida.")

    def find_by_id(self, task_id: str) -> Optional[Task]:
        """Carrega o DBModel e converte de volta para Task."""
        db_model = self._db_session.get(task_id)
        if db_model:
            return self._to_core_task(db_model)
        return None

    def find_pending_tasks(self) -> List[Task]:
        """Encontra tarefas com status que requerem processamento ou recuperação."""
        pending_statuses = [TaskStatus.PENDING.value, TaskStatus.DELEGATED.value, TaskStatus.IN_PROGRESS.value]
        
        pending_db_models = [
            t for t in self._db_session.values() 
            if t.status in pending_statuses
        ]
        
        return [self._to_core_task(t) for t in pending_db_models]
