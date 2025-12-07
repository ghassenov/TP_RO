import json
import sys

# Matplotlib
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.figure import Figure
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (QApplication, QDoubleSpinBox, QFormLayout,
                               QGroupBox, QHBoxLayout, QHeaderView, QLabel,
                               QLineEdit, QMainWindow, QMessageBox,
                               QPushButton, QSpinBox, QSplitter, QTableWidget,
                               QTableWidgetItem, QTabWidget, QTextEdit,
                               QVBoxLayout, QWidget)

# Mailbox imports
from app.solvers.mailbox_solver import MailboxLocationSolver
# Telecom imports
from app.solvers.telecom_solver import TelecomNetworkSolver
from shared.visualization import plot_mailbox_solution, plot_telecom_solution


class MatplotlibCanvas(FigureCanvasQTAgg):
    """A QWidget that displays a Matplotlib figure"""
    def __init__(self, parent=None):
        fig = Figure(figsize=(5, 5))
        super().__init__(fig)
        self.setParent(parent)
        self.axes = fig.add_subplot(111)
        fig.tight_layout()


class MailboxController:
    """Controller for mailbox location module"""

    def __init__(self, parent_widget):
        self.parent = parent_widget
        self.setup_ui()
        self.setup_connections()

    def setup_ui(self):
        # Create main layout
        layout = QVBoxLayout(self.parent)

        # Create splitter for left/right panels
        splitter = QSplitter(Qt.Horizontal)

        # Left panel
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)

        # Basic parameters
        param_group = QGroupBox("Parameters")
        param_layout = QFormLayout()

        self.spinMailboxes = QSpinBox()
        self.spinMailboxes.setMinimum(1)
        self.spinMailboxes.setMaximum(999)
        self.spinMailboxes.setValue(3)
        param_layout.addRow("Number of Mailboxes:", self.spinMailboxes)

        self.spinRadius = QDoubleSpinBox()
        self.spinRadius.setMinimum(0.1)
        self.spinRadius.setMaximum(9999.0)
        self.spinRadius.setValue(2.0)
        param_layout.addRow("Radius:", self.spinRadius)

        self.spinBudget = QDoubleSpinBox()
        self.spinBudget.setMinimum(0.0)
        self.spinBudget.setMaximum(1000000.0)
        self.spinBudget.setValue(1000.0)
        param_layout.addRow("Budget:", self.spinBudget)

        self.spinCoverageLevel = QSpinBox()
        self.spinCoverageLevel.setMinimum(1)
        self.spinCoverageLevel.setMaximum(10)
        self.spinCoverageLevel.setValue(1)
        param_layout.addRow("Max Coverage Level:", self.spinCoverageLevel)

        param_group.setLayout(param_layout)
        left_layout.addWidget(param_group)

        # Demand points table
        left_layout.addWidget(QLabel("Demand Points (x, y, population, demand, priority):"))
        self.tableDemand = QTableWidget()
        self.tableDemand.setColumnCount(5)
        self.tableDemand.setHorizontalHeaderLabels(["X", "Y", "Population", "Demand", "Priority"])
        self.tableDemand.horizontalHeader().setStretchLastSection(True)
        left_layout.addWidget(self.tableDemand)

        # Mailbox parameters table
        left_layout.addWidget(QLabel("Mailbox Parameters (cost, capacity, fixed cost):"))
        self.tableMailboxParams = QTableWidget()
        self.tableMailboxParams.setColumnCount(3)
        self.tableMailboxParams.setHorizontalHeaderLabels(["Cost", "Capacity", "Fixed Cost"])
        left_layout.addWidget(self.tableMailboxParams)

        # Buttons
        self.btnAddDemand = QPushButton("Add Demand Point")
        self.btnAddMailboxParams = QPushButton("Add Mailbox Parameter Row")
        self.btnSolveMailbox = QPushButton("Solve Mailbox Location")

        left_layout.addWidget(self.btnAddDemand)
        left_layout.addWidget(self.btnAddMailboxParams)
        left_layout.addWidget(self.btnSolveMailbox)

        # Status label
        self.lblMailboxStatus = QLabel("Status: Ready")
        left_layout.addWidget(self.lblMailboxStatus)

        left_layout.addStretch()

        # Right panel
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)

        right_layout.addWidget(QLabel("Results:"))
        self.textMailboxResults = QTextEdit()
        self.textMailboxResults.setReadOnly(True)
        right_layout.addWidget(self.textMailboxResults)

        self.mailboxGraphWidget = QWidget()
        right_layout.addWidget(self.mailboxGraphWidget)

        # Setup canvas for mailbox
        self.mailbox_canvas = MatplotlibCanvas(self.mailboxGraphWidget)
        graph_layout = QVBoxLayout(self.mailboxGraphWidget)
        graph_layout.addWidget(self.mailbox_canvas)

        # Add widgets to splitter
        splitter.addWidget(left_widget)
        splitter.addWidget(right_widget)
        splitter.setSizes([400, 600])

        layout.addWidget(splitter)
        self.parent.setLayout(layout)

        # Initialize tables with example data
        self.load_example_data()

    def load_example_data(self):
        """Load example data into tables"""
        # Add 3 demand points
        for i in range(3):
            self.add_demand_row()
            self.tableDemand.setItem(i, 0, QTableWidgetItem(str(i + 1)))
            self.tableDemand.setItem(i, 1, QTableWidgetItem(str(i + 1)))
            self.tableDemand.setItem(i, 2, QTableWidgetItem("50"))
            self.tableDemand.setItem(i, 3, QTableWidgetItem("5"))
            self.tableDemand.setItem(i, 4, QTableWidgetItem("1"))

        # Add 3 mailbox parameter rows
        for i in range(3):
            self.add_mailbox_params_row()
            self.tableMailboxParams.setItem(i, 0, QTableWidgetItem("100"))
            self.tableMailboxParams.setItem(i, 1, QTableWidgetItem("20"))
            self.tableMailboxParams.setItem(i, 2, QTableWidgetItem("50"))

    def setup_connections(self):
        """Connect signals to slots"""
        self.btnAddDemand.clicked.connect(self.add_demand_row)
        self.btnAddMailboxParams.clicked.connect(self.add_mailbox_params_row)
        self.btnSolveMailbox.clicked.connect(self.solve_mailbox)

    def add_demand_row(self):
        row = self.tableDemand.rowCount()
        self.tableDemand.insertRow(row)
        for col in range(5):
            self.tableDemand.setItem(row, col, QTableWidgetItem(""))

    def add_mailbox_params_row(self):
        row = self.tableMailboxParams.rowCount()
        self.tableMailboxParams.insertRow(row)
        for col in range(3):
            self.tableMailboxParams.setItem(row, col, QTableWidgetItem(""))

    def parse_demand_points(self):
        points = []
        table = self.tableDemand
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
        num_mailboxes = int(self.spinMailboxes.value())
        costs, capacities = [], []

        for row in range(num_mailboxes):
            try:
                cost = float(self.tableMailboxParams.item(row, 0).text() or "1.0")
                capacity = float(self.tableMailboxParams.item(row, 1).text() or "1000.0")
                costs.append(cost)
                capacities.append(capacity)
            except:
                costs.append(1.0)
                capacities.append(1000.0)

        return {
            'costs': costs,
            'capacities': capacities,
            'budget': float(self.spinBudget.value()),
            'max_coverage_level': int(self.spinCoverageLevel.value())
        }

    def solve_mailbox(self):
        try:
            demand = self.parse_demand_points()
            num_mailboxes = int(self.spinMailboxes.value())
            radius = float(self.spinRadius.value())
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
            self.display_mailbox_results(result)
            self.plot_mailbox_solution(demand, result, radius)
            self.lblMailboxStatus.setText("Status: Optimization completed")

        except Exception as e:
            self.lblMailboxStatus.setText(f"Error: {str(e)}")
            QMessageBox.critical(self.parent, "Error", str(e))

    def display_mailbox_results(self, result):
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

        self.textMailboxResults.setHtml(text)

    def plot_mailbox_solution(self, demand, result, radius):
        # Clear existing figure
        self.mailbox_canvas.figure.clear()

        # Use the visualization function
        fig = plot_mailbox_solution(
            demand_points=demand,
            mailbox_locations=result['mailbox_locations'],
            coverage_info=result['coverage_info'],
            radius=radius
        )

        # Update canvas with new figure
        self.mailbox_canvas.figure = fig
        self.mailbox_canvas.draw()


class TelecomController:
    """Controller for telecom network module"""

    def __init__(self, parent_widget):
        self.parent = parent_widget
        self.setup_ui()
        self.setup_connections()
        self.load_example_data()

    def setup_ui(self):
        # Create main layout
        layout = QVBoxLayout(self.parent)

        # Title
        title = QLabel("Telecom Network Design - Fiber Optic Network Optimization")
        title.setStyleSheet("font-size: 14pt; font-weight: bold; padding: 10px;")
        layout.addWidget(title)

        # Create tab widget for different sections
        self.tabs = QTabWidget()

        # Nodes tab
        nodes_tab = QWidget()
        nodes_layout = QVBoxLayout(nodes_tab)
        nodes_layout.addWidget(QLabel("Network Nodes (name, x, y):"))
        self.tableNodes = QTableWidget()
        self.tableNodes.setColumnCount(3)
        self.tableNodes.setHorizontalHeaderLabels(["Name", "X", "Y"])
        nodes_layout.addWidget(self.tableNodes)

        self.btnAddNode = QPushButton("Add Node")
        nodes_layout.addWidget(self.btnAddNode)

        self.tabs.addTab(nodes_tab, "Nodes")

        # Links tab
        links_tab = QWidget()
        links_layout = QVBoxLayout(links_tab)
        links_layout.addWidget(QLabel("Potential Links (from, to, distance):"))
        self.tableLinks = QTableWidget()
        self.tableLinks.setColumnCount(3)
        self.tableLinks.setHorizontalHeaderLabels(["From", "To", "Distance"])
        links_layout.addWidget(self.tableLinks)

        self.btnAddLink = QPushButton("Add Link")
        links_layout.addWidget(self.btnAddLink)

        self.tabs.addTab(links_tab, "Links")

        # Demands tab
        demands_tab = QWidget()
        demands_layout = QVBoxLayout(demands_tab)
        demands_layout.addWidget(QLabel("Traffic Demand Matrix (Gbps):"))
        self.tableDemands = QTableWidget()
        demands_layout.addWidget(self.tableDemands)

        self.tabs.addTab(demands_tab, "Demands")

        # Parameters tab
        params_tab = QWidget()
        params_layout = QVBoxLayout(params_tab)

        param_group = QGroupBox("Network Parameters")
        param_form = QFormLayout()

        self.txtCapacities = QLineEdit("100,200,500,1000")
        param_form.addRow("Capacity Options (Gbps):", self.txtCapacities)

        self.spinTelecomBudget = QDoubleSpinBox()
        self.spinTelecomBudget.setMinimum(0.0)
        self.spinTelecomBudget.setMaximum(1000000.0)
        self.spinTelecomBudget.setValue(50000.0)
        param_form.addRow("Budget (€):", self.spinTelecomBudget)

        self.spinFixedCost = QDoubleSpinBox()
        self.spinFixedCost.setValue(500.0)
        param_form.addRow("Fixed Cost per km (€):", self.spinFixedCost)

        self.spinVariableCost = QDoubleSpinBox()
        self.spinVariableCost.setValue(50.0)
        param_form.addRow("Variable Cost per Gbps/km (€):", self.spinVariableCost)

        param_group.setLayout(param_form)
        params_layout.addWidget(param_group)

        self.tabs.addTab(params_tab, "Parameters")

        layout.addWidget(self.tabs)

        # Solve button
        self.btnSolveTelecom = QPushButton("Optimize Network Design")
        self.btnSolveTelecom.setStyleSheet("font-weight: bold; padding: 10px;")
        layout.addWidget(self.btnSolveTelecom)

        # Results area with splitter
        results_splitter = QSplitter(Qt.Horizontal)

        # Results text
        self.textTelecomResults = QTextEdit()
        self.textTelecomResults.setReadOnly(True)
        results_splitter.addWidget(self.textTelecomResults)

        # Graph widget
        self.telecomGraphWidget = QWidget()
        results_splitter.addWidget(self.telecomGraphWidget)
        results_splitter.setSizes([300, 700])

        layout.addWidget(results_splitter)

        # Setup canvas for telecom
        self.telecom_canvas = MatplotlibCanvas(self.telecomGraphWidget)
        graph_layout = QVBoxLayout(self.telecomGraphWidget)
        graph_layout.addWidget(self.telecom_canvas)

        self.parent.setLayout(layout)

    def load_example_data(self):
        """Load example telecom data"""
        try:
            # Create example nodes
            example_nodes = [
                {"name": "Paris", "x": 0, "y": 0},
                {"name": "Lyon", "x": 3, "y": 2},
                {"name": "Marseille", "x": 5, "y": -1},
                {"name": "Toulouse", "x": 2, "y": -3},
                {"name": "Lille", "x": -1, "y": 4}
            ]

            # Create example links
            example_links = [
                {"from": 0, "to": 1, "distance": 3.6},
                {"from": 0, "to": 2, "distance": 5.1},
                {"from": 0, "to": 3, "distance": 3.6},
                {"from": 0, "to": 4, "distance": 4.1},
                {"from": 1, "to": 2, "distance": 3.2},
                {"from": 1, "to": 3, "distance": 3.0},
                {"from": 1, "to": 4, "distance": 5.0},
                {"from": 2, "to": 3, "distance": 3.0},
                {"from": 2, "to": 4, "distance": 6.4},
                {"from": 3, "to": 4, "distance": 5.8}
            ]

            # Create example demand matrix
            example_demands = [
                [0, 100, 80, 60, 70],
                [100, 0, 120, 90, 50],
                [80, 120, 0, 110, 40],
                [60, 90, 110, 0, 30],
                [70, 50, 40, 30, 0]
            ]

            # Load nodes
            self.tableNodes.setRowCount(len(example_nodes))
            for i, node in enumerate(example_nodes):
                self.tableNodes.setItem(i, 0, QTableWidgetItem(node["name"]))
                self.tableNodes.setItem(i, 1, QTableWidgetItem(str(node["x"])))
                self.tableNodes.setItem(i, 2, QTableWidgetItem(str(node["y"])))

            # Load links
            self.tableLinks.setRowCount(len(example_links))
            for i, link in enumerate(example_links):
                self.tableLinks.setItem(i, 0, QTableWidgetItem(str(link["from"])))
                self.tableLinks.setItem(i, 1, QTableWidgetItem(str(link["to"])))
                self.tableLinks.setItem(i, 2, QTableWidgetItem(str(link["distance"])))

            # Setup demand matrix
            n = len(example_demands)
            self.tableDemands.setRowCount(n)
            self.tableDemands.setColumnCount(n)
            for i in range(n):
                for j in range(n):
                    self.tableDemands.setItem(i, j, QTableWidgetItem(str(example_demands[i][j])))

        except Exception as e:
            print(f"Failed to load example data: {e}")

    def setup_connections(self):
        """Connect telecom UI signals"""
        self.btnAddNode.clicked.connect(self.add_node_row)
        self.btnAddLink.clicked.connect(self.add_link_row)
        self.btnSolveTelecom.clicked.connect(self.solve_telecom)

    def add_node_row(self):
        row = self.tableNodes.rowCount()
        self.tableNodes.insertRow(row)

    def add_link_row(self):
        row = self.tableLinks.rowCount()
        self.tableLinks.insertRow(row)

    def parse_telecom_data(self):
        """Parse all telecom input data"""
        # Parse nodes
        nodes = []
        for row in range(self.tableNodes.rowCount()):
            try:
                name = self.tableNodes.item(row, 0).text() or f"Node{row}"
                x = float(self.tableNodes.item(row, 1).text())
                y = float(self.tableNodes.item(row, 2).text())
                nodes.append({"id": row, "name": name, "x": x, "y": y})
            except:
                nodes.append({"id": row, "name": f"Node{row}", "x": 0, "y": 0})

        # Parse links
        potential_links = []
        for row in range(self.tableLinks.rowCount()):
            try:
                from_node = int(self.tableLinks.item(row, 0).text())
                to_node = int(self.tableLinks.item(row, 1).text())
                distance = float(self.tableLinks.item(row, 2).text())
                potential_links.append({
                    "from": from_node,
                    "to": to_node,
                    "distance": distance
                })
            except:
                continue

        # Parse demand matrix
        n = len(nodes)
        demands = [[0] * n for _ in range(n)]
        for i in range(n):
            for j in range(n):
                try:
                    item = self.tableDemands.item(i, j)
                    if item:
                        demands[i][j] = float(item.text())
                except:
                    pass

        # Parse parameters
        capacities = [float(x.strip()) for x in self.txtCapacities.text().split(',')]
        budget = float(self.spinTelecomBudget.value())
        fixed_cost_factor = float(self.spinFixedCost.value())
        variable_cost_factor = float(self.spinVariableCost.value())

        # Calculate costs based on distance
        fixed_costs = [fixed_cost_factor * link['distance'] for link in potential_links]
        variable_costs = [variable_cost_factor * link['distance'] for link in potential_links]

        return {
            "nodes": nodes,
            "potential_links": potential_links,
            "demands": demands,
            "capacities": capacities,
            "budget": budget,
            "fixed_costs": fixed_costs,
            "variable_costs": variable_costs
        }

    def solve_telecom(self):
        """Solve the telecom network optimization problem"""
        try:
            data = self.parse_telecom_data()

            solver = TelecomNetworkSolver(
                nodes=data['nodes'],
                potential_links=data['potential_links'],
                demands=data['demands'],
                fixed_costs=data['fixed_costs'],
                variable_costs=data['variable_costs'],
                capacities=data['capacities'],
                budget=data['budget']
            )

            result = solver.solve()
            self.display_telecom_results(result)
            self.plot_telecom_solution(data['nodes'], result['selected_links'])

        except Exception as e:
            QMessageBox.critical(self.parent, "Error", f"Optimization error: {str(e)}")

    def display_telecom_results(self, result):
        """Display telecom optimization results"""
        text = f"""
<b>OPTIMIZATION RESULTS</b>
<hr>
<b>Total Cost:</b> {result['objective']:,.0f} €<br>
<b>Links Built:</b> {result['num_links_built']}<br>
<b>Total Capacity:</b> {result['total_capacity']} Gbps<br>
<b>Demand Satisfied:</b> {result['demand_satisfied']:.0f}/{result['total_demand']:.0f} Gbps
({result['demand_satisfaction_rate']*100:.1f}%)<br><br>

<b>LINK DETAILS:</b><br>
"""

        for i, link in enumerate(result['selected_links']):
            text += f"""
<b>Link {i+1}:</b> {link['from']} → {link['to']}<br>
• Distance: {link.get('distance', 0):.1f} km<br>
• Capacity: {link.get('capacity', 0)} Gbps<br>
• Flow: {link.get('flow', 0):.1f} Gbps<br>
• Utilization: {link.get('utilization', 0)*100:.1f}%<br>
• Cost: {link.get('cost', 0):,.0f} €<br>
"""

        self.textTelecomResults.setHtml(text)

    def plot_telecom_solution(self, nodes, selected_links):
        """Plot telecom network solution"""
        # Clear existing figure
        self.telecom_canvas.figure.clear()

        # Use the visualization function
        fig = plot_telecom_solution(nodes, selected_links)

        # Update canvas with new figure
        self.telecom_canvas.figure = fig
        self.telecom_canvas.draw()


class Main(QMainWindow):
    """Main application window with tabbed interface"""

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Optimization Suite - Mailbox & Telecom Network")
        self.setGeometry(100, 100, 1400, 800)

        # Create central widget with tabs
        self.tab_widget = QTabWidget()

        # Mailbox tab
        self.mailbox_tab = QWidget()
        self.mailbox_controller = MailboxController(self.mailbox_tab)
        self.tab_widget.addTab(self.mailbox_tab, "📮 Mailbox Location")

        # Telecom tab
        self.telecom_tab = QWidget()
        self.telecom_controller = TelecomController(self.telecom_tab)
        self.tab_widget.addTab(self.telecom_tab, "📡 Telecom Network")

        self.setCentralWidget(self.tab_widget)

        # Status bar
        self.statusBar().showMessage("Ready")


def main():
    """Application entry point"""
    app = QApplication(sys.argv)

    # Set application style
    app.setStyle('Fusion')

    # Create and show main window
    window = Main()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
