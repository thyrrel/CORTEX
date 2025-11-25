# db_setup_action.py (ADICIONAR NA RAIZ)

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

# Função que executa o setup DDL
def setup_database():
    """Conecta ao MySQL e executa o comando CREATE TABLE."""
    try:
        # Garante que as variáveis de ambiente necessárias para a conexão real estão presentes
        if not all(os.environ.get(v) for v in ["DB_HOST", "DB_USER", "DB_PASS", "DB_NAME", "DB_PORT"]):
            raise ValueError("ERRO DE CONFIGURAÇÃO: Secrets de DB ausentes ou incompletos.")

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
        
    except ValueError as ve:
        print(f"🛑 ERRO DE VALIDAÇÃO: {ve}")
        sys.exit(1)
    except mysql.connector.Error as err:
        print(f"🛑 ERRO AO CONFIGURAR O BANCO DE DADOS (MySQL): {err}")
        sys.exit(1)

if __name__ == "__main__":
    setup_database()
