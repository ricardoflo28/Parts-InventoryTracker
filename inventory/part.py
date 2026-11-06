"""Part: the data for one inventory item. No database or GUI code in here."""
from dataclasses import dataclass
from typing import Optional


@dataclass
class Part:
    part_number: str
    name: str
    quantity: int = 0
    reorder_level: int = 0
    location: str = ""
    id: Optional[int] = None  # set by the database when the part is saved

    def is_low_stock(self) -> bool:
        """A part is low on stock when quantity has dropped to its reorder level."""
        return self.quantity <= self.reorder_level

    
