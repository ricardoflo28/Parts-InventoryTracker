"""InventoryService: the business rules. No SQL and no print/input in here.

Rules to enforce (raise ValueError with a clear message when broken):
  - part_number and name cannot be blank
  - quantity and reorder_level cannot be negative
  - part_number must be unique
  - you cannot update or remove a part id that does not exist
"""
import sqlite3
from typing import List

from .part import Part
from .repository import PartRepository


class InventoryService:
    def __init__(self, repo: PartRepository):
        self.repo = repo

    def add_part(
        self,
        part_number: str,
        name: str,
        quantity: int = 0,
        reorder_level: int = 0,
        location: str = "",
    ) -> Part:
        # strip() removes accidental leading/trailing spaces from form input
        # before validating, so "  " doesn't slip past the blank check.
        part_number = part_number.strip()
        name = name.strip()
        if not part_number:
            raise ValueError("part_number cannot be blank.")
        if not name:
            raise ValueError("name cannot be blank.")
        if quantity < 0:
            raise ValueError("quantity cannot be negative.")
        if reorder_level < 0:
            raise ValueError("reorder_level cannot be negative.")

        # id=None because the database assigns the real id on insert -
        # see PartRepository.add(), which sets it from cur.lastrowid.
        part = Part(
            id=None,
            part_number=part_number,
            name=name,
            quantity=quantity,
            reorder_level=reorder_level,
            location=location,
        )
        try:
            return self.repo.add(part)
        except sqlite3.IntegrityError:
            # The database's unique constraint on part_number is what actually
            # catches duplicates. We catch its low-level error here and
            # re-raise it as a ValueError, so the UI layers only ever need
            # to handle one exception type, not SQLite-specific ones.
            raise ValueError(f"part_number '{part_number}' already exists.")

    def update_quantity(self, part_id: int, new_quantity: int) -> None:
        if new_quantity < 0:
            raise ValueError("Quantity cannot be negative.")
        
        # Look the part up first so we can reject updates to an id that
        # doesn't exist, rather than silently doing nothing.
        part = self.repo.find_by_id(part_id)
        if part is None:
            raise ValueError(f"Part with id {part_id} does not exist.")

        part.quantity = new_quantity
        self.repo.update(part)

    def remove_part(self, part_id: int) -> None:
        # Same existence check as update_quantity - you can't remove
        # something that isn't there.
        part = self.repo.find_by_id(part_id)
        if part is None:
            raise ValueError(f"Part with id {part_id} does not exist.")
        self.repo.delete(part_id)

    def list_parts(self) -> List[Part]:
        return self.repo.find_all()

    def search(self, text: str) -> List[Part]:
        text = text.strip()
        if not text:
            return self.list_parts()
        return self.repo.search(text)

    def get_low_stock_parts(self) -> List[Part]:
        # List comprehension with a filter: keep every part where
        # is_low_stock() is True. Reuses list_parts() rather than writing
        # a separate database query
        return [p for p in self.list_parts() if p.is_low_stock()]