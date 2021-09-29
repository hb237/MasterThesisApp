from werkzeug.utils import redirect
from data_processor import DataProcessor
from flask import Blueprint, request, make_response, send_file, jsonify
import constants as const
import os
import app
import shutil
import json


dp = DataProcessor()
dashboard_bp = Blueprint('dashboard', __name__, template_folder='templates')


@dashboard_bp.route('/api/start_monitoring', methods=['GET'])
def start_monitoring():
    dp.init_processing()
    return '', 202


@dashboard_bp.route('/api/stop_monitoring', methods=['GET'])
def stop_monitoring():
    dp.stop_processing()
    return '', 202


@dashboard_bp.route('/api/settings', methods=['POST', 'GET'])
def handle_settings():
    if request.method == 'POST':
        with open(const.SETTINGS_PATH, "w") as settings_file:
            json.dump(request.form, settings_file, indent=4, sort_keys=True)
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


@dashboard_bp.route('/api/events', methods=['GET'])
def get_events():
    with open(const.EVENTS) as f:
        return json.load(f)


@dashboard_bp.route('/api/traces', methods=['GET'])
def get_traces():
    with open(const.TRACES) as f:
        return json.load(f)


@dashboard_bp.route('/api/block_stats', methods=['GET'])
def get_block_stats():
    with open(const.BLOCK_STATS) as f:
        return json.dumps(json.load(f))


@dashboard_bp.route('/api/sender_stats', methods=['GET'])
def get_sender_stats():
    with open(const.SENDER_STATS) as f:
        return json.dumps(json.load(f))


@dashboard_bp.route('/api/receiver_stats', methods=['GET'])
def get_receiver_stats():
    with open(const.RECEIVER_STATS) as f:
        return json.dumps(json.load(f))


@dashboard_bp.route('/api/eth_rates', methods=['GET'])
def get_eth_rates():
    with open(const.ETH_RATES) as f:
        return json.dumps(json.load(f))
