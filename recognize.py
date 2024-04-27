import cv2
import argparse
import os
from ultralytics import YOLO
from paddleocr import PaddleOCR

def process_video(source, output_filename):
    cap = cv2.VideoCapture(source)
    if not cap.isOpened():
        print("Cannot open the video source.")
        return

    
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    ret, frame = cap.read()
    if not ret:
        print("Failed to read a frame from the video.")
        cap.release()
        return
    frame_height, frame_width = frame.shape[:2]
    out = cv2.VideoWriter(output_filename, fourcc, 20.0, (frame_width, frame_height))

    process_frames(cap, out, frame, True)

    cap.release()
    out.release()

def process_image(source, output_filename):
    frame = cv2.imread(source)
    if frame is None:
        print("Failed to read the image file.")
        return

    
    out = cv2.VideoWriter()
    process_frames(None, out, frame, False)

    cv2.imwrite(output_filename, frame)

def process_frames(cap, out, frame, is_video):
    model = YOLO('model.pt')
    ocr = PaddleOCR(use_angle_cls=True, lang='en')

    while True:
        results = model(frame)
        for result in results:
            if hasattr(result, 'boxes') and result.boxes:
                for box in result.boxes.xyxy:
                    if len(box) == 6:
                        x1, y1, x2, y2, conf, cls = map(int, box)
                    elif len(box) == 4:
                        x1, y1, x2, y2 = map(int, box)
                        conf, cls = None, None

                    cropped_plate = frame[y1:y2, x1:x2]
                    ocr_result = ocr.ocr(cropped_plate, cls=True)
                    
                    if ocr_result and ocr_result[0]:
                        text = ' '.join([line[1][0] for line in ocr_result[0]])
                        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                        cv2.putText(frame, text, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)

        cv2.imshow('Frame', frame)  

        if is_video:
            out.write(frame)  
            ret, frame = cap.read()
            if not ret:
                break
        else:
            break

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cv2.destroyAllWindows()  

def main():
    parser = argparse.ArgumentParser(description="Process a video or an image source.")
    parser.add_argument('source', type=str, help='The index of the webcam, or the path to a video or image file')
    args = parser.parse_args()

    source = args.source

    if source.isdigit():  
        source = int(source)
        output_filename = "camera_output.mp4"
        process_video(source, output_filename)
    else:
        base_name = os.path.splitext(os.path.basename(source))[0]
        extension = os.path.splitext(source)[1].lower()

        if extension in ['.avi', '.mp4', '.mov']:  
            output_filename = f"{base_name}_processed.mp4"
            process_video(source, output_filename)
        elif extension in ['.jpg', '.jpeg', '.png']:  
            output_filename = f"{base_name}_processed.jpg"
            process_image(source, output_filename)
        else:
            print("Unsupported file format.")

if __name__ == '__main__':
    main()