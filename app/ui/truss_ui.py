"""
Truss Physical Optimizer UI and Controller
GUI + MILP truss topology optimizer with physics (equilibrium + stress) + connectivity
Left-click node: toggle support (orange square)
Right-click node: set load node (red circle)
Run -> solver finds areas, forces, and topology (z)
"""
import math
import numpy as np
from itertools import combinations
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                               QLabel, QSpinBox, QDoubleSpinBox, QFileDialog,
                               QSplitter, QGroupBox, QFormLayout, QTextEdit, QFrame)
from PySide6.QtCore import Qt
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

# Try to import Gurobi
try:
    import gurobipy as gp
    from gurobipy import GRB
    GUROBI_AVAILABLE = True
except ImportError as e:
    gp = None
    GRB = None
    GUROBI_AVAILABLE = False
    GurobiImportError = e


# ---------- Geometry utils ----------
def length_and_dir(nodes, edge):
    i, j = edge
    xi, yi = nodes[i]
    xj, yj = nodes[j]
    dx = xj - xi
    dy = yj - yi
    L = math.hypot(dx, dy)
    if L == 0:
        return 0.0, 0.0, 0.0
    return L, dx / L, dy / L


# ---------- Solver ----------
def solve_physical_truss(nodes, edges, supports, load_node, load_vector,
                         rho=7850.0, sigma_allow=250e6,
                         A_min=1e-6, A_max=5e-4,
                         min_bar_ratio=0.02, length_penalty=0.0,
                         time_limit=60, mip_gap=1e-3, verbose=False):
    """
    Physical truss optimization solver
    
    Parameters:
    -----------
    nodes: list of (x,y)
    edges: list of (i,j) candidate edges (undirected, i<j)
    supports: list of bool (True if node is fixed support)
    load_node: index of node with external load
    load_vector: (Fx,Fy) applied at load_node (N)
    
    Returns:
    --------
    dict with areas, forces, z, objective, A_max...
    """
    if gp is None:
        raise RuntimeError(f"Gurobi not available: {GurobiImportError}")

    n_nodes = len(nodes)
    n_edges = len(edges)
    
    # Precompute geometry
    L = [0.0] * n_edges
    dirx = [0.0] * n_edges
    diry = [0.0] * n_edges
    incident = [[] for _ in range(n_nodes)]
    
    for k, e in enumerate(edges):
        Li, dx, dy = length_and_dir(nodes, e)
        L[k] = Li
        dirx[k] = dx
        diry[k] = dy
        i, j = e
        incident[i].append(k)
        incident[j].append(k)

    # Required nodes for connectivity: supports + load_node
    required_nodes = [i for i, s in enumerate(supports) if s]
    if load_node is not None and load_node not in required_nodes:
        required_nodes.append(load_node)
    if len(required_nodes) < 2:
        raise RuntimeError("At least two required nodes (supports + load) needed for connectivity.")

    # Build Gurobi model
    m = gp.Model("physical_truss")
    if not verbose:
        m.setParam('OutputFlag', 0)
    m.setParam('TimeLimit', float(time_limit))
    m.setParam('MIPGap', float(mip_gap))

    # Variables
    A = m.addVars(n_edges, lb=0.0, ub=A_max, name="A")  # cross sectional areas
    F = m.addVars(n_edges, lb=-GRB.INFINITY, ub=GRB.INFINITY, name="F")  # axial forces
    z = m.addVars(n_edges, vtype=GRB.BINARY, name="z")  # topology on/off

    # Flow variables for connectivity
    R = len(required_nodes)
    f = {}
    for k, (i, j) in enumerate(edges):
        f[(i, j)] = m.addVar(lb=0.0, ub=R, name=f"f_{i}_{j}")
        f[(j, i)] = m.addVar(lb=0.0, ub=R, name=f"f_{j}_{i}")
        # flow only if edge active
        m.addConstr(f[(i, j)] <= R * z[k])
        m.addConstr(f[(j, i)] <= R * z[k])

    # Objective: minimize weight + length_penalty * sum(L * z)
    weight = gp.quicksum(rho * A[k] * L[k] for k in range(n_edges))
    length_pen = length_penalty * gp.quicksum(L[k] * z[k] for k in range(n_edges)) if length_penalty > 0 else 0
    m.setObjective(weight + length_pen, GRB.MINIMIZE)

    # Equilibrium constraints
    for ni in range(n_nodes):
        if supports[ni]:
            continue
        sum_x = gp.LinExpr()
        sum_y = gp.LinExpr()
        for k, (i, j) in enumerate(edges):
            dx = dirx[k]
            dy = diry[k]
            if i == ni:
                sum_x += F[k] * dx
            elif j == ni:
                sum_x += -F[k] * dx

            if i == ni:
                sum_y += F[k] * dy
            elif j == ni:
                sum_y += -F[k] * dy

        # External loads
        Fx, Fy = (0.0, 0.0)
        if load_node == ni:
            Fx, Fy = load_vector
        m.addConstr(sum_x == Fx, name=f"eq_x_{ni}")
        m.addConstr(sum_y == Fy, name=f"eq_y_{ni}")

    # Stress constraints
    for k in range(n_edges):
        m.addConstr(F[k] <= sigma_allow * A[k], name=f"stress_pos_{k}")
        m.addConstr(-F[k] <= sigma_allow * A[k], name=f"stress_neg_{k}")
        # Link A <-> z
        m.addConstr(A[k] <= A_max * z[k], name=f"A_up_{k}")
        m.addConstr(A[k] >= A_min * z[k], name=f"A_low_{k}")

    # Ensure each required node has at least one incident active member
    for v in required_nodes:
        if incident[v]:
            m.addConstr(gp.quicksum(z[e] for e in incident[v]) >= 1, name=f"req_conn_{v}")

    # Flow conservation for connectivity
    root = required_nodes[0]
    for v in range(n_nodes):
        inflow = gp.LinExpr()
        outflow = gp.LinExpr()
        
        for (i, j) in edges:
            if j == v:
                inflow += f[(i, j)]
                outflow += f[(j, i)]
            if i == v:
                outflow += f[(i, j)]
                inflow += f[(j, i)]

        if v == root:
            m.addConstr(outflow - inflow == R - 1, name=f"flow_root")
        elif v in required_nodes:
            m.addConstr(inflow - outflow == 1, name=f"flow_req_{v}")
        else:
            m.addConstr(inflow - outflow == 0, name=f"flow_free_{v}")

    # Minimum sparsity constraint
    min_bars = max(1, int(min_bar_ratio * n_edges))
    m.addConstr(gp.quicksum(z[k] for k in range(n_edges)) >= min_bars, name="min_bars")

    # Solve
    m.optimize()

    status = m.Status
    if status not in (GRB.OPTIMAL, GRB.SUBOPTIMAL, GRB.TIME_LIMIT):
        raise RuntimeError(f"Solver status {status}")

    areas = [A[k].X for k in range(n_edges)]
    forces = [F[k].X for k in range(n_edges)]
    zs = [z[k].X for k in range(n_edges)]
    objective = m.ObjVal if m.SolCount > 0 else None

    return {
        'areas': areas,
        'forces': forces,
        'z': zs,
        'objective': objective,
        'status': status,
        'A_max': A_max,
        'model': m
    }


class TrussOptimizerCanvas(FigureCanvas):
    """Matplotlib canvas for truss visualization"""
    
    def __init__(self, parent=None):
        self.fig, self.ax = plt.subplots(figsize=(7, 6))
        super().__init__(self.fig)
        self.setParent(parent)
        self.nodes = []
        self.supports = []
        self.load_node = None
        self.last_solution = []
        self.last_A_max = 5e-4
        
    def clear_plot(self):
        """Clear the plot"""
        self.ax.clear()
        self.draw()
        
    def draw_truss(self, nodes, supports, load_node, last_solution=None, last_A_max=5e-4):
        """Draw the truss structure"""
        self.ax.clear()
        self.nodes = nodes
        self.supports = supports
        self.load_node = load_node
        
        if last_solution:
            self.last_solution = last_solution
            self.last_A_max = last_A_max
        
        # Find max coordinates for setting limits
        max_x = max(x for x, y in self.nodes) if self.nodes else 1
        max_y = max(y for x, y in self.nodes) if self.nodes else 1
        
        # Draw candidate edges (near neighbors)
        for i, j in combinations(range(len(nodes)), 2):
            xi, yi = nodes[i]
            xj, yj = nodes[j]
            di = abs(xi - xj)
            dj = abs(yi - yj)
            if di <= 2.0 and dj <= 2.0:
                self.ax.plot([xi, xj], [yi, yj], color='lightgray', linewidth=0.6, zorder=1)
        
        # Draw active solution
        max_lw = 8.0
        if self.last_solution:
            for (i, j, area, force) in self.last_solution:
                xi, yi = self.nodes[i]
                xj, yj = self.nodes[j]
                lw = max(1.0, (area / self.last_A_max) * max_lw)
                col = 'tab:red' if force > 1e-9 else ('tab:blue' if force < -1e-9 else 'white')
                self.ax.plot([xi, xj], [yi, yj], color=col, alpha=0 if col=="white" else 1, 
                            linewidth=lw, zorder=4)
        
        # Draw nodes
        for idx, (x, y) in enumerate(self.nodes):
            if self.supports[idx]:
                self.ax.scatter([x], [y], marker='s', s=100, color='orange', zorder=5)
            elif self.load_node == idx:
                self.ax.scatter([x], [y], marker='o', s=100, color='red', zorder=6)
                # Draw load arrow
                arrow_len = 0.8
                self.ax.annotate('', xy=(x, y - arrow_len), xytext=(x, y),
                               arrowprops=dict(facecolor='red', edgecolor='red', lw=2, 
                                             arrowstyle='-|>', shrinkA=0, mutation_scale=20),
                               zorder=7)
            else:
                self.ax.scatter([x], [y], marker='o', s=30, color='k', zorder=3)
            self.ax.text(x + 0.05, y + 0.05, str(idx), color='black', fontsize=8)
        
        self.ax.set_aspect('equal', 'box')
        self.ax.set_xlim(-1, max_x + 1)
        self.ax.set_ylim(-1, max_y + 1)
        self.ax.set_xticks([])
        self.ax.set_yticks([])
        self.ax.set_title("Truss Physical Optimizer", fontsize=12, fontweight='bold')
        self.draw()


class TrussOptimizerUI(QWidget):
    """UI for Truss Physical Optimizer"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the user interface with a clean, two-panel layout similar to TriangulationUI."""
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(12)
        main_layout.setContentsMargins(12, 12, 12, 12)

        # Header
        header = QLabel("🦺 Truss Physical Optimizer")
        header.setProperty("title", "true")
        header.setAlignment(Qt.AlignCenter)
        header.setStyleSheet("""
            QLabel {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #1abc9c, stop:0.5 #16a085, stop:1 #1abc9c);
                color: white;
                font-size: 18pt;
                font-weight: bold;
                padding: 12px;
                border-radius: 10px;
                margin-bottom: 8px;
            }
        """)
        main_layout.addWidget(header)

        splitter = QSplitter(Qt.Horizontal)

        # LEFT PANEL - Controls
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setSpacing(10)

        control_card = QGroupBox("⚙️ Controls & Parameters")
        control_card.setStyleSheet("""
            QGroupBox {
                background-color: white;
                border: 2px solid #1abc9c;
                border-radius: 8px;
                font-weight: bold;
                font-size: 11pt;
            }
        """)
        form = QFormLayout(control_card)
        form.setVerticalSpacing(8)
        form.setContentsMargins(12, 14, 12, 12)

        # Grid size
        grid_row = QWidget()
        grid_layout = QHBoxLayout(grid_row)
        grid_layout.setContentsMargins(0, 0, 0, 0)
        self.nx_spin = QSpinBox()
        self.nx_spin.setRange(2, 20)
        self.nx_spin.setValue(8)
        self.ny_spin = QSpinBox()
        self.ny_spin.setRange(2, 20)
        self.ny_spin.setValue(5)
        grid_layout.addWidget(QLabel("W:"))
        grid_layout.addWidget(self.nx_spin)
        grid_layout.addWidget(QLabel("H:"))
        grid_layout.addWidget(self.ny_spin)
        self.generate_btn = QPushButton("Generate Grid")
        self.generate_btn.setMinimumHeight(30)
        grid_layout.addWidget(self.generate_btn)
        form.addRow("🔳 Grid:", grid_row)

        # Load magnitude
        self.load_spin = QDoubleSpinBox()
        self.load_spin.setRange(-1e6, 1e6)
        self.load_spin.setValue(-1000)
        form.addRow("⚖️ Load (N):", self.load_spin)

        # Sigma
        self.sigma_spin = QDoubleSpinBox()
        self.sigma_spin.setRange(1e4, 1e9)
        self.sigma_spin.setValue(250e6)
        form.addRow("📐 Allowable Stress (Pa):", self.sigma_spin)

        # Min bar ratio and length penalty
        misc_row = QWidget()
        misc_layout = QHBoxLayout(misc_row)
        misc_layout.setContentsMargins(0, 0, 0, 0)
        self.min_ratio_spin = QDoubleSpinBox()
        self.min_ratio_spin.setRange(0.0, 1.0)
        self.min_ratio_spin.setValue(0.02)
        self.min_ratio_spin.setSingleStep(0.01)
        self.len_pen_spin = QDoubleSpinBox()
        self.len_pen_spin.setRange(0.0, 10.0)
        self.len_pen_spin.setValue(0.0)
        misc_layout.addWidget(QLabel("Min Ratio:"))
        misc_layout.addWidget(self.min_ratio_spin)
        misc_layout.addWidget(QLabel("Len Pen:"))
        misc_layout.addWidget(self.len_pen_spin)
        form.addRow("🔧 Sparsity/Cost:", misc_row)

        # Area max / time limit
        bottom_row = QWidget()
        bottom_layout = QHBoxLayout(bottom_row)
        bottom_layout.setContentsMargins(0, 0, 0, 0)
        self.A_max_spin = QDoubleSpinBox()
        self.A_max_spin.setRange(1e-7, 1e-2)
        self.A_max_spin.setDecimals(7)
        self.A_max_spin.setValue(5e-4)
        self.time_spin = QSpinBox()
        self.time_spin.setRange(1, 3600)
        self.time_spin.setValue(60)
        bottom_layout.addWidget(QLabel("A_max:"))
        bottom_layout.addWidget(self.A_max_spin)
        bottom_layout.addWidget(QLabel("Time(s):"))
        bottom_layout.addWidget(self.time_spin)
        form.addRow("⏱️ Solver:", bottom_row)

        left_layout.addWidget(control_card)

        # Action buttons
        actions = QHBoxLayout()
        self.solve_btn = QPushButton("Run Optimization")
        self.solve_btn.setProperty("special", "true")
        self.clear_btn = QPushButton("Clear Supports/Load")
        self.export_btn = QPushButton("Export CSV")
        self.export_btn.setEnabled(False)
        actions.addWidget(self.solve_btn)
        actions.addWidget(self.clear_btn)
        actions.addWidget(self.export_btn)
        left_layout.addLayout(actions)

        # Status
        self.status_label = QLabel("✅ Status: Ready")
        self.status_label.setStyleSheet("""
            QLabel { background-color: #2ecc71; color: white; padding: 8px; border-radius: 5px; font-weight: bold; }
        """)
        left_layout.addWidget(self.status_label)

        left_layout.addStretch()

        # RIGHT PANEL - Results + Visualization
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setSpacing(8)

        results_header = QLabel("📊 Results & Visualization")
        results_header.setStyleSheet("""
            QLabel { font-size: 14pt; font-weight: bold; color: #2c3e50; padding: 8px; background-color: #f8f9fa; border-radius: 6px; border-left: 5px solid #1abc9c; }
        """)
        right_layout.addWidget(results_header)

        self.results_text = QTextEdit()
        self.results_text.setReadOnly(True)
        self.results_text.setMinimumHeight(160)
        self.results_text.setStyleSheet("""
            QTextEdit { background-color: #f8f9fa; border: 2px solid #ddd; border-radius: 6px; font-family: 'Consolas', monospace; padding: 8px; }
        """)
        right_layout.addWidget(self.results_text)

        viz_header = QLabel("🗺️ Truss Structure Visualization")
        viz_header.setStyleSheet("font-weight: bold; color: #2c3e50; margin-top: 6px;")
        right_layout.addWidget(viz_header)

        self.graphContainer = QFrame()
        self.graphContainer.setFrameStyle(QFrame.StyledPanel | QFrame.Raised)
        self.graphContainer.setMinimumHeight(420)
        self.graphContainer.setStyleSheet("""
            QFrame { background-color: white; border: 2px solid #ddd; border-radius: 8px; padding: 6px; }
        """)
        graph_layout = QVBoxLayout(self.graphContainer)
        self.canvas = TrussOptimizerCanvas()
        graph_layout.addWidget(self.canvas)
        right_layout.addWidget(self.graphContainer)

        right_layout.addStretch()

        splitter.addWidget(left_widget)
        splitter.addWidget(right_widget)
        splitter.setSizes([420, 580])

        main_layout.addWidget(splitter)


class TrussOptimizerController:
    """Controller for Truss Physical Optimizer"""
    
    def __init__(self, parent_widget):
        self.parent = parent_widget
        self.ui = TrussOptimizerUI()
        
        parent_layout = parent_widget.layout()
        if parent_layout is None:
            parent_widget.setLayout(QVBoxLayout())
            parent_widget.layout().addWidget(self.ui)
        else:
            parent_layout.addWidget(self.ui)
        
        # Initialize data
        self.nodes = []
        self.supports = []
        self.load_node = None
        self.last_solution = []
        self.last_A_max = 5e-4
        
        # Setup connections
        self.setup_connections()
        
        # Generate initial grid
        self.generate_grid()
        
    def setup_connections(self):
        """Setup signal-slot connections"""
        self.ui.generate_btn.clicked.connect(self.generate_grid)
        self.ui.solve_btn.clicked.connect(self.run_optimization)
        self.ui.clear_btn.clicked.connect(self.clear_all)
        self.ui.export_btn.clicked.connect(self.export_csv)
        
        # Connect canvas mouse events
        self.ui.canvas.mpl_connect("button_press_event", self.on_canvas_click)
        
    def generate_grid(self):
        """Generate a grid of nodes"""
        nx = self.ui.nx_spin.value()
        ny = self.ui.ny_spin.value()
        dx = 1.0
        dy = 1.0
        
        self.nodes = []
        for j in range(ny):
            for i in range(nx):
                self.nodes.append((i * dx, j * dy))
        
        self.supports = [False] * len(self.nodes)
        self.load_node = None
        self.last_solution = []
        self.ui.export_btn.setEnabled(False)
        
        self.draw()
        self.update_status(f"Generated {nx}x{ny} grid with {len(self.nodes)} nodes")
        
    def clear_all(self):
        """Clear all supports and load"""
        self.supports = [False] * len(self.nodes)
        self.load_node = None
        self.last_solution = []
        self.ui.export_btn.setEnabled(False)
        self.draw()
        self.update_status("Cleared all supports and load")
        
    def on_canvas_click(self, event):
        """Handle canvas click events"""
        if event.xdata is None or event.ydata is None:
            return
            
        # Find closest node
        p = np.array([event.xdata, event.ydata])
        distances = [np.linalg.norm(p - np.array(n)) for n in self.nodes]
        idx = int(np.argmin(distances))
        
        # Check if click is close enough to a node
        if distances[idx] > 0.4:
            return
            
        # Clear previous solution visualization
        self.last_solution = []
        self.ui.export_btn.setEnabled(False)
        
        if event.button == 1:  # Left click - toggle support
            self.supports[idx] = not self.supports[idx]
            self.draw()
            self.update_status(f"Toggled support at node {idx}")
        elif event.button == 3:  # Right click - set/unset load
            if self.load_node == idx:
                self.load_node = None
                self.update_status("Cleared load node")
            else:
                self.load_node = idx
                self.update_status(f"Set load at node {idx}")
            self.draw()
            
    def draw(self):
        """Draw the current state"""
        self.ui.canvas.draw_truss(self.nodes, self.supports, self.load_node, 
                                 self.last_solution, self.last_A_max)
        
    def run_optimization(self):
        """Run the physical truss optimization"""
        from PySide6.QtWidgets import QMessageBox
        from PySide6.QtWidgets import QApplication
        
        if not GUROBI_AVAILABLE:
            QMessageBox.critical(self.parent, "Gurobi Missing", 
                               f"Gurobi is not available: {GurobiImportError}\n"
                               "Please install Gurobi to use this feature.")
            return
            
        # Check inputs
        supports_count = sum(1 for s in self.supports if s)
        if supports_count < 2:
            QMessageBox.warning(self.parent, "Supports Required", 
                              "Select at least two fixed supports (left-click nodes).")
            return
        if self.load_node is None:
            QMessageBox.warning(self.parent, "Load Required", 
                              "Set a load node (right-click a node).")
            return
            
        # Build candidate edges (near neighbors)
        edges = []
        for i, j in combinations(range(len(self.nodes)), 2):
            xi, yi = self.nodes[i]
            xj, yj = self.nodes[j]
            if abs(xi - xj) <= 2.0 and abs(yi - yj) <= 2.0:
                edges.append((i, j))
                
        if not edges:
            QMessageBox.critical(self.parent, "No Edges", 
                               "No candidate edges found. Try a different grid configuration.")
            return
            
        # Get parameters
        sigma = float(self.ui.sigma_spin.value())
        min_ratio = float(self.ui.min_ratio_spin.value())
        alpha = float(self.ui.len_pen_spin.value())
        tlim = int(self.ui.time_spin.value())
        load_val = float(self.ui.load_spin.value())
        A_max_val = float(self.ui.A_max_spin.value())
        load_vec = (0.0, load_val)  # Vertical load
        
        self.update_status("Solving optimization...")
        QApplication.processEvents()  # Update UI
        
        try:
            result = solve_physical_truss(
                self.nodes, edges, self.supports, self.load_node, load_vec,
                rho=7850.0, sigma_allow=sigma,
                A_min=1e-6, A_max=A_max_val,
                min_bar_ratio=min_ratio, length_penalty=alpha,
                time_limit=tlim, mip_gap=1e-3, verbose=False
            )
        except Exception as e:
            QMessageBox.critical(self.parent, "Solver Error", str(e))
            self.update_status(f"Error: {str(e)}", is_error=True)
            return
            
        # Process results
        areas = result['areas']
        forces = result['forces']
        zs = result['z']
        self.last_A_max = result['A_max']
        self.last_solution = []
        
        active_count = 0
        total_weight = 0.0
        for k, (i, j) in enumerate(edges):
            if zs[k] > 0.5:
                self.last_solution.append((i, j, areas[k], forces[k]))
                Li, _, _ = length_and_dir(self.nodes, (i, j))
                total_weight += 7850.0 * areas[k] * Li
                active_count += 1
                
        # Update UI
        self.ui.export_btn.setEnabled(len(self.last_solution) > 0)
        self.draw()
        
        # Display results
        obj_weight = result['objective'] if result['objective'] is not None else 0.0
        
        results_text = f"""
        <b>OPTIMIZATION RESULTS</b>
        <hr>
        <b>Status:</b> {result['status']}<br>
        <b>Objective Value (Mass Penalty):</b> {obj_weight:.4e}<br>
        <b>Active Bars:</b> {active_count}/{len(edges)}<br>
        <b>Total Mass:</b> {total_weight:.4f} kg (ρ=7850 kg/m³)<br>
        <b>Maximum Area (A_max):</b> {self.last_A_max:.2e} m²<br>
        <br>
        <b>Visualization:</b><br>
        • <span style='color: red'>Red bars</span>: Tension (force > 0)<br>
        • <span style='color: blue'>Blue bars</span>: Compression (force < 0)<br>
        • Bar thickness proportional to cross-sectional area
        """
        
        self.ui.results_text.setText(results_text)
        self.update_status(f"Optimization complete: {active_count} active bars")
        
    def export_csv(self):
        """Export results to CSV"""
        if not self.last_solution:
            return
            
        from PySide6.QtWidgets import QMessageBox
        
        fname, _ = QFileDialog.getSaveFileName(self.parent, "Save CSV", "", "CSV files (*.csv)")
        if not fname:
            return
            
        try:
            with open(fname, 'w') as fh:
                fh.write("node_i,node_j,area_m2,force_N\n")
                for (i, j, area, force) in self.last_solution:
                    fh.write(f"{i},{j},{area},{force}\n")
            self.update_status(f"Exported results to {fname}")
            QMessageBox.information(self.parent, "Export Successful", f"Results saved to {fname}")
        except Exception as e:
            QMessageBox.critical(self.parent, "Export Failed", f"Failed to export: {str(e)}")
            
    def update_status(self, message, is_error=False):
        """Update status message"""
        if is_error:
            self.ui.status_label.setText(f"❌ {message}")
            self.ui.status_label.setStyleSheet("color: #e74c3c; font-weight: bold;")
        else:
            self.ui.status_label.setText(f"✅ {message}")
            self.ui.status_label.setStyleSheet("color: #27ae60;")
