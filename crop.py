import cv2
import os
from ultralytics import YOLO  

model = YOLO('model.pt')


input_dir = '../dlp2/car_images_cleaned/'
output_dir = 'processed_images'

os.makedirs(output_dir, exist_ok=True)


for filename in os.listdir(input_dir):
    if filename.endswith('.jpg') or filename.endswith('.jpeg'):
        image_path = os.path.join(input_dir, filename)
        image = cv2.imread(image_path)
        
        if image is None:
            continue 

        results = model(image_path)  
        print(results)


        for result in results:
            for detection in result:
                x1, y1, x2, y2, conf, cls = map(int, detection[:6])
                cropped_plate = image[y1:y2, x1:x2]

                gray = cv2.cvtColor(cropped_plate, cv2.COLOR_BGR2GRAY)
                inverted_image = 255 - gray

                output_image_path = os.path.join(output_dir, filename)
                cv2.imwrite(output_image_path, cropped_plate)  