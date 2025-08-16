import main
from display_delay import PyThreadStimulateExclude
main.PyThreadStimulate = PyThreadStimulateExclude

from main import QApplication, sys, MainWindow

if __name__ == "__main__":
    app = QApplication(sys.argv)
    mainWin = MainWindow()
    mainWin.setStyleSheet("background-color: #7a7a7a;")
    mainWin.show()
    sys.exit(app.exec())
