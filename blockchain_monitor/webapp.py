from flask import Flask
from flask import render_template
from dashboard import dashboard_bp

app = Flask(__name__)
app.register_blueprint(dashboard_bp)


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@ app.route("/index")
def show_start_page():
    return render_template("index.html")


@ app.route("/dashboards/primary")
def show_dashboard_primary():
    return render_template("dashboards/primary.html")


@ app.route("/dashboards/secondary")
def show_dashboard_secondary():
    return render_template("dashboards/secondary.html")


@ app.route("/settings/general")
def show_settings_general():
    return render_template("/settings/settings-general.html")


@ app.route("/settings/manifest")
def show_manifest():
    return render_template("settings/blf-manifest.html")


@ app.route("/settings/process-model")
def show_process_model():
    return render_template("settings/bpmn-process-model.html")


@ app.route("/help/documentation")
def show_documentation():
    return render_template("/help/documentation.html")
