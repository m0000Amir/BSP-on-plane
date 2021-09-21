import networkx as nx
import matplotlib.pyplot as plt
import PIL


import itertools
from itertools import product,  permutations

import pandas as pd

from src.net import Network
from src.mipop.mipop import MIP


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
    # s_list = list(net.s_p.keys())
    s_list = list(net.station.keys())

    all_points = {**net.gateway, **net.device, **net.station}
    pos = dict(enumerate([all_points[i]["coordinates"]
                          for i in range(len(all_points))]))

    draw_graph_node = net.graph.copy()

    sta_node = list(net.station.keys())
    # cov_sta = net.coverage.values()
    cov_sta = [net.station[key]["coverage"] for key in net.station.keys()]
    # s_p_num = int(len(net.s_p)/len(net.c))
    s_p_num = int(len(s_list) / len(net.type))
    s = s_list[:s_p_num] * len(net.type)

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
                           nodelist=sta, node_shape='o', node_size=400,
                           node_color='#07C6FF', linewidths=3)
    nx.draw_networkx_edges(draw_g_node, pos,
                           arrowsize=20, edge_color='#898989')

    fig = plt.gcf()
    ax = fig.gca()
    for i in range(len(sta)):
        coverage = plt.Circle(net.s_p[sta[i]], cov[i], linestyle='--',
                              fill=True,
                              alpha=0.2, color='#898989')
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


def prepare_draw_graph(net: Network, problem: MIP, solution: pd.Series
                       ) -> nx.DiGraph:
    draw_graph = net.graph.copy()
    draw_graph = nx.DiGraph()

    edge_z = list(product(net.device.keys(),
                          net.station.keys()))
    edge_x = (list(permutations(net.station.keys(), 2)) +
              list(product(net.station.keys(),
                           net.gateway.keys())))

    y_node = list(zip(problem.of.column.y, problem.of.var.y))
    solution_variable = edge_z + edge_x + y_node
    labels = {}
    for k in range(len(solution)):
        if solution_variable[k][0] == solution.index[k]:
            labels.update({solution_variable[k][1][1:]: solution[k]})
        else:
            if solution[k] != 0:
                i, j = solution_variable[k]
                draw_graph.add_edge(i, j)
    _sta = [i+1 for i in range(len(net.type))] * int(
        len(net.station)/len(net.type))
    sta = dict(zip(labels.keys(), _sta))

    all_points = {**net.gateway, **net.device, **net.station}
    draw_nodes = list(draw_graph.nodes())
    draw_nodes.sort()
    coordinates = [all_points[i]["coordinates"] for i in draw_nodes]
    pos = dict(zip(draw_nodes, coordinates))

    debug = 1

    # , sta, cov
    return [draw_graph, pos, labels, sta]


def draw_mip_graph(net: Network, problem: MIP, solution: pd.Series) -> None:
    """

    Parameters
    ----------
    net - received graph of devices and stations
    problem - MIP problem
    solution - obtained placement

    Returns
    -------
        None
    """

    fig, ax = plt.subplots()
    plt.grid()
    plt.axis()
    # limits = plt.axis("on")   # turns on axis
    ax.tick_params(left=True, bottom=True, labelleft=True, labelbottom=True)


    g_list = list(net.gateway.keys())
    d_list = list(net.device.keys())

    draw_g_node, pos, labels, sta1, cov = prepare_graph_for_draw(
        net, problem.of.data[problem.of.column.y])

    draw_graph, pos, labels, sta = prepare_draw_graph(net, problem, solution)
    s_list = [i for i in net.station.keys() if i in pos.keys()]
    # nx.draw_networkx_nodes(draw_graph, pos, label='Шлюз',
    #                        nodelist=g_list, node_shape='s',
    #                        node_color='#07C6FF', linewidths=3)
    # nx.draw_networkx_nodes(draw_graph, pos, label='Объекты',
    #                        nodelist=d_list, node_shape='o', node_size=200,
    #                        node_color='#07C6FF', linewidths=3)
    # nx.draw_networkx_nodes(draw_graph, pos, label='Размещенные станции',
    #                        nodelist=s_list, node_shape='o', node_size=400,
    #                        node_color='#07C6FF', linewidths=3)
    # nx.draw_networkx_edges(draw_graph, pos,
    #                        arrowsize=20, edge_color='#898989')

    icons = {
        "gateway": "src/drawing/icons/gateway.png",
        "device": "src/drawing/icons/device.png",
        "bs": "src/drawing/icons/bs.png",
    }

    # Load images
    images = {k: PIL.Image.open(fname) for k, fname in icons.items()}

    G = nx.Graph()
    for i in range(len(sta)):
        if sta1[i] in pos.keys():
            coverage = plt.Circle(net.station[sta1[i]]["coordinates"],
                                  cov[i],
                                  linestyle='--',
                                  fill=True,
                                  alpha=0.2, color='#898989')
            ax.add_patch(coverage)

    for i in pos.keys():
        if i in net.gateway.keys():
            G.add_node(i, image=images["gateway"])
        elif i in net.device.keys():
            G.add_node(i, image=images["device"])
        elif i in net.station.keys():
            G.add_node(i, image=images["bs"])
    nx.draw_networkx_nodes(G, pos, node_size=.01, ax=ax)

    # Transform from data coordinates (scaled between xlim and ylim)
    # to display coordinates
    tr_figure = ax.transData.transform
    # Transform from display to figure coordinates
    tr_axes = fig.transFigure.inverted().transform

    # Select the size of the image (relative to the X axis)
    icon_size = (ax.get_xlim()[1] - ax.get_xlim()[0]) * 0.015
    icon_center = icon_size / 2.0

    # Add the respective image to each node
    for n in G.nodes:
        xf, yf = tr_figure(pos[n])
        xa, ya = tr_axes((xf, yf))
        # get overlapped axes and plot icon
        a = plt.axes([xa - icon_center, ya - icon_center, icon_size, icon_size])
        a.imshow(G.nodes[n]["image"])
        a.axis("off")

    # turn the axis on
    ax.set_axis_on()
    ax.tick_params(left=True, bottom=True, labelleft=True, labelbottom=True)
    plt.show()
    plt.legend(markerscale=0.3)

    ax.axis()
    nx.draw_networkx_labels(draw_g_node, pos, labels=labels, font_color='w')
    station = list(itertools.compress(problem.of.column.y,
                                      problem.of.data[problem.of.column.y]))
    # plt.title(', '.join(station))

    plt.show()



