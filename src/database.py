import sqlite3
import pandas as pd
from .config import DB_PATH

class DatabaseManager:
    def __init__(self):
        self.db_path = DB_PATH

    def get_connection(self):
        return sqlite3.connect(self.db_path)

    def cadastrar_medidor(self, codigo, modelo):
        try:
            with self.get_connection() as conn:
                conn.execute("INSERT INTO medidores (codigo, modelo) VALUES (?, ?)", (codigo, modelo))
        except sqlite3.IntegrityError:
            print(f"Erro: Medidor {codigo} já cadastrado.")

    def cadastrar_desenho(self, medidor_codigo, nome_desenho, caminho_ref):
        with self.get_connection() as conn:
            conn.execute("INSERT INTO desenhos_esperados (medidor_codigo, nome_desenho, caminho_referencia) VALUES (?, ?, ?)", 
                         (medidor_codigo, nome_desenho, caminho_ref))

    def consultar_gabarito(self, medidor_codigo):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT caminho_referencia FROM desenhos_esperados WHERE medidor_codigo = ?", (medidor_codigo,))
            result = cursor.fetchone()
            return result[0] if result else None

    def salvar_inspecao(self, medidor_codigo, resultado, score, caminho_cap):
        with self.get_connection() as conn:
            conn.execute("INSERT INTO inspecoes (medidor_codigo, resultado, score, caminho_captura) VALUES (?, ?, ?, ?)", 
                         (medidor_codigo, resultado, score, caminho_cap))

    def importar_planilha(self, excel_path):
        df = pd.read_excel(excel_path)
        # Lógica para iterar e salvar no banco
        return df
