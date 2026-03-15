from flask import Flask, request, render_template,send_file
import csv
import os
import pandas as pd

app = Flask(__name__)

CSV_FILE = "data/responses.csv"

# create csv header if file doesn't exist
if not os.path.exists(CSV_FILE):
    with open(CSV_FILE, "w", newline="") as f:
        writer = csv.writer(f)
        header = ["student_id"] + [f"q{i}" for i in range(1,51)]
        writer.writerow(header)


@app.route("/download")
def download():
    return send_file("responses.csv", as_attachment=True)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/submit", methods=["POST"])
def submit():

    student_id = request.form.get("student_id")

    # 🔹 CHECK FOR DUPLICATE STUDENT ID
    df = pd.read_csv(CSV_FILE)

    if student_id in df["student_id"].astype(str).values:
        return render_template("repeat.html")

    # collect answers
    answers = [request.form.get(f"q{i}") for i in range(1,51)]

    row = [student_id] + answers

    # save response
    with open(CSV_FILE, "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(row)

    return render_template("thanks.html")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)