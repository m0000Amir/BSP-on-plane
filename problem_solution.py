""" This module consists solution of Base station problem on the plane"""
from dataclasses import dataclass
import json
from itertools import product
from typing import Dict

import pandas as pd


import src.gurobi.milp_problem
import src.matlab.milp_problem
from src.mipop.mipop import create_mipop
from src.draw import draw_input_data, draw_mip_graph
from src.net import create_graph


@dataclass
class InputData:
    """ dataclass of input data (gateway, devices, and stations)"""
    gateway: dict
    device: dict
    station: dict
    type: dict


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
        gateway, device, station, sta_type

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
    sta_type = {k: value for k, value in enumerate(data['station']['type'])}

    return InputData(gateway=gateway,
                     device=device,
                     station=station,
                     type=sta_type)


if __name__ == "__main__":
    with open("./problem.json") as f:
        data_from_json = json.load(f)

    solver = "gurobi"

    input_data = prepare_input_data(data_from_json)
    # Graph of the problem
    net = create_graph(input_data)

    problem = create_mipop(input_data, net)

    if solver == 'gurobi':
        x = src.gurobi.milp_problem.solve(problem)
    else:
        x = src.matlab.milp_problem.solve(problem.of.data.values,
                                          problem.of.int_constraints,
                                          problem.ineq_constraints.data.values,
                                          problem.ineq_constraints.b,
                                          problem.eq_constraints.data.values,
                                          problem.eq_constraints.b,
                                          problem.of.lower_bounds,
                                          problem.of.upper_bounds)

    solution = pd.Series(x, index=problem.of.data.columns.values).T
    placed_station = solution[problem.of.column.y].values
    # placed_station.tolist()
    draw_mip_graph(net, problem)

    debug = 1
