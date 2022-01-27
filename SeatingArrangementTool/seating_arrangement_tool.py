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


class MainUILayout(QtWidgets.QWidget):
     
    def __init__(self):
        super().__init__()
        self.UI()
 
    def UI(self):
        self.label = QtWidgets.QLabel()
        self.label.setText(str(class_list))
        self.name_input = QtWidgets.QLineEdit()
         
        self.grid = QtWidgets.QGridLayout()
        self.grid.addWidget(self.label, 0, 0)
        self.grid.addWidget(self.name_input, 1, 0)

        self.grid.setSpacing(2)

        self.name_input.returnPressed.connect(self.onTextEnter)
        self.setLayout(self.grid)
        self.setGeometry(300, 300, 400, 400)
        self.setWindowTitle('Class Editor')
        self.show()

    def onTextEnter(self):
        global class_list

        value = self.name_input.text()

        local_dict = {'name': value}
        rules = []
        local_dict['rules'] = rules
        class_list.append(local_dict)

        self.label.setText(str(class_list))
        self.name_input.clear()
 
def main():
    global class_list

    # Load data
    if os.path.exists('class_list.p'):
        with open('class_list.p', 'rb') as f:
            class_list = pickle.load(f)

    app = QtWidgets.QApplication(sys.argv)
    ex = MainUILayout()

    exit_value = app.exec_()

    # Save data
    with open('class_list.p', 'wb') as f:
        pickle.dump(class_list, f)

    sys.exit(exit_value)


if __name__ == '__main__':
    main()
