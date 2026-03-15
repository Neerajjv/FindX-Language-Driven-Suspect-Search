
import cv2
import os
import uuid
import sys
from PIL import Image

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config
from core.detector import PersonDetector

class VideoProcessor:
    def __init__(self):
        self.detector = PersonDetector()

    def process_video(self, video_path, sample_rate=config.FRAME_SAMPLE_RATE, callback=None):
        """
        Process a single video file.
        Yields (crop_image_pil, metadata_dict)
        """
        if not os.path.exists(video_path):
            print(f"Video not found: {video_path}")
            return

        cap = cv2.VideoCapture(video_path)
        fps = cap.get(cv2.CAP_PROP_FPS)
        if fps <= 0: fps = 25 # Fallback
        
        frame_interval = int(fps / sample_rate)
        if frame_interval < 1: frame_interval = 1
        
        frame_count = 0
        
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            
            if frame_count % frame_interval == 0:
                # Detect people
                bboxes, _ = self.detector.detect(frame)
                
                # Timestamp Calculation
                timestamp_ms = cap.get(cv2.CAP_PROP_POS_MSEC)
                timestamp_sec = int(timestamp_ms / 1000)
                time_str = f"{timestamp_sec//60:02d}:{timestamp_sec%60:02d}"
                
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                pil_img = Image.fromarray(rgb_frame)
                
                for bbox in bboxes:
                    x1, y1, x2, y2 = bbox
                    # Clamp coordinates
                    x1 = max(0, x1); y1 = max(0, y1)
                    x2 = min(pil_img.width, x2); y2 = min(pil_img.height, y2)
                    
                    if x2 - x1 < 20 or y2 - y1 < 20: continue # Skip too small crops
                    
                    crop = pil_img.crop((x1, y1, x2, y2))
                    
                    meta = {
                        "id": str(uuid.uuid4()),
                        "video_path": video_path,
                        "video_name": os.path.basename(video_path),
                        "timestamp_ms": timestamp_ms,
                        "timestamp_str": time_str,
                        "bbox": [x1, y1, x2, y2]
                    }
                    
                    yield crop, meta
            
            frame_count += 1
            if callback and frame_count % 100 == 0:
                callback(frame_count) # Optional progress update

        cap.release()
