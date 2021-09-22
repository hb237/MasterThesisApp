from flask import Flask
from flask import render_template
from datetime import datetime
from dashboard import Dashboard

app = Flask(__name__)
dashboard = Dashboard()

@app.route("/")
@app.route("/dashboard/")
def show_dashboard():
    dashboard.update()
    return render_template("dashboard.html", dashboard=dashboard)

@app.route("/manifest/")
def show_manifest():
    return render_template("manifest.html")

@app.route("/process_model/")
def show_process_model():
    return render_template("process_model.html")
