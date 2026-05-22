from ultralytics import YOLO

def main():
    """Train YOLO model for electric meter field detection.

    Uses the simplified classes defined in `dataset_prompt.md`.
    Ensure `data.yaml` (dataset description) and the annotated images are present
    in the project root before running this script.
    """
    # Load the pretrained YOLOv8 nano model
    model = YOLO("yolov8n.pt")
    # Train with custom dataset
    model.train(data="data.yaml", epochs=50, imgsz=640, batch=16, project="runs/train", name="meter_fields")

if __name__ == "__main__":
    main()
