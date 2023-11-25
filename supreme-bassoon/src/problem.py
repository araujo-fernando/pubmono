from math import exp
from .data_utils import read_data, Machine, MaintenancePlan, Cluster

class ProblemInstance:
    def __init__(self, data_path: str, delta_t: int) -> None:
        self.machines: dict[int, Machine] = dict()
        self.clusters: dict[int, Cluster] = dict()
        self.plans: dict[int, MaintenancePlan] = dict()
        self.delta_t = delta_t

        self._load_data(data_path)

    def print_data(self) -> None:
        print("Problem Data:\nMachines:")
        for m in self.machines:
            print(m)

        print("\nClusters:")
        for c in self.clusters:
            print(c)

        print("\nMaintenance Plans:")
        for p in self.plans:
            print(p)

        print(f"\nHorizon: {self.delta_t}y")
        print(f"\nMax Possible Maintenance Cost: {self.get_max_maintenance_cost()}")
        print(f"\nMin Possible Maintenance Cost: {self.get_min_maintenance_cost()}")

    def _load_data(self, data_path: str) -> None:
        self._load_clusters(data_path)
        self._load_plans(data_path)
        self._load_machines(data_path)

    def _load_machines(self, data_path: str) -> None:
        data = read_data(data_path + "EquipDB.csv")

        self.machines = dict(
            map(
                lambda m: (m[0], Machine(m[0], m[1], m[2], m[3])),
                data.to_dict("records"),
            )
        )

    def _load_plans(self, data_path: str) -> None:
        data = read_data(data_path + "MPDB.csv")

        self.plans = dict(
            map(
                lambda p: (p[0], MaintenancePlan(p[0], p[1], p[2])),
                data.to_dict("records"),
            )
        )

    def _load_clusters(self, data_path: str) -> None:
        data = read_data(data_path + "ClusterDB.csv")
        self.clusters = dict(
            map(
                lambda c: (c[0], Cluster(c[0], c[1], c[2])),
                data.to_dict("records"),
            )
        )

    def get_max_fault_cost(self) -> float:
        machines = self.machines
        plans = self.plans
        clusters = self.clusters
        dt = self.delta_t

        def F(i, t):
            mac = machines[i]
            clu = clusters[mac.cluster]
            return 1 - exp(-1 * (t / clu.n) ** clu.b)

        def p(i, j):
            mac = machines[i]
            plan = plans[j]
            F0 = F(i, mac.t0)

            return (F(i, mac.t0 + plan.k * dt) - F0) / (1 - F0)

        costs = [max([p(i, j) for j in plans]) * machines[i].fault_cost for i in machines]

        return sum(costs)

    def get_min_fault_cost(self) -> float:
        machines = self.machines
        plans = self.plans
        clusters = self.clusters
        dt = self.delta_t

        def F(i, t):
            mac = machines[i]
            clu = clusters[mac.cluster]
            return 1 - exp(-1 * (t / clu.n) ** clu.b)

        def p(i, j):
            mac = machines[i]
            plan = plans[j]
            F0 = F(i, mac.t0)

            return (F(i, mac.t0 + plan.k * dt) - F0) / (1 - F0)

        costs = [min([p(i, j) for j in plans]) * machines[i].fault_cost for i in machines]

        return sum(costs)

    def get_max_maintenance_cost(self) -> int:
        return max(map(lambda p: p.plan_cost, self.plans.values())) * len(self.machines)

    def get_min_maintenance_cost(self) -> int:
        return min(map(lambda p: p.plan_cost, self.plans.values())) * len(self.machines)

    def get_utopic_solution(self):
        return self.get_min_maintenance_cost(), self.get_min_fault_cost()
    
    def get_nadir_solution(self):
        return self.get_max_maintenance_cost(), self.get_max_fault_cost()

    def get_maintenance_cost_step(self) -> int:
        costs = list(map(lambda p: p.plan_cost, self.plans.values()))
        costs = [c for c in costs if c != 0]
        step = min([abs(costs[i] - costs[i + 1]) for i in range(len(costs) - 1)])

        return step
