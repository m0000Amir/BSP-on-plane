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
    edge_z = list(product(input_data.device.keys(),
                          input_data.station.keys()))
    edge_x = (list(permutations(input_data.station.keys(), 2)) +
              list(product(input_data.station.keys(),
                           input_data.gateway.keys())))

    var_z = create_edge_var_name('z', edge_z)
    var_x = create_edge_var_name('x', edge_x)

    var_y = ['y' + str(i) for i in input_data.station.keys()]
    return {'z': var_z, 'x': var_x, 'y': var_y}


def get_column_name(input_data: InputData) -> Dict:
    point_count = int(len(input_data.station) / len(input_data.type))
    station_point = [list(input_data.station.keys())[0] + i
                     for i in range(point_count)]

    _sp = list(product(station_point,
                       list(map(lambda x: x + 1, input_data.type.keys()))))

    _coordinate_n_sta = [f'c{_[0]}_s{_[1]}' for _ in _sp]
    col_edge_name = list(product(input_data.device.keys(), _coordinate_n_sta))

    # TODO: delete these lists
    device2sta = create_edge_var_name(
        name='d',
        edge_name=list(product(input_data.device.keys(), _coordinate_n_sta)),
        sep='->')
    sta2sta = create_edge_var_name(
        name='',
        edge_name=list(permutations(_coordinate_n_sta, 2)),
        sep='->')
    sta2gtw = create_edge_var_name(
        name='',
        edge_name=list(product(_coordinate_n_sta, input_data.gateway.keys())),
        sep='->')

    return {'z': device2sta,
            'x': (sta2sta + sta2gtw),
            'y': _coordinate_n_sta}


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
