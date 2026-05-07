import cv2

def testar():
    print("Tentando abrir a câmera...")
    # O número 0 tenta a webcam padrão do notebook.
    # Se você tiver uma câmera USB externa, tente mudar para 1.
    cap = cv2.VideoCapture(0) 
    
    if not cap.isOpened():
        print("ERRO: Não consegui acessar a câmera.")
        print("Dica: Verifique se ela está conectada ou se outro app (Teams, Meet, Zoom) está usando ela agora.")
        return

    print("SUCESSO! Câmera conectada.")
    print("Uma janela vai abrir agora. Pressione a tecla 'Q' ou 'ESC' para fechar.")

    while True:
        ret, frame = cap.read()
        if not ret:
            break
            
        # Mostra o vídeo na tela
        cv2.imshow('TESTE DE CAMERA - PROJETO QUALIDADE', frame)
        
        # Espera apertar 'q' para sair
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
    print("Teste finalizado.")

if __name__ == "__main__":
    testar()
