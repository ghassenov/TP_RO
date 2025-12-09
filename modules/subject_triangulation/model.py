"""
MINIMAL MODEL for triangle decomposition
"""

from dataclasses import dataclass
from typing import List, Tuple


@dataclass
class Point:
    """Simple 2D point"""
    id: int
    x: float
    y: float

    def to_dict(self):
        return {'id': self.id, 'x': self.x, 'y': self.y}

@dataclass
class Triangle:
    """Simple triangle"""
    vertices: Tuple[int, int, int]
    cost: float = 1.0

    def to_dict(self):
        return {
            'vertices': self.vertices,
            'cost': self.cost
        }

class TrussStructure:
    """Minimal structure container"""

    def __init__(self):
        self.points: List[Point] = []
        self.triangles: List[Triangle] = []
        self.selected_triangles: List[Triangle] = []

        # Simple parameters
        self.min_triangles = 1
        self.max_triangles = 10
        self.budget = 1000.0

    def add_point(self, x: float, y: float):
        """Add a point"""
        point = Point(id=len(self.points), x=x, y=y)
        self.points.append(point)
        return point

    def add_triangle(self, vertices: Tuple[int, int, int], cost: float = 1.0):
        """Add a triangle"""
        triangle = Triangle(vertices=vertices, cost=cost)
        self.triangles.append(triangle)
        return triangle
