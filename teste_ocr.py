import cv2
from src.vision import VisionSystem

def testar_leitura():
    vision = VisionSystem()
    print("Abrindo câmera para teste de leitura de números...")
    
    if not vision.open_camera(0):
        print("Erro ao abrir a câmera.")
        return

    print("Posicione o medidor na frente da câmera.")
    print("Pressione 'S' para tentar ler o número ou 'Q' para sair.")

    while True:
        frame = vision.capture_frame()
        if frame is None: break
        
        # Desenhar um retângulo no centro para ajudar a posicionar o número
        h, w, _ = frame.shape
        # Região de Interesse (ROI) - Centralizada
        x, y, rw, rh = w//4, h//3, w//2, h//4
        cv2.rectangle(frame, (x, y), (x+rw, y+rh), (0, 255, 0), 2)
        cv2.putText(frame, "Posicione o Numero Aqui", (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

        cv2.imshow('Teste de Leitura de Numero (OCR)', frame)
        
        key = cv2.waitKey(1) & 0xFF
        if key == ord('s'):
            print("Lendo...")
            # Tenta ler o número na região do retângulo
            numero = vision.ler_numero_serie(frame, roi=(x, y, rw, rh))
            print(f"\n========================================")
            print(f"   NUMERO IDENTIFICADO: {numero}")
            print(f"========================================\n")
        
        elif key == ord('q'):
            break

    vision.close_camera()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    testar_leitura()
