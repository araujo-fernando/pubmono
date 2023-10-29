import os
import logging
from time import time
from typing import Iterable

from .vertex import Vertex

def print_forest(forest: list, logger: logging.Logger | None = None):
    method = logger.info if logger else print
    for edge in forest:
        method(edge)

def create_logger(log_file: str, stdout: bool = True):
    logger = logging.getLogger(f"{time()}")
    logger.setLevel(logging.DEBUG)
    if stdout:
        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)
        logger.addHandler(ch)
    else:
        ch = logging.StreamHandler()
        ch.setLevel(logging.ERROR)
        logger.addHandler(ch)

    if os.path.isfile(log_file):
        os.remove(log_file)

    fh = logging.FileHandler(log_file, mode="w")
    fh.setLevel(logging.INFO)
    logger.addHandler(fh)
    return logger

def print_results(tree, algorithm: str, exec_time: float):
    vertexes_degrees = dict()
    for v in tree.V:
        vertexes_degrees[v] = len(tree.find_vertexes_connected_to_vertex(v))

    logger = create_logger(f"logs/{algorithm}_summary.log")
    logger.info(f"Minimum spanning tree by {algorithm.capitalize()}")
    logger.info(f"Total edges: {len(tree.edges)}")
    logger.info(f"Total weight: {round(sum((w for _, _, w in tree.edges)), 4)}")
    logger.info(f"Max node degree: {max(vertexes_degrees.values())}")
    logger.info(f"Execution time: {round(exec_time, 4)} seconds")
    print("")

    logger = create_logger(f"logs/{algorithm}_tree.log", False)
    print_forest(tree.edges, logger)

    logger = create_logger(f"logs/{algorithm}_vertexes_degrees.log", False)
    print_vertexes_degrees(vertexes_degrees, logger)

    with open("Araujo.csv", "w") as output:
        for edge in tree.edges:
            output.write(f"{edge[0].id},{edge[1].id}\n")

def create_vertexes_from_file(file: str) -> list:
    with open(file, "r") as f:
        lines = f.readlines()
    vertexes = [
        Vertex(int(idx), float(x_coord), float(y_coord), int(g_max))
        for idx, x_coord, y_coord, g_max in [line.split(',') for line in lines]
    ]
    return vertexes

def find_set(sets: list, obj) -> set:
    """
    Find the set that contains the given object

    :param sets: list of sets
    :type sets: list
    :param obj: object to find
    :type obj: any
    :raises ValueError: if the object is not found in any set
    :return: the set that contains the given object
    :rtype: set
    """
    for s in sets:
        if obj in s:
            return s
        
    raise ValueError("Vertex not found in any set")

def compute_distance(v1: Vertex, v2: Vertex):
        return ((v1.x_coord - v2.x_coord)**2 + (v1.y_coord - v2.y_coord)**2)**0.5

def find_closest_vertex(vertexes: Iterable[Vertex], vertex: Vertex) -> Vertex:
    """
    Find the closest vertex to the given vertex

    :param edges: list of edges
    :type edges: list
    :param vertex: vertex to find the closest vertex
    :type vertex: Vertex
    :return: the closest vertex to the given vertex
    :rtype: Vertex
    """
    closest_vertex = None
    closest_distance = float("inf")
    for v in vertexes:
        distance = compute_distance(vertex, v)
        if distance < closest_distance:
            closest_distance = distance
            closest_vertex = v

    if closest_vertex is None:
        raise ValueError("No closest vertex found")

    return closest_vertex

def find_closest_vertex_to_subset(vertexes: Iterable[Vertex], subset: set[Vertex]):
    """
    Find the closest vertex to the given subset of vertexes that is not present in 
    the subset

    :param vertexes: list of vertexes
    :type vertexes: list
    :param subset: subset of vertexes
    :type subset: set
    :return: pair of vertexes, the first one is in the subset and the second one is not
    :rtype: Tuple[Vertex, Vertex]
    """
    closest_vertexes = None
    closest_distance = float("inf")
    for v in vertexes:
        if v not in subset:
            u = find_closest_vertex(subset, v)
            distance = compute_distance(u, v)
            if distance < closest_distance:
                closest_distance = distance
                closest_vertexes = (u, v)

    if closest_vertexes is None:
        raise ValueError("No closest vertex found")

    return closest_vertexes

def print_vertexes_degrees(vertexes_degrees: dict, logger: logging.Logger | None = None):
    vertexes_degrees = {k: v for k, v in sorted(vertexes_degrees.items(), key=lambda item: item[0].id)}

    method = logger.info if logger else print
    for v in vertexes_degrees:
        method(f"{v.id}: {vertexes_degrees[v]}")