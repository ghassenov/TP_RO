from typing import Dict, List

from .model import Triangle, TrussStructure


class SimpleTriangulationSolver:
    """Minimal working solver"""

    def __init__(self, structure: TrussStructure):
        self.structure = structure

    def solve_greedy(self) -> Dict:
        """Simple greedy algorithm - always works"""
        print("Running greedy solver...")

        if not self.structure.triangles:
            print("No triangles, creating some...")
            self._create_default_triangles()

        # Simple greedy: pick triangles until we cover all points or reach max
        selected = []
        covered_points = set()
        total_cost = 0.0

        # Sort triangles by cost (cheapest first)
        sorted_triangles = sorted(self.structure.triangles, key=lambda t: t.cost)

        for triangle in sorted_triangles:
            if len(selected) >= self.structure.max_triangles:
                break

            if total_cost + triangle.cost > self.structure.budget:
                continue

            # Add triangle
            selected.append(triangle)
            total_cost += triangle.cost

            # Mark points as covered
            i, j, k = triangle.vertices
            covered_points.update([i, j, k])

        # Calculate statistics
        coverage = len(covered_points) / len(self.structure.points) if self.structure.points else 0

        return {
            'status': 'SUCCESS',
            'selected_triangles': selected,
            'num_triangles': len(selected),
            'total_cost': total_cost,
            'covered_points': len(covered_points),
            'total_points': len(self.structure.points),
            'coverage_rate': coverage
        }

    def _create_default_triangles(self):
        """Create simple triangles if none exist"""
        points = self.structure.points
        n = len(points)

        if n < 3:
            print("Need at least 3 points for triangles")
            return

        # Create triangles from first few points
        triangles_to_create = min(5, n * (n-1) * (n-2) // 6)

        count = 0
        for i in range(n):
            for j in range(i+1, n):
                for k in range(j+1, n):
                    if count >= triangles_to_create:
                        return

                    # Simple cost based on triangle "size"
                    cost = 1.0 + (abs(points[i].x - points[j].x) +
                                 abs(points[j].y - points[k].y)) * 0.1

                    self.structure.add_triangle((i, j, k), cost)
                    count += 1

    def solve_with_gurobi(self) -> Dict:
        """Optional Gurobi solver"""
        try:
            import gurobipy as gp
            from gurobipy import GRB

            if not self.structure.triangles:
                self._create_default_triangles()

            n = len(self.structure.triangles)
            if n == 0:
                return {'status': 'ERROR', 'error': 'No triangles'}

            # Create model
            model = gp.Model("Triangulation")
            model.setParam('OutputFlag', 0)

            # Variables
            x = model.addVars(n, vtype=GRB.BINARY, name="x")

            # Objective: minimize cost
            costs = [t.cost for t in self.structure.triangles]
            model.setObjective(gp.quicksum(costs[i] * x[i] for i in range(n)), GRB.MINIMIZE)

            # Cover all points
            point_map = {}
            for i, triangle in enumerate(self.structure.triangles):
                for v in triangle.vertices:
                    if v not in point_map:
                        point_map[v] = []
                    point_map[v].append(i)

            for point_idx, tri_indices in point_map.items():
                model.addConstr(gp.quicksum(x[i] for i in tri_indices) >= 1,
                              f"cover_{point_idx}")

            # Triangle count limit
            model.addConstr(gp.quicksum(x[i] for i in range(n)) <= self.structure.max_triangles,
                          "max_triangles")

            # Budget
            model.addConstr(gp.quicksum(costs[i] * x[i] for i in range(n)) <= self.structure.budget,
                          "budget")

            # Solve
            model.optimize()

            if model.status == GRB.OPTIMAL:
                selected_idx = [i for i in range(n) if x[i].X > 0.5]
                selected = [self.structure.triangles[i] for i in selected_idx]

                covered = set()
                for tri in selected:
                    covered.update(tri.vertices)

                return {
                    'status': 'OPTIMAL',
                    'selected_triangles': selected,
                    'num_triangles': len(selected),
                    'total_cost': model.ObjVal,
                    'covered_points': len(covered),
                    'total_points': len(self.structure.points),
                    'coverage_rate': len(covered) / len(self.structure.points),
                    'method': 'Gurobi'
                }
            else:
                return self.solve_greedy()  # Fallback to greedy

        except ImportError:
            print("Gurobi not available, using greedy solver")
            return self.solve_greedy()
        except Exception as e:
            print(f"Gurobi error: {e}")
            return self.solve_greedy()
