
from PyQt6.QtWidgets import (QFrame, QVBoxLayout, QLabel, QPushButton, QSlider, QHBoxLayout, 
                             QCheckBox, QLineEdit, QGroupBox, QWidget)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QPixmap, QImage
from PIL import Image
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.restoration import Restorer

class RestorationPanel(QFrame):
    manual_crop_requested = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.setFixedWidth(350)
        self.layout = QVBoxLayout(self)
        self.layout.setSpacing(10)
        
        # Preview Area
        self.preview_lbl = QLabel("No Image Selected")
        self.preview_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.preview_lbl.setMinimumHeight(200)
        self.preview_lbl.setStyleSheet("background-color: #2b2b2b; border-radius: 5px;")
        self.layout.addWidget(self.preview_lbl)
        
        # Controls Group
        controls = QGroupBox("Restoration Settings")
        c_layout = QVBoxLayout(controls)
        c_layout.setSpacing(8)
        
        # Checkboxes
        self.cb_align = QCheckBox("Pre_Face_Align")
        self.cb_align.setChecked(True)
        c_layout.addWidget(self.cb_align)
        
        self.cb_bg_enhance = QCheckBox("Background_Enhance")
        self.cb_bg_enhance.setChecked(True)
        c_layout.addWidget(self.cb_bg_enhance)
        
        self.cb_face_upsample = QCheckBox("Face_Upsample")
        self.cb_face_upsample.setChecked(True)
        c_layout.addWidget(self.cb_face_upsample)
        
        # Rescaling Factor
        scale_layout = QVBoxLayout()
        scale_layout.setSpacing(2)
        scale_lbl = QLabel("Rescaling_Factor (up to 4)")
        scale_lbl.setStyleSheet("color: #cccccc;")
        self.inp_scale = QLineEdit("2")
        scale_layout.addWidget(scale_lbl)
        scale_layout.addWidget(self.inp_scale)
        c_layout.addLayout(scale_layout)
        
        # Codeformer Fidelity
        fid_layout = QVBoxLayout()
        fid_layout.setSpacing(2)
        self.fid_lbl = QLabel("Codeformer_Fidelity (0.5)")
        self.fid_lbl.setStyleSheet("color: #cccccc;")
        
        h_fid = QHBoxLayout()
        self.slider_fid = QSlider(Qt.Orientation.Horizontal)
        self.slider_fid.setRange(0, 100)
        self.slider_fid.setValue(50)
        self.slider_fid.valueChanged.connect(self.update_fid_label)
        
        self.spin_fid = QLabel("0.5")
        self.spin_fid.setFixedWidth(30)
        
        h_fid.addWidget(QLabel("0"))
        h_fid.addWidget(self.slider_fid)
        h_fid.addWidget(QLabel("1"))
        h_fid.addWidget(self.spin_fid)
        
        fid_layout.addWidget(self.fid_lbl)
        fid_layout.addLayout(h_fid)
        c_layout.addLayout(fid_layout)
        
        self.layout.addWidget(controls)
        
        # Buttons
        btn_layout = VStack = QVBoxLayout()
        
        self.btn_manual_crop = QPushButton("Manual Crop ROI")
        self.btn_manual_crop.setToolTip("Select a region on the video viewer to crop")
        self.btn_manual_crop.clicked.connect(self.request_manual_crop)
        btn_layout.addWidget(self.btn_manual_crop)
        
        self.btn_do_restore = QPushButton("Enhance Image")
        self.btn_do_restore.setFixedHeight(40)
        self.btn_do_restore.setStyleSheet("background-color: #4a90e2; font-weight: bold;")
        self.btn_do_restore.clicked.connect(self.run_restoration)
        btn_layout.addWidget(self.btn_do_restore)
        
        self.layout.addLayout(btn_layout)
        self.layout.addStretch()
        
        self.current_crop_pil = None
        self.restorer = Restorer()

    def update_fid_label(self):
        val = self.slider_fid.value() / 100.0
        self.fid_lbl.setText(f"Codeformer_Fidelity ({val:.2f})")
        self.spin_fid.setText(f"{val:.2f}")

    def request_manual_crop(self):
        self.manual_crop_requested.emit()

    def set_image(self, image_pil):
        self.current_crop_pil = image_pil
        self.update_display(image_pil)

    def update_display(self, pil_img):
        if pil_img:
            if pil_img.mode == "RGB":
                pil_img = pil_img.convert("RGBA")
            
            data = pil_img.tobytes("raw", "BGRA")
            qim = QImage(data, pil_img.size[0], pil_img.size[1], QImage.Format.Format_ARGB32)
            
            # Scale to fit while keeping aspect ratio
            w, h = self.preview_lbl.width(), self.preview_lbl.height()
            pix = QPixmap.fromImage(qim).scaled(w, h, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            self.preview_lbl.setPixmap(pix)
        else:
            self.preview_lbl.setText("No Image")

    def run_restoration(self):
        if self.current_crop_pil:
            try:
                fidelity = self.slider_fid.value() / 100.0
                upscale = int(self.inp_scale.text())
                has_aligned = self.cb_align.isChecked()
                only_center_face = False # CodeFormer usually handles full image or face
                draw_up = self.cb_face_upsample.isChecked()
                bg_enhance = self.cb_bg_enhance.isChecked()
                
                self.btn_do_restore.setText("Processing...")
                self.btn_do_restore.setEnabled(False)
                from PyQt6.QtWidgets import QApplication
                QApplication.processEvents()
                
                import cv2
                restored_cv2_rgb = self.restorer.restore(
                    self.current_crop_pil, 
                    fidelity=fidelity,
                    upscale=upscale,
                    has_aligned=has_aligned,
                    bg_enhance=bg_enhance,
                    face_upsample=draw_up
                )
                
                restored_pil = Image.fromarray(restored_cv2_rgb)
                self.update_display(restored_pil)
            except Exception as e:
                print(f"Restoration failed: {e}")
            finally:
                self.btn_do_restore.setText("Enhance Image")
                self.btn_do_restore.setEnabled(True)
