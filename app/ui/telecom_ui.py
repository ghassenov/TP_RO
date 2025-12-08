from PySide6.QtCore import Qt
from PySide6.QtWidgets import (QDoubleSpinBox, QFormLayout, QFrame,
                               QGridLayout, QGroupBox, QHBoxLayout, QLabel,
                               QLineEdit, QPushButton, QSpinBox, QSplitter,
                               QTableWidget, QTabWidget, QTextEdit,
                               QVBoxLayout, QWidget)


class TelecomUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setup_ui()

    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(15, 15, 15, 15)

        # Header
        header = QLabel("📡 Telecom Network Optimization")
        header.setProperty("title", "true")
        header.setAlignment(Qt.AlignCenter)
        header.setStyleSheet("""
            QLabel {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #3498db, stop:0.5 #2980b9, stop:1 #3498db);
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

        # Network Parameters Card
        param_card = QGroupBox("⚙️ Network Parameters")
        param_card.setStyleSheet("""
            QGroupBox {
                background-color: white;
                border: 2px solid #3498db;
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

        self.txtCapacities = QLineEdit("100,200,500,1000")
        self.txtCapacities.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                border: 2px solid #bdc3c7;
                border-radius: 4px;
                background-color: white;
                font-family: 'Consolas', monospace;
            }
            QLineEdit:hover {
                border-color: #3498db;
            }
            QLineEdit:focus {
                border-color: #2980b9;
                background-color: #f8f9fa;
            }
        """)
        param_layout.addRow("🔗 Capacity Options (Gbps):", self.txtCapacities)

        self.spinTelecomBudget = self.create_styled_doublespinbox(0.0, 10000000.0, 50000.0)
        self.spinTelecomBudget.setPrefix("€ ")
        param_layout.addRow("💰 Network Budget:", self.spinTelecomBudget)

        self.spinFixedCost = self.create_styled_doublespinbox(0.0, 10000.0, 500.0)
        self.spinFixedCost.setPrefix("€/km ")
        param_layout.addRow("🏗️ Fixed Cost Factor:", self.spinFixedCost)

        self.spinVariableCost = self.create_styled_doublespinbox(0.0, 1000.0, 50.0)
        self.spinVariableCost.setPrefix("€/Gbps/km ")
        param_layout.addRow("📈 Variable Cost Factor:", self.spinVariableCost)

        param_card.setLayout(param_layout)
        left_layout.addWidget(param_card)

        # Tabs for data input
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet("""
            QTabWidget::pane {
                border: 2px solid #3498db;
                border-radius: 8px;
                background-color: white;
                margin-top: 5px;
            }
            QTabBar::tab {
                background-color: #ecf0f1;
                padding: 10px 20px;
                margin-right: 2px;
                border-top-left-radius: 5px;
                border-top-right-radius: 5px;
                font-weight: bold;
                color: #2c3e50;
            }
            QTabBar::tab:selected {
                background-color: #3498db;
                color: white;
            }
            QTabBar::tab:hover {
                background-color: #2980b9;
                color: white;
            }
        """)

        # Nodes Tab
        nodes_tab = QWidget()
        nodes_layout = QVBoxLayout(nodes_tab)

        nodes_label = QLabel("📍 Network Nodes")
        nodes_label.setStyleSheet("font-weight: bold; color: #2c3e50; font-size: 11pt; margin-bottom: 5px;")
        nodes_layout.addWidget(nodes_label)

        self.tableNodes = QTableWidget()
        self.tableNodes.setColumnCount(3)
        self.tableNodes.setHorizontalHeaderLabels(["Name", "X", "Y"])
        self.tableNodes.horizontalHeader().setStretchLastSection(True)
        self.tableNodes.setMinimumHeight(150)
        nodes_layout.addWidget(self.tableNodes)

        self.btnAddNode = QPushButton("➕ Add Node")
        self.btnAddNode.setProperty("class", "action")
        self.btnAddNode.setMaximumWidth(150)
        nodes_layout.addWidget(self.btnAddNode, 0, Qt.AlignRight)

        self.tabs.addTab(nodes_tab, "🏢 Nodes")

        # Links Tab
        links_tab = QWidget()
        links_layout = QVBoxLayout(links_tab)

        links_label = QLabel("🔗 Potential Links")
        links_label.setStyleSheet("font-weight: bold; color: #2c3e50; font-size: 11pt; margin-bottom: 5px;")
        links_layout.addWidget(links_label)

        self.tableLinks = QTableWidget()
        self.tableLinks.setColumnCount(3)
        self.tableLinks.setHorizontalHeaderLabels(["From", "To", "Distance"])
        self.tableLinks.horizontalHeader().setStretchLastSection(True)
        self.tableLinks.setMinimumHeight(150)
        links_layout.addWidget(self.tableLinks)

        self.btnAddLink = QPushButton("🔗 Add Link")
        self.btnAddLink.setProperty("class", "action")
        self.btnAddLink.setMaximumWidth(150)
        links_layout.addWidget(self.btnAddLink, 0, Qt.AlignRight)

        self.tabs.addTab(links_tab, "🔌 Links")

        # Demands Tab
        demands_tab = QWidget()
        demands_layout = QVBoxLayout(demands_tab)

        demands_label = QLabel("📊 Traffic Demand Matrix")
        demands_label.setStyleSheet("font-weight: bold; color: #2c3e50; font-size: 11pt; margin-bottom: 5px;")
        demands_layout.addWidget(demands_label)

        demand_desc = QLabel("Enter traffic demand between nodes (Gbps)")
        demand_desc.setStyleSheet("color: #7f8c8d; font-size: 10pt; margin-bottom: 10px;")
        demands_layout.addWidget(demand_desc)

        self.tableDemands = QTableWidget()
        demands_layout.addWidget(self.tableDemands)

        self.tabs.addTab(demands_tab, "📈 Demands")

        left_layout.addWidget(self.tabs)

        # Solve Button
        self.btnSolveTelecom = QPushButton("🚀 Optimize Network Design")
        self.btnSolveTelecom.setProperty("special", "true")
        self.btnSolveTelecom.setMinimumHeight(40)
        left_layout.addWidget(self.btnSolveTelecom)

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
                border-left: 5px solid #3498db;
            }
        """)
        right_layout.addWidget(results_header)

        self.textTelecomResults = QTextEdit()
        self.textTelecomResults.setReadOnly(True)
        self.textTelecomResults.setMinimumHeight(250)
        self.textTelecomResults.setStyleSheet("""
            QTextEdit {
                background-color: #f8f9fa;
                border: 2px solid #ddd;
                border-radius: 6px;
                font-family: 'Consolas', monospace;
                padding: 10px;
                font-size: 10pt;
            }
        """)
        right_layout.addWidget(self.textTelecomResults)

        # Visualization area
        viz_label = QLabel("🗺️ Network Visualization")
        viz_label.setStyleSheet("font-weight: bold; color: #2c3e50; margin-top: 10px;")
        right_layout.addWidget(viz_label)

        self.telecomGraphWidget = QWidget()
        self.telecomGraphWidget.setMinimumHeight(400)
        self.telecomGraphWidget.setStyleSheet("""
            QWidget {
                background-color: white;
                border: 2px solid #ddd;
                border-radius: 8px;
            }
        """)
        right_layout.addWidget(self.telecomGraphWidget)

        right_layout.addStretch()

        # Add widgets to splitter
        splitter.addWidget(left_widget)
        splitter.addWidget(right_widget)
        splitter.setSizes([450, 550])
        splitter.setStyleSheet("""
            QSplitter::handle {
                background-color: #3498db;
                width: 3px;
            }
            QSplitter::handle:hover {
                background-color: #2980b9;
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
                border-color: #3498db;
            }
            QSpinBox:focus {
                border-color: #2980b9;
                background-color: #f8f9fa;
            }
            QSpinBox::up-button, QSpinBox::down-button {
                width: 20px;
                border: 1px solid #bdc3c7;
                background-color: #f8f9fa;
                border-radius: 2px;
            }
            QSpinBox::up-button:hover, QSpinBox::down-button:hover {
                background-color: #3498db;
                border-color: #2980b9;
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
                border-color: #3498db;
            }
            QDoubleSpinBox:focus {
                border-color: #2980b9;
                background-color: #f8f9fa;
            }
            QDoubleSpinBox::up-button, QDoubleSpinBox::down-button {
                width: 20px;
                border: 1px solid #bdc3c7;
                background-color: #f8f9fa;
                border-radius: 2px;
            }
            QDoubleSpinBox::up-button:hover, QDoubleSpinBox::down-button:hover {
                background-color: #3498db;
                border-color: #2980b9;
            }
        """)
        return spinbox
