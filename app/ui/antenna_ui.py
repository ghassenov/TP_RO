from PySide6.QtCore import Qt
from PySide6.QtWidgets import (QCheckBox, QDoubleSpinBox, QFormLayout,
                               QGroupBox, QLabel, QLineEdit, QPushButton,
                               QSpinBox, QSplitter, QTableWidget, QTabWidget,
                               QTextEdit, QVBoxLayout, QWidget)


class AntennaUI(QWidget):
    """UI pour le placement d'antennes télécom"""

    def __init__(self):
        super().__init__()
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        title = QLabel("Placement d'Antennes Télécom et Affectation des Utilisateurs")
        title.setStyleSheet("font-size: 14pt; font-weight: bold; padding: 10px;")
        layout.addWidget(title)

        self.tabs = QTabWidget()

        # Users tab
        users_tab = QWidget()
        users_layout = QVBoxLayout(users_tab)
        users_layout.addWidget(QLabel("Utilisateurs (x, y, demande):"))
        self.tableUsers = QTableWidget()
        self.tableUsers.setColumnCount(3)
        self.tableUsers.setHorizontalHeaderLabels(["X", "Y", "Demande"])
        users_layout.addWidget(self.tableUsers)

        self.btnAddUser = QPushButton("Ajouter Utilisateur")
        users_layout.addWidget(self.btnAddUser)

        self.tabs.addTab(users_tab, "Utilisateurs")

        # Sites tab
        sites_tab = QWidget()
        sites_layout = QVBoxLayout(sites_tab)
        sites_layout.addWidget(QLabel("Sites Candidats (nom, x, y, coût):"))
        self.tableSites = QTableWidget()
        self.tableSites.setColumnCount(4)
        self.tableSites.setHorizontalHeaderLabels(["Nom", "X", "Y", "Coût Installation"])
        sites_layout.addWidget(self.tableSites)

        self.btnAddSite = QPushButton("Ajouter Site")
        sites_layout.addWidget(self.btnAddSite)

        self.tabs.addTab(sites_tab, "Sites")

        # Parameters tab
        params_tab = QWidget()
        params_layout = QVBoxLayout(params_tab)

        param_group = QGroupBox("Paramètres d'Optimisation")
        param_form = QFormLayout()

        self.spinCoverageRadius = QDoubleSpinBox()
        self.spinCoverageRadius.setMinimum(0.1)
        self.spinCoverageRadius.setMaximum(100.0)
        self.spinCoverageRadius.setValue(4.0)
        param_form.addRow("Rayon de Couverture:", self.spinCoverageRadius)

        self.spinMaxAntennas = QSpinBox()
        self.spinMaxAntennas.setMinimum(1)
        self.spinMaxAntennas.setMaximum(50)
        self.spinMaxAntennas.setValue(4)
        param_form.addRow("Antennes Max:", self.spinMaxAntennas)

        self.txtCapacities = QLineEdit("50,100,150,200")
        param_form.addRow("Options de Capacité:", self.txtCapacities)

        self.spinMinCoverage = QDoubleSpinBox()
        self.spinMinCoverage.setMinimum(0.0)
        self.spinMinCoverage.setMaximum(100.0)
        self.spinMinCoverage.setValue(80.0)
        self.spinMinCoverage.setSuffix("%")
        param_form.addRow("Couverture Minimale:", self.spinMinCoverage)

        self.chkCapacityConstraint = QCheckBox("Activer contraintes de capacité")
        self.chkCapacityConstraint.setChecked(True)
        param_form.addRow("", self.chkCapacityConstraint)

        param_group.setLayout(param_form)
        params_layout.addWidget(param_group)

        self.tabs.addTab(params_tab, "Paramètres")

        layout.addWidget(self.tabs)

        # Solve button
        self.btnSolveAntenna = QPushButton("Optimiser le Placement d'Antennes")
        self.btnSolveAntenna.setStyleSheet("font-weight: bold; padding: 10px; background-color: #4CAF50; color: white;")
        layout.addWidget(self.btnSolveAntenna)

        # Results area
        results_splitter = QSplitter(Qt.Horizontal)

        self.textAntennaResults = QTextEdit()
        self.textAntennaResults.setReadOnly(True)
        results_splitter.addWidget(self.textAntennaResults)

        self.antennaGraphWidget = QWidget()
        results_splitter.addWidget(self.antennaGraphWidget)
        results_splitter.setSizes([300, 700])

        layout.addWidget(results_splitter)

        self.setLayout(layout)
