import sys

# Matplotlib
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.figure import Figure
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (QApplication, QMainWindow, QMessageBox,
                               QTableWidgetItem, QTabWidget, QVBoxLayout,
                               QWidget)

from app.solvers.antenna_solver import AntennaPlacementSolver
# Solver imports
from app.solvers.mailbox_solver import MailboxLocationSolver
from app.solvers.telecom_solver import TelecomNetworkSolver
from app.ui.antenna_ui import AntennaUI
# UI imports
from app.ui.mailbox_ui import MailboxUI
from app.ui.telecom_ui import TelecomUI
# Visualization imports
from shared.visualization import (plot_antenna_solution, plot_mailbox_solution,
                                  plot_telecom_solution)


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
            example_nodes = [
                {"name": "Tunis", "x": 0, "y": 0},
                {"name": "Sfax", "x": 4, "y": -2},
                {"name": "Sousse", "x": 2, "y": 1},
                {"name": "Kairouan", "x": 1, "y": -1},
                {"name": "Bizerte", "x": -1, "y": 2},
                {"name": "Gabès", "x": 5, "y": -3},
                {"name": "Gafsa", "x": 3, "y": -4},
                {"name": "Tozeur", "x": 4, "y": -5}
            ]

            example_links = [
                {"from": 0, "to": 1, "distance": 4.2},
                {"from": 0, "to": 2, "distance": 1.4},
                {"from": 0, "to": 3, "distance": 1.6},
                {"from": 0, "to": 4, "distance": 0.8},
                {"from": 0, "to": 5, "distance": 4.8},
                {"from": 0, "to": 6, "distance": 3.4},
                {"from": 0, "to": 7, "distance": 4.6},

                {"from": 2, "to": 1, "distance": 2.8},
                {"from": 2, "to": 4, "distance": 2.0},

                {"from": 1, "to": 5, "distance": 1.0},
                {"from": 5, "to": 7, "distance": 1.4},
                {"from": 6, "to": 7, "distance": 1.2},
                {"from": 1, "to": 6, "distance": 2.0},

                {"from": 3, "to": 2, "distance": 1.2},
                {"from": 3, "to": 1, "distance": 3.0},
                {"from": 3, "to": 6, "distance": 2.5},

                {"from": 4, "to": 2, "distance": 2.0},

                {"from": 6, "to": 5, "distance": 2.2},
                {"from": 7, "to": 1, "distance": 3.8},
            ]

            example_demands = [
                [0, 80, 120, 40, 60, 30, 20, 10], # Tunis
                [80, 0, 60, 30, 20, 50, 40, 25],  # Sfax
                [120, 60, 0, 50, 40, 25, 15, 8],  # Sousse
                [40, 30, 50, 0, 15, 20, 30, 15],  # Kairouan
                [60, 20, 40, 15, 0, 10, 8, 5],    # Bizerte
                [30, 50, 25, 20, 10, 0, 35, 40],  # Gabès
                [20, 40, 15, 30, 8, 35, 0, 45],   # Gafsa
                [10, 25, 8, 15, 5, 40, 45, 0]     # Tozeur
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


        # Telecom tab - 6.2
        self.telecom_tab = QWidget()
        self.telecom_controller = TelecomController(self.telecom_tab)
        self.tab_widget.addTab(self.telecom_tab, "📡 Telecom Network")

        # Mailbox tab - 5.3
        self.mailbox_tab = QWidget()
        self.mailbox_controller = MailboxController(self.mailbox_tab)
        self.tab_widget.addTab(self.mailbox_tab, "📮 Mailbox Location")

        # Antenna tab - 4.4
        self.antenna_tab = QWidget()
        self.antenna_controller = AntennaController(self.antenna_tab)
        self.tab_widget.addTab(self.antenna_tab, "📶 Antenna Placement")

        self.setCentralWidget(self.tab_widget)
        self.statusBar().showMessage("Ready")

class AntennaController:
    """Controller for antenna placement module"""

    def __init__(self, parent_widget):
        self.parent = parent_widget

        # Create UI
        self.ui = AntennaUI()
        parent_layout = parent_widget.layout()
        if parent_layout is None:
            parent_widget.setLayout(QVBoxLayout())
            parent_widget.layout().addWidget(self.ui)
        else:
            parent_layout.addWidget(self.ui)

        # Setup canvas
        self.antenna_canvas = MatplotlibCanvas(self.ui.antennaGraphWidget)
        graph_layout = self.ui.antennaGraphWidget.layout()
        if graph_layout is None:
            graph_layout = QVBoxLayout(self.ui.antennaGraphWidget)
        graph_layout.addWidget(self.antenna_canvas)

        self.setup_connections()
        self.load_example_data()

    def setup_connections(self):
        self.ui.btnAddUser.clicked.connect(self.add_user_row)
        self.ui.btnAddSite.clicked.connect(self.add_site_row)
        self.ui.btnSolveAntenna.clicked.connect(self.solve_antenna)

    def load_example_data(self):
        # Create default example data
        users = [
            {"x": 1, "y": 1, "demand": 10},
            {"x": 2, "y": 3, "demand": 15},
            {"x": 4, "y": 2, "demand": 8},
            {"x": 3, "y": 5, "demand": 12},
            {"x": 5, "y": 4, "demand": 20},
            {"x": 6, "y": 1, "demand": 5},
            {"x": 2, "y": 6, "demand": 18},
            {"x": 4, "y": 7, "demand": 10},
            {"x": 7, "y": 3, "demand": 15},
            {"x": 8, "y": 5, "demand": 8}
        ]

        sites = [
            {"name": "Centre", "x": 2, "y": 2, "cost": 50000},
            {"name": "Nord", "x": 3, "y": 6, "cost": 55000},
            {"name": "Est", "x": 4, "y": 4, "cost": 60000},
            {"name": "Sud", "x": 6, "y": 2, "cost": 52000},
            {"name": "Nord-Est", "x": 7, "y": 5, "cost": 58000},
            {"name": "Ouest", "x": 1, "y": 4, "cost": 48000}
        ]

        # Load users
        self.ui.tableUsers.setRowCount(len(users))
        for i, user in enumerate(users):
            self.ui.tableUsers.setItem(i, 0, QTableWidgetItem(str(user['x'])))
            self.ui.tableUsers.setItem(i, 1, QTableWidgetItem(str(user['y'])))
            self.ui.tableUsers.setItem(i, 2, QTableWidgetItem(str(user['demand'])))

        # Load sites
        self.ui.tableSites.setRowCount(len(sites))
        for i, site in enumerate(sites):
            self.ui.tableSites.setItem(i, 0, QTableWidgetItem(site['name']))
            self.ui.tableSites.setItem(i, 1, QTableWidgetItem(str(site['x'])))
            self.ui.tableSites.setItem(i, 2, QTableWidgetItem(str(site['y'])))
            self.ui.tableSites.setItem(i, 3, QTableWidgetItem(str(site['cost'])))

    def add_user_row(self):
        row = self.ui.tableUsers.rowCount()
        self.ui.tableUsers.insertRow(row)

    def add_site_row(self):
        row = self.ui.tableSites.rowCount()
        self.ui.tableSites.insertRow(row)

    def parse_antenna_data(self):
        # Parse users
        users = []
        for row in range(self.ui.tableUsers.rowCount()):
            try:
                x = float(self.ui.tableUsers.item(row, 0).text())
                y = float(self.ui.tableUsers.item(row, 1).text())
                demand = float(self.ui.tableUsers.item(row, 2).text() or "1")
                users.append({"id": row, "x": x, "y": y, "demand": demand})
            except:
                users.append({"id": row, "x": 0, "y": 0, "demand": 1})

        # Parse sites
        candidate_sites = []
        setup_costs = []
        for row in range(self.ui.tableSites.rowCount()):
            try:
                name = self.ui.tableSites.item(row, 0).text() or f"Site {row}"
                x = float(self.ui.tableSites.item(row, 1).text())
                y = float(self.ui.tableSites.item(row, 2).text())
                cost = float(self.ui.tableSites.item(row, 3).text() or "50000")
                candidate_sites.append({"id": row, "name": name, "x": x, "y": y})
                setup_costs.append(cost)
            except:
                candidate_sites.append({"id": row, "name": f"Site {row}", "x": 0, "y": 0})
                setup_costs.append(50000)

        # Parse parameters
        coverage_radius = float(self.ui.spinCoverageRadius.value())
        max_antennas = int(self.ui.spinMaxAntennas.value())
        capacities = [float(x.strip()) for x in self.ui.txtCapacities.text().split(',')]

        return {
            "users": users,
            "candidate_sites": candidate_sites,
            "setup_costs": setup_costs,
            "capacities": capacities,
            "coverage_radius": coverage_radius,
            "max_antennas": max_antennas
        }

    def solve_antenna(self):
        try:
            data = self.parse_antenna_data()

            solver = AntennaPlacementSolver(
                users=data['users'],
                candidate_sites=data['candidate_sites'],
                setup_costs=data['setup_costs'],
                capacities=data['capacities'],
                coverage_radius=data['coverage_radius'],
                max_antennas=data['max_antennas']
            )

            result = solver.solve()
            self.display_antenna_results(result)
            self.plot_antenna_solution(data['users'], result['selected_sites'], data['coverage_radius'])

        except Exception as e:
            QMessageBox.critical(self.parent, "Error", f"Optimization error: {str(e)}")

    def display_antenna_results(self, result):
        text = f"""
<b>RÉSULTATS DU PLACEMENT D'ANTENNES</b>
<hr>
<b>Coût Total:</b> {result['objective']:,.0f} €<br>
<b>Coût Installation:</b> {result['setup_cost']:,.0f} €<br>
<b>Coût Connexion:</b> {result['connection_cost']:,.0f} €<br><br>

<b>Antennes Installées:</b> {result['num_antennas']}<br>
<b>Utilisateurs Totaux:</b> {result['total_users']}<br>
<b>Utilisateurs Couverts:</b> {result['covered_users']} ({result['coverage_rate']*100:.1f}%)<br>
<b>Capacité Totale:</b> {result['total_capacity']} utilisateurs<br>
<b>Utilisation Moyenne:</b> {result['avg_utilization']*100:.1f}%<br><br>

<b>DÉTAIL DES ANTENNES:</b><br>
"""

        for i, site in enumerate(result['selected_sites']):
            text += f"""
<b>Antenne {i+1}:</b> {site.get('name', f'Site {i}')}<br>
• Position: ({site['x']:.1f}, {site['y']:.1f})<br>
• Capacité: {site.get('capacity', 0)} utilisateurs<br>
• Utilisateurs affectés: {site.get('num_users', 0)}<br>
• Utilisation: {site.get('utilization', 0)*100:.1f}%<br>
• Coût installation: {site.get('setup_cost', 0):,.0f} €<br>
"""

        self.ui.textAntennaResults.setHtml(text)

    def plot_antenna_solution(self, users, selected_sites, coverage_radius):
        self.antenna_canvas.figure.clear()
        fig = plot_antenna_solution(users, selected_sites, coverage_radius)
        self.antenna_canvas.figure = fig
        self.antenna_canvas.draw()



def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    window = Main()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
