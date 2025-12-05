import json
import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QFileDialog
from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import QFile

from app.solvers.mailbox_solver import MailboxLocationSolver
from shared.visualization import plot_mailbox_solution

class Main(QMainWindow):
    def __init__(self):
        super().__init__()

        # Load UI
        loader = QUiLoader()
        ui_file = QFile("app/ui/main_window.ui")
        ui_file.open(QFile.ReadOnly)
        self.ui = loader.load(ui_file, self)
        ui_file.close()

        self.setCentralWidget(self.ui)

        # Buttons
        self.ui.loadButton.clicked.connect(self.load_data)
        self.ui.solveButton.clicked.connect(self.solve)

        self.data = None

    def load_data(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Load JSON", "", "JSON Files (*.json)"
        )
        if path:
            with open(path, "r") as f:
                self.data = json.load(f)
            self.ui.status.setText("Status: Data Loaded")

    def solve(self):
        if not self.data:
            self.ui.status.setText("Status: Load data first")
            return

        solver = MailboxLocationSolver(
            demand_points=self.data["demand_points"],
            facilities=self.data["facilities"],
            radius=self.data["radius"],
            num_mailboxes=self.data["num_mailboxes"]
        )

        result = solver.solve()
        self.ui.status.setText(f"Objective: {result['objective']}")

        plot_mailbox_solution(
            self.data["demand_points"],
            self.data["facilities"],
            self.data["radius"],
            result["chosen_facilities"]
        )

if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = Main()
    win.show()
    sys.exit(app.exec())
