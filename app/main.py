import sys

# Matplotlib
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.figure import Figure
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (QApplication, QMainWindow, QMessageBox,
                               QTableWidgetItem, QTabWidget, QVBoxLayout,
                               QWidget)

# Solver imports
from app.solvers.mailbox_solver import MailboxLocationSolver
from app.solvers.telecom_solver import TelecomNetworkSolver
# UI imports
from app.ui.mailbox_ui import MailboxUI
from app.ui.telecom_ui import TelecomUI
# Visualization imports
from shared.visualization import plot_mailbox_solution, plot_telecom_solution


class MatplotlibCanvas(FigureCanvasQTAgg):
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

        # Create UI
        self.ui = MailboxUI()
        parent_layout = parent_widget.layout()
        if parent_layout is None:
            parent_widget.setLayout(QVBoxLayout())
            parent_widget.layout().addWidget(self.ui)
        else:
            parent_layout.addWidget(self.ui)

        # Setup canvas
        self.mailbox_canvas = MatplotlibCanvas(self.ui.mailboxGraphWidget)
        graph_layout = self.ui.mailboxGraphWidget.layout()
        if graph_layout is None:
            graph_layout = QVBoxLayout(self.ui.mailboxGraphWidget)
        graph_layout.addWidget(self.mailbox_canvas)

        self.setup_connections()
        self.load_example_data()

    def setup_connections(self):
        self.ui.btnAddDemand.clicked.connect(self.add_demand_row)
        self.ui.btnAddMailboxParams.clicked.connect(self.add_mailbox_params_row)
        self.ui.btnSolveMailbox.clicked.connect(self.solve_mailbox)

    def load_example_data(self):
        # Add 3 demand points
        for i in range(3):
            self.add_demand_row()
            self.ui.tableDemand.setItem(i, 0, QTableWidgetItem(str(i + 1)))
            self.ui.tableDemand.setItem(i, 1, QTableWidgetItem(str(i + 1)))
            self.ui.tableDemand.setItem(i, 2, QTableWidgetItem("50"))
            self.ui.tableDemand.setItem(i, 3, QTableWidgetItem("5"))
            self.ui.tableDemand.setItem(i, 4, QTableWidgetItem("1"))

        # Add 3 mailbox parameter rows
        for i in range(3):
            self.add_mailbox_params_row()
            self.ui.tableMailboxParams.setItem(i, 0, QTableWidgetItem("100"))
            self.ui.tableMailboxParams.setItem(i, 1, QTableWidgetItem("20"))
            self.ui.tableMailboxParams.setItem(i, 2, QTableWidgetItem("50"))

    def add_demand_row(self):
        row = self.ui.tableDemand.rowCount()
        self.ui.tableDemand.insertRow(row)

    def add_mailbox_params_row(self):
        row = self.ui.tableMailboxParams.rowCount()
        self.ui.tableMailboxParams.insertRow(row)

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

    def solve_mailbox(self):
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
            self.display_mailbox_results(result)
            self.plot_mailbox_solution(demand, result, radius)
            self.ui.lblMailboxStatus.setText("Status: Optimization completed")

        except Exception as e:
            self.ui.lblMailboxStatus.setText(f"Error: {str(e)}")
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

        self.ui.textMailboxResults.setHtml(text)

    def plot_mailbox_solution(self, demand, result, radius):
        self.mailbox_canvas.figure.clear()
        fig = plot_mailbox_solution(
            demand_points=demand,
            mailbox_locations=result['mailbox_locations'],
            coverage_info=result['coverage_info'],
            radius=radius
        )
        self.mailbox_canvas.figure = fig
        self.mailbox_canvas.draw()


class TelecomController:
    """Controller for telecom network module"""

    def __init__(self, parent_widget):
        self.parent = parent_widget

        # Create UI
        self.ui = TelecomUI()
        parent_layout = parent_widget.layout()
        if parent_layout is None:
            parent_widget.setLayout(QVBoxLayout())
            parent_widget.layout().addWidget(self.ui)
        else:
            parent_layout.addWidget(self.ui)

        # Setup canvas
        self.telecom_canvas = MatplotlibCanvas(self.ui.telecomGraphWidget)
        graph_layout = self.ui.telecomGraphWidget.layout()
        if graph_layout is None:
            graph_layout = QVBoxLayout(self.ui.telecomGraphWidget)
        graph_layout.addWidget(self.telecom_canvas)

        self.setup_connections()
        self.load_example_data()

    def setup_connections(self):
        self.ui.btnAddNode.clicked.connect(self.add_node_row)
        self.ui.btnAddLink.clicked.connect(self.add_link_row)
        self.ui.btnSolveTelecom.clicked.connect(self.solve_telecom)

    def load_example_data(self):
        try:
            # Example nodes
            example_nodes = [
                {"name": "Paris", "x": 0, "y": 0},
                {"name": "Lyon", "x": 3, "y": 2},
                {"name": "Marseille", "x": 5, "y": -1},
                {"name": "Toulouse", "x": 2, "y": -3},
                {"name": "Lille", "x": -1, "y": 4}
            ]

            # Example links
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

            # Example demand matrix
            example_demands = [
                [0, 100, 80, 60, 70],
                [100, 0, 120, 90, 50],
                [80, 120, 0, 110, 40],
                [60, 90, 110, 0, 30],
                [70, 50, 40, 30, 0]
            ]

            # Load nodes
            self.ui.tableNodes.setRowCount(len(example_nodes))
            for i, node in enumerate(example_nodes):
                self.ui.tableNodes.setItem(i, 0, QTableWidgetItem(node["name"]))
                self.ui.tableNodes.setItem(i, 1, QTableWidgetItem(str(node["x"])))
                self.ui.tableNodes.setItem(i, 2, QTableWidgetItem(str(node["y"])))

            # Load links
            self.ui.tableLinks.setRowCount(len(example_links))
            for i, link in enumerate(example_links):
                self.ui.tableLinks.setItem(i, 0, QTableWidgetItem(str(link["from"])))
                self.ui.tableLinks.setItem(i, 1, QTableWidgetItem(str(link["to"])))
                self.ui.tableLinks.setItem(i, 2, QTableWidgetItem(str(link["distance"])))

            # Setup demand matrix
            n = len(example_demands)
            self.ui.tableDemands.setRowCount(n)
            self.ui.tableDemands.setColumnCount(n)
            for i in range(n):
                for j in range(n):
                    self.ui.tableDemands.setItem(i, j, QTableWidgetItem(str(example_demands[i][j])))

        except Exception as e:
            print(f"Failed to load example data: {e}")

    def add_node_row(self):
        row = self.ui.tableNodes.rowCount()
        self.ui.tableNodes.insertRow(row)

    def add_link_row(self):
        row = self.ui.tableLinks.rowCount()
        self.ui.tableLinks.insertRow(row)

    def parse_telecom_data(self):
        nodes = []
        for row in range(self.ui.tableNodes.rowCount()):
            try:
                name = self.ui.tableNodes.item(row, 0).text() or f"Node{row}"
                x = float(self.ui.tableNodes.item(row, 1).text())
                y = float(self.ui.tableNodes.item(row, 2).text())
                nodes.append({"id": row, "name": name, "x": x, "y": y})
            except:
                nodes.append({"id": row, "name": f"Node{row}", "x": 0, "y": 0})

        potential_links = []
        for row in range(self.ui.tableLinks.rowCount()):
            try:
                from_node = int(self.ui.tableLinks.item(row, 0).text())
                to_node = int(self.ui.tableLinks.item(row, 1).text())
                distance = float(self.ui.tableLinks.item(row, 2).text())
                potential_links.append({
                    "from": from_node,
                    "to": to_node,
                    "distance": distance
                })
            except:
                continue

        n = len(nodes)
        demands = [[0] * n for _ in range(n)]
        for i in range(n):
            for j in range(n):
                try:
                    item = self.ui.tableDemands.item(i, j)
                    if item:
                        demands[i][j] = float(item.text())
                except:
                    pass

        capacities = [float(x.strip()) for x in self.ui.txtCapacities.text().split(',')]
        budget = float(self.ui.spinTelecomBudget.value())
        fixed_cost_factor = float(self.ui.spinFixedCost.value())
        variable_cost_factor = float(self.ui.spinVariableCost.value())

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

        self.ui.textTelecomResults.setHtml(text)

    def plot_telecom_solution(self, nodes, selected_links):
        self.telecom_canvas.figure.clear()
        fig = plot_telecom_solution(nodes, selected_links)
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
        self.statusBar().showMessage("Ready")


def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    window = Main()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
