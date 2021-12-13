""" This module consists solution of Base station problem on the plane"""
from dataclasses import dataclass
import json
from itertools import product
from typing import Dict

import pandas as pd


import src.gurobi.milp_problem
import src.matlab.milp_problem
from src.op.lpop import create_lpop
from src.drawing.draw import draw_mip_graph, draw_input_data
from src.net import create_graph
from src.link.sta_value import GetDistanceInput, get_distance
from src.lp_problem import solve_lp_problem


@dataclass
class InputData:
    """ dataclass of input data (gateway, devices, and stations)"""
    gateway: dict
    device: dict
    station: dict
    type: dict


def prepare_lp_input_data(data: Dict) -> InputData:
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



    station_coordinates = [{'coordinates': value} for value in
                           data['station']['coordinates']]
    station_types = [value for value in
                     data['station']['type']]
    station = {}
    for i in range(len(station_coordinates)):
        station.update({i + len(data['device']) + 1: {
            **station_coordinates[i], ** station_types[i]}})

    device = {k + 1: value for k, value in enumerate(data['device'])}
    gateway[0]["link_distance"] = {}
    for s1 in station.keys():
        gtw2ld_input = GetDistanceInput(
            p_tr=data["gateway"][0]["p_tr"],
            l_tr=data["gateway"][0]["l"],
            g_tr=data["gateway"][0]["g"],
            p_recv=station[s1]["p_recv"],
            g_recv=station[s1]["g"],
            l_recv=station[s1]["l"],
            frequency=station[s1]["frequency"]
        )
        gateway[0]["link_distance"].update(
            {s1: get_distance(gtw2ld_input, som=30)})

        station[s1]["link_distance"] = {}
        station[s1]["coverage"] = {}
        ld2gtw_input = GetDistanceInput(
            p_tr=station[s1]["p_tr"],
            l_tr=station[s1]["l"],
            g_tr=station[s1]["g"],
            p_recv=data["gateway"][0]["p_recv"],
            g_recv=data["gateway"][0]["g"],
            l_recv=data["gateway"][0]["l"],
            frequency=station[s1]["frequency"]
        )
        station[s1]["link_distance"].update(
            {0: get_distance(ld2gtw_input, som=30)})
        for s2 in station.keys():
            if s1 != s2:
                ld_input = GetDistanceInput(
                    p_tr=station[s1]["p_tr"],
                    l_tr=station[s1]["l"],
                    g_tr=station[s1]["g"],
                    p_recv=station[s2]["p_recv"],
                    g_recv=station[s2]["g"],
                    l_recv=station[s2]["l"],
                    frequency=station[s1]["frequency"]
                )
                station[s1]["link_distance"].update(
                    {s2: get_distance(ld_input, som=30)})

        for d in device.keys():
            coverage_input = GetDistanceInput(
                p_tr=device[d]["p_tr"],
                l_tr=device[d]["l_tr"],
                g_tr=device[d]["g_tr"],
                p_recv=station[s1]["p_recv"],
                g_recv=station[s1]["g"],
                l_recv=station[s1]["l"],
                frequency=station[s1]["frequency"]
            )
            station[s1]["coverage"].update(
                {d: get_distance(coverage_input, som=30)})

    sta_type = {k: value for k, value in enumerate(data['station']['type'])}

    return InputData(gateway=gateway,
                     device=device,
                     station=station,
                     type=sta_type)


if __name__ == "__main__":
    with open("./input/lp_problem_test.json") as f:
        data_from_json = json.load(f)

    input_data = prepare_lp_input_data(data_from_json)
    # Graph of the problem
    net = create_graph(input_data)

    problem = create_lpop(input_data, net)
    draw_input_data(net)
    result = solve_lp_problem(obj_func=problem.of.data.values,
                              ineq_array=problem.ineq_constraints.data.values,
                              ineq_b=problem.ineq_constraints.b,
                              eq_array=problem.eq_constraints.data.values,
                              eq_b=problem.eq_constraints.b,
                              lb=problem.of.lower_bounds,
                              ub=problem.of.upper_bounds)

    solution = pd.Series(result.x, index=problem.of.data.columns.values).T
    draw_mip_graph(net, problem, solution)

    debug = 1
