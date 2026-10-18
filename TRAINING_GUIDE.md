# ML Model Training Guide for CCTV Neural Networks

This document details how you can train the custom models used in the Smart CCTV Application.

## 1. Weapon Detection (YOLO)

Your system uses the latest Ultralytics YOLO models to detect weapons (e.g., Knives, Pistols) in a frame.

**Script Location:** `models/yolo/train.py`

### Dataset Preparation
1. Obtain a custom dataset of weapons (for example natively exported from Roboflow in YOLOv8 formatting).
2. The folder structure should look like this:
   ```text
   data/weapon_detection/
   ├── train/
   │   ├── images/
   │   └── labels/
   ├── val/
   │   ├── images/
   │   └── labels/
   └── weapon.yaml
   ```
3. Your `weapon.yaml` file should point to the relative paths of `train/images` and `val/images` and list the class names (`0: knife`, `1: pistol`).

### Running Training
1. Activate your Python virtual environment.
2. Inside your `train.py` the `data` argument already points to `data/weapon_detection/weapon.yaml`.
3. Execute the script:
   ```bash
   cd models/yolo
   python train.py
   ```
4. The trained weights will output to `runs/detect/trainsample/weights/best.pt`. Move this `best.pt` file into the main root `runs/detect/train/weights/best.pt` so the backend `main.py` can load it out of the box.

---

## 2. Violence Detection (PyTorch CNN-LSTM)

Your backend implements a custom hybrid Model architecture combining a ResNet-18 (CNN feature extractor) with an LSTM (temporal sequencer).

**Script Location:** `models/cnn_lstm/train.py`

### Dataset Preparation
1. Gather a dataset of violent and non-violent short video clips (for example from UCF-Crime or Real Life Violence Situations Dataset).
2. Organize the dataset directory strictly as follows:
   ```text
   data/violence_videos/
   ├── train/
   │   ├── non_violence/ (Contains .mp4 files)
   │   └── violence/     (Contains .mp4 files)
   └── val/
       ├── non_violence/
       └── violence/
   ```

### Running Training
1. In `models/cnn_lstm/train.py`, the `DATASET_ROOT` is configured to `data/violence_videos` which matches our structure.
2. The script processes 16 frames per video clip and resizes them to 112x112 using PyTorch ImageNet normalization.
3. Simply execute:
   ```bash
   cd models/cnn_lstm
   python train.py
   ```
4. The script saves the best weights automatically to `models/cnn_lstm/best_model.pth`. The FastAPI backend already points to this exact path.

---

### Tips
- Always ensure `torch.cuda.is_available()` returns `True` before starting a heavy training session, otherwise training on CPU will take exponentially longer.
- Keep the `NUM_FRAMES = 16` and `IMG_SIZE = 112` the same in both training scripts and the backend `main.py` to ensure consistency.
