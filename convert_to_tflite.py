
from ultralytics import YOLO

model = YOLO('model.pt')
                                                                                                                                                                                                                                                           

model.export(format='tflite')

model = YOLO('model_saved_model/model_float32.tflite')

model.predict(source=0,show=True)