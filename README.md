# TP_RO

## Overview
TP_RO is a Python-based application designed for solving optimization problems in various domains, including triangle decomposition, truss structure optimization, and more. The project leverages PySide6 for its graphical user interface (GUI) and integrates optimization solvers like Gurobi for mathematical modeling and computation.

## Features
- **Triangle Decomposition / Truss Design**: Optimize triangle-based structures with customizable parameters.
- **Truss Physical Optimizer**: Solve truss topology problems with physics-based constraints (equilibrium, stress, and connectivity).
- **Modular Design**: Organized into modules for models, solvers, and UI components.
- **Visualization**: Interactive visualization of results and structures.
- **Example Data**: Preloaded example datasets for quick testing.

## Project Structure
```
TP_RO/
├── app/
│   ├── __init__.py
│   ├── main.py          # Entry point for the application
│   ├── styles.py        # Global styles for the application
│   ├── theme.py         # Theme configurations
│   ├── models/          # Data models for various optimization problems
│   ├── solvers/         # Solver implementations for optimization problems
│   ├── ui/              # User interface components
│   └── __pycache__/     # Compiled Python files
├── modules/
│   ├── subject_antenna_placement/  # Antenna placement optimization
│   ├── subject_mailbox_location/   # Mailbox location optimization
│   ├── subject_mis_scheduling/     # MIS scheduling optimization
│   ├── subject_telecom_network/    # Telecom network optimization
│   ├── subject_triangulation/      # Triangulation optimization
│   └── __pycache__/                # Compiled Python files
├── shared/
│   ├── gurobi_utils.py   # Utilities for Gurobi solver
│   ├── threading_utils.py
│   ├── validation.py     # Validation utilities
│   ├── visualization.py  # Visualization utilities
│   └── __pycache__/      # Compiled Python files
├── test/                 # Test cases
├── requirements.txt      # Python dependencies
├── README.md             # Project documentation (this file)
└── LICENSE               # License information
```

## Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/ghassenov/TP_RO.git
   cd TP_RO
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Ensure Gurobi is installed and licensed if you plan to use the optimization solvers.

## Usage
Run the application:
```bash
python app/main.py
```

### Key Modules
- **UI Components**: Located in `app/ui/`, these define the graphical interface for interacting with the optimization problems.
- **Solvers**: Found in `app/solvers/`, these implement the logic for solving optimization problems.
- **Models**: Located in `app/models/`, these define the data structures used in the application.
- **Shared Utilities**: Common utilities for threading, validation, and visualization are in `shared/`.

### Example Data
Example datasets are provided in the `modules/` subdirectories for quick testing and demonstration purposes.

## Dependencies
- Python 3.10+
- PySide6
- Gurobi (optional, for optimization solvers)
- NumPy
- Matplotlib

## Contributing
Contributions are welcome! Please fork the repository and submit a pull request.

## License
This project is licensed under the MIT License. See the `LICENSE` file for details.
