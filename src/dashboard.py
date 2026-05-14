import tkinter as tk
from tkinter import ttk, messagebox
import cv2
from PIL import Image, ImageTk
import os
from datetime import datetime
from .config import CAMERA_ID, CAP_DIR, ZONA_SERIAL, ZONA_INMETRO, ZONA_ELETRA, ZONA_ID, ZONA_ENERGISA, REF_DIR
from .vision import VisionSystem
from .database import DatabaseManager
import time

class InspectionApp:
    def __init__(self, window):
        self.window = window
        self.window.title("SISTEMA DE INSPEÇÃO INDUSTRIAL - MEDIDORES")
        self.window.geometry("1000x700")
        self.window.configure(bg="#2c3e50")

        self.db = DatabaseManager()
        self.vision = VisionSystem()
        
        # Variáveis para automação
        self.ultimo_frame_cinza = None
        self.tempo_estabilizado = 0
        self.bloqueio_leitura = False
        self.pausado = False
        
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
        
        self.btn_inspecionar = tk.Button(ctrl_frame, text="INSPECIONAR (MANUAL)", font=("Arial", 12, "bold"), 
                                         bg="#27ae60", fg="white", height=1, width=20, command=self.trigger_inspection)
        self.btn_inspecionar.pack(pady=10)

        self.btn_calibrar = tk.Button(ctrl_frame, text="CALIBRAR REFERÊNCIAS", font=("Arial", 10, "bold"), 
                                       bg="#2980b9", fg="white", height=1, width=20, command=self.calibrate)
        self.btn_calibrar.pack(pady=5)

        # Resultado Detalhado
        self.res_frame = tk.LabelFrame(ctrl_frame, text=" STATUS POR PONTO ", font=("Arial", 10, "bold"), fg="white", bg="#2c3e50")
        self.res_frame.pack(pady=10, fill=tk.X)

        self.pontos_ui = {}
        for p in ["INMETRO", "ELETRA", "SERIAL", "ID", "ENERGISA"]:
            f = tk.Frame(self.res_frame, bg="#2c3e50")
            f.pack(fill=tk.X, padx=5, pady=2)
            tk.Label(f, text=f"{p}:", font=("Arial", 10), fg="white", bg="#2c3e50").pack(side=tk.LEFT)
            lbl = tk.Label(f, text="---", font=("Arial", 10, "bold"), fg="#bdc3c7", bg="#2c3e50")
            lbl.pack(side=tk.RIGHT)
            self.pontos_ui[p] = lbl

        self.lbl_status = tk.Label(ctrl_frame, text="MONITORANDO", font=("Arial", 20, "bold"), bg="#2c3e50", fg="#f1c40f")
        self.lbl_status.pack(pady=10)

    def update_webcam(self):
        frame = self.vision.capture_frame()
        if frame is not None:
            display_frame = frame.copy()
            
            # Lógica Automática de Esteira
            if not self.pausado:
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                gray = cv2.GaussianBlur(gray, (21, 21), 0)

                if self.ultimo_frame_cinza is not None:
                    diff = cv2.absdiff(self.ultimo_frame_cinza, gray)
                    _, thresh = cv2.threshold(diff, 25, 255, cv2.THRESH_BINARY)
                    movimento = cv2.countNonZero(thresh)

                    if movimento < 3000: # Medidor Parado
                        if not self.bloqueio_leitura:
                            self.tempo_estabilizado += 1
                        
                        if self.tempo_estabilizado > 15 and not self.bloqueio_leitura:
                            self.lbl_status.config(text="INSPECIONANDO...", fg="#3498db")
                            self.window.update()
                            self.auto_inspect(frame)
                            self.bloqueio_leitura = True
                            self.tempo_estabilizado = 0
                    else: # Medidor em Movimento
                        self.tempo_estabilizado = 0
                        self.bloqueio_leitura = False
                        self.lbl_status.config(text="MONITORANDO...", fg="#f1c40f")

                self.ultimo_frame_cinza = gray

            # Desenhar ROIs na tela
            for p, zona in [("INMETRO", ZONA_INMETRO), ("ELETRA", ZONA_ELETRA), ("SERIAL", ZONA_SERIAL)]:
                cv2.rectangle(display_frame, (zona[0], zona[1]), (zona[0]+zona[2], zona[1]+zona[3]), (255, 255, 255), 1)

            rgb_frame = cv2.cvtColor(display_frame, cv2.COLOR_BGR2RGB)
            rgb_frame = cv2.resize(rgb_frame, (640, 480))
            self.photo = ImageTk.PhotoImage(image=Image.fromarray(rgb_frame))
            self.canvas_cam.create_image(0, 0, image=self.photo, anchor=tk.NW)
            
        self.window.after(10, self.update_webcam)

    def auto_inspect(self, frame):
        try:
            # 1. VERIFICAR LOGOS
            res_i, _, _ = self.vision.compare_images(frame, "referencias/inmetro.png", roi=ZONA_INMETRO)
            res_el, _, _ = self.vision.compare_images(frame, "referencias/eletra.png", roi=ZONA_ELETRA)
            
            # 2. LER NÚMEROS
            serial = self.vision.ler_numero_serie(frame, roi=ZONA_SERIAL)
            id_med = self.vision.ler_numero_serie(frame, roi=ZONA_ID)

            # Atualizar UI Lateral
            self.pontos_ui["INMETRO"].config(text=res_i, fg="#2ecc71" if res_i == "CORRETO" else "#e74c3c")
            self.pontos_ui["ELETRA"].config(text=res_el, fg="#2ecc71" if res_el == "CORRETO" else "#e74c3c")
            self.pontos_ui["SERIAL"].config(text=serial[:10], fg="white")
            self.pontos_ui["ID"].config(text=id_med[:10], fg="white")

            # Decisão Final
            if res_i == "CORRETO" and res_el == "CORRETO" and len(serial) > 5:
                status = "APROVADO"
                cor = "#2ecc71"
            else:
                status = "REPROVADO"
                cor = "#e74c3c"

            self.lbl_status.config(text=status, fg=cor)
            
            # Salvar no Banco e Imagem
            ts = datetime.now().strftime("%Y%m%d_%H%M%S")
            path = os.path.join(CAP_DIR, f"auto_{serial}_{ts}.jpg")
            cv2.imwrite(path, frame)
            self.db.salvar_inspecao(serial, status, 0.9, path)

        except Exception as e:
            print(f"Erro na inspeção: {e}")

    def calibrate(self):
        frame = self.vision.capture_frame()
        if frame is None: return
        
        try:
            zonas = {
                "inmetro.png": ZONA_INMETRO,
                "eletra.png": ZONA_ELETRA,
                "energisa.png": ZONA_ENERGISA
            }
            for nome, zona in zonas.items():
                x, y, w, h = zona
                crop = frame[y:y+h, x:x+w]
                cv2.imwrite(os.path.join(REF_DIR, nome), crop)
            
            messagebox.showinfo("Sucesso", "Referências calibradas com sucesso! A inspeção automática agora pode iniciar.")
        except Exception as e:
            messagebox.showerror("Erro", f"Falha na calibração: {e}")

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
