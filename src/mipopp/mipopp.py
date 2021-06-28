"""Mixed Integer Programming of Optimal Placement Problem """
import json

from src.network import WirelessNetwork


def get_mip_solution(solver: str ='gurobi'):
    with open('../input_data.json') as f:
        data = json.load(f)

    net = WirelessNetwork(data)
    pass

