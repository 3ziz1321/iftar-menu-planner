# server.py - the Flask back end (the "brain" that talks to the database)
import sqlite3
from flask import Flask, request, jsonify

DB_FILE = "iftar.db"
app = Flask(__name__)


# ---------- Class: all database work lives here ----------
class Database:
    def __init__(self, filename):
        self.filename = filename

    def connect(self):
        # A NEW connection for every request
        conn = sqlite3.connect(self.filename)
        conn.row_factory = sqlite3.Row   # lets us read columns by name
        return conn

    def create_tables(self):
        # IF NOT EXISTS = keep old records, only create the table when missing
        conn = self.connect()
        try:
            conn.execute(
                "CREATE TABLE IF NOT EXISTS dishes ("
                "id INTEGER PRIMARY KEY AUTOINCREMENT, "
                "name TEXT NOT NULL, "
                "category TEXT NOT NULL, "
                "price REAL NOT NULL)"
            )
            conn.commit()
        finally:
            conn.close()

    def get_all(self):
        conn = self.connect()
        try:
            rows = conn.execute("SELECT * FROM dishes ORDER BY id").fetchall()
            return [dict(row) for row in rows]   # list of dictionaries
        finally:
            conn.close()

    def add(self, name, category, price):
        conn = self.connect()
        try:
            cursor = conn.execute(
                "INSERT INTO dishes (name, category, price) VALUES (?, ?, ?)",
                (name, category, price),
            )
            conn.commit()
            return cursor.lastrowid          # the new ID
        finally:
            conn.close()

    def edit(self, dish_id, name, category, price):
        conn = self.connect()
        try:
            cursor = conn.execute(
                "UPDATE dishes SET name = ?, category = ?, price = ? WHERE id = ?",
                (name, category, price, dish_id),
            )
            conn.commit()
            return cursor.rowcount           # 0 means: ID not found
        finally:
            conn.close()

    def delete(self, dish_id):
        conn = self.connect()
        try:
            cursor = conn.execute("DELETE FROM dishes WHERE id = ?", (dish_id,))
            conn.commit()
            return cursor.rowcount           # 0 means: ID not found
        finally:
            conn.close()


db = Database(DB_FILE)


# ---------- Small helper functions ----------
def error(message, code):
    return jsonify({"error": message}), code


def read_form():
    """Read and check name, category, price. Returns (values, problem)."""
    name = request.form.get("name", "").strip()
    category = request.form.get("category", "").strip()
    price_text = request.form.get("price", "").strip()

    if name == "" or category == "" or price_text == "":
        return None, "Name, category and price are all required."
    try:
        price = float(price_text)
    except ValueError:
        return None, "Price must be a number."
    if price < 0 or price > 1000:
        return None, "Price must be between 0 and 1000."
    return (name, category, price), None


def read_id():
    try:
        return int(request.form.get("id", "")), None
    except ValueError:
        return None, "Invalid ID."


# ---------- Routes ----------
@app.route("/dishes")                      # GET: read all records + total
def list_dishes():
    dishes = db.get_all()
    total = sum(d["price"] for d in dishes)    # the EXTRA FEATURE
    return jsonify({"dishes": dishes, "total": round(total, 2)})


@app.route("/dishes/add", methods=["POST"])
def add_dish():
    values, problem = read_form()
    if problem:
        return error(problem, 400)
    new_id = db.add(*values)
    return jsonify({"message": "Dish saved.", "id": new_id})


@app.route("/dishes/edit", methods=["POST"])
def edit_dish():
    dish_id, problem = read_id()
    if problem:
        return error(problem, 400)
    values, problem = read_form()
    if problem:
        return error(problem, 400)
    if db.edit(dish_id, *values) == 0:
        return error("That dish no longer exists.", 404)
    return jsonify({"message": "Dish updated."})


@app.route("/dishes/delete", methods=["POST"])
def delete_dish():
    dish_id, problem = read_id()
    if problem:
        return error(problem, 400)
    if db.delete(dish_id) == 0:
        return error("That dish no longer exists.", 404)
    return jsonify({"message": "Dish deleted."})


@app.errorhandler(sqlite3.Error)           # any unexpected database error
def database_problem(e):
    return error("Database error. Please try again.", 500)


if __name__ == "__main__":
    db.create_tables()
    app.run(port=5050)
