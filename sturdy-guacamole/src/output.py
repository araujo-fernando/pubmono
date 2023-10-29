import networkx as nx
from matplotlib import pyplot as plt
from pprint import pprint

from .data_structures import CVRPInstance, CVRPSolution, MAX_VEHICLE_TRIPS


class Output:
    def __init__(self, instance: CVRPInstance, solution: CVRPSolution) -> None:
        self._instance = instance
        self._solution = solution

    def write(self, path: str) -> None:
        with open(path + "solution.txt", "w") as file:
            file.write(f"{self._solution.objective_value}\n")
            for route in self._solution.routes:
                pprint(route, stream=file)

    def plot_graph(self, path: str):
        """
        Plots the graph of the solution with networkX, the graph is saved in the
        specified path. Positions of the nodes are given by the coordinates of the
        deliveries.
        """
        G = nx.Graph()
        G.add_node(0, pos=(self._instance.depot.x, self._instance.depot.y))
        for node in self._instance.deliveries:
            G.add_node(node.id, pos=(node.coordinates.x, node.coordinates.y))

        for route in self._solution.routes:
            edges = route.edges
            vehicle = route.vehicle
            G.add_edges_from(
                edges,
                label=f"V{vehicle.id//MAX_VEHICLE_TRIPS}T{vehicle.id%MAX_VEHICLE_TRIPS}",
            )

        pos = nx.get_node_attributes(G, "pos")
        nx.draw(G, with_labels=True, pos=pos)
        edge_labels = nx.get_edge_attributes(G, "label")
        nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels)
        plt.savefig(f"{path}solution.png", dpi=300)
