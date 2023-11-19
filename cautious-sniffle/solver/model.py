from __future__ import annotations
from copy import deepcopy

from .expression import Expression
from .variables import RealVariable, BinVariable, IntVariable


class Model:
    def __init__(self) -> None:
        self._objectives: list[Expression] = list()
        self._vars: dict[str, RealVariable | BinVariable | IntVariable] = dict()
        self._constraints: list[Expression] = list()
        self._penalty = None

    @property
    def num_vars(self):
        return len(self._vars)

    @property
    def variables(self):
        return deepcopy(self._vars)

    @property
    def variables_values(self) -> dict[str, float]:
        return {name: var.value for name, var in self._vars.items()}

    @property
    def export_solution(self) -> dict[str, float]:
        return {var.name: var.value for var in self._vars.values()}

    @property
    def objectives(self):
        return deepcopy(self._objectives)

    @property
    def objective_values(self) -> list[float]:
        objs = list(obj.value for obj in self._objectives)
        if self._penalty is not None:
            objs.append(self._penalty)

        return objs

    def get_objective_x(self, id: int):
        if id >= len(self._objectives):
            raise ValueError(f"ID must be between 0 and {len(self._objectives)-1}.")

        return self._objectives[id]

    def set_objective_x(self, expression, id: int = 0):
        if id > len(self._objectives):
            raise ValueError(f"ID must be between 0 and {len(self._objectives)}.")
        
        if id == len(self._objectives):
            self._objectives.append(expression)
        else:
            self._objectives[id] = expression

    def set_objective(self, expression):
        self.set_objective_x(expression, 0)

    def create_binary_variables(self, name: str, data: list):
        new_vars = {val: BinVariable(name + str(val)) for val in data}
        for v in new_vars.values():
            self._vars[v.name] = v
        return new_vars

    def create_integer_variables(self, name: str, data: list, lb=None, ub=None):
        new_vars = {val: IntVariable(name + str(val), lb, ub) for val in data}
        for v in new_vars.values():
            self._vars[v.name] = v
        return new_vars

    def create_real_variables(self, name: str, data: list, lb=None, ub=None):
        new_vars = {val: RealVariable(name + str(val), lb, ub) for val in data}
        for v in new_vars.values():
            self._vars[v.name] = v
        return new_vars

    def create_binary_variable(self, name: str):
        new_var = BinVariable(name)
        self._vars[name] = new_var
        return new_var

    def create_integer_variable(self, name: str, lb=None, ub=None):
        new_var = IntVariable(name, lb, ub)
        self._vars[name] = new_var
        return new_var

    def create_real_variable(self, name: str, lb=None, ub=None):
        new_var = RealVariable(name, lb, ub)
        self._vars[name] = new_var
        return new_var

    def copy(self) -> Model:
        return deepcopy(self)

    def set_variables_values(self, var_values: dict[str, int | float]):
        for var, val in var_values.items():
            if var in self._vars:
                self._vars[var].value = val  # type: ignore

    def get_variables_values(self) -> dict[str, int | float]:
        return {var.name: var.value for var in self._vars.values()}

    def set_constraint_violation_penalty(self, value: float):
        self._penalty = value

    def get_objective_values(self) -> list[float]:
        objs = list(obj.value for obj in self._objectives)
        if self._penalty is not None:
            objs.append(self._penalty)

        return objs

    def insert_lt_zero_constraint(self, constraint: Expression):
        """
        Insert a constraint in the form:
            expression <= 0

        :param constraint: left hand side of expression
        :type constraint: Expression
        """
        self._constraints.append(constraint)

    def insert_eq_zero_constraint(self, constraint: Expression):
        """
        Insert a constraint in the form:
            expression = 0

        As two constraints in the form:
            expression <= 0
            -1 * expression <= 0

        :param constraint: left hand side of expression
        :type constraint: Expression
        """
        self._constraints.append(constraint)
        self._constraints.append(-1*constraint)

    def insert_lt_zero_constraints(self, constraints: list[Expression]):
        """
        Insert a constraint in the form:
            expression <= 0

        :param constraint: left hand side of expression
        :type constraint: Expression
        """
        for cnstrt in constraints:
            self._constraints.append(cnstrt)

    def insert_eq_zero_constraints(self, constraints: list[Expression]):
        """
        Insert a constraint in the form:
            expression = 0

        As two constraints in the form:
            expression <= 0
            -1 * expression <= 0

        :param constraint: left hand side of expression
        :type constraint: Expression
        """
        for cnstrt in constraints:
            self._constraints.append(cnstrt)
            self._constraints.append(-1*cnstrt)