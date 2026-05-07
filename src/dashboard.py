import tkinter as tk
from tkinter import ttk, messagebox
import cv2
from PIL import Image, ImageTk
import os
from datetime import datetime
from .config import CAMERA_ID, CAP_DIR
from .vision import VisionSystem
from .database import DatabaseManager

class InspectionApp:
    def __init__(self, window):
        self.window = window
        self.window.title("SISTEMA DE INSPEÇÃO INDUSTRIAL - MEDIDORES")
        self.window.geometry("1000x700")
        self.window.configure(bg="#2c3e50")

        self.db = DatabaseManager()
        self.vision = VisionSystem()
        
        if not self.vision.open_camera(CAMERA_ID):
            messagebox.showerror("Erro", "Não foi possível acessar a câmera.")

        self.setup_ui()
        self.update_webcam()

    def setup_ui(self):
        # Estilo Industrial
        style = ttk.Style()
        style.theme_use('clam')
        
        # Painel Superior
        top_frame = tk.Frame(self.window, bg="#34495e", height=100)
        top_frame.pack(fill=tk.X)
        
        tk.Label(top_frame, text="INSPEÇÃO DE LINHA DE PRODUÇÃO", font=("Arial", 20, "bold"), fg="white", bg="#34495e").pack(pady=20)

        # Conteúdo Principal
        main_frame = tk.Frame(self.window, bg="#2c3e50")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Lado Esquerdo: Câmera
        self.canvas_cam = tk.Canvas(main_frame, width=640, height=480, bg="black")
        self.canvas_cam.grid(row=0, column=0, rowspan=2)

        # Lado Direito: Controles e Resultado
        ctrl_frame = tk.Frame(main_frame, bg="#2c3e50")
        ctrl_frame.grid(row=0, column=1, padx=20, sticky="n")

        tk.Label(ctrl_frame, text="CÓDIGO DO MEDIDOR:", font=("Arial", 12), fg="white", bg="#2c3e50").pack(anchor="w")
        self.entry_codigo = tk.Entry(ctrl_frame, font=("Arial", 14), width=15)
        self.entry_codigo.pack(pady=5)
        
        self.btn_inspecionar = tk.Button(ctrl_frame, text="INSPECIONAR (TRIGGER)", font=("Arial", 12, "bold"), 
                                         bg="#27ae60", fg="white", height=2, width=20, command=self.trigger_inspection)
        self.btn_inspecionar.pack(pady=20)

        # Resultado
        self.lbl_status = tk.Label(ctrl_frame, text="AGUARDANDO", font=("Arial", 24, "bold"), bg="#2c3e50", fg="#bdc3c7")
        self.lbl_status.pack(pady=10)
        
        self.lbl_score = tk.Label(ctrl_frame, text="Score: ---", font=("Arial", 12), bg="#2c3e50", fg="white")
        self.lbl_score.pack()

    def update_webcam(self):
        frame = self.vision.capture_frame()
        if frame is not None:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame = cv2.resize(frame, (640, 480))
            self.photo = ImageTk.PhotoImage(image=Image.fromarray(frame))
            self.canvas_cam.create_image(0, 0, image=self.photo, anchor=tk.NW)
        self.window.after(10, self.update_webcam)

    def trigger_inspection(self):
        codigo = self.entry_codigo.get().strip()
        if not codigo:
            messagebox.showwarning("Aviso", "Insira o código do medidor.")
            return

        caminho_ref = self.db.consultar_gabarito(codigo)
        if not caminho_ref:
            messagebox.showerror("Erro", f"Código {codigo} não cadastrado ou sem desenho de referência.")
            return

        frame = self.vision.capture_frame()
        if frame is None:
            return

        try:
            status, score, loc = self.vision.compare_images(frame, caminho_ref)
            
            # Salvar imagem da inspeção
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"inspecao_{codigo}_{timestamp}.jpg"
            save_path = os.path.join(CAP_DIR, filename)
            cv2.imwrite(save_path, frame)

            # Salvar no Banco
            self.db.salvar_inspecao(codigo, status, score, save_path)

            # Atualizar UI
            self.lbl_status.config(text=status)
            self.lbl_score.config(text=f"Score: {score:.4f}")
            
            colors = {"CORRETO": "#2ecc71", "ERRADO": "#e74c3c", "SEM CONFIANÇA": "#f1c40f"}
            self.lbl_status.config(fg=colors.get(status, "white"))

        except Exception as e:
            messagebox.showerror("Erro de Processamento", str(e))
