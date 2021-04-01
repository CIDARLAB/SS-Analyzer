from ufssanalyzer.electrical.resistance.connection import connection_R
from ufssanalyzer.electrical.resistance.mixer import mixer_R


def compute_connection_resistance(connection):
    if "segments" in connection.params.data:
        return connection_R(connection.params.data)
    else:
        raise Exception("Connection has no waypoints for default computation formula")


def compute_component_resistance(component):
    if component.entity == "MIXER":
        return mixer_R(component.params.data)
    else:
        raise Exception("Unsupported Entity found")