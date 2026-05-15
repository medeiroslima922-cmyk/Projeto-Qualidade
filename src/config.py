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
# Ajustadas após análise das capturas (Resolução 640x480)
ZONA_INMETRO = (220, 100, 100, 80)     # Ponto 2 (Logo INMETRO)
ZONA_ELETRA = (220, 220, 100, 80)      # Ponto 3 (Logo Eletra)
ZONA_SERIAL = (300, 380, 300, 80)      # Ponto 4 (Número de Série Grande embaixo)
ZONA_ID = (250, 310, 200, 40)          # Ponto 5 (Número menor no meio)
ZONA_ENERGISA = (220, 350, 120, 80)    # Ponto 6 (Logo Amazonas/Energisa)
ZONA_BARCODE = (0, 0, 50, 50)
ZONA_TERMINAIS = (500, 400, 100, 80)
ZONA_LOGO = ZONA_ENERGISA # Alias para compatibilidade




