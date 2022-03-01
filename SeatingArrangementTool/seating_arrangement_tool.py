from enum import Enum
import os.path
import pickle
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import sys
import random
import math


# Global settings values assigned here
MIN_ROWS = 3
MAX_ROWS = 15
MIN_COLS = 6
MAX_COLS = 30
MAX_COST = 1

# Global settings values assigned in main
WIDTH = 0
HEIGHT = 0
SUB_WIDTH = 0
SUB_HEIGHT = 0
MENU_WIDTH = 0
SUB_X = 0
SUB_Y = 0


class ListTypes(Enum):
    CLASS_LIST = 0
    ROOM_LAYOUT = 1


class PicPushButton(QAbstractButton):
    def __init__(self, pixmap, parent=None):
        super(PicPushButton, self).__init__(parent)
        self.pixmap = pixmap
        self.parent = parent

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.drawPixmap(event.rect(), self.pixmap)


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


class PicTextToggleButton(QAbstractButton):
    def __init__(self, pixmap, pixmap_active, text, parent=None):
        super(PicTextToggleButton, self).__init__(parent)
        self.pixmap = pixmap
        self.pixmap_active = pixmap_active
        self.text = text
        self.parent = parent

        self.setCheckable(True)
        self.setChecked(False)

        self.pressed.connect(self.update)
        self.released.connect(self.update)

        sizePolicy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        sizePolicy.setHeightForWidth(True)
        self.setSizePolicy(sizePolicy)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setFont(QFont('Times', 8))

        pix = self.pixmap
        if not self.isChecked():
            if self.underMouse():
                pix = self.pixmap_active
                painter.setPen(QColorConstants.White)
            else:
                pix = self.pixmap
                painter.setPen(QColorConstants.Black)
        else:
            if self.underMouse():
                pix = self.pixmap
                painter.setPen(QColorConstants.Black)
            else:
                pix = self.pixmap_active
                painter.setPen(QColorConstants.White)
        
        painter.drawPixmap(event.rect(), pix)
        painter.drawText(event.rect(), Qt.AlignCenter | Qt.TextWordWrap, self.text)

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

    def setText(self, text):
        self.text = text
        self.update()


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
        self.student_editor_talkative_label = QLabel('Talkative')
        self.student_editor_talkative_label.setAlignment(Qt.AlignLeft)
        self.student_editor_talkative_label.setAlignment(Qt.AlignVCenter)

        self.student_editor_front_button = PicToggleButton(QPixmap("assets/up-arrow.png"), QPixmap("assets/up-arrow-fill.png"))
        self.student_editor_front_button.setMaximumSize(64, 64)
        self.student_editor_front_button.clicked.connect(self.frontButtonHandler)
        self.student_editor_front_label = QLabel('Front of room')
        self.student_editor_front_label.setAlignment(Qt.AlignLeft)
        self.student_editor_front_label.setAlignment(Qt.AlignVCenter)

        self.student_editor_label_grid = QGridLayout()
        self.student_editor_label_grid.addWidget(self.student_editor_talkative_button, 0, 0)
        self.student_editor_label_grid.addWidget(self.student_editor_talkative_label, 0, 1)
        self.student_editor_label_grid.addWidget(self.student_editor_front_button, 1, 0)
        self.student_editor_label_grid.addWidget(self.student_editor_front_label, 1, 1)
        self.student_editor_labels_widget = QWidget()
        self.student_editor_labels_widget.setLayout(self.student_editor_label_grid)

        self.student_editor_delete_button = QPushButton("Delete Student")
        self.student_editor_delete_button.clicked.connect(self.deleteButtonHandler)

        self.student_editor_grid = QGridLayout()
        self.student_editor_grid.addWidget(self.student_editor_name, 0, 0, Qt.AlignTop)
        self.student_editor_grid.addWidget(self.student_editor_labels_widget, 1, 0)
        self.student_editor_grid.addWidget(self.student_editor_delete_button, 2, 0, Qt.AlignBottom)
        self.student_editor_grid.setSpacing(5)

        self.student_editor_widget = QWidget()
        self.student_editor_widget.setLayout(self.student_editor_grid)
        
        # Page layout
        self.name_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.name_widget.setMinimumWidth(int(SUB_WIDTH / 2))

        self.student_editor_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.name_widget.setMinimumWidth(int(SUB_WIDTH / 2))

        self.main_grid = QGridLayout()
        self.main_grid.addWidget(self.name_widget, 0, 0)
        self.main_grid.addWidget(self.student_editor_widget, 0, 1)
        self.student_editor_widget.hide()

        self.setLayout(self.main_grid)
        self.setGeometry(SUB_X, SUB_Y, SUB_WIDTH, SUB_HEIGHT)
        self.setWindowTitle('Class Editor')

    def saveButtonHandler(self):
        with open('user_data/class_lists/' + self.filename, 'wb') as f:
                pickle.dump(self.class_list, f)


    def nameClicked(self, item):
        for student in self.class_list:
            if student['name'] == item.text():
                self.student_editor_name.setText(item.text())
                self.student_editor_talkative_button.setChecked(student['talkative'])
                self.student_editor_front_button.setChecked(student['front'])
                self.student_editor_widget.show()
                break

    def deleteButtonHandler(self):
        for student in self.class_list:
            if student['name'] == self.student_editor_name.text():
                self.class_list.remove(student)
                self.student_list.clear()
                self.student_editor_name.setText('')
                self.student_editor_talkative_button.setChecked(False)
                self.student_editor_front_button.setChecked(False)
                self.student_editor_widget.hide()
                for student in self.class_list:
                    QListWidgetItem(student['name'], self.student_list)
                break

    def talkativeButtonHandler(self):
        for student in self.class_list:
            if student['name'] == self.student_editor_name.text():
                student['talkative'] = not student['talkative']
                self.student_editor_talkative_button.setChecked(student['talkative'])

    def frontButtonHandler(self):
        for student in self.class_list:
            if student['name'] == self.student_editor_name.text():
                student['front'] = not student['front']
                self.student_editor_front_button.setChecked(student['front'])

    def onTextEnter(self):
        value = self.name_input.text()

        if value != '':
            duplicate = False
            for student in self.class_list:
                if student['name'] == value:
                    duplicate = True
            if not duplicate:
                new_student = {'name': '', 'talkative' : False, 'front' : False }
                new_student['name'] = value
                self.class_list.append(new_student)
                QListWidgetItem(new_student['name'], self.student_list)
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
            self.layout['rows'] = MIN_ROWS
            self.layout['cols'] = MIN_COLS
            self.layout['list'] = []
            for i in range(MAX_ROWS):
                self.layout['list'].append([])
                for j in range(MAX_COLS):
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
        self.layout_name_widget.setMaximumHeight(150)

        # Grid
        self.layout_grid = QGridLayout()
        self.cells = []
        for i in range(MAX_ROWS):
            self.cells.append([])
            for j in range(MAX_COLS):
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
        self.setGeometry(SUB_X, SUB_Y, SUB_WIDTH, SUB_HEIGHT)
        self.setWindowTitle('Room Layout Editor')

    def saveButtonHandler(self):
        with open('user_data/room_layouts/' + self.filename, 'wb') as f:
                pickle.dump(self.layout, f)

    def clearButtonHandler(self):
        for i in range(MAX_ROWS):
            for j in range(MAX_COLS):
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
        if self.layout['rows'] + 1 <= MAX_ROWS:
            self.layout['rows'] = self.layout['rows'] + 1
            for j in range(self.layout['cols']):
                self.cells[self.layout['rows'] - 1][j].show()
            self.resetGrid()

    def subtractRowButtonCallback(self):
        if self.layout['rows'] - 1 >= MIN_ROWS:
            self.layout['rows'] = self.layout['rows'] - 1
            for j in range(self.layout['cols']):
                self.cells[self.layout['rows']][j].hide()
            self.resetGrid()

    def addColButtonCallback(self):
        if self.layout['cols'] + 1 <= MAX_COLS:
            self.layout['cols'] = self.layout['cols'] + 1
            for i in range(self.layout['rows']):
                self.cells[i][self.layout['cols'] - 1].show()
            self.resetGrid()

    def subtractColButtonCallback(self):
        if self.layout['cols'] - 1 >= MIN_COLS:
            self.layout['cols'] = self.layout['cols'] - 1
            for i in range(self.layout['rows']):
                self.cells[i][self.layout['cols']].hide()
            self.resetGrid()

    def resetGrid(self):
        for i in range(MAX_ROWS):
            for j in range(MAX_COLS):
                if i < self.layout['rows'] and j < self.layout['cols']:
                    if 1 == self.layout['list'][i][j]:
                        self.cells[i][j].setChecked(True)
                    else:
                        self.cells[i][j].setChecked(False)
                else:
                    self.layout['list'][i][j] = 0
                    self.cells[i][j].setChecked(False)


class FileListWidget(QWidget):
    def __init__(self, directory, list_type, title):
        super().__init__()

        self.directory = directory
        self.list_type = list_type
        self.title = title

        self.list = QListWidget()

        if os.path.isdir(directory):
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
        name, exit_status = QInputDialog.getText(self, 'New', 'Enter a name:')
        if exit_status and name != '':
            if ListTypes.CLASS_LIST == self.list_type:
                empty_list = []
                if False == os.path.isdir('user_data/class_lists/'):
                    os.makedirs('user_data/class_lists')
                with open('user_data/class_lists/' + name + '.p', 'wb') as f:
                        pickle.dump(empty_list, f)
            elif ListTypes.ROOM_LAYOUT == self.list_type:
                room_layout = {'rows' : MIN_ROWS, 'cols' : MIN_COLS}
                layout_list = []
                for i in range(MAX_ROWS):
                    layout_list.append([])
                    for j in range(MAX_COLS):
                        layout_list[i].append(0)
                room_layout['list'] = layout_list
                if False == os.path.isdir('user_data/room_layouts/'):
                    os.makedirs('user_data/room_layouts/')
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

    def getSelectedItemName(self):
        return self.selected_list_item_name


class MainScreenWidget(QMainWindow):
    def __init__(self):
        super().__init__()
        self.UI()
 
    def UI(self):
        # Grid
        self.layout = {}
        self.layout['rows'] = MIN_ROWS
        self.layout['cols'] = MIN_COLS
        self.layout['list'] = []
        for i in range(MAX_ROWS):
            self.layout['list'].append([])
            for j in range(MAX_COLS):
                place_dict = {'occupied' : 0, 'name' : ''}
                self.layout['list'][i].append(place_dict)

        self.layout_grid = QGridLayout()
        self.cells = []
        for i in range(MAX_ROWS):
            self.cells.append([])
            for j in range(MAX_COLS):
                self.cells[i].append(PicTextToggleButton(QPixmap("assets/rounded_square.png"), QPixmap("assets/rounded_square_filled.png"), ''))
                self.cells[i][j].clicked.connect(lambda state, arg=(i,j): self.gridCellButtonCallback(arg))
                self.cells[i][j].setChecked(False)
                self.layout_grid.addWidget(self.cells[i][j], i, j)
                self.cells[i][j].hide()

        self.grid_widget = QWidget()
        self.grid_widget.setLayout(self.layout_grid)
        self.grid_widget.setMinimumWidth(SUB_WIDTH)

        # Menu
        self.class_lists = FileListWidget('user_data/class_lists', ListTypes.CLASS_LIST, 'Class Lists')
        self.room_layouts = FileListWidget('user_data/room_layouts', ListTypes.ROOM_LAYOUT, "Room Layouts")

        self.generate_button = QPushButton('Generate')
        self.generate_button.clicked.connect(self.generateButtonCallback)

        self.clear_button = QPushButton('Clear')
        self.clear_button.clicked.connect(self.resetLayout)

        self.menu_grid = QGridLayout()
        self.menu_grid.addWidget(self.class_lists, 0, 0)
        self.menu_grid.addWidget(self.room_layouts, 1, 0)
        self.menu_grid.addWidget(self.generate_button, 2, 0)
        self.menu_grid.addWidget(self.clear_button, 3, 0)

        self.menu_widget = QWidget()
        self.menu_widget.setLayout(self.menu_grid)
        self.menu_widget.setMinimumWidth(MENU_WIDTH)

        # Page layout
        self.main_grid = QGridLayout()
        self.main_grid.addWidget(self.grid_widget, 0, 0)
        self.main_grid.addWidget(self.menu_widget, 0, 1)

        self.main_grid_widget = QWidget()
        self.main_grid_widget.setLayout(self.main_grid)
        self.setCentralWidget(self.main_grid_widget)
        self.setWindowTitle('Seating Arrangement Tool')
        self.setWindowIcon(QIcon('assets/chair.png'))
        self.showMaximized()

    def closeEvent(self, event):
        for window in QApplication.topLevelWidgets():
            window.close()

    def generateButtonCallback(self):
        class_list = []
        if os.path.exists('user_data/class_lists/' + self.class_lists.getSelectedItemName() + '.p'):
            with open('user_data/class_lists/' + self.class_lists.getSelectedItemName() + '.p', 'rb') as f:
                 class_list = pickle.load(f)
        room_layout = {}
        if os.path.exists('user_data/room_layouts/' + self.room_layouts.getSelectedItemName() + '.p'):
            with open('user_data/room_layouts/' + self.room_layouts.getSelectedItemName() + '.p', 'rb') as f:
                 room_layout = pickle.load(f)
        
        if class_list != [] and room_layout != {}:
            # Create a list of available seats
            available_seats = []
            row_ind = 0
            col_ind = 0
            for row in room_layout['list']:
                for col in row:
                    if room_layout['list'][row_ind][col_ind] == 1:
                        available_seats.append((row_ind, col_ind))
                    col_ind += 1
                row_ind += 1
                col_ind = 0

            if len(available_seats) == len(class_list):

                ############# Generate list of seat/student pairs #############
                pairs = []
                
                shuffled_class_list = []
                shuffled_class_list = class_list
                random.shuffle(shuffled_class_list)

                back_of_room = 0
                front_of_room = MAX_ROWS

                for seat in available_seats:
                    if seat[0] > back_of_room:
                        back_of_room = seat[0]
                    if seat[0] < front_of_room:
                        front_of_room = seat[0]

                for student in shuffled_class_list:
                    seat_costs = []
                    acceptable_seats = []
                    if student['talkative'] and student['front']:
                        for seat_index in range(len(available_seats)):
                            cost = 0
                            # Talkative cost
                            if student['talkative']:
                                for pair in pairs:
                                    if pair['student']['talkative']:
                                        cost += 2 / math.dist(pair['seat'], available_seats[seat_index])
                            
                            # Front cost
                            if student['front']:
                                if available_seats[seat_index][0] - front_of_room != 0:
                                    cost += 1 * (available_seats[seat_index][0] - front_of_room)

                            seat_costs.append(cost)

                        for i in range(len(seat_costs)):
                            if seat_costs[i] <= MAX_COST:
                                acceptable_seats.append(i)

                        if len(acceptable_seats) > 0:
                            best_seat_index = random.randrange(0, len(acceptable_seats))
                            pair = {'seat' : available_seats[acceptable_seats[best_seat_index]], 'student' : student, 'cost' : seat_costs[acceptable_seats[best_seat_index]]}
                            pairs.append(pair)
                            available_seats.pop(acceptable_seats[best_seat_index])
                        else:
                            best_seat_index = seat_costs.index(min(seat_costs))
                            pair = {'seat' : available_seats[best_seat_index], 'student' : student, 'cost' : seat_costs[best_seat_index]}
                            pairs.append(pair)
                            available_seats.pop(best_seat_index)

                for student in shuffled_class_list:
                    seat_costs = []
                    acceptable_seats = []
                    if student['talkative'] ^ student['front']:
                        for seat_index in range(len(available_seats)):
                            cost = 0
                            # Talkative cost
                            if student['talkative']:
                                for pair in pairs:
                                    if pair['student']['talkative']:
                                        cost += 2 / math.dist(pair['seat'], available_seats[seat_index])
                            
                            # Front cost
                            if student['front']:
                                if available_seats[seat_index][0] - front_of_room != 0:
                                    cost += 1 * (available_seats[seat_index][0] - front_of_room)

                            seat_costs.append(cost)

                        for i in range(len(seat_costs)):
                            if seat_costs[i] <= MAX_COST:
                                acceptable_seats.append(i)

                        if len(acceptable_seats) > 0:
                            best_seat_index = random.randrange(0, len(acceptable_seats))
                            pair = {'seat' : available_seats[acceptable_seats[best_seat_index]], 'student' : student, 'cost' : seat_costs[acceptable_seats[best_seat_index]]}
                            pairs.append(pair)
                            available_seats.pop(acceptable_seats[best_seat_index])
                        else:
                            best_seat_index = seat_costs.index(min(seat_costs))
                            pair = {'seat' : available_seats[best_seat_index], 'student' : student, 'cost' : seat_costs[best_seat_index]}
                            pairs.append(pair)
                            available_seats.pop(best_seat_index)

                for student in shuffled_class_list:
                    seat_costs = []
                    acceptable_seats = []
                    if not student['talkative'] and not student['front']:
                        best_seat_index = random.randrange(0, len(available_seats))
                        pair = {'seat' : available_seats[best_seat_index], 'student' : student, 'cost' : 0}
                        pairs.append(pair)
                        available_seats.pop(best_seat_index)

                ###############################################################

                # Set layout appropriately
                self.layout['rows'] = room_layout['rows']
                self.layout['cols'] = room_layout['cols']

                self.resetLayout()

                for pair in pairs:
                    row = pair['seat'][0]
                    col = pair['seat'][1]
                    self.layout['list'][row][col] = 1
                    self.cells[row][col].setChecked(True)
                    self.cells[row][col].setText(pair['student']['name'])

                for i in range (self.layout['rows']):
                    for j in range(self.layout['cols']):
                        self.cells[i][j].show()

            else:
                err_msg = QMessageBox()
                err_msg.setText('Need same number of students and seats!')
                err_msg.setIcon(QMessageBox.Warning)
                err_msg.setWindowTitle(' ')
                err_msg.exec_()
        else:
            err_msg = QMessageBox()
            err_msg.setText('Select a class list and room layout!')
            err_msg.setIcon(QMessageBox.Warning)
            err_msg.setWindowTitle(' ')
            err_msg.exec_() 

    def gridCellButtonCallback(self, row_col):
        row = row_col[0]
        col = row_col[1]

        if 0 == self.layout['list'][row][col]:
            self.layout['list'][row][col] = 1
            self.cells[row][col].setChecked(True)
        else:
            self.layout['list'][row][col] = 0
            self.cells[row][col].setChecked(False)

    def resetLayout(self):
        for i in range(MAX_ROWS):
            for j in range(MAX_COLS):
                self.layout['list'][i][j] = 0
                self.cells[i][j].setChecked(False)
                self.cells[i][j].setText('')
                self.cells[i][j].hide()
        

def main():
    global WIDTH
    global HEIGHT
    global SUB_WIDTH
    global SUB_HEIGHT
    global MENU_WIDTH
    global SUB_X
    global SUB_Y
    global MIN_ROWS
    global MAX_ROWS
    global MIN_COLS
    global MAX_COLS

    app = QApplication(sys.argv)

    screen = QApplication.primaryScreen()
    screensize = screen.size()

    WIDTH = int(screensize.width())
    HEIGHT = int(screensize.height())
    SUB_WIDTH = int((WIDTH * 2) / 3)
    SUB_HEIGHT = int((HEIGHT * 2)/ 3)
    MENU_WIDTH = int(WIDTH / 4)
    SUB_X = int(WIDTH / 8)
    SUB_Y = int(HEIGHT / 8)

    ex = MainScreenWidget()

    exit_value = app.exec_()

    sys.exit(exit_value)


if __name__ == '__main__':
    main()
