import cv2
import os
import torch
import numpy as np
import torch.nn as nn
from collections import deque
from datetime import datetime
from ultralytics import YOLO
from torchvision import models
from alerts.whatsapp import send_whatsapp_alert

# =========================
# CONFIG
# =========================
CAMERA_ID = "CAM_01"
CAMERA_URL = "http://192.168.1.5:8080/video"

YOLO_MODEL_PATH = "runs/detect/train/weights/best.pt"
VIOLENCE_MODEL_PATH = "models/cnn_lstm/best_model.pth"

NUM_FRAMES = 16
IMG_SIZE = 112
VIOLENCE_THRESHOLD = 0.75
WEAPON_CONF_THRESHOLD = 0.75

WEAPON_CLASSES = ["knife", "pistol"]

DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

IMAGENET_MEAN = np.array([0.485, 0.456, 0.406])
IMAGENET_STD  = np.array([0.229, 0.224, 0.225])

SNAPSHOT_DIR = "snapshots"
SERVER_URL = "https://nonabrasive-hypothetically-alyse.ngrok-free.dev"  # ngrok URL
os.makedirs(SNAPSHOT_DIR, exist_ok=True)

cv2.setLogLevel(0)

# =========================
# CNN-LSTM MODEL
# =========================
class CNNLSTM(nn.Module):
    def __init__(self, num_classes=2):
        super().__init__()
        backbone = models.resnet18(
            weights=models.ResNet18_Weights.IMAGENET1K_V1
        )
        self.cnn = nn.Sequential(*list(backbone.children())[:-1])

        for p in self.cnn.parameters():
            p.requires_grad = False

        self.lstm = nn.LSTM(
            input_size=512,
            hidden_size=256,
            num_layers=2,
            dropout=0.3,
            batch_first=True
        )

        self.fc = nn.Linear(256, num_classes)

    def forward(self, x):
        B, T, C, H, W = x.shape
        x = x.view(B * T, C, H, W)
        feats = self.cnn(x).view(B, T, 512)
        out, _ = self.lstm(feats)
        return self.fc(out[:, -1])

# =========================
# LOAD MODELS
# =========================
weapon_model = YOLO(YOLO_MODEL_PATH)

violence_model = CNNLSTM().to(DEVICE)
violence_model.load_state_dict(
    torch.load(VIOLENCE_MODEL_PATH, map_location=DEVICE)
)
violence_model.eval()

# =========================
# CAMERA INIT
# =========================
cap = cv2.VideoCapture(CAMERA_URL)
if not cap.isOpened():
    raise RuntimeError("❌ Cannot access camera")

frame_buffer = deque(maxlen=NUM_FRAMES)
violence_history = deque(maxlen=3)
last_status = "NORMAL"

print("🎥 LIVE CCTV FUSION STARTED")

# =========================
# MAIN LOOP
# =========================
while True:
    ret, frame = cap.read()
    if not ret or frame is None:
        continue

    display = frame.copy()

    # -------------------------
    # YOLO WEAPON
    # -------------------------
    weapon_detected = False
    results = weapon_model(frame, verbose=False)

    for r in results:
        for box in r.boxes:
            conf = float(box.conf[0])
            cls_id = int(box.cls[0])
            label = weapon_model.names[cls_id].lower()

            if label in WEAPON_CLASSES and conf >= WEAPON_CONF_THRESHOLD:
                weapon_detected = True
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                cv2.rectangle(display, (x1, y1), (x2, y2), (0, 0, 255), 2)

    # -------------------------
    # VIOLENCE (CNN-LSTM)
    # -------------------------
    resized = cv2.resize(frame, (IMG_SIZE, IMG_SIZE))
    resized = resized[:, :, ::-1] / 255.0
    resized = (resized - IMAGENET_MEAN) / IMAGENET_STD
    frame_buffer.append(resized)

    violence_detected = False
    violence_conf = 0.0

    if len(frame_buffer) == NUM_FRAMES:
        clip = np.array(frame_buffer).transpose(0, 3, 1, 2)
        X = torch.tensor(clip, dtype=torch.float32)\
                 .unsqueeze(0).to(DEVICE)

        with torch.no_grad():
            probs = torch.softmax(violence_model(X), dim=1)
            violence_conf = probs[0, 1].item()

        violence_history.append(violence_conf >= VIOLENCE_THRESHOLD)
        violence_detected = sum(violence_history) >= 2

    # -------------------------
    # FUSION
    # -------------------------
    if weapon_detected and violence_detected:
        status, color = "THREAT", (0, 0, 255)
    elif weapon_detected:
        status, color = "THREAT", (0, 165, 255)
    elif violence_detected:
        status, color = "THREAT", (0, 0, 255)
    else:
        status, color = "NORMAL", (0, 255, 0)

    if status != last_status and status != "NORMAL":
        now = datetime.now()
        filename = f"{CAMERA_ID}_{now.strftime('%Y%m%d_%H%M%S')}.jpg"
        path = os.path.join(SNAPSHOT_DIR, filename)
        cv2.imwrite(path, display)

        image_url = f"{SERVER_URL}/{SNAPSHOT_DIR}/{filename}"

        send_whatsapp_alert(
            camera_id=CAMERA_ID,
            threat_type=status,
            confidence=violence_conf,
            timestamp=now,
            image_url=image_url
        )

    last_status = status

    cv2.putText(display, f"STATUS: {status}", (20, 40),
                cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)

    cv2.imshow("CCTV Threat Detection (PyTorch)", display)

    if cv2.waitKey(1) & 0xFF in (ord('q'), ord('Q')):
        break

cap.release()
cv2.destroyAllWindows()
