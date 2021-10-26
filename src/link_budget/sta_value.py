"""
It is used link_budget budget equation to calculate:
 - link_budget distance parameter between station;
 - coverage parameter of station.

LINK BUDGET:
Ptr - Ltr + Gtr - Lfs + Grecv - Lrecv = SOM + Precv,
where
    Ptr is a transmitter output power, [dBm];

    Ltr is a ransmitter losses, [dB];

    Gtr is a transmitter antenna gain, [dBi];

    Lfs is a free space path loss, [dB];

    Grecv is a receiver antenna gain,  [dBi];

    Lrecv is a receiver losses, [dB];

    SOM is a system operating margin, [dB];

    Precv is a receiver sensitivity, [dBm].

The Free Space Path Loss equation defines the propagation signal loss between
two antennas through free space (air).

FREE SPACE PATH LOSS EQUATION:
    FSPL = ((4⋅pi⋅R⋅f)/c)^2.

This formula expressed in decibels will be calculated as:
    L_fs = 20⋅lg(F) + 20⋅lg(R) + K,
where
    F is a radio wave centre frequency of a communication link_budget;
    R is a distance between transmit and receive antennas;
    K is a constant.

Constant K depends on frequency and distance:
    - for a frequency in GHz and a distance in km, constant K is equal to 92.45;
    - for a frequency in MHz and distance in km, constant K is equal to 32.4;
    - for a frequency in MHz and distance in m, constant K is equal to -27.55.

"""

from dataclasses import dataclass
from math import log10
from itertools import product
from typing import Tuple, Union

import numpy as np


@dataclass
class StaParameterSet:
    """
    Given station parameter set. This parameters is used to calculate
    link_budget distance parameter between station and coverage parameter of station
    """
    p_tr: list
    g: list
    p_recv: list
    g_recv_link: list
    l: list
    l_coverage: list
    p_recv_coverage: list
    g_recv_coverage: list


@dataclass
class UserDeviceParameterSet:
    """ This parameters is used to calculate
    coverage parameter between station and user device"""
    p_tr: float
    g: float
    l: float


@dataclass
class GatewayParameterSet:
    """This parameters is used to calculate
    link_budget distance parameter between station and gateway"""
    p_tr: float
    g: float
    p_recv: float
    g_recv: float
    l: float


@dataclass
class GetDistanceInput:
    """ Inputs to solve distance parameters"""
    p_tr: float
    l_tr: float
    g_tr: float
    p_recv: float
    g_recv: float
    l_recv: float
    frequency: float


def get_distance(lb_input,
                 som: float = 10,
                 k: float = -27.55) -> float:
    """
    Calculate distance parameter (link_budget distance or coverage) using by link_budget
    budget equation.

    :param lb_input: link_budget budget equation input
    :param som: system operating margin
    :param f: radio wave centre frequency
    :param k: constant of free space path loss equation
    :return:
    """
    l_fs = (lb_input.p_tr - lb_input.l_tr + lb_input.g_tr + lb_input.g_recv -
            lb_input.l_tr - lb_input.p_recv - som)
    distance = round(10 ** ((l_fs - 20 * log10(lb_input.frequency) - k)/20))
    return distance
