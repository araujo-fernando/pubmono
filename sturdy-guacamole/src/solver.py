from typing import NamedTuple

import gurobipy.gurobipy as grb

from .data_structures import ArcDrivenBy


class VarTypes:
    CONTINUOUS = grb.GRB.CONTINUOUS
    INTEGER = grb.GRB.INTEGER
    BINARY = grb.GRB.BINARY


class Senses:
    LESS_EQUAL = grb.GRB.LESS_EQUAL
    EQUAL = grb.GRB.EQUAL
    GREATER_EQUAL = grb.GRB.GREATER_EQUAL


class Solver:
    def __init__(self) -> None:
        self._variables = {}
        self._model = grb.Model()
        self._objective = grb.LinExpr()

    def add_variable(self, variable: ArcDrivenBy, lb: float, ub: float, vtype) -> None:
        self._variables[variable] = self._model.addVar(
            vtype=vtype, lb=lb, ub=ub, name=str(variable)
        )

    def add_constraint(
        self, name: str, lhs: grb.LinExpr, sense: str, rhs: float
    ) -> None:
        self._model.addConstr(lhs, sense, rhs, name=name)

    def add_constraint_triggered_by_sum(
        self,
        name: str,
        lhs: grb.LinExpr,
        sense: str,
        rhs: float,
        trigger_exp: grb.LinExpr,
        trigger_value: float,
    ) -> None:
        eps = 0.01

        indicator_var = self._model.addVar(
            vtype=grb.GRB.BINARY, name=f"indicator_{name}"
        )
        # trigger_exp + M * (1 - indicator_var) >= eps + trigger_value - 1
        self._model.addConstr(
            lhs=trigger_exp + 1000 * (1 - indicator_var),
            sense=grb.GRB.GREATER_EQUAL,
            rhs=eps + trigger_value - 1,
            name=f"bigM_constr1_{name}",
        )
        # trigger_exp - M * indicator_var <= trigger_value - 1
        self._model.addConstr(
            lhs=trigger_exp - 1000 * indicator_var,
            sense=grb.GRB.LESS_EQUAL,
            rhs=trigger_value - 1,
            name=f"bigM_constr2_{name}",
        )

        self._model.addGenConstrIndicator(
            binvar=indicator_var,
            binval=1,
            lhs=lhs,
            sense=sense,
            rhs=rhs,
            name=name,
        )

    def set_objective(self, sense: str = grb.GRB.MINIMIZE) -> None:
        self._model.setObjective(self._objective, sense)

    def add_objective_term(self, coefficient: float, variable: grb.Var) -> None:
        self._objective += coefficient * variable

    def optimize(self, threads: int = 4) -> None:
        print(self._model)

        self._model.setParam("Threads", threads)
        self._model.optimize()
        if self.get_status() in [3, 4]:
            self._model.computeIIS()
            self._model.write("model.ilp")
            raise Exception("The problem is infeasible")

    def get_solution(self) -> dict:
        return {var.varName: var.x for var in self._model.getVars()}

    def get_objective_value(self) -> float:
        return self._model.ObjVal

    def get_status(self) -> str:
        return self._model.status

    def get_solution_time(self) -> float:
        return self._model.Runtime

    def get_mip_gap(self) -> float:
        return self._model.MIPGap

    def get_num_vars(self) -> int:
        return self._model.NumVars

    def get_num_constrs(self) -> int:
        return self._model.NumConstrs

    def get_num_nodes(self) -> int:
        return self._model.NumNodes

    def get_num_solutions(self) -> int:
        return self._model.SolCount

    def get_num_iterations(self) -> int:
        return self._model.IterCount

    def get_variable(self, variable: ArcDrivenBy) -> grb.Var:
        return self._variables.get(variable, 0)

    def export_model(self, path: str) -> None:
        self._model.write(path + "model.rlp")
