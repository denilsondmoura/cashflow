from decimal import Decimal
from dataclasses import dataclass

@dataclass
class Currency:
    value: Decimal

    def __post_init__(self):
        if not isinstance(self.value, Decimal):
            self.value = Decimal(str(self.value))

    def mask_value(self):
        return "R$ {0:.2f}".format(self.value)

    def __add__(self, other):
        if isinstance(other, Currency):
            return Currency(self.value + other.value)
        return Currency(self.value + Decimal(str(other)))

    def __radd__(self, other):
        if other == 0:
            return self
        return self.__add__(other)

    def __sub__(self, other):
        if isinstance(other, Currency):
            return Currency(self.value - other.value)
        return Currency(self.value - Decimal(str(other)))

    def __truediv__(self, other):
        if isinstance(other, (int, float, Decimal)):
            return Currency(self.value / Decimal(str(other)))
        raise TypeError("Unsupported operand type for /")

    def __lt__(self, other):
        if isinstance(other, Currency):
            return self.value < other.value
        return self.value < Decimal(str(other))

    def __gt__(self, other):
        if isinstance(other, Currency):
            return self.value > other.value
        return self.value > Decimal(str(other))

    def __le__(self, other):
        if isinstance(other, Currency):
            return self.value <= other.value
        return self.value <= Decimal(str(other))

    def __ge__(self, other):
        if isinstance(other, Currency):
            return self.value >= other.value
        return self.value >= Decimal(str(other))