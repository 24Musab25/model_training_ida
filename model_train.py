from ultralytics import YOLO

# En son kaydedilen modeli yükle
model = YOLO("runs/detect/train/weights/best.pt")  # veya best.pt

# Eğitime devam et
model.train(data="data.yaml", epochs=70, imgsz=640)
