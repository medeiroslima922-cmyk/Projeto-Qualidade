# Integração do Ultralytics YOLO (YOLOv8 / YOLOv11)

Este plano descreve as etapas para instalar a biblioteca `ultralytics` no ambiente Python do projeto e criar um script de teste (`teste_yolo.py`) para verificar o funcionamento do YOLO em tempo real via câmera.

## User Review Required

> [!NOTE]
> A biblioteca `ultralytics` depende do PyTorch. O download completo (incluindo PyTorch e o modelo pré-treinado do YOLO) pode demorar alguns minutos dependendo da sua conexão com a internet (cerca de 150MB a 300MB no total).

> [!IMPORTANT]
> Certifique-se de que nenhum outro aplicativo (como Teams, Zoom, Meet) esteja utilizando a câmera ao rodar o script de teste.

## Open Questions

Não há perguntas em aberto no momento. O objetivo inicial é instalar e validar se o YOLO roda corretamente com a sua webcam.

---

## Proposed Changes

### Instalação de Dependências

#### [NEW] [.venv](file:///c:/Users/joao.lima/.gemini/antigravity/scratch/Projeto%20Qualidade/.venv)
Criar um ambiente virtual Python (`venv`) local na raiz do projeto. Isso reduzirá o comprimento do caminho dos arquivos (evitando o limite de 260 caracteres do Windows na instalação do PyTorch) e isolará as dependências.

#### [MODIFY] [requirements.txt](file:///c:/Users/joao.lima/.gemini/antigravity/scratch/Projeto%20Qualidade/requirements.txt)
Adicionar `ultralytics` à lista de dependências do projeto para garantir a reprodutibilidade.

---

### Scripts de Teste

#### [NEW] [teste_yolo.py](file:///c:/Users/joao.lima/.gemini/antigravity/scratch/Projeto%20Qualidade/teste_yolo.py)
Criar um script para carregar o modelo YOLO pré-treinado (`yolov8n.pt` - versão Nano, extremamente rápida) e rodá-lo na captura da webcam, desenhando as caixas delimitadoras e classes detectadas em tempo real na tela.

---

## Verification Plan

### Manual Verification
1. Criar o ambiente virtual na pasta do projeto:
   `python -m venv .venv`
2. Instalar as dependências do projeto usando o pip do ambiente virtual:
   `.venv\Scripts\pip install -r requirements.txt`
3. Executar o script de teste usando o Python do ambiente virtual:
   `.venv\Scripts\python teste_yolo.py`
4. Confirmar que a janela da câmera abre com o YOLO detectando objetos comuns do dia-a-dia com suas respectivas etiquetas.
