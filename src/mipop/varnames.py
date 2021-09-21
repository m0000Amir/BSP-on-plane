"""
Creation of variable names and column names for MIP
"""
from __future__ import annotations
from typing import List, Tuple, Dict, TYPE_CHECKING, Any
if TYPE_CHECKING:
    from problem_solution import InputData
from itertools import product,  permutations


def create_edge_var_name(name: str,
                         edge_name: List[Any, ...],
                         sep: str = '_') -> List[str]:
    return [name + sep.join(map(str, edge_name[i]))
            for i in range(len(edge_name))]


def get_variable_name(input_data: InputData) -> Dict:
    """
    Get variable name of the problem
    Returns
    -------
        Dict of variable names
    """
    device_edge = list(product(input_data.device.keys(),
                               input_data.station.keys()))
    sta_edge = (list(permutations(input_data.station.keys(), 2)) +
                list(product(input_data.station.keys(),
                             input_data.gateway.keys())))

    var_z = (create_edge_var_name('z', device_edge) +
             create_edge_var_name('z', sta_edge))
    var_x = create_edge_var_name('x', sta_edge)

    var_y = ['y' + str(i) for i in input_data.station.keys()]
    return {'z': var_z, 'x': var_x, 'y': var_y}


def get_column_name(input_data: InputData) -> Dict:
    point_count = int(len(input_data.station) / len(input_data.type))
    station_point = [list(input_data.station.keys())[0] + i
                     for i in range(point_count)]

    _sp = list(product(station_point,
                       list(map(lambda x: x + 1, input_data.type.keys()))))

    y_column = [f'c{_[0]}_s{_[1]}' for _ in _sp]
    col_edge_name = list(product(input_data.device.keys(), y_column))

    # TODO: delete these lists
    # device2sta = create_edge_var_name(
    #     name='d',
    #     edge_name=list(product(input_data.device.keys(), y_column)),
    #     sep='->')
    # sta2sta = create_edge_var_name(
    #     name='',
    #     edge_name=list(permutations(y_column, 2)),
    #     sep='->')
    # sta2gtw = create_edge_var_name(
    #     name='',
    #     edge_name=list(product(y_column, input_data.gateway.keys())),
    #     sep='->')
    z_column = (
            create_edge_var_name(
                name='z_d',
                edge_name=list(product(input_data.device.keys(),
                                       y_column)),
                sep='->') +
            create_edge_var_name(
                name='z_',
                edge_name=list(permutations(y_column, 2)),
                sep='->') +
            create_edge_var_name(
                    name='z_',
                    edge_name=list(product(y_column, input_data.gateway.keys())),
                    sep='->')
            )
    x_column = (
        create_edge_var_name(
            name='x_',
            edge_name=list(permutations(y_column, 2)),
            sep='->') +
        create_edge_var_name(
                name='x_',
                edge_name=list(product(y_column, input_data.gateway.keys())),
                sep='->')
    )

    return {'z': z_column,
            'x': x_column,
            'y': y_column}


def create_names(input_data: InputData) -> Tuple[Dict[str], Dict[str]]:
    """
    Create variable and column name
    Parameters
    ----------
    input_data: include device, station points with placed station,
                gateway, and station types.

    Returns
    -------
        - variable name;
        - column name.
    """
    variable_name = get_variable_name(input_data)
    column_name = get_column_name(input_data)
    return variable_name, column_name
