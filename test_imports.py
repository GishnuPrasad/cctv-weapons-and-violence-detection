import sys

def test_imports():
    print("Testing torch...")
    sys.stdout.flush()
    import torch
    print("Torch ok.")
    sys.stdout.flush()

    print("Testing cv2...")
    sys.stdout.flush()
    import cv2
    print("cv2 ok.")
    sys.stdout.flush()

    print("Testing sqlalchemy...")
    sys.stdout.flush()
    import sqlalchemy
    print("sqlalchemy ok.")
    sys.stdout.flush()

    print("Testing psycopg2...")
    sys.stdout.flush()
    import psycopg2
    print("psycopg2 ok.")
    sys.stdout.flush()

    print("Testing ultralytics...")
    sys.stdout.flush()
    from ultralytics import YOLO
    print("ultralytics ok.")
    sys.stdout.flush()

if __name__ == "__main__":
    test_imports()
    print("All imports succeeded!")
