import unittest

from inventory.part import Part
from inventory.repository import PartRepository


class TestPartRepository(unittest.TestCase):
    def setUp(self):
        self.repo = PartRepository(":memory:")  # fresh empty database per test

    def tearDown(self):
        self.repo.close()

    def make(self, number="A-100", name="Hinge", qty=10, reorder=5, loc="Bin 1"):
        return self.repo.add(Part(number, name, qty, reorder, loc))

    def test_add_assigns_id(self):
        self.assertIsNotNone(self.make().id)

    def test_find_by_id(self):
        saved = self.make()
        self.assertEqual(self.repo.find_by_id(saved.id).name, "Hinge")

    def test_find_by_id_missing_returns_none(self):
        self.assertIsNone(self.repo.find_by_id(999))

    def test_find_all(self):
        self.make("A-100", "Hinge")
        self.make("B-200", "Bracket")
        self.assertEqual(len(self.repo.find_all()), 2)

    def test_update(self):
        saved = self.make()
        saved.quantity = 42
        self.repo.update(saved)
        self.assertEqual(self.repo.find_by_id(saved.id).quantity, 42)

    def test_delete(self):
        saved = self.make()
        self.repo.delete(saved.id)
        self.assertIsNone(self.repo.find_by_id(saved.id))

    def test_search_matches_name_or_part_number(self):
        self.make("A-100", "Hinge")
        self.make("B-200", "Bracket")
        self.assertEqual(len(self.repo.search("hing")), 1)
        self.assertEqual(len(self.repo.search("B-2")), 1)


if __name__ == "__main__":
    unittest.main()
