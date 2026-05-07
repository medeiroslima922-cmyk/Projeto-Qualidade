import tkinter as tk
from src.dashboard import InspectionApp
import os

def main():
    # Garantir que o banco existe
    if not os.path.exists("data/inspecao.db"):
        print("Banco não encontrado. Inicializando...")
        from setup_db import init_db
        init_db()

    root = tk.Tk()
    app = InspectionApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
