""" Mixed Integer Problem of Optimal Placement """
from __future__ import annotations
from typing import List, Tuple, Dict, TYPE_CHECKING, Any
if TYPE_CHECKING:
    from problem_solution import InputData
from itertools import product,  permutations


from src.net import Network
from src.mipop.varnames import create_names

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

    # @property
    # def all(self):
    #     return np.array(self.x + self.y)


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
    def __init__(self, var: VarName, column: VarName):
        super().__init__(var, column)
        self.lower_bounds = None
        self.upper_bounds = None
        self.int_constraints = None
        # self._create(nodes)

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
        # column = self.col_name.x + self.col_name.y
        data = np.zeros([1, len(self.column.name)]).astype(int)
        self.data = pd.DataFrame(data, columns=self.column.name)

        # Cost * y -> min
        y_col = np.where(np.in1d(self.data.columns.values,
                                 self.column.y))
        self.data.iloc[0, y_col] = [nodes['station'][i]['cost']
                                    for i in nodes['station'].keys()]

        # Bounds
        self.lower_bounds = np.zeros([1, len(self.column.name)]).astype(int)
        self.upper_bounds = np.ones([1, len(self.column.name)]).astype(int) * np.inf

        # TODO: change it
        self.int_constraints = self.get_index(self.column.y)
        self.upper_bounds[0, self.int_constraints] = 1


# class Constraints(Matrix):
#     """ Matrix of constraints"""
#     def __init__(self, var: VarName, column: VarName,
#                  adj_matrix: np.ndarray):
#         super().__init__(var, column)
#         self.b = None
#         self.adj_matrix = adj_matrix


# class EqualityConstraints(Constraints):
#     """ Matrix of equality constraints"""
#     def __init__(self, var: VarName, column: VarName,
#                  nodes: Dict, adj_matrix: np.ndarray):
#         super().__init__(var, column, adj_matrix)
#         self._create(nodes)

class Constraints(Matrix):
    """ Matrix of constraints"""
    def __init__(self, var: VarName, column: VarName):
        super().__init__(var, column)
        self.b = None
        self._count = 0
        # self.adj_matrix = adj_matrix

    def counter(self) -> int:
        count = self._count
        self._count += 1
        return count


class EqualityConstraints(Constraints):
    """ Matrix of equality constraints"""
    def __init__(self,
                 var: VarName,
                 column: VarName,
                 nodes: Dict, adj_matrix: np.ndarray):
        super().__init__(var, column)
        self._create(nodes)

    def _prepare_gateway_equality_condition(self, nodes: Dict) -> None:
        """
        Prepare equality constraints for gateway.
        Through the stations, all information flow from devices must be
        available to the gateway.

        Parameters
        ----------
        nodes - dict including gateway, devices, and stations

        Returns
        -------
            None
        """
        for i in nodes['gateway'].keys():
            _row, = np.where(self.adj_matrix[:, i] == 1)
            _row_name = ['x' + str(_row[j]) + '_' +
                         str(i) for j in range(len(_row))]
            _col, = np.where(np.in1d(self.var.name, _row_name))
            self.data.iloc[i, _col] = 1
            self.b[i] = sum(nodes["device"][i]["intensity"]
                            for i in nodes["device"].keys())

    def _prepare_device_equality_condition(self, nodes: Dict) -> None:
        """
        Prepare equality constraints for device.

        """
        for i in nodes['device'].keys():
            _row, = np.where(self.adj_matrix[i, :] == 1)
            a = _row.tolist()
            b = [j for j in _row.tolist()]
            _row_name = ['z' + str(i) + '_' + str(j)
                         for j in _row.tolist()]
            _col, = np.where(np.in1d(self.var.name, _row_name))
            self.data.iloc[i, _col] = 1
            self.b[i] = 1

    def _add_sta_input_link(self, i: int, nodes: Dict) -> None:
        """
        All station has incoming links from devices and other stations.
        Using adjacency matrix, we add all input edges
        """
        _row, = np.where(self.adj_matrix[:, i] == 1)
        for j in _row:
            if int(j) in nodes["device"].keys():
                var = "z"
                value = nodes["device"][j]["intensity"]
            else:
                var = "x"
                value = 1
            _var_name = [var + str(int(j)) + "_" + str(i)]
            _col = np.where(np.in1d(self.var.name, _var_name))
            self.data.iloc[i, _col] = value
            # TODO: delete it
            debug = 1

    def _add_sta_output_link(self, i: int, nodes: Dict) -> None:
        """
        All station has outgoing links from devices and other stations.
        Using adjacency matrix, we add all output edges
        """
        _col, = np.where(self.adj_matrix[i, :] == 1)
        _var_name = [f"x{i}_{_col[j]}" for j in range(len(_col))]
        _column, = np.where(np.in1d(self.var.name, _var_name))
        self.data.iloc[i, _column] = -1
        self.b[i] = 0
        debug = 1

    def _prepare_sta_equality_condition(self, nodes: Dict):
        for i in nodes["station"].keys():
            """ Incoming links for station 'S_j'"""
            self._add_sta_input_link(i, nodes)
            """ Outgoing links for station 'S_j' """
            self._add_sta_output_link(i, nodes)

        debug = 1

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
        # column = self.column.z + self.column.x + self.column.y
        data = np.zeros([row_number, len(self.column.name)]).astype(int)
        self.b = np.zeros(row_number)
        self.data = pd.DataFrame(data, columns=self.column.name)

        self._prepare_gateway_equality_condition(nodes)
        self._prepare_device_equality_condition(nodes)
        self._prepare_sta_equality_condition(nodes)

        a  = 1


class InequalityConstraints(Constraints):
    """ Matrix of inequality constraints"""

    def __init__(self, var: VarName, column: VarName,
                 nodes: Dict, adj_matrix: np.ndarray):
        super().__init__(var, column, adj_matrix)
        self._count = 0
        self._create(nodes)

    def counter(self) -> int:
        count = self._count
        self._count += 1
        return count

    def _add_sta_input_link(self, i: int, nodes: Dict) -> None:
        """
        All station has incoming links from devices and other stations.
        Using adjacency matrix, we add all input edges
        """
        _row, = np.where(self.adj_matrix[:, i] == 1)
        for j in _row:
            if int(j) in nodes["device"].keys():
                var = "z"
                value = nodes["device"][j]["intensity"]
            else:
                var = "x"
                value = 1
            _var_name = [var + str(int(j)) + "_" + str(i)]
            _col = np.where(np.in1d(self.var.name, _var_name))
            self.data.iloc[i, _col] = value

    def _prepare_sta_inequality_condition(self, nodes: Dict):
        for i in nodes["station"].keys():
            data_row = self.counter()
            self._add_sta_input_link(data_row, nodes)
            _column = np.where(np.in1d(self.var.name, f"y{i}"))
            self.data.iloc[data_row, _column] = (
                    -1 * nodes["station"][i]["intensity"]
            )

    def _create(self, nodes: Dict) -> None:
        """
        Create matrix and right vector of inequality constraints

        Parameters
        ----------
        nodes - dict including gateway, devices, and stations

        Returns
        -------
            None
        """
        # TODO: DANGER. rewrite 'row_number'
        row_number = 1000
        self.b = np.zeros(row_number)
        data = np.zeros([row_number, len(self.column.name)]).astype(int)
        self.data = pd.DataFrame(data, columns=self.column.name)
        self._prepare_sta_inequality_condition(nodes)



        debug = 1


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
    def _create_edge_var_name(name: str, edge_name: List[Tuple[Any, ...]],
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
        # var_edge_name = (
        #         list(product(self.device.keys(), self.station.keys())) +
        #         list(permutations(self.station.keys(), 2)) +
        #         list(product(self.station.keys(), self.gateway.keys())))
        edge_z = list(product(self.device.keys(), self.station.keys()))
        edge_x = (list(permutations(self.station.keys(), 2)) +
                  list(product(self.station.keys(), self.gateway.keys())))
        var_z = self._create_edge_var_name('z', edge_z)
        var_x = self._create_edge_var_name('x', edge_x)

        var_y = ['y' + str(i) for i in self.station.keys()]
        return {'z': var_z, 'x': var_x, 'y': var_y}

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
        # aa = list(permutations(station_point, 2))
        # var_edge_name = (
        #         list(product(self.device.keys(), _coordinate_n_sta)) +
        #         list(permutations(_coordinate_n_sta, 2)) +
        #         list(product(_coordinate_n_sta, self.gateway.keys())))

        # TODO: delete these lists
        device2sta = self._create_edge_var_name(
            name='d',
            edge_name=list(product(self.device.keys(), _coordinate_n_sta)),
            sep='->')
        sta2sta = self._create_edge_var_name(
            name='',
            edge_name=list(permutations(_coordinate_n_sta, 2)),
            sep='->')
        sta2gtw = self._create_edge_var_name(
            name='',
            edge_name=list(product(_coordinate_n_sta, self.gateway.keys())),
            sep='->')
        # var_edge_name = (device2sta + sta2sta + sta2gtw)

        # a = list(product(self.device.keys(), _coordinate_n_sta))
        # b = list(permutations(_coordinate_n_sta, 2))
        # c = list(product(_coordinate_n_sta, self.gateway.keys()))
        #

        # col_x = self._create_edge_var_name('d', col_edge_name, sep='->')
        # col_x = self._create_edge_var_name('d', var_edge_name, sep='->')

        # col_y = _coordinate_n_sta

        return {'z': device2sta,
                'x': (sta2sta + sta2gtw),
                'y': _coordinate_n_sta}

    def _create_names(self) -> Tuple[Dict[str], Dict[str]]:
        """ Create variable and column name"""
        variable_name = self._get_variable_name()
        column_name = self._get_column_name()

        # # TODO: delete this permutations
        # b = list(permutations(self.station.keys(), 2))
        #
        # # TODO: rewrite for column name

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
                                                  nodes, self.adj_matrix)
        self.ineq_constraints = InequalityConstraints(var_name,
                                                      col_name,
                                                      nodes,
                                                      self.adj_matrix)

        pass


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


def create_of(input_data: InputData,
              var_name: VarName,
              col_name: VarName) -> OF:
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
        objective function: OF
    """
    of = OF(var_name, col_name)
    data = np.zeros([1, len(of.column.name)]).astype(int)
    of.data = pd.DataFrame(data, columns=of.column.name)
    # Cost * y -> min
    y_col = np.where(np.in1d(of.data.columns.values,
                             of.column.y))
    of.data.iloc[0, y_col] = [input_data.station[i]['cost']
                              for i in input_data.station.keys()]
    # Bounds
    of.lower_bounds = np.zeros([1, len(of.column.name)]).astype(int)
    of.upper_bounds = np.ones([1, len(of.column.name)]).astype(int) * np.inf

    of.int_constraints = np.where(np.in1d(of.data.columns.values,
                                          of.column.y))
    of.upper_bounds[0, of.int_constraints] = 1
    return of


def create_eq_constraints(input_data: InputData,
                          var_name: VarName,
                          col_name: VarName,
                          net: Network) -> Constraints:
    """
    Prepare equality constraints
    Parameters
    ----------
    input_data: gateway, device, station
    var_name
    col_name
    net

    Returns
    -------
        eq : Constraints

    """
    eq = Constraints(var_name, col_name)

    # TODO: check number of row
    row_number = (len(input_data.gateway) +
                  len(input_data.device) +
                  len(input_data.station))

    data = np.zeros([row_number, len(eq.column.name)]).astype(int)
    eq.b = np.zeros(row_number)
    eq.data = pd.DataFrame(data, columns=eq.column.name)

    """ 
    Prepare equality constraints for gateway. Through the stations, all 
    information flow from devices must be available to the gateway.
    """
    for i in input_data.gateway.keys():
        data_row = eq.counter()
        _row, = np.where(net.adj_matrix[:, i] == 1)
        _row_name = ['x' + str(_row[j]) + '_' +
                     str(i) for j in range(len(_row))]
        _col, = np.where(np.in1d(eq.var.name, _row_name))
        eq.data.iloc[data_row, _col] = 1
        eq.b[i] = sum(input_data.device[i]["intensity"]
                      for i in input_data.device.keys())

    """
        Prepare equality constraints for devices. Any device has only 1 outgoing 
        links to station.
    """
    for i in input_data.device.keys():
        data_row = eq.counter()
        _row, = np.where(net.adj_matrix[i, :] == 1)
        a = _row.tolist()
        b = [j for j in _row.tolist()]
        _row_name = ['z' + str(i) + '_' + str(j)
                     for j in _row.tolist()]
        _col, = np.where(np.in1d(eq.var.name, _row_name))
        eq.data.iloc[data_row, _col] = 1
        eq.b[i] = 1

    """
    Prepare equality constraints for stations. Traffic must be move through a 
    station.
    """

    for i in input_data.station.keys():
        """ 
        Incoming links for station 'S_j'
        All station has incoming links from devices and other stations.
        Using adjacency matrix, we add all input edges
        """
        data_row = eq.counter()
        _row, = np.where(net.adj_matrix[:, i] == 1)
        for j in _row:
            if int(j) in input_data.device.keys():
                var = "z"
                value = input_data.device[j]["intensity"]
            else:
                var = "x"
                value = 1
            _var_name = [var + str(int(j)) + "_" + str(i)]
            _col = np.where(np.in1d(eq.var.name, _var_name))
            eq.data.iloc[data_row, _col] = value
        """ 
        Outgoing links for station 'S_j' 
        All station has outgoing links from devices and other stations.
        Using adjacency matrix, we add all output edges
        """
        _col, = np.where(net.adj_matrix[i, :] == 1)
        _var_name = [f"x{i}_{_col[j]}" for j in range(len(_col))]
        _column, = np.where(np.in1d(eq.var.name, _var_name))
        eq.data.iloc[i, _column] = -1
        eq.b[i] = 0

    # delete empty last rows
    _row = eq.counter()
    eq.data = eq.data.head(_row)
    eq.b = eq.b[:_row]
    # eq.b = np.delete(eq.b, np.s_[-3:], axis=0)
    return eq


def create_ineq_constraints(input_data: InputData,
                            var_name: VarName,
                            col_name: VarName,
                            net: Network) -> Constraints:
    """
    Prepare inequality constraints
    Parameters
    ----------
    input_data: gateway, device, station
    var_name
    col_name
    net

    Returns
    -------
        eq : Constraints

    """
    ineq = Constraints(var_name, col_name)

    # TODO: DANGER. rewrite 'row_number'
    row_number = 1000

    data = np.zeros([row_number, len(ineq.column.name)]).astype(int)
    ineq.b = np.zeros(row_number)
    ineq.data = pd.DataFrame(data, columns=ineq.column.name)

    for i in input_data.station.keys():
        data_row = ineq.counter()
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
            _col = np.where(np.in1d(ineq.var.name, _var_name))
            ineq.data.iloc[data_row, _col] = value

        """ Traffic is limited by intensity of station service time"""
        _column = np.where(np.in1d(ineq.var.name, f"y{i}"))
        ineq.data.iloc[data_row, _column] = (
                -1 * input_data.station[i]["intensity"]
        )
        for k in range(0, len(input_data.type)):
            data_row = ineq.counter()
            _col, = np.where(np.in1d(ineq.data.columns.values, ineq.var.y))
            ineq.data.iloc[data_row, _col] = 1
            ineq.b[data_row] = 1

    # delete empty last rows
    _row = ineq.counter()
    ineq.data = ineq.data.head(_row)
    ineq.b = ineq.b[:_row]
    return ineq


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
    v_name, c_name = create_names(input_data)
    var_name = VarName(**v_name)
    col_name = VarName(**c_name)

    mipop.of = create_of(input_data, var_name, col_name)

    mipop.eq_constraints = create_eq_constraints(input_data, var_name,
                                                 col_name, net)
    mipop.ineq_constraints = create_ineq_constraints(input_data, var_name,
                                                     col_name, net)

    return mipop





