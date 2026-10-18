import os
import cv2
import torch
import numpy as np
import torch.nn as nn
import torch.optim as optim
from tqdm import tqdm
from torchvision import models
from torch.utils.data import Dataset, DataLoader

# =========================
# SILENCE OPENCV WARNINGS
# =========================
cv2.setLogLevel(0)

# =========================
# CONFIG
# =========================
DATASET_ROOT = "data/violence_videos"
NUM_FRAMES = 16
IMG_SIZE = 112
BATCH_SIZE = 16
EPOCHS = 30
LR = 1e-4
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
SAVE_PATH = "models/cnn_lstm/best_model.pth"

LABEL_MAP = {
    "non_violence": 0,
    "violence": 1
}

IMAGENET_MEAN = np.array([0.485, 0.456, 0.406])
IMAGENET_STD  = np.array([0.229, 0.224, 0.225])

os.makedirs(os.path.dirname(SAVE_PATH), exist_ok=True)

# =========================
# DATASET
# =========================
class VideoDataset(Dataset):
    def __init__(self, split):
        self.samples = []
        split_path = os.path.join(DATASET_ROOT, split)

        for cls in LABEL_MAP:
            cls_path = os.path.join(split_path, cls)
            for v in os.listdir(cls_path):
                if v.lower().endswith((".mp4", ".avi", ".mov", ".mkv")):
                    self.samples.append(
                        (os.path.join(cls_path, v), LABEL_MAP[cls])
                    )

    def __len__(self):
        return len(self.samples)

    def _sample_frames(self, cap):
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        if total_frames <= 0:
            return []

        indices = np.linspace(0, total_frames - 1, NUM_FRAMES).astype(int)
        frames = []
        last_valid = None

        for idx in indices:
            try:
                cap.set(cv2.CAP_PROP_POS_FRAMES, idx)
                ret, frame = cap.read()

                if not ret or frame is None:
                    continue

                frame = cv2.resize(frame, (IMG_SIZE, IMG_SIZE))
                frame = frame[:, :, ::-1] / 255.0
                frame = (frame - IMAGENET_MEAN) / IMAGENET_STD

                frames.append(frame)
                last_valid = frame

            except Exception:
                continue

        if len(frames) == 0 and last_valid is not None:
            frames.append(last_valid)

        return frames

    def __getitem__(self, idx):
        path, label = self.samples[idx]
        cap = cv2.VideoCapture(path)

        frames = self._sample_frames(cap)
        cap.release()

        if len(frames) == 0:
            frames = [np.zeros((IMG_SIZE, IMG_SIZE, 3))]

        while len(frames) < NUM_FRAMES:
            frames.append(frames[-1])

        frames = np.array(frames).transpose(0, 3, 1, 2)
        frames = torch.tensor(frames, dtype=torch.float32)

        return frames, torch.tensor(label)

# =========================
# MODEL
# =========================
class CNNLSTM(nn.Module):
    def __init__(self, num_classes=2):
        super().__init__()

        backbone = models.resnet18(
            weights=models.ResNet18_Weights.IMAGENET1K_V1
        )
        self.cnn = nn.Sequential(*list(backbone.children())[:-1])

        # Freeze CNN
        for p in self.cnn.parameters():
            p.requires_grad = False

        self.feature_dim = 512

        self.lstm = nn.LSTM(
            input_size=self.feature_dim,
            hidden_size=256,
            num_layers=2,
            dropout=0.3,
            batch_first=True
        )

        self.fc = nn.Linear(256, num_classes)

    def forward(self, x):
        B, T, C, H, W = x.shape
        x = x.view(B * T, C, H, W)

        feats = self.cnn(x)
        feats = feats.view(B, T, self.feature_dim)

        lstm_out, _ = self.lstm(feats)
        out = self.fc(lstm_out[:, -1])

        return out

# =========================
# TRAIN FUNCTION
# =========================
def main():
    train_ds = VideoDataset("train")
    val_ds   = VideoDataset("val")

    train_loader = DataLoader(
        train_ds,
        batch_size=BATCH_SIZE,
        shuffle=True,
        num_workers=2,
        pin_memory=True,
        persistent_workers=True
    )

    val_loader = DataLoader(
        val_ds,
        batch_size=BATCH_SIZE,
        num_workers=2,
        pin_memory=True,
        persistent_workers=True
    )

    model = CNNLSTM().to(DEVICE)

    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(
        filter(lambda p: p.requires_grad, model.parameters()),
        lr=LR
    )

    best_val_loss = float("inf")

    for epoch in range(EPOCHS):
        model.train()
        train_loss = 0

        for X, y in tqdm(train_loader, desc=f"Epoch {epoch+1}/{EPOCHS}"):
            X, y = X.to(DEVICE), y.to(DEVICE)

            optimizer.zero_grad()
            out = model(X)
            loss = criterion(out, y)
            loss.backward()
            optimizer.step()

            train_loss += loss.item()

        model.eval()
        val_loss = 0
        with torch.no_grad():
            for X, y in val_loader:
                X, y = X.to(DEVICE), y.to(DEVICE)
                val_loss += criterion(model(X), y).item()

        print(
            f"Train Loss: {train_loss/len(train_loader):.4f} | "
            f"Val Loss: {val_loss/len(val_loader):.4f}"
        )

        if val_loss < best_val_loss:
            best_val_loss = val_loss
            torch.save(model.state_dict(), SAVE_PATH)
            print("✅ Best model saved")

    print("🔥 TRAINING COMPLETE")

# =========================
# WINDOWS ENTRY POINT
# =========================
if __name__ == "__main__":
    import torch.multiprocessing as mp
    mp.freeze_support()
    main()
