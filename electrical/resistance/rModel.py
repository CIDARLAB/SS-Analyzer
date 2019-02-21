from .connection import connection_R
from .mixer import mixer_R

def computeConnectionResistance(connection):
    if "segments" in connection.params.data:
        return connection_R(connection.params.data)
    else:
        raise Exception("Connection has no waypoints for default computation formula")


def computeComponentResistance(component):
    if component.entity == "MIXER":
        return mixer_R(component.params.data)
    else:
        raise Exception("Unsupported Entity found")