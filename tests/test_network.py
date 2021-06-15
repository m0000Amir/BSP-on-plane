from problem.lppfs_input import gate, obj, sta, sta_set
from src.network import BSS

net = BSS(gate, obj, sta, sta_set)
net.create()


def test_adj_mat():
    """ check adj matrix """
    assert net.adj_matrix is not None

