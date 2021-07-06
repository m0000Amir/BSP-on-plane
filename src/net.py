""" This module consists graph of wireless network """
from dataclasses import dataclass
from itertools import product,  permutations
from typing import Tuple, Dict, List
import math


import networkx as nx
import numpy as np


@dataclass
class ProblemInputData:
    gateway: list
    device: list
    station: dict


class Network:
    """ Wireless network of the problem"""
    def __init__(self, nodes: Tuple[Dict, Dict, Dict]):
        self.graph = nx.DiGraph()
        self.gateway = nodes[0]
        self.device = nodes[1]
        self.station = nodes[2]
        self._create()

    @staticmethod
    def exist_edge(point1: List[float],
                   point2: List[float],
                   param: float) -> bool:
        distance = math.sqrt((point1[0] - point2[0]) ** 2 +
                             (point1[1] - point2[1]) ** 2)
        return distance <= param

    def _make_graph_edge(self) -> None:
        """
        Make edge between Device 2 Station,
        Station 2 Station, and Station 2 Gateway

        """

        # Device To Station
        for d2s in product(self.device.keys(), self.station.keys()):
            if self.exist_edge(self.device[d2s[0]]['coordinates'],
                               self.station[d2s[1]]['coordinates'],
                               self.station[d2s[1]]['coverage']):
                self.graph.add_edge(d2s[0], d2s[1])

        # Station To Station
        for s2s in permutations(self.station.keys(), 2):
            if self.exist_edge(self.station[s2s[0]]['coordinates'],
                               self.station[s2s[1]]['coordinates'],
                               self.station[s2s[1]]['link_distance']):
                self.graph.add_edge(s2s[0], s2s[1])

        # Station To Gateway
        for s2g in product(self.station.keys(), self.gateway.keys()):
            if self.exist_edge(self.station[s2g[0]]['coordinates'],
                               self.gateway[s2g[1]]['coordinates'],
                               self.station[s2g[0]]['link_distance']):
                self.graph.add_edge(s2g[0], s2g[1])

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
    def adjacency_matrix(self) -> np.ndarray:
        return nx.adjacency_matrix(self.graph).toarray()

    def _create(self) -> None:
        self.graph.add_nodes_from(list(self.gateway.keys()) +
                                  list(self.device.keys()) +
                                  list(self.station.keys()))
        self._make_graph_edge()
        self.is_connected_graph()


def get_net_nodes(problem: ProblemInputData) -> Tuple[Dict, Dict, Dict]:
    """
        Prepare nodes to network graph.
        Node types:
            - gateway;
            - device;
            - station.
    Parameters
    ----------
    problem
        input data of the problem

    Returns
    -------
        gateway, device, station

    """
    gateway = {k: value for k, value in enumerate(problem.gateway)}
    device = {k + 1: value for k, value in enumerate(problem.device)}
    station_coordinates = [{'coordinates': value} for value in
                           problem.station['coordinates']]
    _product_station = list(product(station_coordinates,
                                    problem.station['type']))
    station = {i + len(device) + 1: {**_product_station[i][0],
                                     **_product_station[i][1]}
               for i in range(len(_product_station))}

    return gateway, device, station


def create_net(problem: ProblemInputData) -> Network:
    """
    Prepare network for the problem

    Parameters
    ----------
    problem
        input data of the problem

    Returns
    -------
        Network
    """
    gateway, device, station = get_net_nodes(problem)

    return Network(gateway, device, station)

