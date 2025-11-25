# db_setup_action.py (ADICIONAR NA RAIZ)

import os, sys, mysql.connector
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
    try:
        if not all(os.environ.get(v) for v in ["DB_HOST", "DB_USER", "DB_PASS", "DB_NAME", "DB_PORT"]):
            raise ValueError("ERRO DE CONFIGURAÇÃO: Secrets de DB ausentes ou incompletos.")

        conn = mysql.connector.connect(
            host=os.environ.get("DB_HOST"),
            user=os.environ.get("DB_USER"),
            password=os.environ.get("DB_PASS"),
            database=os.environ.get("DB_NAME"),
            port=int(os.environ.get("DB_PORT")),
            ssl_mode="REQUIRED"
        )
        cursor = conn.cursor()
        cursor.execute(CREATE_TABLE_SQL)
        conn.commit()
        print("✅ SUCESSO! Tabela 'Tasks' criada ou já existente.")
    except Exception as err:
        print(f"🛑 ERRO: {err}")
        sys.exit(1)

if __name__ == "__main__":
    setup_database()
    
