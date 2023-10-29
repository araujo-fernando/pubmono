from typing import NamedTuple

MAX_VEHICLE_TRIPS = 10


class ArcDrivenBy(NamedTuple):
    """
    Defines the decisiona variable in the Capacitaded Vehicle Routing Problem.
    Currently the index corresponds to:
    x - origin node
    y - destination node
    k - vehicle
    """

    x: int
    y: int
    k: int


class Coordinates(NamedTuple):
    x: float
    y: float


class Delivery(NamedTuple):
    id: int
    coordinates: Coordinates
    weight: float
    volume: float


class Vehicle(NamedTuple):
    id: int
    variable_cost: float
    capacity: float
    volume: float


class Route(NamedTuple):
    deliveries: list[Delivery]
    vehicle: Vehicle
    distance: float
    cost: float
    edges: list[tuple[int, int]]


class CVRPInstance(NamedTuple):
    vehicles: list[Vehicle]
    deliveries: list[Delivery]
    depot: Coordinates


class CVRPSolution(NamedTuple):
    routes: list[Route]
    objective_value: float
    status: str
    solution_time: float
    mip_gap: float
    num_vars: int
    num_constrs: int
