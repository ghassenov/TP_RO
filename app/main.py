import sys
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QTableWidgetItem, QMessageBox, QVBoxLayout
)
from PySide6.QtCore import Qt

from app.ui.main_window import Ui_MainWindow
from app.solvers.mailbox_solver import MailboxLocationSolver
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure
from shared.visualization import plot_mailbox_solution


class MatplotlibCanvas(FigureCanvasQTAgg):
    def __init__(self, parent=None):
        fig = Figure(figsize=(5, 5))
        super().__init__(fig)
        self.setParent(parent)
        self.axes = fig.add_subplot(111)
        fig.tight_layout()


class Main(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.canvas = MatplotlibCanvas(self.ui.graphWidget)
        layout = self.ui.graphWidget.layout()
        if layout is None:
            layout = QVBoxLayout(self.ui.graphWidget)
        layout.addWidget(self.canvas)

        self.ui.btnAddDemand.clicked.connect(self.add_demand_row)
        self.ui.btnAddMailboxParams.clicked.connect(self.add_mailbox_params_row)
        self.ui.btnSolve.clicked.connect(self.solve)

        self.setup_tables()
        self.ui.status.setText("Status: Ready")

    def setup_tables(self):
        self.ui.tableDemand.setColumnCount(5)
        self.ui.tableDemand.setHorizontalHeaderLabels(
            ["X", "Y", "Population", "Demand", "Priority"]
        )
        self.ui.tableMailboxParams.setColumnCount(3)
        self.ui.tableMailboxParams.setHorizontalHeaderLabels(
            ["Cost", "Capacity", "Fixed Cost"]
        )
        self.ui.spinCoverageLevel.setValue(1)
        self.ui.spinBudget.setValue(1000)

    def add_demand_row(self):
        row = self.ui.tableDemand.rowCount()
        self.ui.tableDemand.insertRow(row)
        for col in range(5):
            self.ui.tableDemand.setItem(row, col, QTableWidgetItem(""))

    def add_mailbox_params_row(self):
        row = self.ui.tableMailboxParams.rowCount()
        self.ui.tableMailboxParams.insertRow(row)
        for col in range(3):
            self.ui.tableMailboxParams.setItem(row, col, QTableWidgetItem(""))

    def parse_demand_points(self):
        points = []
        table = self.ui.tableDemand
        for row in range(table.rowCount()):
            try:
                x = float(table.item(row, 0).text())
                y = float(table.item(row, 1).text())
                pop = float(table.item(row, 2).text() or "1")
                demand = float(table.item(row, 3).text() or "1")
                priority = float(table.item(row, 4).text() or "1")
                points.append({
                    "x": x, "y": y, 
                    "population": pop, 
                    "demand": demand, 
                    "priority": priority
                })
            except:
                raise ValueError(f"Invalid demand point at row {row+1}")
        return points

    def parse_advanced_parameters(self):
        num_mailboxes = int(self.ui.spinMailboxes.value())
        costs, capacities = [], []
        
        for row in range(num_mailboxes):
            try:
                cost = float(self.ui.tableMailboxParams.item(row, 0).text() or "1.0")
                capacity = float(self.ui.tableMailboxParams.item(row, 1).text() or "1000.0")
                costs.append(cost)
                capacities.append(capacity)
            except:
                costs.append(1.0)
                capacities.append(1000.0)
        
        return {
            'costs': costs,
            'capacities': capacities,
            'budget': float(self.ui.spinBudget.value()),
            'max_coverage_level': int(self.ui.spinCoverageLevel.value())
        }

    def solve(self):
        try:
            demand = self.parse_demand_points()
            num_mailboxes = int(self.ui.spinMailboxes.value())
            radius = float(self.ui.spinRadius.value())
            params = self.parse_advanced_parameters()

            solver = MailboxLocationSolver(
                demand_points=demand,
                num_mailboxes=num_mailboxes,
                radius=radius,
                costs=params['costs'],
                budgets=params['budget'],
                capacities=params['capacities'],
                max_coverage_level=params['max_coverage_level']
            )
            
            result = solver.solve()
            self.display_advanced_results(result)
            self.draw_advanced_graph(demand, result, radius)
            self.ui.status.setText("Status: Optimization completed")

        except Exception as e:
            self.ui.status.setText(f"Error: {str(e)}")
            QMessageBox.critical(self, "Error", str(e))

    def display_advanced_results(self, result):
        text = f"""
<b>Objective Value:</b> {result['objective']:.2f}<br>
<b>Mailboxes Built:</b> {result['total_built']}<br><br>

<b>Mailbox Locations:</b><br>
"""
        for i, loc in enumerate(result['mailbox_locations']):
            if loc['built']:
                text += f"{i}: ({loc['x']:.2f}, {loc['y']:.2f})<br>"
        
        text += "<br><b>Coverage Summary:</b><br>"
        covered_count = 0
        for info in result['coverage_info']:
            if info['coverage_level'] > 0:
                text += f"Point {info['point']}: Level {info['coverage_level']}<br>"
                covered_count += 1
        
        text += f"<br><b>Points Covered:</b> {covered_count}/{len(result['coverage_info'])}"
        
        self.ui.textResults.setHtml(text)

    def draw_advanced_graph(self, demand, result, radius):
        # Clear existing figure
        self.canvas.figure.clear()
        
        # Use the new visualization function
        fig = plot_mailbox_solution(
            demand_points=demand,
            mailbox_locations=result['mailbox_locations'],
            coverage_info=result['coverage_info'],
            radius=radius
        )
        
        # Update canvas with new figure
        self.canvas.figure = fig
        self.canvas.draw()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Main()
    window.show()
    sys.exit(app.exec())