from dataclasses import dataclass
from typing import List

from surveillance.roombuilder.roombuilder import RoomMap


@dataclass
class Pose:
    x: float
    y: float
    theta: float


def _get_number_cycles(graph: dict) -> int:
    """
    Determine the number of cycles present in the given graph this needs to
    ignore the bidirectional edges
    """
    edges = set()
    for node in graph:
        for neighbor in graph[node]['neighbors']:
            # Make the edge representation, have the smaller node always
            # come first to avoid duplicates (i.e. (1, 2) and (2, 1))
            edge = (min(node, neighbor), max(node, neighbor))
            if edge not in edges:
                edges.add(edge)

    return len(edges) - len(graph) + 1


def _get_hallways(room_map: RoomMap) -> List[int]:
    hallways = []
    for node in room_map.reduced_graph:
        if room_map._is_hallway_node(node):
            hallways.append(node)
    return hallways


def _get_sub_graph_sizes(graph: dict) -> List[int]:
    """
    Count the number of nodes in each subgraph of the larger graph
    """
    sub_graphs: List[set] = []

    for node in graph:
        sub_graph_index = None
        # Check if the node is already assigned a subgraph
        for (index, sub_graph) in enumerate(sub_graphs):
            if node in sub_graph:
                sub_graph_index = index
                break

        # If the node is not assigned a subgraph, make one for it
        if sub_graph_index is None:
            new_sub_graph = set()
            new_sub_graph.add(node)
            new_sub_graph.update(graph[node]['neighbors'])
            sub_graphs.append(new_sub_graph)
        # If the node is assigned a subgraph, add the neighbors to the
        # subgraph
        else:
            sub_graphs[sub_graph_index].update(graph[node]['neighbors'])

    return [len(sub_graph) for sub_graph in sub_graphs]
