import cv2
import time
from src.vision import VisionSystem
from src.config import ZONA_SERIAL, ZONA_LOGO, ZONA_TERMINAIS

def rodar_esteira_automatica():
    vision = VisionSystem()
    if not vision.open_camera(0): 
        print("Erro ao abrir a câmera.")
        return

    print("\n" + "="*50)
    print("   SISTEMA DE ESTEIRA AUTOMÁTICA ATIVO")
    print("   Aguardando detecção de medidor...")
    print("="*50)

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
                    
                    print("\n>>> INICIANDO INSPEÇÃO AUTOMÁTICA EM TODAS AS ZONAS...")
                    
                    # 1. LER SERIAL (OCR)
                    serial = vision.ler_numero_serie(frame, roi=ZONA_SERIAL)
                    print(f"ZONA SERIAL: {serial}")
                    
                    # 2. CONFERIR LOGO (Exemplo: se houver imagem de referência)
                    # Aqui ele tentaria comparar com o que está na pasta referencias
                    # status_logo, score_logo, _ = vision.compare_images(frame, "referencias/logo_amazonas.png", roi=ZONA_LOGO)
                    # print(f"ZONA LOGO: {status_logo}")

                    # 3. LER TERMINAIS (OCR ou Imagem)
                    terminais = vision.ler_numero_serie(frame, roi=ZONA_TERMINAIS)
                    print(f"ZONA TERMINAIS: {terminais}")
                    
                    # Lógica de contagem
                    if len(serial) > 2 or len(terminais) > 2:
                        cont_ok += 1
                        cv2.putText(display_frame, f"SERIAL: {serial}", (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
                        cv2.putText(display_frame, f"TERM: {terminais}", (50, 150), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
                    else:
                        cont_erro += 1
                        cv2.putText(display_frame, "FALHA NA LEITURA", (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
                    
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

    vision.close_camera()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    rodar_esteira_automatica()
