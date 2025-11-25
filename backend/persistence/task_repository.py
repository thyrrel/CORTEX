# backend/persistence/task_repository.py
import mysql.connector
from mysql.connector import Error
import json
from typing import Optional, Dict
from ..core.dataclasses import Task, TaskStatus, ExecutionTrace # Importa a Task de domínio
from ..utilities.logger import CORTEX_LOGGER

# Nota: TaskDBModel e TraceDBModel seriam definidos em db_models.py,
# mas para fins de demonstração, vamos simplificar a persistência direta.

class TaskRepository:
    """Implementação real de persistência usando MySQL."""
    
    def __init__(self, db_config: Dict[str, str]):
        self._db_config = db_config 
        self._conn = None
        self._initialize_connection()
        
    def _initialize_connection(self):
        """Estabelece a conexão e cria as tabelas necessárias."""
        try:
            # Tenta conectar, ignorando o erro inicial se o DB não existir
            self._conn = mysql.connector.connect(**self._db_config)
            
            if self._conn.is_connected():
                CORTEX_LOGGER.info("TaskRepository: Conexão MySQL estabelecida com sucesso.")
                self._ensure_tables()
            else:
                raise Error("Não foi possível conectar ao MySQL.")
                
        except Error as e:
            CORTEX_LOGGER.critical(f"Falha ao conectar/inicializar MySQL. Usando modo 'NO_PERSISTENCE'. Erro: {e}")
            # Em caso de falha, poderíamos retornar a um TaskRepository em memória aqui.
            self._conn = None # Força o modo de falha para que save/load falhem
            
    def _ensure_tables(self):
        """Cria as tabelas Tasks e ExecutionTraces."""
        cursor = self._conn.cursor()
        
        # Tabela para armazenar as Tasks principais
        tasks_table = """
        CREATE TABLE IF NOT EXISTS Tasks (
            task_id VARCHAR(15) PRIMARY KEY,
            status VARCHAR(20),
            priority VARCHAR(10),
            delegated_to VARCHAR(50),
            description TEXT,
            final_result JSON,
            context_json JSON
        )
        """
        # Tabela para armazenar o histórico de ExecutionTrace (separado por performance)
        traces_table = """
        CREATE TABLE IF NOT EXISTS ExecutionTraces (
            trace_id INT AUTO_INCREMENT PRIMARY KEY,
            task_id VARCHAR(15),
            agent_name VARCHAR(50),
            action_description TEXT,
            timestamp DATETIME,
            success BOOLEAN,
            result_data JSON,
            FOREIGN KEY (task_id) REFERENCES Tasks(task_id)
        )
        """
        cursor.execute(tasks_table)
        cursor.execute(traces_table)
        self._conn.commit()
        cursor.close()

    def save_task(self, task: Task):
        """Persiste o estado da Task e seus Traces no banco."""
        if not self._conn:
            return
            
        cursor = self._conn.cursor()
        
        # 1. Serializa a Task para JSON para inserção/atualização
        try:
            final_result_json = json.dumps(task.final_result)
        except TypeError:
            final_result_json = json.dumps(str(task.final_result)) # Trata objetos não serializáveis

        context_json = json.dumps(task.context.__dict__)

        # Verifica se a task existe
        cursor.execute("SELECT task_id FROM Tasks WHERE task_id = %s", (task.task_id,))
        exists = cursor.fetchone()

        if exists:
            # UPDATE
            query = """
            UPDATE Tasks SET status=%s, priority=%s, delegated_to=%s, description=%s, 
            final_result=%s, context_json=%s WHERE task_id=%s
            """
            cursor.execute(query, (
                task.status.value, task.priority.value, task.delegated_to, task.description, 
                final_result_json, context_json, task.task_id
            ))
        else:
            # INSERT
            query = """
            INSERT INTO Tasks (task_id, status, priority, delegated_to, description, final_result, context_json) 
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(query, (
                task.task_id, task.status.value, task.priority.value, task.delegated_to, task.description, 
                final_result_json, context_json
            ))
        
        # 2. Persiste os Traces (Simplificado: remove e insere todos para garantir coerência)
        # Numa aplicação de produção, apenas novos traces seriam inseridos.
        cursor.execute("DELETE FROM ExecutionTraces WHERE task_id = %s", (task.task_id,))
        
        trace_query = """
        INSERT INTO ExecutionTraces (task_id, agent_name, action_description, timestamp, success, result_data)
        VALUES (%s, %s, %s, NOW(), %s, %s)
        """
        for trace in task.trace_history:
            cursor.execute(trace_query, (
                task.task_id, trace.agent_name, trace.action_description, trace.success, json.dumps(trace.result_data)
            ))
        
        self._conn.commit()
        cursor.close()
        
    def load_task(self, task_id: str) -> Optional[Task]:
        """Carrega uma Task do banco, incluindo seu histórico de Traces."""
        if not self._conn:
            return None
            
        cursor = self._conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM Tasks WHERE task_id = %s", (task_id,))
        task_data = cursor.fetchone()
        
        if not task_data:
            cursor.close()
            return None
            
        # Carrega Traces
        cursor.execute("SELECT * FROM ExecutionTraces WHERE task_id = %s ORDER BY timestamp ASC", (task_id,))
        trace_data = cursor.fetchall()
        
        cursor.close()
        
        # Reconstrói os objetos de domínio
        trace_history = [
            ExecutionTrace(
                agent_name=t['agent_name'],
                action_description=t['action_description'],
                success=t['success'],
                # O result_data é lido como string JSON e precisa ser desserializado
                result_data=json.loads(t['result_data']) if isinstance(t['result_data'], str) else t['result_data'],
            ) for t in trace_data
        ]
        
        # NOTA: A reconstrução do GlobalContext é complexa e dependeria de um modelo de dados mais claro,
        # mas usamos a string JSON salva para a reconstrução (Simplificado).
        
        task = Task(
            task_id=task_data['task_id'],
            description=task_data['description'],
            status=TaskStatus(task_data['status']),
            priority=task_data['priority'],
            delegated_to=task_data['delegated_to'],
            final_result=json.loads(task_data['final_result']) if isinstance(task_data['final_result'], str) else task_data['final_result'],
            context=json.loads(task_data['context_json']), # Aqui precisaríamos converter o JSON de volta para GlobalContext
            trace_history=trace_history
        )
        return task
    
    # ... (outros métodos como find_by_id)
