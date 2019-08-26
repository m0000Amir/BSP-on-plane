import networkx as nx
import matplotlib.pyplot as plt
import itertools


def get_coordinates(position):
    point = position.values()
    x, y = zip(*point)
    return x, y


def draw_input_data(gate, obj, station):
    gtw_pos = gate['pos']
    obj_pos = obj['pos']
    sta_pos = {k + len(obj_pos): value
               for k, value in enumerate(station['pos'].values())}

    plt.close()
    fig = plt.gcf()
    ax = fig.gca()
    g_x, g_y = get_coordinates(gtw_pos)
    plt.plot(g_x, g_y, color='r', marker='s', markersize=20, linestyle='')
    [plt.annotate(i, xy=gtw_pos[i], xytext=gtw_pos[i], ha='center', va='center',
                  color='w') for i in gtw_pos]

    o_x, o_y = get_coordinates(obj_pos)
    plt.plot(o_x, o_y, color='b', marker='o', markersize=20, linestyle='')
    [plt.annotate(i, xy=obj_pos[i], xytext=obj_pos[i], ha='center', va='center',
                  color='w') for i in obj_pos]

    s_x, s_y = get_coordinates(sta_pos)
    plt.plot(s_x, s_y, color='#FF9999', marker='o', markersize=20, linestyle='')
    [plt.annotate(i, xy=sta_pos[i], xytext=sta_pos[i], ha='center', va='center',
                  color='w') for i in sta_pos]

    ax.axis('equal')
    plt.grid()
    plt.show()


def prepare_graph_for_draw(graph, s_p, placed_sta):
    pos = graph.pos.copy()
    draw_graph_node = graph.G.copy()

    sta_node = graph.s_key
    # cov_sta = graph.cov * len(list(s_p.keys()))
    # cov_sta.sort()
    cov_sta = graph.coverage.values()

    s = graph.s_origin * len(graph.cov)

    sta = list(itertools.compress(graph.s_key, placed_sta))
    cov = list(itertools.compress(cov_sta, placed_sta))
    sta_name = list(itertools.compress(s, placed_sta))

    remote_node = [i for i in sta_node if i not in sta]

    draw_graph_node.remove_nodes_from(remote_node)
    dict(pos.pop(i) for i in remote_node)

    key = list(draw_graph_node.node)
    value = key.copy()
    [value.remove(i) for i in sta]
    labels = dict(zip(key, value + sta_name))
    return [draw_graph_node, pos, labels, sta, cov]


def draw_ilp_graph(graph, placed_sta, y):
    """
    Draw network graph
    :param graph:  received graph of objects and stations
    :param placed_sta: placed station selectors after solving the problem
    :return: ILP problem graph
    """

    draw_g_node, pos, labels, sta, cov = prepare_graph_for_draw(graph,
                                                                graph.s_p,
                                                                placed_sta)
    g_list = list(graph.g_p.keys())
    o_list = list(graph.o_p.keys())

    nx.draw_networkx_nodes(draw_g_node, pos,
                           nodelist=g_list, node_shape='s',
                           node_color='r', linewidths=3)
    nx.draw_networkx_nodes(draw_g_node, pos,
                           nodelist=o_list, node_shape='o',
                           node_color='b', linewidths=3)
    nx.draw_networkx_nodes(draw_g_node, pos,
                           nodelist=sta, node_shape='^',
                           node_color='r', linewidths=3)
    nx.draw_networkx_edges(draw_g_node, pos,
                           arrowsize=20, edge_color='b')

    nx.draw_networkx_labels(draw_g_node, pos, labels=labels, font_color='w')
    station = list(itertools.compress(y, placed_sta))
    plt.title(station)
    fig = plt.gcf()
    ax = fig.gca()
    for i in range(len(sta)):
        coverage = plt.Circle(graph.s_p[sta[i]], cov[i],
                              color='r', alpha=0.1)
        ax.add_artist(coverage)
    ax.axis('equal')
    plt.grid()
    plt.show()
    a=1


def draw_lp_graph(net):
    """
    Draw network graph of LP problem
    :param net:  received graph of objects and stations
    :return: LP problem graph
    """
    g_list = list(net.g_p.keys())
    o_list = list(net.o_p.keys())
    s_list = list(net.s_p.keys())

    pos = {**net.g_p, **net.o_p, **net.s_p}

    nx.draw_networkx_nodes(net.G, pos,
                           nodelist=g_list, node_shape='s',
                           node_color='r', linewidths=10)
    nx.draw_networkx_nodes(net.G, pos,
                           nodelist=o_list, node_shape='o',
                           node_color='b', linewidths=5)
    nx.draw_networkx_nodes(net.G, pos,
                           nodelist=s_list, node_shape='^',
                           node_color='r', linewidths=10)
    nx.draw_networkx_edges(net.G, pos,
                           arrowsize=20, edge_color='b')
    nx.draw_networkx_labels(net.G, pos, font_color='w')

    # for i in range(len(sta)):
    #     coverage = plt.Circle(net.s_p[sta[i]], net.cov[i],
    #                           color='r', alpha=0.1)
    #     ax.add_artist(coverage)
    # ax.axis('equal')
    # plt.grid()
    # plt.show()

    plt.grid()
    plt.show()

