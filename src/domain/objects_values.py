from decimal import Decimal
from dataclasses import dataclass

@dataclass
class Currency:
    value: Decimal

    def mask_value(self):
        return "R$ {0:.2f}".format(self.value)