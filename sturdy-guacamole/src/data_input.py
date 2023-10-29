from .data_structures import *
from random import uniform, seed


def create_instance_from_data(path: str):
    """
    Reads the data from a file and creates an instance of the problem.
    A problem has three files, needed to be in the format:
        vehicles.csv: variable_cost, capacity, volume
        deliveries.csv: x, y, weight, volume
        depot.csv: x, y
    """
    vehicles = []
    deliveries = []
    depot = None

    with open(path + "vehicles.csv", "r") as file:
        for id, line in enumerate(file.readlines(), start=1):
            variable_cost, capacity, volume = line.split(",")
            for trip in range(MAX_VEHICLE_TRIPS):
                vehicles.append(
                    Vehicle(
                        MAX_VEHICLE_TRIPS * int(id) + trip,
                        float(variable_cost),
                        float(capacity),
                        float(volume),
                    )
                )

    with open(path + "deliveries.csv", "r") as file:
        for id, line in enumerate(file.readlines(), start=1):
            x, y, weight, volume = line.split(",")
            deliveries.append(
                Delivery(
                    int(id),
                    Coordinates(float(x), float(y)),
                    float(weight),
                    float(volume),
                )
            )

    with open(path + "depot.csv", "r") as file:
        line = file.readline()
        x, y = line.split(",")
        depot = Coordinates(float(x), float(y))

    return CVRPInstance(vehicles, deliveries, depot)


def create_random_instance(
    num_vehicles: int,
    num_deliveries: int,
    path: str | None = None,
    rd_seed: int | None = None,
):
    if rd_seed:
        seed(rd_seed)

    vehicles = []
    for i in range(1, num_vehicles + 1):
        var_cost = uniform(0.5, 1.5)
        capacity = uniform(5, 20)
        volume = uniform(5, 20)
        vehicles.extend(
            [
                Vehicle(MAX_VEHICLE_TRIPS * i + trip, var_cost, capacity, volume)
                for trip in range(MAX_VEHICLE_TRIPS)
            ]
        )

    deliveries = [
        Delivery(
            i,
            Coordinates(uniform(0, 100), uniform(0, 100)),
            uniform(0.5, 1.5),
            uniform(0.5, 1.5),
        )
        for i in range(1, num_deliveries + 1)
    ]

    depot = Coordinates(uniform(0, 100), uniform(0, 100))

    if path:
        with open(path + "vehicles.csv", "w") as file:
            for vehicle in vehicles:
                if vehicle.id % MAX_VEHICLE_TRIPS == 0:
                    file.write(
                        f"{vehicle.variable_cost},{vehicle.capacity},{vehicle.volume}\n"
                    )

        with open(path + "deliveries.csv", "w") as file:
            for delivery in deliveries:
                file.write(
                    f"{delivery.coordinates.x},{delivery.coordinates.y},{delivery.weight},{delivery.volume}\n"
                )

        with open(path + "depot.csv", "w") as file:
            file.write(f"{depot.x},{depot.y}\n")

    return CVRPInstance(vehicles, deliveries, depot)
