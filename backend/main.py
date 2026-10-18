from fastapi import FastAPI, Depends, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session

import cv2
import numpy as np
import torch
import torch.nn as nn
from torchvision import models
from ultralytics import YOLO

from collections import deque
from datetime import datetime
import time
from pathlib import Path
import os

from backend.database import SessionLocal, engine
from backend.table_model import User, Camera, Base
from backend.schemas import SignupRequest, LoginRequest, CameraCreate, ResetPasswordRequest
from backend.auth import (
    validate_username,
    validate_mobile,
    validate_password,
    hash_password,
    verify_password,
)

from alerts.whatsapp import send_whatsapp_alert

# ============================================================
# APP
# ============================================================
Base.metadata.create_all(bind=engine)
app = FastAPI(title="Smart CCTV AI API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================
# SNAPSHOTS (PROJECT ROOT)
# ============================================================
BASE_DIR = Path(__file__).resolve().parent.parent
SNAPSHOT_DIR = BASE_DIR / "snapshots"
SNAPSHOT_DIR.mkdir(exist_ok=True)

print("📸 Snapshots directory:", SNAPSHOT_DIR)

app.mount(
    "/snapshots",
    StaticFiles(directory=str(SNAPSHOT_DIR)),
    name="snapshots",
)

# 🔴 REPLACE with your current ngrok backend URL
SERVER_URL = "https://doubtable-ardell-unnicked.ngrok-free.dev"

# ============================================================
# GLOBAL STATUS
# ============================================================
LATEST_STATUS: dict[str, str] = {}   # user_id -> NORMAL | THREAT

# ============================================================
# DB
# ============================================================
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ============================================================
# AUTH
# ============================================================
@app.post("/signup")
def signup(data: SignupRequest, db: Session = Depends(get_db)):
    validate_username(data.username)
    validate_mobile(data.mobile_number)
    validate_password(data.password)

    if db.query(User).filter(User.username.ilike(data.username)).first():
        raise HTTPException(409, "Username exists")

    user = User(
        username=data.username,
        name=data.name,
        mobile_number=data.mobile_number,
        password=hash_password(data.password),
    )
    db.add(user)
    db.commit()

    return {"message": "Registered"}

@app.post("/login")
def login(data: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username.ilike(data.username)).first()
    if not user or not verify_password(data.password, user.password):
        raise HTTPException(401, "Invalid credentials")

    return {"user_id": str(user.userid)}

@app.post("/reset-password")
def reset_password(data: ResetPasswordRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username.ilike(data.username)).first()
    if not user:
        raise HTTPException(404, "User not found")
    
    validate_password(data.new_password)
    user.password = hash_password(data.new_password)
    db.commit()
    
    return {"message": "Password reset successful"}

# ============================================================
# CAMERA
# ============================================================
@app.post("/camera/{user_id}")
def add_camera(user_id: str, data: CameraCreate, db: Session = Depends(get_db)):
    cam = Camera(
        user_id=user_id,
        camera_name=data.camera_name,
        ip_url=data.ip_url,
    )
    db.add(cam)
    db.commit()
    return {"message": "Camera added"}

@app.get("/camera/{user_id}")
def get_camera(user_id: str, db: Session = Depends(get_db)):
    cam = db.query(Camera).filter(Camera.user_id == user_id).first()
    if not cam:
        raise HTTPException(404, "No camera")
    return cam

# ============================================================
# AI MODELS
# ============================================================
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

# 🔫 Weapon detection
WEAPON_MODEL = YOLO("runs/detect/train/weights/best.pt")
WEAPON_CLASSES = {"knife", "pistol"}
WEAPON_CONF = 0.75

# 🤼 Violence detection
NUM_FRAMES = 16
IMG_SIZE = 112
VIOLENCE_THRESHOLD = 0.75

IMAGENET_MEAN = np.array([0.485, 0.456, 0.406])
IMAGENET_STD = np.array([0.229, 0.224, 0.225])

class CNNLSTM(nn.Module):
    def __init__(self):
        super().__init__()
        backbone = models.resnet18(
            weights=models.ResNet18_Weights.IMAGENET1K_V1
        )
        self.cnn = nn.Sequential(*list(backbone.children())[:-1])
        for p in self.cnn.parameters():
            p.requires_grad = False

        self.lstm = nn.LSTM(512, 256, num_layers=2, batch_first=True)
        self.fc = nn.Linear(256, 2)

    def forward(self, x):
        B, T, C, H, W = x.shape
        x = x.view(B * T, C, H, W)
        feats = self.cnn(x).view(B, T, 512)
        out, _ = self.lstm(feats)
        return self.fc(out[:, -1])

VIOLENCE_MODEL = CNNLSTM().to(DEVICE)
VIOLENCE_MODEL.load_state_dict(
    torch.load("models/cnn_lstm/best_model.pth", map_location=DEVICE)
)
VIOLENCE_MODEL.eval()

# ============================================================
# STREAM + AI PIPELINE
# ============================================================
def generate_stream(ip_url: str, user_id: str):
    cap = cv2.VideoCapture(ip_url)

    frame_buffer = deque(maxlen=NUM_FRAMES)
    violence_votes = deque(maxlen=3)
    last_alert_time = 0

    LATEST_STATUS[user_id] = "NORMAL"

    if not cap.isOpened():
        while True:
            offline = np.zeros((480, 640, 3), dtype=np.uint8)
            cv2.putText(
                offline, "CAMERA OFFLINE",
                (160, 240), cv2.FONT_HERSHEY_SIMPLEX,
                1, (0, 0, 255), 2
            )
            _, jpeg = cv2.imencode(".jpg", offline)
            yield b"--frame\r\nContent-Type: image/jpeg\r\n\r\n" + jpeg.tobytes() + b"\r\n"

    while True:
        ret, frame = cap.read()
        if not ret:
            continue

        display = frame.copy()

        # ----------------------------
        # WEAPON DETECTION
        # ----------------------------
        weapon_detected = False
        results = WEAPON_MODEL(frame, verbose=False)

        for r in results:
            for box in r.boxes:
                label = WEAPON_MODEL.names[int(box.cls[0])].lower()
                conf = float(box.conf[0])
                if label in WEAPON_CLASSES and conf >= WEAPON_CONF:
                    weapon_detected = True
                    x1, y1, x2, y2 = map(int, box.xyxy[0])
                    cv2.rectangle(display, (x1, y1), (x2, y2), (0, 0, 255), 2)

        # ----------------------------
        # VIOLENCE DETECTION
        # ----------------------------
        resized = cv2.resize(frame, (IMG_SIZE, IMG_SIZE))
        resized = resized[:, :, ::-1] / 255.0
        resized = (resized - IMAGENET_MEAN) / IMAGENET_STD
        frame_buffer.append(resized)

        violence_detected = False
        violence_conf = 0.0

        if len(frame_buffer) == NUM_FRAMES:
            clip = np.array(frame_buffer).transpose(0, 3, 1, 2)
            X = torch.tensor(clip, dtype=torch.float32).unsqueeze(0).to(DEVICE)

            with torch.no_grad():
                probs = torch.softmax(VIOLENCE_MODEL(X), dim=1)
                violence_conf = probs[0, 1].item()

            violence_votes.append(violence_conf >= VIOLENCE_THRESHOLD)
            violence_detected = sum(violence_votes) >= 2

        # ----------------------------
        # FUSION
        # ----------------------------
        status = "THREAT" if (weapon_detected or violence_detected) else "NORMAL"
        LATEST_STATUS[user_id] = status

        # ----------------------------
        # ALERT (WITH SNAPSHOT)
        # ----------------------------
        if status == "THREAT" and time.time() - last_alert_time > 30:
            last_alert_time = time.time()

            ts = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{user_id}_{ts}.jpg"
            snapshot_path = SNAPSHOT_DIR / filename
            cv2.imwrite(str(snapshot_path), display)

            image_url = f"{SERVER_URL}/snapshots/{filename}"

            send_whatsapp_alert(
                camera_id=user_id,
                threat_type="Weapon / Violence",
                confidence=violence_conf,
                timestamp=datetime.now(),
                image_url=image_url,
            )

        # ----------------------------
        # OVERLAY
        # ----------------------------
        color = (0, 0, 255) if status == "THREAT" else (0, 255, 0)
        cv2.putText(
            display,
            f"STATUS: {status}",
            (20, 40),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            color,
            2,
        )

        _, jpeg = cv2.imencode(".jpg", display)
        yield b"--frame\r\nContent-Type: image/jpeg\r\n\r\n" + jpeg.tobytes() + b"\r\n"

# ============================================================
# STATUS API
# ============================================================
@app.get("/status/{user_id}")
def get_status(user_id: str):
    return {"status": LATEST_STATUS.get(user_id, "NORMAL")}

# ============================================================
# STREAM ENDPOINT
# ============================================================
@app.get("/stream/{user_id}")
def stream(user_id: str, db: Session = Depends(get_db)):
    cam = db.query(Camera).filter(Camera.user_id == user_id).first()
    if not cam:
        raise HTTPException(404, "Camera not found")

    return StreamingResponse(
        generate_stream(cam.ip_url, user_id),
        media_type="multipart/x-mixed-replace; boundary=frame",
    )
# ============================================================