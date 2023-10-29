from itertools import combinations
from re import sub

from .data_structures import *
from .solver import Solver, VarTypes, Senses
from .utilities import compute_distance


class CVRPProblem:
    def __init__(self, instance: CVRPInstance) -> None:
        self._instance = instance
        self._solver = Solver()
        self._distances = self._compute_distances()
        self._arcs = self._create_arcs()

    @property
    def status(self) -> str:
        return self._solver.get_status()

    def export_model(self, path: str):
        self._solver.export_model(path)

    def create_model(self) -> None:
        self._create_variables()
        self._create_objective()
        self._create_constraints()

    def solve(self) -> None:
        self._solver.optimize()

    def create_solution(self) -> CVRPSolution:
        objective_value = self._solver.get_objective_value()
        status = self._solver.get_status()
        solution_time = self._solver.get_solution_time()
        mip_gap = self._solver.get_mip_gap()
        num_vars = self._solver.get_num_vars()
        num_constrs = self._solver.get_num_constrs()
        routes = self._create_routes()

        return CVRPSolution(
            objective_value=objective_value,
            status=status,
            solution_time=solution_time,
            mip_gap=mip_gap,
            num_vars=num_vars,
            num_constrs=num_constrs,
            routes=routes,
        )

    def _create_arcs(self) -> list:
        return [
            ArcDrivenBy(point_a, point_b, vehicle.id)
            for (point_a, point_b) in self._distances
            for vehicle in self._instance.vehicles
            if point_a != point_b
        ]

    def _create_routes(self) -> list:
        routes = list()
        for vehicle in self._instance.vehicles:
            arcs = [arc for arc in self._arcs if arc.k == vehicle.id]
            route = []
            for arc in arcs:
                if self._solver.get_variable(arc).x > 0.5:
                    route.append((arc.x, arc.y))
            if route:
                deliveries = set([point for edge in route for point in edge])
                routes.append(
                    Route(
                        deliveries=[
                            delivery
                            for delivery in self._instance.deliveries
                            if delivery.id in deliveries
                        ],
                        vehicle=vehicle,
                        distance=sum(
                            self._distances[(point_a, point_b)]
                            for (point_a, point_b) in route
                        ),
                        cost=sum(
                            self._distances[(point_a, point_b)] * vehicle.variable_cost
                            for (point_a, point_b) in route
                        ),
                        edges=route,
                    )
                )

        return routes

    def _compute_distances(self) -> dict:
        distances = {}

        for delivery_a in self._instance.deliveries:
            for delivery_b in self._instance.deliveries:
                if delivery_a.id == delivery_b.id:
                    continue

                distances[(delivery_a.id, delivery_b.id)] = compute_distance(
                    delivery_a.coordinates, delivery_b.coordinates
                )

        for delivery in self._instance.deliveries:
            distances[(0, delivery.id)] = compute_distance(
                self._instance.depot, delivery.coordinates
            )
            distances[(delivery.id, 0)] = compute_distance(
                delivery.coordinates, self._instance.depot
            )

        return distances

    def _create_variables(self) -> None:
        for arc in self._arcs:
            self._solver.add_variable(arc, lb=0, ub=1, vtype=VarTypes.BINARY)

    def _create_objective(self) -> None:
        for arc, distance in self._distances.items():
            for vehicle in self._instance.vehicles:
                self._solver.add_objective_term(
                    coefficient=distance * vehicle.variable_cost,
                    variable=self._solver.get_variable(
                        ArcDrivenBy(arc[0], arc[1], vehicle.id)
                    ),
                )

        self._solver.set_objective()

    def _create_constraints(self) -> None:
        self._create_flow_conservation_constraints()
        self._create_node_visit_constraints()
        self._create_vehicle_start_constraints()
        self._create_vehicle_capacity_constraints()
        self._create_vehicle_volume_constraints()
        self._create_subtour_elimination_constraints()

    def _create_flow_conservation_constraints(self):
        nodes = [delivery.id for delivery in self._instance.deliveries] + [0]
        for node in nodes:
            for vehicle in self._instance.vehicles:
                inflow_arcs = [
                    ArcDrivenBy(point_a, point_b, vehicle.id)
                    for (point_a, point_b) in self._distances
                    if point_b == node
                ]

                outflow_arcs = [
                    ArcDrivenBy(point_a, point_b, vehicle.id)
                    for (point_a, point_b) in self._distances
                    if point_a == node
                ]

                inflow_variables = sum(
                    self._solver.get_variable(arc) for arc in inflow_arcs
                )
                outflow_variables = sum(
                    self._solver.get_variable(arc) for arc in outflow_arcs
                )

                self._solver.add_constraint(
                    lhs=inflow_variables - outflow_variables,
                    rhs=0,
                    sense=Senses.EQUAL,
                    name=f"flow_conservation_{node}_{vehicle.id}",
                )

    def _create_node_visit_constraints(self):
        deliveries_ids = [delivery.id for delivery in self._instance.deliveries]
        nodes = deliveries_ids + [0]
        for delivery in deliveries_ids:
            arcs = [
                ArcDrivenBy(point_a, delivery, vehicle.id)
                for point_a in nodes
                for vehicle in self._instance.vehicles
            ]

            variables = sum(self._solver.get_variable(arc) for arc in arcs)

            self._solver.add_constraint(
                lhs=variables,
                rhs=1,
                sense=Senses.EQUAL,
                name=f"node_visit_{delivery}",
            )

    def _create_vehicle_start_constraints(self):
        for vehicle in self._instance.vehicles:
            arcs_from_depot = [
                ArcDrivenBy(0, point_b, vehicle.id)
                for (point_a, point_b) in self._distances
                if point_a == 0
            ]

            arcs_not_from_depot = [
                ArcDrivenBy(point_a, point_b, vehicle.id)
                for (point_a, point_b) in self._distances
                if point_a != 0
            ]

            lhs = sum(self._solver.get_variable(arc) for arc in arcs_from_depot)
            rhs = (
                1.0
                / len(self._instance.deliveries)
                * sum(self._solver.get_variable(arc) for arc in arcs_not_from_depot)
            )

            self._solver.add_constraint(
                lhs=lhs,
                rhs=rhs,
                sense=Senses.GREATER_EQUAL,
                name=f"vehicle_start_{vehicle.id}",
            )

    def _create_vehicle_capacity_constraints(self):
        for vehicle in self._instance.vehicles:
            arcs = [
                ArcDrivenBy(point_a, point_b, vehicle.id)
                for (point_a, point_b) in self._distances
                if point_b != 0
            ]

            lhs = sum(
                self._instance.deliveries[arc.y - 1].weight
                * self._solver.get_variable(arc)
                for arc in arcs
            )

            self._solver.add_constraint(
                lhs=lhs,
                rhs=vehicle.capacity,
                sense=Senses.LESS_EQUAL,
                name=f"vehicle_capacity_{vehicle.id}",
            )

    def _create_vehicle_volume_constraints(self):
        for vehicle in self._instance.vehicles:
            arcs = [
                ArcDrivenBy(point_a, point_b, vehicle.id)
                for (point_a, point_b) in self._distances
                if point_b != 0
            ]

            lhs = sum(
                self._instance.deliveries[arc.y - 1].volume
                * self._solver.get_variable(arc)
                for arc in arcs
            )

            self._solver.add_constraint(
                lhs=lhs,
                rhs=vehicle.volume,
                sense=Senses.LESS_EQUAL,
                name=f"vehicle_capacity_{vehicle.id}",
            )

    def _create_subtour_elimination_constraints(self):
        deliveries_ids = [delivery.id for delivery in self._instance.deliveries]
        subsets = [
            list(subset)
            for i in range(2, len(deliveries_ids) - 1)
            for subset in combinations(deliveries_ids, i)
        ]

        for s in subsets:
            for vehicle in self._instance.vehicles:
                arcs_in_s = [
                    ArcDrivenBy(point_a, point_b, vehicle.id)
                    for point_a in s
                    for point_b in s
                    if point_a != point_b
                ]

                lhs = sum(self._solver.get_variable(arc) for arc in arcs_in_s)

                self._solver.add_constraint(
                    name=f"subtour_elimination_{s}_{vehicle.id}",
                    lhs=lhs,
                    sense=Senses.LESS_EQUAL,
                    rhs=len(s) - 1,
                )
