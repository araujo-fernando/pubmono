import networkx as nx

from .graphs import CompleteUndirectedGraph, UndirectedGraph, Edge
from .utilities import *


def kruskal(graph: UndirectedGraph):
    f = []
    sets = [{v} for v in graph.V]

    for u, v, w in graph.edges:
        set_u = find_set(sets, u)
        set_v = find_set(sets, v)

        if set_u != set_v:
            f.append([u, v, w])
            sets.remove(set_v)
            sets.remove(set_u)
            sets.append(set_u.union(set_v))

    return UndirectedGraph(graph.V.copy(), [Edge(u, v, w) for u, v, w in f])


def prim(graph: UndirectedGraph):
    f = []
    Q = graph.V.copy()

    u = Q.pop(0)
    v = find_closest_vertex(Q, u)
    f.append([u, v, compute_distance(u, v)])
    selected_vertexes = {u, v}
    Q.remove(v)

    while len(Q) > 0:
        u, v = find_closest_vertex_to_subset(Q, selected_vertexes)
        f.append([u, v, compute_distance(u, v)])
        Q.remove(v)
        selected_vertexes.add(v)

    return UndirectedGraph(graph.V.copy(), [Edge(u, v, w) for u, v, w in f])


def ning_xiong(graph: CompleteUndirectedGraph):
    """
    Implements Aibing Ning and Xiaohua Xiong algorithm for finding a minimum spanning tree of a complete undirected graph
    with degree constraints. The algorithm is described in the paper "A New Algorithm for degree-constrained minimum
    spanning tree problem based on the reduction technique".

    :param graph: graph to find the minimum spanning tree
    :type graph: CompleteUndirectedGraph
    """

    def reduction(graph: UndirectedGraph):
        g = graph.copy()
        t_star = UndirectedGraph(g.V.copy())

        v_1 = [v for v in g.V if v.max_degree == 1]
        e_1 = [e for e in g.edges if (e.u in v_1 and e.v in v_1)]
        if len(g.V) > 2:
            for edge in e_1:
                g.edges.remove(edge)

        degree_one_vertexes = g.find_vertexes_with_degree(1)
        for v in degree_one_vertexes:
            edges = g.find_egdes_of_vertex(v)
            for edge in edges:
                g.edges.remove(edge)
            t_star.edges.extend(edges)
            g.V.remove(v)

        degree_two_vertexes = g.find_vertexes_with_degree(2)
        aux_graph = nx.Graph()
        for edge in g.edges:
            aux_graph.add_edge(edge.u, edge.v)

        for vk in degree_two_vertexes:
            vi, vj = g.find_vertexes_connected_to_vertex(vk)
            paths = list(nx.all_simple_paths(aux_graph, vi, vj))
            if all(vk in path for path in paths):
                edges = g.find_egdes_of_vertex(vk)
                for edge in edges:
                    g.edges.remove(edge)
                t_star.edges.extend(edges)

        return g, t_star

    g = graph.copy()
    g_star = UndirectedGraph(g.V.copy())
    g, t_star = reduction(g)
    e_1 = g.edges.copy()
    total_vertexes = len(g.V)
    while len(g_star.edges) < total_vertexes - 1 and e_1:
        min_cost_edge = min(e_1, key=lambda e: e.w)
        vk = min_cost_edge.u
        vh = min_cost_edge.v

        component_vk = t_star.find_vertexes_connected_to_vertex(vk)
        component_vh = t_star.find_vertexes_connected_to_vertex(vh)

        empty_intersection = len(component_vk & component_vh) == 0
        vk_not_with_max_degree = vk.max_degree > len(component_vk)
        vh_not_with_max_degree = vh.max_degree > len(component_vh)

        if all([empty_intersection, vk_not_with_max_degree, vh_not_with_max_degree]):
            t_star.edges.append(min_cost_edge)

        e_1.remove(min_cost_edge)

    return t_star


def custom(graph: UndirectedGraph):
    def edge_exchage_for_degree_reduction(
        graph: UndirectedGraph, tree: UndirectedGraph, v: Vertex
    ):
        edges = sorted(tree.find_egdes_of_vertex(v), key=lambda e: e.w, reverse=True)
        forbidden_edges = graph.find_egdes_of_vertex(v)
        other_edges = sorted(
            (e for e in graph.edges if e not in forbidden_edges), key=lambda e: e.w
        )
        current_vextex_degree = len(tree.find_vertexes_connected_to_vertex(v))
        for e in edges:
            for oe in other_edges:
                candidate = UndirectedGraph(tree.V.copy(), tree.edges.copy())
                candidate.edges.remove(e)
                candidate.edges.append(oe)

                ov = oe.u if oe.u != v else oe.v

                vextex_degree = len(candidate.find_vertexes_connected_to_vertex(v))
                other_vertex_degree = len(
                    candidate.find_vertexes_connected_to_vertex(ov)
                )
                if (
                    candidate.is_connected
                    and vextex_degree < current_vextex_degree
                    and other_vertex_degree <= ov.max_degree
                ):
                    if e in graph.edges:
                        graph.edges.remove(e)
                    if oe in graph.edges:
                        graph.edges.remove(oe)
                    tree.edges.remove(e)
                    tree.edges.append(oe)
                    return True

        return False

    tree = kruskal(graph)
    continue_reducing = True
    while continue_reducing:
        vertexes_with_degree_greater_than_max = [
            v
            for v in tree.V
            if len(tree.find_vertexes_connected_to_vertex(v)) > v.max_degree
        ]
        exchanged = [
            edge_exchage_for_degree_reduction(graph, tree, v)
            for v in vertexes_with_degree_greater_than_max
        ]

        continue_reducing = any(exchanged) and vertexes_with_degree_greater_than_max

    return tree


def custom2(graph: UndirectedGraph):
    def edge_exchage_for_degree_reduction(
        graph: UndirectedGraph, tree: UndirectedGraph, v: Vertex
    ):
        edges = sorted(tree.find_egdes_of_vertex(v), key=lambda e: e.w, reverse=True)
        forbidden_edges = graph.find_egdes_of_vertex(v)
        other_edges = sorted(
            (e for e in graph.edges if e not in forbidden_edges), key=lambda e: e.w
        )
        current_vextex_degree = len(tree.find_vertexes_connected_to_vertex(v))
        for e in edges:
            for oe in other_edges:
                candidate = UndirectedGraph(tree.V.copy(), tree.edges.copy())
                candidate.edges.remove(e)
                candidate.edges.append(oe)

                ov = oe.u if oe.u != v else oe.v

                vextex_degree = len(candidate.find_vertexes_connected_to_vertex(v))
                other_vertex_degree = len(
                    candidate.find_vertexes_connected_to_vertex(ov)
                )
                if (
                    candidate.is_connected
                    and vextex_degree < current_vextex_degree
                    and other_vertex_degree <= ov.max_degree
                ):
                    if e in graph.edges:
                        graph.edges.remove(e)
                    if oe in graph.edges:
                        graph.edges.remove(oe)
                    tree.edges.remove(e)
                    tree.edges.append(oe)
                    return True

        return False

    tree = prim(graph)
    continue_reducing = True
    while continue_reducing:
        vertexes_with_degree_greater_than_max = [
            v
            for v in tree.V
            if len(tree.find_vertexes_connected_to_vertex(v)) > v.max_degree
        ]
        exchanged = [
            edge_exchage_for_degree_reduction(graph, tree, v)
            for v in vertexes_with_degree_greater_than_max
        ]

        continue_reducing = any(exchanged) and vertexes_with_degree_greater_than_max

    return tree
