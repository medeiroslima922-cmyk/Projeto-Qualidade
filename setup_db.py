import sqlite3
from src.config import DB_PATH

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Tabela de Medidores
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS medidores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            codigo TEXT UNIQUE NOT NULL,
            modelo TEXT,
            data_cadastro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Tabela de Desenhos Esperados (Gabaritos)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS desenhos_esperados (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            medidor_codigo TEXT NOT NULL,
            nome_desenho TEXT NOT NULL,
            caminho_referencia TEXT NOT NULL,
            FOREIGN KEY (medidor_codigo) REFERENCES medidores (codigo)
        )
    ''')

    # Tabela de Inspeções Realizadas
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS inspecoes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            medidor_codigo TEXT NOT NULL,
            data_hora TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            resultado TEXT NOT NULL, -- CORRETO, ERRADO, SEM CONFIANÇA
            score REAL,
            caminho_captura TEXT,
            FOREIGN KEY (medidor_codigo) REFERENCES medidores (codigo)
        )
    ''')

    conn.commit()
    conn.close()
    print(f"Banco de dados inicializado em: {DB_PATH}")

if __name__ == "__main__":
    init_db()
