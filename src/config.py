import os

# Caminhos de Pastas
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
REF_DIR = os.path.join(BASE_DIR, "referencias")
CAP_DIR = os.path.join(BASE_DIR, "capturas")
DB_PATH = os.path.join(DATA_DIR, "inspecao.db")

# Criar pastas se não existirem
for folder in [DATA_DIR, REF_DIR, CAP_DIR]:
    if not os.path.exists(folder):
        os.makedirs(folder)

# Configurações de Visão
# matchTemplate retorna valor entre 0 e 1
THRESHOLD_CORRETO = 0.85    # Acima disso é CORRETO
THRESHOLD_DUVIDA = 0.60     # Entre 0.60 e 0.85 é SEM CONFIANÇA. Abaixo é ERRADO.

# Configurações da Câmera
CAMERA_ID = 0  # 0 para webcam integrada, 1 para USB externa

# Coordenadas das Zonas de Inspeção (X, Y, Largura, Altura)
# Ajuste estes valores conforme a posição do medidor na câmera
ZONA_INMETRO = (250, 180, 120, 80)    # Ponto 2 (Logo INMETRO)
ZONA_ELETRA = (250, 300, 120, 80)     # Ponto 3 (Logo Eletra)
ZONA_SERIAL = (180, 480, 250, 40)     # Ponto 4 (Número de Série)
ZONA_ID = (180, 520, 250, 40)         # Ponto 5 (ID do Medidor)
ZONA_BARCODE = (300, 580, 300, 100)   # Ponto 5 (Código de Barras)
ZONA_ENERGISA = (50, 600, 150, 80)    # Ponto 6 (Logo Energisa)
ZONA_TERMINAIS = (550, 560, 250, 40)  # Outros modelos
