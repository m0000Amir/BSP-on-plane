"""
Mixed-integer linear programming problem feasible solution
"""
from itertools import product
from itertools import permutations

from problem.milppfs_input import gate, obj, sta, sta_set
from src.network import BSS
from src.draw import draw_input_data, draw_milp_graph
from src.matlab.milp_problem import solve

import pandas as pd
import numpy as np


class MILPPFS:
    """ Mixed-integer linear programming problem feasible solution"""
    def __init__(self, network):
        self.net = network
        self.adj_mat = network.adj_matrix.toarray()

        self.g_lim = gate['lim']
        self.o_lim = obj['lim']
        self.limit = None

        self._lim = [sta_set[i + 1]['limit']
                     for i in range(len(sta_set))]
        self._common_limit = None
        self._y_index = None

        self.f = None
        self.int_constraints = None
        self.lower_bounds = None
        self.upper_bounds = None
        self.eq_array = None
        self.eq_b = None
        self.ineq_array = None
        self.ineq_b = None

    @staticmethod
    def value_name(name, edge_name):
        return [name + '_'.join(map(str, edge_name[i]))
                for i in range(len(edge_name))]

    def create_edge(self):
        # g_k = ''.join(map(str, list(self.net.g_p.keys())))
        # o_k = ''.join(map(str, list(self.net.o_p.keys())))
        # s_k = ''.join(map(str, list(self.net.s_p.keys())))
        g_k = list(map(str, self.net.g_p.keys()))
        o_k = list(map(str, self.net.o_p.keys()))
        s_k = list(map(str, self.net.s_p.keys()))

        o_s = [i for i in product(o_k, s_k)]
        s_s = [i for i in permutations(s_k, 2)]
        s_g = [i for i in product(s_k, g_k)]

        o_s_name = self.value_name('x', o_s)
        s_s_name = self.value_name('x', s_s)
        s_g_name = self.value_name('x', s_g)

        return o_s_name + s_s_name + s_g_name

    def create_value(self, w_num):
        x = self.create_edge()
        y = ['y' + str(i) for i in self.net.s_p.keys()]
        w = ['w' + str(i) for i in range(w_num)]

        return [x, y, w]

    def make_objective(self, x, y, w):
        """
        make objective function
        :param x: name of edge parameter vector
        :param y: name of bool parameter vector
        :param w: name of bool parameter vector
        :return: self.f
        """
        col = x + y + w
        data = np.zeros([1, len(col)]).astype(int)
        self.f = pd.DataFrame(data, columns=col)
        column, = np.where(np.in1d(self.f.columns.values, w))

        # Objective function consist on only w values
        self.f.iloc[0, column] = 1

        self.lower_bounds = np.zeros([1, len(col)]).astype(int)
        self.upper_bounds = np.ones([1, len(col)]).astype(int) * np.inf

        self._y_index, = np.where(np.in1d(self.f.columns.values, y))
        self.upper_bounds[0, self._y_index] = 1
        # because index start from 1 not 0 in Matlab Optimization Toolbox
        self.int_constraints = [i + 1 for i in self._y_index.tolist()]

    def make_for_g(self, i):
        adj_mat_r, = np.where(self.adj_mat[:, i] == 1)
        adj_mat_r_name = ['x' + str(adj_mat_r[j]) + '_' +
                          str(i) for j in range(len(adj_mat_r))]

        column, = np.where(np.in1d(self.eq_array.columns.values,
                                   adj_mat_r_name))
        self.eq_array.iloc[i, column] = 1
        self.eq_array.loc[i, 'w' + str(i)] = 1
        self.eq_b[i] = sum(self._common_limit[j]
                           for j in list(self.net.o_p.keys()))

    def make_for_o(self, i):
        adj_mat_c, = np.where(self.adj_mat[i, :] == 1)
        adg_mat_c_name = ['x' + str(i) + '_' +
                          str(adj_mat_c[j]) for j in range(len(adj_mat_c))]

        column, = np.where(np.in1d(self.eq_array.columns.values,
                                   adg_mat_c_name))
        self.eq_array.iloc[i, column] = 1
        self.eq_array.loc[i, 'w' + str(i)] = 1
        self.eq_b[i] = self._common_limit[i]

    def add_input_edge_s(self, i, array):
        row_mat, = np.where(self.adj_mat[:, i] == 1)
        mat_name_plus = ['x' + str(row_mat[j]) + '_' + str(i)
                         for j in range(len(row_mat))]

        column_plus, = np.where(np.in1d(array.columns.values,
                                        mat_name_plus))
        array.iloc[i, column_plus] = 1

    def make_for_s(self, i):

        self.add_input_edge_s(i, self.eq_array)

        col_mat, = np.where(self.adj_mat[i, :] == 1)
        mat_name_minus = ['x' + str(i) + '_' + str(col_mat[j])
                          for j in range(len(col_mat))]
        column_minus, = np.where(np.in1d(self.eq_array.columns.values,
                                         mat_name_minus))
        self.eq_array.iloc[i, column_minus] = -1
        self.eq_array.loc[i, 'w' + str(i)] = 1
        self.eq_b[i] = 0

    def make_equality(self, row, x, y, w):
        data_eq = np.zeros([row + 1, len(x + y + w)]).astype(int)
        self.eq_b = np.zeros(row + 1)
        self.eq_array = pd.DataFrame(data_eq, columns=x+y+w)

        for i in range(row + 1):
            if i in list(self.net.g_p.keys()):
                self.make_for_g(i)

            if i in list(self.net.o_p.keys()):
                self.make_for_o(i)

            if i in list(self.net.s_p.keys()):
                self.make_for_s(i)
            # add condition, that len(placed station) == m.
            if i == row:
                self.eq_array.iloc[i, self._y_index] = 1
                self.eq_b[i] = len(self._lim)

    def add_y_condition(self, row1, y):
        """

        :param row1:condition columns that a station of the same type can be
        used only once. After row2: columns of the condition that only one
        station can be located at the location
        :param y: y name
        :return:
        """
        _s_p_num = int(len(self.net.s_p) / len(self._lim))
        # ai ∈ A2D
        for i in range(0, len(self._lim)):
            y_1 = [y[j+i*_s_p_num] for j in range(0, _s_p_num)]
            column, = np.where(np.in1d(self.ineq_array.columns.values,y_1))
            self.ineq_array.iloc[row1 + i, column] = 1
            self.ineq_b[row1 + i] = 1
        # ai ∈ Dj
        row2 = row1 + i
        for k in range(0, _s_p_num):
            y_2 = [y[k+j*_s_p_num] for j in range(0, len(self._lim))]
            column, = np.where(np.in1d(self.ineq_array.columns.values, y_2))
            self.ineq_array.iloc[row2+k+1, column] = 1
            self.ineq_b[row2+k+1] = 1

    def make_inequality(self, row, x, y, w):
        ineq_row = (row + len(self._lim) +
                    int(len(self.net.s_p) / len(self._lim)))
        data_ineq = np.zeros([ineq_row, len(x + y + w)]).astype(int)
        self.ineq_b = np.zeros(ineq_row)
        self.ineq_array = pd.DataFrame(data_ineq, columns=x+y+w)
        for i in list(self.net.s_p.keys()):
            self.add_input_edge_s(i, self.ineq_array)
            coef = -1 * self._common_limit[i]
            column, = np.where(np.in1d(self.ineq_array.columns.values,
                                       'y' + str(i)))
            self.ineq_array.iloc[i, column] = coef
            # self.ineq_b[i] = self._common_limit[i]
        self.add_y_condition(row, y)

    def create_matrix(self):
        """
        Input matrices of task 1

        :return: equality matrix, linear equality constraint vector;
         inequality matrix, linear inequality constraint vector;
         upper bounds vector; lower bounds vector
        """
        row_num = (len(self.net.g_p) + len(self.net.o_p) + len(self.net.s_p))

        [x_name, y_name, w_name] = self.create_value(row_num)

        self.make_objective(x_name, y_name, w_name)

        _s_key = list(self.net.s_p.keys())
        # limit
        _lim = list(j for i in [[k] * int(len(self.net.s_p)/len(self._lim))
                                for k in self._lim] for j in i)
        self.limit = {k + _s_key[0]: value
                      for k, value in enumerate(_lim)}
        self._common_limit = {**self.g_lim, **self.o_lim, **self.limit}

        self.make_equality(row_num, x_name, y_name, w_name)
        self.make_inequality(row_num, x_name, y_name, w_name)

    def get_solution_col_name(self):
        row_num = (len(self.net.g_p) + len(self.net.o_p) + len(self.net.s_p))
        [_, y_name, _] = self.create_value(row_num)

        _s_p_num = int(len(self.net.s_p) / len(self._lim))

        _s_key = list(self.net.s_p.keys())
        name = ['y' + str(_s_key[0]+j) + '_s_' + str(i+1)
                for i in range(0, len(self._lim))
                for j in range(0, _s_p_num)]
        column, = np.where(np.in1d(self.f.columns.values, y_name))
        self.f.columns.values[column] = name
        return name


def milppfs_solver():
    """

    :return: milppfs solution
    """
    draw_input_data(gate, obj, sta)
    net = BSS(gate, obj, sta, sta_set)
    net.create()
    problem = MILPPFS(net)
    problem.create_matrix()
    y_solution = problem.get_solution_col_name()

    x = solve(problem.f.values,
              problem.int_constraints,
              problem.ineq_array.values,
              problem.ineq_b,
              problem.eq_array.values,
              problem.eq_b,
              problem.lower_bounds,
              problem.upper_bounds,
              option='feasible_solution')
    solution = pd.Series(x, index=problem.f.columns.values).T
    placed_station = solution[y_solution].values
    placed_station.tolist()
    draw_milp_graph(net, placed_station, y_solution)
    return solution