""" Mixed Integer Problem of Optimal Placement """
from __future__ import annotations
from typing import List, Tuple, Dict, TYPE_CHECKING, Any
if TYPE_CHECKING:
    from mip_solution import InputData
from itertools import product,  permutations


from src.net import Network
from src.op.varnames import create_names

import numpy as np
import pandas as pd


class VarName:
    """ Names of problem variable"""
    def __init__(self,
                 z: List[str] = None,
                 x: List[str] = None,
                 y: List[str] = None) -> None:
        self.name = np.array(z + x + y)
        self.z = z
        self.x = x
        self.y = y


class Matrix:
    """
    Matrix for object function, equality and inequality
    constraints.
    """
    def __init__(self, var: VarName, column: VarName):
        self.var = var
        self.column = column
        self.data = None


class OF(Matrix):
    """ Object function vector [1 x n]"""
    def __init__(self,
                 input_data: InputData,
                 var_name: VarName,
                 col_name: VarName):
        super().__init__(var_name, col_name)
        self.lower_bounds = None
        self.upper_bounds = None
        self.int_constraints = None
        self.create(input_data, var_name, col_name)

    def get_index(self, var_name: List[str]) -> np.ndarray:
        """
        Returns indexes of the required variables

        Parameters
        ----------
        var_name list of variable names

        Returns
        -------
            Indexes of the required variables

        """
        return np.where(np.in1d(self.data.columns.values, var_name))

    def prepare_of_variables(self, input_data, var_name, col_name):
        # Cost * y -> min
        y_col = np.where(np.in1d(self.data.columns.values,
                                 self.column.y))
        self.data.iloc[0, y_col] = [input_data.station[i]['cost']
                                    for i in input_data.station.keys()]

        self.int_constraints = np.where(np.in1d(self.data.columns.values,
                                                self.column.y))
        # Bounds
        self.lower_bounds = np.zeros([1, len(self.column.name)]).astype(int)

        __sta2sta = [input_data.station[i]["intensity"] for i in
                     input_data.station.keys()
                     for j in input_data.station.keys() if i != j]
        __sta2gtw = [input_data.station[i]["intensity"] for i in
                     input_data.station.keys()]
        # of.upper_bounds[0, of.int_constraints] = 1
        self.upper_bounds = np.concatenate((
            np.ones([len(self.var.z)]).astype(int),
            np.array(__sta2sta + __sta2gtw).astype(int),
            np.ones([len(self.var.y)]).astype(int))
        )

    def create(self, input_data, var_name, col_name):
        """
        Create objective function of MIP

        Cost * y -> min

        Parameters
        ----------
        input_data
        var_name
        col_name

        Returns
        -------
            objective function
        """
        data = np.zeros([1, len(self.column.name)]).astype(int)
        self.data = pd.DataFrame(data, columns=self.column.name)

        self.prepare_of_variables(input_data, var_name, col_name)




class Constraints(Matrix):
    """ Matrix of constraints"""
    def __init__(self, var: VarName, column: VarName):
        super().__init__(var, column)
        self.b = None
        self._count = 0

    def counter(self) -> int:
        count = self._count
        self._count += 1
        return count


class EqualityConstraints(Constraints):
    """ Matrix of equality constraints"""
    def __init__(self,
                 input_data: InputData,
                 var_name: VarName,
                 col_name: VarName,
                 net: Network):
        super().__init__(var_name, col_name)
        self.create(input_data, net)

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

    def device_conditions_array(self, input_data: InputData, net: Network):
        """ left array for device conditions """
        for i in input_data.device.keys():
            data_row = self.counter()
            _row, = np.where(net.adj_matrix[i, :] == 1)
            _row_name = ['z' + str(i) + '_' + str(j)
                         for j in _row.tolist()]
            _col, = np.where(np.in1d(self.var.name, _row_name))
            self.data.iloc[data_row, _col] = 1

    def device_conditions_b(self, input_data: InputData):
        """ right vector for device conditions """
        for i in input_data.device.keys():
            self.b[i] = 1

    def device_conditions(self, input_data: InputData, net: Network):
        """
        Prepare equality constraints for devices. Any device has only 1
        outgoing links to station.
        """
        self.device_conditions_array(input_data, net)

        self.device_conditions_b(input_data)

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
                value = input_data.device[j]["intensity"]
            else:
                var = "x"
                value = 1
            _var_name = [var + str(int(j)) + "_" + str(i)]
            _col = np.where(np.in1d(self.var.name, _var_name))
            self.data.iloc[data_row, _col] = value

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
            self.data.iloc[i, _column] = -1
            self.b[i] = 0

    def create(self,
               input_data: InputData,
               net: Network) -> None:
        """
        Prepare equality constraints
        Parameters
        ----------
        input_data: gateway, device, station
        net

        Returns
        -------
            eq : Constraints

        """

        # TODO: check number of row
        row_number = (len(input_data.gateway) +
                      len(input_data.device) +
                      len(input_data.station))

        data = np.zeros([row_number, len(self.column.name)]).astype(int)
        self.b = np.zeros(row_number)
        self.data = pd.DataFrame(data, columns=self.column.name)

        """ Preparation constraints for gateway, devices, and stations"""
        self.gateway_conditions(input_data, net)
        self.device_conditions(input_data, net)
        self.station_conditions(input_data, net)

        # deleting empty last rows
        _row = self.counter()
        self.data = self.data.head(_row)
        self.b = self.b[:_row]


class InequalityConstraints(Constraints):
    """ Matrix of inequality constraints"""

    def __init__(self,
                 input_data: InputData,
                 var_name: VarName,
                 col_name: VarName,
                 net: Network):
        super().__init__(var_name, col_name)
        self.create(input_data, net)

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
                value = input_data.device[j]["intensity"]
            else:
                var = "x"
                value = 1
            _var_name = [var + str(int(j)) + "_" + str(i)]
            _col = np.where(np.in1d(self.var.name, _var_name))
            self.data.iloc[data_row, _col] = value

    def get_station_limit_condition(self,
                                    i: int,
                                    data_row: int,
                                    input_data: InputData):
        """ Traffic is limited by intensity of station service time"""
        _column = np.where(np.in1d(self.var.name, f"y{i}"))
        self.data.iloc[data_row, _column] = (
                -1 * input_data.station[i]["intensity"]
        )

    def to_place_only_one_station_condition(self,
                                            input_data: InputData):
        """In each point coordinate must be only one placed station"""
        for k in range(0, len(input_data.station), len(input_data.type)):
            data_row = self.counter()
            y_name = [
                f"y{k + len(input_data.device) + 1 + j}"
                for j in range(len(input_data.type))]
            _col, = np.where(np.in1d(self.var.name, y_name))
            self.data.iloc[data_row, _col] = 1
            self.b[data_row] = 1

    def station_conditions(self, input_data, net) -> None:
        for i in input_data.station.keys():
            data_row = self.counter()
            self.get_links_from_device_to_sta(i, data_row, input_data, net)

            self.get_station_limit_condition(i, data_row, input_data)

        # TODO: check this condition
        # """ All traffic from sta is no more than intensity of station
        # service time"""
        # for i in input_data.station.keys():
        #     data_row = self.counter()
        #     _row, = np.where(net.adj_matrix[i, :] == 1)
        #     for j in _row:
        #         _var_name = [f"x{i}_{j}"]
        #         _col = np.where(np.in1d(self.var.name, _var_name))
        #         self.data.iloc[data_row, _col] = 1
        #
        #     _column = np.where(np.in1d(self.var.name, f"y{i}"))
        #     self.data.iloc[data_row, _column] = (
        #             -1 * input_data.station[i]["intensity"]
        #     )

        self.to_place_only_one_station_condition(input_data)

    def create(self, input_data, net) -> None:
        """
        Prepare inequality constraints
        Parameters
        ----------
        input_data: gateway, device, station
        net

        Returns
        -------
            eq : Constraints

        """

        # TODO: DANGER. rewrite 'row_number'
        row_number = 1000

        data = np.zeros([row_number, len(self.column.name)]).astype(int)
        self.b = np.zeros(row_number)
        self.data = pd.DataFrame(data, columns=self.column.name)
        self.station_conditions(input_data, net)

        # deleting empty last rows
        _row = self.counter()
        self.data = self.data.head(_row)
        self.b = self.b[:_row]


class MIP:
    """
    MIXED INTEGER PROGRAMMING OPTIMIZATION PROBLEM
    Here MIP model is prepared.
    Model consists :
        - objective function;
        - equality constraints with right value vector;
        - inequality constraints with right value vector;
    """
    def __init__(self):
        self.of = None
        self.eq_constraints = None
        self.ineq_constraints = None


def create_mipop(input_data: InputData, net: Network) -> MIP:
    """
    Create Mixed Integer Problem of Optimal Placement

    Parameters
    ----------
    input_data: include:
        - device parameter;
        - sta coordinates with each placed station;
        - gateway parameter.

    net: graph of feasible base station placement

    Returns
    -------
        MIPOP:
            - objective function;
            - equality constraints with right vector;
            - inequality constraints with right vector;

    """


    # MIP
    mipop = MIP()
    v_name, c_name = create_names(input_data, net.adj_matrix)
    var_name = VarName(**v_name)
    col_name = VarName(**c_name)

    mipop.of = OF(input_data, var_name, col_name)

    mipop.eq_constraints = EqualityConstraints(input_data, var_name,
                                               col_name, net)
    mipop.ineq_constraints = InequalityConstraints(input_data, var_name,
                                                   col_name, net)
    return mipop





