"""
UI for Triangle Decomposition / Truss Structure Optimization
Clean layout with both tables together
"""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (QCheckBox, QComboBox, QDoubleSpinBox,
                               QFormLayout, QFrame, QGridLayout, QGroupBox,
                               QHBoxLayout, QLabel, QLineEdit, QPushButton,
                               QSpinBox, QSplitter, QTableWidget,
                               QTableWidgetItem, QTextEdit, QVBoxLayout,
                               QWidget)


class TriangulationUI(QWidget):
    """UI for triangle decomposition module - Clean layout"""

    def __init__(self):
        super().__init__()
        self.setup_ui()

    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(15, 15, 15, 15)

        # Header - matches other tabs
        header = QLabel("🔺 Triangle Decomposition / Truss Design")
        header.setProperty("title", "true")
        header.setAlignment(Qt.AlignCenter)
        header.setStyleSheet("""
            QLabel {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #1abc9c, stop:0.5 #16a085, stop:1 #1abc9c);
                color: white;
                font-size: 18pt;
                font-weight: bold;
                padding: 15px;
                border-radius: 10px;
                margin-bottom: 10px;
            }
        """)
        main_layout.addWidget(header)

        # Splitter - like other tabs
        splitter = QSplitter(Qt.Horizontal)

        # LEFT PANEL - Inputs
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setSpacing(10)

        # Data Input Card - Contains BOTH tables
        data_card = QGroupBox("📋 Input Data")
        data_card.setStyleSheet("""
            QGroupBox {
                background-color: white;
                border: 2px solid #1abc9c;
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

        # Create a grid layout for the card
        data_layout = QGridLayout(data_card)
        data_layout.setContentsMargins(15, 20, 15, 15)
        data_layout.setVerticalSpacing(10)

        # Points table
        points_header = QLabel("📍 Points (Nodes):")
        points_header.setStyleSheet("font-weight: bold; color: #2c3e50; font-size: 10pt;")
        data_layout.addWidget(points_header, 0, 0, 1, 2)

        self.tablePoints = QTableWidget()
        self.tablePoints.setColumnCount(3)
        self.tablePoints.setHorizontalHeaderLabels(["ID", "X", "Y"])
        self.tablePoints.horizontalHeader().setStretchLastSection(True)
        self.tablePoints.setMinimumHeight(150)
        self.tablePoints.setStyleSheet("""
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
                background-color: #1abc9c;
                color: white;
                padding: 6px;
                font-weight: bold;
                border: none;
            }
        """)
        data_layout.addWidget(self.tablePoints, 1, 0, 1, 2)

        # Triangles table (right of points table)
        triangles_header = QLabel("🔺 Candidate Triangles:")
        triangles_header.setStyleSheet("font-weight: bold; color: #2c3e50; font-size: 10pt;")
        data_layout.addWidget(triangles_header, 0, 2, 1, 2)

        self.tableTriangles = QTableWidget()
        self.tableTriangles.setColumnCount(4)
        self.tableTriangles.setHorizontalHeaderLabels(["P1", "P2", "P3", "Cost"])
        self.tableTriangles.horizontalHeader().setStretchLastSection(True)
        self.tableTriangles.setMinimumHeight(150)
        self.tableTriangles.setStyleSheet("""
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
                background-color: #1abc9c;
                color: white;
                padding: 6px;
                font-weight: bold;
                border: none;
            }
        """)
        data_layout.addWidget(self.tableTriangles, 1, 2, 1, 2)

        # Set column stretch so tables take equal width
        data_layout.setColumnStretch(0, 1)
        data_layout.setColumnStretch(1, 1)
        data_layout.setColumnStretch(2, 1)
        data_layout.setColumnStretch(3, 1)

        left_layout.addWidget(data_card)

        # Parameters Card - styled like other tabs
        param_card = QGroupBox("⚙️ Optimization Parameters")
        param_card.setStyleSheet("""
            QGroupBox {
                background-color: white;
                border: 2px solid #1abc9c;
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
        param_layout = QFormLayout(param_card)
        param_layout.setVerticalSpacing(10)
        param_layout.setContentsMargins(15, 20, 15, 15)

        # Min triangles
        self.spinMinTriangles = QSpinBox()
        self.spinMinTriangles.setRange(1, 100)
        self.spinMinTriangles.setValue(1)
        self.spinMinTriangles.setStyleSheet(self._get_spinbox_style())
        param_layout.addRow("🔺 Min Triangles:", self.spinMinTriangles)

        # Max triangles
        self.spinMaxTriangles = QSpinBox()
        self.spinMaxTriangles.setRange(1, 200)
        self.spinMaxTriangles.setValue(10)
        self.spinMaxTriangles.setStyleSheet(self._get_spinbox_style())
        param_layout.addRow("🔺 Max Triangles:", self.spinMaxTriangles)

        # Max edge length
        self.spinMaxEdgeLength = QDoubleSpinBox()
        self.spinMaxEdgeLength.setRange(0.1, 100.0)
        self.spinMaxEdgeLength.setValue(5.0)
        self.spinMaxEdgeLength.setSuffix(" m")
        self.spinMaxEdgeLength.setStyleSheet(self._get_doublespinbox_style())
        param_layout.addRow("📏 Max Edge Length:", self.spinMaxEdgeLength)

        # Min angle
        self.spinMinAngle = QDoubleSpinBox()
        self.spinMinAngle.setRange(10.0, 60.0)
        self.spinMinAngle.setValue(20.0)
        self.spinMinAngle.setSuffix(" °")
        self.spinMinAngle.setStyleSheet(self._get_doublespinbox_style())
        param_layout.addRow("📐 Min Angle:", self.spinMinAngle)

        # Budget
        self.spinBudget = QDoubleSpinBox()
        self.spinBudget.setRange(0.0, 1000000.0)
        self.spinBudget.setValue(1000.0)
        self.spinBudget.setPrefix("€ ")
        self.spinBudget.setStyleSheet(self._get_doublespinbox_style())
        param_layout.addRow("💰 Budget:", self.spinBudget)

        # Objective function
        self.comboObjective = QComboBox()
        self.comboObjective.addItems([
            "Minimize Total Cost",
            "Minimize Number of Triangles",
            "Maximize Coverage"
        ])
        self.comboObjective.setStyleSheet(self._get_combobox_style())
        param_layout.addRow("🎯 Objective:", self.comboObjective)

        left_layout.addWidget(param_card)

        # Status label (like MailboxUI)
        self.lblStatus = QLabel("✅ Status: Ready")
        self.lblStatus.setStyleSheet("""
            QLabel {
                background-color: #2ecc71;
                color: white;
                padding: 8px;
                border-radius: 5px;
                font-weight: bold;
                margin-top: 10px;
            }
        """)
        left_layout.addWidget(self.lblStatus)

        # Main Solve Button
        self.btnSolve = QPushButton("🚀 Optimize Triangle Decomposition")
        self.btnSolve.setProperty("special", "true")
        self.btnSolve.setMinimumHeight(40)
        left_layout.addWidget(self.btnSolve)

        # Action buttons below the optimize button
        action_buttons_layout = QHBoxLayout()

        self.btnAddPoint = QPushButton("➕ Add Point")
        self.btnAddPoint.setProperty("class", "action")
        self.btnAddPoint.setMinimumHeight(35)

        self.btnAddTriangle = QPushButton("🔺 Add Triangle")
        self.btnAddTriangle.setProperty("class", "action")
        self.btnAddTriangle.setMinimumHeight(35)

        action_buttons_layout.addWidget(self.btnAddPoint)
        action_buttons_layout.addWidget(self.btnAddTriangle)

        left_layout.addLayout(action_buttons_layout)

        left_layout.addStretch()

        # RIGHT PANEL - Results
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setSpacing(10)

        # Results header - matches style
        results_header = QLabel("📊 Results & Visualization")
        results_header.setStyleSheet("""
            QLabel {
                font-size: 14pt;
                font-weight: bold;
                color: #2c3e50;
                padding: 10px;
                background-color: #f8f9fa;
                border-radius: 6px;
                border-left: 5px solid #1abc9c;
            }
        """)
        right_layout.addWidget(results_header)

        # Results text area
        self.textResults = QTextEdit()
        self.textResults.setReadOnly(True)
        self.textResults.setMinimumHeight(250)
        self.textResults.setStyleSheet("""
            QTextEdit {
                background-color: #f8f9fa;
                border: 2px solid #ddd;
                border-radius: 6px;
                font-family: 'Consolas', monospace;
                padding: 10px;
                font-size: 10pt;
            }
        """)
        right_layout.addWidget(self.textResults)

        # Visualization area
        viz_header = QLabel("🗺️ Truss Structure Visualization")
        viz_header.setStyleSheet("font-weight: bold; color: #2c3e50; margin-top: 10px; font-size: 11pt;")
        right_layout.addWidget(viz_header)

        # Graph widget container
        self.graphContainer = QFrame()
        self.graphContainer.setFrameStyle(QFrame.StyledPanel | QFrame.Raised)
        self.graphContainer.setMinimumHeight(400)
        self.graphContainer.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 2px solid #ddd;
                border-radius: 8px;
                padding: 5px;
            }
        """)

        # Layout for graph widget
        graph_layout = QVBoxLayout(self.graphContainer)
        self.graphWidget = QWidget()
        self.graphWidget.setStyleSheet("background-color: white;")
        graph_layout.addWidget(self.graphWidget)

        right_layout.addWidget(self.graphContainer)

        right_layout.addStretch()

        # Add widgets to splitter
        splitter.addWidget(left_widget)
        splitter.addWidget(right_widget)
        splitter.setSizes([450, 550])
        splitter.setStyleSheet("""
            QSplitter::handle {
                background-color: #1abc9c;
                width: 3px;
            }
            QSplitter::handle:hover {
                background-color: #16a085;
            }
        """)

        main_layout.addWidget(splitter)

        # Load example data
        self._load_example_data()

    def _get_spinbox_style(self):
        """Return consistent spinbox style"""
        return """
            QSpinBox {
                padding: 8px;
                border: 2px solid #bdc3c7;
                border-radius: 4px;
                background-color: white;
                font-family: 'Consolas', monospace;
            }
            QSpinBox:hover {
                border-color: #1abc9c;
            }
            QSpinBox:focus {
                border-color: #16a085;
                background-color: #f8f9fa;
            }
            QSpinBox::up-button, QSpinBox::down-button {
                width: 20px;
                border: 1px solid #bdc3c7;
                background-color: #f8f9fa;
                border-radius: 2px;
            }
            QSpinBox::up-button:hover, QSpinBox::down-button:hover {
                background-color: #1abc9c;
                border-color: #16a085;
            }
        """

    def _get_doublespinbox_style(self):
        """Return consistent double spinbox style"""
        return """
            QDoubleSpinBox {
                padding: 8px;
                border: 2px solid #bdc3c7;
                border-radius: 4px;
                background-color: white;
                font-family: 'Consolas', monospace;
            }
            QDoubleSpinBox:hover {
                border-color: #1abc9c;
            }
            QDoubleSpinBox:focus {
                border-color: #16a085;
                background-color: #f8f9fa;
            }
            QDoubleSpinBox::up-button, QDoubleSpinBox::down-button {
                width: 20px;
                border: 1px solid #bdc3c7;
                background-color: #f8f9fa;
                border-radius: 2px;
            }
            QDoubleSpinBox::up-button:hover, QDoubleSpinBox::down-button:hover {
                background-color: #1abc9c;
                border-color: #16a085;
            }
        """

    def _get_combobox_style(self):
        """Return consistent combobox style"""
        return """
            QComboBox {
                padding: 8px;
                border: 2px solid #bdc3c7;
                border-radius: 4px;
                background-color: white;
                font-family: 'Consolas', monospace;
                min-height: 30px;
            }
            QComboBox:hover {
                border-color: #1abc9c;
            }
            QComboBox:focus {
                border-color: #16a085;
                background-color: #f8f9fa;
            }
            QComboBox::drop-down {
                border: none;
                width: 30px;
            }
            QComboBox::down-arrow {
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid #2c3e50;
                width: 0;
                height: 0;
                margin-right: 10px;
            }
            QComboBox QAbstractItemView {
                border: 2px solid #1abc9c;
                border-radius: 4px;
                background-color: white;
                selection-background-color: #1abc9c;
                selection-color: white;
            }
        """

    def _load_example_data(self):
        """Load example data into tables"""
        try:
            # Example points
            example_points = [
                (0, 0),
                (2, 0),
                (0, 2),
                (2, 2),
                (1, 1)
            ]

            self.tablePoints.setRowCount(len(example_points))
            for i, (x, y) in enumerate(example_points):
                self.tablePoints.setItem(i, 0, QTableWidgetItem(str(i)))
                self.tablePoints.setItem(i, 1, QTableWidgetItem(str(x)))
                self.tablePoints.setItem(i, 2, QTableWidgetItem(str(y)))

            # Example triangles
            example_triangles = [
                (0, 1, 2, 2.0),
                (1, 2, 3, 2.0),
                (0, 2, 4, 1.0),
                (1, 3, 4, 1.5)
            ]

            self.tableTriangles.setRowCount(len(example_triangles))
            for i, (p1, p2, p3, cost) in enumerate(example_triangles):
                self.tableTriangles.setItem(i, 0, QTableWidgetItem(str(p1)))
                self.tableTriangles.setItem(i, 1, QTableWidgetItem(str(p2)))
                self.tableTriangles.setItem(i, 2, QTableWidgetItem(str(p3)))
                self.tableTriangles.setItem(i, 3, QTableWidgetItem(str(cost)))

        except Exception as e:
            print(f"Error loading example data: {e}")

    def update_status(self, message: str, is_error: bool = False):
        """Update status label with color coding"""
        if is_error:
            self.lblStatus.setText(f"❌ Status: {message}")
            self.lblStatus.setStyleSheet("""
                QLabel {
                    background-color: #e74c3c;
                    color: white;
                    padding: 8px;
                    border-radius: 5px;
                    font-weight: bold;
                    margin-top: 10px;
                }
            """)
        else:
            self.lblStatus.setText(f"✅ Status: {message}")
            self.lblStatus.setStyleSheet("""
                QLabel {
                    background-color: #2ecc71;
                    color: white;
                    padding: 8px;
                    border-radius: 5px;
                    font-weight: bold;
                    margin-top: 10px;
                }
            """)
