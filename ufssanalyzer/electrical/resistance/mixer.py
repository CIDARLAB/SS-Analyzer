from math import pow, pi, tanh
from ufssanalyzer.electrical.resistance.constants import MICRONS, WATER_VISCOSITY


def mixer_R(params):

    numberOfBends = float(params["numberOfBends"])
    bendLength = float(params["bendLength"])
    bendSpacing = float(params["bendSpacing"])

    width = float(params["channelWidth"])
    depth = float(params["height"])

    length = numberOfBends * ((2 * bendLength) + (2 * bendSpacing))

    width = width * MICRONS
    depth = depth * MICRONS
    length = length * MICRONS

    alpha = 12 * pow(
        1 - ((192 * depth) / (pow(pi, 5) * width)) * tanh((pi * width) / (2 * depth)),
        -1,
    )
    resistance = (alpha * WATER_VISCOSITY * length) / (width * pow(depth, 3))

    return resistance
