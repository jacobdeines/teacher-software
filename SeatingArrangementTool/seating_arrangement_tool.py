from enum import Enum
import os.path
import pickle
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import sys
import ctypes


class RuleTypes(Enum):
    NONE = 0
    CANNOT_BE_NEXT_TO = 1
    CANNOT_BE_NEAR = 2
    MUST_BE_NEXT_TO = 3
    MUST_BE_NEAR = 4
    MUST_BE_IN_SPOT = 5

class Settings():
    user32 = ctypes.windll.user32
    screensize = user32.GetSystemMetrics(0), user32.GetSystemMetrics(1)
    WIDTH = int(screensize[0])
    HEIGHT = int(screensize[1])
    SUB_WIDTH = int((WIDTH * 2) / 3)
    SUB_HEIGHT = int((HEIGHT * 2)/ 3)
    SUB_X = int(WIDTH / 8)
    SUB_Y = int(HEIGHT / 8)

    DEFAULT_COLS = 30
    DEFAULT_ROWS = 25


class_list = []

editting_grid = [[0]*Settings.DEFAULT_COLS]*Settings.DEFAULT_ROWS


class PicToggleButton(QAbstractButton):
    def __init__(self, pixmap, pixmap_active, parent=None):
        super(PicToggleButton, self).__init__(parent)
        self.pixmap = pixmap
        self.pixmap_active = pixmap_active
        self.parent = parent

        self.pressed.connect(self.update)
        self.released.connect(self.update)

    def paintEvent(self, event):
        if not self.isChecked():
            pix = self.pixmap_active if self.underMouse() else self.pixmap
        else:
            pix = self.pixmap if self.underMouse() else self.pixmap_active

        painter = QPainter(self)
        painter.drawPixmap(event.rect(), pix)

    def enterEvent(self, event):
        self.update()

    def leaveEvent(self, event):
        self.update()


class ClassEditorWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.UI()
 
    def UI(self):
        global class_list

        # Class list editor
        self.student_list = QListWidget()
        for student in class_list:
            QListWidgetItem(student['name'], self.student_list)
        self.student_list.itemClicked.connect(self.nameClicked)

        self.name_input = QLineEdit()
        self.name_input.returnPressed.connect(self.onTextEnter)

        self.name_grid = QGridLayout()
        self.name_grid.addWidget(self.student_list, 0, 0)
        self.name_grid.addWidget(self.name_input, 1, 0)
        self.name_grid.setSpacing(5)

        self.name_widget = QWidget()
        self.name_widget.setLayout(self.name_grid)

        # Student editor
        self.student_editor_name = QLabel()
        self.student_editor_name.setText('')
        self.student_editor_name_font = QFont("Times", 22, QFont.Bold)
        self.student_editor_name.setFont(self.student_editor_name_font)
        self.student_editor_name.adjustSize()
        self.student_editor_name.setAlignment(Qt.AlignTop)

        self.student_editor_talkative_button = PicToggleButton(QPixmap("speech-bubble.png"), QPixmap("speech-bubble-fill.png"))
        self.student_editor_talkative_button.setMaximumSize(64, 64)
        self.student_editor_talkative_button.setCheckable(True)
        self.student_editor_talkative_button.setChecked(False)
        self.student_editor_talkative_button.clicked.connect(self.talkativeButtonHandler)

        self.student_editor_labels_grid = QGridLayout()
        self.student_editor_labels_grid.addWidget(self.student_editor_talkative_button, 0, 0)
        self.student_editor_labels_widget = QWidget()
        self.student_editor_labels_widget.setLayout(self.student_editor_labels_grid)

        self.student_editor_grid = QGridLayout()
        self.student_editor_grid.addWidget(self.student_editor_name, 0, 0)
        self.student_editor_grid.addWidget(self.student_editor_labels_widget, 1, 0)
        self.student_editor_grid.setRowStretch(0, 1)
        self.student_editor_grid.setRowStretch(1, 10)
        self.student_editor_grid.setSpacing(5)

        self.student_editor_widget = QWidget()
        self.student_editor_widget.setLayout(self.student_editor_grid)
        
        # Page layout
        self.name_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.name_widget.setMinimumWidth(int(Settings.SUB_WIDTH / 2))

        self.student_editor_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.name_widget.setMinimumWidth(int(Settings.SUB_WIDTH / 2))

        self.main_grid = QGridLayout()
        self.main_grid.addWidget(self.name_widget, 0, 0)
        self.main_grid.addWidget(self.student_editor_widget, 0, 1)
        self.student_editor_widget.hide()

        self.setLayout(self.main_grid)
        self.setGeometry(Settings.SUB_X, Settings.SUB_Y, Settings.SUB_WIDTH, Settings.SUB_HEIGHT)
        self.setWindowTitle('Class Editor')

    def nameClicked(self, item):
        global class_list

        for student in class_list:
            if student['name'] == item.text():
                self.student_editor_name.setText(item.text())
                self.student_editor_talkative_button.setChecked(student['talkative'])
                self.student_editor_widget.show()
                break

    def talkativeButtonHandler(self):
        global class_list

        for student in class_list:
            if student['name'] == self.student_editor_name.text():
                student['talkative'] = not student['talkative']
                self.student_editor_talkative_button.setChecked(student['talkative'])

    def onTextEnter(self):
        global class_list

        value = self.name_input.text()

        if value != '':
            duplicate = False
            for student in class_list:
                if student['name'] == value:
                    duplicate = True
            if not duplicate:
                local_dict = {'name': value}
                local_dict['talkative'] = False
                rules = []
                local_dict['rules'] = rules
                class_list.append(local_dict)
                QListWidgetItem(local_dict['name'], self.student_list)
            else:
                dup_msg = QMessageBox()
                dup_msg.setText('Cannot have duplicate student names')
                dup_msg.setIcon(QMessageBox.Warning)
                dup_msg.setWindowTitle(' ')
                dup_msg.exec_()
            self.name_input.clear()


class MainScreenWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.UI()
 
    def UI(self):
        global class_list
        global editting_grid

        self.class_editor = ClassEditorWidget()

        # Editting grid
        self.editting_grid_grid = QGridLayout()

        self.editting_grid_buttons = [[0]*Settings.DEFAULT_COLS]*Settings.DEFAULT_ROWS

        for row in range(Settings.DEFAULT_ROWS):
            for col in range(Settings.DEFAULT_COLS):
                self.editting_grid_buttons[row][col] = QPushButton('(' + str(row) + ',' + str(col) + ')')
                self.editting_grid_grid.addWidget(self.editting_grid_buttons[row][col], row, col)

        self.editting_grid_widget = QWidget()
        self.editting_grid_widget.setLayout(self.editting_grid_grid)
        self.editting_grid_widget.setMinimumWidth(Settings.SUB_WIDTH)

        # Menu
        self.class_editor_button = QPushButton('Class Editor')
        self.class_editor_button.clicked.connect(self.classEditorButtonHandler)

        self.menu_grid = QGridLayout()
        self.menu_grid.addWidget(self.class_editor_button, 0, 0)

        self.menu_widget = QWidget()
        self.menu_widget.setLayout(self.menu_grid)

        # Page layout
        self.main_grid = QGridLayout()
        self.main_grid.addWidget(self.editting_grid_widget, 0, 0)
        self.main_grid.addWidget(self.menu_widget, 0, 1)

        self.setLayout(self.main_grid)
        self.setWindowTitle('Seating Arrangement Tool')
        self.setWindowIcon(QIcon('chair.png'))
        self.showMaximized()

    def classEditorButtonHandler(self):
        self.class_editor.show()
        

def main():
    global class_list

    # Load data
    if os.path.exists('class_list.p'):
        with open('class_list.p', 'rb') as f:
            class_list = pickle.load(f)

    app = QApplication(sys.argv)
    ex = MainScreenWidget()

    exit_value = app.exec_()

    # Save data
    with open('class_list.p', 'wb') as f:
        pickle.dump(class_list, f)

    sys.exit(exit_value)


if __name__ == '__main__':
    main()
