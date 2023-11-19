import sys

class RecursionLimiter:
    def __init__(self, depth: int) -> None:
        if depth <= 0:
            raise ValueError("depth must be a positive integer")
        
        self.depth = depth

    def __enter__(self):
        self.old_limit = sys.getrecursionlimit()
        sys.setrecursionlimit(self.depth)

    def __exit__(self, exc_type, exc_value, traceback): 
        sys.setrecursionlimit(self.old_limit)
