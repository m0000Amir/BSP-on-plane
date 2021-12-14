""" Linear Problem of Optimal Placement """
from __future__ import annotations
from typing import List, Tuple, Dict, TYPE_CHECKING, Any
if TYPE_CHECKING:
    from mip_solution import InputData
from itertools import product,  permutations


from src.net import Network
from src.op.mipop import MIP,  OF
from src.op.varnames import VarName
from src.op.mipop import EqualityConstraints, InequalityConstraints
from src.op.varnames import create_names

import numpy as np
import pandas as pd


class LP(MIP):
    def __init__(self):
        super(LP, self).__init__()


class LpOF(OF):
    def __init__(self,
                 input_data: InputData,
                 var_name: VarName,
                 col_name: VarName):
        super(LpOF, self).__init__(input_data, var_name, col_name)

    # TODO : make variable w_i
    def prepare_of_variables(self, input_data, var_name, col_name):
        # Cost * y -> min
        y_col = np.where(np.in1d(self.data.columns.values,
                                 self.column.y))
        self.data.iloc[0, y_col] = 1

        # Bounds
        self.lower_bounds = np.zeros([1, len(self.column.name)]).astype(int)
        __sta2sta = [input_data.station[i]["intensity"] for i in
                     input_data.station.keys()
                     for j in input_data.station.keys() if i != j]
        __sta2gtw = [input_data.station[i]["intensity"] for i in
                     input_data.station.keys()]

        self.upper_bounds = np.concatenate((
            np.ones([len(self.var.z)]).astype(int)*np.inf,
            np.array(__sta2sta + __sta2gtw).astype(int),
            np.ones([len(self.var.y)]).astype(int)*np.inf)
        )

        self.int_constraints = None


class LpEqualityConstraints(EqualityConstraints):
    def __init__(self,
                 input_data: InputData,
                 var_name: VarName,
                 col_name: VarName,
                 net: Network):
        super().__init__(input_data, var_name, col_name, net)

    def device_conditions_b(self, input_data: InputData):
        """ right vector for device conditions """
        for i in input_data.device.keys():
            self.b[i] = input_data.device[i]['intensity']

    def get_links_from_device_to_sta(self,
                                     i: int,
                                     data_row: int,
                                     input_data: InputData,
                                     net: Network):
        """
        All station has incoming links from devices and other stations.
        Using adjacency matrix, we add all input edges
        """
        _row, = np.where(net.adj_matrix[:, i] == 1)
        for j in _row:
            if int(j) in input_data.device.keys():
                var = "z"
            else:
                var = "x"
            _var_name = [f'{var}{int(j)}_{i}']
            _col = np.where(np.in1d(self.var.name, _var_name))
            self.data.iloc[data_row, _col] = 1


class LpInequalityConstraints(InequalityConstraints):
    """ Matrix of inequality constraints"""

    def __init__(self,
                 input_data: InputData,
                 var_name: VarName,
                 col_name: VarName,
                 net: Network):
        super().__init__(input_data, var_name, col_name, net)

    def get_links_from_device_to_sta(self,
                                     i: int,
                                     data_row: int,
                                     input_data: InputData,
                                     net: Network):
        """
        All station has incoming links from devices and other stations.
        Using adjacency matrix, we add all input edges
        """
        _row, = np.where(net.adj_matrix[:, i] == 1)
        for j in _row:
            if int(j) in input_data.device.keys():
                var = "z"
            else:
                var = "x"
            _var_name = [f'{var}{int(j)}_{i}']
            _col = np.where(np.in1d(self.var.name, _var_name))
            self.data.iloc[data_row, _col] = 1

    def get_station_limit_condition(self,
                                    i: int,
                                    data_row: int,
                                    input_data: InputData):
        """ Condition from class InequalityConstraints of Station's
        throughput is note needed"""
        self.b[data_row] = input_data.station[i]["intensity"]

    def to_place_only_one_station_condition(self,
                                            input_data: InputData,
                                            net: Network):
        """ This method (from class InequalityConstraints) is not needed """
        pass


def create_lpop(input_data: InputData, net: Network) -> LP:
    """
    Create Linear Problem of Optimal Placement

    Parameters
    ----------
    input_data: include:
        - device parameter;
        - sta coordinates with each placed station;
        - gateway parameter.

    net: graph of feasible base station placement

    Returns
    -------
        LPOP:
            - objective function;
            - equality constraints with right vector;
            - inequality constraints with right vector;

    """
    lpop = LP()
    _v_name, _c_name = create_names(input_data, net.adj_matrix)

    var_name, col_name = create_names(input_data, net.adj_matrix)

    lpop.of = LpOF(input_data, var_name, col_name)

    lpop.eq_constraints = LpEqualityConstraints(input_data, var_name,
                                                col_name, net)
    lpop.ineq_constraints = LpInequalityConstraints(input_data, var_name,
                                                    col_name, net)

    # y = [f'y{i + 1}' for i in range(
    #     len(input_data.gateway) +
    #     len(input_data.device) +
    #     len(input_data.station)
    # )]
    # var_name = VarName(z=_v_name['z'], x=_v_name['x'], y=y)
    # col_name = VarName(z=_c_name['z'], x=_c_name['x'], y=y)
    # lpop.of = LpOF(input_data, var_name, col_name)
    #
    # lpop.eq_constraints = LpEqualityConstraints(input_data, var_name,
    #                                             col_name, net)
    # lpop.ineq_constraints = LpInequalityConstraints(input_data, var_name,
    #                                                 col_name, net)
    return lpop