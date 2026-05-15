import cv2
import time
from src.vision import VisionSystem
from src.database import DatabaseManager
from src.config import ZONA_SERIAL, ZONA_INMETRO, ZONA_ELETRA, ZONA_ID, ZONA_BARCODE, ZONA_ENERGISA, ZONA_TERMINAIS, CAP_DIR
import os

def rodar_esteira_automatica():
    vision = VisionSystem()
    db = DatabaseManager()
    if not vision.open_camera(0): 
        print("Erro ao abrir a câmera.")
        return

    print("="*50)
    
    # Pegar resolução real
    frame_teste = vision.capture_frame()
    if frame_teste is not None:
        h, w = frame_teste.shape[:2]
        print(f"   Resolução Detectada: {w}x{h}")
    else:
        print("   Erro ao capturar frame de teste.")


    ultimo_frame_cinza = None
    tempo_estabilizado = 0
    medidor_em_posicao = False
    bloqueio_leitura = False
    pausado = False
    
    # CONTADORES DE PRODUÇÃO
    cont_ok = 0
    cont_erro = 0

    while True:
        frame = vision.capture_frame()
        if frame is None: break
        
        display_frame = frame.copy()
        h, w, _ = frame.shape

        # DESENHAR PAINEL DE PRODUÇÃO NO TOPO
        cv2.rectangle(display_frame, (0, 0), (w, 60), (50, 50, 50), -1) # Fundo escuro
        cv2.putText(display_frame, f"OK: {cont_ok}", (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
        cv2.putText(display_frame, f"ERRO: {cont_erro}", (150, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
        cv2.putText(display_frame, f"TOTAL: {cont_ok + cont_erro}", (300, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
        
        if pausado:
            cv2.putText(display_frame, "SISTEMA PAUSADO", (w//4, h//2), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 165, 255), 3)
            cv2.putText(display_frame, "Pressione 'P' para Retomar", (w//4, h//2 + 50), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 165, 255), 2)
        else:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            gray = cv2.GaussianBlur(gray, (21, 21), 0)

            if ultimo_frame_cinza is None:
                ultimo_frame_cinza = gray
                continue

            # Lógica de detecção de movimento
            diff = cv2.absdiff(ultimo_frame_cinza, gray)
            _, thresh = cv2.threshold(diff, 25, 255, cv2.THRESH_BINARY)
            movimento = cv2.countNonZero(thresh)

            if movimento < 3000:
                if not medidor_em_posicao:
                    tempo_estabilizado += 1
                
                if tempo_estabilizado > 15 and not bloqueio_leitura:
                    # Feedback visual de leitura (Borda Verde)
                    cv2.rectangle(display_frame, (0,0), (w,h), (0, 255, 0), 20)
                    
                    # 1. VERIFICAR LOGOS (PONTOS 2, 3 e 6)
                    # Nota: Precisa ter as imagens na pasta referencias/
                    res_inmetro = "AGUARDANDO REF"
                    res_eletra = "AGUARDANDO REF"
                    res_energisa = "AGUARDANDO REF"
                    
                    try:
                        status_i, _, _ = vision.compare_images(frame, "referencias/inmetro.png", roi=ZONA_INMETRO)
                        res_inmetro = status_i
                        status_el, _, _ = vision.compare_images(frame, "referencias/eletra.png", roi=ZONA_ELETRA)
                        res_eletra = status_el
                        status_en, _, _ = vision.compare_images(frame, "referencias/energisa.png", roi=ZONA_ENERGISA)
                        res_energisa = status_en
                    except: pass

                    # 2. LER NÚMEROS (PONTOS 4 e 5)
                    serial = vision.ler_numero_serie(frame, roi=ZONA_SERIAL)
                    id_medidor = vision.ler_numero_serie(frame, roi=ZONA_ID)
                    
                    print(f"PONTO 2 (INMETRO): {res_inmetro}")
                    print(f"PONTO 3 (ELETRA): {res_eletra}")
                    print(f"PONTO 4 (SERIAL): {serial}")
                    print(f"PONTO 5 (ID): {id_medidor}")
                    print(f"PONTO 6 (ENERGISA): {res_energisa}")

                    # Lógica de decisão final
                    if res_inmetro == "CORRETO" and res_eletra == "CORRETO" and len(serial) > 5:
                        cont_ok += 1
                        cor_status = (0, 255, 0)
                        txt_final = "APROVADO"
                        status_db = "OK"
                    else:
                        cont_erro += 1
                        cor_status = (0, 0, 255)
                        txt_final = "REPROVADO"
                        status_db = "FALHA"
                    
                    # 3. SALVAR IMAGEM E REGISTRAR NO BANCO
                    timestamp = time.strftime("%Y%m%d-%H%M%S")
                    nome_foto = f"inspecao_{serial}_{timestamp}.jpg"
                    caminho_foto = os.path.join(CAP_DIR, nome_foto)
                    cv2.imwrite(caminho_foto, frame)
                    
                    try:
                        db.salvar_inspecao(serial, status_db, 0.9, caminho_foto)
                        print(f"Inspeção salva no banco: {serial} -> {status_db}")
                    except Exception as e:
                        print(f"Erro ao salvar no banco: {e}")

                    # Desenhar Veridito na Tela
                    cv2.putText(display_frame, txt_final, (w//2 - 50, 100), cv2.FONT_HERSHEY_SIMPLEX, 1.2, cor_status, 3)
                    
                    # Mostrar status detalhado dos pontos na tela
                    cv2.putText(display_frame, f"INMETRO: {res_inmetro}", (20, 100), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0) if res_inmetro == "CORRETO" else (0, 0, 255), 2)
                    cv2.putText(display_frame, f"ELETRA: {res_eletra}", (20, 130), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0) if res_eletra == "CORRETO" else (0, 0, 255), 2)
                    cv2.putText(display_frame, f"SERIAL: {serial}", (20, 160), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
                    
                    bloqueio_leitura = True
                    tempo_estabilizado = 0
            else:
                tempo_estabilizado = 0
                bloqueio_leitura = False
                cv2.putText(display_frame, "MONITORANDO ESTEIRA...", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

            ultimo_frame_cinza = gray
        
        # DESENHAR TODAS AS ZONAS DEFINIDAS NO CONFIG.PY AUTOMATICAMENTE
        import src.config as cfg
        for attr in dir(cfg):
            if attr.startswith("ZONA_"):
                zona = getattr(cfg, attr)
                # Desenha o quadrado
                cv2.rectangle(display_frame, (zona[0], zona[1]), 
                             (zona[0]+zona[2], zona[1]+zona[3]), (255, 255, 255), 1)
                # Escreve o nome da zona em cima
                cv2.putText(display_frame, attr.replace("ZONA_", ""), 
                           (zona[0], zona[1]-5), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)

        cv2.imshow('Linha Industrial Automatizada', display_frame)
        
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'): break
        if key == ord('p'): 
            pausado = not pausado
            print("SISTEMA PAUSADO" if pausado else "SISTEMA RETOMADO")
        
        if key == ord('c'):
            # MODO CALIBRAÇÃO: Salva o que está nas zonas como nova referência
            print("\n[CALIBRAÇÃO] Salvando novas imagens de referência...")
            zonas_para_salvar = {
                "inmetro.png": ZONA_INMETRO,
                "eletra.png": ZONA_ELETRA,
                "energisa.png": ZONA_ENERGISA
            }
            from src.config import REF_DIR
            for nome, zona in zonas_para_salvar.items():
                x, y, w, h = zona
                recorte = frame[y:y+h, x:x+w]
                if recorte.size == 0:
                    print(f"ERRO: Zona {nome} está fora dos limites da imagem ({frame.shape[1]}x{frame.shape[0]})")
                    continue
                caminho = os.path.join(REF_DIR, nome)
                cv2.imwrite(caminho, recorte)
                print(f"Salvo: {caminho}")
            print("[CALIBRAÇÃO] Sucesso! Reinicie o sistema para usar as novas referências.\n")

    vision.close_camera()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    rodar_esteira_automatica()

