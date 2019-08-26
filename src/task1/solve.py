from problem.input1 import gate, obj, station, sta_type
from src.network import BSS
from src.draw import draw_input_data, draw_lp_graph

from itertools import product
from itertools import permutations

from scipy.optimize import linprog
import pandas as pd
import numpy as np


class OP:
    """Optimization problem"""
    def __init__(self, network):
        self.net = network
        self.adj_mat = network.adj_matrix.toarray()

        self.g_lim = gate['lim']
        self.o_lim = obj['lim']
        self.limit = None

        self._lim = [sta_type[i + 1]['limit']
                     for i in range(len(sta_type))]
        self._l = None

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
        g_k = ''.join(map(str, list(self.net.g_p.keys())))
        o_k = ''.join(map(str, list(self.net.o_p.keys())))
        s_k = ''.join(map(str, list(self.net.s_p.keys())))

        o_s = [i for i in product(o_k, s_k)]
        s_s = [i for i in permutations(s_k, 2)]
        s_g = [i for i in product(s_k, g_k)]

        o_s_name = self.value_name('x', o_s)
        s_s_name = self.value_name('x', s_s)
        s_g_name = self.value_name('x', s_g)

        return o_s_name + s_s_name + s_g_name

    def create_value(self, w_num):
        x = self.create_edge()
        w = ['w' + str(i) for i in range(w_num)]

        return [x, w]

    def make_objective(self, x, w):
        """
        make objective function
        :param x: name of x parameter vector
        :param w: name of w parameter vector
        :return: self.f
        """
        col = x + w
        data = np.zeros([1, len(col)]).astype(int)
        self.f = pd.DataFrame(data, columns=col)
        column, = np.where(np.in1d(self.f.columns.values, w))

        # Objective function consist on only w values
        self.f.iloc[0, column] = 1

        self.lower_bounds = np.zeros([1, len(col)]).astype(int)
        self.upper_bounds = np.ones([1, len(col)]).astype(int) * np.inf

    def make_for_g(self, i):
        adj_mat_r, = np.where(self.adj_mat[:, i] == 1)
        adj_mat_r_name = ['x' + str(adj_mat_r[j]) + '_' +
                          str(i) for j in range(len(adj_mat_r))]

        column, = np.where(np.in1d(self.eq_array.columns.values,
                                   adj_mat_r_name))
        self.eq_array.iloc[i, column] = 1
        self.eq_array.loc[i, 'w' + str(i)] = 1
        self.eq_b[i] = sum(self._l[j] for j in list(self.net.o_p.keys()))

    def make_for_o(self, i):
        adj_mat_c, = np.where(self.adj_mat[i, :] == 1)
        adg_mat_c_name = ['x' + str(i) + '_' +
                          str(adj_mat_c[j]) for j in range(len(adj_mat_c))]

        column, = np.where(np.in1d(self.eq_array.columns.values,
                                   adg_mat_c_name))
        self.eq_array.iloc[i, column] = 1
        self.eq_array.loc[i, 'w' + str(i)] = 1
        self.eq_b[i] = self._l[i]

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

    def make_equality(self, row, x, w):
        data_eq = np.zeros([row, len(x + w)]).astype(int)
        self.eq_b = np.zeros(row)
        self.eq_array = pd.DataFrame(data_eq, columns=x+w)

        for i in range(row + 1):
            if i in list(self.net.g_p.keys()):
                self.make_for_g(i)

            if i in list(self.net.o_p.keys()):
                self.make_for_o(i)

            if i in list(self.net.s_p.keys()):
                self.make_for_s(i)

    def make_inequality(self, row, x, w):
        data_ineq = np.zeros([row, len(x + w)]).astype(int)
        self.ineq_b = np.zeros(row)
        self.ineq_array = pd.DataFrame(data_ineq, columns=x + w)
        for i in list(self.net.s_p.keys()):
            self.add_input_edge_s(i, self.ineq_array)
            self.ineq_b[i] = self._l[i]

    def create_matrix(self):
        """
        Input matrices of task 1

        :return: equality matrix, linear equality constraint vector;
         inequality matrix, linear inequality constraint vector;
         upper bounds vector; lower bounds vector
        """
        row_num = (len(self.net.g_p) + len(self.net.o_p) + len(self.net.s_p))

        [x_name, w_name] = self.create_value(row_num)

        self.make_objective(x_name, w_name)

        _s_key = list(self.net.s_p.keys())
        # limit
        _lim = list(j for i in [[k] * len(self.net.s_p)
                                for k in self._lim] for j in i)
        self.limit = {k + _s_key[0]: value
                      for k, value in enumerate(_lim)}
        self._l = {**self.g_lim, **self.o_lim, **self.limit}

        self.make_equality(row_num, x_name, w_name)
        self.make_inequality(row_num, x_name, w_name)


def solve_lp_problem(obj_func, ineq_array, ineq_b, eq_array, eq_b, lb, ub):
    """
    Simplex Method solution
    :param obj_func: objective function (f = 0, feasible solution)
    :param ineq_array: inequality matrix
    :param ineq_b: linear inequality constraint vector
    :param eq_array: equality matrix
    :param eq_b: linear equality constraint vector
    :param lb: lower bound
    :param ub: upper bound
    :return: result
    """
    b_array = np.vstack([lb, ub])
    minmax_bounds = tuple((b_array[0, i], b_array[1, i])
                          for i in range(len(b_array[0])))

    res = linprog(obj_func, A_ub=ineq_array, b_ub=ineq_b,
                  A_eq=eq_array, b_eq=eq_b, bounds=minmax_bounds,
                  method='simplex', callback=None,
                  options={'disp': True})
    assert round(res.fun) == 0, \
        ('There is no solution because the '
         'objective function value of linear '
         'programing problem is not zero')
    return res


draw_input_data(gate, obj, station)
net = BSS(gate, obj, station, sta_type)
net.create()

problem = OP(net)
problem.create_matrix()
draw_lp_graph(net)

res = solve_lp_problem(problem.f.values,
                       problem.ineq_array.values,
                       problem.ineq_b,
                       problem.eq_array.values,
                       problem.eq_b,
                       problem.lower_bounds,
                       problem.upper_bounds)

solution = pd.Series(res.x, index=problem.eq_array.columns.values)
draw_lp_graph(net)

debug = 'stop'
