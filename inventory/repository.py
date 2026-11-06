import sqlite3
from typing import List, Optional

from .part import Part


class PartRepository:
    def __init__(self, db_path: str = "parts.db"):

        # check_same_thread=False is needed because Flask's dev server can
        # handle requests on a different thread than the one that opened
        # this connection. Safe here since this app only has one user at a time.
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row  # lets you read columns by name
        self._create_table()

    def _create_table(self) -> None:
        # IF NOT EXISTS matters because this runs every time the app starts -
        # without it, the second launch would crash saying the table already exists.
        self.conn.execute(
            """
            CREATE TABLE IF NOT EXISTS parts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                part_number TEXT NOT NULL UNIQUE,
                name TEXT NOT NULL,
                quantity INTEGER NOT NULL DEFAULT 0,
                reorder_level INTEGER NOT NULL DEFAULT 0,
                location TEXT NOT NULL DEFAULT ''
            )
            """
        )
        self.conn.commit()
        # lastrowid gives us the id SQLite just assigned, so the caller gets
        # back a complete Part instead of one with id=None.

    @staticmethod
    def _row_to_part(row: sqlite3.Row) -> Part:
        return Part(
            id=row["id"],
            part_number=row["part_number"],
            name=row["name"],
            quantity=row["quantity"],
            reorder_level=row["reorder_level"],
            location=row["location"],
        )

    def add(self, part: Part) -> Part:
        """Insert a part and return it with its new id. Use this as your pattern."""
        cur = self.conn.execute(
            "INSERT INTO parts (part_number, name, quantity, reorder_level, location) "
            "VALUES (?, ?, ?, ?, ?)",
            (part.part_number, part.name, part.quantity, part.reorder_level, part.location),
        )
        self.conn.commit()
        part.id = cur.lastrowid
        return part

    def find_by_id(self, part_id: int) -> Optional[Part]:
        # The ? is a placeholder - SQLite fills it in safely, which avoids
        # SQL injection. Never build this string with an f-string instead.
        cursor = self.conn.execute("SELECT * FROM parts WHERE id = ?", (part_id,))
        row = cursor.fetchone()
        if row is None:
            return None
        return self._row_to_part(row)

    def find_all(self) -> List[Part]:
        cursor = self.conn.execute("SELECT * FROM parts ORDER BY part_number")
        rows = cursor.fetchall()
        return [self._row_to_part(row) for row in rows]

    def update(self, part: Part) -> None:
        # WHERE id = ? is critical here - without it, this would overwrite
        # every row in the table instead of just one.
        self.conn.execute(
            "UPDATE parts SET part_number=?, name=?, quantity=?, reorder_level=?, location=? "
            "WHERE id = ?",
            (part.part_number, part.name, part.quantity,
             part.reorder_level, part.location, part.id),
        )
        self.conn.commit()

    def delete(self, part_id: int) -> None:
        self.conn.execute("DELETE FROM parts WHERE id = ?", (part_id,))
        self.conn.commit()

    def search(self, text: str) -> List[Part]:
        # % is a wildcard in SQL LIKE, meaning "any characters." Wrapping the
        # search text in % on both sides matches it anywhere in the field,
        # not just at the start or end.
        pattern = f"%{text}%"
        cursor = self.conn.execute(
            "SELECT * FROM parts WHERE part_number LIKE ? OR name LIKE ? ORDER BY part_number",
            (pattern, pattern),
        )
        return [self._row_to_part(row) for row in cursor.fetchall()]

    def close(self) -> None:
        self.conn.close()