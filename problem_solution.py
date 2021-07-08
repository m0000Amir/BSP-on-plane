""" This module consists solution of Base station problem on the plane"""
import json


from src.net import InputData, prepare_input_data, Network
from src.mipop.mipop import MIPOP

with open("../problem.json") as f:
    data = json.load(f)

input_data = prepare_input_data(data)
net = Network(input_data)
MIPOP(net)


print(net.adjacency_matrix)

# create_net(nodes)
