import cv2
from src.vision import VisionSystem
from src.database import DatabaseManager
from src.config import ZONA_SERIAL, ZONA_LOGO
import os

def simular_api_fabrica(serial):
    """
    Aqui simulamos a consulta ao sistema da fábrica.
    """
    dados_producao = {
        "12181247": {
            "cliente": "AMAZONAS ENERGIA",
            "logo_ref": "referencias/logo_amazonas.png"
        }
    }
    return dados_producao.get(serial)

def rodar_inspecao():
    vision = VisionSystem()
    db = DatabaseManager()
    
    print("Iniciando câmera...")
    if not vision.open_camera(0): return

    print("\n--- SISTEMA MULTI-ZONA ATUALIZADO ---")
    print("Aperte 'S' para inspecionar.")

    while True:
        frame = vision.capture_frame()
        if frame is None: break
        
        display_frame = frame.copy()

        # DEFINIÇÃO DAS ZONAS (Puxando do config.py)
        roi_serial = ZONA_SERIAL
        roi_logo_cliente = ZONA_LOGO

        # Desenhar as zonas ajustadas
        cv2.rectangle(display_frame, (roi_serial[0], roi_serial[1]), (roi_serial[0]+roi_serial[2], roi_serial[1]+roi_serial[3]), (255, 0, 0), 2)
        cv2.rectangle(display_frame, (roi_logo_cliente[0], roi_logo_cliente[1]), (roi_logo_cliente[0]+roi_logo_cliente[2], roi_logo_cliente[1]+roi_logo_cliente[3]), (0, 255, 255), 2)

        cv2.imshow('Inspecao de Qualidade Industrial', display_frame)
        
        key = cv2.waitKey(1) & 0xFF
        if key == ord('s'):
            print("\n" + "="*40)
            print(">>> INICIANDO INSPEÇÃO...")
            
            # 1. LER SERIAL VIA OCR
            serial = vision.ler_numero_serie(frame, roi=roi_serial)
            print(f"SERIAL LIDO: {serial}")
            
            # 2. CONSULTAR DADOS NO SISTEMA "AO VIVO"
            info = simular_api_fabrica(serial)
            
            if info:
                print(f"INFO SISTEMA: Medidor para {info['cliente']}")
                
                # 3. CONFERIR LOGO DO CLIENTE
                if os.path.exists(info['logo_ref']):
                    status_logo, score_logo, _ = vision.compare_images(frame, info['logo_ref'], roi=roi_logo_cliente)
                    print(f"STATUS LOGO: {status_logo} (Score: {score_logo:.2f})")
                else:
                    print(f"AVISO: Gabarito '{info['logo_ref']}' não encontrado.")
                    status_logo = "N/A"
                
                # SALVAR RESULTADO (Apenas baseado nos desenhos/logos corretos)
                res_final = "APROVADO" if status_logo == "CORRETO" else "REPROVADO"
                print(f"RESULTADO FINAL: {res_final}")
                db.salvar_inspecao(serial, res_final, 1.0, "capturas/ultima.jpg")
            else:
                print("ERRO: Serial não encontrado no sistema da fábrica!")
            print("="*40 + "\n")

        elif key == ord('q'):
            break

    vision.close_camera()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    rodar_inspecao()
