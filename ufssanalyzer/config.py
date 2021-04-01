from typing import Dict, TextIO
from parchmint.device import Device


pressureDict: Dict[str, float] = dict()
flowrateDict: Dict[str, float] = dict()
inletOutletDict: Dict[str, str] = dict()


def setPressure(name: str, pressure: float) -> None:
    print("Setting pressure", name, pressure)
    pressureDict[name] = pressure


def get_pressure(name: str) -> float:
    return pressureDict[name]


def setFlowRate(name: str, flowrate: float) -> None:
    print("Setting pressure", name, flowrate)
    flowrateDict[name] = flowrate


def get_flow_rate(name: str) -> float:
    return flowrateDict[name]


def setInletOutlet(name: str, state: str) -> None:
    inletOutletDict[name] = state


def getInletOutlet(name: str) -> str:
    return inletOutletDict[name]


def get_inlets_outlets() -> Dict[str, str]:
    return inletOutletDict


def getIDForName(name: str, device: Device) -> str:
    components = device.get_components()
    for component in components:
        if component.name == name:
            return component.ID
    raise Exception("Could not find component with name in config:", name)


def parseConfig(file: TextIO, device: Device) -> None:

    lines = file.read().splitlines()
    for line in lines:
        line = line.strip()
        parts = line.split(",")
        name = parts[0].strip()
        id = getIDForName(name, device)
        state = parts[1].strip()
        value = parts[2].strip()
        setInletOutlet(id, state)
        if state == "IN":
            setFlowRate(id, float(value))
        elif state == "OUT":
            setPressure(id, float(value))
        else:
            print("Unkown state:", state)
    file.close()
