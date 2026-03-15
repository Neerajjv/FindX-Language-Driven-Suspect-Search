from PyQt6.QtWidgets import QFrame, QHBoxLayout, QVBoxLayout, QTextEdit, QPushButton, QSpinBox, QLabel
from PyQt6.QtCore import pyqtSignal, Qt

class SearchTextEdit(QTextEdit):
    submit_pressed = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setPlaceholderText("Enter search query (e.g., 'man in red shirt')...\nResults will appear below.")
        # Enable word wrap
        self.setLineWrapMode(QTextEdit.LineWrapMode.WidgetWidth)
        
    def keyPressEvent(self, event):
        # Enter key sends the search, Shift+Enter adds a new line
        if event.key() == Qt.Key.Key_Return or event.key() == Qt.Key.Key_Enter:
            if not event.modifiers() & Qt.KeyboardModifier.ShiftModifier:
                self.submit_pressed.emit()
                return
        super().keyPressEvent(event)

class TopBar(QFrame):
    search_triggered = pyqtSignal(str, int) # query, top_k

    def __init__(self):
        super().__init__()
        self.setObjectName("top_bar")
        
        # Main layout (Vertical)
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(5)
        
        # Title Label
        self.title_label = QLabel("FindX")
        self.title_label.setObjectName("title_label")
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.main_layout.addWidget(self.title_label)
        
        # Controls Layout (Horizontal)
        self.controls_layout = QHBoxLayout()
        self.controls_layout.setContentsMargins(0, 0, 0, 0)
        
        self.search_input = SearchTextEdit()
        self.search_input.setMinimumHeight(60) 
        self.search_input.setMaximumHeight(80)
        self.search_input.setObjectName("search_input")
        
        # Connect the custom signal for Enter key
        self.search_input.submit_pressed.connect(self.on_search)
        
        self.controls_layout.addWidget(self.search_input, stretch=1)
        
        # Max Results Filter
        self.controls_layout.addWidget(QLabel("Max Results:"))
        self.spin_k = QSpinBox()
        self.spin_k.setRange(1, 100)
        self.spin_k.setValue(10)
        self.controls_layout.addWidget(self.spin_k)
        
        self.btn_search = QPushButton("Search")
        self.btn_search.clicked.connect(self.on_search)
        self.controls_layout.addWidget(self.btn_search)
        
        self.main_layout.addLayout(self.controls_layout)

    def on_search(self):
        text = self.search_input.toPlainText().strip()
        k = self.spin_k.value()
        if text:
            self.search_triggered.emit(text, k)
