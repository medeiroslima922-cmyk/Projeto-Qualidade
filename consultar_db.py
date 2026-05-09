import sqlite3
import pandas as pd
from src.config import DB_PATH

def ver_dados():
    try:
        # Conecta ao banco de dados
        conn = sqlite3.connect(DB_PATH)
        
        print("\n" + "="*50)
        print("   RELATÓRIO DO BANCO DE DADOS (INSPEÇÃO)")
        print("="*50)

        # Ver Inspeções
        print("\n--- ÚLTIMAS INSPEÇÕES ---")
        df_inspecoes = pd.read_sql_query("SELECT id, medidor_codigo, data_hora, resultado, score FROM inspecoes ORDER BY data_hora DESC LIMIT 10", conn)
        if df_inspecoes.empty:
            print("Nenhuma inspeção registrada no histórico.")
        else:
            print(df_inspecoes.to_string(index=False))

        # Ver Medidores
        print("\n--- MEDIDORES NO CADASTRO ---")
        df_medidores = pd.read_sql_query("SELECT codigo, modelo FROM medidores", conn)
        if df_medidores.empty:
            print("Nenhum medidor cadastrado.")
        else:
            print(df_medidores.to_string(index=False))

        conn.close()
        print("\n" + "="*50)
        
    except Exception as e:
        print(f"Erro ao acessar o banco de dados: {e}")

if __name__ == "__main__":
    ver_dados()
