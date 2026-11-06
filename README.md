# Parts Inventory Tracker

A small inventory app for tracking parts in stock. You can add parts, change quantities, remove parts, search, and see which parts are running low. It comes in two versions that share the same data and the same rules:

- **Web app** (`app.py`): open it in your browser at http://127.0.0.1:5000
- **Desktop window** (`main.py`): a tkinter window that runs on your computer

Data is stored in a SQLite database file, `parts.db`, in the project folder.

---

## Quick start

Run all commands from the folder that contains `app.py`.

```
pip install flask            # needed for the web app only
python app.py                # web app -> open http://127.0.0.1:5000
python main.py               # desktop window
python -m unittest -v        # run the tests
```

**Requirements:** Python 3.9 or newer. The desktop window and the tests use only the standard library. The web app also needs Flask. The tkinter window comes with the Windows and macOS installers from python.org. On Linux, install it with `python3-tk`.

> **Note:** `python app.py` starts the web server, which keeps running until you press Ctrl+C in that terminal. `python main.py` opens the desktop window instead, so it does not start the website. If the browser says it can't connect, the web server probably isn't running.

---

## What you can do

| Action | Web app | Desktop window |
|---|---|---|
| Add a part | Fill in the form at the bottom of the page and click **Add Part** | **Add Part** button, then answer each prompt |
| See all parts | The table on the home page | Shown on launch, or click **Show All** |
| Search | Type in the search box and click **Search** | **Search** button |
| Change a quantity | Type a new number in the row's box and click **Update** | Select a row, click **Update Quantity** |
| Remove a part | Click **Remove** on the row and confirm | Select a row, click **Remove Part** and confirm |
| See low-stock parts | Click **Low Stock Only** | Click **Low Stock** |

A part is **low on stock** when its quantity is less than or equal to its reorder level. Low parts are highlighted in the web table and shown in red in the desktop window.

Search matches part numbers and names anywhere in the text, and it ignores capital letters for plain letters. Results are sorted by part number.

---

## How the code is organized

The code is split into four layers. Each layer only talks to the one directly below it:

```
   app.py (web)  ──┐
                   ├──>  inventory/service.py  ──>  inventory/repository.py  ──>  parts.db
   main.py + gui.py┘      business rules              SQL statements              SQLite file
```

| Layer | File | Its job | What it does *not* do |
|---|---|---|---|
| Data | `inventory/part.py` | Defines what one part is and the low-stock check | No database, no screens |
| Storage | `inventory/repository.py` | Saves, loads, searches, and deletes rows | No validation rules, no screens |
| Rules | `inventory/service.py` | Checks input and enforces the rules below | No SQL, no screens |
| Screens | `app.py`, `gui.py` | Forms, buttons, tables, and messages | Never runs SQL or changes data directly |

`main.py` only launches the desktop window from `gui.py`. Both screens call the same `InventoryService`, so a rule only has to be written once.

### Project layout

```
parts_inventory_tracker/
├── app.py                  Web app (Flask). Run this for the browser version.
├── main.py                 Launches the desktop window.
├── gui.py                  The desktop window (tkinter).
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
│   └── style.css           Styling for the web app.
└── tests/
    ├── test_repository.py  Tests for the storage layer.
    └── test_service.py     Tests for the rules.
```

---

## Walkthrough: changing a quantity

Here is what happens when you change a part's quantity in the browser:

1. You type `12` in the row's box and click **Update**. The browser sends `POST /update/7` with `new_quantity=12`.
2. `app.py` (`update_quantity`) reads the number. Blank or non-numeric input is rejected with a readable message.
3. `service.update_quantity` checks that the quantity isn't negative and that part 7 exists.
4. `repository.find_by_id` loads part 7. The service sets the new quantity, and `repository.update` runs `UPDATE parts ... WHERE id = ?` and saves it.
5. The app shows a "Quantity updated." message and redirects to the home page, which reloads the table.

The desktop window follows the same path, except that `gui.py` reads the number from a prompt and shows errors in a pop-up.

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

The service layer enforces these rules. Each broken rule raises a `ValueError` with a message that the screens show to the user.

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
| Browser says it can't connect to 127.0.0.1:5000 | Run `python app.py` in a terminal and leave that terminal open. `python main.py` does not start the website. |
| `ModuleNotFoundError: No module named 'flask'` | Run `pip install flask`. |
| `ModuleNotFoundError: No module named 'tkinter'` | Reinstall Python from python.org with the tcl/tk option included, or on Linux run `sudo apt install python3-tk`. |
| Tests aren't found | Run `python -m unittest -v` from the folder that contains `tests/`. |
