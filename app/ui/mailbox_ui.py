from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (QDoubleSpinBox, QFormLayout, QFrame,
                               QGridLayout, QGroupBox, QHBoxLayout, QLabel,
                               QPushButton, QSpinBox, QSplitter, QTableWidget,
                               QTextEdit, QVBoxLayout, QWidget)


class MailboxUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setup_ui()

    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(15, 15, 15, 15)

        # Header
        header = QLabel("📮 Mailbox Location Optimization")
        header.setProperty("title", "true")
        header.setAlignment(Qt.AlignCenter)
        header.setStyleSheet("""
            QLabel {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #e74c3c, stop:0.5 #c0392b, stop:1 #e74c3c);
                color: white;
                font-size: 18pt;
                font-weight: bold;
                padding: 15px;
                border-radius: 10px;
                margin-bottom: 10px;
            }
        """)
        main_layout.addWidget(header)

        # Splitter
        splitter = QSplitter(Qt.Horizontal)

        # LEFT PANEL - Inputs
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setSpacing(10)

        # Parameters Card
        param_card = QGroupBox("⚙️ Optimization Parameters")
        param_card.setStyleSheet("""
            QGroupBox {
                background-color: white;
                border: 2px solid #e74c3c;
            }
        """)
        param_layout = QFormLayout()
        param_layout.setVerticalSpacing(10)

        self.spinMailboxes = self.create_styled_spinbox(1, 999, 3)
        param_layout.addRow("📦 Number of Mailboxes:", self.spinMailboxes)

        self.spinRadius = self.create_styled_doublespinbox(0.1, 9999.0, 2.0)
        param_layout.addRow("🎯 Coverage Radius:", self.spinRadius)

        self.spinBudget = self.create_styled_doublespinbox(0.0, 1000000.0, 1000.0)
        self.spinBudget.setPrefix("€ ")
        param_layout.addRow("💰 Budget:", self.spinBudget)

        self.spinCoverageLevel = self.create_styled_spinbox(1, 10, 1)
        param_layout.addRow("📊 Max Coverage Level:", self.spinCoverageLevel)

        param_card.setLayout(param_layout)
        left_layout.addWidget(param_card)

        # Tables Card
        tables_card = QGroupBox("📋 Input Data")
        tables_card.setStyleSheet("""
            QGroupBox {
                background-color: white;
                border: 2px solid #e74c3c;
            }
        """)
        tables_layout = QVBoxLayout()

        # Demand Points
        demand_label = QLabel("📍 Demand Points")
        demand_label.setStyleSheet("font-weight: bold; color: #2c3e50; font-size: 11pt;")
        tables_layout.addWidget(demand_label)

        self.tableDemand = QTableWidget()
        self.tableDemand.setColumnCount(5)
        self.tableDemand.setHorizontalHeaderLabels(["X", "Y", "Population", "Demand", "Priority"])
        self.tableDemand.horizontalHeader().setStretchLastSection(True)
        self.tableDemand.setMinimumHeight(150)
        tables_layout.addWidget(self.tableDemand)

        # Mailbox Parameters
        mailbox_label = QLabel("📦 Mailbox Parameters")
        mailbox_label.setStyleSheet("font-weight: bold; color: #2c3e50; font-size: 11pt;")
        tables_layout.addWidget(mailbox_label)

        self.tableMailboxParams = QTableWidget()
        self.tableMailboxParams.setColumnCount(3)
        self.tableMailboxParams.setHorizontalHeaderLabels(["Cost", "Capacity", "Fixed Cost"])
        self.tableMailboxParams.setMinimumHeight(100)
        tables_layout.addWidget(self.tableMailboxParams)

        tables_card.setLayout(tables_layout)
        left_layout.addWidget(tables_card)

        # Buttons
        button_layout = QHBoxLayout()

        self.btnAddDemand = QPushButton("➕ Add Demand Point")
        self.btnAddDemand.setProperty("class", "action")

        self.btnAddMailboxParams = QPushButton("⚙️ Add Mailbox Row")
        self.btnAddMailboxParams.setProperty("class", "action")

        button_layout.addWidget(self.btnAddDemand)
        button_layout.addWidget(self.btnAddMailboxParams)
        left_layout.addLayout(button_layout)

        self.btnSolveMailbox = QPushButton("🚀 Optimize Mailbox Location")
        self.btnSolveMailbox.setProperty("special", "true")
        self.btnSolveMailbox.setMinimumHeight(40)
        left_layout.addWidget(self.btnSolveMailbox)

        # Status
        self.lblMailboxStatus = QLabel("✅ Status: Ready")
        self.lblMailboxStatus.setStyleSheet("""
            QLabel {
                background-color: #2ecc71;
                color: white;
                padding: 8px;
                border-radius: 5px;
                font-weight: bold;
            }
        """)
        left_layout.addWidget(self.lblMailboxStatus)

        left_layout.addStretch()

        # RIGHT PANEL - Results
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setSpacing(10)

        results_header = QLabel("📊 Results & Visualization")
        results_header.setStyleSheet("""
            QLabel {
                font-size: 14pt;
                font-weight: bold;
                color: #2c3e50;
                padding: 10px;
                background-color: #f8f9fa;
                border-radius: 6px;
                border-left: 5px solid #e74c3c;
            }
        """)
        right_layout.addWidget(results_header)

        self.textMailboxResults = QTextEdit()
        self.textMailboxResults.setReadOnly(True)
        self.textMailboxResults.setMinimumHeight(200)
        self.textMailboxResults.setStyleSheet("""
            QTextEdit {
                background-color: #f8f9fa;
                border: 2px solid #ddd;
                border-radius: 6px;
                font-family: 'Consolas', monospace;
                padding: 10px;
            }
        """)
        right_layout.addWidget(self.textMailboxResults)

        # Visualization area
        viz_label = QLabel("🗺️ Solution Visualization")
        viz_label.setStyleSheet("font-weight: bold; color: #2c3e50; margin-top: 10px;")
        right_layout.addWidget(viz_label)

        self.mailboxGraphWidget = QWidget()
        self.mailboxGraphWidget.setMinimumHeight(400)
        self.mailboxGraphWidget.setStyleSheet("""
            QWidget {
                background-color: white;
                border: 2px solid #ddd;
                border-radius: 8px;
            }
        """)
        right_layout.addWidget(self.mailboxGraphWidget)

        right_layout.addStretch()

        # Add widgets to splitter
        splitter.addWidget(left_widget)
        splitter.addWidget(right_widget)
        splitter.setSizes([400, 600])
        splitter.setStyleSheet("""
            QSplitter::handle {
                background-color: #e74c3c;
                width: 3px;
            }
        """)

        main_layout.addWidget(splitter)

    def create_styled_spinbox(self, min_val, max_val, default):
        spinbox = QSpinBox()
        spinbox.setRange(min_val, max_val)
        spinbox.setValue(default)
        spinbox.setStyleSheet("""
            QSpinBox {
                padding: 6px;
                border: 2px solid #bdc3c7;
                border-radius: 4px;
                background-color: white;
            }
            QSpinBox:hover {
                border-color: #e74c3c;
            }
            QSpinBox::up-button, QSpinBox::down-button {
                width: 20px;
                border: 1px solid #bdc3c7;
                background-color: #f8f9fa;
            }
            QSpinBox::up-button:hover, QSpinBox::down-button:hover {
                background-color: #e74c3c;
            }
        """)
        return spinbox

    def create_styled_doublespinbox(self, min_val, max_val, default):
        spinbox = QDoubleSpinBox()
        spinbox.setRange(min_val, max_val)
        spinbox.setValue(default)
        spinbox.setStyleSheet("""
            QDoubleSpinBox {
                padding: 6px;
                border: 2px solid #bdc3c7;
                border-radius: 4px;
                background-color: white;
            }
            QDoubleSpinBox:hover {
                border-color: #e74c3c;
            }
            QDoubleSpinBox::up-button, QDoubleSpinBox::down-button {
                width: 20px;
                border: 1px solid #bdc3c7;
                background-color: #f8f9fa;
            }
            QDoubleSpinBox::up-button:hover, QDoubleSpinBox::down-button:hover {
                background-color: #e74c3c;
            }
        """)
        return spinbox
