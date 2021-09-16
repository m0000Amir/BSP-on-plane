""" This module consists solution of Base station problem on the plane"""
from dataclasses import dataclass
import json
from itertools import product
from typing import Dict


from src.net import Network
from src.mipop.mipop import MIPOP


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
    type = {k: value for k, value in enumerate(data['station']['type'])}

    return InputData(gateway=gateway,
                     device=device,
                     station=station,
                     type=type)


if __name__ == "__main__":
    with open("./problem.json") as f:
        data_from_json = json.load(f)

    input_data = prepare_input_data(data_from_json)
    # net = Network(input_data)
    MIPOP(input_data)


    print(net.adjacency_matrix)

    # create_net(nodes)
