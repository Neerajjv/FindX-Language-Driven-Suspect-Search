
import logging
from ultralytics import YOLO
import torch

class PersonDetector:
    def __init__(self, model_name='yolov8n-pose.pt'):
        """
        Initialize YOLOv8 detector for person class only.
        """
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        print(f"Loading YOLOv8 ({model_name}) on {self.device}...")
        try:
            self.model = YOLO(model_name)
        except Exception as e:
            logging.error(f"Failed to load YOLO model: {e}")
            raise
        
        # Person class ID in COCO is 0
        self.target_class = 0 

    def detect(self, frame):
        """
        Detect people in a frame.
        Returns: 
            bboxes: List of [x1, y1, x2, y2]
            keypoints: List of keypoints (if available) or None
        """
        results = self.model.predict(frame, classes=[self.target_class], verbose=False, device=self.device)
        bboxes = []
        keypoints_list = []
        
        for result in results:
            boxes = result.boxes
            keypoints = result.keypoints
            
            for i, box in enumerate(boxes):
                x1, y1, x2, y2 = box.xyxy[0].tolist()
                bboxes.append([int(x1), int(y1), int(x2), int(y2)])
                
                if keypoints is not None:
                    # keypoints.xy is time, people, xy? No, result.keypoints.xy is (N, 17, 2)
                    # result.keypoints[i] corresponds to box i
                    kpts = keypoints[i].xy[0].tolist() # (17, 2)
                    keypoints_list.append(kpts)
                else:
                    keypoints_list.append([])
                    
        return bboxes, keypoints_list

    def track(self, frame):
        """
        Track people in a frame.
        Returns:
            tracks: List of [x1, y1, x2, y2, track_id]
            keypoints: List of keypoints (matching tracks)
        """
        results = self.model.track(frame, classes=[self.target_class], verbose=False, device=self.device, persist=True)
        tracks = []
        keypoints_list = []
        
        for result in results:
            boxes = result.boxes
            keypoints = result.keypoints
            
            if boxes.id is not None:
                track_ids = boxes.id.int().cpu().tolist()
                coordinates = boxes.xyxy.cpu().tolist()
                
                for i, (box, track_id) in enumerate(zip(coordinates, track_ids)):
                    x1, y1, x2, y2 = box
                    tracks.append([int(x1), int(y1), int(x2), int(y2), track_id])
                    
                    if keypoints is not None:
                        kpts = keypoints[i].xy[0].tolist()
                        keypoints_list.append(kpts)
                    else:
                        keypoints_list.append([])
            else:
                # Fallback if no tracks identified but objects detected (rare in track mode)
                pass
                    
        return tracks, keypoints_list
