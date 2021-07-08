""" Mixed Integer Problem of Optimal Placement """
from typing import List, Tuple, Dict


from src.net import Network


import numpy as np
import pandas as pd


# class VarName1:
#     def __init__(self, z: List[str] = None,
#                  x: List[str] = None,
#                  y: List[str] = None,
#                  w: List[str] = None) -> None:
#         self.z = z
#         self.x = x
#         self.y = y
#         self.w = w

class VarName:
    """ Names of problem variable"""
    def __init__(self,
                 x: List[str] = None,
                 y: List[str] = None) -> None:
        self.x = x
        self.y = y


class Matrix:
    """
    Matrix for object function, equality and inequality
    constraints.
    """
    def __init__(self, var_name: VarName):
        self.var_name = var_name
        self.data = None


class OF(Matrix):
    """ Object function vector [1 x n]"""
    def __init__(self, var_name: VarName, nodes: Dict):
        super().__init__(var_name)
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

        Parameters
        ----------
        nodes

        Returns
        -------
            None

        """
        column = self.var_name.x + self.var_name.y
        data = np.zeros([1, len(column)]).astype(int)
        self.data = pd.DataFrame(data, columns=column)

        # Cost * y -> min
        y_col = np.where(np.in1d(self.data.columns.values,
                                 self.var_name.y))
        self.data.iloc[0, y_col] = [nodes['station'][i]['cost']
                                    for i in nodes['station'].keys()]

        # Bounds
        self.lower_bounds = np.zeros([1, len(column)]).astype(int)
        self.upper_bounds = np.ones([1, len(column)]).astype(int) * np.inf

        # TODO: change it
        self.int_constraints = self.get_index(self.var_name.y)
        self.upper_bounds[0, self.int_constraints] = 1


class Constraints(Matrix):
    """ Matrix of constraints"""
    def __init__(self, var_name: VarName):
        super().__init__(var_name)
        self.b = None


class EqualityConstraints(Constraints):
    """ Matrix of equality constraints"""
    def __init__(self, var_name: VarName, nodes: Dict):
        super().__init__(var_name)
        self._create(nodes)

    def _create(self, nodes: Dict) -> None:
        # TODO: check number of row
        row_number = (len(nodes['gateway']) +
                      len(nodes['device']) +
                      len(nodes['station']))
        column = self.var_name.x + self.var_name.y
        data = np.zeros([row_number, len(column)]).astype(int)
        self.b = np.zeros(row_number)
        self.data = pd.DataFrame(data, columns=column)


        a = 1


class InequalityConstraints(Constraints):
    """ Matrix of inequality constraints"""
    def __init__(self, var_name: VarName):
        super().__init__(var_name)


class MIPOP:
    def __init__(self, net: Network):
        self.of = None
        self.eq_c = None
        self.ineq_c = None
        self._create_matrix(net)

    @staticmethod
    def _create_edge_var_name(name: str, edge_name: List[Tuple[float, float]]):
        return [name + '_'.join(map(str, edge_name[i]))
                for i in range(len(edge_name))]

    # def _create_matrix_var_name(self, net):
    def _create_matrix(self, net):
        nodes = {'gateway': net.gateway,
                 'device': net.device,
                 'station': net.station}

        x = self._create_edge_var_name('x', (net.get_device2station_edge +
                                             net.get_station2station_edge +
                                             net.get_station2gateway_edge))

        z = self._create_edge_var_name('z', net.get_device2station_edge)
        w = ['w' + str(i) for i in range(20)]
        y = ['y' + str(i) for i in net.station.keys()]
        # var_name = VarName1(z, x, y, w)
        var_name = VarName(x, y)

        self.of = OF(var_name, nodes)
        self.eq_c = EqualityConstraints(var_name, nodes)
        self.ineq_c = InequalityConstraints(var_name)

        pass




