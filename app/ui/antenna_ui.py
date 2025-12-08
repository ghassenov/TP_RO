from PySide6.QtCore import Qt
from PySide6.QtWidgets import (QCheckBox, QDoubleSpinBox, QFormLayout, QFrame,
                               QGridLayout, QGroupBox, QHBoxLayout, QLabel,
                               QLineEdit, QPushButton, QSpinBox, QSplitter,
                               QTableWidget, QTextEdit, QVBoxLayout, QWidget)


class AntennaUI(QWidget):
    """UI pour le placement d'antennes télécom"""

    def __init__(self):
        super().__init__()
        self.setup_ui()

    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(15, 15, 15, 15)

        # Header
        header = QLabel("📶 Antenna Placement Optimization")
        header.setProperty("title", "true")
        header.setAlignment(Qt.AlignCenter)
        header.setStyleSheet("""
            QLabel {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #9b59b6, stop:0.5 #8e44ad, stop:1 #9b59b6);
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

        # Optimization Parameters Card
        param_card = QGroupBox("⚙️ Optimization Parameters")
        param_card.setStyleSheet("""
            QGroupBox {
                background-color: white;
                border: 2px solid #9b59b6;
                border-radius: 8px;
                font-weight: bold;
                font-size: 11pt;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
        """)
        param_layout = QFormLayout()
        param_layout.setVerticalSpacing(10)
        param_layout.setContentsMargins(15, 20, 15, 15)

        self.spinCoverageRadius = self.create_styled_doublespinbox(0.1, 100.0, 4.0)
        param_layout.addRow("🎯 Coverage Radius:", self.spinCoverageRadius)

        self.spinMaxAntennas = self.create_styled_spinbox(1, 50, 4)
        param_layout.addRow("📡 Max Antennas:", self.spinMaxAntennas)

        self.txtCapacities = QLineEdit("50,100,150,200")
        self.txtCapacities.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                border: 2px solid #bdc3c7;
                border-radius: 4px;
                background-color: white;
                font-family: 'Consolas', monospace;
            }
            QLineEdit:hover {
                border-color: #9b59b6;
            }
            QLineEdit:focus {
                border-color: #8e44ad;
                background-color: #f8f9fa;
            }
        """)
        param_layout.addRow("🔋 Capacity Options:", self.txtCapacities)

        self.spinMinCoverage = QDoubleSpinBox()
        self.spinMinCoverage.setMinimum(0.0)
        self.spinMinCoverage.setMaximum(100.0)
        self.spinMinCoverage.setValue(80.0)
        self.spinMinCoverage.setSuffix("%")
        self.spinMinCoverage.setStyleSheet("""
            QDoubleSpinBox {
                padding: 8px;
                border: 2px solid #bdc3c7;
                border-radius: 4px;
                background-color: white;
                font-family: 'Consolas', monospace;
            }
            QDoubleSpinBox:hover {
                border-color: #9b59b6;
            }
            QDoubleSpinBox:focus {
                border-color: #8e44ad;
                background-color: #f8f9fa;
            }
            QDoubleSpinBox::up-button, QDoubleSpinBox::down-button {
                width: 20px;
                border: 1px solid #bdc3c7;
                background-color: #f8f9fa;
                border-radius: 2px;
            }
            QDoubleSpinBox::up-button:hover, QDoubleSpinBox::down-button:hover {
                background-color: #9b59b6;
                border-color: #8e44ad;
            }
        """)
        param_layout.addRow("📊 Minimum Coverage:", self.spinMinCoverage)

        self.chkCapacityConstraint = QCheckBox("Activer contraintes de capacité")
        self.chkCapacityConstraint.setChecked(True)
        self.chkCapacityConstraint.setStyleSheet("""
            QCheckBox {
                spacing: 8px;
                font-weight: bold;
                color: #2c3e50;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
                border: 2px solid #bdc3c7;
                border-radius: 3px;
                background-color: white;
            }
            QCheckBox::indicator:checked {
                background-color: #9b59b6;
                border-color: #8e44ad;
                image: url(:/icons/check.svg);
            }
            QCheckBox::indicator:hover {
                border-color: #9b59b6;
            }
        """)
        param_layout.addRow("", self.chkCapacityConstraint)

        param_card.setLayout(param_layout)
        left_layout.addWidget(param_card)

        # Data Input Tables in a card
        data_card = QGroupBox("📋 Input Data")
        data_card.setStyleSheet("""
            QGroupBox {
                background-color: white;
                border: 2px solid #9b59b6;
                border-radius: 8px;
                font-weight: bold;
                font-size: 11pt;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
        """)
        data_layout = QVBoxLayout(data_card)
        data_layout.setSpacing(10)
        data_layout.setContentsMargins(15, 20, 15, 15)

        # Users section
        users_label = QLabel("👥 Users")
        users_label.setStyleSheet("font-weight: bold; color: #2c3e50; font-size: 11pt;")
        data_layout.addWidget(users_label)

        self.tableUsers = QTableWidget()
        self.tableUsers.setColumnCount(3)
        self.tableUsers.setHorizontalHeaderLabels(["X", "Y", "Demand"])
        self.tableUsers.horizontalHeader().setStretchLastSection(True)
        self.tableUsers.setMinimumHeight(120)
        self.tableUsers.setStyleSheet("""
            QTableWidget {
                border: 1px solid #ddd;
                border-radius: 4px;
                background-color: white;
                alternate-background-color: #f8f9fa;
            }
            QTableWidget::item {
                padding: 4px;
            }
            QHeaderView::section {
                background-color: #9b59b6;
                color: white;
                padding: 6px;
                font-weight: bold;
                border: none;
            }
        """)
        data_layout.addWidget(self.tableUsers)

        # Sites section
        sites_label = QLabel("🏢 Candidate Sites")
        sites_label.setStyleSheet("font-weight: bold; color: #2c3e50; font-size: 11pt; margin-top: 15px;")
        data_layout.addWidget(sites_label)

        self.tableSites = QTableWidget()
        self.tableSites.setColumnCount(4)
        self.tableSites.setHorizontalHeaderLabels(["Name", "X", "Y", "Setup Cost"])
        self.tableSites.horizontalHeader().setStretchLastSection(True)
        self.tableSites.setMinimumHeight(120)
        self.tableSites.setStyleSheet("""
            QTableWidget {
                border: 1px solid #ddd;
                border-radius: 4px;
                background-color: white;
                alternate-background-color: #f8f9fa;
            }
            QTableWidget::item {
                padding: 4px;
            }
            QHeaderView::section {
                background-color: #9b59b6;
                color: white;
                padding: 6px;
                font-weight: bold;
                border: none;
            }
        """)
        data_layout.addWidget(self.tableSites)

        left_layout.addWidget(data_card)

        # Buttons
        button_layout = QHBoxLayout()

        self.btnAddUser = QPushButton("➕ Add User")
        self.btnAddUser.setProperty("class", "action")

        self.btnAddSite = QPushButton("🏢 Add Site")
        self.btnAddSite.setProperty("class", "action")

        button_layout.addWidget(self.btnAddUser)
        button_layout.addWidget(self.btnAddSite)
        left_layout.addLayout(button_layout)

        self.btnSolveAntenna = QPushButton("🚀 Optimize Antenna Placement")
        self.btnSolveAntenna.setProperty("special", "true")
        self.btnSolveAntenna.setMinimumHeight(40)
        left_layout.addWidget(self.btnSolveAntenna)

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
                border-left: 5px solid #9b59b6;
            }
        """)
        right_layout.addWidget(results_header)

        self.textAntennaResults = QTextEdit()
        self.textAntennaResults.setReadOnly(True)
        self.textAntennaResults.setMinimumHeight(250)
        self.textAntennaResults.setStyleSheet("""
            QTextEdit {
                background-color: #f8f9fa;
                border: 2px solid #ddd;
                border-radius: 6px;
                font-family: 'Consolas', monospace;
                padding: 10px;
                font-size: 10pt;
            }
        """)
        right_layout.addWidget(self.textAntennaResults)

        # Visualization area
        viz_label = QLabel("🗺️ Solution Visualization")
        viz_label.setStyleSheet("font-weight: bold; color: #2c3e50; margin-top: 10px;")
        right_layout.addWidget(viz_label)

        self.antennaGraphWidget = QWidget()
        self.antennaGraphWidget.setMinimumHeight(400)
        self.antennaGraphWidget.setStyleSheet("""
            QWidget {
                background-color: white;
                border: 2px solid #ddd;
                border-radius: 8px;
            }
        """)
        right_layout.addWidget(self.antennaGraphWidget)

        right_layout.addStretch()

        # Add widgets to splitter
        splitter.addWidget(left_widget)
        splitter.addWidget(right_widget)
        splitter.setSizes([450, 550])
        splitter.setStyleSheet("""
            QSplitter::handle {
                background-color: #9b59b6;
                width: 3px;
            }
            QSplitter::handle:hover {
                background-color: #8e44ad;
            }
        """)

        main_layout.addWidget(splitter)

    def create_styled_spinbox(self, min_val, max_val, default):
        spinbox = QSpinBox()
        spinbox.setRange(min_val, max_val)
        spinbox.setValue(default)
        spinbox.setStyleSheet("""
            QSpinBox {
                padding: 8px;
                border: 2px solid #bdc3c7;
                border-radius: 4px;
                background-color: white;
                font-family: 'Consolas', monospace;
            }
            QSpinBox:hover {
                border-color: #9b59b6;
            }
            QSpinBox:focus {
                border-color: #8e44ad;
                background-color: #f8f9fa;
            }
            QSpinBox::up-button, QSpinBox::down-button {
                width: 20px;
                border: 1px solid #bdc3c7;
                background-color: #f8f9fa;
                border-radius: 2px;
            }
            QSpinBox::up-button:hover, QSpinBox::down-button:hover {
                background-color: #9b59b6;
                border-color: #8e44ad;
            }
        """)
        return spinbox

    def create_styled_doublespinbox(self, min_val, max_val, default):
        spinbox = QDoubleSpinBox()
        spinbox.setRange(min_val, max_val)
        spinbox.setValue(default)
        spinbox.setStyleSheet("""
            QDoubleSpinBox {
                padding: 8px;
                border: 2px solid #bdc3c7;
                border-radius: 4px;
                background-color: white;
                font-family: 'Consolas', monospace;
            }
            QDoubleSpinBox:hover {
                border-color: #9b59b6;
            }
            QDoubleSpinBox:focus {
                border-color: #8e44ad;
                background-color: #f8f9fa;
            }
            QDoubleSpinBox::up-button, QDoubleSpinBox::down-button {
                width: 20px;
                border: 1px solid #bdc3c7;
                background-color: #f8f9fa;
                border-radius: 2px;
            }
            QDoubleSpinBox::up-button:hover, QDoubleSpinBox::down-button:hover {
                background-color: #9b59b6;
                border-color: #8e44ad;
            }
        """)
        return spinbox
