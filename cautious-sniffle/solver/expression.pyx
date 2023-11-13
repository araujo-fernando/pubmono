# expression_cython.pyx
import operator as op
from typing import Union

_OPERADORES = {
    "add": "+",
    "sub": "-",
    "mul": "*",
    "truediv": "/",
    "floordiv": "//",
    "pow": "^",
    "lt": "<",
    "le": "<=",
    "eq": "=",
    "ge": ">=",
    "gt": ">",
}

cdef class Expression:
    cdef public object a
    cdef public object b
    cdef public object op

    def __init__(self, a, op, b):
        self.a = a
        self.op = op
        self.b = b

    @property
    def value(self) -> Union[float, int]:
        try:
            val_a = self.a.value
        except AttributeError:
            val_a = self.a
        try:
            val_b = self.b.value
        except AttributeError:
            val_b = self.b

        return self.op(val_a, val_b)

    def __repr__(self):
        op_name = self.op.__name__
        op = _OPERADORES.get(op_name, op_name)
        return f"{self.a} {op} {self.b}"

    def __str__(self):
        op_name = self.op.__name__
        op = _OPERADORES.get(op_name, op_name)
        return f"({self.a} {op} {self.b})"

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
