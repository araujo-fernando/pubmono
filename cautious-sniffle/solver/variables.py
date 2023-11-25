from ast import In
import re
import sys

import numpy as np
import operator as op
import random as rd

from enum import Enum, auto

from .expression import Expression


class VarType(Enum):
    BINARY = auto()
    INTEGER = auto()
    REAL = auto()


_FORBIDDEN_NAME_PATTERN = re.compile(r"[^A-Z0-9_]")


class _Variable:
    def __init__(
        self, name: str, lb: float | int | None = None, ub: float | int | None = None
    ) -> None:
        name = str(name).upper().replace(" ", "_")
        self.name = _FORBIDDEN_NAME_PATTERN.sub("", name)
        self.lb = lb if lb is not None else sys.float_info.min
        self.ub = ub if ub is not None else sys.float_info.max

        self._value: float | int = 0 if self.lb <= 0 and self.ub >= 0 else self.lb
        self.type = None

    @property
    def value(self) -> int | float:
        return self._value

    def set_value(self, v):
        self._value = np.clip(v, self.lb, self.ub)

    def set_random_value(self):
        val = rd.uniform(self.lb, self.ub)
        self._value = val
        return val

    def get_random_value(self):
        val = rd.uniform(self.lb, self.ub)
        return val

    def __setattr__(self, name, value):
        if name == "value":
            self._value = np.clip(value, self.lb, self.ub)
        self.__dict__[name] = value

    def __hash__(self) -> int:
        return hash(self.name)

    def __repr__(self) -> str:
        return (
            f"({self.__class__.__name__}: {self.name}, bounds:[{self.lb}, {self.ub}])"
        )

    def __str__(self) -> str:
        return f"{self.name}"

    def __add__(self, other):
        return Expression(self, op.add, other)

    def __sub__(self, other):
        return Expression(self, op.sub, other)

    def __mul__(self, other):
        return Expression(self, op.mul, other)

    def __truediv__(self, other):
        return Expression(self, op.truediv, other)

    def __floordiv__(self, other):
        return Expression(self, op.floordiv, other)

    def __pow__(self, other):
        return Expression(self, op.pow, other)

    def __lt__(self, other):
        return Expression(self, op.lt, other)

    def __le__(self, other):
        return Expression(self, op.le, other)

    def __eq__(self, other):
        return Expression(self, op.eq, other)

    def __ge__(self, other):
        return Expression(self, op.ge, other)

    def __gt__(self, other):
        return Expression(self, op.gt, other)

    def __radd__(self, other):
        return Expression(other, op.add, self)

    def __rsub__(self, other):
        return Expression(other, op.sub, self)

    def __rmul__(self, other):
        return Expression(other, op.mul, self)

    def __rtruediv__(self, other):
        return Expression(other, op.truediv, self)

    def __rfloordiv__(self, other):
        return Expression(other, op.floordiv, self)

    def __rpow__(self, other):
        return Expression(other, op.pow, self)

    def __rlt__(self, other):
        return Expression(other, op.lt, self)

    def __rle__(self, other):
        return Expression(other, op.le, self)

    def __req__(self, other):
        return Expression(other, op.eq, self)

    def __rge__(self, other):
        return Expression(other, op.ge, self)

    def __rgt__(self, other):
        return Expression(other, op.gt, self)


class BinVariable(_Variable):
    def __init__(self, name) -> None:
        super().__init__(name, 0, 1)
        self.type = VarType.BINARY

    def set_value(self, v):
        self._value = int(v >= 0.5)


class IntVariable(_Variable):
    def __init__(self, name, lb=None, ub=None) -> None:
        super().__init__(name, lb, ub)
        self.type = VarType.INTEGER

    def set_value(self, v):
        self._value = np.round(np.clip(v, self.lb, self.ub))


class RealVariable(_Variable):
    def __init__(self, name, lb=None, ub=None) -> None:
        super().__init__(name, lb, ub)
        self.type = VarType.REAL

    def set_value(self, v):
        self._value = np.clip(v, self.lb, self.ub)
