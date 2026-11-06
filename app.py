"""app.py — Flask web interface for the Parts Inventory Tracker.

Run with:
    python app.py
Then open http://127.0.0.1:5000 in browser.
"""
from flask import Flask, render_template, request, redirect, url_for, flash

from inventory.repository import PartRepository
from inventory.service import InventoryService

app = Flask(__name__)
app.secret_key = "dev"  # fine for local testing

service = InventoryService(PartRepository("parts.db"))

@app.route("/")
def index():
    search_text = request.args.get("q", "")
    show_low = request.args.get("low") == "1"
    if show_low:
        parts = service.get_low_stock_parts()
    elif search_text:
        parts = service.search(search_text)
    else:
        parts = service.list_parts()
    return render_template("index.html", parts=parts, search_text=search_text, show_low=show_low)


@app.route("/add", methods=["POST"])
def add_part():
    try:
        service.add_part(
            part_number=request.form["part_number"],
            name=request.form["name"],
            quantity=int(request.form.get("quantity") or 0),
            reorder_level=int(request.form.get("reorder_level") or 0),
            location=request.form.get("location", ""),
        )
        flash("Part added.", "success")
    except ValueError as err:
        flash(str(err), "error")
    return redirect(url_for("index"))


@app.route("/update/<int:part_id>", methods=["POST"])
def update_quantity(part_id):
    try:
        service.update_quantity(part_id, int(request.form["new_quantity"]))
        flash("Quantity updated.", "success")
    except ValueError as err:
        flash(str(err), "error")
    return redirect(url_for("index"))


@app.route("/remove/<int:part_id>", methods=["POST"])
def remove_part(part_id):
    try:
        service.remove_part(part_id)
        flash("Part removed.", "success")
    except ValueError as err:
        flash(str(err), "error")
    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(debug=True)