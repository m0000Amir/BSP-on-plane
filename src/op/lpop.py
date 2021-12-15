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

    def add_synthetic_variables(self):
        if ((self.eq_constraints is not None) and
                (self.ineq_constraints is not None)):
            eq_constraints_count = len(self.eq_constraints.data)
            ineq_constraints_count = len(self.ineq_constraints.data)

            all_synthetic_variables = np.eye(eq_constraints_count +
                                             ineq_constraints_count).astype(int)
            # _col = len(self.eq_constraints.var.z)
            # all_synthetic_variables = _all_synthetic_variables[:, _col:]
            self.add_synthetic_name(all_synthetic_variables)
            eq_synthetic_variables = \
                all_synthetic_variables[:eq_constraints_count, :]
            eq_data = np.hstack(
                (self.eq_constraints.data.values, eq_synthetic_variables))
            self.eq_constraints.data = pd.DataFrame(
                eq_data, columns=self.eq_constraints.column.name)

            ineq_synthetic_variables = \
                all_synthetic_variables[eq_constraints_count:, :]
            ineq_data = np.hstack(
                (self.ineq_constraints.data.values, ineq_synthetic_variables))
            self.ineq_constraints.data = pd.DataFrame(
                ineq_data, columns=self.ineq_constraints.column.name)

    def add_synthetic_name(self,
                           all_synthetic_variables: np.array
                           ):
        """ Need to add synthetic variables for OF """
        synthetic_name = [f"y{i + 1}" for i in range(len(all_synthetic_variables[0, :]))]
        self.eq_constraints.var.y = synthetic_name
        self.eq_constraints.var.y = synthetic_name
        self.eq_constraints.var.name = np.append(
            self.eq_constraints.var.name,
            np.array(synthetic_name)
        )

        self.ineq_constraints.column.y = synthetic_name
        self.ineq_constraints.column.y = synthetic_name
        self.ineq_constraints.column.name = np.append(
            self.ineq_constraints.column.name,
            np.array(synthetic_name)
        )


class LpOF(OF):
    def __init__(self,
                 input_data: InputData,
                 adj_matrix: np.array,
                 var_name: VarName,
                 col_name: VarName):
        super(LpOF, self).__init__(input_data, adj_matrix, var_name, col_name)

    # TODO : make variable w_i
    def prepare_of_variables(self, input_data, adj_matrix, var_name, col_name):
        # Cost * y -> min
        y_col = np.where(np.in1d(self.data.columns.values,
                                 self.column.y))
        self.data.iloc[0, y_col] = 1

        # Bounds
        self.lower_bounds = np.zeros([1, len(self.column.name)]).astype(int)
        # __sta2sta = [input_data.station[i]["intensity"] for i in
        #              input_data.station.keys()
        #              for j in input_data.station.keys() if i != j]
        # __sta2gtw = [input_data.station[i]["intensity"] for i in
        #              input_data.station.keys()]

        throughput = []
        # TODO: change as throughput in MIPOP
        for i in input_data.station.keys():
            if adj_matrix[i, 0] == 1:
                throughput.append(input_data.station[i]["intensity"])
            for j in input_data.station.keys():
                if (i != j) and (adj_matrix[i, j] == 1):
                    throughput.append(input_data.station[i]["intensity"])

        self.upper_bounds = np.concatenate((
            np.ones([len(self.var.z)]).astype(int)*np.inf,
            np.array(throughput).astype(int),
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

    def gateway_conditions(self, input_data: InputData, net: Network):
        """
            Prepare equality constraints for gateway. Through the stations, all
            information flow from devices must be available to the gateway.
        """
        for i in input_data.gateway.keys():
            data_row = self.counter()
            _row, = np.where(net.adj_matrix[:, i] == 1)
            _row_name = ['x' + str(_row[j]) + '_' +
                         str(i) for j in range(len(_row))]
            _col, = np.where(np.in1d(self.var.name, _row_name))
            self.data.iloc[data_row, _col] = 1
            self.b[i] = sum(input_data.device[i]["intensity"]
                            for i in input_data.device.keys())

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

    def station_conditions(self, input_data: InputData, net: Network):
        """
            Prepare equality constraints for stations. Traffic must be move
            through a station.
        """

        for i in input_data.station.keys():
            data_row = self.counter()
            self.get_links_from_device_to_sta(i, data_row, input_data, net)

            """ 
            Outgoing links for station 'S_j' 
            All station has outgoing links from devices and other stations.
            Using adjacency matrix, we add all output edges
            """
            _col, = np.where(net.adj_matrix[i, :] == 1)
            _var_name = [f"x{i}_{_col[j]}" for j in range(len(_col))]
            _column, = np.where(np.in1d(self.var.name, _var_name))
            self.data.iloc[data_row, _column] = -1
            self.b[data_row] = 0

        # TODO: check it ($x_{ij} = - x_{ji}$)

        # for i in input_data.station.keys():
        #     for j in input_data.station.keys():
        #         if i != j:
        #             data_row = self.counter()
        #             input_var_name = f"x{i}_{j}"
        #             output_var_name = f"x{j}_{i}"
        #             input_column, = np.where(np.in1d(self.var.name,
        #                                              [input_var_name]))
        #             output_column, = np.where(np.in1d(self.var.name,
        #                                               [output_var_name]))
        #             self.data.iloc[data_row, input_column] = 1
        #             self.data.iloc[data_row, output_column] = -1
        #             self.b[data_row] = 0


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

    # def station_conditions(self, input_data, net) -> None:
    #     # for i in input_data.station.keys():
    #     #     data_row = self.counter()
    #     #     self.get_links_from_device_to_sta(i, data_row, input_data, net)
    #     #
    #     #     self.get_station_limit_condition(i, data_row, input_data)
    #     #
    #     # self.to_place_only_one_station_condition(input_data, net)
    #     for i in input_data.station.keys():
    #         data_row = self.counter()
    #         _row, = np.where(net.adj_matrix[i, :] == 1)
    #         for j in _row:
    #             _var_name = [f'x{int(i)}_{j}']
    #             _col = np.where(np.in1d(self.var.name, _var_name))
    #             self.data.iloc[data_row, _col] = 1
    #             self.get_station_limit_condition(i, data_row, input_data)
    #     a = 1

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

    var_name, col_name = create_names(input_data,
                                      net.adj_matrix,
                                      problem="lp")

    lpop.eq_constraints = LpEqualityConstraints(input_data, var_name,
                                                col_name, net)
    lpop.ineq_constraints = LpInequalityConstraints(input_data, var_name,
                                                    col_name, net)
    lpop.add_synthetic_variables()

    lpop.of = LpOF(input_data, net.adj_matrix, var_name, col_name)
    a = 1
    return lpop