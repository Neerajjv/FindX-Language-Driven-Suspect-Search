

# Modern Dark Theme Palette
# Backgrounds: #1e1e24, #25252d
# Accents: #00d4ff (Cyan), #007acc (Blue)
# Text: #e0e0e0

DARK_THEME = """
/* Global Reset */
QWidget {
    font-family: "Segoe UI", "Roboto", sans-serif;
    font-size: 14px;
    background-color: #1e1e24; /* Deep dark blue-grey */
    color: #e0e0e0;
    outline: none;
}

/* Main Window & Central Widget */
QMainWindow, QWidget#central_widget {
    background-color: #1e1e24;
}

/* Tooltips */
QToolTip {
    background-color: #33333d;
    color: #ffffff;
    border: 1px solid #444455;
    padding: 4px;
    border-radius: 4px;
}

/* -------------------------------------------------------------------
   FRAMES & PANELS 
------------------------------------------------------------------- */
QFrame {
    border: none;
}

/* Sidebar */
QFrame#sidebar {
    background-color: #25252d;
    border-right: 1px solid #33333d;
}

/* Top Bar */
QFrame#top_bar {
    background-color: #25252d;
    border-bottom: 1px solid #33333d;
    padding: 10px;
}

/* Results Grid & Viewer Areas */
QScrollArea {
    background-color: transparent;
    border: none;
}
QWidget#results_container {
    background-color: transparent;
}

QFrame#video_viewer, QFrame#restoration_panel {
    background-color: #25252d;
    border: 1px solid #33333d;
    border-radius: 8px; /* Softer corners */
    margin: 4px;
}

/* Result Card */
QFrame#result_card {
    background-color: #2a2a35;
    border: 1px solid #3a3a45;
    border-radius: 8px;
    padding: 5px;
}
QFrame#result_card:hover {
    background-color: #323240;
    border: 1px solid #00d4ff; /* Cyan glow on hover */
}

/* -------------------------------------------------------------------
   BUTTONS
------------------------------------------------------------------- */
QPushButton {
    background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #3a3a45, stop:1 #2a2a35);
    color: #ffffff;
    border: 1px solid #444455;
    padding: 8px 16px;
    border-radius: 6px;
    font-weight: 600;
}
QPushButton:hover {
    background-color: #4a4a55;
    border-color: #555566;
}
QPushButton:pressed {
    background-color: #22222a;
    border-color: #00d4ff;
}
QPushButton:disabled {
    background-color: #22222a;
    color: #666666;
    border-color: #333333;
}

/* Primary Action Buttons (if we add a specific class/id later) */
QPushButton#btn_primary {
    background-color: #007acc;
    border: 1px solid #006bb3;
}
QPushButton#btn_primary:hover {
    background-color: #008ae6;
}

/* -------------------------------------------------------------------
   INPUTS (TextEdit, LineEdit, SpinBox)
------------------------------------------------------------------- */
QLineEdit, QTextEdit, QSpinBox, QPlainTextEdit {
    background-color: #1a1a20;
    border: 1px solid #3a3a45;
    border-radius: 6px;
    padding: 6px;
    color: #ffffff;
    selection-background-color: #007acc;
}
QLineEdit:focus, QTextEdit:focus, QSpinBox:focus {
    border: 1px solid #00d4ff;
    background-color: #15151a;
}

/* SpinBox Arrows */
QSpinBox::up-button, QSpinBox::down-button {
    background-color: transparent;
    border: none;
    width: 20px;
}
QSpinBox::up-button:hover, QSpinBox::down-button:hover {
    background-color: #333340;
    border-radius: 2px;
}

/* -------------------------------------------------------------------
   LISTS & TREES
------------------------------------------------------------------- */
QListWidget {
    background-color: #1a1a20;
    border: 1px solid #3a3a45;
    border-radius: 6px;
    outline: none;
}
QListWidget::item {
    padding: 8px;
    border-bottom: 1px solid #2a2a35;
}
QListWidget::item:selected {
    background-color: rgba(0, 122, 204, 0.4);
    border-left: 3px solid #00d4ff;
    color: #ffffff;
}
QListWidget::item:hover:!selected {
    background-color: #2a2a35;
}

/* -------------------------------------------------------------------
   SCROLLBARS
------------------------------------------------------------------- */
QScrollBar:vertical {
    border: none;
    background: #1e1e24;
    width: 10px;
    margin: 0px; 0px; 0px; 0px;
}
QScrollBar::handle:vertical {
    background: #444455;
    min-height: 20px;
    border-radius: 5px;
}
QScrollBar::handle:vertical:hover {
    background: #555566;
}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}

/* -------------------------------------------------------------------
   OTHER
------------------------------------------------------------------- */
QLabel {
    color: #dddddd;
}
QLabel#title_label {
    font-size: 24px;
    font-weight: bold;
    color: #00d4ff; /* Cyan Title */
    margin-bottom: 10px;
}
QLabel#section_header {
    font-size: 16px;
    font-weight: 600;
    color: #ffffff;
    margin-top: 10px;
    margin-bottom: 5px;
}

/* Progress Bar */
QProgressBar {
    border: 1px solid #444455;
    border-radius: 4px;
    text-align: center;
    background-color: #1a1a20;
}
QProgressBar::chunk {
    background-color: #007acc;
    width: 10px;
}
"""

