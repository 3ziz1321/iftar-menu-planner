# app.py - the Tkinter window (what the user sees)
import json
import socket
import tkinter as tk
from tkinter import ttk, messagebox
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import urlopen

SERVER = "http://127.0.0.1:5050"


def send_request(path, values=None):
    """Send a request to Flask. Always returns a dictionary.
    No values -> GET.  With values -> POST."""
    data = None
    if values is not None:
        data = urlencode(values).encode("utf-8")
    try:
        with urlopen(SERVER + path, data=data, timeout=5) as reply:
            return json.loads(reply.read().decode("utf-8"))
    except HTTPError as e:                      # Flask said 400 / 404 / 500
        return json.loads(e.read().decode("utf-8"))
    except (URLError, socket.timeout):          # Flask is off or too slow
        return {"error": "Cannot reach the server. Start Flask and try again."}


class IftarApp:
    def __init__(self, window):
        self.window = window
        window.title("Iftar Menu Planner")

        # --- input fields ---
        form = tk.Frame(window)
        form.pack(padx=10, pady=10)
        tk.Label(form, text="Dish name:").grid(row=0, column=0, sticky="e")
        tk.Label(form, text="Category:").grid(row=1, column=0, sticky="e")
        tk.Label(form, text="Price (SAR):").grid(row=2, column=0, sticky="e")
        self.name_box = tk.Entry(form, width=25)
        self.category_box = tk.Entry(form, width=25)
        self.price_box = tk.Entry(form, width=25)
        self.name_box.grid(row=0, column=1, pady=2)
        self.category_box.grid(row=1, column=1, pady=2)
        self.price_box.grid(row=2, column=1, pady=2)

        # --- buttons ---
        buttons = tk.Frame(window)
        buttons.pack()
        tk.Button(buttons, text="Add", width=10, command=self.add).grid(row=0, column=0, padx=3)
        tk.Button(buttons, text="Update", width=10, command=self.edit).grid(row=0, column=1, padx=3)
        tk.Button(buttons, text="Delete", width=10, command=self.delete).grid(row=0, column=2, padx=3)
        tk.Button(buttons, text="Refresh", width=10, command=self.refresh).grid(row=0, column=3, padx=3)

        # --- table of records ---
        self.table = ttk.Treeview(window, columns=("id", "name", "category", "price"),
                                  show="headings", height=8)
        for column in ("id", "name", "category", "price"):
            self.table.heading(column, text=column.title())
        self.table.column("id", width=40)
        self.table.pack(padx=10, pady=10)
        self.table.bind("<<TreeviewSelect>>", self.on_select)

        # --- total + message ---
        self.total_label = tk.Label(window, text="Total: 0 SAR", font=("Arial", 12, "bold"))
        self.total_label.pack()
        self.message_label = tk.Label(window, text="")
        self.message_label.pack(pady=5)

        self.refresh()

    # ----- helpers -----
    def show(self, text, good):
        self.message_label.config(text=text, fg="green" if good else "red")

    def show_result(self, result):
        """Show success or error from a Flask reply, then reload the table."""
        if "error" in result:
            self.show(result["error"], False)
        else:
            self.show(result["message"], True)
            self.clear_boxes()
        self.refresh()

    def clear_boxes(self):
        for box in (self.name_box, self.category_box, self.price_box):
            box.delete(0, tk.END)

    def form_values(self):
        return {"name": self.name_box.get(),
                "category": self.category_box.get(),
                "price": self.price_box.get()}

    def selected_id(self):
        chosen = self.table.selection()
        if not chosen:
            return None
        return self.table.item(chosen[0])["values"][0]

    # ----- actions -----
    def refresh(self):
        result = send_request("/dishes")                 # GET
        if "error" in result:
            self.show(result["error"], False)
            return
        for row in self.table.get_children():            # empty the table
            self.table.delete(row)
        for dish in result["dishes"]:                    # fill it again
            self.table.insert("", tk.END, values=(dish["id"], dish["name"],
                                                  dish["category"], dish["price"]))
        self.total_label.config(text=f"Total: {result['total']} SAR")
        if not result["dishes"]:
            self.show("No dishes yet. Add your first one!", True)

    def on_select(self, event):
        chosen = self.table.selection()
        if chosen:
            _, name, category, price = self.table.item(chosen[0])["values"]
            self.clear_boxes()
            self.name_box.insert(0, name)
            self.category_box.insert(0, category)
            self.price_box.insert(0, price)

    def add(self):
        self.show_result(send_request("/dishes/add", self.form_values()))

    def edit(self):
        dish_id = self.selected_id()
        if dish_id is None:
            self.show("Select a dish from the table first.", False)
            return
        values = self.form_values()
        values["id"] = dish_id
        self.show_result(send_request("/dishes/edit", values))

    def delete(self):
        dish_id = self.selected_id()
        if dish_id is None:
            self.show("Select a dish from the table first.", False)
            return
        if messagebox.askyesno("Confirm", "Delete this dish?"):
            self.show_result(send_request("/dishes/delete", {"id": dish_id}))


window = tk.Tk()
IftarApp(window)
window.mainloop()
