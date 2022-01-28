from enum import Enum
import os.path
import pickle
from PyQt5 import QtWidgets
import sys


# List of all students in this class
class_list = []


class RuleTypes(Enum):
    NONE = 0
    CANNOT_BE_NEXT_TO = 1
    CANNOT_BE_NEAR = 2
    MUST_BE_NEXT_TO = 3
    MUST_BE_NEAR = 4
    MUST_BE_IN_SPOT = 5


class ClassEditorWidget(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.UI()
 
    def UI(self):
        global class_list

        self.student_list = QtWidgets.QListWidget()
        for student in class_list:
            QtWidgets.QListWidgetItem(student['name'], self.student_list)
        self.student_list.itemClicked.connect(self.nameClicked)

        self.name_input = QtWidgets.QLineEdit()
        self.name_input.returnPressed.connect(self.onTextEnter)

        self.grid = QtWidgets.QGridLayout()
        self.grid.addWidget(self.student_list, 0, 0)
        self.grid.addWidget(self.name_input, 1, 0)
        self.grid.setSpacing(2)

        self.setLayout(self.grid)
        self.setGeometry(300, 300, 400, 400)
        # self.setFixedWidth(400)
        # self.setFixedHeight(400)
        self.setWindowTitle('Class Editor')
        self.show()


    def nameClicked(self, item):
        global class_list

        delete_msg = QtWidgets.QMessageBox()
        delete_msg.setText('Would you like to remove ' + item.text() + '?')
        delete_msg.setIcon(QtWidgets.QMessageBox.Warning)
        delete_msg.setStandardButtons(QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
        retval = delete_msg.exec_()
        if retval == 16384:
            pass
            # remove this student from the list
        



    def onTextEnter(self):
        global class_list

        value = self.name_input.text()
        local_dict = {'name': value}
        rules = []
        local_dict['rules'] = rules
        class_list.append(local_dict)
        QtWidgets.QListWidgetItem(local_dict['name'], self.student_list)
        self.name_input.clear()
 
def main():
    global class_list

    # Load data
    if os.path.exists('class_list.p'):
        with open('class_list.p', 'rb') as f:
            class_list = pickle.load(f)

    app = QtWidgets.QApplication(sys.argv)
    ex = ClassEditorWidget()

    exit_value = app.exec_()

    # Save data
    with open('class_list.p', 'wb') as f:
        pickle.dump(class_list, f)

    sys.exit(exit_value)


if __name__ == '__main__':
    main()
