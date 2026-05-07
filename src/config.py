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
