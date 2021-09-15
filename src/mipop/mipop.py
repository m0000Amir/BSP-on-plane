""" Mixed Integer Problem of Optimal Placement """
from __future__ import annotations
from typing import List, Tuple, Dict, TYPE_CHECKING, Any
if TYPE_CHECKING:
    from problem_solution import InputData
from itertools import product,  permutations


from src.net import Network
from src.myitertools import permutate

import numpy as np
import pandas as pd


class VarName:
    """ Names of problem variable"""
    def __init__(self, x: List[str] = None, y: List[str] = None) -> None:
        self.x = x
        self.y = y

    @property
    def all(self):
        return np.array(self.x + self.y)


class Matrix:
    """
    Matrix for object function, equality and inequality
    constraints.
    """
    def __init__(self, var_name: VarName, col_name: VarName):
        self.var_name = var_name
        self.col_name = col_name
        self.data = None


class OF(Matrix):
    """ Object function vector [1 x n]"""
    def __init__(self, var_name: VarName, col_name: VarName, nodes: Dict):
        super().__init__(var_name, col_name)
        self.lower_bounds = None
        self.upper_bounds = None
        self.int_constraints = None
        self._create(nodes)

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

    def _create(self, nodes: Dict) -> None:
        """
        Create objective function data, lower and upper bounds, and
        integer constraints

        Returns
        -------
            None

        """
        column = self.col_name.x + self.col_name.y
        data = np.zeros([1, len(column)]).astype(int)
        self.data = pd.DataFrame(data, columns=column)

        # Cost * y -> min
        y_col = np.where(np.in1d(self.data.columns.values,
                                 self.col_name.y))
        self.data.iloc[0, y_col] = [nodes['station'][i]['cost']
                                    for i in nodes['station'].keys()]

        # Bounds
        self.lower_bounds = np.zeros([1, len(column)]).astype(int)
        self.upper_bounds = np.ones([1, len(column)]).astype(int) * np.inf

        # TODO: change it
        self.int_constraints = self.get_index(self.col_name.y)
        self.upper_bounds[0, self.int_constraints] = 1


class Constraints(Matrix):
    """ Matrix of constraints"""
    def __init__(self, var_name: VarName, col_name: VarName,
                 adj_matrix: np.ndarray):
        super().__init__(var_name, col_name)
        self.b = None
        self.adj_matrix = adj_matrix


class EqualityConstraints(Constraints):
    """ Matrix of equality constraints"""
    def __init__(self, var_name: VarName, col_name: VarName,
                 nodes: Dict, adj_matrix: np.ndarray):
        super().__init__(var_name, col_name, adj_matrix)
        self._create(nodes)

    def _prepare_gateway_condition(self, nodes: Dict):
        """
        Prepare equality constraints for gateway

        Parameters
        ----------
        nodes - dict including gateway, devices, and stations

        Returns
        -------
            None
        """
        for i in list(nodes['gateway'].keys()):
            _row, = np.where(self.adj_matrix[:, i] == 1)
            _row_name = ['x' + str(_row[j]) + '_' +
                         str(i) for j in range(len(_row))]
            _col, = np.where(np.in1d(self.var_name.all, _row_name))
            self.data.iloc[i, _col] = 1
            self.b[i] = sum(self._common_limit[j] for j in list(self.net.o_p.keys()))
        pass

    def _create(self, nodes: Dict) -> None:
        """
        Create matrix and right vector of equality constraints

        Parameters
        ----------
        nodes - dict including gateway, devices, and stations

        Returns
        -------
            None
        """
        # TODO: check number of row
        row_number = (len(nodes['gateway']) +
                      len(nodes['device']) +
                      len(nodes['station']))
        column = self.col_name.x + self.col_name.y
        data = np.zeros([row_number, len(column)]).astype(int)
        self.b = np.zeros(row_number)
        self.data = pd.DataFrame(data, columns=column)

        self._prepare_gateway_condition(nodes)

        pass


class InequalityConstraints(Constraints):
    """ Matrix of inequality constraints"""
    def __init__(self, var_name: VarName, col_name: VarName):
        super().__init__(var_name, col_name)
        pass


class MIPOP(Network):
    """
    MIXED INTEGER PROGRAMMING OPTIMIZATION PROBLEM
    Here MIP model is prepared.
    Model consists :
        - input data;
        - prepared matrix:
            1 objective function;
            2 equality constraints with right value vector;
            3 inequality constraints with right value vector;
    """
    def __init__(self, input_data: InputData):
        super().__init__(input_data)
        self.of = None
        self.eq_constraints = None
        self.ineq_constraints = None
        self._create_matrix()

    @staticmethod
    def _create_edge_var_name(name: str, edge_name: List[Tuple[Any]],
                              sep: str = '_'):
        return [name + sep.join(map(str, edge_name[i]))
                for i in range(len(edge_name))]

    def _get_variable_name(self) -> Dict:
        """
        Get variable name of the problem
        Returns
        -------
            Dict of variable names
        """
        var_edge_name = (
                list(product(self.device.keys(), self.station.keys())) +
                list(permutations(self.station.keys(), 2)) +
                list(product(self.station.keys(), self.gateway.keys())))
        var_x = self._create_edge_var_name('x', var_edge_name)
        var_y = ['y' + str(i) for i in self.station.keys()]
        return {'x': var_x, 'y': var_y}

    def _get_column_name(self) -> Dict:
        point_count = int(len(self.station) / len(self.type))
        station_point = [list(self.station.keys())[0] + i
                         for i in range(point_count)]

        _sp = list(product(station_point,
                           list(map(lambda x: x + 1, self.type.keys()))))

        _coordinate_n_sta = [f'c{_[0]}_s{_[1]}' for _ in _sp]
        col_edge_name = list(product(self.device.keys(), _coordinate_n_sta))
        # TODO: delete permutate
        # aa = list(permutate(_coordinate_n_sta, 2))
        aa = list(permutations(station_point, 2))
        var_edge_name = (
                list(product(self.device.keys(), _coordinate_n_sta)) +
                list(permutations(_coordinate_n_sta, 2)) +
                list(product(_coordinate_n_sta, self.gateway.keys())))

        # TODO: delete these lists
        a = list(product(self.device.keys(), _coordinate_n_sta))
        b = list(permutations(_coordinate_n_sta, 2))
        c = list(product(_coordinate_n_sta, self.gateway.keys()))
        #

        col_x = self._create_edge_var_name('d', col_edge_name, sep='->')

        col_y = _coordinate_n_sta

        return {'x': col_x, 'y': col_y}

    def _create_names(self) -> Tuple[Dict[str], Dict[str]]:
        """ Create variable and column name"""
        variable_name = self._get_variable_name()
        column_name = self._get_column_name()

        # TODO: delete this permutations
        b = list(permutations(self.station.keys(), 2))

        # TODO: rewrite for column name

        return variable_name, column_name

    def _create_matrix(self):
        """ Main class method. It return MIP model matrices."""
        nodes = {'gateway': self.gateway,
                 'device': self.device,
                 'station': self.station}
        v_name, c_name = self._create_names()
        var_name = VarName(**v_name)
        col_name = VarName(**c_name)

        self.of = OF(var_name, col_name, nodes)
        self.eq_constraints = EqualityConstraints(var_name, col_name,
                                                  nodes, self.adjacency_matrix)
        self.ineq_constraints = InequalityConstraints(var_name)

        pass




