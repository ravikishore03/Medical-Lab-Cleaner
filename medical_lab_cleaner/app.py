from flask import Flask, render_template, request, send_file
import pandas as pd
import numpy as np
import os

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
PROCESSED_FOLDER = "processed"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(PROCESSED_FOLDER, exist_ok=True)

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        file = request.files["file"]
        filepath = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(filepath)

        # Read CSV
        df = pd.read_csv(filepath)

        # Handle missing values
        df.fillna(df.mean(numeric_only=True), inplace=True)

        # Unit conversion (example: glucose mg/dL → mmol/L)
        if "unit" in df.columns and "glucose" in df.columns:
            df.loc[df["unit"] == "mg/dL", "glucose"] = df["glucose"] / 18

        # Remove outliers using IQR
        if "glucose" in df.columns:
            Q1 = df["glucose"].quantile(0.25)
            Q3 = df["glucose"].quantile(0.75)
            IQR = Q3 - Q1
            df = df[(df["glucose"] >= Q1 - 1.5 * IQR) &
                    (df["glucose"] <= Q3 + 1.5 * IQR)]

            # Normalize glucose values
            df["glucose"] = (df["glucose"] - df["glucose"].mean()) / df["glucose"].std()

        output_path = os.path.join(PROCESSED_FOLDER, "cleaned_data.csv")
        df.to_csv(output_path, index=False)

        return render_template("result.html")

    return render_template("index.html")

@app.route("/download")
def download():
    return send_file("processed/cleaned_data.csv", as_attachment=True)

if __name__ == "__main__":
    app.run(debug=True)
