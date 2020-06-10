from PyQt5 import QtWidgets, uic
from ViewModel.mainWindowViewModel import MainWindowViewModel
import sys

def main():
    app = QtWidgets.QApplication(sys.argv)
    main = MainWindowViewModel()
    main.show()
    sys.exit(app.exec_())

if __name__ == '__main__':         
    main()