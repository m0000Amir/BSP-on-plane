""" This module consists graph of wireless network """
from dataclasses import dataclass
from itertools import product,  permutations
from typing import Tuple, Dict, List
import math


import networkx as nx
import numpy as np


@dataclass
class InputData:
    """ dataclass of input data (gateway, devices, and stations)"""
    gateway: dict
    device: dict
    station: dict


class Network:
    """ Wireless network of the problem"""
    def __init__(self, input_data: InputData):
        self.graph = nx.DiGraph()
        self.gateway = input_data.gateway
        self.device = input_data.device
        self.station = input_data.station
        self.__d2s = None
        self.__s2s = None
        self.__s2g = None
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
        self.__d2s = list(product(self.device.keys(), self.station.keys()))
        for d2s in self.__d2s:
            if self.exist_edge(self.device[d2s[0]]['coordinates'],
                               self.station[d2s[1]]['coordinates'],
                               self.station[d2s[1]]['coverage']):
                self.graph.add_edge(d2s[0], d2s[1])

        # Station To Station
        self.__s2s = list(permutations(self.station.keys(), 2))
        for s2s in self.__s2s:
            if self.exist_edge(self.station[s2s[0]]['coordinates'],
                               self.station[s2s[1]]['coordinates'],
                               self.station[s2s[1]]['link_distance']):
                self.graph.add_edge(s2s[0], s2s[1])

        # Station To Gateway
        self.__s2g = list(product(self.station.keys(), self.gateway.keys()))
        for s2g in self.__s2g:
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

    @property
    def get_device2station_edge(self):
        return self.__d2s

    @property
    def get_station2station_edge(self):
        return self.__s2s

    @property
    def get_station2gateway_edge(self):
        return self.__s2g


def prepare_input_data(data: Dict) -> InputData:
    """
    Prepare nodes to network graph.
        Node types:
            - gateway;
            - device;
            - station.
    Parameters
    ----------
    data
        input data of the problem

    Returns
    -------
        gateway, device, station

    """
    gateway = {k: value for k, value in enumerate(data['gateway'])}
    device = {k + 1: value for k, value in enumerate(data['device'])}
    station_coordinates = [{'coordinates': value} for value in
                           data['station']['coordinates']]
    _product_station = list(product(station_coordinates,
                                    data['station']['type']))
    station = {i + len(device) + 1: {**_product_station[i][0],
                                     **_product_station[i][1]}
               for i in range(len(_product_station))}

    return InputData(gateway=gateway, device=device, station=station)


