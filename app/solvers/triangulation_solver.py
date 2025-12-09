"""
App solver wrapper (optional)
"""

from modules.subject_triangulation.solver import SimpleTriangulationSolver


class AppTriangulationSolver:
    def __init__(self, model):
        self.model = model

    def solve(self):
        solver = SimpleTriangulationSolver(self.model.structure)
        return solver.solve_with_gurobi()
