import pandas as pd
from src.database import DatabaseManager
import os

def popular_exemplo():
    db = DatabaseManager()
    
    # Cadastrando um medidor de teste
    print("Cadastrando medidores de teste...")
    db.cadastrar_medidor("MED-001", "Monofásico Digital")
    db.cadastrar_medidor("MED-002", "Trifásico Industrial")
    
    # Associando desenhos
    # Atenção: caminho deve ser relativo à raiz do projeto ou absoluto conforme config.py
    db.cadastrar_desenho("MED-001", "Logo Principal", "referencias/logo_padrao.png")
    
    print("Cadastro inicial concluído.")

if __name__ == "__main__":
    popular_exemplo()
