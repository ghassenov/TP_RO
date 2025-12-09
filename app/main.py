import sys

# Matplotlib
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.figure import Figure
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QAction, QIcon
from PySide6.QtWidgets import (QApplication, QLabel, QMainWindow, QMessageBox,
                               QProgressBar, QTableWidgetItem, QTabWidget,
                               QVBoxLayout, QWidget)

from app.models.triangulation_model import TriangulationModel
# Solver imports
from app.solvers.antenna_solver import AntennaPlacementSolver
from app.solvers.mailbox_solver import MailboxLocationSolver
from app.solvers.mis_solver import MISSolver
from app.solvers.telecom_solver import TelecomNetworkSolver
from app.solvers.triangulation_solver import AppTriangulationSolver
from app.ui.antenna_ui import AntennaUI
from app.ui.introduction_ui import IntroductionController, IntroductionTab
# UI imports
from app.ui.mailbox_ui import MailboxUI
from app.ui.mis_ui import MISUI
from app.ui.telecom_ui import TelecomUI
from modules.subject_triangulation.model import Triangle
# Visualization imports
from shared.visualization import (plot_antenna_solution, plot_mailbox_solution,
                                  plot_mis_solution, plot_telecom_solution,
                                  plot_triangulation_solution)


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


class MISController:
    """Controller for Maximum Independent Set module"""

    def __init__(self, parent_widget):
        self.parent = parent_widget

        # Create UI
        self.ui = MISUI()
        parent_layout = parent_widget.layout()
        if parent_layout is None:
            parent_widget.setLayout(QVBoxLayout())
            parent_widget.layout().addWidget(self.ui)
        else:
            parent_layout.addWidget(self.ui)

        # Setup canvas
        self.mis_canvas = MatplotlibCanvas(self.ui.misGraphWidget)
        graph_layout = self.ui.misGraphWidget.layout()
        if graph_layout is None:
            graph_layout = QVBoxLayout(self.ui.misGraphWidget)
        graph_layout.addWidget(self.mis_canvas)

        self.setup_connections()
        self.load_example_data()

    def setup_connections(self):
        self.ui.btnAddTask.clicked.connect(self.add_task_row)
        self.ui.btnAddConflict.clicked.connect(self.add_conflict_row)
        self.ui.btnAutoDetect.clicked.connect(self.auto_detect_conflicts)
        self.ui.btnSolveMIS.clicked.connect(self.solve_mis)

    def load_example_data(self):
        # Example tasks
        tasks = [
            {"name": "Traitement données", "duration": 10, "priority": 3, "resource": "CPU"},
            {"name": "Sauvegarde BD", "duration": 5, "priority": 2, "resource": "Disk"},
            {"name": "Analyse images", "duration": 15, "priority": 4, "resource": "GPU"},
            {"name": "Envoi emails", "duration": 2, "priority": 1, "resource": "Network"},
            {"name": "Calcul scientifique", "duration": 20, "priority": 5, "resource": "CPU"},
            {"name": "Synthèse rapport", "duration": 8, "priority": 2, "resource": "Memory"},
            {"name": "Entraînement ML", "duration": 30, "priority": 4, "resource": "GPU"},
            {"name": "Vérification sécurité", "duration": 3, "priority": 3, "resource": "CPU"}
        ]

        # Example conflicts
        conflicts = [
            [0, 4], [0, 7], [4, 7], [2, 6],
            [0, 5], [4, 5], [1, 3], [3, 6]
        ]

        # Load tasks
        self.ui.tableTasks.setRowCount(len(tasks))
        for i, task in enumerate(tasks):
            self.ui.tableTasks.setItem(i, 0, QTableWidgetItem(task['name']))
            self.ui.tableTasks.setItem(i, 1, QTableWidgetItem(str(task['duration'])))
            self.ui.tableTasks.setItem(i, 2, QTableWidgetItem(str(task['priority'])))
            self.ui.tableTasks.setItem(i, 3, QTableWidgetItem(task['resource']))

        # Load conflicts
        self.ui.tableConflicts.setRowCount(len(conflicts))
        for i, conflict in enumerate(conflicts):
            self.ui.tableConflicts.setItem(i, 0, QTableWidgetItem(str(conflict[0])))
            self.ui.tableConflicts.setItem(i, 1, QTableWidgetItem(str(conflict[1])))

    def add_task_row(self):
        row = self.ui.tableTasks.rowCount()
        self.ui.tableTasks.insertRow(row)

    def add_conflict_row(self):
        row = self.ui.tableConflicts.rowCount()
        self.ui.tableConflicts.insertRow(row)

    def auto_detect_conflicts(self):
        """Détecter automatiquement les conflits basés sur les ressources"""
        num_tasks = self.ui.tableTasks.rowCount()

        # Collecter les ressources par tâche
        resources = []
        for i in range(num_tasks):
            resource_item = self.ui.tableTasks.item(i, 3)
            if resource_item:
                resources.append(resource_item.text().strip())
            else:
                resources.append("")

        # Trouver les conflits (tâches partageant la même ressource)
        conflicts = []
        for i in range(num_tasks):
            for j in range(i + 1, num_tasks):
                if resources[i] and resources[i] == resources[j]:
                    conflicts.append([i, j])

        # Afficher les conflits détectés
        self.ui.tableConflicts.setRowCount(len(conflicts))
        for idx, conflict in enumerate(conflicts):
            self.ui.tableConflicts.setItem(idx, 0, QTableWidgetItem(str(conflict[0])))
            self.ui.tableConflicts.setItem(idx, 1, QTableWidgetItem(str(conflict[1])))

    def parse_mis_data(self):
        # Parse tasks
        tasks = []
        for row in range(self.ui.tableTasks.rowCount()):
            try:
                name = self.ui.tableTasks.item(row, 0).text() or f"Tâche {row}"
                duration = int(self.ui.tableTasks.item(row, 1).text() or "1")
                priority = int(self.ui.tableTasks.item(row, 2).text() or "1")
                resource = self.ui.tableTasks.item(row, 3).text() or ""
                tasks.append({
                    "id": row,
                    "name": name,
                    "duration": duration,
                    "priority": priority,
                    "resource": resource
                })
            except:
                tasks.append({
                    "id": row,
                    "name": f"Tâche {row}",
                    "duration": 1,
                    "priority": 1,
                    "resource": ""
                })

        # Parse conflicts
        conflicts = []
        for row in range(self.ui.tableConflicts.rowCount()):
            try:
                task1 = int(self.ui.tableConflicts.item(row, 0).text())
                task2 = int(self.ui.tableConflicts.item(row, 1).text())
                if 0 <= task1 < len(tasks) and 0 <= task2 < len(tasks):
                    conflicts.append([task1, task2])
            except:
                continue

        return {
            "tasks": tasks,
            "conflicts": conflicts,
            "use_weights": self.ui.chkUseWeights.isChecked()
        }

    def solve_mis(self):
        try:
            data = self.parse_mis_data()

            # Utiliser les priorités comme poids si demandé
            weights = None
            if data['use_weights']:
                weights = [task['priority'] for task in data['tasks']]

            solver = MISSolver(
                tasks=data['tasks'],
                conflicts=data['conflicts'],
                weights=weights
            )

            result = solver.solve()
            self.display_mis_results(result)
            self.plot_mis_solution(data['tasks'], data['conflicts'], result['selected_tasks'])

        except Exception as e:
            QMessageBox.critical(self.parent, "Error", f"Optimization error: {str(e)}")

    def display_mis_results(self, result):
        objective_type = "somme des priorités" if self.ui.chkUseWeights.isChecked() else "nombre de tâches"

        text = f"""
<b>RÉSULTATS DE L'ENSEMBLE INDÉPENDANT MAXIMUM</b>
<hr>
<b>Valeur objective ({objective_type}):</b> {result['objective']}<br>
<b>Tâches sélectionnées:</b> {result['total_tasks']}/{result['total_possible_tasks']} ({result['selection_ratio']*100:.1f}%)<br>
<b>Validité:</b> {"✓ Oui" if result['is_valid'] else "✗ Non"}<br><br>

<b>TÂCHES SÉLECTIONNÉES:</b><br>
"""

        for i, task in enumerate(result['selected_tasks']):
            text += f"""
<b>Tâche {i+1}:</b> {task['name']}<br>
• ID: {task['id']}<br>
• Durée: {task.get('duration', 0)}<br>
• Priorité: {task.get('priority', 1)}<br>
• Ressource: {task.get('resource', 'N/A')}<br>
• Conflits: {task.get('num_conflicts', 0)} autres tâches<br>
"""

        text += f"<br><b>Note:</b> {result.get('status', '')} {result.get('note', '')}"

        self.ui.textMISResults.setHtml(text)

    def plot_mis_solution(self, tasks, conflicts, selected_tasks):
        self.mis_canvas.figure.clear()
        fig = plot_mis_solution(tasks, conflicts, selected_tasks)
        self.mis_canvas.figure = fig
        self.mis_canvas.draw()


from app.styles import STYLESHEET
# Add at the top
from app.theme import Theme


def main():
    app = QApplication(sys.argv)

    # Apply theme
    Theme.setup_light_theme(app)  # or Theme.setup_dark_theme(app)
    app.setStyleSheet(STYLESHEET)

    # Set application icon
    app.setWindowIcon(QIcon("app/ui/icon.png"))  # Add an icon

    # Create and show main window
    window = Main()

    # Center window on screen
    screen_geometry = app.primaryScreen().availableGeometry()
    window_size = window.size()
    window.move(
        (screen_geometry.width() - window_size.width()) // 2,
        (screen_geometry.height() - window_size.height()) // 2
    )

    window.show()
    sys.exit(app.exec())

from app.ui.triangulation_ui import TriangulationUI  # Use the new UI
from modules.subject_triangulation.model import TrussStructure
from modules.subject_triangulation.solver import SimpleTriangulationSolver


class TriangulationController:
    """Controller for triangle decomposition - Clean layout"""

    def __init__(self, parent_widget):
        self.parent = parent_widget

        # Create UI
        self.ui = TriangulationUI()
        parent_widget.setLayout(QVBoxLayout())
        parent_widget.layout().addWidget(self.ui)

        # Setup connections
        self.ui.btnAddPoint.clicked.connect(self.add_point)
        self.ui.btnAddTriangle.clicked.connect(self.add_triangle)
        self.ui.btnSolve.clicked.connect(self.solve)

        # Setup matplotlib canvas
        self.canvas = MatplotlibCanvas(self.ui.graphWidget)
        graph_layout = self.ui.graphWidget.layout()
        if graph_layout is None:
            graph_layout = QVBoxLayout(self.ui.graphWidget)
        graph_layout.addWidget(self.canvas)

        # Initialize structure
        self.structure = TrussStructure()
        self.ui.update_status("Ready - Loaded example data")

    def add_point(self):
        """Add a new point row"""
        row = self.ui.tablePoints.rowCount()
        self.ui.tablePoints.insertRow(row)
        # Set default ID
        self.ui.tablePoints.setItem(row, 0, QTableWidgetItem(str(row)))
        self.ui.update_status(f"Added point row {row}")

    def add_triangle(self):
        """Add a new triangle row"""
        row = self.ui.tableTriangles.rowCount()
        self.ui.tableTriangles.insertRow(row)
        self.ui.update_status(f"Added triangle row {row}")

    def parse_input_data(self):
        """Parse data from UI tables"""
        # Parse points
        points = []
        for row in range(self.ui.tablePoints.rowCount()):
            try:
                x_item = self.ui.tablePoints.item(row, 1)
                y_item = self.ui.tablePoints.item(row, 2)

                if x_item and y_item and x_item.text() and y_item.text():
                    x = float(x_item.text())
                    y = float(y_item.text())
                    points.append({
                        'id': row,
                        'x': x,
                        'y': y
                    })
            except:
                continue

        # Parse triangles
        triangles = []
        for row in range(self.ui.tableTriangles.rowCount()):
            try:
                p1_item = self.ui.tableTriangles.item(row, 0)
                p2_item = self.ui.tableTriangles.item(row, 1)
                p3_item = self.ui.tableTriangles.item(row, 2)
                cost_item = self.ui.tableTriangles.item(row, 3)

                if p1_item and p2_item and p3_item:
                    p1 = int(p1_item.text() or "0")
                    p2 = int(p2_item.text() or "1")
                    p3 = int(p3_item.text() or "2")
                    cost = float(cost_item.text()) if cost_item and cost_item.text() else 1.0

                    triangles.append({
                        'vertices': (p1, p2, p3),
                        'cost': cost
                    })
            except:
                continue

        return points, triangles

    def solve(self):
        """Solve the optimization problem"""
        try:
            self.ui.update_status("Solving...")

            # Parse data
            points, triangles = self.parse_input_data()

            if len(points) < 3:
                raise ValueError("Need at least 3 points")

            # Create structure
            self.structure = TrussStructure()

            # Add points
            for p in points:
                self.structure.add_point(p['x'], p['y'])

            # Add triangles
            for t in triangles:
                self.structure.add_triangle(t['vertices'], t['cost'])

            # Set parameters from UI
            self.structure.min_triangles = self.ui.spinMinTriangles.value()
            self.structure.max_triangles = self.ui.spinMaxTriangles.value()
            self.structure.budget = self.ui.spinBudget.value()

            # Solve
            solver = SimpleTriangulationSolver(self.structure)
            result = solver.solve_with_gurobi()

            # Display results
            self.display_results(result)

            # Update status
            if result['status'] in ['OPTIMAL', 'SUCCESS']:
                self.ui.update_status(f"Solved: {result['num_triangles']} triangles selected")
            else:
                self.ui.update_status(f"Failed: {result.get('error', 'Unknown error')}", is_error=True)

            # Plot results if available
            if result.get('selected_triangles'):
                self.plot_solution(result)

        except Exception as e:
            self.ui.update_status(f"Error: {str(e)}", is_error=True)
            QMessageBox.critical(self.parent, "Error", f"Optimization error: {str(e)}")

    def display_results(self, result):
        """Display results in HTML format like other tabs"""
        if result['status'] not in ['OPTIMAL', 'SUCCESS']:
            html = f"""
            <h3 style='color: #e74c3c;'>❌ Optimization Failed</h3>
            <p><b>Error:</b> {result.get('error', 'Unknown error')}</p>
            """
            self.ui.textResults.setHtml(html)
            return

        # Format successful results
        coverage_pct = result['coverage_rate'] * 100

        html = f"""
        <h3 style='color: #2ecc71;'>✅ Optimization Successful</h3>
        <hr>
        <table style='width: 100%; border-collapse: collapse;'>
            <tr>
                <td style='padding: 5px;'><b>Status:</b></td>
                <td style='padding: 5px;'>{result['status']}</td>
            </tr>
            <tr style='background-color: #f8f9fa;'>
                <td style='padding: 5px;'><b>Triangles Selected:</b></td>
                <td style='padding: 5px;'>{result['num_triangles']}</td>
            </tr>
            <tr>
                <td style='padding: 5px;'><b>Total Cost:</b></td>
                <td style='padding: 5px;'>{result['total_cost']:.2f} €</td>
            </tr>
            <tr style='background-color: #f8f9fa;'>
                <td style='padding: 5px;'><b>Points Covered:</b></td>
                <td style='padding: 5px;'>{result['covered_points']}/{result['total_points']} ({coverage_pct:.1f}%)</td>
            </tr>
            <tr>
                <td style='padding: 5px;'><b>Method:</b></td>
                <td style='padding: 5px;'>{result.get('method', 'Gurobi')}</td>
            </tr>
        </table>

        <h4>Selected Triangles:</h4>
        <table style='width: 100%; border-collapse: collapse; border: 1px solid #ddd;'>
            <tr style='background-color: #1abc9c; color: white;'>
                <th style='padding: 8px;'>Triangle</th>
                <th style='padding: 8px;'>Points</th>
                <th style='padding: 8px;'>Cost</th>
            </tr>
        """

        if result.get('selected_triangles'):
            for i, tri in enumerate(result['selected_triangles']):
                p1, p2, p3 = tri.vertices
                html += f"""
                <tr style='border-bottom: 1px solid #ddd;'>
                    <td style='padding: 8px;'>{i+1}</td>
                    <td style='padding: 8px;'>({p1}, {p2}, {p3})</td>
                    <td style='padding: 8px;'>{tri.cost:.2f} €</td>
                </tr>
                """
        else:
            html += """
            <tr>
                <td colspan='3' style='padding: 8px; text-align: center;'>No triangles selected</td>
            </tr>
            """

        html += "</table>"

        self.ui.textResults.setHtml(html)

    def plot_solution(self, result):
        """Plot the solution"""
        try:
            from shared.visualization import plot_triangulation_solution

            if not result.get('selected_triangles'):
                return

            # Prepare data for plotting
            points_data = []
            for i, point in enumerate(self.structure.points):
                points_data.append({
                    'id': i,
                    'x': point.x,
                    'y': point.y
                })

            triangles_data = []
            for tri in result['selected_triangles']:
                triangles_data.append({
                    'vertices': tri.vertices,
                    'cost': tri.cost
                })

            # Create figure
            self.canvas.figure.clear()
            fig = plot_triangulation_solution(
                points=points_data,
                selected_triangles=triangles_data,
                title="Truss Structure Optimization"
            )
            self.canvas.figure = fig
            self.canvas.draw()

        except Exception as e:
            print(f"Error plotting: {e}")



class Main(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Optimization Suite v2.0 - Operations Research Tools")
        self.setGeometry(100, 100, 1600, 900)  # Larger window

        # Create central widget with tabs
        self.tab_widget = QTabWidget()
        self.tab_widget.setTabPosition(QTabWidget.North)
        self.tab_widget.setMovable(True)


        # introduction tab
        self.intro_tab = QWidget()
        self.intro_controller = IntroductionController(self.intro_tab)
        self.tab_widget.addTab(self.intro_tab, "🏠 Home")

        # 14.1 - MIS Scheduling Tab
        self.mis_tab = QWidget()
        self.mis_controller = MISController(self.mis_tab)
        self.tab_widget.addTab(self.mis_tab, "📊 MIS Scheduling")

        # 6.2 - Telecom Network Tab
        self.telecom_tab = QWidget()
        self.telecom_controller = TelecomController(self.telecom_tab)
        self.tab_widget.addTab(self.telecom_tab, "📡 Telecom")

        # 5.3 - Mailbox Location Tab
        self.mailbox_tab = QWidget()
        self.mailbox_controller = MailboxController(self.mailbox_tab)
        self.tab_widget.addTab(self.mailbox_tab, "📮 Mailbox")

        # 4.4 - Antenna Placement Tab
        self.antenna_tab = QWidget()
        self.antenna_controller = AntennaController(self.antenna_tab)
        self.tab_widget.addTab(self.antenna_tab, "📶 Antenna")

        # 10.5 - Triangulation
        self.triangulation_tab = QWidget()
        self.triangulation_controller = TriangulationController(self.triangulation_tab)
        self.tab_widget.addTab(self.triangulation_tab, "🔺 Triangulation")

        self.setCentralWidget(self.tab_widget)

        # Create status bar with widgets
        self.status_bar = self.statusBar()
        self.status_bar.showMessage("Ready - Optimization Suite v2.0")

        # Add progress bar to status bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setMaximumWidth(200)
        self.progress_bar.setVisible(False)
        self.status_bar.addPermanentWidget(self.progress_bar)

        # Add memory usage label
        self.memory_label = QLabel("Memory: --")
        self.status_bar.addPermanentWidget(self.memory_label)

        # Create menu bar
        # self.create_menu_bar()

        # Timer for updating status
        # self.timer = QTimer()
        # self.timer.timeout.connect(self.update_status)
        # self.timer.start(5000)

    def create_menu_bar(self):
        menubar = self.menuBar()

        # View menu
        view_menu = menubar.addMenu("👁️ View")

        theme_menu = view_menu.addMenu("Theme")
        light_action = QAction("Light Theme", self)
        dark_action = QAction("Dark Theme", self)
        theme_menu.addAction(light_action)
        theme_menu.addAction(dark_action)
        dark_action.triggered.connect(
                lambda: Theme.setup_dark_theme(QApplication.instance())
                )
        light_action.triggered.connect(
                lambda: Theme.setup_light_theme(QApplication.instance())
                )

        # Help menu
        help_menu = menubar.addMenu("❓ Help")

        about_action = QAction("About", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)

    def update_status(self, message="", is_error=False):
        """Update status bar with colored message"""
        if is_error:
            self.status_bar.showMessage(f"❌ {message}", 5000)
            self.status_bar.setStyleSheet("""
                QStatusBar {
                    background-color: #ffebee;
                    color: #c62828;
                    font-weight: bold;
                }
            """)
            QTimer.singleShot(5000, self.reset_status_style)
        else:
            self.status_bar.showMessage(f"✅ {message}", 3000)
            self.status_bar.setStyleSheet("""
                QStatusBar {
                    background-color: #e8f5e9;
                    color: #2e7d32;
                }
            """)
            QTimer.singleShot(3000, self.reset_status_style)

    def reset_status_style(self):
        """Reset status bar to default style"""
        self.status_bar.setStyleSheet("")


    def show_about(self):
        QMessageBox.about(self, "About Optimization Suite",
            "<h2>Optimization Suite v2.0</h2>"
            "<p><b>Advanced Operations Research Tools</b></p>"
            "<p>Developed for academic project</p>"
            "<p>Modules: Mailbox Location, Telecom Network, "
            "Antenna Placement, MIS Scheduling</p>"
            "<p>Using: PySide6, Gurobi, Matplotlib</p>"
            "<p>© 2024 - All rights reserved</p>")

if __name__ == "__main__":
    main()
