from .data_structures import Coordinates


def compute_distance(coordinate_a: Coordinates, coordinate_b: Coordinates) -> float:
    return (
        (coordinate_a.x - coordinate_b.x) ** 2 + (coordinate_a.y - coordinate_b.y) ** 2
    ) ** 0.5
