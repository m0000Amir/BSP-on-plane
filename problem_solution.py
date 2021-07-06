""" This module consists solution of Base station problem on the plane"""
import json


from src.net import ProblemInputData, create_net, get_net_nodes, Network

with open("../problem.json") as f:
    data = json.load(f)
    problem = ProblemInputData(gateway=data['gateway'],
                               device=data['device'],
                               station=data['station'])
nodes = get_net_nodes(problem)
net = Network(nodes)
# create_net(nodes)
