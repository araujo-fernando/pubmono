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

cdef double c_value(self):
    cdef double val_a, val_b
    try:
        val_a = (<Expression>self.a).c_value()
    except AttributeError:
        val_a = <double>self.a
    try:
        val_b = (<Expression>self.b).c_value()
    except AttributeError:
        val_b = <double>self.b

    cdef double result
    if self.op == op.add:
        result = val_a + val_b
    elif self.op == op.sub:
        result = val_a - val_b
    elif self.op == op.mul:
        result = val_a * val_b
    elif self.op == op.truediv:
        result = val_a / val_b
    elif self.op == op.floordiv:
        result = <int>(val_a / val_b)
    elif self.op == op.pow:
        result = pow(val_a, val_b)
    elif self.op == op.lt:
        result = val_a < val_b
    elif self.op == op.le:
        result = val_a <= val_b
    elif self.op == op.eq:
        result = val_a == val_b
    elif self.op == op.ge:
        result = val_a >= val_b
    elif self.op == op.gt:
        result = val_a > val_b
    else:
        raise ValueError(f"Invalid operator: {self.op.__name__}")

    return result

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
