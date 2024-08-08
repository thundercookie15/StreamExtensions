from PyQt6.QtWidgets import QApplication, QMainWindow

import sys

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Stream Extensions")


app = QApplication(sys.argv)

window = MainWindow()
window.show()

app.exec()
