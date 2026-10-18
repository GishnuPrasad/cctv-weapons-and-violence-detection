from ultralytics import YOLO
import torch
import torch.multiprocessing as mp

def main():
    # Ensure CUDA is available
    assert torch.cuda.is_available(), "❌ CUDA not available"

    # Force RTX GPU (CUDA:0 is always NVIDIA)
    device = 0

    model = YOLO("yolov8n.pt")

    model.train(
        data="data/weapon_detection/weapon.yaml",
        epochs=50,
        imgsz=640,
        batch=16,          
        workers=4,
        device=device,     
        project="runs/detect",
        name="trainsample",
        exist_ok=True
    )

if __name__ == "__main__":
    mp.freeze_support()
    main()
