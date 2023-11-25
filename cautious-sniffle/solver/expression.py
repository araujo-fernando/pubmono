from typing import Union
import warnings

warnings.filterwarnings("ignore")

import operator as op

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


class Expression:
    def __init__(
        self,
        a,
        op,
        b,
        lefts: list | None = None,
        operators: list | None = None,
        rights: list | None = None,
    ) -> None:
        if lefts is not None and operators is not None and rights is not None:
            lefts.append(a)
            self.a = lefts
            operators.append(op)
            self.op = operators
            rights.append(b)
            self.b = rights

        elif lefts is None and operators is None and rights is None:
            self.a = [a]
            self.op = [op]
            self.b = [b]
        else:
            raise ValueError(
                "All or none of lefts, operators and rights must be specified"
            )

    @property
    def value(self) -> Union[float, int]:
        result = 0
        for position in range(len(self.a)):
            val_a = self.a[position]
            val_b = self.b[position]
            op = self.op[position]

            if val_a is None:
                left_value = result
            else:
                try:
                    left_value = val_a.value
                except AttributeError:
                    left_value = val_a

            if val_b is None:
                right_value = result
            else:
                try:
                    right_value = val_b.value
                except AttributeError:
                    right_value = val_b

            try:
                result = op(left_value, right_value)
            except ZeroDivisionError:
                result = float("inf")

        return result

    def __repr__(self) -> str:
        # op_name = self.op.__name__
        # op = _OPERADORES.get(op_name, op_name)
        # return f"{self.a} {op} {self.b}"

        representation = ""
        for position in range(len(self.a)):
            val_a = self.a[position]
            val_b = self.b[position]
            op_name = self.op[position].__name__
            op = _OPERADORES.get(op_name, op_name)
            if val_a is None:
                left_value = representation
            else:
                left_value = val_a

            if val_b is None:
                right_value = representation
            else:
                right_value = val_b

            representation = f"({left_value} {op} {right_value})"

        return representation

    def __str__(self) -> str:
        # op_name = self.op.__name__
        # op = _OPERADORES.get(op_name, op_name)
        # return f"({self.a} {op} {self.b})"

        representation = ""
        for position in range(len(self.a)):
            val_a = self.a[position]
            val_b = self.b[position]
            op_name = self.op[position].__name__
            op = _OPERADORES.get(op_name, op_name)
            if val_a is None:
                left_value = representation
            else:
                left_value = val_a

            if val_b is None:
                right_value = representation
            else:
                right_value = val_b

            representation = f"({left_value} {op} {right_value})"

        return representation

    def __add__(self, other):
        return Expression(
            None,
            op.add,
            other,
            lefts=self.a.copy(),
            operators=self.op.copy(),
            rights=self.b.copy(),
        )

    def __sub__(self, other):
        return Expression(
            None,
            op.sub,
            other,
            lefts=self.a.copy(),
            operators=self.op.copy(),
            rights=self.b.copy(),
        )

    def __mul__(self, other):
        return Expression(
            None,
            op.mul,
            other,
            lefts=self.a.copy(),
            operators=self.op.copy(),
            rights=self.b.copy(),
        )

    def __truediv__(self, other):
        return Expression(
            None,
            op.truediv,
            other,
            lefts=self.a.copy(),
            operators=self.op.copy(),
            rights=self.b.copy(),
        )

    def __floordiv__(self, other):
        return Expression(
            None,
            op.floordiv,
            other,
            lefts=self.a.copy(),
            operators=self.op.copy(),
            rights=self.b.copy(),
        )

    def __pow__(self, other):
        return Expression(
            None,
            op.pow,
            other,
            lefts=self.a.copy(),
            operators=self.op.copy(),
            rights=self.b.copy(),
        )

    def __lt__(self, other):
        return Expression(
            None,
            op.lt,
            other,
            lefts=self.a.copy(),
            operators=self.op.copy(),
            rights=self.b.copy(),
        )

    def __le__(self, other):
        return Expression(
            None,
            op.le,
            other,
            lefts=self.a.copy(),
            operators=self.op.copy(),
            rights=self.b.copy(),
        )

    def __eq__(self, other):
        return Expression(
            None,
            op.eq,
            other,
            lefts=self.a.copy(),
            operators=self.op.copy(),
            rights=self.b.copy(),
        )

    def __ge__(self, other):
        return Expression(
            None,
            op.ge,
            other,
            lefts=self.a.copy(),
            operators=self.op.copy(),
            rights=self.b.copy(),
        )

    def __gt__(self, other):
        return Expression(
            None,
            op.gt,
            other,
            lefts=self.a.copy(),
            operators=self.op.copy(),
            rights=self.b.copy(),
        )

    def __radd__(self, other):
        return Expression(
            other,
            op.add,
            None,
            lefts=self.a.copy(),
            operators=self.op.copy(),
            rights=self.b.copy(),
        )

    def __rsub__(self, other):
        return Expression(
            other,
            op.sub,
            None,
            lefts=self.a.copy(),
            operators=self.op.copy(),
            rights=self.b.copy(),
        )

    def __rmul__(self, other):
        return Expression(
            other,
            op.mul,
            None,
            lefts=self.a.copy(),
            operators=self.op.copy(),
            rights=self.b.copy(),
        )

    def __rtruediv__(self, other):
        return Expression(
            other,
            op.truediv,
            None,
            lefts=self.a.copy(),
            operators=self.op.copy(),
            rights=self.b.copy(),
        )

    def __rfloordiv__(self, other):
        return Expression(
            other,
            op.floordiv,
            None,
            lefts=self.a.copy(),
            operators=self.op.copy(),
            rights=self.b.copy(),
        )

    def __rpow__(self, other):
        return Expression(
            other,
            op.pow,
            None,
            lefts=self.a.copy(),
            operators=self.op.copy(),
            rights=self.b.copy(),
        )

    def __rlt__(self, other):
        return Expression(
            other,
            op.lt,
            None,
            lefts=self.a.copy(),
            operators=self.op.copy(),
            rights=self.b.copy(),
        )

    def __rle__(self, other):
        return Expression(
            other,
            op.le,
            None,
            lefts=self.a.copy(),
            operators=self.op.copy(),
            rights=self.b.copy(),
        )

    def __req__(self, other):
        return Expression(
            other,
            op.eq,
            None,
            lefts=self.a.copy(),
            operators=self.op.copy(),
            rights=self.b.copy(),
        )

    def __rge__(self, other):
        return Expression(
            other,
            op.ge,
            None,
            lefts=self.a.copy(),
            operators=self.op.copy(),
            rights=self.b.copy(),
        )

    def __rgt__(self, other):
        return Expression(
            other,
            op.gt,
            None,
            lefts=self.a.copy(),
            operators=self.op.copy(),
            rights=self.b.copy(),
        )
