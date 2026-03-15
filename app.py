
import sys
import os
from PyQt6.QtWidgets import QApplication

# Ensure src is in path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))
from ui.main_window import MainWindow

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
