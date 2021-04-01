from typing import Dict, TextIO
from parchmint.device import Device


pressureDict: Dict[str, float] = dict()
flowrateDict: Dict[str, float] = dict()
inletOutletDict: Dict[str, str] = dict()


def set_pressure(name: str, pressure: float) -> None:
    print("Setting pressure", name, pressure)
    pressureDict[name] = pressure


def get_pressure(name: str) -> float:
    return pressureDict[name]


def set_flowrate(name: str, flowrate: float) -> None:
    print("Setting pressure", name, flowrate)
    flowrateDict[name] = flowrate


def get_flowrate(name: str) -> float:
    return flowrateDict[name]


def set_inlet_outlet(name: str, state: str) -> None:
    inletOutletDict[name] = state


def get_inlet_outlet(name: str) -> str:
    return inletOutletDict[name]


def get_inlets_outlets() -> Dict[str, str]:
    return inletOutletDict


def get_id_for_name(name: str, device: Device) -> str:
    components = device.get_components()
    for component in components:
        if component.name == name:
            return component.ID
    raise Exception("Could not find component with name in config:", name)


def parse_config(file: TextIO, device: Device) -> None:
    """Parses the config file and sets the fixed states of the entire device

    Args:
        file (TextIO): Config File pointer
        device (Device): Device object
    """

    lines = file.read().splitlines()
    for line in lines:
        line = line.strip()
        parts = line.split(",")
        name = parts[0].strip()
        id = get_id_for_name(name, device)
        state = parts[1].strip()
        value = parts[2].strip()
        set_inlet_outlet(id, state)
        if state == "IN":
            set_flowrate(id, float(value))
        elif state == "OUT":
            set_pressure(id, float(value))
        else:
            print("Unkown state:", state)
    file.close()
