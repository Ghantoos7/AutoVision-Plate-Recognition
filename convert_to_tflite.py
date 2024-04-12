
from ultralytics import YOLO

model = YOLO('model.pt')

model.export(format='tflite')

model = YOLO('model_saved_model/model_float32.tflite')

model.predict('Demo.jpg', save=True, imgsz=640, conf=0.2)