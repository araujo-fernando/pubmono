
class Vertex:
    def __init__(self, id: int, x_coord: float, y_coord: float, max_degree: int):
        self.id = id
        self.x_coord = x_coord
        self.y_coord = y_coord
        self.max_degree = max_degree

    def __eq__(self, other) -> bool:
        return self.id == other.id

    def __repr__(self) -> str:
        return f"{self.id}"
    
    def __str__(self) -> str:
        return f"Vertex {self.id} ({self.x_coord}, {self.y_coord})"
    
    def __hash__(self) -> int:
        return hash(self.id)
