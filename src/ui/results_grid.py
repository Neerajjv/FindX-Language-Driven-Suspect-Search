
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QScrollArea, QGridLayout, 
                            QFrame, QLabel)
from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtGui import QPixmap, QImage
from PIL import Image

class ResultCard(QFrame):
    clicked = pyqtSignal(dict) 

    def __init__(self, metadata, image_pil):
        super().__init__()
        self.setObjectName("result_card")
        self.metadata = metadata
        self.setFixedSize(160, 220)
        
        layout = QVBoxLayout(self)
        self.img_label = QLabel()
        self.img_label.setFixedSize(148, 148)
        self.img_label.setScaledContents(True)
        img_qt = self.pil2pixmap(image_pil)
        self.img_label.setPixmap(img_qt)
        layout.addWidget(self.img_label)
        
        layout.addWidget(QLabel(f"Sim: {metadata.get('score', 0):.2f}"))

    def mousePressEvent(self, event):
        self.clicked.emit(self.metadata)

    def pil2pixmap(self, im):
        if im.mode == "RGB":
            im = im.convert("RGBA")
        
        data = im.tobytes("raw", "BGRA")
        qim = QImage(data, im.size[0], im.size[1], QImage.Format.Format_ARGB32)
        return QPixmap.fromImage(qim)

class ResultsGrid(QScrollArea):
    item_clicked = pyqtSignal(dict)

    def __init__(self):
        super().__init__()
        self.setWidgetResizable(True)
        self.container = QWidget()
        self.container.setObjectName("results_container")
        self.grid = QGridLayout(self.container)
        self.setWidget(self.container)
        self.cards = []

    def clear_results(self):
        for i in reversed(range(self.grid.count())): 
            self.grid.itemAt(i).widget().setParent(None)
        self.cards = []

    def add_card(self, metadata, image_pil):
        card = ResultCard(metadata, image_pil)
        card.clicked.connect(self.item_clicked.emit)
        row = len(self.cards) // 3
        col = len(self.cards) % 3
        self.grid.addWidget(card, row, col)
        self.cards.append(card)
