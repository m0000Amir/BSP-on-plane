"""
Base sta system
"""
import itertools
import math

import networkx as nx


class BSS:
    def __init__(self, gate, obj, station, sta_type):
        self.g_p = gate['pos']
        self.o_p = obj['pos']
        self.s_p = {k + len(self.o_p) + 1: value for k, value in
                    enumerate(list(station['pos'].values()) * len(sta_type))}
        self.coverage = None
        self.link_distance = None
        self.G = nx.DiGraph()
        self.adj_matrix = None

        self.c = [sta_type[i + 1]['coverage']
                  for i in range(len(sta_type))]
        self.ld = [sta_type[i + 1]['link_distance']
                   for i in range(len(sta_type))]

    def prepare_sta_param(self):
        """
        prepare sta params
        :return: sta_pos, coverage, link distance.
        """
        _s_key = list(self.s_p.keys())
        # coverage
        _cov = list(j for i in [[k] * int(len(self.s_p) / len(self.c))
                                for k in self.c] for j in i)
        self.coverage = {k + _s_key[0]: value
                         for k, value in enumerate(_cov)}

        # link distance
        _link = list(j for i in [[k] * int(len(self.s_p) / len(self.ld))
                                 for k in self.ld] for j in i)
        self.link_distance = {k + _s_key[0]: value
                              for k, value in enumerate(_link)}

    @staticmethod
    def make_edge(i, j, point1, point2, param):
        distance = math.sqrt((point1[i][0] - point2[j][0]) ** 2 +
                             (point1[i][1] - point2[j][1]) ** 2)
        return distance < param[i]

    def check_o2g_path(self):
        gateway = list(self.g_p.keys())[0]
        paths_exist = all([nx.has_path(self.G, i, gateway)
                           for i in list(self.o_p.keys())])
        assert paths_exist, \
            'The graph does not link all objects with the gateway'

    def create(self):
        self.prepare_sta_param()
        # create graph(G) nodes
        self.G.add_nodes_from([i for i in range(len(self.g_p) +
                                                len(self.s_p) +
                                                len(self.o_p))])
        for o2s in itertools.product(self.o_p.keys(), self.s_p.keys()):
            if self.make_edge(o2s[1], o2s[0],
                              self.s_p, self.o_p, self.coverage):
                self.G.add_edge(o2s[0], o2s[1])

        # add edge of station2station
        for s2s in itertools.permutations(self.s_p.keys(), 2):
            if self.make_edge(s2s[0], s2s[1],
                              self.s_p, self.s_p, self.link_distance):
                self.G.add_edge(s2s[0], s2s[1])

        # add edge of station2gateway
        for s2g in itertools.product(self.s_p.keys(), self.g_p.keys()):
            if self.make_edge(s2g[0], s2g[1],
                              self.s_p, self.g_p, self.link_distance):
                self.G.add_edge(s2g[0], s2g[1])

        self.check_o2g_path()

        self.adj_matrix = nx.adjacency_matrix(self.G)
