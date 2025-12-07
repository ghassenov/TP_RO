from PySide6.QtCore import Qt
from PySide6.QtWidgets import (QDoubleSpinBox, QFormLayout, QGroupBox, QLabel,
                               QPushButton, QSpinBox, QSplitter, QTableWidget,
                               QTextEdit, QVBoxLayout, QWidget)


class MailboxUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        splitter = QSplitter(Qt.Horizontal)

        # Left panel
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)

        # Parameters
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

        # Tables
        left_layout.addWidget(QLabel("Demand Points (x, y, population, demand, priority):"))
        self.tableDemand = QTableWidget()
        self.tableDemand.setColumnCount(5)
        self.tableDemand.setHorizontalHeaderLabels(["X", "Y", "Population", "Demand", "Priority"])
        left_layout.addWidget(self.tableDemand)

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

        splitter.addWidget(left_widget)
        splitter.addWidget(right_widget)
        splitter.setSizes([400, 600])

        layout.addWidget(splitter)
        self.setLayout(layout)
