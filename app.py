from flask import Flask, render_template, request, redirect
import json
from datetime import date
DAILY_GOAL = 2400

app = Flask(__name__)

DATA_FILE = "nutrition_data.json"

def load_data():
    try:
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

def add_food_entry(food, calories, protein):
    data = load_data()
    today = str(date.today())
    if today not in data:
        data[today] = []
    data[today].append({
        "food": food,
        "calories": calories,
        "protein": protein
    })
    save_data(data)

def get_daily_totals():
    data = load_data()
    today = str(date.today())
    if today not in data:
        return [], 0, 0
    entries = data[today]
    total_cal = sum(item["calories"] for item in entries)
    total_pro = sum(item["protein"] for item in entries)
    return entries, total_cal, total_pro

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        food = request.form["food"]
        calories = int(request.form["calories"])
        protein = float(request.form["protein"])
        add_food_entry(food, calories, protein)
        return redirect("/")

    entries, total_cal, total_pro = get_daily_totals()

    remaining = DAILY_GOAL - total_cal
    if remaining < 0:
        remaining = 0

    return render_template("index.html",
                           entries=entries,
                           total_cal=total_cal,
                           total_pro=total_pro,
                           remaining=remaining,
                           goal=DAILY_GOAL)
    
@app.route("/delete/<int:index>", methods=["POST"])
def delete_entry(index):
    data = load_data()
    today = str(date.today())

    if today in data and 0 <= index < len(data[today]):
        data[today].pop(index)
        save_data(data)

    return redirect("/")
    
if __name__ == "__main__":
    app.run(debug=True)
