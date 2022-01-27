from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QWidget, QPushButton, QApplication, QGridLayout
import sys

 
class PyQtLayout(QWidget):
 
    def __init__(self):
        super().__init__()
        self.UI()
 
    def UI(self):
        Button1 = QPushButton('Up')
        Button2 = QPushButton('Left')
        Button3 = QPushButton('Right')
        Button4 = QPushButton('Down')
         
        grid = QGridLayout()
        grid.addWidget(Button1, 0, 1)
        grid.addWidget(Button2, 1, 0)
        grid.addWidget(Button3, 1, 2)
        grid.addWidget(Button4, 1, 1)

        grid.setSpacing(0)
 
        self.setLayout(grid)
        self.setGeometry(300, 300, 200, 200)
        self.setWindowTitle('PyQt5 Layout')
        self.show()
 
def main():
    app = QApplication(sys.argv)
    ex = PyQtLayout()
    sys.exit(app.exec_())
 
if __name__ == '__main__':
    main()