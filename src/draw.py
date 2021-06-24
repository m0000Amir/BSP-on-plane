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
    sta_pos = {k+1+len(obj_pos): value
               for k, value in enumerate(station['pos'].values())}

    plt.close()
    fig = plt.gcf()
    ax = fig.gca()
    g_x, g_y = get_coordinates(gtw_pos)
    plt.plot(g_x, g_y, color='#07C6FF', marker='o', markersize=22, linestyle='',
             label='Координаты шлюза')
    [plt.annotate(i, xy=gtw_pos[i], xytext=gtw_pos[i], ha='center', va='center',
                  color='w') for i in gtw_pos]

    o_x, o_y = get_coordinates(obj_pos)
    plt.plot(o_x, o_y, color='#07C6FF', marker='o', markersize=16, linestyle='',
             label='Координаты объектов')
    [plt.annotate(i, xy=obj_pos[i], xytext=obj_pos[i], ha='center', va='center',
                  color='w', size=12) for i in obj_pos]

    s_x, s_y = get_coordinates(sta_pos)
    plt.plot(s_x, s_y, color='#07C6FF', marker='X', markersize=20,
             linestyle='', label='Координаты размещения станций')
    [plt.annotate(i, xy=sta_pos[i], xytext=sta_pos[i], ha='center', va='center',
                  color='w', size=12) for i in sta_pos]
    plt.legend(markerscale=0.3)
    # plt.rc('font', size=20)
    ax.axis('equal')
    plt.grid()
    plt.show()


def prepare_graph_for_draw(net, placed_sta):
    s_list = list(net.s_p.keys())

    pos = {**net.g_p, **net.o_p, **net.s_p}
    draw_graph_node = net.G.copy()

    sta_node = list(net.s_p.keys())
    cov_sta = net.coverage.values()
    s_p_num = int(len(net.s_p)/len(net.c))
    s = s_list[:s_p_num] * len(net.c)

    sta = list(itertools.compress(s_list, placed_sta))
    cov = list(itertools.compress(cov_sta, placed_sta))
    sta_name = list(itertools.compress(s, placed_sta))

    remote_node = [i for i in sta_node if i not in sta]

    draw_graph_node.remove_nodes_from(remote_node)
    dict(pos.pop(i) for i in remote_node)

    key = list(draw_graph_node.nodes)
    value = key.copy()
    [value.remove(i) for i in sta]
    labels = dict(zip(key, value + sta_name))
    return [draw_graph_node, pos, labels, sta, cov]


def draw_milp_graph(net, placed_sta, y):
    """
    Draw network graph
    :param net:  received graph of objects and stations
    :param placed_sta: placed sta selectors after solving the problem
    :return: ILP problem graph
    """
    g_list = list(net.g_p.keys())
    o_list = list(net.o_p.keys())

    draw_g_node, pos, labels, sta, cov = prepare_graph_for_draw(net, placed_sta)

    nx.draw_networkx_nodes(draw_g_node, pos, label='Шлюз',
                           nodelist=g_list, node_shape='s',
                           node_color='#07C6FF', linewidths=3)
    nx.draw_networkx_nodes(draw_g_node, pos, label='Объекты',
                           nodelist=o_list, node_shape='o', node_size=200,
                           node_color='#07C6FF', linewidths=3)
    nx.draw_networkx_nodes(draw_g_node, pos, label='Размещенные станции',
                           nodelist=sta, node_shape='o', node_size=300,
                           node_color='#07C6FF', linewidths=3)
    nx.draw_networkx_edges(draw_g_node, pos,
                           arrowsize=20, edge_color='#898989')

    fig = plt.gcf()
    ax = fig.gca()
    for i in range(len(sta)):
        coverage = plt.Circle(net.s_p[sta[i]], cov[i], linestyle='--',
                              fill=True,
                              alpha=0.1, color='#898989')
        ax.add_artist(coverage)
    ax.axis('equal')
    plt.legend(markerscale=0.3)
    plt.grid()

    nx.draw_networkx_labels(draw_g_node, pos, labels=labels, font_color='w')
    station = list(itertools.compress(y, placed_sta))
    # plt.title(', '.join(station))

    plt.show()


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
                           node_color='r', linewidths=10, label='Gateway')
    nx.draw_networkx_nodes(net.G, pos,
                           nodelist=o_list, node_shape='o',
                           node_color='b', linewidths=5, label='Client')
    nx.draw_networkx_nodes(net.G, pos,
                           nodelist=s_list, node_shape='^',
                           node_color='r', linewidths=10, label='Base STA')
    nx.draw_networkx_edges(net.G, pos,
                           arrowsize=20, edge_color='b', label='r')
    nx.draw_networkx_labels(net.G, pos, font_color='w')

    plt.legend(markerscale=0.3)

    plt.grid()
    plt.show()

