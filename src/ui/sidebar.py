
from PyQt6.QtWidgets import QFrame, QVBoxLayout, QPushButton, QLabel, QListWidget
from PyQt6.QtCore import pyqtSignal
import os
import sys

# Add src to path for config
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config

class Sidebar(QFrame):
    mode_changed = pyqtSignal(str) 
    action_triggered = pyqtSignal(str) 
    file_selected = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.setObjectName("sidebar")
        self.setFixedWidth(200) # Ensure sidebar has some width
        self.layout = QVBoxLayout(self)
        self.layout.setSpacing(10)
        
        self.btn_upload = QPushButton("Upload Video")
        self.btn_upload.clicked.connect(lambda: self.handle_mode("upload"))
        self.layout.addWidget(self.btn_upload)

        self.btn_scan = QPushButton("Scan CCTV Folder")
        self.btn_scan.clicked.connect(lambda: self.handle_mode("cctv"))
        self.layout.addWidget(self.btn_scan)
        
        # File List Area
        self.lbl_files = QLabel("CCTV Files:")
        self.lbl_files.setObjectName("section_header")
        self.layout.addWidget(self.lbl_files)
        
        self.file_list = QListWidget()
        self.file_list.setObjectName("file_list")
        self.file_list.itemClicked.connect(self.on_file_clicked)
        self.layout.addWidget(self.file_list)
        
        self.lbl_status = QLabel("Ready")
        self.lbl_status.setWordWrap(True)
        self.layout.addWidget(self.lbl_status)
        
        self.populate_files()

    def populate_files(self):
        self.file_list.clear()
        if os.path.exists(config.CCTV_FOLDER):
            try:
                files = sorted([f for f in os.listdir(config.CCTV_FOLDER) 
                              if f.lower().endswith(('.mp4', '.avi', '.mkv'))])
                self.file_list.addItems(files)
                self.lbl_files.setText(f"CCTV Files ({len(files)}):")
            except Exception as e:
                self.lbl_status.setText(f"Error listing files: {e}")
        else:
            self.lbl_status.setText("CCTV folder not found")

    def on_file_clicked(self, item):
        # Optional: Emit a signal if we want to preview the video when clicked
        # For now just logging or ready for expansion
        full_path = os.path.join(config.CCTV_FOLDER, item.text())
        self.file_selected.emit(full_path)

    def handle_mode(self, mode):
        self.action_triggered.emit("upload_file" if mode == "upload" else "scan")
        self.mode_changed.emit(mode)

    def set_scan_enabled(self, enabled):
        self.btn_scan.setEnabled(enabled)
