from flask import Flask, request, render_template, send_file
import csv
import os
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials

app = Flask(__name__)

# Base directory (important for deployment)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_FILE = os.path.join(BASE_DIR, "data", "responses.csv")

# Ensure CSV file exists with header
if not os.path.exists(CSV_FILE):
    with open(CSV_FILE, "w", newline="") as f:
        writer = csv.writer(f)
        header = ["student_id"] + [f"q{i}" for i in range(1, 51)]
        writer.writerow(header)


# ✅ Google Sheets function
def save_to_sheets(row):
    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/drive"
    ]

    creds = ServiceAccountCredentials.from_json_keyfile_name(
        os.path.join(BASE_DIR, "credentials.json"), scope
    )

    client = gspread.authorize(creds)

    sheet = client.open("Flask Responses").sheet1

    sheet.append_row(row)


@app.route("/divy")
def download():
    return send_file(CSV_FILE, as_attachment=True)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/submit", methods=["POST"])
def submit():

    # Normalize student ID
    student_id = request.form.get("student_id", "").strip().upper()

    # Load CSV for duplicate check
    df = pd.read_csv(CSV_FILE)

    if student_id in df["student_id"].astype(str).str.strip().str.upper().values:
        return render_template("repeat.html")

    # Collect answers
    answers = [request.form.get(f"q{i}") for i in range(1, 51)]

    row = [student_id] + answers

    # ✅ Save to CSV (backup)
    with open(CSV_FILE, "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(row)

    # ✅ Save to Google Sheets
    save_to_sheets(row)

    return render_template("thanks.html")

@app.route("/test")
def test():
    try:
        save_to_sheets(["TEST_ID"] + ["A"]*50)
        return "Sheets working ✅"
    except Exception as e:
        return str(e)
    
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))