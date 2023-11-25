from re import L
from typing import Iterable
import numpy as np

from copy import deepcopy
from .expression import Expression
from .variables import RealVariable, BinVariable, IntVariable

class Model:
    def __init__(self) -> None:
        self._objectives: list = list()
        self._constraints: list = list()

        self._variables: dict[str, RealVariable | BinVariable | IntVariable] = dict()
        self._variables_values: dict[RealVariable | BinVariable | IntVariable, float] = dict()
        self._variables_lower_bounds: dict[RealVariable | BinVariable | IntVariable, float | None] = dict()
        self._variables_upper_bounds: dict[RealVariable | BinVariable | IntVariable, float | None] = dict()

        self._integer_vars = set()

        self._penalty = 1e-3

    @property
    def num_vars(self):
        return len(self._variables)

    @property
    def variables(self):
        return deepcopy(self._variables)

    @property
    def variables_values(self) -> dict[RealVariable | BinVariable | IntVariable, float]:
        return self._variables_values.copy()

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

    def _set_variables_bounds(self, variables: Iterable, lb, ub):
        self._variables_lower_bounds.update({v: lb for v in variables})
        self._variables_upper_bounds.update({v: ub for v in variables})

    def create_binary_variables(self, name: str, data: list):
        new_vars = {val: BinVariable(name + str(val)) for val in data}
        for v in new_vars.values():
            self._variables[v.name] = v

        self._set_variables_bounds(new_vars.values(), 0, 1)
        self._integer_vars.update([var for var in new_vars.values()])

        return new_vars

    def create_integer_variables(self, name: str, data: list, lb=None, ub=None):
        new_vars = {val: IntVariable(name + str(val), lb=lb, ub=ub) for val in data}
        for v in new_vars.values():
            self._variables[v.name] = v

        self._set_variables_bounds(new_vars.values(), lb, ub)
        self._integer_vars.update([var for var in new_vars.values()])

        return new_vars

    def create_real_variables(self, name: str, data: list, lb=None, ub=None):
        new_vars = {val: RealVariable(name + str(val), lb=lb, ub=ub) for val in data}
        for v in new_vars.values():
            self._variables[v.name] = v

        self._set_variables_bounds(new_vars.values(), lb, ub)

        return new_vars

    def create_binary_variable(self, name: str):
        new_var = BinVariable(name)
        self._variables[new_var.name] = new_var
        self._variables_lower_bounds[new_var] = 0
        self._variables_upper_bounds[new_var] = 1
        self._integer_vars.add(new_var)
        return new_var

    def create_integer_variable(self, name: str, lb=None, ub=None):
        new_var = IntVariable(name, lb=lb, ub=ub)
        self._variables[new_var.name] = new_var
        self._variables_lower_bounds[new_var] = lb
        self._variables_upper_bounds[new_var] = ub
        self._integer_vars.add(new_var)
        return new_var

    def create_real_variable(self, name: str, lb=None, ub=None):
        new_var = RealVariable(name, lb=lb, ub=ub)
        self._variables[new_var.name] = new_var
        self._variables_lower_bounds[new_var] = lb
        self._variables_upper_bounds[new_var] = ub
        return new_var

    def copy(self):
        return deepcopy(self)

    def set_variables_values(self, var_values: dict[BinVariable | IntVariable | RealVariable, int | float]):
        for var, val in var_values.items():
            if var.name not in self._variables:
                raise ValueError(f"Variable {var} not found in model.")

            var.set_value(val)
            self._variables_values[var] = var.value

    def get_variables_values(self) -> dict[str, int | float]:
        return {var.name: value for var, value in self._variables_values.items()}

    def set_constraint_violation_penalty(self, value: float):
        self._penalty = value

    def get_random_variables_values(self) -> dict[BinVariable | IntVariable | RealVariable, int | float]:
        return {
            var: var.get_random_value()
            for var in self._variables.values()
        }

    def set_random_variables_values(self):
        for var in self._variables.values():
            self._variables_values[var] = var.set_random_value()

    def insert_lt_zero_constraint(self, constraint):
        """
        Insert a constraint in the form:
            expression <= 0

        :param constraint: left hand side of expression
        :type constraint: Expression
        """
        self._constraints.append(constraint)

    def insert_eq_zero_constraint(self, constraint):
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

    def insert_lt_zero_constraints(self, constraints: list):
        """
        Insert a constraint in the form:
            expression <= 0

        :param constraint: left hand side of expression
        :type constraint: Expression
        """
        for cnstrt in constraints:
            self._constraints.append(cnstrt)

    def insert_eq_zero_constraints(self, constraints: list):
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