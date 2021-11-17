""" This module consists graph of wireless network """
from __future__ import annotations
from typing import List, TYPE_CHECKING
if TYPE_CHECKING:
    from mip_solution import InputData
from itertools import product,  permutations
import math


import networkx as nx
import numpy as np


class Network:
    """ Wireless network of the problem"""
    def __init__(self, input_data: InputData):
        self.graph = nx.DiGraph()
        self.gateway = input_data.gateway
        self.device = input_data.device
        self.station = input_data.station
        self.type = input_data.type

    @staticmethod
    def exist_edge(point1: List[float],
                   point2: List[float],
                   param: float) -> bool:
        distance = math.sqrt((point1[0] - point2[0]) ** 2 +
                             (point1[1] - point2[1]) ** 2)
        return distance <= param

    def is_connected_graph(self) -> bool:
        """
        Shortest paths is computed for all device in the graph using
        Dijkstra's algorithm

        Returns
        -------
        bool
            True if path from device is exist, False otherwise
        """

        gateway_key = list(self.gateway.keys())[0]
        all_paths_exist = all([nx.has_path(self.graph, i, gateway_key)
                               for i in list(self.device.keys())])
        return all_paths_exist

    @property
    def adj_matrix(self) -> np.ndarray:
        return nx.adjacency_matrix(self.graph).toarray()


def create_graph(input_data: InputData) -> Network:
    net = Network(input_data)

    net.graph.add_nodes_from(list(net.gateway.keys()) +
                             list(net.device.keys()) +
                             list(net.station.keys()))
    """ 
    Make edge between 
        - Device 2 Station;
        - Station 2 Station; 
        - Station 2 Gateway.
    """
    # Device To Station
    for d2s in product(net.device.keys(), net.station.keys()):
        if net.exist_edge(net.device[d2s[0]]['coordinates'],
                          net.station[d2s[1]]['coordinates'],
                          net.station[d2s[1]]['coverage'][d2s[0]]):
            net.graph.add_edge(d2s[0], d2s[1])

    # Station To Station
    for s2s in permutations(net.station.keys(), 2):
        # if (s2s[0] == 22) and (s2s[1] == 19):
        #     a = 1
        param_min = min(net.station[s2s[0]]['link_distance'][s2s[1]],
                        net.station[s2s[1]]['link_distance'][s2s[0]])
        if net.exist_edge(net.station[s2s[0]]['coordinates'],
                          net.station[s2s[1]]['coordinates'],
                          param_min):
            net.graph.add_edge(s2s[0], s2s[1])

    # Station To Gateway
    for s2g in product(net.station.keys(), net.gateway.keys()):
        param_min = min(net.station[s2g[0]]['link_distance'][s2g[1]],
                        net.gateway[s2g[1]]['link_distance'][s2g[0]])
        if net.exist_edge(net.station[s2g[0]]['coordinates'],
                          net.gateway[s2g[1]]['coordinates'],
                          param_min):
            net.graph.add_edge(s2g[0], s2g[1])

    net.is_connected_graph()
    return net
