# db_setup.py (Adicionar na raiz do repositório)

import os
import sys
import mysql.connector

# O comando SQL para criar a tabela Tasks
CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS Tasks (
    task_id VARCHAR(36) PRIMARY KEY,
    content TEXT NOT NULL,
    status VARCHAR(10) NOT NULL DEFAULT 'PENDING',
    priority VARCHAR(10) NOT NULL DEFAULT 'MEDIUM',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);
"""

def setup_database():
    """Conecta ao MySQL e executa o comando CREATE TABLE."""
    try:
        # Pega as credenciais diretamente do ambiente do Actions
        conn = mysql.connector.connect(
            host=os.environ.get("DB_HOST"),
            user=os.environ.get("DB_USER"),
            password=os.environ.get("DB_PASS"),
            database=os.environ.get("DB_NAME"),
            port=int(os.environ.get("DB_PORT")),
            ssl_mode="REQUIRED" # Essencial para Aiven
        )
        cursor = conn.cursor()
        
        # Executa o comando DDL
        cursor.execute(CREATE_TABLE_SQL)
        conn.commit()
        
        print("✅ SUCESSO! Tabela 'Tasks' criada ou já existente.")
        
    except mysql.connector.Error as err:
        print(f"🛑 ERRO AO CONFIGURAR O BANCO DE DADOS: {err}")
        print("Verifique se as credenciais estão corretas.")
        sys.exit(1) # Força a falha do workflow em caso de erro

if __name__ == "__main__":
    # Garante que todas as variáveis necessárias estão presentes
    if not all(os.environ.get(v) for v in ["DB_HOST", "DB_USER", "DB_PASS", "DB_NAME", "DB_PORT"]):
        print("ERRO DE CONFIGURAÇÃO: Secrets ausentes no ambiente do Actions.")
        sys.exit(1)
        
    setup_database()
