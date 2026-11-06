# Parts Inventory Tracker

A small web app for tracking parts in stock. You can add parts, change quantities, remove parts, search, and see which parts are running low. Data is stored in a SQLite database file, `parts.db`, in the project folder.

Open the app in your browser at http://127.0.0.1:5000

---

## Quick start

Run all commands from the folder that contains `app.py`.

```
pip install flask            # install the web framework
python app.py                # start the app -> open http://127.0.0.1:5000
python -m unittest -v        # run the tests
```

**Requirements:** Python 3.9 or newer, plus Flask. SQLite comes with Python, so nothing else needs to be installed.

> **Note:** `python app.py` starts the web server, which keeps running until you press Ctrl+C in that terminal. If the browser says it can't connect, the server isn't running.

---

## What you can do

| Action | How |
|---|---|
| Add a part | Fill in the form at the bottom of the page and click **Add Part** |
| See all parts | The table on the home page |
| Search | Type in the search box and click **Search** |
| Change a quantity | Type a new number in the row's box and click **Update** |
| Remove a part | Click **Remove** on the row and confirm |
| See low-stock parts | Click **Low Stock Only** |

A part is **low on stock** when its quantity is less than or equal to its reorder level. Low parts are highlighted in the table.

Search matches part numbers and names anywhere in the text, and it ignores capital letters for plain letters. Results are sorted by part number.

---

## How the code is organized

The code is split into layers. Each layer only talks to the one directly below it:

```
   app.py (web pages)  ──>  inventory/service.py  ──>  inventory/repository.py  ──>  parts.db
                              business rules             SQL statements              SQLite file
```

| Layer | File | Its job | What it does *not* do |
|---|---|---|---|
| Data | `inventory/part.py` | Defines what one part is and the low-stock check | No database, no web code |
| Storage | `inventory/repository.py` | Saves, loads, searches, and deletes rows | No validation rules, no web code |
| Rules | `inventory/service.py` | Checks input and enforces the rules below | No SQL, no web code |
| Web pages | `app.py` | Routes, forms, and flash messages | Never runs SQL or changes data directly |

The service layer holds all the rules, so if you add another screen later it can reuse them without copying any logic.

### Project layout

```
parts_inventory_tracker/
├── app.py                  Web app (Flask). Run this to start the app.
├── parts.db                Your data. Created on first run if it's missing.
├── inventory/
│   ├── __init__.py
│   ├── part.py             The Part data class.
│   ├── repository.py       All SQL lives here.
│   └── service.py          Validation and business rules.
├── templates/
│   ├── base.html           Shared page layout and flash messages.
│   └── index.html          Home page: search, table, and add form.
├── static/
│   └── style.css           Styling for the web pages.
└── tests/
    ├── test_repository.py  Tests for the storage layer.
    └── test_service.py     Tests for the rules.
```

---

## Walkthrough: changing a quantity

Here is what happens when you change a part's quantity:

1. You type `12` in the row's box and click **Update**. The browser sends `POST /update/7` with `new_quantity=12`.
2. `app.py` (`update_quantity`) reads the number. Blank or non-numeric input is rejected with a readable message.
3. `service.update_quantity` checks that the quantity isn't negative and that part 7 exists.
4. `repository.find_by_id` loads part 7. The service sets the new quantity, and `repository.update` runs `UPDATE parts ... WHERE id = ?` and saves it.
5. The app shows a "Quantity updated." message and redirects to the home page, which reloads the table.

---

## The database

One table, `parts`, created automatically the first time the app starts:

| Column | Type | Notes |
|---|---|---|
| `id` | INTEGER | Primary key. Assigned by the database and never reused. |
| `part_number` | TEXT | Required and unique. |
| `name` | TEXT | Required. |
| `quantity` | INTEGER | Defaults to 0. |
| `reorder_level` | INTEGER | Defaults to 0. Low stock when quantity is at or below this. |
| `location` | TEXT | Optional, for example `Shelf A2`. |

Every query uses `?` placeholders, so user input is never pasted into SQL text. This prevents SQL injection.

---

## Business rules

The service layer enforces these rules. Each broken rule raises a `ValueError` with a message that the page shows to the user.

| Rule | Where it is checked | Message |
|---|---|---|
| Part number can't be blank (spaces are trimmed first) | `service.add_part` | `part_number cannot be blank.` |
| Name can't be blank | `service.add_part` | `name cannot be blank.` |
| Quantity and reorder level can't be negative | `service.add_part` | `quantity cannot be negative.` |
| Quantity can't be set to a negative number | `service.update_quantity` | `Quantity cannot be negative.` |
| Part number must be unique | `repository.add`, from the database's UNIQUE constraint | `part_number 'A-100' already exists.` |
| Can't update or remove an ID that doesn't exist | `service.update_quantity`, `service.remove_part` | `Part with id 99 does not exist.` |
| Numbers must be whole numbers | `app.py` (`_whole_number`) | `Quantity must be a whole number.` |

---

## Running the tests

```
python -m unittest -v
```

There are 16 tests. The repository tests check each database operation, including that search treats `%` and `_` as ordinary characters. The service tests check each business rule. Every test uses a fresh in-memory database, so the tests never touch `parts.db`.

---

## Known limitations

- **Only quantity can be edited after a part is added.** Name, location, reorder level, and part number can't be changed yet. The repository already has an `update` method, so this is mostly a new service method and a form.
- **Part numbers are case-sensitive.** `A-100` and `a-100` can both exist as separate parts.
- **No history.** Quantity changes aren't logged, so you can't see past values.
- **Single user.** The app isn't built for several people changing data at the same time.
- **Local use only.** `app.py` runs with Flask's debug mode and a placeholder secret key. Don't expose it to a network.

---

## Troubleshooting

| Problem | Fix |
|---|---|
| Browser says it can't connect to 127.0.0.1:5000 | Run `python app.py` in a terminal and leave that terminal open. |
| `ModuleNotFoundError: No module named 'flask'` | Run `pip install flask`. |
| Tests aren't found | Run `python -m unittest -v` from the folder that contains `tests/`. |
