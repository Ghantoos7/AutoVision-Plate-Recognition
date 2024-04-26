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
        
        for result in results:
            if hasattr(result, 'boxes') and result.boxes:
                for box in result.boxes.xyxy:
                    if len(box) == 6:
                        x1, y1, x2, y2, conf, cls = map(int, box)
                    elif len(box) == 4:
                        x1, y1, x2, y2 = map(int, box)
                        conf, cls = None, None

                    cropped_plate = image[y1:y2, x1:x2]

                    gray = cv2.cvtColor(cropped_plate, cv2.COLOR_BGR2GRAY)

                    inverted_image = 255 - gray

                    output_image_path = os.path.join(output_dir, filename)

                    cv2.imwrite(output_image_path, inverted_image)

                    if os.path.exists(output_image_path):
                        print(f"Saved: {output_image_path}")
                    else:
                        print(f"Failed to save: {output_image_path}")
