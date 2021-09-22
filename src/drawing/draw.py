import networkx as nx
import matplotlib.pyplot as plt
import pandas as pd
import PIL


import itertools
from itertools import product,  permutations
from typing import List, Dict, Union
import math



from src.net import Network
from src.mipop.mipop import MIP


def get_coordinates(position):
    point = position.values()
    x, y = zip(*point)
    return x, y


def draw_input_data(net: Network) -> None:
    """
    Draw input data:
        - gateway coordinates;
        - devices coordinates;
        - station placement coordinates
    """
    title = "Заданные координаты"

    gtw_pos = {0: net.gateway[0]["coordinates"]}
    device_pos = {i: net.device[i]["coordinates"] for i in net.device.keys()}
    for i in net.station.keys():
        pass

    station_pos = {}
    key = len(device_pos) + 1
    for i in range(0, len(list(net.station.keys())), len(net.type)):
        station_pos.update({key: net.station[len(device_pos)+1+i]["coordinates"]})
        key += 1


    plt.close()
    fig = plt.gcf()
    ax = fig.gca()
    ax.set_title(title)
    g_x, g_y = get_coordinates(gtw_pos)
    plt.plot(g_x, g_y, color='#57FF9A', marker='X', markersize=30, linestyle='',
             label='Координаты шлюза')
    [plt.annotate(i, xy=gtw_pos[i], xytext=gtw_pos[i], ha='center', va='center',
                  color='k') for i in gtw_pos]

    o_x, o_y = get_coordinates(device_pos)
    plt.plot(o_x, o_y, color='#57FF9A', marker='o', markersize=20, linestyle='',
             label='Координаты объектов')
    [plt.annotate(i, xy=device_pos[i], xytext=device_pos[i], ha='center',
                  va='center', color='k', size=12) for i in device_pos]

    s_x, s_y = get_coordinates(station_pos)
    plt.plot(s_x, s_y, color='#57FF9A', marker='X', markersize=30,
             linestyle='', label='Координаты размещения станций')
    [plt.annotate(i, xy=station_pos[i], xytext=station_pos[i], ha='center',
                  va='center', color='k', size=15) for i in station_pos]
    plt.legend(markerscale=0.3)
    # plt.rc('font', size=20)
    ax.axis('equal')
    plt.grid()
    plt.show()


def prepare_graph_for_draw(net, placed_sta):
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


def prepare_draw_graph(net: Network, problem: MIP, solution: pd.Series
                       ) -> List[Union[nx.DiGraph, nx.DiGraph,
                                       Dict, Dict, Dict]]:
    draw_graph = nx.DiGraph()
    draw_link_distance = nx.DiGraph()

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

    draw_link_distance_pos = {}
    for i, j in edge_x:
        if (i in net.station.keys()) and (i in pos.keys()):
            if (j in net.station.keys()) and (j in pos.keys()):
                _distance = math.sqrt(
                    (net.station[i]["coordinates"][0] -
                     net.station[j]["coordinates"][0]) ** 2 +
                    (net.station[i]["coordinates"][1] -
                     net.station[j]["coordinates"][1]) ** 2)
                if _distance <= net.station[i]["link_distance"]:
                    draw_link_distance.add_edge(i, j)
                    draw_link_distance_pos.update(
                        {i: net.station[i]["coordinates"]})
            if j in net.gateway.keys():
                _distance = math.sqrt(
                    (net.station[i]["coordinates"][0] -
                     net.gateway[j]["coordinates"][0]) ** 2 +
                    (net.station[i]["coordinates"][1] -
                     net.gateway[j]["coordinates"][1]) ** 2)
                if _distance <= net.station[i]["link_distance"]:
                    draw_link_distance.add_edge(i, j)
    draw_link_distance_pos.update({0: net.gateway[0]["coordinates"]})

    return [draw_graph, draw_link_distance, pos, draw_link_distance_pos, sta]


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

    title = 'Топологическая структрура полученного размещения БС.'

    fig, ax = plt.subplots()
    ax.set_title(title)

    plt.grid()
    # limits = plt.axis("on")   # turns on axis
    ax.tick_params(left=True, bottom=True, labelleft=True, labelbottom=True)

    draw_graph, draw_link_distance, pos, draw_link_distance_pos, sta = prepare_draw_graph(net, problem, solution)
    node_label = {}
    for i in pos.keys():
        if i in net.gateway.keys():
            node_label.update({int(i): r"$S_0$"})
        elif i in net.device.keys():
            node_label.update({int(i): f"d$_{{{i}}}$"})
        elif i in net.station.keys():
            node_label.update({int(i): f"S$_{{{sta[str(i)]}}}$"})


    icons = {
        "gateway": "src/drawing/icons/gateway.png",
        "device": "src/drawing/icons/device.png",
        "bs": "src/drawing/icons/bs.png",
    }
    # Load images
    images = {k: PIL.Image.open(fname) for k, fname in icons.items()}

    G = nx.Graph()
    for i in pos.keys():
        if i in net.gateway.keys():
            G.add_node(i, image=images["gateway"])
        elif i in net.device.keys():
            G.add_node(i, image=images["device"])
        elif i in net.station.keys():
            G.add_node(i, image=images["bs"])
    nx.draw_networkx_nodes(G, pos, node_size=.001)
    label_pos = {i: [pos[i][0]+.1, pos[i][1]+.1] for i in pos.keys()}
    nx.draw_networkx_labels(draw_graph, label_pos, labels=node_label,
                            font_color='k',
                            font_size=13,
                            verticalalignment='bottom',
                            horizontalalignment='left')

    nx.draw_networkx_edges(draw_link_distance, draw_link_distance_pos,
                           edge_color='#484E49', width=12,
                           alpha=.3,
                           arrows=False)
    nx.draw_networkx_edges(draw_graph, pos,
                           arrowsize=10,
                           width=3,
                           edge_color='#000000')
    # Transform from data coordinates (scaled between xlim and ylim)
    # to display coordinates
    # ax.set_ylim(1, 7)
    # ax.set_xlim(0, 6)
    # ax.axis('scaled')
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

    ax.set_axis_on()
    ax.tick_params(left=True, bottom=True, labelleft=True, labelbottom=True)
    # plt.legend(markerscale=0.3)

    for i in range(len(sta)):
        key = list(net.station.keys())[i]
        if key in pos.keys():
            coverage = plt.Circle(net.station[key]["coordinates"],
                                  net.station[key]["coverage"],
                                  linestyle='--',
                                  fill=True,
                                  alpha=0.4, color='#3CFF8A')
            ax.add_patch(coverage)

    # for i in range(len(sta)):
    #     key = list(net.station.keys())[i]
    #     if key in pos.keys():
    #         link_distance = plt.Circle(net.station[key]["coordinates"],
    #                               net.station[key]["link_distance"],
    #                               linestyle='--',
    #                               fill=True,
    #                               alpha=0.1, color='r')
    #         ax.add_patch(link_distance)

    plt.show()
    debug = 1



