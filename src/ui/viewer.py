
from PyQt6.QtWidgets import QFrame, QVBoxLayout, QLabel, QHBoxLayout, QPushButton, QSizePolicy, QProgressBar
from PyQt6.QtCore import Qt, QTimer, QThread, pyqtSignal, QRect, QPoint, QSize
from PyQt6.QtGui import QImage, QPixmap, QPainter, QPen, QColor, QAction
import cv2
import numpy as np
from PIL import Image

def calculate_iou(box1, box2):
    # box: [x1, y1, x2, y2]
    x1 = max(box1[0], box2[0])
    y1 = max(box1[1], box2[1])
    x2 = min(box1[2], box2[2])
    y2 = min(box1[3], box2[3])
    
    intersection = max(0, x2 - x1) * max(0, y2 - y1)
    area1 = (box1[2] - box1[0]) * (box1[3] - box1[1])
    area2 = (box2[2] - box2[0]) * (box2[3] - box2[1])
    
    union = area1 + area2 - intersection
    if union == 0: return 0
    return intersection / union

class AnalysisWorker(QThread):
    finished = pyqtSignal(dict, int) # cache, target_id
    progress = pyqtSignal(int)

    def __init__(self, video_path, start_ms, end_ms, target_ms, target_bbox, detector):
        super().__init__()
        self.video_path = video_path
        self.start_ms = start_ms
        self.end_ms = end_ms
        self.target_ms = target_ms
        self.target_bbox = target_bbox
        self.detector = detector

    def run(self):
        cap = cv2.VideoCapture(self.video_path)
        cap.set(cv2.CAP_PROP_POS_MSEC, self.start_ms)
        
        frame_data = [] # (frame_idx, tracks, kpts)
        target_track_id = -1
        
        frames_to_process = 0
        # Estimate frames
        fps = cap.get(cv2.CAP_PROP_FPS) or 30
        duration_sec = (self.end_ms - self.start_ms) / 1000
        total_frames = int(duration_sec * fps)
        
        current_frame = 0
        
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret: break
            
            timestamp = cap.get(cv2.CAP_PROP_POS_MSEC)
            if timestamp > self.end_ms: break
            
            tracks, kpts = self.detector.track(frame)
            frame_idx = int(cap.get(cv2.CAP_PROP_POS_FRAMES)) - 1
            
            # Check for target match
            if abs(timestamp - self.target_ms) < 1000: # Within 1 sec buffer to find match
                 # If we haven't found a definitively strong match yet, or if we are closer to target time...
                 # Ideally, we find the track that overlaps target_bbox the most at target_ms.
                 # But target_ms is a single point.
                 
                 # Simple logic: closest frame to target_ms dictates the ID.
                 if abs(timestamp - self.target_ms) < (1000 / fps): # Closest frame
                     best_iou = 0
                     for t in tracks:
                         # t: [x1, y1, x2, y2, id]
                         iou = calculate_iou(self.target_bbox, t[:4])
                         if iou > best_iou:
                             best_iou = iou
                             if iou > 0.3:
                                 target_track_id = int(t[4])

            frame_data.append((frame_idx, tracks, kpts))
            
            current_frame += 1
            self.progress.emit(int(current_frame / total_frames * 100))

        cap.release()
        
        # Build cache
        cache = {}
        if target_track_id != -1:
            for f_idx, tracks, kpts_list in frame_data:
                for i, t in enumerate(tracks):
                    if int(t[4]) == target_track_id:
                         # Found the person
                         cache[f_idx] = (t[:4], kpts_list[i])
                         break
        
        self.finished.emit(cache, target_track_id)

class SelectableLabel(QLabel):
    selection_finished = pyqtSignal(QRect)

    def __init__(self):
        super().__init__()
        self.start_pos = None
        self.current_pos = None
        self.is_selecting = False
        self.active = False # Selection mode active?

    def set_active(self, active):
        self.active = active
        if active:
            self.setCursor(Qt.CursorShape.CrossCursor)
        else:
            self.setCursor(Qt.CursorShape.ArrowCursor)
            self.start_pos = None
            self.current_pos = None
            self.update()

    def mousePressEvent(self, event):
        if self.active and event.button() == Qt.MouseButton.LeftButton:
            self.is_selecting = True
            self.start_pos = event.pos()
            self.current_pos = event.pos()
            self.update()
        else:
            super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self.active and self.is_selecting:
            self.current_pos = event.pos()
            self.update()
        else:
            super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if self.active and self.is_selecting and event.button() == Qt.MouseButton.LeftButton:
            self.is_selecting = False
            self.current_pos = event.pos()
            rect = QRect(self.start_pos, self.current_pos).normalized()
            # Only emit if decent size
            if rect.width() > 5 and rect.height() > 5:
                self.selection_finished.emit(rect)
            self.update()
            
            # Auto-disable selection after one selection? 
            # Often better to stay in mode or let parent decide. 
            # Here we let parent decide.
        else:
            super().mouseReleaseEvent(event)

    def paintEvent(self, event):
        super().paintEvent(event)
        if self.active and self.start_pos and self.current_pos:
            painter = QPainter(self)
            painter.setPen(QPen(Qt.GlobalColor.red, 2, Qt.PenStyle.SolidLine))
            rect = QRect(self.start_pos, self.current_pos).normalized()
            painter.drawRect(rect)

class VideoViewer(QFrame):
    crop_selected = pyqtSignal(object) # Emit PIL Image

    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        
        self.display_label = SelectableLabel()
        self.display_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.display_label.setStyleSheet("background-color: black;")
        self.display_label.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Ignored)
        self.display_label.selection_finished.connect(self.on_selection)
        self.layout.addWidget(self.display_label)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setStyleSheet("QProgressBar {height: 5px; text-align: center; background: #333; color: white;} QProgressBar::chunk {background-color: #0078d7;}")
        self.layout.addWidget(self.progress_bar)

        controls = QHBoxLayout()
        self.btn_play = QPushButton("Play")
        self.btn_play.clicked.connect(self.play)
        controls.addWidget(self.btn_play)
        self.btn_pause = QPushButton("Pause")
        self.btn_pause.clicked.connect(self.pause)
        controls.addWidget(self.btn_pause)
        self.layout.addLayout(controls)

        self.cap = None
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)
        self.detector = None
        self.analysis_worker = None
        self.detection_cache = {}
        self.start_ms = 0
        self.current_frame_cv2 = None
        self.current_pixmap_rect = QRect() # The rect of the image drawn inside label

    def set_detector(self, detector):
        self.detector = detector

    def enable_selection_mode(self):
        self.pause()
        self.display_label.set_active(True)

    def on_selection(self, rect):
        # rect is in label coordinates
        # Map to image coordinates
        if self.current_frame_cv2 is None: return
        
        # We need to know where the image is drawn.
        # It's centered. calculation in update_frame:
        # pix.scaled(target_size, KeepAspect...)
        
        # Re-verify layout
        lbl_size = self.display_label.size()
        img_h, img_w = self.current_frame_cv2.shape[:2]
        if img_w == 0 or img_h == 0: return
        
        # Calculate scaled dimensions
        scale_w = lbl_size.width() / img_w
        scale_h = lbl_size.height() / img_h
        scale = min(scale_w, scale_h)
        
        disp_w = int(img_w * scale)
        disp_h = int(img_h * scale)
        
        # Offsets
        off_x = (lbl_size.width() - disp_w) // 2
        off_y = (lbl_size.height() - disp_h) // 2
        
        # Map rect
        rx = rect.x() - off_x
        ry = rect.y() - off_y
        rw = rect.width()
        rh = rect.height()
        
        # Normalize to image coords
        ix1 = int(rx / scale)
        iy1 = int(ry / scale)
        ix2 = int((rx + rw) / scale)
        iy2 = int((ry + rh) / scale)
        
        # Clip
        ix1 = max(0, min(ix1, img_w))
        iy1 = max(0, min(iy1, img_h))
        ix2 = max(0, min(ix2, img_w))
        iy2 = max(0, min(iy2, img_h))
        
        if ix2 > ix1 and iy2 > iy1:
            crop = self.current_frame_cv2[iy1:iy2, ix1:ix2]
            crop_rgb = cv2.cvtColor(crop, cv2.COLOR_BGR2RGB)
            self.crop_selected.emit(Image.fromarray(crop_rgb))
            
        self.display_label.set_active(False)

    def load_video(self, video_path, timestamp_ms, bbox):
        self.stop()
        self.detection_cache = {}
        
        if not self.detector or not bbox:
            self.start_playback(video_path, max(0, timestamp_ms - 2000))
            return

        self.display_label.setText("Analyzing...")
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.btn_play.setEnabled(False)
        self.btn_pause.setEnabled(False)
        
        self.start_ms = max(0, timestamp_ms - 2000)
        end_ms = timestamp_ms + 4000 
        
        self.analysis_worker = AnalysisWorker(video_path, self.start_ms, end_ms, timestamp_ms, bbox, self.detector)
        self.analysis_worker.progress.connect(self.progress_bar.setValue)
        self.analysis_worker.finished.connect(lambda cache, tid: self.on_analysis_complete(cache, tid, video_path))
        self.analysis_worker.start()

    def on_analysis_complete(self, cache, tid, video_path):
        self.detection_cache = cache
        self.progress_bar.setVisible(False)
        self.btn_play.setEnabled(True)
        self.btn_pause.setEnabled(True)
        self.start_playback(video_path, self.start_ms)

    def start_playback(self, video_path, start_ms):
        self.cap = cv2.VideoCapture(video_path)
        self.cap.set(cv2.CAP_PROP_POS_MSEC, start_ms)
        self.play()

    def update_frame(self):
        if self.cap is None or not self.cap.isOpened(): return
        ret, frame = self.cap.read()
        if not ret: 
            self.cap.set(cv2.CAP_PROP_POS_MSEC, self.start_ms)
            return
        
        self.current_frame_cv2 = frame.copy()
        frame_vis = frame.copy()
        
        frame_idx = int(self.cap.get(cv2.CAP_PROP_POS_FRAMES)) - 1
        
        if frame_idx in self.detection_cache:
            bbox, kpts = self.detection_cache[frame_idx]
            x1, y1, x2, y2 = bbox
            cv2.rectangle(frame_vis, (x1, y1), (x2, y2), (0, 255, 0), 2)
            
            for kp in kpts:
                if len(kp) >= 2:
                    kx, ky = int(kp[0]), int(kp[1])
                    if kx != 0 and ky != 0:
                        cv2.circle(frame_vis, (kx, ky), 3, (0, 0, 255), -1)

        h, w, ch = frame_vis.shape
        bytes_per_line = ch * w
        q_img = QImage(frame_vis.data, w, h, bytes_per_line, QImage.Format.Format_BGR888)
        
        if not self.display_label.size().isEmpty():
            target_size = self.display_label.size()
            self.display_label.setPixmap(QPixmap.fromImage(q_img).scaled(target_size, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        else:
             self.display_label.setPixmap(QPixmap.fromImage(q_img))

    def play(self):
        self.display_label.set_active(False)
        self.timer.start(30)

    def pause(self):
        self.timer.stop()

    def stop(self):
        self.pause()
        if self.cap: self.cap.release(); self.cap = None
