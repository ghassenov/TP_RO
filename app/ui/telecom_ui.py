from PySide6.QtCore import Qt
from PySide6.QtWidgets import (QDoubleSpinBox, QFormLayout, QGroupBox, QLabel,
                               QLineEdit, QPushButton, QSplitter, QTableWidget,
                               QTabWidget, QTextEdit, QVBoxLayout, QWidget)


class TelecomUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        title = QLabel("Telecom Network Design - Fiber Optic Network Optimization")
        title.setStyleSheet("font-size: 14pt; font-weight: bold; padding: 10px;")
        layout.addWidget(title)

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

        # Results area
        results_splitter = QSplitter(Qt.Horizontal)

        self.textTelecomResults = QTextEdit()
        self.textTelecomResults.setReadOnly(True)
        results_splitter.addWidget(self.textTelecomResults)

        self.telecomGraphWidget = QWidget()
        results_splitter.addWidget(self.telecomGraphWidget)
        results_splitter.setSizes([300, 700])

        layout.addWidget(results_splitter)

        self.setLayout(layout)
