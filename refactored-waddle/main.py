import os

from time import time
from argparse import ArgumentParser
from src import *

ALL_ALGORITHMS = ["kruskal", "prim", "ning_xiong", "custom", "custom2"]

def main(file: str, algorithms: list[str]):
    graph = CompleteUndirectedGraph(create_vertexes_from_file(file))

    print("Graph data")
    print("Total vertexes:", len(graph.V))
    print("Total edges:", len(graph.edges), "\n")
    
    for alg in algorithms:
        start_time = time()
        tree = eval(alg)(graph)
        exec_time = time() - start_time
        print_results(tree, alg, exec_time)

def parse_arguments():
    parser = ArgumentParser()
    parser.add_argument("file", help="File for the graph instance")
    parser.add_argument("-a","--algorithm", help=f"Algorithm to use: {ALL_ALGORITHMS + ['all']}", default="custom")
    return parser

if __name__ == "__main__":
    parser = parse_arguments()
    args = parser.parse_args()

    if not os.path.isdir("logs"):
        os.mkdir("logs")
    if args.algorithm == "all":
        args.algorithm = ALL_ALGORITHMS
    else:
        args.algorithm = [args.algorithm]

    main(args.file, args.algorithm)
