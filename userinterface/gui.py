import sys
from PyQt6.QtWidgets import QMainWindow, QApplication
from PyQt6 import uic


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi("userinterface/ui/mainwindow.ui", self)
        

    def init_ui(self):
        self.setWindowTitle("Stream Extensions")
        self.setFixedSize(800, 600)

app = QApplication(sys.argv)
window = MainWindow()
window.show()

app.exec()