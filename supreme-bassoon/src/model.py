import gurobipy.gurobipy as grb

from math import exp
from numpy import array

from .data_utils import Solution
from .problem import ProblemInstance


class Modes:
    MIN_FAULT_COST = "min_fault_cost"
    MIN_MAINTENANCE_COST = "min_maintenance_cost"


class Model:
    def __init__(
        self,
        instace: ProblemInstance,
        eps: int,
        mode: str,
        verbose: bool,
        log_file_path: str | None = None,
    ) -> None:
        self.instace = instace
        self._model = grb.Model()
        if not verbose:
            self._model.setParam("OutputFlag", 0)
            self._model.setParam("LogToConsole", 0)

        self.eps = eps
        self._mode = mode
        self._verbose = verbose
        self._log_file_path = None
        if log_file_path:
            self._log_file_path = f"{log_file_path}optimization_{mode}_eps_{eps}.log"
        self._validate_mode()

        self.build_model()

    def _validate_mode(self) -> None:
        if self._mode not in [Modes.MIN_FAULT_COST, Modes.MIN_MAINTENANCE_COST]:
            raise ValueError(
                f"Invalid mode: {self._mode}. Valid modes are: {Modes.MIN_FAULT_COST}, {Modes.MIN_MAINTENANCE_COST}"
            )

    def build_model(self) -> None:
        self._model = grb.Model()
        self._add_variables()
        self._add_constraints()
        self._add_objective()

    def _add_variables(self) -> None:
        self._add_x_variables()

    def _add_x_variables(self) -> None:
        machines = self.instace.machines
        plans = self.instace.plans

        machine_plans = [(m, p) for m in machines for p in plans]

        self.x = self._model.addVars(machine_plans, vtype=grb.GRB.BINARY, name="x")

    def _add_constraints(self) -> None:
        self._add_eps_constraints()
        self._add_plan_assignment_constraints()

    def _add_eps_constraints(self) -> None:
        e = self.eps
        lhs = 0
        if self._mode == Modes.MIN_MAINTENANCE_COST:
            lhs = self._compute_fault_cost()
        elif self._mode == Modes.MIN_FAULT_COST:
            lhs = self._compute_maintenance_cost()

        self._model.addConstr(
            lhs == e,
            name="eps_restriction",
        )

    def _add_plan_assignment_constraints(self) -> None:
        machines = self.instace.machines
        plans = self.instace.plans

        for i in machines:
            lhs = sum(self.x[i, j] for j in plans)
            self._model.addConstr(
                lhs == 1,
                name=f"plan_assignment_machine_{i}",
            )

    def _compute_fault_cost(self) -> grb.LinExpr:
        machines = self.instace.machines
        plans = self.instace.plans
        clusters = self.instace.clusters
        dt = self.instace.delta_t

        def F(i, t):
            mac = machines[i]
            clu = clusters[mac.cluster]
            return 1 - exp(-1 * (t / clu.n) ** clu.b)

        def p(i, j):
            mac = machines[i]
            plan = plans[j]
            F0 = F(i, mac.t0)

            return (F(i, mac.t0 + plan.k * dt) - F0) / (1 - F0)

        return sum(
            p(i, j) * machines[i].fault_cost * self.x[i, j]
            for i in machines
            for j in plans
        )

    def _compute_maintenance_cost(self) -> grb.LinExpr:
        machines = self.instace.machines
        plans = self.instace.plans

        return sum(plans[j].plan_cost * self.x[i, j] for i in machines for j in plans)

    def _add_objective(self) -> None:
        if self._mode == Modes.MIN_FAULT_COST:
            self._model.setObjective(self._compute_fault_cost(), grb.GRB.MINIMIZE)
        elif self._mode == Modes.MIN_MAINTENANCE_COST:
            self._model.setObjective(self._compute_maintenance_cost(), grb.GRB.MINIMIZE)

    def export_model(self, path: str) -> None:
        self._model.write(path)

    def export_solution(self) -> Solution | None:
        if not self._model.status == grb.GRB.OPTIMAL:
            return None

        machines = self.instace.machines
        plans = self.instace.plans
        x = self._model.getAttr("x", self.x)
        selected_plans = [j for i in machines for j in plans if x[i, j] > 0.5]

        return Solution(
            x=selected_plans,
            maintenance_cost=self._compute_maintenance_cost().getValue(),
            fault_cost=self._compute_fault_cost().getValue(),
        )

    def optimize(self) -> None:
        if not self._verbose:
            self._model.setParam("LogToConsole", 0)
            self._model.setParam("OutputFlag", 0)
        if self._log_file_path:
            self._model.setParam("LogFile", self._log_file_path)

        self._model.setParam("FeasibilityTol", 1e-9)
        self._model.setParam("NumericFocus", 3)

        self._model.optimize()


class ModelHiperV:
    def __init__(
        self, instace: ProblemInstance, verbose: bool, log_file_path: str | None = None
    ) -> None:
        self.instace = instace
        self._model = grb.Model()
        if not verbose:
            self._model.setParam("OutputFlag", 0)
            self._model.setParam("LogToConsole", 0)

        self._verbose = verbose
        self._log_file_path = None
        if log_file_path:
            self._log_file_path = f"{log_file_path}optimization_hipervolume.log"

        self.K = self.generate_k_values()

        self.build_model()

    def optimize(self) -> None:
        if not self._verbose:
            self._model.setParam("LogToConsole", 0)
            self._model.setParam("OutputFlag", 0)
        if self._log_file_path:
            self._model.setParam("LogFile", self._log_file_path)

        self._model.setParam("FeasibilityTol", 1e-9)
        self._model.setParam("NumericFocus", 3)

        self._model.optimize()

    def generate_k_values(self) -> list[int]:
        u_m, _ = self.instace.get_utopic_solution()
        v_m, _ = self.instace.get_nadir_solution()

        return list(range(u_m, v_m + 1))

    def build_model(self) -> None:
        self._model = grb.Model()
        self._add_variables()
        self._add_constraints()
        self._add_objective()

    def _add_variables(self) -> None:
        self._add_h_variables()
        self._add_b_variables()
        self._add_x_variables()

    def _add_h_variables(self) -> None:
        self.h = self._model.addVars(
            self.K, vtype=grb.GRB.CONTINUOUS, name="h", lb=0, ub=1
        )

    def _add_b_variables(self) -> None:
        self.b = self._model.addVars(
            self.K, vtype=grb.GRB.CONTINUOUS, name="b", lb=0, ub=1
        )

    def _add_x_variables(self) -> None:
        machines = self.instace.machines
        plans = self.instace.plans

        machine_plans = [(k, m, p) for k in self.K for m in machines for p in plans]

        self.x = self._model.addVars(machine_plans, vtype=grb.GRB.BINARY, name="x")

    def _add_constraints(self) -> None:
        self._add_rectangle_base_constraints()
        self._add_rectangle_height_constraints()
        self._add_maintenance_cost_constraints()
        self._add_plan_assignment_constraints()

    def _add_rectangle_base_constraints(self) -> None:
        u_m, _ = self.instace.get_utopic_solution()
        v_m, _ = self.instace.get_nadir_solution()

        for k in self.K:
            self._model.addConstr(
                self.b[k] == 1 - (self._f_m(k) - u_m) / (v_m - u_m),
                name=f"rectangle_base_{k}",
            )

    def _add_rectangle_height_constraints(self) -> None:
        _, u_f = self.instace.get_utopic_solution()
        _, v_f = self.instace.get_nadir_solution()

        for k in self.K[1:]:
            self._model.addConstr(
                self.h[k] == (self._f_f(k - 1) - self._f_f(k)) / (v_f - u_f),
                name=f"rectangle_height_{k}",
            )

    def _add_maintenance_cost_constraints(self) -> None:
        for k in self.K:
            self._model.addConstr(
                self._f_m(k) == self.h[k],
                name=f"maintenance_cost_{k}",
            )

    def _add_plan_assignment_constraints(self) -> None:
        machines = self.instace.machines
        plans = self.instace.plans

        for k in self.K:
            for i in machines:
                lhs = sum(self.x[k, i, j] for j in plans)
                self._model.addConstr(
                    lhs == 1,
                    name=f"plan_assignment_machine_{i}",
                )

    def _f_f(self, k: int) -> grb.LinExpr:
        machines = self.instace.machines
        plans = self.instace.plans
        clusters = self.instace.clusters
        dt = self.instace.delta_t

        def F(i, t):
            mac = machines[i]
            clu = clusters[mac.cluster]
            return 1 - exp(-1 * (t / clu.n) ** clu.b)

        def p(i, j):
            mac = machines[i]
            plan = plans[j]
            F0 = F(i, mac.t0)

            return (F(i, mac.t0 + plan.k * dt) - F0) / (1 - F0)

        return sum(
            p(i, j) * machines[i].fault_cost * self.x[k, i, j]
            for i in machines
            for j in plans
        )

    def _f_m(self, k: int) -> grb.LinExpr:
        machines = self.instace.machines
        plans = self.instace.plans

        return sum(
            plans[j].plan_cost * self.x[k, i, j] for i in machines for j in plans
        )

    def _compute_hipervolume(self) -> grb.LinExpr:
        return sum(
            self.h[k] * self.b[k] for k in self.K
        )

    def _add_objective(self) -> None:
        hipervolume = self._compute_hipervolume()

        self._model.setObjective(hipervolume, grb.GRB.MAXIMIZE)

    def export_model(self, path: str) -> None:
        self._model.write(path)

    def export_solution(self, k:int) -> Solution | None:
        if not self._model.status == grb.GRB.OPTIMAL:
            return None

        machines = self.instace.machines
        plans = self.instace.plans
        x = self._model.getAttr("x", self.x)
        selected_plans = [j for i in machines for j in plans if x[k, i, j] > 0.5]

        return Solution(
            x=selected_plans,
            maintenance_cost=self._f_m(k).getValue(),
            fault_cost=self._f_f(k).getValue(),
        )

    def export_solution_pool(self) -> list[Solution]:
        pool = list()
        for k in self.K:
            sol = self.export_solution(k)
            if sol:
                pool.append(sol)

        return pool