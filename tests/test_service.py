import unittest

from inventory.repository import PartRepository
from inventory.service import InventoryService


class TestInventoryService(unittest.TestCase):
    def setUp(self):
        self.repo = PartRepository(":memory:")
        self.service = InventoryService(self.repo)

    def tearDown(self):
        self.repo.close()

    def test_add_part_saves_it(self):
        part = self.service.add_part("A-100", "Hinge", 10, 5, "Bin 1")
        self.assertIsNotNone(part.id)

    def test_blank_part_number_rejected(self):
        with self.assertRaises(ValueError):
            self.service.add_part("  ", "Hinge")

    def test_negative_quantity_rejected(self):
        with self.assertRaises(ValueError):
            self.service.add_part("A-100", "Hinge", quantity=-1)

    def test_duplicate_part_number_rejected(self):
        self.service.add_part("A-100", "Hinge")
        with self.assertRaises(ValueError):
            self.service.add_part("A-100", "Another hinge")

    def test_update_quantity(self):
        part = self.service.add_part("A-100", "Hinge", 10)
        self.service.update_quantity(part.id, 3)
        self.assertEqual(self.repo.find_by_id(part.id).quantity, 3)

    def test_update_quantity_rejects_negative(self):
        part = self.service.add_part("A-100", "Hinge", 10)
        with self.assertRaises(ValueError):
            self.service.update_quantity(part.id, -5)

    def test_remove_unknown_id_rejected(self):
        with self.assertRaises(ValueError):
            self.service.remove_part(999)

    def test_low_stock_only_returns_low_parts(self):
        self.service.add_part("A-100", "Hinge", quantity=2, reorder_level=5)
        self.service.add_part("B-200", "Bracket", quantity=50, reorder_level=5)
        low = self.service.get_low_stock_parts()
        self.assertEqual([p.part_number for p in low], ["A-100"])


if __name__ == "__main__":
    unittest.main()
