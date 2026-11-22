# Iftar Menu Planner

Advanced Programming 462 – Individual Project
Name: Abdulaziz Abou  Student ID: 443043833  GitHub: https://github.com/3ziz1321

## What it does
A small desktop app to plan an Iftar menu. You add dishes (name, category, price),
view them in a table, edit and delete them. **Extra feature:** it shows the
**total estimated cost** of the whole menu.

Structure: `Tkinter window (app.py)  <->  Flask (server.py)  <->  SQLite (iftar.db)`

## Setup (exact steps)
1. Install Python 3 (Tkinter comes with it).
2. Install packages: `pip install -r requirements.txt`
3. Start Flask (this also creates the table if missing): `python server.py`
4. In a **second** terminal start the window: `python app.py`

## Report helper (thread demo)
With Flask running, in a third terminal: `python report.py`
It writes `report.txt` and prints whether it was saved.

## Course topics – where to find them
| Topic | Evidence |
|---|---|
| Python and collections | `server.py`: `read_form()` (conditions), `list_dishes()` (list of dictionaries, loop in `sum(...)`), `app.py`: `refresh()` (for loops) |
| Exceptions | `app.py`: `send_request()` (HTTPError, URLError, timeout); `server.py`: `read_form()` (ValueError), `database_problem()`; `report.py` (OSError) |
| Classes | `server.py`: class `Database`; `app.py`: class `IftarApp` |
| SQLite | `server.py`: `Database.add / get_all / edit / delete` using `?` placeholders |
| Threads and files | `report.py`: `write_report()` run by `threading.Thread`, `start()`, `join()`, `with open(...)` |
| Tkinter | `app.py`: labels, entries, buttons, Treeview table, message label |
| Client and server | See below |
| Flask | `server.py`: routes `/dishes`, `/dishes/add`, `/dishes/edit`, `/dishes/delete`, JSON replies, 400/404 errors |

### One HTTP request explained
Click **Add** -> `IftarApp.add()` -> `send_request("/dishes/add", values)` sends a POST
with the form data -> Flask `add_dish()` checks the values -> `Database.add()` saves them
in SQLite -> Flask replies JSON `{"message": "Dish saved.", "id": 1}` -> the window
shows "Dish saved." and reloads the table.

## Test results
| Test | Result |
|---|---|
| Add / view / edit / delete (backend) | Passed |
| Missing input -> 400 error | Passed |
| Invalid price (letters, negative) -> 400 error | Passed |
| Unknown ID (edit/delete) -> 404 error | Passed |
| Empty list | Passed |
| Data remains after restart | Passed |
| Report helper creates report.txt | Passed |
| Window tests (Flask stopped / restarted, delete confirmation) | Passed |

Credits

Code written with help from Claude (AI assistant).