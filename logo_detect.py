import cv2
from ultralytics import YOLO
import datetime

# 1. Load your fine-tuned model
model = YOLO('best.pt')

# 2. Setup Video Capture
video_path = 'compliance_test.mp4'
cap = cv2.VideoCapture(video_path)

original_fps = cap.get(cv2.CAP_PROP_FPS) # e.g., 30
sample_rate = 5  # We want 5 frames per second
frame_interval = int(original_fps / sample_rate) # Process every 6th frame if FPS is 30

frame_count = 0
detections_log = []

print(f"Audit Engine Started | Sampling at {sample_rate} FPS")
print("-" * 60)
print(f"{'Time (HH:MM:SS)':<18} | {'Brand Detected':<18} | {'Confidence'}")
print("-" * 60)

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    # 3. Only process the frame if it matches our 5 FPS interval
    if frame_count % frame_interval == 0:
        results = model.predict(frame, conf=0.5, verbose=False)

        # Calculate exact timestamp
        seconds = frame_count / original_fps
        timestamp = str(datetime.timedelta(seconds=seconds))[2:10] # MM:SS.mm

        for r in results:
            for box in r.boxes:
                class_id = int(box.cls[0])
                team_name = model.names[class_id]
                conf = float(box.conf[0])

                # Print to console
                print(f"{timestamp:<18} | {team_name:<18} | {conf:.2f}")
                
                # Store for report
                detections_log.append([timestamp, team_name, conf])

    frame_count += 1

cap.release()
print("-" * 60)
print(f" Audit Complete. Processed {len(detections_log)} detection points.")