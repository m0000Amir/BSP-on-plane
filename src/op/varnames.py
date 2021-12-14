"""
Creation of variable names and column names for MIP
"""
from __future__ import annotations
from typing import List, Tuple, Dict, TYPE_CHECKING, Any, Union
if TYPE_CHECKING:
    from mip_solution import InputData
from itertools import product,  permutations, repeat, chain
import numpy as np


class VarName:
    """ Names of problem variable"""
    def __init__(self,
                 z: List[str] = None,
                 edge_z: List[Tuple[int, int]] = None,
                 x: List[str] = None,
                 edge_x: List[Tuple[int, int]] = None,
                 y: List[str] = None) -> None:
        self.name = np.array(z + x + y)
        self.z = z
        self.edge_z = edge_z
        self.x = x
        self.edge_x = edge_x
        self.y = y


class LpVarName:
    """ Names of linear problem variable"""
    def __init__(self,
                 z: List[str] = None,
                 edge_z: List[Tuple[int, int]] = None,
                 x: List[str] = None,
                 edge_x: List[Tuple[int, int]] = None) -> None:
        self.name = np.array(z + x)
        self.z = z
        self.edge_z = edge_z
        self.x = x
        self.edge_x = edge_x
        self.y = None


def create_edge_var_name(name: str,
                         edge_nodes: List[Any, ...],
                         sep: str = '_') -> List[str]:
    return [name + sep.join(map(str, edge_nodes[i]))
            for i in range(len(edge_nodes))]


def get_variable_name(input_data: InputData,
                      adj_matrix: np.array,
                      problem: str = "mip") -> Union[VarName, LpVarName]:
    """
    Get variable name of the problem

    Parameters
    ----------
    input_data -  data from JSON-file

    Returns
    -------
         Dict of variable names
    """

    _x_nodes = (list(permutations(input_data.station.keys(), 2)) +
                list(product(input_data.station.keys(),
                             input_data.gateway.keys())))
    edge_z = [(i, j) for i, j in product(input_data.device.keys(),
                                         input_data.station.keys())
              if adj_matrix[i, j] == 1]
    edge_x = [(i, j) for i, j in _x_nodes if adj_matrix[i, j] == 1]
    var_z = create_edge_var_name('z', edge_z)
    var_x = create_edge_var_name('x', edge_x)

    if problem == "mip":
        var_y = create_edge_var_name('y', edge_x)
        return VarName(var_z, edge_z, var_x, edge_x, var_y)
    else:
        return LpVarName(var_z, edge_z, var_x, edge_x)


def get_column_name(input_data: InputData,
                    adj_matrix: np.array,
                    problem: str = "mip") -> Union[VarName, LpVarName]:
    point_count = int(len(input_data.station) / len(input_data.type))
    station_point = [list(input_data.station.keys())[0] + i
                     for i in range(point_count)]
    _point = list(chain.from_iterable(
        repeat(p, len(input_data.type)) for p in station_point))
    _station = [i + 1 for i in input_data.type] * len(station_point)

    label = {}
    station_keys = list(input_data.station.keys())
    for i in range(len(station_keys)):
        label.update({station_keys[i]: {"point": _point[i],
                                        "sta": _station[i]}})

    device2sta_nodes = product(input_data.device.keys(), label.keys())
    device2sta_edge = [(i, f'c{label[j]["point"]}_s{label[j]["sta"]}')
                       for i, j in device2sta_nodes if adj_matrix[i, j] == 1]

    device2sta = create_edge_var_name(
        name='d',
        edge_nodes=device2sta_edge,
        sep='->')

    sta2sta_nodes = product(label.keys(), label.keys())
    sta2sta_edge = [(f'c{label[i]["point"]}_s{label[i]["sta"]}', f'c{label[j]["point"]}_s{label[j]["sta"]}')
                    for i, j in sta2sta_nodes if adj_matrix[i, j] == 1]
    sta2sta = create_edge_var_name(
        name='',
        edge_nodes=sta2sta_edge,
        sep='->')

    sta2gtw_nodes = product(label.keys(), input_data.gateway.keys())
    sta2sta_edge = [(f'c{label[i]["point"]}_s{label[i]["sta"]}',
                     f's{j}')
                    for i, j in sta2gtw_nodes if adj_matrix[i, j] == 1]

    sta2gtw = create_edge_var_name(
        name='',
        edge_nodes=sta2sta_edge,
        sep='->')

    # _sp = list(product(
    #     station_point,
    #     list(map(lambda x: x + 1, input_data.type.keys()))))
    # _coordinate_n_sta = [f'c{_[0]}_s{_[1]}' for _ in _sp]  # y=_coordinate_n_sta
    if problem == "mip":
        _edge = sta2sta + sta2gtw
        binary_value_y = [f'Y_{i}' for i in _edge]
        return VarName(z=device2sta, x=(sta2sta + sta2gtw), y=binary_value_y)
    else:
        return LpVarName(z=device2sta, x=(sta2sta + sta2gtw))


def create_names(input_data: InputData,
                 adj_matrix: np.array,
                 problem:str = "mip") -> Tuple[VarName, VarName]:
    """
    Create variable and column name
    Parameters
    ----------

    input_data: include device, station points with placed station,
                gateway, and station types.

    adj_matrix
    problem: string Type of problem MIP or otherwise (LP)

    Returns
    -------
        - variable name;
        - column name.
    """
    variable_name = get_variable_name(input_data, adj_matrix, problem)
    column_name = get_column_name(input_data, adj_matrix, problem)
    return variable_name, column_name
