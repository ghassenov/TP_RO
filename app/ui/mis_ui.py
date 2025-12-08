from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QTabWidget, QLabel,
    QTableWidget, QPushButton, QGroupBox, QFormLayout,
    QLineEdit, QSpinBox, QSplitter, QTextEdit,
    QCheckBox, QHBoxLayout, QComboBox
)
from PySide6.QtCore import Qt

class MISUI(QWidget):
    """UI pour l'Ensemble Indépendant Maximum (ordonnancement de tâches)"""

    def __init__(self):
        super().__init__()
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        title = QLabel("Ensemble Indépendant Maximum - Ordonnancement de Tâches Concurrentes")
        title.setStyleSheet("font-size: 14pt; font-weight: bold; padding: 10px;")
        layout.addWidget(title)

        self.tabs = QTabWidget()

        # Tasks tab
        tasks_tab = QWidget()
        tasks_layout = QVBoxLayout(tasks_tab)
        tasks_layout.addWidget(QLabel("Tâches (nom, durée, priorité, ressource):"))
        self.tableTasks = QTableWidget()
        self.tableTasks.setColumnCount(4)
        self.tableTasks.setHorizontalHeaderLabels(["Nom", "Durée", "Priorité", "Ressource"])
        tasks_layout.addWidget(self.tableTasks)

        self.btnAddTask = QPushButton("Ajouter Tâche")
        tasks_layout.addWidget(self.btnAddTask)

        self.tabs.addTab(tasks_tab, "Tâches")

        # Conflicts tab
        conflicts_tab = QWidget()
        conflicts_layout = QVBoxLayout(conflicts_tab)
        conflicts_layout.addWidget(QLabel("Conflits entre tâches (ID1, ID2):"))
        self.tableConflicts = QTableWidget()
        self.tableConflicts.setColumnCount(2)
        self.tableConflicts.setHorizontalHeaderLabels(["Tâche 1", "Tâche 2"])
        conflicts_layout.addWidget(self.tableConflicts)

        btn_layout = QHBoxLayout()
        self.btnAddConflict = QPushButton("Ajouter Conflit")
        self.btnAutoDetect = QPushButton("Détection Auto par Ressource")
        btn_layout.addWidget(self.btnAddConflict)
        btn_layout.addWidget(self.btnAutoDetect)
        conflicts_layout.addLayout(btn_layout)

        self.tabs.addTab(conflicts_tab, "Conflits")

        # Parameters tab
        params_tab = QWidget()
        params_layout = QVBoxLayout(params_tab)

        param_group = QGroupBox("Paramètres d'Optimisation")
        param_form = QFormLayout()

        self.comboObjective = QComboBox()
        self.comboObjective.addItems(["Maximiser le nombre de tâches", "Maximiser la somme des priorités"])
        param_form.addRow("Objectif:", self.comboObjective)

        self.spinTimeLimit = QSpinBox()
        self.spinTimeLimit.setMinimum(1)
        self.spinTimeLimit.setMaximum(300)
        self.spinTimeLimit.setValue(30)
        self.spinTimeLimit.setSuffix(" s")
        param_form.addRow("Limite de temps:", self.spinTimeLimit)

        self.chkUseWeights = QCheckBox("Utiliser les priorités comme poids")
        self.chkUseWeights.setChecked(True)
        param_form.addRow("", self.chkUseWeights)

        param_group.setLayout(param_form)
        params_layout.addWidget(param_group)

        self.tabs.addTab(params_tab, "Paramètres")

        layout.addWidget(self.tabs)

        # Solve button
        self.btnSolveMIS = QPushButton("Trouver l'Ensemble Indépendant Maximum")
        self.btnSolveMIS.setStyleSheet("font-weight: bold; padding: 10px; background-color: #9b59b6; color: white;")
        layout.addWidget(self.btnSolveMIS)

        # Results area
        results_splitter = QSplitter(Qt.Horizontal)

        self.textMISResults = QTextEdit()
        self.textMISResults.setReadOnly(True)
        results_splitter.addWidget(self.textMISResults)

        self.misGraphWidget = QWidget()
        results_splitter.addWidget(self.misGraphWidget)
        results_splitter.setSizes([300, 700])

        layout.addWidget(results_splitter)

        self.setLayout(layout)
