import cv2
import os
# pyrefly: ignore [missing-import]
from ultralytics import YOLO

def testar_yolo():
    print("Carregando o modelo YOLOv8 Nano (yolov8n.pt)...")
    # Caminho absoluto para o modelo na raiz do projeto
    model_path = os.path.join(os.path.dirname(__file__), "yolov8n.pt")
    model = YOLO(model_path)
    
    print("Tentando abrir a câmera...")
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        print("ERRO: Não foi possível acessar a câmera.")
        print("Dica: Verifique se ela está conectada ou se outro aplicativo está usando ela.")
        return

    print("\n" + "="*50)
    print("SUCESSO! YOLO carregado e câmera conectada.")
    print("Pressione 'q' na janela do vídeo para encerrar o teste.")
    print("="*50 + "\n")

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Erro ao ler o frame da câmera.")
            break
            
        # Rodar a inferência do YOLO no frame atual
        # conf=0.25 (mínimo de 25% de confiança para mostrar a detecção)
        # verbose=False (evita poluir o terminal com logs de detecção a cada frame)
        results = model.predict(frame, conf=0.25, verbose=False)
        
        # O método .plot() desenha automaticamente as caixas delimitadoras,
        # nomes das classes e porcentagens de confiança no frame.
        annotated_frame = results[0].plot()
        
        # Adicionar texto de ajuda na tela
        cv2.putText(annotated_frame, "Pressione 'Q' para Sair", (10, 30), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

        # Mostra o vídeo anotado na tela
        cv2.imshow('TESTE YOLOv8 - PROJETO QUALIDADE', annotated_frame)
        
        # Espera apertar 'q' para sair
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
    print("Teste finalizado com sucesso!")

if __name__ == "__main__":
    testar_yolo()
