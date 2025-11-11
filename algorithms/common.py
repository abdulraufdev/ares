"""Common utilities for pathfinding algorithms."""

def manhattan(a: tuple[int, int], b: tuple[int, int]) -> float:
    """Calculate Manhattan distance between two points."""
    return abs(a[0] - b[0]) + abs(a[1] - b[1])

def euclidean(a: tuple[int, int], b: tuple[int, int]) -> float:
    """Calculate Euclidean distance between two points."""
    return ((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2) ** 0.5

def octile(a: tuple[int, int], b: tuple[int, int]) -> float:
    """Calculate Octile distance (for 8-way movement)."""
    dx = abs(a[0] - b[0])
    dy = abs(a[1] - b[1])
    return max(dx, dy) + 0.414 * min(dx, dy)

def get_heuristic(name: str):
    """Get heuristic function by name."""
    heuristics = {
        'manhattan': manhattan,
        'euclidean': euclidean,
        'octile': octile
    }
    return heuristics.get(name.lower(), manhattan)