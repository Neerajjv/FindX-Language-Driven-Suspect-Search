
import sys
import os
from PyQt6.QtWidgets import (QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, 
                             QFileDialog, QMessageBox, QProgressDialog)
from PyQt6.QtCore import Qt, QThread, pyqtSignal

# Add src to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config
from ui.styles import DARK_THEME
from ui.sidebar import Sidebar
from ui.top_bar import TopBar
from ui.results_grid import ResultsGrid
from ui.viewer import VideoViewer
from ui.restoration_panel import RestorationPanel
from core.encoder import CLIPEncoder
from core.indexer import IndexManager
from core.processor import VideoProcessor

class IndexingWorker(QThread):
    progress = pyqtSignal(int)
    finished = pyqtSignal(list, list)

    def __init__(self, mode, path, encoder, processor):
        super().__init__()
        self.mode = mode
        self.path = path
        self.encoder = encoder
        self.processor = processor

    def run(self):
        videos = []
        if self.mode == 'cctv':
            if os.path.exists(self.path):
                for f in os.listdir(self.path):
                    if f.lower().endswith(('.mp4', '.avi', '.mkv')):
                        videos.append(os.path.join(self.path, f))
        else:
            videos = [self.path]

        all_crops = []
        all_meta = []
        
        total_videos = len(videos)
        for i, video_path in enumerate(videos):
            for crop, meta in self.processor.process_video(video_path):
                all_crops.append(crop)
                all_meta.append(meta)
            self.progress.emit(int((i + 1) / (total_videos or 1) * 50))

        if all_crops:
            BATCH_SIZE = 32
            embeddings = []
            for i in range(0, len(all_crops), BATCH_SIZE):
                batch = all_crops[i:i+BATCH_SIZE]
                emb = self.encoder.encode_image(batch)
                embeddings.extend(emb)
                self.progress.emit(50 + int((i / len(all_crops)) * 50))
            self.finished.emit(embeddings, all_meta)
        else:
            self.finished.emit([], [])

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("FindX")
        self.resize(1200, 800)
        self.setStyleSheet(DARK_THEME)
        
        self.encoder = CLIPEncoder()
        self.processor = VideoProcessor() 
        self.index_manager = IndexManager(use_persistent=True)
        self.session_index = IndexManager(use_persistent=False)
        self.current_mode = "cctv"
        
        self.init_ui()
        
        if self.index_manager.index and self.index_manager.index.ntotal > 0:
            self.sidebar.set_scan_enabled(False)
            self.sidebar.lbl_status.setText(f"Index Ready ({self.index_manager.index.ntotal})")
        else:
            self.sidebar.set_scan_enabled(True)

    def init_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        layout = QHBoxLayout(central)
        
        self.sidebar = Sidebar()
        self.sidebar.mode_changed.connect(self.switch_mode)
        self.sidebar.action_triggered.connect(self.handle_action)
        layout.addWidget(self.sidebar)
        
        # Main content area (Right of Sidebar)
        content = QHBoxLayout()
        
        # Left Panel: TopBar + (Results & Viewer)
        left_panel = QVBoxLayout()
        
        self.top_bar = TopBar()
        self.top_bar.search_triggered.connect(self.search)
        left_panel.addWidget(self.top_bar)
        
        # Workspace: Results Grid + Video Viewer
        workspace = QHBoxLayout()
        workspace.setSpacing(10)
        
        self.results_grid = ResultsGrid()
        self.results_grid.setObjectName("results_grid")
        self.results_grid.item_clicked.connect(self.on_result)
        workspace.addWidget(self.results_grid, stretch=3)
        
        self.viewer = VideoViewer()
        self.viewer.setObjectName("video_viewer")
        self.viewer.set_detector(self.processor.detector)
        workspace.addWidget(self.viewer, stretch=4)
        
        left_panel.addLayout(workspace)
        
        # Add Left Panel to Main Content
        content.addLayout(left_panel, stretch=7)
        
        # Right Panel: Restoration
        self.restoration = RestorationPanel()
        self.restoration.setObjectName("restoration_panel")
        content.addWidget(self.restoration, stretch=2)
        
        # Connect signals
        self.restoration.manual_crop_requested.connect(self.viewer.enable_selection_mode)
        self.viewer.crop_selected.connect(self.restoration.set_image)
        
        layout.addLayout(content)

    def switch_mode(self, mode):
        self.current_mode = mode
        self.results_grid.clear_results()

    def handle_action(self, action):
        if action == "scan":
            self.worker = IndexingWorker('cctv', config.CCTV_FOLDER, self.encoder, self.processor)
            self.run_worker()
        elif action == 'upload_file':
            fname, _ = QFileDialog.getOpenFileName(self, "Video", "", "Videos (*.mp4)")
            if fname:
                self.current_video_path = fname
                self.worker = IndexingWorker('upload', fname, self.encoder, self.processor)
                self.run_worker()

    def run_worker(self):
        self.progress = QProgressDialog("Processing...", "Cancel", 0, 100, self)
        self.progress.show()
        self.worker.progress.connect(self.progress.setValue)
        self.worker.finished.connect(self.on_finished)
        self.worker.start()

    def on_finished(self, emb, meta):
        import numpy as np
        if emb:
            emb_np = np.stack(emb).astype('float32')
            if self.worker.mode == 'cctv':
                self.index_manager.add_items(emb_np, meta)
                self.index_manager.save_index()
                self.sidebar.set_scan_enabled(False)
            else:
                self.session_index.reset_index()
                self.session_index.add_items(emb_np, meta)
        self.progress.close()

    def search(self, text, top_k=10):
        import datetime
        def log(msg):
            with open("debug_search.txt", "a") as f:
                f.write(f"[{datetime.datetime.now()}] {msg}\n")
            print(msg)
            
        log(f"Search requested for '{text}' with limit {top_k}")
        idx = self.session_index if self.current_mode == 'upload' else self.index_manager
        
        if idx.index is None:
            log("Index is None")
            QMessageBox.warning(self, "Search Error", "Index is not initialized.")
            return

        if idx.index.ntotal == 0:
            log("Index is empty (ntotal=0)")
            QMessageBox.warning(self, "Search Error", "Index is empty. Please scan CCTV folder or upload a video.")
            return

        try:
            emb = self.encoder.encode_text(text).astype('float32')
            results = idx.search(emb, top_k=top_k)
            log(f"Found {len(results)} matches from index.")
            
            self.results_grid.clear_results()
            
            if not results:
                log("No results returned from index search.")
                QMessageBox.information(self, "Search", "No results found.")
                return

            import cv2
            from PIL import Image
            
            card_count = 0
            for i, res in enumerate(results):
                video_path = res['video_path']
                try:
                    if not os.path.exists(video_path):
                        log(f"Video file missing: {video_path}")
                        continue
                        
                    cap = cv2.VideoCapture(video_path)
                    cap.set(cv2.CAP_PROP_POS_MSEC, res['timestamp_ms'])
                    ret, frame = cap.read()
                    cap.release()
                    
                    if ret:
                        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                        pil = Image.fromarray(rgb)
                        x1, y1, x2, y2 = res['bbox']
                        # Ensure crop coords are valid
                        h, w = rgb.shape[:2]
                        x1, y1 = max(0, x1), max(0, y1)
                        x2, y2 = min(w, x2), min(h, y2)
                        
                        if x2 > x1 and y2 > y1:
                            crop = pil.crop((x1, y1, x2, y2))
                            self.results_grid.add_card(res, crop)
                            card_count += 1
                        else:
                             log(f"Invalid crop coords for result {i}: {x1},{y1},{x2},{y2} img {w}x{h}")
                    else:
                        log(f"Failed to read frame from {video_path} at {res['timestamp_ms']}")
                except Exception as e:
                    log(f"Error processing result {i}: {e}")
            
            log(f"Populated {card_count} cards.")
            
        except Exception as e:
            log(f"Search exception: {e}")
            import traceback
            traceback.print_exc()
            QMessageBox.critical(self, "Error", f"Search failed: {e}")

    def on_result(self, meta):
        self.viewer.load_video(meta['video_path'], meta['timestamp_ms'], meta['bbox'])
        
        import cv2
        from PIL import Image
        cap = cv2.VideoCapture(meta['video_path'])
        cap.set(cv2.CAP_PROP_POS_MSEC, meta['timestamp_ms'])
        ret, frame = cap.read()
        cap.release()
        if ret:
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            pil = Image.fromarray(rgb)
            x1, y1, x2, y2 = meta['bbox']
            crop = pil.crop((x1, y1, x2, y2))
            self.restoration.set_image(crop)
