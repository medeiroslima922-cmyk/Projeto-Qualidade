import cv2
import numpy as np
import pytesseract
import os
from .config import THRESHOLD_CORRETO, THRESHOLD_DUVIDA

# Nota: O Tesseract OCR precisa estar instalado no sistema operacional.
# O comando abaixo aponta para o caminho padrão de instalação no Windows:
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

class VisionSystem:
    def __init__(self):
        self.cap = None

    def open_camera(self, camera_id=0):
        self.cap = cv2.VideoCapture(camera_id)
        return self.cap.isOpened()

    def capture_frame(self):
        if self.cap and self.cap.isOpened():
            ret, frame = self.cap.read()
            if ret:
                return frame
        return None

    def ler_numero_serie(self, frame, roi=None):
        """
        Lê texto de uma região da imagem (OCR).
        roi = (x, y, w, h)
        """
        try:
            if roi:
                x, y, w, h = roi
                img_crop = frame[y:y+h, x:x+w]
            else:
                img_crop = frame

            gray = cv2.cvtColor(img_crop, cv2.COLOR_BGR2GRAY)
            # Aplicar um threshold para melhorar o OCR
            _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            
            texto = pytesseract.image_to_string(thresh, config='--psm 6 digits')
            return texto.strip()
        except Exception as e:
            return f"Erro OCR: {str(e)}"

    def compare_images(self, img_capturada, caminho_referencia, roi=None):
        """
        Compara a imagem (ou uma região) com a referência.
        """
        if not os.path.exists(caminho_referencia):
            raise FileNotFoundError(f"Referência não encontrada: {caminho_referencia}")

        ref_img = cv2.imread(caminho_referencia, cv2.IMREAD_GRAYSCALE)
        
        if roi:
            x, y, w, h = roi
            cap_roi = img_capturada[y:y+h, x:x+w]
            cap_gray = cv2.cvtColor(cap_roi, cv2.COLOR_BGR2GRAY)
            # Ajustar tamanho da referência para o ROI se necessário
            ref_img = cv2.resize(ref_img, (w, h))
        else:
            cap_gray = cv2.cvtColor(img_capturada, cv2.COLOR_BGR2GRAY)

        result = cv2.matchTemplate(cap_gray, ref_img, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

        score = max_val

        if score >= THRESHOLD_CORRETO:
            status = "CORRETO"
        elif score >= THRESHOLD_DUVIDA:
            status = "SEM CONFIANÇA"
        else:
            status = "ERRADO"

        return status, score, max_loc

    def close_camera(self):
        if self.cap:
            self.cap.release()
