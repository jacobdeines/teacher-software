from enum import Enum
import os.path
import pickle
from tkinter import E
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import sys
import ctypes


class Settings():
    user32 = ctypes.windll.user32
    screensize = user32.GetSystemMetrics(0), user32.GetSystemMetrics(1)
    WIDTH = int(screensize[0])
    HEIGHT = int(screensize[1])
    SUB_WIDTH = int((WIDTH * 2) / 3)
    SUB_HEIGHT = int((HEIGHT * 2)/ 3)
    MENU_WIDTH = int(WIDTH / 4)
    SUB_X = int(WIDTH / 8)
    SUB_Y = int(HEIGHT / 8)

    MIN_ROWS = 3
    MIN_COLS = 6
    
    MAX_ROWS = 15
    MAX_COLS = 30


class ListTypes(Enum):
    CLASS_LIST = 0
    ROOM_LAYOUT = 1


class RuleTypes(Enum):
    NONE = 0
    CANNOT_BE_NEXT_TO = 1
    CANNOT_BE_NEAR = 2
    MUST_BE_NEXT_TO = 3
    MUST_BE_NEAR = 4
    MUST_BE_IN_SPOT = 5


class PicToggleButton(QAbstractButton):
    def __init__(self, pixmap, pixmap_active, parent=None):
        super(PicToggleButton, self).__init__(parent)
        self.pixmap = pixmap
        self.pixmap_active = pixmap_active
        self.parent = parent

        self.setCheckable(True)
        self.setChecked(False)

        self.pressed.connect(self.update)
        self.released.connect(self.update)

        sizePolicy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        sizePolicy.setHeightForWidth(True)
        self.setSizePolicy(sizePolicy)

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

    def sizeHint(self):
        return QSize(64, 64)

    def heightForWidth(self, width):
        return width

    def resizeEvent(self, event):
        new_size = QSize(1, 1)
        new_size.scale(event.size(), Qt.KeepAspectRatio)
        self.resize(new_size)


class PicPushButton(QAbstractButton):
    def __init__(self, pixmap, parent=None):
        super(PicPushButton, self).__init__(parent)
        self.pixmap = pixmap
        self.parent = parent

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.drawPixmap(event.rect(), self.pixmap)


class ClassEditorWidget(QWidget):
    def __init__(self, filename):
        super().__init__()

        self.filename = filename
        self.class_name = filename.removesuffix('.p')

        self.class_list = []

        # Load data
        if os.path.exists('user_data/class_lists/' + self.filename):
            with open('user_data/class_lists/' + self.filename, 'rb') as f:
                 self.class_list = pickle.load(f)

        self.UI()
 
    def UI(self):
        self.class_name_label = QLabel(self.class_name)
        self.class_name_label_font = QFont("Times", 20)
        self.class_name_label.setFont(self.class_name_label_font)

        self.save_button = QPushButton('Save')
        self.save_button.clicked.connect(self.saveButtonHandler)

        self.class_name_grid = QGridLayout()
        self.class_name_grid.addWidget(self.class_name_label, 0, 0)
        self.class_name_grid.addWidget(self.save_button, 0, 1)

        self.class_name_widget = QWidget()
        self.class_name_widget.setLayout(self.class_name_grid)

        # Class list
        self.student_list = QListWidget()
        for student in self.class_list:
            QListWidgetItem(student['name'], self.student_list)
        self.student_list.itemClicked.connect(self.nameClicked)

        self.name_input = QLineEdit()
        self.name_input.returnPressed.connect(self.onTextEnter)

        self.name_grid = QGridLayout()
        self.name_grid.addWidget(self.class_name_widget, 0, 0)
        self.name_grid.addWidget(self.student_list, 1, 0)
        self.name_grid.addWidget(self.name_input, 2, 0)
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

        self.student_editor_talkative_button = PicToggleButton(QPixmap("assets/speech-bubble.png"), QPixmap("assets/speech-bubble-fill.png"))
        self.student_editor_talkative_button.setMaximumSize(64, 64)
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

    def saveButtonHandler(self):
        if self.filename == '':
            name_msg = QMessageBox()
            name_msg.setText('Name this class before saving')
            name_msg.setIcon(QMessageBox.Information)
            name_msg.setWindowTitle(' ')
            name_msg.exec_()
        else:
            with open('user_data/class_lists/' + self.filename, 'wb') as f:
                pickle.dump(self.class_list, f)


    def nameClicked(self, item):
        for student in self.class_list:
            if student['name'] == item.text():
                self.student_editor_name.setText(item.text())
                self.student_editor_talkative_button.setChecked(student['talkative'])
                self.student_editor_widget.show()
                break

    def talkativeButtonHandler(self):
        for student in self.class_list:
            if student['name'] == self.student_editor_name.text():
                student['talkative'] = not student['talkative']
                self.student_editor_talkative_button.setChecked(student['talkative'])

    def onTextEnter(self):
        value = self.name_input.text()

        if value != '':
            duplicate = False
            for student in self.class_list:
                if student['name'] == value:
                    duplicate = True
            if not duplicate:
                local_dict = {'name': value}
                local_dict['talkative'] = False
                rules = []
                local_dict['rules'] = rules
                self.class_list.append(local_dict)
                QListWidgetItem(local_dict['name'], self.student_list)
            else:
                dup_msg = QMessageBox()
                dup_msg.setText('Cannot have duplicate student names')
                dup_msg.setIcon(QMessageBox.Warning)
                dup_msg.setWindowTitle(' ')
                dup_msg.exec_()
            self.name_input.clear()


class RoomLayoutEditorWidget(QWidget):
    def __init__(self, filename):
        super().__init__()

        self.filename = filename
        self.layout_name = filename.removesuffix('.p')

        self.layout = {}

        # Load data
        if os.path.exists('user_data/room_layouts/' + self.filename):
            with open('user_data/room_layouts/' + self.filename, 'rb') as f:
                 self.layout = pickle.load(f)

        if {} == self.layout:
            self.layout['rows'] = Settings.MIN_ROWS
            self.layout['cols'] = Settings.MIN_COLS
            self.layout['list'] = []
            for i in range(Settings.MAX_ROWS):
                self.layout['list'].append([])
                for j in range(Settings.MAX_COLS):
                    self.layout['list'][i].append(0)

        self.UI()
 
    def UI(self):
        self.layout_name_label = QLabel(self.layout_name)
        self.layout_name_label_font = QFont("Times", 20)
        self.layout_name_label.setFont(self.layout_name_label_font)

        self.save_button = QPushButton('Save')
        self.save_button.clicked.connect(self.saveButtonHandler)

        self.clear_button = QPushButton('Clear')
        self.clear_button.clicked.connect(self.clearButtonHandler)

        self.layout_name_grid = QGridLayout()
        self.layout_name_grid.addWidget(self.layout_name_label, 0, 0)
        self.layout_name_grid.addWidget(self.save_button, 0, 1)
        self.layout_name_grid.addWidget(self.clear_button, 0, 2)

        self.layout_name_widget = QWidget()
        self.layout_name_widget.setLayout(self.layout_name_grid)
        self.layout_name_widget.setMaximumHeight(80)

        # Grid
        self.layout_grid = QGridLayout()
        self.cells = []
        for i in range(Settings.MAX_ROWS):
            self.cells.append([])
            for j in range(Settings.MAX_COLS):
                self.cells[i].append(PicToggleButton(QPixmap("assets/rounded_square.png"), QPixmap("assets/rounded_square_filled.png")))
                self.cells[i][j].clicked.connect(lambda state, arg=(i,j): self.gridCellButtonCallback(arg))
                if 1 == self.layout['list'][i][j]:
                    self.cells[i][j].setChecked(True)
                else:
                    self.cells[i][j].setChecked(False)
                self.layout_grid.addWidget(self.cells[i][j], i, j)

                if i >= self.layout['rows'] or j >= self.layout['cols']:
                     self.cells[i][j].hide()

        self.grid_widget = QWidget()
        self.grid_widget.setLayout(self.layout_grid)

        # Add/remove row/col buttons
        self.add_row_button = PicPushButton(QPixmap("assets/add.png"))
        self.add_row_button.setFixedSize(32, 32)
        self.add_row_button.clicked.connect(self.addRowButtonCallback)
        self.subtract_row_button = PicPushButton(QPixmap("assets/subtract.png"))
        self.subtract_row_button.setFixedSize(32, 32)
        self.subtract_row_button.clicked.connect(self.subtractRowButtonCallback)
        self.add_col_button = PicPushButton(QPixmap("assets/add.png"))
        self.add_col_button.setFixedSize(32, 32)
        self.add_col_button.clicked.connect(self.addColButtonCallback)
        self.subtract_col_button = PicPushButton(QPixmap("assets/subtract.png"))
        self.subtract_col_button.setFixedSize(32, 32)
        self.subtract_col_button.clicked.connect(self.subtractColButtonCallback)

        self.row_button_grid = QGridLayout()
        self.row_button_grid.addWidget(self.add_row_button, 0, 0)
        self.row_button_grid.addWidget(self.subtract_row_button, 0, 1)
        self.row_button_widget = QWidget()
        self.row_button_widget.setLayout(self.row_button_grid)
        self.row_button_widget.setMaximumHeight(50)
        
        self.col_button_grid = QGridLayout()
        self.col_button_grid.addWidget(self.add_col_button, 0, 0)
        self.col_button_grid.addWidget(self.subtract_col_button, 1, 0)
        self.col_button_widget = QWidget()
        self.col_button_widget.setLayout(self.col_button_grid)
        self.col_button_widget.setMaximumWidth(50)

        # Page layout
        self.main_grid = QGridLayout()
        self.main_grid.addWidget(self.layout_name_widget, 0, 0)
        self.main_grid.addWidget(self.grid_widget, 1, 0)
        self.main_grid.addWidget(self.row_button_widget, 2, 0)
        self.main_grid.addWidget(self.col_button_widget, 1, 1)

        self.setLayout(self.main_grid)
        self.setGeometry(Settings.SUB_X, Settings.SUB_Y, Settings.SUB_WIDTH, Settings.SUB_HEIGHT)
        self.setWindowTitle('Room Layout Editor')

    def saveButtonHandler(self):
        if self.filename == '':
            name_msg = QMessageBox()
            name_msg.setText('Name this layout before saving')
            name_msg.setIcon(QMessageBox.Information)
            name_msg.setWindowTitle(' ')
            name_msg.exec_()
        else:
            with open('user_data/room_layouts/' + self.filename, 'wb') as f:
                pickle.dump(self.layout, f)

    def clearButtonHandler(self):
        for i in range(Settings.MAX_ROWS):
            for j in range(Settings.MAX_COLS):
                self.cells[i][j].setChecked(False)
                self.layout['list'][i][j] = 0

    def gridCellButtonCallback(self, row_col):
        row = row_col[0]
        col = row_col[1]

        if 0 == self.layout['list'][row][col]:
            self.layout['list'][row][col] = 1
            self.cells[row][col].setChecked(True)
        else:
            self.layout['list'][row][col] = 0
            self.cells[row][col].setChecked(False)

    def addRowButtonCallback(self):
        if self.layout['rows'] + 1 <= Settings.MAX_ROWS:
            self.layout['rows'] = self.layout['rows'] + 1
            for j in range(self.layout['cols']):
                self.cells[self.layout['rows'] - 1][j].show()
            self.resetGrid()

    def subtractRowButtonCallback(self):
        if self.layout['rows'] - 1 >= Settings.MIN_ROWS:
            self.layout['rows'] = self.layout['rows'] - 1
            for j in range(self.layout['cols']):
                self.cells[self.layout['rows']][j].hide()
            self.resetGrid()

    def addColButtonCallback(self):
        if self.layout['cols'] + 1 <= Settings.MAX_COLS:
            self.layout['cols'] = self.layout['cols'] + 1
            for i in range(self.layout['rows']):
                self.cells[i][self.layout['cols'] - 1].show()
            self.resetGrid()

    def subtractColButtonCallback(self):
        if self.layout['cols'] - 1 >= Settings.MIN_COLS:
            self.layout['cols'] = self.layout['cols'] - 1
            for i in range(self.layout['rows']):
                self.cells[i][self.layout['cols']].hide()
            self.resetGrid()

    def resetGrid(self):
        for i in range(Settings.MAX_ROWS):
            for j in range(Settings.MAX_COLS):
                if i < self.layout['rows'] and j < self.layout['cols']:
                    if 1 == self.layout['list'][i][j]:
                        self.cells[i][j].setChecked(True)
                    else:
                        self.cells[i][j].setChecked(False)
                else:
                    self.layout['list'][i][j] = 0
                    self.cells[i][j].setChecked(False)


class ListWidget(QWidget):
    def __init__(self, directory, list_type, title):
        super().__init__()

        self.directory = directory
        self.list_type = list_type
        self.title = title

        self.list = QListWidget()

        for filename in os.listdir(self.directory):
            f = os.path.join(self.directory, filename)
            if os.path.isfile(f):
                QListWidgetItem(filename.removesuffix('.p'), self.list)

        self.list.itemClicked.connect(self.listItemClicked)

        self.selected_list_item_name = ''

        self.title_label = QLabel(self.title)
        self.title_label_font = QFont("Times", 20)
        self.title_label.setFont(self.title_label_font)

        self.edit_button = PicPushButton(QPixmap("assets/edit.png"))
        self.edit_button.setFixedSize(32, 32)
        self.edit_button.clicked.connect(self.editButtonHandler)

        self.add_button = PicPushButton(QPixmap("assets/add.png"))
        self.add_button.setFixedSize(32, 32)
        self.add_button.clicked.connect(self.addButtonHandler)

        self.delete_button = PicPushButton(QPixmap("assets/delete.png"))
        self.delete_button.setFixedSize(32, 32)
        self.delete_button.clicked.connect(self.deleteButtonHandler)

        self.button_layout = QHBoxLayout()
        self.button_layout.addWidget(self.add_button)
        self.button_layout.addWidget(self.edit_button)
        self.button_layout.addWidget(self.delete_button)

        self.button_widget = QWidget()
        self.button_widget.setLayout(self.button_layout)

        self.grid = QGridLayout()
        self.grid.addWidget(self.title_label, 0, 0)
        self.grid.addWidget(self.button_widget, 1, 0)
        self.grid.addWidget(self.list, 2, 0)

        self.setLayout(self.grid)

        self.show()

    def listItemClicked(self, item):
        self.selected_list_item_name = item.text()

    def editButtonHandler(self):
        if '' != self.selected_list_item_name:
            if ListTypes.CLASS_LIST == self.list_type:
                ex = ClassEditorWidget(self.selected_list_item_name + '.p')
                ex.show()
                loop = QEventLoop()
                ex.destroyed.connect(loop.quit)
                loop.exec()
            elif ListTypes.ROOM_LAYOUT == self.list_type:
                ex = RoomLayoutEditorWidget(self.selected_list_item_name + '.p')
                ex.show()
                loop = QEventLoop()
                ex.destroyed.connect(loop.quit)
                loop.exec()

    def addButtonHandler(self):
        name, exit_status = QInputDialog.getText(self, 'Input Dialog', 'Enter a name:')
        if exit_status and name != '':
            if ListTypes.CLASS_LIST == self.list_type:
                empty_list = []
                with open('user_data/class_lists/' + name + '.p', 'wb') as f:
                        pickle.dump(empty_list, f)
            elif ListTypes.ROOM_LAYOUT == self.list_type:
                room_layout = {'rows' : Settings.MIN_ROWS, 'cols' : Settings.MIN_COLS}
                layout_list = []
                for i in range(Settings.MAX_ROWS):
                    layout_list.append([])
                    for j in range(Settings.MAX_COLS):
                        layout_list[i].append(0)
                room_layout['list'] = layout_list
                with open('user_data/room_layouts/' + name + '.p', 'wb') as f:
                        pickle.dump(room_layout, f)
            self.updateList()

    def deleteButtonHandler(self):
        if '' != self.selected_list_item_name:
            if ListTypes.CLASS_LIST == self.list_type:
                os.remove('user_data/class_lists/' + self.selected_list_item_name + '.p')
            elif ListTypes.ROOM_LAYOUT == self.list_type:
                os.remove('user_data/room_layouts/' + self.selected_list_item_name + '.p')
            self.updateList()

    def updateList(self):
        self.list.clear()
        for filename in os.listdir(self.directory):
            f = os.path.join(self.directory, filename)
            if os.path.isfile(f):
                QListWidgetItem(filename.removesuffix('.p'), self.list)
        self.selected_list_item_name = ''


class MainScreenWidget(QMainWindow):
    def __init__(self):
        super().__init__()
        self.UI()
 
    def UI(self):
        # Editting grid
        self.editting_grid_grid = QGridLayout()

        self.editting_grid_buttons = [[0]*Settings.MAX_COLS]*Settings.MAX_ROWS

        for row in range(Settings.MAX_ROWS):
            for col in range(Settings.MAX_COLS):
                self.editting_grid_buttons[row][col] = QPushButton('(' + str(row) + ',' + str(col) + ')')
                self.editting_grid_grid.addWidget(self.editting_grid_buttons[row][col], row, col)

        self.editting_grid_widget = QWidget()
        self.editting_grid_widget.setLayout(self.editting_grid_grid)
        self.editting_grid_widget.setMinimumWidth(Settings.SUB_WIDTH)

        # Menu
        self.class_lists = ListWidget('user_data/class_lists', ListTypes.CLASS_LIST, 'Class Lists')
        self.room_layouts = ListWidget('user_data/room_layouts', ListTypes.ROOM_LAYOUT, "Room Layouts")

        self.menu_grid = QGridLayout()
        self.menu_grid.addWidget(self.class_lists, 0, 0)
        self.menu_grid.addWidget(self.room_layouts, 1, 0)

        self.menu_widget = QWidget()
        self.menu_widget.setLayout(self.menu_grid)
        self.menu_widget.setMinimumWidth(Settings.MENU_WIDTH)

        # Page layout
        self.main_grid = QGridLayout()
        self.main_grid.addWidget(self.editting_grid_widget, 0, 0)
        self.main_grid.addWidget(self.menu_widget, 0, 1)

        self.main_grid_widget = QWidget()
        self.main_grid_widget.setLayout(self.main_grid)
        self.setCentralWidget(self.main_grid_widget)
        self.setWindowTitle('Seating Arrangement Tool')
        self.setWindowIcon(QIcon('assets/chair.png'))
        self.showMaximized()

    def classEditorButtonHandler(self):
        self.class_editor.show()

    def closeEvent(self, event):
        for window in QApplication.topLevelWidgets():
            window.close()
        

def main():
    app = QApplication(sys.argv)
    ex = MainScreenWidget()

    exit_value = app.exec_()

    sys.exit(exit_value)


if __name__ == '__main__':
    main()
