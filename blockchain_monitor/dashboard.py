from werkzeug.utils import redirect
from data_processor import DataProcessor
from flask import Blueprint, request, make_response, send_file
import constants as const
import os
import app
import shutil
import json


dp = DataProcessor()
dashboard_bp = Blueprint('dashboard', __name__, template_folder='templates')


def validate_settings(from_dict: dict) -> bool:
    # TODO
    return


def process_settings(form_dict: dict):
    with open(const.SETTINGS_PATH, "w") as settings_file:
        const.SETTINGS = form_dict
        # settings_file.write(const.SETTINGS)
        json.dump(form_dict, settings_file, indent=4, sort_keys=True)
    # validate_settings()  # TODO
    dp.start_processing()


@dashboard_bp.route('/api/settings', methods=['POST', 'GET'])
def handle_settings():
    if request.method == 'POST':
        process_settings(request.form)
        return redirect('/settings/general')
    elif request.method == 'GET':
        return send_file(const.SETTINGS_PATH)


def allowed_file(filename, allow_extensions):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower(
           ) in allow_extensions


@dashboard_bp.route('/api/process_model', methods=['POST', 'GET', 'DELETE'])
def handle_process_model():
    if request.method == 'DELETE':
        shutil.copy2(const.BPMN_EMPTY_PATH, const.BPMN_PATH)
        return make_response('', 200)
    elif request.method == 'GET':
        return send_file(const.BPMN_PATH)
    elif request.method == 'POST':
        if 'bpmn-diagram' in request.files:  # upload file
            file = request.files['bpmn-diagram']
            if file.filename != '' and file and allowed_file(file.filename, const.ALLOWED_BPMN_EXTENSIONS):
                file.save(os.path.join(const.BPMN_PATH))
                return redirect('/settings/process-model')
        elif request.data:  # save file
            canvas_content = str(request.data, 'utf-8')
            with open(const.BPMN_PATH, "w") as text_file:
                text_file.write(canvas_content)
            return make_response('', 200)
    return redirect('/settings/process-model')


@dashboard_bp.route('/api/manifest', methods=['POST', 'GET', 'DELETE', 'VALIDATE'])
def handle_mainfest():
    if request.method == 'DELETE':
        open(const.MANIFEST_PATH, 'w').close()
        return make_response('', 200)
    elif request.method == 'GET':
        return send_file(const.MANIFEST_PATH)
    elif request.method == 'VALIDATE':
        result = app.validate_current_manifest()
        return make_response(result, 200)
    elif request.method == 'POST':
        if 'blf-manifest' in request.files:  # upload file
            file = request.files['blf-manifest']
            if file.filename != '' and file and allowed_file(file.filename, const.ALLOWED_MANIFEST_EXTENSIONS):
                file.save(os.path.join(const.MANIFEST_PATH))
                return redirect('/settings/manifest')
        else:  # save file
            editor_content = request.form['editor_content']
            with open(const.MANIFEST_PATH, "w") as text_file:
                text_file.write(editor_content)
            return make_response('', 200)
    return redirect('/settings/manifest')


@ dashboard_bp.route("/api/sender_stats", methods=['GET'])
def get_sender_stats():
    return dp.reitreive_sender_stats()


@ dashboard_bp.route("/api/receiver_stats", methods=['GET'])
def get_receiver_stats():
    return dp.retreive_receiver_stats()
