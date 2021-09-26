from flask import Flask
from flask import render_template
from flask.templating import render_template_string
from dashboard import Dashboard

app = Flask(__name__)
dashboard = Dashboard()


@app.route("/index")
def show_start_page():
    return render_template("index.html")


@app.route("/dashboards/primary")
def show_dashboard_primary():
    return render_template("dashboards/primary.html")


@app.route("/dashboards/secondary")
def show_dashboard_secondary():
    return render_template("dashboards/secondary.html")


@app.route("/dashboards/tertiary")
def show_dashboard_tertiary():
    return render_template("dashboards/tertiary.html")


@app.route("/settings/general")
def show_settings_general():
    return render_template("/settings/settings-general.html")


# @app.route("/dashboards/tertiary")
# def show_dashboard_tertiary():
#     return render_template("dashboards/tertiary.html")


# @app.route("/dashboards/tertiary")
# def show_dashboard_tertiary():
#     return render_template("dashboards/tertiary.html")


# @app.route("/dashboards/tertiary")
# def show_dashboard_tertiary():
#     return render_template("dashboards/tertiary.html")


# @app.route("/dashboard/")
# def show_dashboard():
#     dashboard.update()
#     return render_template("dashboard.html", dashboard=dashboard)


# @app.route("/manifest/")
# def show_manifest():
#     return render_template("manifest.html")


@app.route("/help/documentation")
def show_documentationl():
    return render_template("/help/documentation.html")
