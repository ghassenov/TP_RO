from .model import TrussStructure


def create_simple_example():
    """Create a simple working example"""
    structure = TrussStructure()

    # Add points (a simple triangle)
    structure.add_point(0, 0)
    structure.add_point(2, 0)
    structure.add_point(1, 2)
    structure.add_point(1, 1)  # Center point

    # Add some triangles
    structure.add_triangle((0, 1, 2), cost=2.0)
    structure.add_triangle((0, 1, 3), cost=1.0)
    structure.add_triangle((1, 2, 3), cost=1.5)
    structure.add_triangle((0, 2, 3), cost=1.5)

    # Set parameters
    structure.min_triangles = 1
    structure.max_triangles = 3
    structure.budget = 4.0

    return structure
